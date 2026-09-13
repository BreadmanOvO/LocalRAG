"""D08 worker leases, fencing and run control.

The module is an in-memory reference implementation of the Runtime write
boundary.  It is intentionally deterministic and injectable so the same
state transitions can be exercised before the PostgreSQL worker adapter is
introduced.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Callable, Literal
from uuid import uuid4

from agent_platform.contracts.identity import new_identifier, validate_identifier


class ControlError(RuntimeError):
    pass


class ControlConflictError(ControlError):
    """Expected version, lease ownership, or fencing token is stale."""


class LeaseConflictError(ControlConflictError):
    pass


class RunNotClaimableError(ControlError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _future(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class WorkerLease:
    lease_id: str
    step_id: str
    run_id: str
    worker_id: str
    fencing_token: int
    control_epoch: int
    expires_at: datetime
    status: Literal["active", "expired", "released"] = "active"


@dataclass(frozen=True)
class AttemptRecord:
    attempt_id: str
    step_id: str
    run_id: str
    worker_id: str
    plan_revision: int
    control_epoch: int
    fencing_token: int
    lease_id: str
    status: Literal["running", "succeeded", "failed", "expired", "cancelled", "late_audit", "rejected"] = "running"
    result: str | None = None
    finished_at: datetime | None = None
    audit_reason: str | None = None


@dataclass(frozen=True)
class RunControlState:
    run_id: str
    plan_revision: int
    status: Literal["queued", "running", "paused", "needs_input", "completed", "failed", "cancelled"]
    control_epoch: int = 0
    row_version: int = 1


class LeaseManager:
    """Issue monotonically fenced worker leases for logical steps."""

    def __init__(self, *, clock: Callable[[], datetime] = _now) -> None:
        self._clock = clock
        self._lock = RLock()
        self._current: dict[str, WorkerLease] = {}
        self._tokens: dict[str, int] = {}

    def acquire(
        self,
        step_id: str,
        run_id: str,
        worker_id: str,
        *,
        control_epoch: int,
        ttl_seconds: int = 30,
    ) -> WorkerLease:
        step_id = validate_identifier(step_id, "step")
        run_id = validate_identifier(run_id, "run")
        if not isinstance(worker_id, str) or not worker_id.strip():
            raise ValueError("worker_id must not be empty")
        if type(control_epoch) is not int or control_epoch < 0:
            raise ValueError("control_epoch must be non-negative")
        if type(ttl_seconds) is not int or ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        with self._lock:
            current = self._current.get(step_id)
            now = _future(self._clock())
            if current and current.status == "active" and current.expires_at > now:
                raise LeaseConflictError(f"step is leased by {current.worker_id}")
            if current and current.status == "active":
                self._current[step_id] = replace(current, status="expired")
            token = self._tokens.get(step_id, 0) + 1
            self._tokens[step_id] = token
            lease = WorkerLease(
                lease_id=f"lease-{uuid4().hex}",
                step_id=step_id,
                run_id=run_id,
                worker_id=worker_id.strip(),
                fencing_token=token,
                control_epoch=control_epoch,
                expires_at=now + timedelta(seconds=ttl_seconds),
            )
            self._current[step_id] = lease
            return lease

    def renew(self, lease_id: str, *, worker_id: str, ttl_seconds: int = 30) -> WorkerLease:
        with self._lock:
            lease = self._find(lease_id)
            self._assert_active(lease, worker_id=worker_id)
            updated = replace(lease, expires_at=_future(self._clock()) + timedelta(seconds=ttl_seconds))
            self._current[lease.step_id] = updated
            return updated

    def release(self, lease_id: str, *, worker_id: str) -> WorkerLease:
        with self._lock:
            lease = self._find(lease_id)
            self._assert_current(lease, worker_id=worker_id)
            updated = replace(lease, status="released")
            self._current[lease.step_id] = updated
            return updated

    def assert_valid(self, lease_id: str, *, worker_id: str, fencing_token: int, control_epoch: int) -> WorkerLease:
        with self._lock:
            lease = self._find(lease_id)
            self._assert_active(lease, worker_id=worker_id)
            if lease.fencing_token != fencing_token or lease.control_epoch != control_epoch:
                raise ControlConflictError("lease fencing or control epoch is stale")
            return lease

    def _find(self, lease_id: str) -> WorkerLease:
        for lease in self._current.values():
            if lease.lease_id == lease_id:
                return lease
        raise ControlConflictError("unknown lease")

    def _assert_current(self, lease: WorkerLease, *, worker_id: str) -> None:
        current = self._current.get(lease.step_id)
        if current != lease or current.worker_id != worker_id:
            raise ControlConflictError("lease is fenced by a newer worker")

    def _assert_active(self, lease: WorkerLease, *, worker_id: str) -> None:
        self._assert_current(lease, worker_id=worker_id)
        now = _future(self._clock())
        if lease.status != "active" or lease.expires_at <= now:
            if lease.status == "active":
                self._current[lease.step_id] = replace(lease, status="expired")
            raise ControlConflictError("lease is expired")


class RunController:
    """CAS-protected run state and fenced attempt submission."""

    def __init__(self, *, lease_manager: LeaseManager | None = None, clock: Callable[[], datetime] = _now) -> None:
        self._clock = clock
        self._leases = lease_manager or LeaseManager(clock=clock)
        self._lock = RLock()
        self._runs: dict[str, RunControlState] = {}
        self._attempts: dict[str, AttemptRecord] = {}
        self._audit: list[AttemptRecord] = []

    @property
    def leases(self) -> LeaseManager:
        return self._leases

    def register_run(self, run_id: str, *, plan_revision: int = 1, status: str = "queued") -> RunControlState:
        run_id = validate_identifier(run_id, "run")
        if type(plan_revision) is not int or plan_revision <= 0:
            raise ValueError("plan_revision must be positive")
        if status not in {"queued", "running", "paused", "needs_input", "completed", "failed", "cancelled"}:
            raise ValueError("unsupported run status")
        with self._lock:
            if run_id in self._runs:
                raise ControlConflictError("run already exists")
            state = RunControlState(run_id, plan_revision, status)  # type: ignore[arg-type]
            self._runs[run_id] = state
            return state

    def get_run(self, run_id: str) -> RunControlState:
        try:
            return self._runs[validate_identifier(run_id, "run")]
        except KeyError as exc:
            raise ControlError("unknown run") from exc

    def start(self, run_id: str, *, expected_row_version: int) -> RunControlState:
        with self._lock:
            state = self._checked(run_id, expected_row_version)
            if state.status not in {"queued", "paused"}:
                raise RunNotClaimableError(f"run is {state.status}")
            updated = replace(state, status="running", control_epoch=state.control_epoch + 1, row_version=state.row_version + 1)
            self._runs[state.run_id] = updated
            return updated

    def pause(self, run_id: str, *, expected_row_version: int, expected_control_epoch: int) -> RunControlState:
        return self._control(run_id, expected_row_version, expected_control_epoch, "paused")

    def cancel(self, run_id: str, *, expected_row_version: int, expected_control_epoch: int) -> RunControlState:
        return self._control(run_id, expected_row_version, expected_control_epoch, "cancelled")

    def finish(self, run_id: str, *, status: Literal["completed", "failed"], expected_row_version: int) -> RunControlState:
        with self._lock:
            state = self._checked(run_id, expected_row_version)
            if state.status in {"completed", "failed", "cancelled"}:
                return state
            updated = replace(state, status=status, row_version=state.row_version + 1)
            self._runs[state.run_id] = updated
            return updated

    def claim_attempt(
        self,
        run_id: str,
        step_id: str,
        worker_id: str,
        *,
        expected_row_version: int,
        plan_revision: int,
        ttl_seconds: int = 30,
    ) -> AttemptRecord:
        with self._lock:
            state = self._checked(run_id, expected_row_version)
            if state.status != "running":
                raise RunNotClaimableError(f"run is {state.status}")
            if state.plan_revision != plan_revision:
                raise ControlConflictError("plan revision is stale")
            lease = self._leases.acquire(step_id, state.run_id, worker_id, control_epoch=state.control_epoch, ttl_seconds=ttl_seconds)
            attempt = AttemptRecord(
                attempt_id=new_identifier("attempt"),
                step_id=lease.step_id,
                run_id=state.run_id,
                worker_id=lease.worker_id,
                plan_revision=plan_revision,
                control_epoch=state.control_epoch,
                fencing_token=lease.fencing_token,
                lease_id=lease.lease_id,
            )
            self._attempts[attempt.attempt_id] = attempt
            self._runs[state.run_id] = replace(state, row_version=state.row_version + 1)
            return attempt

    def submit_attempt(self, attempt_id: str, *, result: str, status: Literal["succeeded", "failed"] = "succeeded") -> AttemptRecord:
        with self._lock:
            attempt = self._attempts.get(validate_identifier(attempt_id, "attempt"))
            if attempt is None:
                raise ControlError("unknown attempt")
            if attempt.status != "running":
                return attempt
            state = self.get_run(attempt.run_id)
            try:
                self._leases.assert_valid(
                    attempt.lease_id,
                    worker_id=attempt.worker_id,
                    fencing_token=attempt.fencing_token,
                    control_epoch=attempt.control_epoch,
                )
                if state.status != "running" or state.control_epoch != attempt.control_epoch:
                    raise ControlConflictError("run control state is stale")
            except ControlConflictError as exc:
                late = replace(attempt, status="late_audit", result=result, finished_at=_future(self._clock()), audit_reason=str(exc))
                self._attempts[attempt.attempt_id] = late
                self._audit.append(late)
                return late
            completed = replace(attempt, status=status, result=result, finished_at=_future(self._clock()))
            self._attempts[attempt.attempt_id] = completed
            self._runs[state.run_id] = replace(state, row_version=state.row_version + 1)
            return completed

    def list_audit(self) -> tuple[AttemptRecord, ...]:
        with self._lock:
            return tuple(self._audit)

    def _checked(self, run_id: str, expected_row_version: int) -> RunControlState:
        state = self.get_run(run_id)
        if state.row_version != expected_row_version:
            raise ControlConflictError("row_version CAS failed")
        return state

    def _control(self, run_id: str, expected_row_version: int, expected_control_epoch: int, status: str) -> RunControlState:
        with self._lock:
            state = self._checked(run_id, expected_row_version)
            if state.control_epoch != expected_control_epoch:
                raise ControlConflictError("control_epoch CAS failed")
            if state.status in {"completed", "failed", "cancelled"}:
                return state
            updated = replace(state, status=status, control_epoch=state.control_epoch + 1, row_version=state.row_version + 1)  # type: ignore[arg-type]
            self._runs[state.run_id] = updated
            return updated
