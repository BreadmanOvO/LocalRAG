"""FastAPI composition layer for the v1.8 Runtime contracts.

The default app uses deterministic in-memory stores for local demos. A
SQLAlchemy conversation repository can be selected with ``database_url`` or
``LOCALRAG_DATABASE_URL``; cloud multi-agent execution is injected as a
runtime and remains bounded by the room event contract.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
import base64
import binascii
import asyncio
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.concurrency import run_in_threadpool

from agent_platform.contracts.identity import RoomEventCursor, new_identifier, validate_identifier
from agent_platform.conversations.repository import ConflictError, ConversationRepository, NotFoundError, RepositoryError
from agent_platform.conversations.sql_repository import SqlAlchemyConversationRepository
from agent_platform.runtime.control import ControlConflictError, ControlError, RunController, RunNotClaimableError
from agent_platform.runtime.event_store import EventConflictError, EventStore
from agent_platform.runtime.sql_event_store import SqlAlchemyEventStore
from agent_platform.worker import TeamWorker
from agent_platform.personas import PersonaProfile, default_registry
from agent_platform.routing import ArchitectureSpec, PlanCompiler, TaskProfile, TaskRouter
from agent_platform.runtime.multi_agent import CloudTeamRuntime
from agent_platform.capability_packs import LocalObjectStore
from .auth import AuthConfigError, BearerAuthenticator, Principal, env_auth_required

from .schemas import (
    AssistantMessageRequest, AssistantMessageResponse, CommandRequest, CommandResponse, ErrorEnvelope, EventListResponse, EventResponse,
    FollowupRequest, FollowupResponse, HealthResponse, MessageCreateRequest,
    MemberListResponse, MessageListResponse, MessageResponse, RoomCreateRequest, RoomListResponse, RoomResponse,
    PersonaCreateRequest, PersonaResponse, PersonaBindingResponse, RoleListResponse, PlanCompileRequest, PlanCompileResponse,
    RunCreateRequest, RunResponse, TaskCreateRequest, TaskResponse, MultiAgentExecuteRequest, MultiAgentExecuteResponse,
    AssetUploadRequest, AssetUploadResponse,
)


@dataclass
class _Task:
    task_id: str
    room_id: str
    title: str
    status: str = "active"
    version: int = 1
    active_run_id: str | None = None


class ApiDomainError(RuntimeError):
    def __init__(self, code: str, message: str, *, status: int = 400, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code, self.status, self.details = code, status, details or {}


def _dump(value: Any) -> Any:
    return jsonable_encoder(asdict(value) if hasattr(value, "__dataclass_fields__") else value)


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID") or f"req-{uuid4().hex}"


def _error(request: Request, exc: ApiDomainError) -> JSONResponse:
    payload = ErrorEnvelope(code=exc.code, message=str(exc), details=exc.details, request_id=_request_id(request), control_epoch=exc.details.get("control_epoch"), row_version=exc.details.get("row_version"))
    return JSONResponse(status_code=exc.status, content=payload.model_dump())


def create_app(*, repository: ConversationRepository | SqlAlchemyConversationRepository | None = None, events: EventStore | SqlAlchemyEventStore | None = None, runs: RunController | None = None, team_runtime: CloudTeamRuntime | None = None, database_url: str | None = None, asset_store: LocalObjectStore | None = None, auth_required: bool | None = None, auth_tokens: dict[str, str | list[str] | tuple[str, ...]] | None = None) -> FastAPI:
    """Create an API app with injectable in-memory stores for tests and demos."""
    if repository is None and (database_url or os.environ.get("LOCALRAG_DATABASE_URL")):
        repository = SqlAlchemyConversationRepository.from_url(database_url or os.environ["LOCALRAG_DATABASE_URL"])
    repository = repository or ConversationRepository()
    if events is None and isinstance(repository, SqlAlchemyConversationRepository):
        events = SqlAlchemyEventStore(repository.engine, create_schema=repository.engine.dialect.name == "sqlite")
    events = events or EventStore()
    runs = runs or RunController()
    tasks: dict[str, _Task] = {}
    personas = default_registry()
    planner = PlanCompiler()
    task_router = TaskRouter()
    asset_store = asset_store or LocalObjectStore()
    room_keys: dict[str, tuple[str, str]] = {}
    assistant_keys: dict[str, tuple[str, str, str]] = {}
    commands: dict[str, dict[str, Any]] = {}
    active_team_rooms: set[str] = set()
    team_worker = TeamWorker(max_workers=max(1, int(os.environ.get("LOCALRAG_WORKER_CONCURRENCY", "2"))))
    auth_required = env_auth_required() if auth_required is None else auth_required
    if os.environ.get("LOCALRAG_ENV", "").strip().lower() in {"prod", "production"}:
        auth_required = True
    authenticator: BearerAuthenticator | None = None
    if auth_required:
        try:
            authenticator = BearerAuthenticator(auth_tokens) if auth_tokens is not None else BearerAuthenticator.from_env()
        except AuthConfigError as exc:
            raise RuntimeError(f"authentication configuration is incomplete: {exc}") from exc
    asset_spaces: dict[str, str] = {}

    def _record_message_event(message: Any) -> None:
        """Project each saved message into the room event stream exactly once."""
        events.append(
            message.room_id,
            "message_saved",
            event_id=f"event-message-{message.message_id}",
            payload={"message_id": message.message_id, "role": message.role},
        )

    app = FastAPI(title="LocalRAG Agent Platform API", version="1.8.0")
    app.state.repository, app.state.events, app.state.runs, app.state.tasks, app.state.personas, app.state.planner, app.state.team_runtime, app.state.asset_store, app.state.team_worker = repository, events, runs, tasks, personas, planner, team_runtime, asset_store, team_worker

    @app.on_event("shutdown")
    async def _shutdown_worker() -> None:
        team_worker.close()

    @app.middleware("http")
    async def authenticate(request: Request, call_next: Any) -> JSONResponse | StreamingResponse:
        """Authenticate before dispatch; health remains probeable without a token."""
        if not auth_required or request.url.path in {"/health", "/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}:
            return await call_next(request)
        header = request.headers.get("Authorization", "")
        scheme, _, token = header.partition(" ")
        principal = authenticator.authenticate(token.strip()) if scheme.lower() == "bearer" and token.strip() else None
        if principal is None:
            return JSONResponse(status_code=401, content={"code": "authentication_required", "message": "valid Bearer credentials are required", "details": {}, "request_id": _request_id(request)})
        request.state.principal = principal
        return await call_next(request)

    def _principal(request: Request) -> Principal | None:
        return getattr(request.state, "principal", None)

    def _require_space(request: Request, space_id: str) -> Principal | None:
        principal = _principal(request)
        if principal is not None and not principal.can_access(space_id):
            raise ApiDomainError("space_forbidden", "the credential cannot access this space", status=403, details={"space_id": space_id})
        return principal

    def _room_for_request(request: Request, room_id: str) -> Any:
        room = repository.get_room(room_id)
        _require_space(request, room.space_id)
        return room

    @app.exception_handler(ApiDomainError)
    async def _handle_domain(request: Request, exc: ApiDomainError) -> JSONResponse:
        return _error(request, exc)

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _error(request, ApiDomainError("invalid_request", "request validation failed", status=422, details={"errors": exc.errors()}))

    @app.exception_handler(Exception)
    async def _handle_contract(request: Request, exc: Exception) -> JSONResponse:
        if isinstance(exc, (ConflictError, ControlConflictError, EventConflictError)):
            status, code = 409, "conflict"
        elif isinstance(exc, (NotFoundError, ControlError)):
            status, code = 404, "not_found"
        elif isinstance(exc, (RepositoryError, ValueError)):
            status, code = 400, "invalid_request"
        else:
            raise exc
        return _error(request, ApiDomainError(code, str(exc), status=status))

    @app.get("/health", response_model=HealthResponse)
    async def health() -> dict[str, str]:
        return {"status": "ok", "contract": "v1.8-inmemory"}

    @app.get("/roles", response_model=RoleListResponse)
    async def list_roles() -> Any:
        return {"items": [_dump(item) for item in personas.list_roles()]}

    @app.get("/persona-profiles/{persona_id}", response_model=PersonaResponse)
    async def get_persona(persona_id: str) -> Any:
        try:
            return _dump(personas.latest(persona_id))
        except KeyError as exc:
            raise ApiDomainError("not_found", "persona not found", status=404) from exc

    @app.post("/persona-profiles", status_code=201, response_model=PersonaResponse)
    async def save_persona(body: PersonaCreateRequest) -> Any:
        try:
            profile = personas.latest(body.persona_id)
            version = profile.version + 1
        except KeyError:
            version = 1
        try:
            saved = personas.save_profile(PersonaProfile(body.persona_id, body.role_id, version, body.display_name, body.system_prompt, body.tone))
        except ValueError as exc:
            raise ApiDomainError("invalid_request", str(exc), status=400) from exc
        return _dump(saved)

    @app.post("/persona-bindings", status_code=201, response_model=PersonaBindingResponse)
    async def bind_persona(persona_id: str = Query(..., min_length=1)) -> Any:
        try:
            return _dump(personas.bind(persona_id))
        except KeyError as exc:
            raise ApiDomainError("not_found", "persona not found", status=404) from exc

    @app.post("/plans/compile", response_model=PlanCompileResponse)
    async def compile_plan(body: PlanCompileRequest) -> Any:
        try:
            plan = planner.compile(TaskProfile(body.task_id, body.goal, body.requires_decomposition, tuple(body.required_capabilities), body.budget_units), ArchitectureSpec(body.architecture, body.max_agents, body.architecture == "graph"), mode=body.mode, available_capabilities={"rag", "analysis", "review", "chat", "route"})
        except ValueError as exc:
            raise ApiDomainError("plan_rejected", str(exc), status=422) from exc
        return _dump(plan)

    @app.post("/rooms", status_code=201, response_model=RoomResponse)
    async def create_room(request: Request, body: RoomCreateRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> Any:
        _require_space(request, body.space_id)
        if idempotency_key and idempotency_key in room_keys:
            old_space, room_id = room_keys[idempotency_key]
            if old_space != body.space_id or body.room_id not in (None, room_id):
                raise ApiDomainError("idempotency_conflict", "idempotency key payload differs", status=409)
            return _dump(repository.get_room(room_id))
        room = repository.create_room(body.space_id, body.title, room_id=body.room_id)
        if idempotency_key:
            room_keys[idempotency_key] = (body.space_id, room.room_id)
        return _dump(room)

    @app.get("/rooms", response_model=RoomListResponse)
    async def list_rooms(request: Request, space_id: str | None = None) -> Any:
        principal = _principal(request)
        if space_id:
            _require_space(request, space_id)
            rooms = repository.list_rooms(space_id)
        elif principal is None or "*" in principal.spaces:
            rooms = repository.list_rooms()
        else:
            rooms = tuple(room for allowed in principal.spaces for room in repository.list_rooms(allowed))
        return {"items": [_dump(room) for room in rooms]}

    @app.post("/assistant/messages", status_code=201, response_model=AssistantMessageResponse)
    async def assistant_message(
        request: Request,
        body: AssistantMessageRequest,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> Any:
        """Persist the first assistant message and room in one repository boundary."""
        if body.room_id:
            room = _room_for_request(request, body.room_id)
        else:
            _require_space(request, body.space_id)
            room = None
        if idempotency_key and idempotency_key in assistant_keys:
            old_space, room_id, old_content = assistant_keys[idempotency_key]
            if old_space != body.space_id or old_content != body.content.strip():
                raise ApiDomainError("idempotency_conflict", "idempotency key payload differs", status=409)
            room = _room_for_request(request, room_id)
            messages = repository.list_messages(room_id)
            if messages:
                _record_message_event(messages[0])
            return {"room": _dump(room), "message": _dump(messages[0]), "created": False}
        if body.room_id:
            assert room is not None
            message = repository.save_message(room.room_id, body.content, role="user", idempotency_key=idempotency_key)
            _record_message_event(message)
            return {"room": _dump(room), "message": _dump(message), "created": False}
        title = body.title.strip() or body.content.strip().splitlines()[0][:80]
        room, message = repository.create_room_with_message(body.space_id, title, body.content, idempotency_key=idempotency_key)
        _record_message_event(message)
        if idempotency_key:
            assistant_keys[idempotency_key] = (body.space_id, room.room_id, body.content.strip())
        return {"room": _dump(room), "message": _dump(message), "created": True}

    @app.get("/rooms/{room_id}", response_model=RoomResponse)
    async def get_room(request: Request, room_id: str) -> Any:
        return _dump(_room_for_request(request, room_id))

    @app.post("/rooms/{room_id}/messages", status_code=201, response_model=MessageResponse)
    async def create_message(request: Request, room_id: str, body: MessageCreateRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> Any:
        _room_for_request(request, room_id)
        message = repository.save_message(room_id, body.content, role=body.role, message_id=body.message_id, idempotency_key=idempotency_key)
        _record_message_event(message)
        return _dump(message)

    @app.get("/rooms/{room_id}/messages", response_model=MessageListResponse)
    async def list_messages(request: Request, room_id: str, after: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=1000)) -> Any:
        _room_for_request(request, room_id)
        items = repository.list_messages(room_id, after=after, limit=limit)
        next_cursor = items[-1].room_sequence if items else after
        return {"items": [_dump(item) for item in items], "next": next_cursor}

    @app.get("/rooms/{room_id}/members", response_model=MemberListResponse)
    async def list_members(request: Request, room_id: str) -> Any:
        _room_for_request(request, room_id)
        return {"items": [_dump(item) for item in repository.list_members(room_id)]}


    @app.get("/rooms/{room_id}/events", response_model=EventListResponse)
    async def list_events(request: Request, room_id: str, after: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=1000)) -> Any:
        _room_for_request(request, room_id)
        cursor = RoomEventCursor(validate_identifier(room_id, "room"), after)
        return {"items": [_dump(item) for item in events.read_after(cursor, limit=limit)], "next": events.snapshot(room_id).cursor.room_sequence}

    @app.get("/rooms/{room_id}/events/stream")
    async def stream_events(request: Request, room_id: str, after: int = Query(default=0, ge=0), follow: bool = Query(default=False), timeout: float = Query(default=15.0, ge=0.0, le=60.0)) -> StreamingResponse:
        _room_for_request(request, room_id)
        cursor = RoomEventCursor(validate_identifier(room_id, "room"), after)

        async def generate() -> Any:
            nonlocal cursor
            deadline = asyncio.get_running_loop().time() + timeout
            emitted = False
            while True:
                batch = events.read_after(cursor, limit=100)
                if batch:
                    for item in batch:
                        emitted = True
                        yield f"id: {item.identity.room_sequence}\ndata: {json.dumps(_dump(item), ensure_ascii=False, separators=(',', ':'))}\n\n"
                    cursor = RoomEventCursor(cursor.room_id, batch[-1].identity.room_sequence)
                    if not follow:
                        return
                    continue
                if not follow or asyncio.get_running_loop().time() >= deadline:
                    if not emitted:
                        yield ": heartbeat\n\n"
                    return
                yield ": heartbeat\n\n"
                await asyncio.sleep(0.25)

        return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    @app.get("/rooms/{room_id}/events/{event_id}", response_model=EventResponse)
    async def get_event(request: Request, room_id: str, event_id: str) -> Any:
        _room_for_request(request, room_id)
        validate_identifier(room_id, "room")
        for item in events.read_after(RoomEventCursor(validate_identifier(room_id, "room"), 0), limit=1000):
            if item.identity.event_id == event_id:
                return _dump(item)
        raise ApiDomainError("not_found", "event not found", status=404)

    @app.post("/tasks", status_code=201, response_model=TaskResponse)
    async def create_task(request: Request, body: TaskCreateRequest) -> Any:
        _room_for_request(request, body.room_id)
        task_id = validate_identifier(body.task_id, "task") if body.task_id else new_identifier("task")
        if task_id in tasks:
            raise ApiDomainError("conflict", "task already exists", status=409)
        task = _Task(task_id, body.room_id, body.title.strip())
        tasks[task_id] = task
        return _dump(task)

    @app.post("/rooms/{room_id}/multi-agent/execute", response_model=MultiAgentExecuteResponse)
    async def execute_multi_agent(request: Request, room_id: str, body: MultiAgentExecuteRequest) -> Any:
        room = _room_for_request(request, room_id)
        if room.status != "active":
            raise ApiDomainError("conflict", "room is not active", status=409)
        task_id = validate_identifier(body.task_id, "task") if body.task_id else new_identifier("task")
        task = tasks.get(task_id)
        if task is not None and task.room_id != room.room_id:
            raise ApiDomainError("conflict", "task belongs to another room", status=409)
        if room.room_id in active_team_rooms:
            raise ApiDomainError("run_active", "room already has an active team run", status=409)
        runtime = app.state.team_runtime
        if runtime is None:
            try:
                runtime = CloudTeamRuntime.from_config()
            except (RuntimeError, OSError) as exc:
                raise ApiDomainError("capability_not_ready", str(exc), status=503) from exc
        decision = task_router.route(body.goal, requested_architecture=body.architecture, max_agents=body.max_agents)
        if decision.architecture in {"graph", "heterogeneous"}:
            raise ApiDomainError("capability_not_ready", f"当前策略尚未接入真实执行器：{decision.architecture}", status=503, details={"route_reason": decision.reason, "required_capabilities": list(decision.required_capabilities)})
        runtime.validate(body.goal, decision.architecture, decision.max_agents)
        history = repository.list_messages(room.room_id)
        context = "\n".join(f"{message.role}: {message.content}" for message in history[-20:])[-16000:]
        if task is None:
            task = _Task(task_id, room.room_id, body.goal.strip())
            tasks[task_id] = task
        run_id = new_identifier("run")
        runs.register_run(run_id, plan_revision=1, status="running")
        task.active_run_id = run_id
        user_message = repository.save_message(room.room_id, body.goal, role="user", idempotency_key=f"team-goal-{run_id}")
        _record_message_event(user_message)
        events.append(room.room_id, "run_started", run_id=run_id, task_id=task_id, payload={"requested_architecture": body.architecture, "architecture": decision.architecture, "route_reason": decision.reason})
        active_team_rooms.add(room.room_id)

        def record_turn(turn: Any) -> None:
            if runs.get_run(run_id).status != "running":
                raise ControlConflictError("team run is no longer running")
            existing = repository.list_members(room.room_id)
            if not any(member.agent_id == turn.agent_id and member.status == "active" for member in existing):
                repository.join_member(room.room_id, turn.agent_id)
            message = repository.save_message(room.room_id, f"[{turn.agent_id}] {turn.content}", role="assistant")
            _record_message_event(message)
            events.append(room.room_id, "step_completed", task_id=task_id, run_id=run_id, step_id=f"step-{run_id}-{turn.sequence}", payload={"agent_id": turn.agent_id, "message_id": message.message_id})

        if body.background:
            def execute_in_worker() -> None:
                try:
                    result = runtime.execute(body.goal, architecture=decision.architecture, max_agents=decision.max_agents, context=context, on_turn=record_turn)
                    current = runs.get_run(run_id)
                    if current.status == "running":
                        runs.finish(run_id, status="completed", expected_row_version=current.row_version)
                    events.append(room.room_id, "run_completed", run_id=run_id, task_id=task_id, payload={"turn_count": len(result.turns), "worker": True})
                except Exception as exc:
                    current = runs.get_run(run_id)
                    if current.status == "running":
                        runs.finish(run_id, status="failed", expected_row_version=current.row_version)
                    events.append(room.room_id, "run_failed", run_id=run_id, task_id=task_id, payload={"error": type(exc).__name__, "worker": True})
                finally:
                    task.active_run_id = None
                    active_team_rooms.discard(room.room_id)

            job = team_worker.submit(execute_in_worker)
            events.append(room.room_id, "run_queued", run_id=run_id, task_id=task_id, payload={"job_id": job.job_id})
            return {"room_id": room.room_id, "task_id": task_id, "run_id": run_id, "architecture": decision.architecture, "route_reason": decision.reason, "status": "queued", "final": "", "turns": []}

        try:
            result = await run_in_threadpool(runtime.execute, body.goal, architecture=decision.architecture, max_agents=decision.max_agents, context=context, on_turn=record_turn)
            current = runs.get_run(run_id)
            if current.status != "running":
                raise ControlConflictError("team run is no longer running")
            runs.finish(run_id, status="completed", expected_row_version=current.row_version)
            events.append(room.room_id, "run_completed", run_id=run_id, task_id=task_id, payload={"turn_count": len(result.turns)})
        except Exception as exc:
            current = runs.get_run(run_id)
            if current.status == "running":
                runs.finish(run_id, status="failed", expected_row_version=current.row_version)
            events.append(room.room_id, "run_failed", run_id=run_id, task_id=task_id, payload={"error": type(exc).__name__, "status": runs.get_run(run_id).status})
            raise ApiDomainError("multi_agent_failed", "团队执行未完成，已保留完成步骤，请查看运行轨迹。", status=502) from exc
        finally:
            task.active_run_id = None
            active_team_rooms.discard(room.room_id)
        return {"room_id": room.room_id, "task_id": task_id, "run_id": run_id, "architecture": result.architecture, "route_reason": decision.reason, "status": result.status, "final": result.final, "turns": [{"agent_id": turn.agent_id, "responsibility": turn.responsibility, "content": turn.content, "sequence": turn.sequence} for turn in result.turns]}

    @app.get("/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(request: Request, task_id: str) -> Any:
        task = tasks.get(validate_identifier(task_id, "task"))
        if task is None:
            raise ApiDomainError("not_found", "task not found", status=404)
        _room_for_request(request, task.room_id)
        return _dump(task)

    async def _followup(request: Request, task_id: str, body: FollowupRequest, idempotency_key: str | None) -> Any:
        task = tasks.get(validate_identifier(task_id, "task"))
        if task is None:
            raise ApiDomainError("not_found", "task not found", status=404)
        _room_for_request(request, task.room_id)
        if body.expected_task_version is not None and body.expected_task_version != task.version:
            raise ApiDomainError("version_conflict", "task version is stale", status=409, details={"row_version": task.version})
        message = repository.save_message(task.room_id, body.content, role="user", idempotency_key=idempotency_key)
        _record_message_event(message)
        task.version += 1
        return {"task": _dump(task), "message": _dump(message), "status": "accepted", "run_id": task.active_run_id}

    @app.post("/tasks/{task_id}/followups", response_model=FollowupResponse)
    async def create_followup(request: Request, task_id: str, body: FollowupRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> Any:
        return await _followup(request, task_id, body, idempotency_key)

    @app.post("/tasks/{task_id}/messages", response_model=FollowupResponse)
    async def create_task_message(request: Request, task_id: str, body: FollowupRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> Any:
        return await _followup(request, task_id, body, idempotency_key)

    @app.post("/runs", status_code=201, response_model=RunResponse)
    async def create_run(body: RunCreateRequest) -> Any:
        run_id = validate_identifier(body.run_id, "run") if body.run_id else new_identifier("run")
        state = runs.register_run(run_id, plan_revision=body.plan_revision, status=body.status)
        if body.task_id:
            task = tasks.get(validate_identifier(body.task_id, "task"))
            if task is None:
                raise ApiDomainError("not_found", "task not found", status=404)
            task.active_run_id = state.run_id
        return _dump(state)

    @app.get("/runs/{run_id}", response_model=RunResponse)
    async def get_run(run_id: str) -> Any:
        try:
            return _dump(runs.get_run(run_id))
        except ControlError as exc:
            raise ApiDomainError("not_found", str(exc), status=404) from exc

    @app.post("/commands/{command_id}", response_model=CommandResponse)
    async def execute_command(command_id: str, body: CommandRequest) -> Any:
        command_id = validate_identifier(command_id, "operation")
        if command_id in commands:
            return commands[command_id]
        try:
            if body.action == "start":
                state = runs.start(body.run_id, expected_row_version=body.expected_row_version)
            elif body.expected_control_epoch is None:
                raise ApiDomainError("invalid_request", "expected_control_epoch is required", status=422)
            elif body.action == "pause":
                state = runs.pause(body.run_id, expected_row_version=body.expected_row_version, expected_control_epoch=body.expected_control_epoch)
            else:
                state = runs.cancel(body.run_id, expected_row_version=body.expected_row_version, expected_control_epoch=body.expected_control_epoch)
        except ControlConflictError as exc:
            try:
                current = runs.get_run(body.run_id)
                details = {"expected_row_version": body.expected_row_version, "expected_control_epoch": body.expected_control_epoch, "row_version": current.row_version, "control_epoch": current.control_epoch}
            except ControlError:
                details = {"expected_row_version": body.expected_row_version, "expected_control_epoch": body.expected_control_epoch}
            raise ApiDomainError("version_conflict", str(exc), status=409, details=details) from exc
        except (ControlError, RunNotClaimableError) as exc:
            raise ApiDomainError("command_rejected", str(exc), status=409) from exc
        result = {"command_id": command_id, "status": "accepted", "run": _dump(state)}
        commands[command_id] = result
        return result

    @app.post("/assets", response_model=AssetUploadResponse, status_code=201)
    async def upload_asset(request: Request, body: AssetUploadRequest) -> Any:
        _require_space(request, body.space_id)
        try:
            content = base64.b64decode(body.content_base64, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ApiDomainError("invalid_asset", "content_base64 is invalid", status=422) from exc
        try:
            result = asset_store.ingest(body.filename, content, evaluate=body.evaluate, space_id=body.space_id)
        except (ValueError, UnicodeError) as exc:
            raise ApiDomainError("invalid_asset", str(exc), status=422) from exc
        asset_spaces[result.record.asset_id] = body.space_id
        return {"asset_id": result.record.asset_id, "media_type": result.record.media_type, "content_hash": result.record.content_hash, "size_bytes": result.record.size_bytes, "object_path": result.object_path, "chunks": list(result.chunks), "evaluation_requested": result.evaluation_requested, "evaluation_status": "requested" if result.evaluation_requested else "not_requested"}

    @app.get("/assets/{asset_id}")
    async def get_asset(request: Request, asset_id: str) -> Any:
        owner_space = asset_spaces.get(asset_id)
        if owner_space is None:
            try:
                owner_space = asset_store.read_asset_space(asset_id)
            except (AttributeError, FileNotFoundError):
                owner_space = None
        if owner_space:
            _require_space(request, owner_space)
        try:
            content = asset_store.read_asset(asset_id)
        except FileNotFoundError as exc:
            raise ApiDomainError("not_found", "asset not found", status=404) from exc
        return {"asset_id": asset_id, "size_bytes": len(content), "content_base64": base64.b64encode(content).decode("ascii")}

    @app.get("/artifacts/{artifact_id}")
    async def get_artifact(artifact_id: str) -> Any:
        raise ApiDomainError("capability_not_ready", "artifact API is reserved for the execution slice", status=501, details={"artifact_id": artifact_id, "status": "not_available"})

    return app


app = create_app()
