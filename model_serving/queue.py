from __future__ import annotations

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from threading import Condition
import time


class QueueFullError(RuntimeError):
    pass


class QueueTimeoutError(RuntimeError):
    pass


@dataclass(frozen=True)
class QueueSnapshot:
    active: int
    waiting: int


class _QueueLease:
    def __init__(self, queue: "GenerationQueue", timeout_seconds: float) -> None:
        self._queue = queue
        self._timeout_seconds = timeout_seconds
        self._acquired = False

    def __enter__(self) -> "_QueueLease":
        if self._acquired:
            raise RuntimeError("queue lease is already active")
        self._queue._enter(self._timeout_seconds)
        self._acquired = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self._acquired:
            self._acquired = False
            self._queue._leave()


class GenerationQueue:
    def __init__(
        self,
        active_limit: int = 1,
        waiting_limit: int = 4,
        *,
        on_change: Callable[[QueueSnapshot], None] | None = None,
    ) -> None:
        if type(active_limit) is not int or active_limit <= 0:
            raise ValueError("active_limit must be a positive integer")
        if type(waiting_limit) is not int or waiting_limit < 0:
            raise ValueError("waiting_limit must be a non-negative integer")
        self._active_limit = active_limit
        self._waiting_limit = waiting_limit
        self._condition = Condition()
        self._active = 0
        self._waiters: deque[object] = deque()
        self._on_change = on_change

    def acquire(self, timeout_seconds: float) -> _QueueLease:
        if not isinstance(timeout_seconds, (int, float)) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        return _QueueLease(self, float(timeout_seconds))

    def snapshot(self) -> QueueSnapshot:
        with self._condition:
            return QueueSnapshot(self._active, len(self._waiters))

    def _notify_change(self) -> None:
        if self._on_change is None:
            return
        try:
            self._on_change(QueueSnapshot(self._active, len(self._waiters)))
        except Exception:
            return

    def _enter(self, timeout_seconds: float) -> None:
        deadline = time.monotonic() + timeout_seconds
        with self._condition:
            if self._active < self._active_limit and not self._waiters:
                self._active += 1
                self._notify_change()
                return
            if len(self._waiters) >= self._waiting_limit:
                raise QueueFullError("generation queue is full")
            ticket = object()
            self._waiters.append(ticket)
            self._notify_change()
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self._waiters.remove(ticket)
                    self._notify_change()
                    self._condition.notify_all()
                    raise QueueTimeoutError("generation queue wait timed out")
                self._condition.wait(timeout=remaining)
                if (
                    self._waiters
                    and self._waiters[0] is ticket
                    and self._active < self._active_limit
                ):
                    self._waiters.popleft()
                    self._active += 1
                    self._notify_change()
                    return

    def _leave(self) -> None:
        with self._condition:
            if self._active <= 0:
                raise RuntimeError("generation queue active count underflow")
            self._active -= 1
            self._notify_change()
            self._condition.notify_all()
