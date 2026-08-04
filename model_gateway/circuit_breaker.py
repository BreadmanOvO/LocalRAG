from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
import math
import time
from uuid import uuid4

from .models import GatewayError


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(RuntimeError):
    pass


@dataclass(frozen=True)
class CircuitPermit:
    token: str
    probe: bool


@dataclass(frozen=True)
class CircuitSnapshot:
    state: CircuitState
    failure_count: int
    probe_in_flight: bool
    opened_at: float | None


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        reset_seconds: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
        transition_sink: Callable[[CircuitState, CircuitState], None] | None = None,
    ) -> None:
        if type(failure_threshold) is not int or failure_threshold <= 0:
            raise ValueError("failure_threshold must be a positive int")
        if (
            isinstance(reset_seconds, bool)
            or not isinstance(reset_seconds, (int, float))
            or not math.isfinite(reset_seconds)
            or reset_seconds <= 0
        ):
            raise ValueError("reset_seconds must be positive")
        self.failure_threshold = failure_threshold
        self.reset_seconds = float(reset_seconds)
        self._clock = clock
        self._transition_sink = transition_sink
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._opened_at: float | None = None
        self._probe_in_flight = False
        self._active: dict[str, CircuitPermit] = {}
        import threading

        self._lock = threading.Lock()

    def before_request(self) -> CircuitPermit:
        with self._lock:
            now = self._clock()
            if self._state is CircuitState.OPEN:
                if self._opened_at is None or now - self._opened_at < self.reset_seconds:
                    raise CircuitOpenError("local model circuit is open")
                self._set_state(CircuitState.HALF_OPEN)
            if self._state is CircuitState.HALF_OPEN:
                if self._probe_in_flight:
                    raise CircuitOpenError("local model circuit probe is in flight")
                self._probe_in_flight = True
                permit = CircuitPermit(uuid4().hex, probe=True)
            else:
                permit = CircuitPermit(uuid4().hex, probe=False)
            self._active[permit.token] = permit
            return permit

    def record_success(self, permit: CircuitPermit) -> None:
        with self._lock:
            active = self._active.pop(permit.token, None)
            if active is None:
                return
            if active.probe:
                self._probe_in_flight = False
            self._set_state(CircuitState.CLOSED)
            self._failure_count = 0
            self._opened_at = None

    def record_failure(self, permit: CircuitPermit, error: GatewayError) -> None:
        with self._lock:
            active = self._active.pop(permit.token, None)
            if active is None:
                return
            if active.probe:
                self._probe_in_flight = False
            if error.started or not error.fallback_allowed:
                return
            if active.probe:
                self._set_state(CircuitState.OPEN)
                self._opened_at = self._clock()
                self._failure_count = self.failure_threshold
                return
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._set_state(CircuitState.OPEN)
                self._opened_at = self._clock()

    def release(self, permit: CircuitPermit | None) -> None:
        if permit is None:
            return
        with self._lock:
            active = self._active.pop(permit.token, None)
            if active is not None and active.probe:
                self._probe_in_flight = False

    def snapshot(self) -> CircuitSnapshot:
        with self._lock:
            return CircuitSnapshot(
                state=self._state,
                failure_count=self._failure_count,
                probe_in_flight=self._probe_in_flight,
                opened_at=self._opened_at,
            )

    def _set_state(self, state: CircuitState) -> None:
        previous = self._state
        self._state = state
        if previous is not state and self._transition_sink is not None:
            self._transition_sink(previous, state)
