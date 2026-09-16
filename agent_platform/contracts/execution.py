"""Execution, tool, collaboration, and evaluation contracts for D04."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

from .identity import (
    AttemptIdentity,
    OperationIdentity,
    RoomEventIdentity,
    validate_identifier,
)


EffectKind = Literal["none", "read", "deterministic", "side_effect"]
EffectState = Literal["none", "not_applied", "applied", "unknown"]
ResultStatus = Literal["succeeded", "failed", "blocked", "needs_input"]
ClaimStatus = Literal["unreviewed", "supported", "contradicted", "insufficient"]
EventType = Literal[
    "task_start_failed",
    "room_deleted",
    "step_reused",
    "run_paused",
    "team_plan_created",
    "step_claimed",
    "step_retrying",
    "step_blocked",
    "step_output_delta",
    "memory_read",
    "room_persona_selected",
    "room_architecture_selected",
    "team_planned",
    "step_queued",
    "step_failed",
    "message_saved",
    "run_started",
    "run_queued",
    "step_started",
    "tool_started",
    "tool_completed",
    "handoff_created",
    "handoff_accepted",
    "claim_recorded",
    "step_completed",
    "run_completed",
    "run_failed",
    "run_cancelled",
    "command_rejected",
]


def _text(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not allow_empty and not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if len(normalized) > 4000:
        raise ValueError(f"{field_name} must not exceed 4000 characters")
    return normalized


def _strings(value: object, field_name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)):
        raise TypeError(f"{field_name} must be a sequence of strings")
    try:
        values = tuple(value)  # type: ignore[arg-type]
    except TypeError as exc:
        raise TypeError(f"{field_name} must be a sequence of strings") from exc
    if not all(isinstance(item, str) and item.strip() for item in values):
        raise ValueError(f"{field_name} must contain non-empty strings")
    return tuple(item.strip() for item in values)


def _nonnegative_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return value


def _positive_int(value: object, field_name: str) -> int:
    normalized = _nonnegative_int(value, field_name)
    if normalized == 0:
        raise ValueError(f"{field_name} must be greater than zero")
    return normalized


class _Contract:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolManifest(_Contract):
    """Capability declaration consumed by the Runtime, not by a prompt."""

    name: str
    version: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    effect_kind: EffectKind = "read"
    idempotency_support: bool = True
    reconcile_support: bool = False
    required_permissions: tuple[str, ...] = ()
    data_scopes: tuple[str, ...] = ()
    timeout_seconds: int = 60
    sandbox_required: bool = False
    failure_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _text(self.name, "name"))
        object.__setattr__(self, "version", _text(self.version, "version"))
        if not isinstance(self.input_schema, dict):
            raise TypeError("input_schema must be a mapping")
        if not isinstance(self.output_schema, dict):
            raise TypeError("output_schema must be a mapping")
        if self.effect_kind not in {"none", "read", "deterministic", "side_effect"}:
            raise ValueError(f"unsupported effect_kind: {self.effect_kind}")
        if type(self.idempotency_support) is not bool:
            raise TypeError("idempotency_support must be a bool")
        if type(self.reconcile_support) is not bool:
            raise TypeError("reconcile_support must be a bool")
        if self.effect_kind == "side_effect" and not self.idempotency_support and not self.reconcile_support:
            raise ValueError("side_effect tools need idempotency or reconciliation support")
        object.__setattr__(self, "required_permissions", _strings(self.required_permissions, "required_permissions"))
        object.__setattr__(self, "data_scopes", _strings(self.data_scopes, "data_scopes"))
        object.__setattr__(self, "failure_codes", _strings(self.failure_codes, "failure_codes"))
        object.__setattr__(self, "timeout_seconds", _positive_int(self.timeout_seconds, "timeout_seconds"))
        if type(self.sandbox_required) is not bool:
            raise TypeError("sandbox_required must be a bool")


@dataclass(frozen=True)
class Result(_Contract):
    """Uniform output envelope for tools, model steps, and delegated work."""

    status: ResultStatus
    output: Any = None
    error_code: str = ""
    error_message: str = ""
    artifact_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    operation_id: str | None = None
    effect_state: EffectState = "none"

    def __post_init__(self) -> None:
        if self.status not in {"succeeded", "failed", "blocked", "needs_input"}:
            raise ValueError(f"unsupported result status: {self.status}")
        object.__setattr__(self, "error_code", _text(self.error_code, "error_code", allow_empty=True))
        object.__setattr__(self, "error_message", _text(self.error_message, "error_message", allow_empty=True))
        object.__setattr__(self, "artifact_refs", _strings(self.artifact_refs, "artifact_refs"))
        object.__setattr__(self, "evidence_refs", _strings(self.evidence_refs, "evidence_refs"))
        if self.operation_id is not None:
            object.__setattr__(self, "operation_id", validate_identifier(self.operation_id, "operation"))
        if self.effect_state not in {"none", "not_applied", "applied", "unknown"}:
            raise ValueError(f"unsupported effect_state: {self.effect_state}")
        if self.status == "succeeded" and self.error_code:
            raise ValueError("successful results cannot carry error_code")
        if self.status in {"failed", "blocked", "needs_input"} and not self.error_code:
            raise ValueError("non-success results require error_code")
        if self.effect_state == "unknown" and self.status == "succeeded":
            raise ValueError("unknown side effect cannot be reported as succeeded")


@dataclass(frozen=True)
class RunEvent(_Contract):
    """Append-only event envelope; persistence and ordering are Runtime duties."""

    identity: RoomEventIdentity
    event_type: EventType
    room_id: str
    task_id: str | None = None
    run_id: str | None = None
    step_id: str | None = None
    attempt_id: str | None = None
    run_sequence: int = 0
    caused_by: tuple[str, ...] = ()
    consumes: tuple[str, ...] = ()
    produces: tuple[str, ...] = ()
    usage: dict[str, int] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.identity, RoomEventIdentity):
            raise TypeError("identity must be a RoomEventIdentity")
        object.__setattr__(self, "room_id", validate_identifier(self.room_id, "room"))
        if self.room_id != self.identity.room_id:
            raise ValueError("room_id must match event identity")
        if self.event_type not in {
            "task_start_failed",
            "room_deleted", "step_reused",
            "run_paused",
            "team_plan_created", "step_claimed", "step_retrying", "step_blocked", "step_output_delta", "memory_read",
            "room_persona_selected", "room_architecture_selected", "team_planned", "step_queued", "step_failed",
            "message_saved", "run_started", "run_queued", "step_started", "tool_started", "tool_completed",
            "handoff_created", "handoff_accepted", "claim_recorded", "step_completed", "run_completed", "run_failed",
            "run_cancelled", "command_rejected",
        }:
            raise ValueError(f"unsupported event_type: {self.event_type}")
        for field_name, kind in (
            ("task_id", "task"), ("run_id", "run"), ("step_id", "step"), ("attempt_id", "attempt")
        ):
            value = getattr(self, field_name)
            if value is not None:
                object.__setattr__(self, field_name, validate_identifier(value, kind))
        object.__setattr__(self, "run_sequence", _nonnegative_int(self.run_sequence, "run_sequence"))
        object.__setattr__(self, "caused_by", _strings(self.caused_by, "caused_by"))
        object.__setattr__(self, "consumes", _strings(self.consumes, "consumes"))
        object.__setattr__(self, "produces", _strings(self.produces, "produces"))
        if not isinstance(self.usage, dict) or any(type(v) is not int or v < 0 for v in self.usage.values()):
            raise TypeError("usage must map names to non-negative integers")
        if not isinstance(self.payload, dict):
            raise TypeError("payload must be a mapping")
        normalized_timestamp = self.timestamp or datetime.now(timezone.utc).isoformat()
        object.__setattr__(self, "timestamp", _text(normalized_timestamp, "timestamp"))


@dataclass(frozen=True)
class Handoff(_Contract):
    """Structured delegation request shown in the room as an event projection."""

    handoff_id: str
    schema_version: str
    room_id: str
    task_id: str
    run_id: str
    sender_id: str
    recipient_id: str
    source_step_id: str
    target_step_id: str
    source_attempt_id: str
    input_refs: tuple[str, ...]
    expected_schema: dict[str, Any]
    acceptance_rules: tuple[str, ...]
    plan_revision: int
    control_epoch: int
    deadline: str

    def __post_init__(self) -> None:
        for field_name, kind in (
            ("handoff_id", "operation"), ("room_id", "room"), ("task_id", "task"),
            ("run_id", "run"), ("source_step_id", "step"), ("target_step_id", "step"),
            ("source_attempt_id", "attempt"),
        ):
            object.__setattr__(self, field_name, validate_identifier(getattr(self, field_name), kind))
        object.__setattr__(self, "schema_version", _text(self.schema_version, "schema_version"))
        object.__setattr__(self, "sender_id", _text(self.sender_id, "sender_id"))
        object.__setattr__(self, "recipient_id", _text(self.recipient_id, "recipient_id"))
        object.__setattr__(self, "input_refs", _strings(self.input_refs, "input_refs"))
        if not isinstance(self.expected_schema, dict):
            raise TypeError("expected_schema must be a mapping")
        object.__setattr__(self, "acceptance_rules", _strings(self.acceptance_rules, "acceptance_rules"))
        object.__setattr__(self, "plan_revision", _positive_int(self.plan_revision, "plan_revision"))
        object.__setattr__(self, "control_epoch", _nonnegative_int(self.control_epoch, "control_epoch"))
        object.__setattr__(self, "deadline", _text(self.deadline, "deadline"))


@dataclass(frozen=True)
class Claim(_Contract):
    """Versioned claim whose support state is separate from persistence success."""

    claim_id: str
    run_id: str
    step_id: str
    text: str
    evidence_ids: tuple[str, ...] = ()
    status: ClaimStatus = "unreviewed"
    confirmed_by: str | None = None
    input_revision: str = ""

    def __post_init__(self) -> None:
        for field_name, kind in (("claim_id", "operation"), ("run_id", "run"), ("step_id", "step")):
            object.__setattr__(self, field_name, validate_identifier(getattr(self, field_name), kind))
        object.__setattr__(self, "text", _text(self.text, "text"))
        object.__setattr__(self, "evidence_ids", _strings(self.evidence_ids, "evidence_ids"))
        if self.status not in {"unreviewed", "supported", "contradicted", "insufficient"}:
            raise ValueError(f"unsupported claim status: {self.status}")
        object.__setattr__(self, "confirmed_by", _text(self.confirmed_by, "confirmed_by") if self.confirmed_by else None)
        object.__setattr__(self, "input_revision", _text(self.input_revision, "input_revision", allow_empty=True))
        if self.status == "supported" and not self.evidence_ids:
            raise ValueError("supported claims require evidence_ids")


@dataclass(frozen=True)
class EvaluationPolicy(_Contract):
    """Separates upload publish integrity from optional quality evaluation."""

    publish_requires_integrity_check: bool = True
    publish_requires_quality_evaluation: bool = False
    quality_evaluation_trigger: Literal["manual", "command", "scheduled"] = "manual"
    release_gate_requires_quality_evaluation: bool = True
    command: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "publish_requires_integrity_check",
            "publish_requires_quality_evaluation",
            "release_gate_requires_quality_evaluation",
        ):
            if type(getattr(self, field_name)) is not bool:
                raise TypeError(f"{field_name} must be a bool")
        if self.quality_evaluation_trigger not in {"manual", "command", "scheduled"}:
            raise ValueError("unsupported quality_evaluation_trigger")
        object.__setattr__(self, "command", _text(self.command, "command", allow_empty=True))
        if self.publish_requires_quality_evaluation and not self.command and self.quality_evaluation_trigger == "command":
            raise ValueError("command-triggered evaluation requires command")
