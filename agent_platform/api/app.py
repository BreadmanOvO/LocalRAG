"""FastAPI composition layer for the v1.8 in-memory contracts.

The app adapts D06-D10 stores; it does not start model loops, workers, or
PostgreSQL connections.  Persistence adapters can replace the injected
stores without changing this wire contract.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse

from agent_platform.contracts.identity import RoomEventCursor, new_identifier, validate_identifier
from agent_platform.conversations.repository import ConflictError, ConversationRepository, NotFoundError, RepositoryError
from agent_platform.runtime.control import ControlConflictError, ControlError, RunController, RunNotClaimableError
from agent_platform.runtime.event_store import EventConflictError, EventStore
from agent_platform.personas import PersonaProfile, default_registry
from agent_platform.routing import ArchitectureSpec, PlanCompiler, TaskProfile

from .schemas import (
    AssistantMessageRequest, AssistantMessageResponse, CommandRequest, CommandResponse, ErrorEnvelope, EventListResponse, EventResponse,
    FollowupRequest, FollowupResponse, HealthResponse, MessageCreateRequest,
    MemberListResponse, MessageListResponse, MessageResponse, RoomCreateRequest, RoomListResponse, RoomResponse,
    PersonaCreateRequest, PersonaResponse, PersonaBindingResponse, RoleListResponse, PlanCompileRequest, PlanCompileResponse,
    RunCreateRequest, RunResponse, TaskCreateRequest, TaskResponse,
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


def create_app(*, repository: ConversationRepository | None = None, events: EventStore | None = None, runs: RunController | None = None) -> FastAPI:
    """Create an API app with injectable in-memory stores for tests and demos."""
    repository = repository or ConversationRepository()
    events = events or EventStore()
    runs = runs or RunController()
    tasks: dict[str, _Task] = {}
    personas = default_registry()
    planner = PlanCompiler()
    room_keys: dict[str, tuple[str, str]] = {}
    assistant_keys: dict[str, tuple[str, str, str]] = {}
    commands: dict[str, dict[str, Any]] = {}

    def _record_message_event(message: Any) -> None:
        """Project each saved message into the room event stream exactly once."""
        events.append(
            message.room_id,
            "message_saved",
            event_id=f"event-message-{message.message_id}",
            payload={"message_id": message.message_id, "role": message.role},
        )

    app = FastAPI(title="LocalRAG Agent Platform API", version="1.8.0")
    app.state.repository, app.state.events, app.state.runs, app.state.tasks, app.state.personas, app.state.planner = repository, events, runs, tasks, personas, planner

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
    async def create_room(body: RoomCreateRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> Any:
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
    async def list_rooms(space_id: str | None = None) -> Any:
        return {"items": [_dump(room) for room in repository.list_rooms(space_id)]}

    @app.post("/assistant/messages", status_code=201, response_model=AssistantMessageResponse)
    async def assistant_message(
        body: AssistantMessageRequest,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> Any:
        """Persist the first assistant message and room in one repository boundary."""
        if idempotency_key and idempotency_key in assistant_keys:
            old_space, room_id, old_content = assistant_keys[idempotency_key]
            if old_space != body.space_id or old_content != body.content.strip():
                raise ApiDomainError("idempotency_conflict", "idempotency key payload differs", status=409)
            room = repository.get_room(room_id)
            messages = repository.list_messages(room_id)
            if messages:
                _record_message_event(messages[0])
            return {"room": _dump(room), "message": _dump(messages[0]), "created": False}
        if body.room_id:
            room = repository.get_room(body.room_id)
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
    async def get_room(room_id: str) -> Any:
        return _dump(repository.get_room(room_id))

    @app.post("/rooms/{room_id}/messages", status_code=201, response_model=MessageResponse)
    async def create_message(room_id: str, body: MessageCreateRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> Any:
        message = repository.save_message(room_id, body.content, role=body.role, message_id=body.message_id, idempotency_key=idempotency_key)
        _record_message_event(message)
        return _dump(message)

    @app.get("/rooms/{room_id}/messages", response_model=MessageListResponse)
    async def list_messages(room_id: str, after: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=1000)) -> Any:
        items = repository.list_messages(room_id, after=after, limit=limit)
        next_cursor = items[-1].room_sequence if items else after
        return {"items": [_dump(item) for item in items], "next": next_cursor}

    @app.get("/rooms/{room_id}/members", response_model=MemberListResponse)
    async def list_members(room_id: str) -> Any:
        return {"items": [_dump(item) for item in repository.list_members(room_id)]}


    @app.get("/rooms/{room_id}/events", response_model=EventListResponse)
    async def list_events(room_id: str, after: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=1000)) -> Any:
        cursor = RoomEventCursor(validate_identifier(room_id, "room"), after)
        return {"items": [_dump(item) for item in events.read_after(cursor, limit=limit)], "next": events.snapshot(room_id).cursor.room_sequence}

    @app.get("/rooms/{room_id}/events/stream")
    async def stream_events(room_id: str, after: int = Query(default=0, ge=0)) -> StreamingResponse:
        snapshot = events.read_after(RoomEventCursor(validate_identifier(room_id, "room"), after))
        body = "".join(f"data: {json.dumps(_dump(item), ensure_ascii=False, separators=(',', ':'))}\n\n" for item in snapshot)
        return StreamingResponse(iter([body]), media_type="text/event-stream")

    @app.get("/rooms/{room_id}/events/{event_id}", response_model=EventResponse)
    async def get_event(room_id: str, event_id: str) -> Any:
        validate_identifier(room_id, "room")
        for item in events.read_after(RoomEventCursor(validate_identifier(room_id, "room"), 0), limit=1000):
            if item.identity.event_id == event_id:
                return _dump(item)
        raise ApiDomainError("not_found", "event not found", status=404)

    @app.post("/tasks", status_code=201, response_model=TaskResponse)
    async def create_task(body: TaskCreateRequest) -> Any:
        repository.get_room(body.room_id)
        task_id = validate_identifier(body.task_id, "task") if body.task_id else new_identifier("task")
        if task_id in tasks:
            raise ApiDomainError("conflict", "task already exists", status=409)
        task = _Task(task_id, body.room_id, body.title.strip())
        tasks[task_id] = task
        return _dump(task)

    @app.get("/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(task_id: str) -> Any:
        task = tasks.get(validate_identifier(task_id, "task"))
        if task is None:
            raise ApiDomainError("not_found", "task not found", status=404)
        return _dump(task)

    async def _followup(task_id: str, body: FollowupRequest, idempotency_key: str | None) -> Any:
        task = tasks.get(validate_identifier(task_id, "task"))
        if task is None:
            raise ApiDomainError("not_found", "task not found", status=404)
        if body.expected_task_version is not None and body.expected_task_version != task.version:
            raise ApiDomainError("version_conflict", "task version is stale", status=409, details={"row_version": task.version})
        message = repository.save_message(task.room_id, body.content, role="user", idempotency_key=idempotency_key)
        _record_message_event(message)
        task.version += 1
        return {"task": _dump(task), "message": _dump(message), "status": "accepted", "run_id": task.active_run_id}

    @app.post("/tasks/{task_id}/followups", response_model=FollowupResponse)
    async def create_followup(task_id: str, body: FollowupRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> Any:
        return await _followup(task_id, body, idempotency_key)

    @app.post("/tasks/{task_id}/messages", response_model=FollowupResponse)
    async def create_task_message(task_id: str, body: FollowupRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> Any:
        return await _followup(task_id, body, idempotency_key)

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

    @app.get("/assets/{asset_id}")
    async def get_asset(asset_id: str) -> Any:
        raise ApiDomainError("capability_not_ready", "asset API is reserved for D23-D24", status=501, details={"asset_id": asset_id, "status": "not_available"})

    @app.get("/artifacts/{artifact_id}")
    async def get_artifact(artifact_id: str) -> Any:
        raise ApiDomainError("capability_not_ready", "artifact API is reserved for the execution slice", status=501, details={"artifact_id": artifact_id, "status": "not_available"})

    return app


app = create_app()
