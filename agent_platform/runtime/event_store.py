"""D07 append-only event store and cursor projection.

This in-memory implementation defines the ordering and replay contract used
by the future PostgreSQL/SSE adapter.  It never invokes a model or tool while
reading or replaying events.
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable

from agent_platform.contracts.execution import EventType, RunEvent
from agent_platform.contracts.identity import RoomEventCursor, RoomEventIdentity, new_identifier, validate_identifier


class EventStoreError(RuntimeError):
    pass


class EventConflictError(EventStoreError):
    pass


@dataclass(frozen=True)
class RoomSnapshot:
    room_id: str
    cursor: RoomEventCursor
    events: tuple[RunEvent, ...]


class EventStore:
    """Thread-safe append/read store with gap-free per-room ordering."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._events: dict[str, list[RunEvent]] = {}
        self._by_id: dict[str, RunEvent] = {}

    def append(
        self,
        room_id: str,
        event_type: EventType,
        *,
        event_id: str | None = None,
        task_id: str | None = None,
        run_id: str | None = None,
        step_id: str | None = None,
        attempt_id: str | None = None,
        run_sequence: int = 0,
        caused_by: tuple[str, ...] = (),
        consumes: tuple[str, ...] = (),
        produces: tuple[str, ...] = (),
        usage: dict[str, int] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> RunEvent:
        room_id = validate_identifier(room_id, "room")
        with self._lock:
            if event_id is not None:
                event_id = validate_identifier(event_id, "event")
                existing = self._by_id.get(event_id)
                if existing is not None:
                    if existing.room_id != room_id or existing.event_type != event_type:
                        raise EventConflictError("event_id is already bound to another event")
                    return existing
            sequence = len(self._events.get(room_id, ())) + 1
            event = RunEvent(
                identity=RoomEventIdentity(
                    room_id=room_id,
                    event_id=event_id or new_identifier("event"),
                    room_sequence=sequence,
                ),
                event_type=event_type,
                room_id=room_id,
                task_id=task_id,
                run_id=run_id,
                step_id=step_id,
                attempt_id=attempt_id,
                run_sequence=run_sequence,
                caused_by=caused_by,
                consumes=consumes,
                produces=produces,
                usage=usage or {},
                payload=payload or {},
            )
            self._events.setdefault(room_id, []).append(event)
            self._by_id[event.identity.event_id] = event
            return event

    def append_and_publish(self, publisher: Callable[[RunEvent], None], *args: Any, **kwargs: Any) -> RunEvent:
        """Commit first, then publish; a publisher failure cannot erase the event."""
        event = self.append(*args, **kwargs)
        publisher(event)
        return event

    def read_after(self, cursor: RoomEventCursor, *, limit: int | None = None) -> tuple[RunEvent, ...]:
        with self._lock:
            events = tuple(event for event in self._events.get(cursor.room_id, ()) if event.identity.room_sequence > cursor.room_sequence)
            if limit is not None:
                if type(limit) is not int or limit <= 0:
                    raise ValueError("limit must be a positive int")
                events = events[:limit]
            return events

    def snapshot(self, room_id: str) -> RoomSnapshot:
        room_id = validate_identifier(room_id, "room")
        with self._lock:
            events = tuple(self._events.get(room_id, ()))
            sequence = events[-1].identity.room_sequence if events else 0
            return RoomSnapshot(room_id, RoomEventCursor(room_id, sequence), events)

    def replay(self, snapshot: RoomSnapshot) -> tuple[RunEvent, ...]:
        """Return persisted events only; replay has no execution side effects."""
        if not isinstance(snapshot, RoomSnapshot):
            raise TypeError("snapshot must be a RoomSnapshot")
        return snapshot.events

