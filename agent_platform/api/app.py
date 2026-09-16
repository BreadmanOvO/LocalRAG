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
import hashlib
import inspect
from threading import RLock, Event as ThreadEvent, Thread
from contextlib import nullcontext
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.concurrency import run_in_threadpool

from agent_platform.contracts.identity import RoomEventCursor, new_identifier, validate_identifier
from agent_platform.conversations.repository import ConflictError, ConversationRepository, NotFoundError, RepositoryError, RoomClosedError
from agent_platform.conversations.sql_repository import SqlAlchemyConversationRepository
from agent_platform.runtime.control import ControlConflictError, ControlError, RunController, RunControlState, RunNotClaimableError
from agent_platform.runtime.event_store import EventConflictError, EventStore
from agent_platform.runtime.sql_event_store import SqlAlchemyEventStore
from agent_platform.runtime.sql_runtime_store import SqlRuntimeStore
from agent_platform.worker import TeamWorker
from agent_platform.personas import PersonaProfile, RoleSpec, default_registry
from agent_platform.routing import ArchitectureSpec, PlanCompiler, TaskProfile, TaskRouter
from agent_platform.runtime.multi_agent import AgentTurn, CloudTeamRuntime, ModelRoutingError, TeamModelSnapshot
from agent_platform.runtime.durable_team import DurableTeamStore, RoomLeaseBusy
from agent_platform.runtime.team_plan import build_team_plan
from agent_platform.runtime.context_engineering import prepare_room_memory
from agent_platform.runtime.error_details import serialize_exception
from agent_platform.capability_packs import ObjectStore, object_store_from_env
from agent_platform.capability_packs.asset_ingestion import AssetIngestionService, configured_vision
from agent_platform.integrations.model_config_store import ModelConfigError, ModelConfigStore
from .auth import AuthConfigError, BearerAuthenticator, Principal, env_auth_required

