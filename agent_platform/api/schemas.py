"""Pydantic wire models for the v1.8 API boundary."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class RoomCreateRequest(BaseModel):
    space_id: str = Field(min_length=1)
    title: str = ""
    room_id: str | None = None


class AssistantMessageRequest(BaseModel):
    space_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    title: str = ""
    room_id: str | None = None
    persona_theme: Literal["company", "emperor"] | None = None
    architecture: Literal["auto", "direct", "hierarchical", "swarm", "adversarial", "heterogeneous", "graph"] = "auto"


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1)
    role: Literal["user", "assistant", "system", "tool"] = "user"
    message_id: str | None = None


class TaskCreateRequest(BaseModel):
    room_id: str
    title: str = Field(min_length=1)
    task_id: str | None = None


class FollowupRequest(BaseModel):
    content: str = Field(min_length=1)
    expected_task_version: int | None = Field(default=None, ge=1)


class RunCreateRequest(BaseModel):
    run_id: str | None = None
    task_id: str | None = None
    plan_revision: int = Field(default=1, ge=1)
    status: Literal["queued", "running"] = "queued"


class CommandRequest(BaseModel):
    action: Literal["start", "pause", "cancel"]
    run_id: str
    expected_row_version: int = Field(ge=1)
    expected_control_epoch: int | None = Field(default=None, ge=0)


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str
    control_epoch: int | None = None
    row_version: int | None = None


class HealthResponse(BaseModel):
    status: str
    contract: str


class RoomResponse(BaseModel):
    space_id: str
    room_id: str
    title: str
    status: Literal["active", "archived", "deleted"]
    room_sequence: int
    row_version: int


class RoomListResponse(BaseModel):
    items: list[RoomResponse]


class MemberResponse(BaseModel):
    membership_id: str
    room_id: str
    agent_id: str
    status: str
    joined_at: datetime | None
    left_at: datetime | None


class MemberListResponse(BaseModel):
    items: list[MemberResponse]

class RoleResponse(BaseModel):
    role_id: str
    name: str
    department: str
    responsibilities: list[str]
    capabilities: list[str]

class RoleListResponse(BaseModel):
    items: list[RoleResponse]

class PersonaCreateRequest(BaseModel):
    persona_id: str = Field(min_length=1)
    role_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    system_prompt: str = Field(min_length=1)
    tone: str = "professional"

class PersonaResponse(BaseModel):
    persona_id: str
    role_id: str
    version: int
    display_name: str
    system_prompt: str
    tone: str

class PersonaBindingResponse(BaseModel):
    binding_id: str
    persona_id: str
    role_id: str
    persona_version: int
    capabilities: list[str]

class PlanCompileRequest(BaseModel):
    task_id: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    mode: Literal["auto", "direct", "delegate"] = "auto"
    architecture: Literal["direct", "hierarchical", "graph"] = "direct"
    requires_decomposition: bool = False
    required_capabilities: list[str] = Field(default_factory=list)
    max_agents: int = Field(default=1, ge=1)
    budget_units: int = Field(default=100, ge=1)

class PlanCompileResponse(BaseModel):
    plan_id: str
    task_id: str
    mode: Literal["direct", "delegate"]
    architecture: str
    members: list[str]
    steps: list[str]
    budget_units: int

class MultiAgentExecuteRequest(BaseModel):
    goal: str = Field(min_length=1)
    architecture: Literal["auto", "direct", "hierarchical", "swarm", "adversarial", "heterogeneous", "graph"] = "auto"
    max_agents: int = Field(default=3, ge=1, le=8)
    task_id: str | None = None
    background: bool = False
    persona_theme: Literal["company", "emperor"] | None = None

class MultiAgentTurnResponse(BaseModel):
    agent_id: str
    responsibility: str
    content: str
    sequence: int
    model: str
    model_profile: str
    selection_mode: Literal["fixed", "auto"]
    selection_reason: str

class MultiAgentExecuteResponse(BaseModel):
    room_id: str
    task_id: str
    run_id: str
    architecture: str
    route_reason: str = ""
    status: Literal["queued", "running", "completed", "failed"]
    final: str
    turns: list[MultiAgentTurnResponse]


class ModelBindingUpdateRequest(BaseModel):
    source_agent_id: str = Field(min_length=1)
    tier: str | None = Field(default=None, min_length=1)


class ModelAgentSetting(BaseModel):
    agent_id: str
    display_name: str
    responsibility: str
    tier: str
    model_binding_mode: Literal["fixed", "auto"]
    model_profile: str
    provider: str
    model: str
    capabilities: list[str]
    modalities: list[str]
    max_concurrency: int
    auto_tier: str
    auto_capabilities: list[str]
    auto_modalities: list[str]
    auto_scenarios: list[str]


class ModelChoice(BaseModel):
    source_agent_id: str
    model_profile: str
    provider: str
    base_url: str
    model: str
    capabilities: list[str]
    modalities: list[str]
    max_concurrency: int


class ModelSettingsResponse(BaseModel):
    agents: list[ModelAgentSetting]
    models: list[ModelChoice]


class ModelProfileRequest(BaseModel):
    profile_id: str = Field(min_length=1)
    display_name: str = ""
    provider: str = ""
    base_url: str = ""
    model: str = ""
    api_key_env: str = ""
    api_key: str = ""
    capabilities: list[str] = Field(default_factory=list)
    modalities: list[str] = Field(default_factory=lambda: ["text"])
    scenarios: list[str] = Field(default_factory=list)
    tier: str = "standard"
    max_concurrency: int = Field(default=4, ge=1)
    enabled: bool = False
    clear_api_key: bool = False


class AgentConfigRequest(BaseModel):
    agent_id: str = Field(min_length=1)
    display_name: str = ""
    responsibility: str = ""
    model_binding_mode: Literal["fixed", "auto"] = "fixed"
    model_profile: str = ""
    tier: str = "standard"
    capabilities: list[str] = Field(default_factory=list)
    modalities: list[str] = Field(default_factory=lambda: ["text"])
    auto_tier: str = ""
    auto_capabilities: list[str] = Field(default_factory=list)
    auto_modalities: list[str] = Field(default_factory=list)
    auto_scenarios: list[str] = Field(default_factory=list)
    system_prompt: str = ""
    enabled: bool = False


class ModelProfileResponse(BaseModel):
    profile_id: str
    display_name: str
    provider: str
    base_url: str
    model: str
    api_key_env: str
    has_api_key: bool
    capabilities: list[str]
    modalities: list[str]
    scenarios: list[str]
    tier: str
    max_concurrency: int
    enabled: bool
    ready: bool
    readiness_issues: list[str]


class AgentConfigResponse(BaseModel):
    agent_id: str
    display_name: str
    responsibility: str
    model_binding_mode: Literal["fixed", "auto"]
    model_profile: str
    tier: str
    capabilities: list[str]
    modalities: list[str]
    auto_tier: str
    auto_capabilities: list[str]
    auto_modalities: list[str]
    auto_scenarios: list[str]
    system_prompt: str
    enabled: bool
    ready: bool
    readiness_issues: list[str]


class ModelCatalogResponse(BaseModel):
    contract_version: str
    profiles: list[ModelProfileResponse]
    agents: list[AgentConfigResponse]


class ModelProfileCloneResponse(BaseModel):
    profile_id: str
    catalog: ModelCatalogResponse


class ModelDiscoveryRequest(BaseModel):
    base_url: str = Field(min_length=1)
    api_key: str = ""
    profile_id: str = ""


class DiscoveredModelResponse(BaseModel):
    id: str
    owned_by: str = ""


class ModelDiscoveryResponse(BaseModel):
    items: list[DiscoveredModelResponse]

class ModelVerificationResponse(BaseModel):
    profile_id: str
    verified: bool
    message: str
    model: str

class AssetUploadRequest(BaseModel):
    space_id: str = Field(default="default", min_length=1, max_length=128)
    filename: str = Field(min_length=1, max_length=255)
    content_base64: str = Field(min_length=1, max_length=41943040)
    evaluate: bool = False

class AssetStageResponse(BaseModel):
    stage: str
    at: str

class AssetIngestionResponse(BaseModel):
    job_id: str
    space_id: str
    filename: str
    asset_id: str
    size_bytes: int
    status: Literal["queued", "running", "completed", "failed", "deleted"]
    stage: str
    chunk_count: int
    source_id: str | None
    error: str | None
    history: list[AssetStageResponse]
    updated_at: str
    evaluation_status: str

class AssetIngestionListResponse(BaseModel):
    items: list[AssetIngestionResponse]

class AssetSearchHit(BaseModel):
    text: str
    metadata: dict[str, Any]

class AssetSearchResponse(BaseModel):
    items: list[AssetSearchHit]

class AssetUploadResponse(BaseModel):
    asset_id: str
    media_type: str
    content_hash: str
    size_bytes: int
    object_path: str
    chunks: list[str]
    evaluation_requested: bool
    evaluation_status: Literal["not_requested", "requested"]


class AssistantMessageResponse(BaseModel):
    room: RoomResponse
    message: "MessageResponse"
    created: bool


class MessageResponse(BaseModel):
    message_id: str
    room_id: str
    content: str
    role: Literal["user", "assistant", "system", "tool"]
    status: str
    room_sequence: int
    idempotency_key: str | None
    content_sha256: str
    created_at: datetime | None


class MessageListResponse(BaseModel):
    items: list[MessageResponse]
    next: int = 0


class EventIdentityResponse(BaseModel):
    room_id: str
    event_id: str
    room_sequence: int


class EventResponse(BaseModel):
    identity: EventIdentityResponse
    event_type: str
    room_id: str
    task_id: str | None
    run_id: str | None
    step_id: str | None
    attempt_id: str | None
    run_sequence: int
    caused_by: list[str]
    consumes: list[str]
    produces: list[str]
    usage: dict[str, int]
    payload: dict[str, Any]
    timestamp: str


class EventListResponse(BaseModel):
    items: list[EventResponse]
    next: int


class ArtifactResponse(BaseModel):
    """A room-scoped projection of a step output or declared artifact."""

    artifact_id: str
    title: str
    artifact_type: str
    content: str
    output: Any = None
    source_event_id: str
    source_step_id: str | None
    source_agent_id: str | None
    source_agent_name: str | None
    run_id: str | None
    task_id: str | None
    timestamp: str
    is_final: bool = False


class ArtifactListResponse(BaseModel):
    items: list[ArtifactResponse]


class TaskResponse(BaseModel):
    task_id: str
    room_id: str
    title: str
    status: str
    version: int
    active_run_id: str | None


class FollowupResponse(BaseModel):
    task: TaskResponse
    message: MessageResponse
    status: Literal["accepted"]
    run_id: str | None


class RunResponse(BaseModel):
    run_id: str
    plan_revision: int
    status: str
    control_epoch: int
    row_version: int


class CommandResponse(BaseModel):
    command_id: str
    status: Literal["accepted"]
    run: RunResponse


AssistantMessageResponse.model_rebuild()
