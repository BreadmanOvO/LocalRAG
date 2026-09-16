"""Durable task/run/job records shared by API and worker processes."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any
from dataclasses import asdict

from .control import ControlConflictError, ControlError, RunController, RunControlState

from sqlalchemy import JSON, BigInteger, Column, DateTime, Integer, MetaData, String, Table, Text, create_engine, insert, select, update, and_, or_, func
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SqlRuntimeStore:
    """Small transactional store for API-visible task/run/job state.

    The adapter intentionally stores only model profile references and public
    snapshots; provider credentials never enter the database.
    """

    def __init__(self, engine: Engine, *, create_schema: bool = True) -> None:
        self.engine = engine
        self.metadata = MetaData()
        self.tasks = Table(
            "runtime_tasks", self.metadata,
            Column("task_id", String(255), primary_key=True),
            Column("room_id", String(255), nullable=False),
            Column("title", Text, nullable=False),
            Column("status", String(32), nullable=False),
            Column("row_version", Integer, nullable=False, default=1),
            Column("active_run_id", String(255)),
            Column("created_at", DateTime(timezone=True), nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
        )
        self.runs = Table(
            "runtime_runs", self.metadata,
            Column("run_id", String(255), primary_key=True),
            Column("task_id", String(255)),
            Column("room_id", String(255), nullable=False),
            Column("plan_revision", Integer, nullable=False),
            Column("status", String(32), nullable=False),
            Column("control_epoch", Integer, nullable=False, default=0),
            Column("row_version", Integer, nullable=False, default=1),
            Column("model_snapshot", JSON, nullable=False, default=list),
            Column("created_at", DateTime(timezone=True), nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
        )
        self.jobs = Table(
            "runtime_jobs", self.metadata,
            Column("job_id", String(255), primary_key=True),
            Column("run_id", String(255), nullable=False),
            Column("status", String(32), nullable=False),
            Column("payload", JSON, nullable=False, default=dict),
            Column("worker_id", String(255)),
            Column("lease_expires_at", DateTime(timezone=True)),
            Column("attempt_count", Integer, nullable=False, default=0),
            Column("error_code", String(128)),
            Column("created_at", DateTime(timezone=True), nullable=False),
            Column("updated_at", DateTime(timezone=True), nullable=False),
        )
        self.commands = Table(
            "runtime_commands", self.metadata,
            Column("command_id", String(255), primary_key=True),
            Column("run_id", String(255), nullable=False),
            Column("action", String(32), nullable=False),
            Column("result", JSON, nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False),
        )
        if create_schema and engine.dialect.name == "sqlite":
            self.metadata.create_all(engine)

    def ensure_schema(self) -> None:
        self.metadata.create_all(self.engine)

    def upsert_task(self, task_id: str, room_id: str, title: str, *, status: str = "active", row_version: int = 1, active_run_id: str | None = None) -> dict[str, Any]:
        now = _now()
        with self.engine.begin() as conn:
            existing = conn.execute(select(self.tasks).where(self.tasks.c.task_id == task_id)).mappings().first()
            values = {"task_id": task_id, "room_id": room_id, "title": title, "status": status, "row_version": row_version, "active_run_id": active_run_id, "updated_at": now}
            if existing is None:
                conn.execute(insert(self.tasks).values(**values, created_at=now))
            else:
                conn.execute(update(self.tasks).where(self.tasks.c.task_id == task_id).values(**values))
        return self.get_task(task_id) or values

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(select(self.tasks).where(self.tasks.c.task_id == task_id)).mappings().first()
        return dict(row) if row else None

    def upsert_run(self, run_id: str, *, task_id: str | None, room_id: str, plan_revision: int, status: str, control_epoch: int = 0, row_version: int = 1, model_snapshot: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        now = _now()
        with self.engine.begin() as conn:
            existing = conn.execute(select(self.runs).where(self.runs.c.run_id == run_id)).mappings().first()
            values = {"run_id": run_id, "task_id": task_id, "room_id": room_id, "plan_revision": plan_revision, "status": status, "control_epoch": control_epoch, "row_version": row_version, "model_snapshot": model_snapshot or [], "updated_at": now}
            if existing is None:
                conn.execute(insert(self.runs).values(**values, created_at=now))
            else:
                conn.execute(update(self.runs).where(self.runs.c.run_id == run_id).values(**values))
        return self.get_run(run_id) or values

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(select(self.runs).where(self.runs.c.run_id == run_id)).mappings().first()
        return dict(row) if row else None

    def apply_control(self, command_id: str, run_id: str, action: str, *, expected_row_version: int, expected_control_epoch: int | None) -> dict[str, Any]:
        """Commit the command, run and task together before acknowledging it."""
        with self.engine.begin() as conn:
            prior = conn.execute(select(self.commands).where(self.commands.c.command_id == command_id)).mappings().first()
            if prior:
                if prior["run_id"] != run_id or prior["action"] != action:
                    raise ControlConflictError("command id is bound to another request")
                return dict(prior["result"])
            row = conn.execute(select(self.runs).where(self.runs.c.run_id == run_id).with_for_update()).mappings().first()
            if row is None:
                raise ControlError("unknown run")
            controller = RunController()
            controller.restore_run(RunControlState(**{key: row[key] for key in ("run_id", "plan_revision", "status", "control_epoch", "row_version")}))
            if action == "start":
                state = controller.start(run_id, expected_row_version=expected_row_version)
            elif action in {"pause", "cancel"} and expected_control_epoch is not None:
                state = getattr(controller, action)(run_id, expected_row_version=expected_row_version, expected_control_epoch=expected_control_epoch)
            else:
                raise ControlError("invalid control action or missing control epoch")
            changed = conn.execute(update(self.runs).where(self.runs.c.run_id == run_id,
                self.runs.c.row_version == row["row_version"], self.runs.c.control_epoch == row["control_epoch"])
                .values(status=state.status, row_version=state.row_version, control_epoch=state.control_epoch, updated_at=_now()))
            if changed.rowcount != 1:
                raise ControlConflictError("run changed while applying command")
            task_status = {"cancelled": "cancelled", "paused": "blocked", "running": "active"}[state.status]
            conn.execute(update(self.tasks).where(self.tasks.c.task_id == row["task_id"],
                or_(self.tasks.c.active_run_id == run_id, self.tasks.c.active_run_id.is_(None)))
                .values(status=task_status, active_run_id=run_id if state.status == "running" else None,
                    row_version=self.tasks.c.row_version + 1, updated_at=_now()))
            result = {"command_id": command_id, "status": "accepted", "run": asdict(state)}
            conn.execute(insert(self.commands).values(command_id=command_id, run_id=run_id, action=action, result=result, created_at=_now()))
            return result

    def finish_run(self, state: RunControlState) -> dict[str, Any]:
        """A late worker cannot undo a committed cancel/pause or another run."""
        with self.engine.begin() as conn:
            row = conn.execute(select(self.runs).where(self.runs.c.run_id == state.run_id).with_for_update()).mappings().one()
            if state.status in {"completed", "failed"} and row["status"] == "running":
                conn.execute(update(self.runs).where(self.runs.c.run_id == state.run_id,
                    self.runs.c.row_version == state.row_version - 1, self.runs.c.control_epoch == state.control_epoch,
                    self.runs.c.status == "running").values(status=state.status, row_version=state.row_version, updated_at=_now()))
            row = conn.execute(select(self.runs).where(self.runs.c.run_id == state.run_id)).mappings().one()
            task_status = {"completed": "completed", "failed": "blocked", "paused": "blocked", "cancelled": "cancelled"}.get(row["status"])
            if task_status:
                conn.execute(update(self.tasks).where(self.tasks.c.task_id == row["task_id"], self.tasks.c.active_run_id == state.run_id)
                    .values(status=task_status, active_run_id=None, row_version=self.tasks.c.row_version + 1, updated_at=_now()))
            return dict(row)

    def enqueue_job(self, job_id: str, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        now = _now()
        with self.engine.begin() as conn:
            conn.execute(insert(self.jobs).values(job_id=job_id, run_id=run_id, status="queued", payload=payload, attempt_count=0, created_at=now, updated_at=now))
        return self.get_job(job_id) or {}

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(select(self.jobs).where(self.jobs.c.job_id == job_id)).mappings().first()
        return dict(row) if row else None

    def update_job(self, job_id: str, *, status: str, worker_id: str | None = None, error_code: str | None = None, attempt_count: int | None = None) -> dict[str, Any] | None:
        values: dict[str, Any] = {"status": status, "updated_at": _now()}
        if worker_id is not None:
            values["worker_id"] = worker_id
        if error_code is not None:
            values["error_code"] = error_code
        if attempt_count is not None:
            values["attempt_count"] = attempt_count
        with self.engine.begin() as conn:
            conn.execute(update(self.jobs).where(self.jobs.c.job_id == job_id).values(**values))
        return self.get_job(job_id)

    def claim_job(self, worker_id: str, *, lease_seconds: int = 60) -> dict[str, Any] | None:
        """Atomically claim one queued or expired job.

        PostgreSQL uses row locking with SKIP LOCKED; SQLite relies on its
        write transaction. The returned lease token is the attempt count and
        must be supplied to complete/fail, preventing stale workers from
        overwriting a newer attempt.
        """
        if not worker_id.strip() or lease_seconds < 1:
            raise ValueError("worker_id and positive lease_seconds are required")
        now = _now(); expiry = now + timedelta(seconds=lease_seconds)
        with self.engine.begin() as conn:
            predicate = and_(
                self.jobs.c.status.in_(["queued", "running"]),
                or_(self.jobs.c.status == "queued", self.jobs.c.lease_expires_at.is_(None), self.jobs.c.lease_expires_at < now),
            )
            stmt = select(self.jobs).where(predicate).order_by(self.jobs.c.created_at).limit(1)
            if conn.dialect.name == "postgresql":
                stmt = stmt.with_for_update(skip_locked=True)
            row = conn.execute(stmt).mappings().first()
            if row is None:
                return None
            attempt = int(row["attempt_count"] or 0) + 1
            conn.execute(update(self.jobs).where(self.jobs.c.job_id == row["job_id"]).values(status="running", worker_id=worker_id, lease_expires_at=expiry, attempt_count=attempt, updated_at=now))
            updated = conn.execute(select(self.jobs).where(self.jobs.c.job_id == row["job_id"])).mappings().one()
            return dict(updated)

    def finish_job(self, job_id: str, *, worker_id: str, attempt_count: int, status: str = "completed", error_code: str | None = None) -> dict[str, Any] | None:
        if status not in {"completed", "failed"}:
            raise ValueError("status must be completed or failed")
        values: dict[str, Any] = {"status": status, "lease_expires_at": None, "updated_at": _now()}
        if error_code is not None:
            values["error_code"] = error_code
        with self.engine.begin() as conn:
            result = conn.execute(update(self.jobs).where(and_(self.jobs.c.job_id == job_id, self.jobs.c.worker_id == worker_id, self.jobs.c.attempt_count == attempt_count, self.jobs.c.status == "running")).values(**values))
            if result.rowcount != 1:
                raise RuntimeError("job lease lost or fenced")
        return self.get_job(job_id)

    def list_jobs(self, *, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        stmt = select(self.jobs).order_by(self.jobs.c.created_at).limit(limit)
        if status:
            stmt = stmt.where(self.jobs.c.status == status)
        with self.engine.connect() as conn:
            return [dict(row) for row in conn.execute(stmt).mappings().all()]
