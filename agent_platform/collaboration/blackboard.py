"""Shared work items and bounded swarm coordination contracts for D19-D20."""
from __future__ import annotations
from dataclasses import dataclass, replace
from threading import RLock
from time import monotonic
from uuid import uuid4

@dataclass(frozen=True)
class WorkItem:
    work_id: str
    room_id: str
    title: str
    required_capabilities: tuple[str, ...] = ()
    status: str = "queued"
    claimed_by: str | None = None
    lease_until: float | None = None

class Blackboard:
    def __init__(self) -> None:
        self._lock = RLock(); self._items: dict[str, WorkItem] = {}
    def publish(self, room_id: str, title: str, required_capabilities: tuple[str, ...] = ()) -> WorkItem:
        item = WorkItem(f"work-{uuid4().hex}", room_id, title.strip(), tuple(required_capabilities))
        if not item.title: raise ValueError("title must not be empty")
        with self._lock: self._items[item.work_id] = item
        return item
    def claim(self, work_id: str, agent_id: str, *, lease_seconds: float = 60) -> WorkItem:
        with self._lock:
            item = self._items[work_id]
            now = monotonic()
            if item.status == "claimed" and (item.lease_until or 0) > now: raise ValueError("work item already claimed")
            updated = replace(item, status="claimed", claimed_by=agent_id, lease_until=now + lease_seconds)
            self._items[work_id] = updated; return updated
    def complete(self, work_id: str, agent_id: str) -> WorkItem:
        with self._lock:
            item = self._items[work_id]
            if item.claimed_by != agent_id: raise ValueError("only claimant can complete work")
            updated = replace(item, status="completed"); self._items[work_id] = updated; return updated
    def list_open(self, room_id: str) -> tuple[WorkItem, ...]:
        with self._lock: return tuple(item for item in self._items.values() if item.room_id == room_id and item.status != "completed")

class SwarmReducer:
    def __init__(self, *, max_items: int = 32, idle_rounds: int = 2) -> None:
        self.max_items, self.idle_rounds = max_items, idle_rounds
    def should_stop(self, items: tuple[WorkItem, ...], *, idle_rounds: int, budget_exhausted: bool = False) -> tuple[bool, str]:
        if budget_exhausted: return True, "budget_exhausted"
        if len(items) >= self.max_items: return True, "derivation_limit"
        if not items and idle_rounds >= self.idle_rounds: return True, "idle_converged"
        return False, "continue"
