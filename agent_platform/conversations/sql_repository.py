"""SQLAlchemy conversation repository for PostgreSQL and local smoke tests.

The adapter intentionally implements the same small contract as
``ConversationRepository``.  A room lock and a single transaction protect the
per-room message sequence, while the unique idempotency key makes retries
safe across processes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, UniqueConstraint, create_engine, insert, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from agent_platform.contracts.identity import new_identifier, validate_identifier
from .repository import ConflictError, Membership, Message, NotFoundError, Room, RoomClosedError


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SqlAlchemyConversationRepository:
    """Transactional repository backed by a SQLAlchemy engine.

    PostgreSQL is the production target (use ``postgresql+psycopg://``); SQLite
    is supported for deterministic local integration tests.
    """

    def __init__(self, engine: Engine, *, create_schema: bool = True) -> None:
        self.engine = engine
        self.metadata = MetaData()
        self.spaces = Table("spaces", self.metadata,
            Column("space_id", String(255), primary_key=True),
            Column("name", Text, nullable=False, default=""),
        )
        self.rooms = Table("rooms", self.metadata,
            Column("room_id", String(255), primary_key=True),
            Column("space_id", String(255), nullable=False),
            Column("status", String(16), nullable=False),
            Column("title", Text, nullable=False, default=""),
            Column("room_sequence", Integer, nullable=False, default=0),
            Column("row_version", Integer, nullable=False, default=1),
            Column("created_at", DateTime(timezone=True), nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
        )
        self.messages = Table("messages", self.metadata,
            Column("message_id", String(255), primary_key=True),
            Column("room_id", String(255), nullable=False),
            Column("task_id", String(255)),
            Column("turn_id", String(255), nullable=False, default="turn-legacy"),
            Column("content", Text, nullable=False),
            Column("role", String(16), nullable=False),
            Column("status", String(16), nullable=False),
            Column("room_sequence", Integer, nullable=False),
            Column("idempotency_key", String(255)),
            Column("content_sha256", String(64), nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
            UniqueConstraint("room_id", "room_sequence"),
            UniqueConstraint("room_id", "idempotency_key"),
        )
        self.memberships = Table("room_memberships", self.metadata,
            Column("membership_id", String(255), primary_key=True),
            Column("room_id", String(255), nullable=False),
            Column("agent_id", String(255), nullable=False),
            Column("status", String(16), nullable=False),
            Column("joined_at", DateTime(timezone=True), nullable=False),
            Column("left_at", DateTime(timezone=True)),
        )
        if create_schema and engine.dialect.name == "sqlite":
            self.metadata.create_all(engine)

    @classmethod
    def from_url(cls, url: str, *, create_schema: bool = True) -> "SqlAlchemyConversationRepository":
        return cls(create_engine(url, future=True, pool_pre_ping=True), create_schema=create_schema)

    def close(self) -> None:
        """Release pooled connections (useful for process shutdown and tests)."""
        self.engine.dispose()

    def create_room(self, space_id: str, title: str = "", *, room_id: str | None = None) -> Room:
        space_id = validate_identifier(space_id, "space")
        room_id = validate_identifier(room_id, "room") if room_id else new_identifier("room")
        now = _now()
        try:
            with self.engine.begin() as conn:
                existing_space = conn.execute(select(self.spaces.c.space_id).where(self.spaces.c.space_id == space_id)).first()
                if existing_space is None:
                    conn.execute(insert(self.spaces).values(space_id=space_id, name=space_id))
                conn.execute(insert(self.rooms).values(room_id=room_id, space_id=space_id, status="active", title=title.strip(), room_sequence=0, row_version=1, created_at=now, updated_at=now))
        except IntegrityError as exc:
            raise ConflictError(f"room already exists: {room_id}") from exc
        return self.get_room(room_id)

    def create_room_with_message(self, space_id: str, title: str, content: str, *, room_id: str | None = None, idempotency_key: str | None = None) -> tuple[Room, Message]:
        space_id = validate_identifier(space_id, "space")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content must not be empty")
        room_id = validate_identifier(room_id, "room") if room_id else new_identifier("room")
        message_id = new_identifier("message")
        now = _now()
        try:
            with self.engine.begin() as conn:
                if conn.execute(select(self.spaces.c.space_id).where(self.spaces.c.space_id == space_id)).first() is None:
                    conn.execute(insert(self.spaces).values(space_id=space_id, name=space_id))
                conn.execute(insert(self.rooms).values(room_id=room_id, space_id=space_id, status="active", title=title.strip(), room_sequence=0, row_version=1, created_at=now, updated_at=now))
                conn.execute(insert(self.messages).values(message_id=message_id, room_id=room_id, task_id=None, turn_id=f"turn-{message_id}", content=content.strip(), role="user", status="saved", room_sequence=1, idempotency_key=idempotency_key, content_sha256=sha256(content.strip().encode()).hexdigest(), created_at=now))
                conn.execute(update(self.rooms).where(self.rooms.c.room_id == room_id).values(room_sequence=1, row_version=2, updated_at=now))
        except IntegrityError as exc:
            raise ConflictError("room or initial message already exists") from exc
        return self.get_room(room_id), self._message({"message_id": message_id, "room_id": room_id, "content": content.strip(), "role": "user", "status": "saved", "room_sequence": 1, "idempotency_key": idempotency_key, "content_sha256": sha256(content.strip().encode()).hexdigest(), "created_at": now})

    def get_room(self, room_id: str) -> Room:
        room_id = validate_identifier(room_id, "room")
        with self.engine.connect() as conn:
            row = conn.execute(select(self.rooms).where(self.rooms.c.room_id == room_id)).mappings().first()
        if row is None:
            raise NotFoundError(room_id)
        return Room(row["space_id"], row["room_id"], row["title"], row["status"], row["room_sequence"], row["row_version"])

    def list_rooms(self, space_id: str | None = None) -> tuple[Room, ...]:
        statement = select(self.rooms).order_by(self.rooms.c.room_id)
        if space_id:
            statement = statement.where(self.rooms.c.space_id == validate_identifier(space_id, "space"))
        with self.engine.connect() as conn:
            rows = conn.execute(statement).mappings().all()
        return tuple(Room(row["space_id"], row["room_id"], row["title"], row["status"], row["room_sequence"], row["row_version"]) for row in rows)

    def save_message(self, room_id: str, content: str, *, role: Literal["user", "assistant", "system", "tool"] = "user", idempotency_key: str | None = None, message_id: str | None = None) -> Message:
        room_id = validate_identifier(room_id, "room")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content must not be empty")
        if role not in {"user", "assistant", "system", "tool"}:
            raise ValueError(f"unsupported role: {role}")
        identifier = validate_identifier(message_id, "message") if message_id else new_identifier("message")
        now = _now()
        try:
            with self.engine.begin() as conn:
                room = conn.execute(select(self.rooms).where(self.rooms.c.room_id == room_id).with_for_update()).mappings().first()
                if room is None:
                    raise NotFoundError(room_id)
                if room["status"] != "active":
                    raise RoomClosedError(f"room is {room['status']}")
                if idempotency_key:
                    existing = conn.execute(select(self.messages).where(self.messages.c.room_id == room_id, self.messages.c.idempotency_key == idempotency_key)).mappings().first()
                    if existing is not None:
                        if existing["status"] == "tombstoned":
                            raise ConflictError("idempotency key belongs to tombstoned message")
                        if existing["content"] != content.strip() or existing["role"] != role:
                            raise ConflictError("idempotency key payload differs")
                        return self._message(existing)
                sequence = int(room["room_sequence"]) + 1
                conn.execute(insert(self.messages).values(message_id=identifier, room_id=room_id, task_id=None, turn_id=f"turn-{identifier}", content=content.strip(), role=role, status="saved", room_sequence=sequence, idempotency_key=idempotency_key, content_sha256=sha256(content.strip().encode()).hexdigest(), created_at=now))
                conn.execute(update(self.rooms).where(self.rooms.c.room_id == room_id).values(room_sequence=sequence, row_version=int(room["row_version"]) + 1, updated_at=now))
                row = conn.execute(select(self.messages).where(self.messages.c.message_id == identifier)).mappings().one()
                return self._message(row)
        except IntegrityError as exc:
            raise ConflictError("message already exists or room sequence conflicted") from exc

    def list_messages(self, room_id: str, *, after: int = 0, limit: int | None = None) -> tuple[Message, ...]:
        if after < 0 or (limit is not None and limit < 1):
            raise ValueError("invalid message page")
        self.get_room(room_id)
        statement = select(self.messages).where(self.messages.c.room_id == validate_identifier(room_id, "room"), self.messages.c.room_sequence > after).order_by(self.messages.c.room_sequence)
        if limit is not None:
            statement = statement.limit(limit)
        with self.engine.connect() as conn:
            rows = conn.execute(statement).mappings().all()
        return tuple(self._message(row) for row in rows)

    def list_members(self, room_id: str) -> tuple[Membership, ...]:
        self.get_room(room_id)
        with self.engine.connect() as conn:
            rows = conn.execute(select(self.memberships).where(self.memberships.c.room_id == validate_identifier(room_id, "room")).order_by(self.memberships.c.joined_at)).mappings().all()
        return tuple(Membership(row["membership_id"], row["room_id"], row["agent_id"], row["status"], row["joined_at"], row["left_at"]) for row in rows)

    def join_member(self, room_id: str, agent_id: str) -> Membership:
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id must not be empty")
        membership = Membership(f"membership-{uuid4().hex}", validate_identifier(room_id, "room"), agent_id.strip(), joined_at=_now())
        with self.engine.begin() as conn:
            room = conn.execute(select(self.rooms).where(self.rooms.c.room_id == room_id).with_for_update()).mappings().first()
            if room is None:
                raise NotFoundError(room_id)
            if room["status"] != "active":
                raise RoomClosedError(f"room is {room['status']}")
            conn.execute(insert(self.memberships).values(membership_id=membership.membership_id, room_id=membership.room_id, agent_id=membership.agent_id, status="active", joined_at=membership.joined_at))
        return membership

    @staticmethod
    def _message(row) -> Message:
        return Message(row["message_id"], row["room_id"], row["content"], row["role"], row["status"], row["room_sequence"], row["idempotency_key"], row["content_sha256"], row["created_at"])
