"""Stable identity and version contracts for the v1.8 Runtime.

The classes in this module carry no persistence or execution behavior. They
make resource scope and concurrency versions explicit before the P1 storage
work starts.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Literal
from uuid import uuid4


IdentifierKind = Literal[
    "space",
    "room",
    "task",
    "turn",
    "message",
    "run",
    "plan",
    "step",
    "attempt",
    "operation",
    "event",
]

IDENTIFIER_KINDS: tuple[IdentifierKind, ...] = (
    "space",
    "room",
    "task",
    "turn",
    "message",
    "run",
    "plan",
    "step",
    "attempt",
    "operation",
    "event",
)

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_MAX_IDENTIFIER_LENGTH = 128


def validate_identifier(value: str, kind: IdentifierKind) -> str:
    """Validate a namespaced identifier and return its normalized value."""
    if kind not in IDENTIFIER_KINDS:
        raise ValueError(f"unsupported identifier kind: {kind}")
    if not isinstance(value, str):
        raise TypeError(f"{kind}_id must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{kind}_id must not be empty")
    if len(normalized) > _MAX_IDENTIFIER_LENGTH:
        raise ValueError(
            f"{kind}_id must not exceed {_MAX_IDENTIFIER_LENGTH} characters"
        )
    prefix = f"{kind}-"
    suffix = normalized.removeprefix(prefix)
    if not normalized.startswith(prefix) or not suffix:
        raise ValueError(f"{kind}_id must start with '{prefix}'")
    if not _IDENTIFIER_PATTERN.fullmatch(suffix):
        raise ValueError(
            f"{kind}_id may only contain letters, numbers, '.', '_' and '-'"
        )
    return normalized


def new_identifier(kind: IdentifierKind) -> str:
    """Create a sortable-independent opaque ID with an explicit resource prefix."""
    if kind not in IDENTIFIER_KINDS:
        raise ValueError(f"unsupported identifier kind: {kind}")
    return f"{kind}-{uuid4().hex}"


def _version(value: int, field_name: str, *, minimum: int) -> int:
    if type(value) is not int:
        raise TypeError(f"{field_name} must be an int")
    if value < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}")
    return value


def _optional_identifier(value: str | None, kind: IdentifierKind) -> str | None:
    return None if value is None else validate_identifier(value, kind)


class _Contract:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MessageIdentity(_Contract):
    """A persisted user or agent message inside one room and turn."""

    space_id: str
    room_id: str
    turn_id: str
    message_id: str
    task_id: str | None = None
    target_run_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "space_id", validate_identifier(self.space_id, "space"))
        object.__setattr__(self, "room_id", validate_identifier(self.room_id, "room"))
        object.__setattr__(self, "turn_id", validate_identifier(self.turn_id, "turn"))
        object.__setattr__(self, "message_id", validate_identifier(self.message_id, "message"))
        object.__setattr__(self, "task_id", _optional_identifier(self.task_id, "task"))
        object.__setattr__(
            self,
            "target_run_id",
            _optional_identifier(self.target_run_id, "run"),
        )


@dataclass(frozen=True)
class RunIdentity(_Contract):
    """A single immutable execution lineage inside a persistent task."""

    space_id: str
    room_id: str
    task_id: str
    run_id: str
    plan_id: str
    plan_revision: int = 1
    control_epoch: int = 0
    source_run_id: str | None = None
    trigger_turn_id: str | None = None

    def __post_init__(self) -> None:
        for field_name, kind in (
            ("space_id", "space"),
            ("room_id", "room"),
            ("task_id", "task"),
            ("run_id", "run"),
            ("plan_id", "plan"),
        ):
            object.__setattr__(
                self,
                field_name,
                validate_identifier(getattr(self, field_name), kind),
            )
        object.__setattr__(
            self,
            "source_run_id",
            _optional_identifier(self.source_run_id, "run"),
        )
        object.__setattr__(
            self,
            "trigger_turn_id",
            _optional_identifier(self.trigger_turn_id, "turn"),
        )
        object.__setattr__(
            self,
            "plan_revision",
            _version(self.plan_revision, "plan_revision", minimum=1),
        )
        object.__setattr__(
            self,
            "control_epoch",
            _version(self.control_epoch, "control_epoch", minimum=0),
        )
        if self.source_run_id == self.run_id:
            raise ValueError("source_run_id must not equal run_id")


@dataclass(frozen=True)
class AttemptIdentity(_Contract):
    """One attempt of a logical plan step, pinned to plan and control versions."""

    room_id: str
    task_id: str
    run_id: str
    plan_id: str
    step_id: str
    attempt_id: str
    plan_revision: int
    control_epoch: int

    def __post_init__(self) -> None:
        for field_name, kind in (
            ("room_id", "room"),
            ("task_id", "task"),
            ("run_id", "run"),
            ("plan_id", "plan"),
            ("step_id", "step"),
            ("attempt_id", "attempt"),
        ):
            object.__setattr__(
                self,
                field_name,
                validate_identifier(getattr(self, field_name), kind),
            )
        object.__setattr__(
            self,
            "plan_revision",
            _version(self.plan_revision, "plan_revision", minimum=1),
        )
        object.__setattr__(
            self,
            "control_epoch",
            _version(self.control_epoch, "control_epoch", minimum=0),
        )


@dataclass(frozen=True)
class OperationIdentity(_Contract):
    """A logical tool operation whose ID survives retry attempts."""

    room_id: str
    task_id: str
    run_id: str
    step_id: str
    attempt_id: str
    operation_id: str

    def __post_init__(self) -> None:
        for field_name, kind in (
            ("room_id", "room"),
            ("task_id", "task"),
            ("run_id", "run"),
            ("step_id", "step"),
            ("attempt_id", "attempt"),
            ("operation_id", "operation"),
        ):
            object.__setattr__(
                self,
                field_name,
                validate_identifier(getattr(self, field_name), kind),
            )


@dataclass(frozen=True)
class RoomEventIdentity(_Contract):
    """A committed room event and its gap-free per-room ordering key."""

    room_id: str
    event_id: str
    room_sequence: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "room_id", validate_identifier(self.room_id, "room"))
        object.__setattr__(self, "event_id", validate_identifier(self.event_id, "event"))
        object.__setattr__(
            self,
            "room_sequence",
            _version(self.room_sequence, "room_sequence", minimum=1),
        )


@dataclass(frozen=True)
class RoomEventCursor(_Contract):
    """Last committed sequence observed by a room subscriber; zero means none."""

    room_id: str
    room_sequence: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "room_id", validate_identifier(self.room_id, "room"))
        object.__setattr__(
            self,
            "room_sequence",
            _version(self.room_sequence, "room_sequence", minimum=0),
        )
