"""D06 in-memory conversation repositories.

The implementation is deliberately persistence-agnostic.  It provides the
atomic/idempotent contract that a PostgreSQL adapter must preserve later.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from threading import RLock
from typing import Literal
from uuid import uuid4

from agent_platform.contracts.identity import new_identifier, validate_identifier


class RepositoryError(RuntimeError):
    """Base class for repository contract failures."""


class NotFoundError(RepositoryError):
    pass


class ConflictError(RepositoryError):
    pass


class RoomClosedError(ConflictError):
    pass


@dataclass(frozen=True)
class Room:
    space_id: str
    room_id: str
    title: str
    status: Literal["active", "archived", "deleted"] = "active"
    room_sequence: int = 0
    row_version: int = 1


@dataclass(frozen=True)
class Message:
    message_id: str
    room_id: str
    content: str
    role: Literal["user", "assistant", "system", "tool"]
    status: Literal["saved", "queued", "applied", "rejected", "tombstoned"] = "saved"
    room_sequence: int = 0
    idempotency_key: str | None = None
    content_sha256: str = ""
    created_at: datetime | None = None


@dataclass(frozen=True)
class Membership:
    membership_id: str
    room_id: str
    agent_id: str
    status: Literal["active", "left", "removed"] = "active"
    joined_at: datetime | None = None
    left_at: datetime | None = None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must not be empty")
    return value.strip()


def _sha256(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class ConversationRepository:
    """Atomic room/message/member store used by D06 tests and prototypes."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._rooms: dict[str, Room] = {}
        self._messages: dict[str, Message] = {}
        self._memberships: dict[str, Membership] = {}
        self._idempotency: dict[tuple[str, str], str] = {}

    def create_room(self, space_id: str, title: str = "", *, room_id: str | None = None) -> Room:
        space_id = validate_identifier(space_id, "space")
        title = title.strip()
        with self._lock:
            identifier = validate_identifier(room_id, "room") if room_id else new_identifier("room")
            if identifier in self._rooms:
                raise ConflictError(f"room already exists: {identifier}")
            room = Room(space_id=space_id, room_id=identifier, title=title)
            self._rooms[identifier] = room
            return room

    def get_room(self, room_id: str) -> Room:
        room_id = validate_identifier(room_id, "room")
        with self._lock:
            try:
                return self._rooms[room_id]
            except KeyError as exc:
                raise NotFoundError(room_id) from exc

    def archive_room(self, room_id: str) -> Room:
        with self._lock:
            room = self.get_room(room_id)
            if room.status == "deleted":
                raise RoomClosedError("deleted room cannot be archived")
            updated = replace(room, status="archived", row_version=room.row_version + 1)
            self._rooms[room.room_id] = updated
            return updated

    def delete_room(self, room_id: str) -> Room:
        with self._lock:
            room = self.get_room(room_id)
            updated = replace(room, status="deleted", row_version=room.row_version + 1)
            self._rooms[room.room_id] = updated
            return updated

    def save_message(
        self,
        room_id: str,
        content: str,
        *,
        role: Literal["user", "assistant", "system", "tool"] = "user",
        idempotency_key: str | None = None,
        message_id: str | None = None,
    ) -> Message:
        room_id = validate_identifier(room_id, "room")
        content = _text(content, "content")
        if role not in {"user", "assistant", "system", "tool"}:
            raise ValueError(f"unsupported role: {role}")
        with self._lock:
            room = self.get_room(room_id)
            if room.status != "active":
                raise RoomClosedError(f"room is {room.status}")
            if idempotency_key:
                existing_id = self._idempotency.get((room_id, idempotency_key))
                if existing_id:
                    existing = self._messages[existing_id]
                    if existing.status == "tombstoned":
                        raise ConflictError("idempotency key belongs to tombstoned message")
                    if existing.content != content or existing.role != role:
                        raise ConflictError("idempotency key payload differs")
                    return existing
            identifier = validate_identifier(message_id, "message") if message_id else new_identifier("message")
            if identifier in self._messages:
                raise ConflictError(f"message already exists: {identifier}")
            sequence = room.room_sequence + 1
            message = Message(
                message_id=identifier,
                room_id=room_id,
                content=content,
                role=role,
                room_sequence=sequence,
                idempotency_key=idempotency_key,
                content_sha256=_sha256(content),
                created_at=_now(),
            )
            self._messages[identifier] = message
            if idempotency_key:
                self._idempotency[(room_id, idempotency_key)] = identifier
            self._rooms[room_id] = replace(room, room_sequence=sequence, row_version=room.row_version + 1)
            return message

    def update_message_status(self, message_id: str, status: Literal["queued", "applied", "rejected"]) -> Message:
        message_id = validate_identifier(message_id, "message")
        with self._lock:
            message = self._messages.get(message_id)
            if message is None:
                raise NotFoundError(message_id)
            if message.status == "tombstoned":
                raise ConflictError("tombstoned message cannot be requeued")
            updated = replace(message, status=status)
            self._messages[message_id] = updated
            return updated

    def tombstone_message(self, message_id: str) -> Message:
        message_id = validate_identifier(message_id, "message")
        with self._lock:
            message = self._messages.get(message_id)
            if message is None:
                raise NotFoundError(message_id)
            updated = replace(message, status="tombstoned")
            self._messages[message_id] = updated
            return updated

    def list_messages(self, room_id: str) -> tuple[Message, ...]:
        room_id = validate_identifier(room_id, "room")
        with self._lock:
            self.get_room(room_id)
            return tuple(sorted((m for m in self._messages.values() if m.room_id == room_id), key=lambda m: m.room_sequence))

    def join_member(self, room_id: str, agent_id: str) -> Membership:
        room_id = validate_identifier(room_id, "room")
        agent_id = _text(agent_id, "agent_id")
        with self._lock:
            room = self.get_room(room_id)
            if room.status != "active":
                raise RoomClosedError(f"room is {room.status}")
            membership = Membership(f"membership-{uuid4().hex}", room_id, agent_id, joined_at=_now())
            self._memberships[membership.membership_id] = membership
            return membership

    def leave_member(self, membership_id: str) -> Membership:
        if not isinstance(membership_id, str) or not membership_id.startswith("membership-"):
            raise ValueError("membership_id must start with 'membership-'")
        with self._lock:
            membership = self._memberships.get(membership_id)
            if membership is None:
                raise NotFoundError(membership_id)
            if membership.status != "active":
                return membership
            updated = replace(membership, status="left", left_at=_now())
            self._memberships[membership_id] = updated
            return updated

    def list_members(self, room_id: str) -> tuple[Membership, ...]:
        room_id = validate_identifier(room_id, "room")
        with self._lock:
            self.get_room(room_id)
            return tuple(m for m in self._memberships.values() if m.room_id == room_id)
