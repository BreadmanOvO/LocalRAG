"""SQLAlchemy EventStore adapter used by D36 persistence tests and workers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

from sqlalchemy import Column, DateTime, Integer, JSON, MetaData, String, Table, Text, create_engine, insert, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from agent_platform.contracts.execution import EventType, RunEvent
from agent_platform.contracts.identity import RoomEventCursor, RoomEventIdentity, new_identifier, validate_identifier
from .event_store import EventConflictError, RoomSnapshot


class SqlAlchemyEventStore:
    """Append-only SQL event store with per-room sequence allocation."""

    def __init__(self, engine: Engine, *, create_schema: bool = True) -> None:
        self.engine = engine
        self.metadata = MetaData()
        self.events = Table(
            "run_events", self.metadata,
            Column("event_id", String(255), primary_key=True),
            Column("room_id", String(255), nullable=False),
            Column("task_id", String(255)), Column("run_id", String(255)),
            Column("step_id", String(255)), Column("attempt_id", String(255)),
            Column("event_type", String(64), nullable=False),
            Column("room_sequence", Integer, nullable=False),
            Column("run_sequence", Integer, nullable=False, default=0),
            Column("caused_by", JSON, nullable=False), Column("consumes", JSON, nullable=False),
            Column("produces", JSON, nullable=False), Column("usage", JSON, nullable=False),
            Column("payload", JSON, nullable=False),
            Column("timestamp", Text, nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
        )
        if create_schema and engine.dialect.name == "sqlite":
            self.metadata.create_all(engine)

    def append(self, room_id: str, event_type: EventType, *, event_id: str | None = None,
               task_id: str | None = None, run_id: str | None = None,
               step_id: str | None = None, attempt_id: str | None = None,
               run_sequence: int = 0, caused_by: tuple[str, ...] = (),
               consumes: tuple[str, ...] = (), produces: tuple[str, ...] = (),
               usage: dict[str, int] | None = None, payload: dict[str, Any] | None = None) -> RunEvent:
        room_id = validate_identifier(room_id, "room")
        identifier = validate_identifier(event_id, "event") if event_id else new_identifier("event")
        now = datetime.now(timezone.utc).isoformat()
        try:
            with self.engine.begin() as conn:
                # The production migration adds a room-row lock around this
                # allocation; the compact adapter uses the event unique key.
                existing = conn.execute(select(self.events).where(self.events.c.event_id == identifier)).mappings().first()
                if existing is not None:
                    if existing["room_id"] != room_id or existing["event_type"] != event_type:
                        raise EventConflictError("event_id is already bound to another event")
                    return self._event(existing)
                current = conn.execute(select(self.events.c.room_sequence).where(self.events.c.room_id == room_id).order_by(self.events.c.room_sequence.desc()).limit(1)).scalar()
                sequence = int(current or 0) + 1
                conn.execute(insert(self.events).values(event_id=identifier, room_id=room_id, task_id=task_id, run_id=run_id, step_id=step_id, attempt_id=attempt_id, event_type=event_type, room_sequence=sequence, run_sequence=run_sequence, caused_by=list(caused_by), consumes=list(consumes), produces=list(produces), usage=usage or {}, payload=payload or {}, timestamp=now, created_at=datetime.now(timezone.utc)))
                row = conn.execute(select(self.events).where(self.events.c.event_id == identifier)).mappings().one()
                return self._event(row)
        except IntegrityError as exc:
            raise EventConflictError("event sequence conflicted") from exc

    def read_after(self, cursor: RoomEventCursor, *, limit: int | None = None) -> tuple[RunEvent, ...]:
        if limit is not None and limit < 1:
            raise ValueError("limit must be positive")
        statement = select(self.events).where(self.events.c.room_id == validate_identifier(cursor.room_id, "room"), self.events.c.room_sequence > cursor.room_sequence).order_by(self.events.c.room_sequence)
        if limit is not None:
            statement = statement.limit(limit)
        with self.engine.connect() as conn:
            rows = conn.execute(statement).mappings().all()
        return tuple(self._event(row) for row in rows)

    def snapshot(self, room_id: str) -> RoomSnapshot:
        events = self.read_after(RoomEventCursor(validate_identifier(room_id, "room"), 0))
        cursor = RoomEventCursor(room_id, events[-1].identity.room_sequence if events else 0)
        return RoomSnapshot(room_id, cursor, events)

    @staticmethod
    def _event(row: Any) -> RunEvent:
        return RunEvent(RoomEventIdentity(row["room_id"], row["event_id"], row["room_sequence"]), row["event_type"], row["room_id"], row["task_id"], row["run_id"], row["step_id"], row["attempt_id"], row["run_sequence"], tuple(row["caused_by"]), tuple(row["consumes"]), tuple(row["produces"]), dict(row["usage"]), dict(row["payload"]), row["timestamp"])