from .schemas import (
    AssistantMessageRequest, AssistantMessageResponse, CommandRequest, CommandResponse, ErrorEnvelope, EventListResponse, EventResponse,
    FollowupRequest, FollowupResponse, HealthResponse, MessageCreateRequest,
    MemberListResponse, MessageListResponse, MessageResponse, RoomCreateRequest, RoomListResponse, RoomResponse,
    PersonaCreateRequest, PersonaResponse, PersonaBindingResponse, RoleListResponse, PlanCompileRequest, PlanCompileResponse,
    RunCreateRequest, RunResponse, TaskCreateRequest, TaskResponse, MultiAgentExecuteRequest, MultiAgentExecuteResponse,
    AssetUploadRequest, AssetUploadResponse, ModelBindingUpdateRequest, ModelSettingsResponse, ModelProfileRequest, AgentConfigRequest, ModelCatalogResponse, ModelDiscoveryRequest, ModelDiscoveryResponse,
    AssetIngestionResponse, AssetIngestionListResponse, AssetSearchResponse, ModelVerificationResponse, ModelProfileCloneResponse, ArtifactListResponse,
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


def _artifact_descriptors(value: Any) -> list[dict[str, Any]]:
    """Normalize event artifact references without assuming a storage backend.

    Runtime events intentionally keep artifact references opaque.  A provider
    may emit a bare id, a descriptor object, or a nested ``artifacts`` list;
    the room projection accepts all three forms and keeps unknown fields out of
    the public response.
    """
    if value is None:
        return []
    if isinstance(value, str):
        value = value.strip()
        return [{"artifact_id": value}] if value else []
    if isinstance(value, dict):
        if any(key in value for key in ("artifact_id", "id", "ref", "artifact_ref")):
            return [dict(value)]
        nested = value.get("artifacts")
        return _artifact_descriptors(nested) if nested is not None else []
    if isinstance(value, (list, tuple, set)):
        descriptors: list[dict[str, Any]] = []
        for item in value:
            descriptors.extend(_artifact_descriptors(item))
        return descriptors
    return []


def _artifact_text(value: Any) -> str:
    """Provide a compact, deterministic text representation for the card."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError):
        return str(value)


def _format_asset_context(hits: list[dict[str, Any]], *, max_chars: int = 12000) -> tuple[str, list[str]]:
    """Turn asset search hits into bounded, auditable prompt context."""
    sections: list[str] = []
    source_ids: list[str] = []
    used = 0
    for index, hit in enumerate(hits[:5], start=1):
        if not isinstance(hit, dict):
            continue
        text = str(hit.get("text") or "").strip()
        metadata = hit.get("metadata") if isinstance(hit.get("metadata"), dict) else {}
        source = str(metadata.get("source") or metadata.get("title") or "资料")
        locator = str(metadata.get("locator") or "正文")
        source_id = str(metadata.get("source_id") or "").strip()
        if source_id and source_id not in source_ids:
            source_ids.append(source_id)
        if not text:
            continue
        section = f"[资料 {index}] {source} · {locator}\n{text[:3000]}"
        if used + len(section) > max_chars:
            remaining = max_chars - used
            if remaining < 120:
                break
            section = section[:remaining]
        sections.append(section)
        used += len(section)
        if used >= max_chars:
            break
    if not sections:
        return "", source_ids
    return (
        "知识库检索结果（仅可作为有出处的参考，不要把检索结果之外的内容伪装成资料事实）：\n"
        + "\n\n".join(sections),
        source_ids,
    )


def _project_room_artifacts(history: Any) -> list[dict[str, Any]]:
    """Build room-local artifact cards from append-only execution events.

    This is deliberately an event projection, not an artifact store lookup:
    callers can inspect outputs immediately, while durable/object-backed
    artifacts may be added later without changing the room API shape.
    """
    projected: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for event in history:
        payload = event.payload if isinstance(getattr(event, "payload", None), dict) else {}
        output = payload.get("output")
        descriptors: list[dict[str, Any]] = []
        descriptors.extend(_artifact_descriptors(getattr(event, "produces", ())))
        for key in ("produces", "artifact_refs", "artifacts"):
            descriptors.extend(_artifact_descriptors(payload.get(key)))

        # A completed step without an explicit reference still has a useful
        # room artifact: its output.  The event id keeps this synthetic id
        # stable across refreshes and replay.
        if not descriptors and getattr(event, "event_type", "") == "step_completed" and _artifact_text(output).strip():
            descriptors = [{"artifact_id": f"artifact-{event.identity.event_id}"}]
        if not descriptors:
            continue

        event_id = event.identity.event_id
        for descriptor in descriptors:
            artifact_id = str(
                descriptor.get("artifact_id")
                or descriptor.get("id")
                or descriptor.get("ref")
                or descriptor.get("artifact_ref")
                or f"artifact-{event_id}"
            ).strip()
            if not artifact_id:
                continue
            descriptor_output = descriptor.get("output", descriptor.get("content", output))
            content = _artifact_text(descriptor_output)
            title = str(descriptor.get("title") or descriptor.get("name") or artifact_id)
            item = {
                "artifact_id": artifact_id,
                "title": title,
                "artifact_type": str(descriptor.get("type") or descriptor.get("artifact_type") or "step_output"),
                "content": content,
                "output": descriptor_output,
                "source_event_id": event_id,
                "source_step_id": event.step_id or descriptor.get("step_id"),
                "source_agent_id": payload.get("agent_id") or descriptor.get("agent_id"),
                "source_agent_name": payload.get("display_name") or payload.get("agent_name") or descriptor.get("agent_name"),
                "run_id": event.run_id,
                "task_id": event.task_id,
                "timestamp": event.timestamp,
                "is_final": bool(payload.get("is_final") or descriptor.get("is_final")),
            }
            if artifact_id not in projected:
                order.append(artifact_id)
            # Re-emitting the same reference is an update; the latest event is
            # the authoritative source while preserving first-seen ordering.
            projected[artifact_id] = item
    return [projected[artifact_id] for artifact_id in order if artifact_id in projected]


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID") or f"req-{uuid4().hex}"


def _error(request: Request, exc: ApiDomainError) -> JSONResponse:
    payload = ErrorEnvelope(code=exc.code, message=str(exc), details=exc.details, request_id=_request_id(request), control_epoch=exc.details.get("control_epoch"), row_version=exc.details.get("row_version"))
    return JSONResponse(status_code=exc.status, content=payload.model_dump())


def create_app(*, repository: ConversationRepository | SqlAlchemyConversationRepository | None = None, events: EventStore | SqlAlchemyEventStore | None = None, runs: RunController | None = None, team_runtime: CloudTeamRuntime | None = None, database_url: str | None = None, asset_store: ObjectStore | None = None, model_config_store: ModelConfigStore | None = None, auth_required: bool | None = None, auth_tokens: dict[str, str | list[str] | tuple[str, ...]] | None = None) -> FastAPI:
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
    asset_store = asset_store or object_store_from_env()
    room_keys: dict[str, tuple[str, str]] = {}
    assistant_keys: dict[str, tuple[str, str, str]] = {}
    commands: dict[str, dict[str, Any]] = {}
    active_team_rooms: set[str] = set()
    room_model_snapshots: dict[str, TeamModelSnapshot] = {}
    room_runtimes: dict[str, CloudTeamRuntime] = {}
    room_model_snapshot_lock = RLock()
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
    model_config = model_config_store or ModelConfigStore()
    runtime_store = SqlRuntimeStore(repository.engine, create_schema=repository.engine.dialect.name == "sqlite") if isinstance(repository, SqlAlchemyConversationRepository) else None
    durable_team = DurableTeamStore(repository.engine) if runtime_store is not None else None
    if runtime_store is not None and repository.engine.dialect.name == "sqlite":
        runtime_store.ensure_schema()

    def _run_state(run_id: str):
        if runtime_store:
            row = runtime_store.get_run(run_id)
            if row:
                persisted = RunControlState(**{key: row[key] for key in ("run_id", "plan_revision", "status", "control_epoch", "row_version")})
                try:
                    local = runs.get_run(run_id)
                except ControlError:
                    local = None
                if local is None or persisted.row_version >= local.row_version:
                    return runs.restore_run(persisted)
        return runs.get_run(run_id)

    def _record_message_event(message: Any) -> None:
        """Project each saved message into the room event stream exactly once."""
        events.append(
            message.room_id,
            "message_saved",
            event_id=f"event-message-{message.message_id}",
            payload={"message_id": message.message_id, "role": message.role},
        )

    def _release_team_room(room_id: str) -> None:
        with room_model_snapshot_lock:
            active_team_rooms.discard(room_id)

    app = FastAPI(title="LocalRAG Agent Platform API", version="1.8.0")
    app.state.asset_ingestion = None
    ingestion_lock = RLock()

    def _ingestion() -> AssetIngestionService:
        with ingestion_lock:
            if app.state.asset_ingestion is None:
                app.state.asset_ingestion = AssetIngestionService(asset_store, vision=configured_vision(model_config))
            return app.state.asset_ingestion
    app.state.repository, app.state.events, app.state.runs, app.state.tasks, app.state.personas, app.state.planner, app.state.team_runtime, app.state.asset_store, app.state.team_worker, app.state.runtime_store = repository, events, runs, tasks, personas, planner, team_runtime, asset_store, team_worker, runtime_store

    @app.on_event("shutdown")
    async def _shutdown_worker() -> None:
        team_worker.close()
        if app.state.asset_ingestion is not None:
            await run_in_threadpool(app.state.asset_ingestion.close)

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

    def _require_admin(request: Request) -> None:
        """Require the wildcard space grant for credentialed admin actions."""
        principal = _principal(request)
        if auth_required and (principal is None or "*" not in principal.spaces):
            raise ApiDomainError("admin_required", "管理员凭证才能执行此操作", status=403)

    def _room_for_request(request: Request, room_id: str) -> Any:
        room = repository.get_room(room_id)
        _require_space(request, room.space_id)
        if room.status == "deleted":
            raise ApiDomainError("not_found", "房间已删除", status=404)
        return room

    def _room_persona_theme(room_id: str, requested: str | None) -> str | None:
        history = events.read_after(RoomEventCursor(room_id=room_id, room_sequence=0))
        previous = next((item.payload.get("persona_theme") for item in history if item.event_type == "room_persona_selected"), None)
        if previous and requested and previous != requested:
            raise ApiDomainError("persona_theme_conflict", "房间人设已固定，请新建房间使用其他人设", status=409)
        if previous:
            return str(previous)
        if requested:
            events.append(room_id, "room_persona_selected", event_id=f"event-theme-{room_id}", payload={"persona_theme": requested})
        return requested

    def _room_architecture(room_id: str, requested: str = "auto") -> str:
        history = events.read_after(RoomEventCursor(room_id=room_id, room_sequence=0))
        previous = next((item.payload.get("architecture") for item in history if item.event_type == "room_architecture_selected"), None)
        chosen = str(previous or requested or "auto")
        if previous and requested not in {"", "auto", str(previous)}:
            raise ApiDomainError("architecture_conflict", "房间协作模式已固定，请新建房间使用其他模式", status=409)
        if not previous:
            events.append(room_id, "room_architecture_selected", event_id=f"event-architecture-{room_id}", payload={"architecture": chosen})
        return chosen

    def _runtime_for_settings() -> CloudTeamRuntime:
        runtime = app.state.team_runtime
        if runtime is None:
            try:
                runtime = CloudTeamRuntime.from_config()
            except (RuntimeError, OSError) as exc:
                raise ApiDomainError("capability_not_ready", str(exc), status=503) from exc
            app.state.team_runtime = runtime
        return runtime

    def _runtime_for_room(room_id: str) -> CloudTeamRuntime:
        """Load current settings, falling back only to this room's frozen runtime."""
        runtime = app.state.team_runtime
        if runtime is not None:
            return runtime
        try:
            runtime = CloudTeamRuntime.from_config()
        except (RuntimeError, OSError) as exc:
            runtime = room_runtimes.get(room_id)
            if runtime is None:
                raise ApiDomainError("capability_not_ready", str(exc), status=503) from exc
        app.state.team_runtime = runtime
        return runtime

    @app.exception_handler(ApiDomainError)
    async def _handle_domain(request: Request, exc: ApiDomainError) -> JSONResponse:
        return _error(request, exc)

    @app.exception_handler(RoomClosedError)
    async def _handle_closed(request: Request, exc: RoomClosedError):
        return _error(request, ApiDomainError("room_closed", "房间已关闭，请重新打开后继续", status=409))

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
        contract = "v1.8-postgresql" if runtime_store is not None and isinstance(repository, SqlAlchemyConversationRepository) and repository.engine.dialect.name == "postgresql" else "v1.8-sqlite" if runtime_store is not None else "v1.8-inmemory"
        return {"status": "ok", "contract": contract}

    @app.get("/settings/models", response_model=ModelSettingsResponse)
    async def model_settings(request: Request) -> Any:
        _require_admin(request)
        return _runtime_for_settings().model_settings()

    @app.put("/settings/models/{agent_id}", response_model=ModelSettingsResponse)
    async def update_model_setting(request: Request, agent_id: str, body: ModelBindingUpdateRequest) -> Any:
        _require_admin(request)
        runtime = _runtime_for_settings()
        try:
            runtime.update_model_binding(agent_id, source_agent_id=body.source_agent_id, tier=body.tier)
        except KeyError as exc:
            raise ApiDomainError("not_found", "agent or model choice not found", status=404) from exc
        return runtime.model_settings()

    @app.get("/settings/model-catalog", response_model=ModelCatalogResponse)
    async def model_catalog(request: Request) -> Any:
        _require_admin(request)
        return model_config.public()

    @app.put("/settings/model-profiles/{profile_id}", response_model=ModelCatalogResponse)
    async def save_model_profile(request: Request, profile_id: str, body: ModelProfileRequest) -> Any:
        _require_admin(request)
        if profile_id != body.profile_id:
            raise ApiDomainError("invalid_request", "profile_id in path and body must match", status=422)
        try:
            result = model_config.upsert_profile(body.model_dump())
        except ModelConfigError as exc:
            raise ApiDomainError("invalid_model_config", str(exc), status=422) from exc
        app.state.team_runtime = None
        return result

    @app.delete("/settings/model-profiles/{profile_id}", response_model=ModelCatalogResponse)
    async def remove_model_profile(request: Request, profile_id: str) -> Any:
        _require_admin(request)
        try:
            result = model_config.delete_profile(profile_id)
        except KeyError as exc:
            raise ApiDomainError("not_found", "model profile not found", status=404) from exc
        except ModelConfigError as exc:
            raise ApiDomainError("model_in_use", str(exc), status=409) from exc
        app.state.team_runtime = None
        return result

    @app.post("/settings/model-profiles/{profile_id}/clone", response_model=ModelProfileCloneResponse)
    async def clone_model_profile(request: Request, profile_id: str) -> Any:
        _require_admin(request)
        try:
            clone_id, catalog = model_config.clone_profile(profile_id)
        except KeyError as exc:
            raise ApiDomainError("not_found", "model profile not found", status=404) from exc
        except ModelConfigError as exc:
            raise ApiDomainError("invalid_model_config", str(exc), status=422) from exc
        app.state.team_runtime = None
        return {"profile_id": clone_id, "catalog": catalog}

    @app.post("/settings/model-profiles/{profile_id}/verify", response_model=ModelVerificationResponse)
    async def verify_model_profile(request: Request, profile_id: str) -> Any:
        _require_admin(request)
        profile = model_config.load().get("model_profiles", {}).get(profile_id)
        if not profile:
            raise ApiDomainError("not_found", "model profile not found", status=404)
        key = str(profile.get("api_key", "")).strip() or os.environ.get(str(profile.get("api_key_env", "")).strip(), "")
        if not key or not profile.get("base_url") or not profile.get("model"):
            raise ApiDomainError("model_not_ready", "请先填写 URL、模型名称和 API Key", status=422)
        try:
            # Verification performs a real outbound request just like model
            # discovery; apply the same SSRF policy before constructing the
            # provider client.  Development-only synthetic DNS compatibility
            # is handled inside the shared host check.
            parsed_base_url = ModelConfigStore._parse_discovery_url(str(profile["base_url"]))
            safe_addresses = ModelConfigStore._resolve_safe_discovery_host(parsed_base_url.hostname)
        except ModelConfigError as exc:
            raise ApiDomainError("model_verification_failed", str(exc), status=502) from exc
        try:
            from openai import OpenAI
            with ModelConfigStore._pin_discovery_resolution(parsed_base_url.hostname, safe_addresses):
                with OpenAI(api_key=key, base_url=profile["base_url"], timeout=20, max_retries=0) as client:
                    response = client.chat.completions.create(
                        model=profile["model"],
                        messages=[{"role": "user", "content": "Reply with a short confirmation: OK"}],
                        max_tokens=16,
                    )
            if not response.choices:
                raise RuntimeError("模型未返回候选结果")
            choice = response.choices[0]
            content = choice.message.content or ""
            # Some compatible providers may consume the tiny probe budget before
            # emitting text; a valid choice still proves authentication/routing.
            if not content.strip() and getattr(choice, "finish_reason", "") not in {"length", "stop"}:
                raise RuntimeError("模型返回空响应")
        except Exception as exc:
            status_code = getattr(exc, "status_code", None) or getattr(exc, "status", None)
            response = getattr(exc, "response", None)
            if status_code is None and response is not None:
                status_code = getattr(response, "status_code", None)
            status_code = int(status_code) if str(status_code or "").isdigit() else None
            if status_code == 402:
                raise ApiDomainError(
                    "model_quota_exhausted",
                    "连接验证失败：模型供应商账户余额不足或额度已用尽，请充值或改用有额度的模型",
                    status=402,
                ) from exc
            if status_code in {401, 403}:
                raise ApiDomainError(
                    "model_auth_failed",
                    "连接验证失败：API Key 无效、过期或没有该模型权限",
                    status=status_code,
                ) from exc
            if status_code == 404:
                raise ApiDomainError(
                    "model_not_found",
                    "连接验证失败：模型不存在，请从模型列表重新选择模型名称",
                    status=404,
                ) from exc
            raise ApiDomainError("model_verification_failed", f"连接验证失败：{type(exc).__name__}", status=502) from exc
        return {"profile_id": profile_id, "verified": True, "message": "连接成功。请在编辑表单中勾选“允许用于新任务”并保存，模型才会参与路由。", "model": profile["model"]}

    @app.put("/settings/agents/{agent_id}", response_model=ModelCatalogResponse)
    async def save_agent_config(request: Request, agent_id: str, body: AgentConfigRequest) -> Any:
        _require_admin(request)
        if agent_id != body.agent_id:
            raise ApiDomainError("invalid_request", "agent_id in path and body must match", status=422)
        try:
            result = model_config.upsert_agent(body.model_dump())
        except ModelConfigError as exc:
            raise ApiDomainError("invalid_agent_config", str(exc), status=422) from exc
        app.state.team_runtime = None
        return result

    @app.delete("/settings/agents/{agent_id}", response_model=ModelCatalogResponse)
    async def remove_agent_config(request: Request, agent_id: str) -> Any:
        _require_admin(request)
        try:
            result = model_config.delete_agent(agent_id)
        except KeyError as exc:
            raise ApiDomainError("not_found", "agent not found", status=404) from exc
        app.state.team_runtime = None
        return result

    @app.post("/settings/model-discovery", response_model=ModelDiscoveryResponse)
    async def discover_models(request: Request, body: ModelDiscoveryRequest) -> Any:
        _require_admin(request)
        try:
            api_key = model_config.discovery_key(body.profile_id, body.api_key, base_url=body.base_url)
            items = ModelConfigStore.discover_models(body.base_url, api_key)
        except ModelConfigError as exc:
            raise ApiDomainError("model_discovery_failed", str(exc), status=502) from exc
        return {"items": items}

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
        if body.role_id == "custom":
            # A custom role is a first-class role in the current persona catalog.
            # Its capabilities remain bounded until an Agent binding selects it.
            custom_role_id = f"custom-{validate_identifier(body.persona_id, 'persona')}"
            personas.add_role(RoleSpec(custom_role_id, body.display_name, "自定义部门", (body.tone or "承担用户定义职责",), ("chat", "analysis")))
            body = body.model_copy(update={"role_id": custom_role_id})
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
        return {"items": [_dump(room) for room in rooms if room.status != "deleted"]}

    @app.post("/assistant/messages", status_code=201, response_model=AssistantMessageResponse)
    async def assistant_message(
        request: Request,
        body: AssistantMessageRequest,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> Any:
        """Save a user instruction and start execution without a second UI action."""
        if body.room_id:
            room = _room_for_request(request, body.room_id)
        else:
            _require_space(request, body.space_id)
            room = None
        if idempotency_key:
            candidates = [room] if room else repository.list_rooms(body.space_id)
            for candidate in candidates:
                old_message = next((m for m in repository.list_messages(candidate.room_id) if m.idempotency_key == idempotency_key), None)
                if old_message:
                    _room_for_request(request, candidate.room_id)
                    if old_message.content != body.content.strip():
                        raise ApiDomainError("idempotency_conflict", "idempotency key payload differs", status=409)
                    return {"room": _dump(candidate), "message": _dump(old_message), "created": False}
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
            if room.room_id in active_team_rooms or (durable_team and durable_team.active(room.room_id)):
                raise ApiDomainError("run_active", "当前任务仍在执行，请完成后继续追问", status=409)
            message = repository.save_message(room.room_id, body.content, role="user", idempotency_key=idempotency_key)
            _record_message_event(message)
            await _start_saved_message(request, room.room_id, message)
            return {"room": _dump(room), "message": _dump(message), "created": False}
        title = body.title.strip() or body.content.strip().splitlines()[0][:80]
        room, message = repository.create_room_with_message(body.space_id, title, body.content, idempotency_key=idempotency_key)
        _room_persona_theme(room.room_id, body.persona_theme)
        _room_architecture(room.room_id, body.architecture)
        _record_message_event(message)
        if idempotency_key:
            assistant_keys[idempotency_key] = (body.space_id, room.room_id, body.content.strip())
        await _start_saved_message(request, room.room_id, message)
        return {"room": _dump(room), "message": _dump(message), "created": True}

    async def _start_saved_message(request: Request, room_id: str, message: Any, *, resume=False) -> Any:
        try:
            return await _execute_multi_agent(request, room_id, MultiAgentExecuteRequest(goal=message.content, background=True,
                architecture=_room_architecture(room_id)), saved_message=message, resume=resume)
        except (ApiDomainError, ValueError, RuntimeError) as exc:
            if isinstance(exc, ApiDomainError) and exc.code == "run_active":
                raise
            details = serialize_exception(exc, phase="task_start")
            reason = str(exc) if isinstance(exc, (ApiDomainError, ModelRoutingError)) else "请检查模型和角色配置后重试"
            events.append(room_id, "task_start_failed", payload={"message_id": message.message_id, **details, "error": reason})
            return {"status": "blocked"}

    @app.post("/rooms/{room_id}/start")
    async def start_saved_task(request: Request, room_id: str) -> Any:
        _room_for_request(request, room_id)
        messages = repository.list_messages(room_id)
        message = next((item for item in reversed(messages) if item.role == "user"), None)
        if message is None:
            raise ApiDomainError("invalid_request", "房间中没有待执行任务", status=422)
        return await _start_saved_message(request, room_id, message, resume=True)

    @app.get("/rooms/{room_id}", response_model=RoomResponse)
    async def get_room(request: Request, room_id: str) -> Any:
        return _dump(_room_for_request(request, room_id))

    @app.get("/rooms/{room_id}/execution")
    async def room_execution(request: Request, room_id: str):
        room = _room_for_request(request, room_id)
        history = events.read_after(RoomEventCursor(room_id, 0))
        latest = next((e for e in reversed(history) if e.event_type == "run_started"), None)
        terminal = next((e for e in reversed(history) if latest and e.run_id == latest.run_id and e.event_type in {"run_completed", "run_failed", "run_cancelled"}), None)
        active = durable_team.active(room_id) if durable_team else room_id in active_team_rooms
        messages = repository.list_messages(room_id)
        last_user = next((m for m in reversed(messages) if m.role == "user"), None)
        finished = bool(terminal and terminal.event_type == "run_completed" and last_user and latest.payload.get("message_id") == last_user.message_id)
        persisted = runtime_store.get_run(latest.run_id) if runtime_store and latest else None
        stopped_status = persisted["status"] if persisted and persisted["status"] in {"cancelled", "paused"} else None
        status = stopped_status or ("running" if active else "completed" if finished else "interrupted" if latest else "pending")
        return {"status": status, "run_id": latest.run_id if latest else None,
            "can_resume": bool(last_user and not active and not finished and stopped_status != "cancelled" and room.status == "active")}

    @app.post("/rooms/{room_id}/archive", response_model=RoomResponse)
    async def archive_room(request: Request, room_id: str) -> Any:
        room = _room_for_request(request, room_id)
        if room.room_id in active_team_rooms:
            raise ApiDomainError("run_active", "任务仍在执行，完成或停止后再关闭房间", status=409)
        try:
            with durable_team.exclusive(room_id) if durable_team else nullcontext():
                return _dump(repository.archive_room(room_id))
        except RoomLeaseBusy as exc:
            raise ApiDomainError("run_active", str(exc), status=409) from exc

    @app.post("/rooms/{room_id}/reopen", response_model=RoomResponse)
    async def reopen_room(request: Request, room_id: str) -> Any:
        _room_for_request(request, room_id)
        return _dump(repository.reopen_room(room_id))

    @app.delete("/rooms/{room_id}", response_model=RoomResponse)
    async def delete_room(request: Request, room_id: str) -> Any:
        room = _room_for_request(request, room_id)
        if room.room_id in active_team_rooms:
            raise ApiDomainError("run_active", "任务仍在执行，完成或停止后再删除房间", status=409)
        try:
            with durable_team.exclusive(room_id) if durable_team else nullcontext():
                deleted = repository.delete_room(room_id)
                events.append(room_id, "room_deleted", payload={"status": "deleted"})
                return _dump(deleted)
        except RoomLeaseBusy as exc:
            raise ApiDomainError("run_active", str(exc), status=409) from exc

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
        items = events.read_after(cursor, limit=limit)
        return {"items": [_dump(item) for item in items], "next": items[-1].identity.room_sequence if items else after}

    @app.get("/rooms/{room_id}/events/stream")
    async def stream_events(request: Request, room_id: str, after: int = Query(default=0, ge=0), follow: bool = Query(default=False), timeout: float = Query(default=15.0, ge=0.0, le=60.0), last_event_id: str | None = Header(default=None, alias="Last-Event-ID")) -> StreamingResponse:
        _room_for_request(request, room_id)
        if last_event_id and after == 0 and last_event_id.isdecimal():
            after = int(last_event_id)
        elif last_event_id and after == 0 and hasattr(events, "get_event"):
            prior = events.get_event(last_event_id)
            if prior is not None and prior.identity.room_id == room_id:
                after = prior.identity.room_sequence
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
        if hasattr(events, "get_event"):
            item = events.get_event(event_id)
            if item is not None and item.identity.room_id == room_id:
                return _dump(item)
        else:
            for item in events.read_after(RoomEventCursor(validate_identifier(room_id, "room"), 0), limit=1000):
                if item.identity.event_id == event_id:
                    return _dump(item)
        raise ApiDomainError("not_found", "event not found", status=404)

    @app.get("/rooms/{room_id}/artifacts", response_model=ArtifactListResponse)
    async def list_room_artifacts(request: Request, room_id: str) -> Any:
        """Return only artifacts projected from this room's event stream."""
        _room_for_request(request, room_id)
        history = events.read_after(RoomEventCursor(validate_identifier(room_id, "room"), 0), limit=10000)
        return {"items": _project_room_artifacts(history)}

    @app.post("/tasks", status_code=201, response_model=TaskResponse)
    async def create_task(request: Request, body: TaskCreateRequest) -> Any:
        _room_for_request(request, body.room_id)
        task_id = validate_identifier(body.task_id, "task") if body.task_id else new_identifier("task")
        if task_id in tasks:
            raise ApiDomainError("conflict", "task already exists", status=409)
        task = _Task(task_id, body.room_id, body.title.strip())
        tasks[task_id] = task
        if runtime_store is not None:
            runtime_store.upsert_task(task.task_id, task.room_id, task.title, status=task.status, row_version=task.version, active_run_id=task.active_run_id)
        return _dump(task)

    @app.post("/rooms/{room_id}/multi-agent/execute", response_model=MultiAgentExecuteResponse)
    async def execute_multi_agent(request: Request, room_id: str, body: MultiAgentExecuteRequest) -> Any:
        return await _execute_multi_agent(request, room_id, body)

    async def _execute_multi_agent(request: Request, room_id: str, body: MultiAgentExecuteRequest, *, saved_message=None, resume=False) -> Any:
        _room_for_request(request, room_id)
        token = None
        stopped = ThreadEvent()
        lease_failed = ThreadEvent()
        if durable_team:
            try:
                token = durable_team.claim(room_id)
            except RoomLeaseBusy as exc:
                raise ApiDomainError("run_active", str(exc), status=409) from exc

        def keep_alive():
            while not stopped.wait(20):
                try:
                    durable_team.heartbeat(room_id, token)
                except Exception:
                    lease_failed.set()
                    return

        def release_execution():
            stopped.set()
            if durable_team and token:
                durable_team.release(room_id, token)

        def check_lease():
            if lease_failed.is_set():
                raise RoomLeaseBusy("执行租约续期失败，已停止后续步骤")
            if durable_team:
                durable_team.heartbeat(room_id, token)

        if durable_team:
            Thread(target=keep_alive, daemon=True, name="room-lease").start()
        try:
            result = await _execute_claimed(request, room_id, body, saved_message=saved_message,
                resume=resume, lease_token=token, release_execution=release_execution, check_lease=check_lease)
            if result.get("status") != "queued":
                release_execution()
            return result
        except Exception:
            release_execution()
            raise

    async def _execute_claimed(request: Request, room_id: str, body: MultiAgentExecuteRequest, *, saved_message=None, resume=False, lease_token=None, release_execution=lambda: None, check_lease=lambda: None) -> Any:
        room = _room_for_request(request, room_id)
        if room.status != "active":
            raise ApiDomainError("conflict", "room is not active", status=409)
        task_id = validate_identifier(body.task_id, "task") if body.task_id else new_identifier("task")
        task = tasks.get(task_id)
        if task is not None and task.room_id != room.room_id:
            raise ApiDomainError("conflict", "task belongs to another room", status=409)
        runtime = _runtime_for_room(room.room_id)
        persona_theme = _room_persona_theme(room.room_id, body.persona_theme)
        decision = task_router.route(body.goal, requested_architecture=body.architecture, max_agents=body.max_agents)
        rag_hits: list[dict[str, Any]] = []
        rag_error: str | None = None
        rag_sources: list[str] = []
        # The asset index is a Runtime tool: only query it when this space has
        # completed ingestion jobs, so a fresh workspace does not initialize an
        # embedding model for every ordinary conversation.
        try:
            ingestion = _ingestion()
            jobs = await run_in_threadpool(ingestion.list, room.space_id)
            if any(item.get("status") == "completed" for item in jobs if isinstance(item, dict)):
                rag_hits = await run_in_threadpool(ingestion.search, room.space_id, body.goal)
                rag_context, rag_sources = _format_asset_context(rag_hits)
            else:
                rag_context = ""
        except Exception as exc:
            rag_context = ""
            rag_error = f"{type(exc).__name__}: {str(exc)[:240]}"
        prior = None
        recovered_turns = {}
        recovered_messages = {}
        all_events = events.read_after(RoomEventCursor(room_id, 0))
        with room_model_snapshot_lock:
            if saved_message is not None:
                prior = next((event for event in reversed(all_events)
                    if event.event_type == "run_started" and event.payload.get("message_id") == saved_message.message_id), None)
                completed = prior and any(e.run_id == prior.run_id and e.event_type == "run_completed" for e in all_events)
                if prior is not None and (not resume or completed):
                    return {"status": "already_started", "run_id": prior.run_id}
            if room.room_id in active_team_rooms:
                raise ApiDomainError("run_active", "room already has an active team run", status=409)
            try:
                existing_snapshot = room_model_snapshots.get(room.room_id)
                if durable_team and existing_snapshot is None:
                    existing_snapshot = runtime.restore_bindings(durable_team.bindings(room.room_id))
                if prior is not None and resume:
                    decision = task_router.route(body.goal, requested_architecture=prior.payload["architecture"], max_agents=int(prior.payload.get("max_agents", body.max_agents)))
                # The first team run fixes each participating Agent's model for
                # this room. Later runs can add roles, but never re-route a role
                # that has already participated in the room.
                model_snapshot = runtime.freeze_model_bindings(
                    architecture=decision.architecture,
                    max_agents=decision.max_agents,
                    goal=body.goal,
                    required_capabilities=decision.required_capabilities,
                    existing_snapshot=existing_snapshot,
                    persona_theme=persona_theme,
                )
            except ModelRoutingError as exc:
                raise ApiDomainError(
                    "model_routing_failed",
                    str(exc),
                    status=422,
                    details=exc.public_details(),
                ) from exc
            history = repository.list_messages(room.room_id)
            memory = prepare_room_memory(history, exclude_message_id=saved_message.message_id if saved_message is not None else "")
            context = memory.text
            if rag_context:
                context = "\n\n".join(part for part in (context, rag_context) if part)
            if prior is not None and resume:
                saved_memory = prior.payload.get("memory", {})
                context = str(saved_memory.get("text", prior.payload.get("context", ""))) if isinstance(saved_memory, dict) else str(prior.payload.get("context", ""))
            plan_fingerprint = hashlib.sha256(json.dumps({"version": 2, "strategy": decision.architecture,
                "max_agents": decision.max_agents, "theme": persona_theme,
                "goal": body.goal.strip(), "context": context,
                "plan_source": inspect.getsource(inspect.getmodule(build_team_plan)),
                "participants_source": inspect.getsource(runtime._execution_agent_ids),
                "bindings": model_snapshot.persistent()},
                sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            if prior is not None and resume and prior.payload.get("plan_fingerprint") != plan_fingerprint:
                raise ApiDomainError("plan_changed", "执行计划或角色配置已变更，无法安全复用旧步骤，请新建任务", status=409)
            if durable_team:
                durable_team.save_bindings(room.room_id, lease_token, model_snapshot.persistent())
            if prior is not None and resume:
                terminal = any(e.run_id == prior.run_id and e.event_type in {"run_completed", "run_failed", "run_cancelled"} for e in all_events)
                if not terminal:
                    events.append(room_id, "run_failed", run_id=prior.run_id, task_id=prior.task_id, payload={"error": "执行中断，已从检查点恢复"})
                if runtime_store:
                    previous_run = runtime_store.get_run(prior.run_id)
                    if previous_run and previous_run["status"] in {"running", "queued"}:
                        runtime_store.upsert_run(prior.run_id, task_id=prior.task_id, room_id=room_id, plan_revision=1, status="failed", model_snapshot=prior.payload.get("model_snapshot", []))
                        previous_task = runtime_store.get_task(prior.task_id)
                        if previous_task:
                            runtime_store.upsert_task(prior.task_id, room_id, previous_task["title"], status="blocked", active_run_id=None)
                for event in all_events:
                    if event.run_id == prior.run_id and event.event_type == "step_completed":
                        p = event.payload
                        binding = model_snapshot.by_agent_id().get(p["agent_id"])
                        if binding:
                            recovered_turns[int(p["sequence"])] = AgentTurn(binding.agent_id, binding.display_name,
                                binding.spec.responsibility, "", p["output"], int(p["sequence"]), binding.model,
                                binding.model_profile, binding.selection_mode, binding.selection_reason)
                            recovered_messages[int(p["sequence"])] = next((m for m in history if m.message_id == p["message_id"]), None)
            if task is None:
                task = _Task(task_id, room.room_id, body.goal.strip())
                tasks[task_id] = task
                if runtime_store is not None:
                    runtime_store.upsert_task(task.task_id, task.room_id, task.title, status=task.status, row_version=task.version, active_run_id=task.active_run_id)
            run_id = new_identifier("run")
            runs.register_run(run_id, plan_revision=1, status="running")
            task.active_run_id = run_id
            if runtime_store is not None:
                runtime_store.upsert_task(task.task_id, task.room_id, task.title, status=task.status, row_version=task.version, active_run_id=task.active_run_id)
                runtime_store.upsert_run(run_id, task_id=task_id, room_id=room.room_id, plan_revision=1, status="running", model_snapshot=model_snapshot.public())
            user_message = saved_message or repository.save_message(room.room_id, body.goal, role="user", idempotency_key=f"team-goal-{run_id}")
            _record_message_event(user_message)
            events.append(
                room.room_id,
                "run_started",
                run_id=run_id,
                task_id=task_id,
                payload={
                    "requested_architecture": body.architecture,
                    "architecture": decision.architecture,
                    "route_reason": decision.reason,
                    "rag": {"used": bool(rag_context), "query": body.goal, "hit_count": len(rag_hits), "source_ids": rag_sources, "error": rag_error},
                    "model_snapshot": model_snapshot.public(),
                    "message_id": user_message.message_id,
                    "max_agents": decision.max_agents,
                    "memory": {**memory.public(), "text": context},
                    "resumed_from": prior.run_id if prior is not None and resume else None,
                    "plan_fingerprint": plan_fingerprint,
                },
            )
            room_runtimes[room.room_id] = runtime
            room_model_snapshots[room.room_id] = model_snapshot
            active_team_rooms.add(room.room_id)

            events.append(
                room.room_id,
                "memory_read",
                run_id=run_id,
                task_id=task_id,
                payload={
                    "scope": "room",
                    "message_refs": list(memory.message_refs),
                    "tokens_before": memory.tokens_before,
                    "tokens_after": memory.tokens_after,
                    "compressed": memory.compressed,
                    "summary": context,
                    "rag_used": bool(rag_context),
                    "rag_hit_count": len(rag_hits),
                    "rag_source_ids": rag_sources,
                    "rag_error": rag_error,
                },
            )

        activity_lock = RLock()
        completed_events: dict[int, str] = {}
        started_events: dict[int, str] = {}
        last_failure_payload: dict[str, Any] = {}

        def record_activity(event_type: str, payload: dict) -> None:
            with activity_lock:
                check_lease()
                if event_type in {"step_claimed", "step_started"} and _run_state(run_id).status != "running":
                    raise ControlConflictError("team run is no longer running")
                sequence = payload.get("sequence")
                parents = ()
                if event_type == "handoff_created":
                    source_event = completed_events.get(payload.get("source_sequence"))
                    if source_event:
                        parents = (source_event,)
                event = events.append(room.room_id, event_type, task_id=task_id, run_id=run_id,
                    step_id=f"step-{run_id}-{sequence}" if sequence is not None else None,
                    caused_by=parents, payload=payload)
                if event_type == "step_failed":
                    last_failure_payload.update(payload)
                if event_type == "step_started":
                    started_events[sequence] = event.identity.event_id
                if event_type == "team_planned":
                    existing = {member.agent_id for member in repository.list_members(room.room_id) if member.status == "active"}
                    for participant in payload.get("participants", []):
                        if participant["agent_id"] not in existing:
                            repository.join_member(room.room_id, participant["agent_id"])

        def record_turn(turn: Any) -> None:
            check_lease()
            if _run_state(run_id).status != "running":
                raise ControlConflictError("team run is no longer running")
            existing = repository.list_members(room.room_id)
            if not any(member.agent_id == turn.agent_id and member.status == "active" for member in existing):
                repository.join_member(room.room_id, turn.agent_id)
            # Background room runs are rendered as a real group conversation:
            # each completed Agent turn gets its own durable message.  Keep
            # the synchronous low-level endpoint's historical contract of
            # persisting only the final answer.
            message = None
            persist_turn = bool(getattr(turn, "is_final", False) or body.background or saved_message is not None)
            if persist_turn:
                message = recovered_messages.get(turn.sequence) or repository.save_message(
                    room.room_id,
                    turn.content,
                    role="assistant",
                    idempotency_key=f"team-final-{run_id}" if getattr(turn, "is_final", False) else f"team-step-{run_id}-{turn.sequence}",
                )
                _record_message_event(message)
            completion = events.append(
                room.room_id,
                "step_completed",
                task_id=task_id,
                run_id=run_id,
                step_id=f"step-{run_id}-{turn.sequence}",
                caused_by=(started_events[turn.sequence],) if turn.sequence in started_events else (),
                payload={
                    "agent_id": turn.agent_id,
                    "display_name": getattr(turn, "display_name", turn.agent_id),
                    "message_id": message.message_id if message is not None else "",
                    "model": turn.model,
                    "model_profile": turn.model_profile,
                    "selection_mode": turn.selection_mode,
                    "selection_reason": turn.selection_reason,
                    "sequence": turn.sequence,
                    "output": turn.content,
                    "duration_ms": turn.duration_ms,
                    "reused": turn.sequence in recovered_turns,
                    "plan_fingerprint": plan_fingerprint,
                    "is_final": bool(getattr(turn, "is_final", False)),
                },
            )
            completed_events[turn.sequence] = completion.identity.event_id

        def check_run_active() -> None:
            check_lease()
            current = _run_state(run_id)
            if current.status != "running":
                raise ControlConflictError("team run is no longer running")

        def persist_finished():
            current = _run_state(run_id)
            task.active_run_id = None
            task.status = {"cancelled": "cancelled", "paused": "blocked", "failed": "blocked", "completed": "completed"}.get(current.status, task.status)
            try:
                check_lease()
                if runtime_store:
                    row = runtime_store.finish_run(current)
                    runs.restore_run(RunControlState(**{key: row[key] for key in ("run_id", "plan_revision", "status", "control_epoch", "row_version")}))
                    saved_task = runtime_store.get_task(task_id)
                    if saved_task:
                        task.version = saved_task["row_version"]
                        task.status = saved_task["status"]
                        task.active_run_id = saved_task["active_run_id"]
            finally:
                _release_team_room(room_id)
                release_execution()

        def finish_team_run(status):
            current = _run_state(run_id)
            if current.status == "running":
                current = runs.finish(run_id, status=status, expected_row_version=current.row_version)
            if runtime_store:
                check_lease()
                row = runtime_store.finish_run(current)
                current = runs.restore_run(RunControlState(**{key: row[key] for key in ("run_id", "plan_revision", "status", "control_epoch", "row_version")}))
            return current

        if body.background:
            events.append(room.room_id, "run_queued", run_id=run_id, task_id=task_id)
            def execute_in_worker() -> None:
                try:
                    result = runtime.execute(body.goal, architecture=decision.architecture, max_agents=decision.max_agents, context=context, on_turn=record_turn, on_activity=record_activity, model_snapshot=model_snapshot, persona_theme=persona_theme, check_active=check_run_active, completed_turns=recovered_turns)
                    current = finish_team_run("completed")
                    if current.status == "completed":
                        events.append(room.room_id, "run_completed", run_id=run_id, task_id=task_id, payload={"turn_count": len(result.turns), "worker": True})
                except Exception as exc:
                    current = finish_team_run("failed") if not isinstance(exc, RoomLeaseBusy) else _run_state(run_id)
                    if current.status == "failed" and not isinstance(exc, RoomLeaseBusy):
                        events.append(room.room_id, "run_failed", run_id=run_id, task_id=task_id, payload={**serialize_exception(exc, phase="team_execution"), **last_failure_payload, "error": type(exc).__name__, "worker": True})
                finally:
                    persist_finished()

            try:
                team_worker.submit(execute_in_worker)
            except Exception:
                finish_team_run("failed")
                events.append(room_id, "run_failed", run_id=run_id, task_id=task_id, payload={"error_code": "worker_unavailable", "error_type": "WorkerUnavailable", "error_message": "后台执行器不可用", "phase": "worker_submit", "retryable": True, "suggestion": "重启后台 worker 后恢复任务", "error": "worker_unavailable"})
                persist_finished()
                raise
            return {"room_id": room.room_id, "task_id": task_id, "run_id": run_id, "architecture": decision.architecture, "route_reason": decision.reason, "status": "queued", "final": "", "turns": []}

        try:
            result = await run_in_threadpool(runtime.execute, body.goal, architecture=decision.architecture, max_agents=decision.max_agents, context=context, on_turn=record_turn, on_activity=record_activity, model_snapshot=model_snapshot, persona_theme=persona_theme, check_active=check_run_active, completed_turns=recovered_turns)
            current = finish_team_run("completed")
            if current.status != "completed":
                raise ControlConflictError("team run is no longer running")
            events.append(room.room_id, "run_completed", run_id=run_id, task_id=task_id, payload={"turn_count": len(result.turns)})
        except Exception as exc:
            current = finish_team_run("failed") if not isinstance(exc, RoomLeaseBusy) else _run_state(run_id)
            if current.status == "failed":
                events.append(room.room_id, "run_failed", run_id=run_id, task_id=task_id, payload={**serialize_exception(exc, phase="team_execution"), **last_failure_payload, "error": type(exc).__name__, "status": current.status})
            raise ApiDomainError("multi_agent_failed", "团队执行未完成，已保留完成步骤，请查看运行轨迹。", status=502) from exc
        finally:
            persist_finished()
        return {
            "room_id": room.room_id,
            "task_id": task_id,
            "run_id": run_id,
            "architecture": result.architecture,
            "route_reason": decision.reason,
            "status": result.status,
            "final": result.final,
            "turns": [{
                "agent_id": turn.agent_id,
                "responsibility": turn.responsibility,
                "content": turn.content,
                "sequence": turn.sequence,
                "model": turn.model,
                "model_profile": turn.model_profile,
                "selection_mode": turn.selection_mode,
                "selection_reason": turn.selection_reason,
            } for turn in result.turns],
        }

    @app.get("/tasks/{task_id}", response_model=TaskResponse)
    async def get_task(request: Request, task_id: str) -> Any:
        task_id = validate_identifier(task_id, "task")
        task = tasks.get(task_id)
        if runtime_store is not None:
            row = runtime_store.get_task(task_id)
            if row:
                task = _Task(row["task_id"], row["room_id"], row["title"], row["status"], int(row["row_version"]), row.get("active_run_id"))
                tasks[task_id] = task
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
            if runtime_store is not None:
                runtime_store.upsert_task(task.task_id, task.room_id, task.title, status=task.status, row_version=task.version, active_run_id=task.active_run_id)
                runtime_store.upsert_run(state.run_id, task_id=task.task_id, room_id=task.room_id, plan_revision=state.plan_revision, status=state.status)
        return _dump(state)

    @app.get("/runs/{run_id}", response_model=RunResponse)
    async def get_run(run_id: str) -> Any:
        try:
            return _dump(_run_state(run_id))
        except ControlError as exc:
            if runtime_store is not None:
                row = runtime_store.get_run(validate_identifier(run_id, "run"))
                if row:
                    return {"run_id": row["run_id"], "plan_revision": row["plan_revision"], "status": row["status"], "control_epoch": row["control_epoch"], "row_version": row["row_version"]}
            raise ApiDomainError("not_found", str(exc), status=404) from exc

    @app.post("/commands/{command_id}", response_model=CommandResponse)
    async def execute_command(request: Request, command_id: str, body: CommandRequest) -> Any:
        command_id = validate_identifier(command_id, "operation")
        run_row = runtime_store.get_run(body.run_id) if runtime_store else None
        if run_row:
            _room_for_request(request, run_row["room_id"])
        if command_id in commands:
            return commands[command_id]
        try:
            if body.action != "start" and body.expected_control_epoch is None:
                raise ApiDomainError("invalid_request", "expected_control_epoch is required", status=422)
            if runtime_store and run_row:
                result = runtime_store.apply_control(command_id, body.run_id, body.action,
                    expected_row_version=body.expected_row_version, expected_control_epoch=body.expected_control_epoch)
                state = _run_state(body.run_id)
            elif body.action == "start":
                state = runs.start(body.run_id, expected_row_version=body.expected_row_version)
            elif body.expected_control_epoch is None:
                raise ApiDomainError("invalid_request", "expected_control_epoch is required", status=422)
            elif body.action == "pause":
                state = runs.pause(body.run_id, expected_row_version=body.expected_row_version, expected_control_epoch=body.expected_control_epoch)
            else:
                state = runs.cancel(body.run_id, expected_row_version=body.expected_row_version, expected_control_epoch=body.expected_control_epoch)
        except ControlConflictError as exc:
            try:
                current = _run_state(body.run_id)
                details = {"expected_row_version": body.expected_row_version, "expected_control_epoch": body.expected_control_epoch, "row_version": current.row_version, "control_epoch": current.control_epoch}
            except ControlError:
                details = {"expected_row_version": body.expected_row_version, "expected_control_epoch": body.expected_control_epoch}
            raise ApiDomainError("version_conflict", str(exc), status=409, details=details) from exc
        except (ControlError, RunNotClaimableError) as exc:
            raise ApiDomainError("command_rejected", str(exc), status=409) from exc
        if not (runtime_store and run_row):
            result = {"command_id": command_id, "status": "accepted", "run": _dump(state)}
        if runtime_store and run_row:
            if result["run"]["status"] in {"cancelled", "paused"}:
                task_row = runtime_store.get_task(run_row["task_id"])
                if task_row:
                    tasks[task_row["task_id"]] = _Task(task_row["task_id"], task_row["room_id"], task_row["title"], task_row["status"], task_row["row_version"], task_row["active_run_id"])
                events.append(run_row["room_id"], "run_cancelled" if result["run"]["status"] == "cancelled" else "run_paused",
                    run_id=state.run_id, task_id=run_row["task_id"], event_id=f"event-command-{command_id}", payload={"status": result["run"]["status"]})
        commands[command_id] = result
        return result

    @app.post("/asset-ingestions", response_model=AssetIngestionResponse, status_code=202)
    async def ingest_asset(request: Request, body: AssetUploadRequest) -> Any:
        _require_space(request, body.space_id)
        try:
            content = base64.b64decode(body.content_base64, validate=True)
            return await run_in_threadpool(_ingestion().submit, body.filename, content, body.space_id, evaluate=body.evaluate)
        except (ValueError, binascii.Error) as exc:
            raise ApiDomainError("invalid_asset", str(exc), status=422) from exc

    @app.get("/asset-ingestions", response_model=AssetIngestionListResponse)
    async def list_ingestions(request: Request, space_id: str = Query(min_length=1, max_length=128)) -> Any:
        _require_space(request, space_id)
        return {"items": await run_in_threadpool(_ingestion().list, space_id)}

    def _ingestion_for_request(request: Request, job_id: str) -> dict:
        try:
            job = _ingestion().get(job_id)
        except KeyError as exc:
            raise ApiDomainError("not_found", "入库任务不存在", status=404) from exc
        _require_space(request, job["space_id"])
        return job

    @app.get("/asset-ingestions/{job_id}", response_model=AssetIngestionResponse)
    async def get_ingestion(request: Request, job_id: str) -> Any:
        return _ingestion_for_request(request, job_id)

    @app.post("/asset-ingestions/{job_id}/retry", response_model=AssetIngestionResponse, status_code=202)
    async def retry_ingestion(request: Request, job_id: str) -> Any:
        _ingestion_for_request(request, job_id)
        try:
            return await run_in_threadpool(_ingestion().retry, job_id)
        except ValueError as exc:
            raise ApiDomainError("ingestion_conflict", str(exc), status=409) from exc

    @app.delete("/asset-ingestions/{job_id}", response_model=AssetIngestionResponse)
    async def delete_ingestion(request: Request, job_id: str) -> Any:
        _ingestion_for_request(request, job_id)
        try:
            return await run_in_threadpool(_ingestion().delete, job_id)
        except ValueError as exc:
            raise ApiDomainError("ingestion_conflict", str(exc), status=409) from exc

    @app.get("/assets/search", response_model=AssetSearchResponse)
    async def search_assets(request: Request, space_id: str = Query(min_length=1, max_length=128), q: str = Query(min_length=1, max_length=2000)) -> Any:
        _require_space(request, space_id)
        try:
            return {"items": await run_in_threadpool(_ingestion().search, space_id, q)}
        except Exception as exc:
            raise ApiDomainError("asset_search_failed", "检索失败，请检查嵌入模型配置后重试", status=503) from exc

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


def create_local_app():
    storage = Path(__file__).resolve().parents[2] / ".localrag" / "workspace.sqlite3"
    storage.parent.mkdir(parents=True, exist_ok=True)
    return create_app(database_url=os.environ.get("LOCALRAG_DATABASE_URL") or f"sqlite:///{storage.as_posix()}")


app = create_local_app()
