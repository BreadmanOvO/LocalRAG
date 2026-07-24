from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Sequence
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from agent.memory import TaskMemoryStore
from agent.research.models import (
    FindingStatus,
    ResearchExecutionIdentity,
    ResearchFinding,
    ResearchPlanSnapshot,
    ResearchRun,
    ResearchStep,
    ResearchStepCommit,
    ResearchStepDraft,
    ResearchStepTransition,
    RunStatus,
)
from agent.research.records import (
    evidence_from_row,
    finding_from_row,
    run_from_row,
    step_from_row,
)
from agent.research.schema import apply_research_migration
from agent.research.validation import (
    FINDING_STATUSES,
    FINDING_TRANSITIONS,
    RUN_STATUSES,
    RUN_TRANSITIONS,
    STEP_STATUSES,
    STEP_TRANSITIONS,
    clean_identifier,
    clean_text,
    new_id,
    normalize_evidence_draft,
    normalize_execution_identity,
    normalize_finding_draft,
    normalize_step_draft,
    step_commit_fingerprint,
    validate_counter,
    validate_revision,
    validate_status,
)
from utils.path_tools import get_abs_path
from utils.session import validate_task_id


class ResearchNotFoundError(LookupError):
    pass


class ResearchStateError(ValueError):
    pass


class ResearchRevisionConflictError(RuntimeError):
    def __init__(self, run_id: str, expected: int, actual: int) -> None:
        self.run_id = run_id
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Research run revision conflict for {run_id}: expected {expected}, actual {actual}"
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ResearchRunStore:
    """Persist research plans and enforce their state transitions."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        default_path = Path(get_abs_path("agent_memory/task_memory.sqlite3"))
        self.db_path = Path(db_path).resolve() if db_path is not None else default_path.resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._task_store = TaskMemoryStore(self.db_path)
        self._initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            apply_research_migration(connection, _utc_now())

    def create_plan(
        self,
        task_id: str,
        goal: str,
        steps: Sequence[ResearchStepDraft],
        *,
        run_id: str | None = None,
        identity: ResearchExecutionIdentity | None = None,
    ) -> ResearchPlanSnapshot:
        task_id = validate_task_id(task_id)
        goal = clean_text(goal, "goal")
        if not goal:
            raise ValueError("goal must not be empty")
        normalized_steps = tuple(normalize_step_draft(step) for step in steps)
        if not normalized_steps:
            raise ValueError("steps must not be empty")
        run_id = clean_identifier(run_id or new_id("run"), "run_id")
        normalized_identity = (
            normalize_execution_identity(identity) if identity is not None else None
        )
        now = _utc_now()

        self._task_store.ensure_task(task_id)
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO research_runs(
                    run_id, task_id, goal, status, current_step_id,
                    plan_revision, revision, created_at, updated_at
                )
                VALUES (?, ?, ?, 'planned', NULL, 1, 0, ?, ?)
                """,
                (run_id, task_id, goal, now, now),
            )
            if normalized_identity is not None:
                connection.execute(
                    """
                    INSERT INTO research_run_identities(
                        run_id, corpus_fingerprint, registry_fingerprint,
                        code_revision, code_dirty, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        normalized_identity.corpus_fingerprint,
                        normalized_identity.registry_fingerprint,
                        normalized_identity.code_revision,
                        int(normalized_identity.code_dirty),
                        now,
                    ),
                )
            for position, (draft, arguments_json) in enumerate(normalized_steps, start=1):
                connection.execute(
                    """
                    INSERT INTO research_steps(
                        step_id, run_id, position, objective, action, arguments_json,
                        status, attempt_count, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 'pending', 0, ?, ?)
                    """,
                    (
                        new_id("step"),
                        run_id,
                        position,
                        draft.objective,
                        draft.action,
                        arguments_json,
                        now,
                        now,
                    ),
                )
        return self.get_plan(run_id)

    def get_run(self, run_id: str) -> ResearchRun:
        run_id = clean_identifier(run_id, "run_id")
        with self._lock, self._connect() as connection:
            return run_from_row(self._require_run(connection, run_id))

    def get_identity(self, run_id: str) -> ResearchExecutionIdentity | None:
        run_id = clean_identifier(run_id, "run_id")
        with self._lock, self._connect() as connection:
            self._require_run(connection, run_id)
            row = connection.execute(
                "SELECT * FROM research_run_identities WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return ResearchExecutionIdentity(
            corpus_fingerprint=row["corpus_fingerprint"],
            registry_fingerprint=row["registry_fingerprint"],
            code_revision=row["code_revision"],
            code_dirty=bool(row["code_dirty"]),
        )

    def get_plan(self, run_id: str) -> ResearchPlanSnapshot:
        run_id = clean_identifier(run_id, "run_id")
        with self._lock, self._connect() as connection:
            run = run_from_row(self._require_run(connection, run_id))
            step_rows = connection.execute(
                "SELECT * FROM research_steps WHERE run_id = ? ORDER BY position",
                (run_id,),
            ).fetchall()
            evidence_rows = connection.execute(
                "SELECT * FROM research_evidence_refs WHERE run_id = ? ORDER BY created_at, evidence_id",
                (run_id,),
            ).fetchall()
            finding_rows = connection.execute(
                "SELECT * FROM research_findings WHERE run_id = ? ORDER BY created_at, finding_id",
                (run_id,),
            ).fetchall()
            binding_rows = connection.execute(
                """
                SELECT finding_id, evidence_id
                FROM research_finding_evidence
                WHERE run_id = ?
                ORDER BY finding_id, evidence_id
                """,
                (run_id,),
            ).fetchall()

        step_evidence: dict[str, list[str]] = {}
        for row in evidence_rows:
            step_evidence.setdefault(row["step_id"], []).append(row["evidence_id"])
        finding_evidence: dict[str, list[str]] = {}
        for row in binding_rows:
            finding_evidence.setdefault(row["finding_id"], []).append(row["evidence_id"])

        return ResearchPlanSnapshot(
            run=run,
            steps=tuple(
                step_from_row(row, tuple(step_evidence.get(row["step_id"], ())))
                for row in step_rows
            ),
            evidence_refs=tuple(evidence_from_row(row) for row in evidence_rows),
            findings=tuple(
                finding_from_row(
                    row,
                    tuple(finding_evidence.get(row["finding_id"], ())),
                )
                for row in finding_rows
            ),
        )

    def get_latest_plan_for_task(self, task_id: str) -> ResearchPlanSnapshot | None:
        task_id = validate_task_id(task_id)
        with self._lock, self._connect() as connection:
            row = connection.execute(
                """
                SELECT run_id FROM research_runs
                WHERE task_id = ?
                ORDER BY updated_at DESC, created_at DESC, run_id DESC
                LIMIT 1
                """,
                (task_id,),
            ).fetchone()
        return self.get_plan(row["run_id"]) if row is not None else None

    def get_next_pending_step(self, run_id: str) -> ResearchStep | None:
        run_id = clean_identifier(run_id, "run_id")
        with self._lock, self._connect() as connection:
            self._require_run(connection, run_id)
            row = connection.execute(
                """
                SELECT * FROM research_steps
                WHERE run_id = ? AND status = 'pending'
                ORDER BY position
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
        return step_from_row(row, ()) if row is not None else None

    def start_next_step(
        self,
        run_id: str,
        *,
        expected_revision: int,
    ) -> tuple[ResearchRun, ResearchStep] | None:
        run_id = clean_identifier(run_id, "run_id")
        expected_revision = validate_revision(expected_revision)
        now = _utc_now()

        with self._lock, self._connect() as connection:
            run_row = self._require_run(connection, run_id)
            self._require_expected_revision(run_row, expected_revision)
            if run_row["status"] not in {"planned", "running"}:
                raise ResearchStateError(
                    f"cannot start a step while run is {run_row['status']}"
                )
            active = connection.execute(
                "SELECT step_id FROM research_steps WHERE run_id = ? AND status = 'running'",
                (run_id,),
            ).fetchone()
            if active is not None:
                raise ResearchStateError(f"step {active['step_id']} is already running")
            step_row = connection.execute(
                """
                SELECT * FROM research_steps
                WHERE run_id = ? AND status = 'pending'
                ORDER BY position
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
            if step_row is None:
                return None

            self._claim_revision(connection, run_id, expected_revision, now)
            connection.execute(
                """
                UPDATE research_steps
                SET status = 'running', attempt_count = attempt_count + 1, updated_at = ?
                WHERE step_id = ?
                """,
                (now, step_row["step_id"]),
            )
            connection.execute(
                """
                UPDATE research_runs
                SET status = 'running', current_step_id = ?, stop_reason = ''
                WHERE run_id = ?
                """,
                (step_row["step_id"], run_id),
            )
            run = run_from_row(self._require_run(connection, run_id))
            updated_step = connection.execute(
                "SELECT * FROM research_steps WHERE step_id = ?",
                (step_row["step_id"],),
            ).fetchone()
        return run, step_from_row(updated_step, ())

    def transition_run(
        self,
        run_id: str,
        status: RunStatus,
        *,
        expected_revision: int,
        stop_reason: str = "",
    ) -> ResearchRun:
        run_id = clean_identifier(run_id, "run_id")
        status = validate_status(status, RUN_STATUSES, "run status")
        expected_revision = validate_revision(expected_revision)
        stop_reason = clean_text(stop_reason, "stop_reason")
        now = _utc_now()

        with self._lock, self._connect() as connection:
            run_row = self._require_run(connection, run_id)
            self._require_expected_revision(run_row, expected_revision)
            current_status = run_row["status"]
            if status not in RUN_TRANSITIONS[current_status]:
                raise ResearchStateError(
                    f"invalid research run transition: {current_status} -> {status}"
                )
            if status == "completed":
                incomplete = connection.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM research_steps
                    WHERE run_id = ? AND status NOT IN ('completed', 'skipped')
                    """,
                    (run_id,),
                ).fetchone()["count"]
                if incomplete:
                    raise ResearchStateError("cannot complete a run with unfinished steps")

            self._claim_revision(connection, run_id, expected_revision, now)
            if status in {"blocked", "cancelled", "failed"}:
                step_status = "failed" if status == "failed" else "blocked"
                error_code = "research_cancelled" if status == "cancelled" else stop_reason
                connection.execute(
                    """
                    UPDATE research_steps
                    SET status = ?, error_code = ?, updated_at = ?
                    WHERE run_id = ? AND status = 'running'
                    """,
                    (step_status, error_code, now, run_id),
                )
            current_step_id = (
                run_row["current_step_id"] if status == "running" else None
            )
            connection.execute(
                """
                UPDATE research_runs
                SET status = ?, current_step_id = ?, stop_reason = ?
                WHERE run_id = ?
                """,
                (status, current_step_id, stop_reason, run_id),
            )
            return run_from_row(self._require_run(connection, run_id))

    def prepare_resume(
        self,
        run_id: str,
        *,
        expected_revision: int,
    ) -> ResearchPlanSnapshot:
        run_id = clean_identifier(run_id, "run_id")
        expected_revision = validate_revision(expected_revision)
        now = _utc_now()

        with self._lock, self._connect() as connection:
            run_row = self._require_run(connection, run_id)
            self._require_expected_revision(run_row, expected_revision)
            status = run_row["status"]
            if status not in {"planned", "running", "blocked"}:
                raise ResearchStateError(f"cannot resume a run while it is {status}")

            interrupted_step = connection.execute(
                """
                SELECT step_id FROM research_steps
                WHERE run_id = ? AND status = 'running'
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
            needs_recovery = status == "blocked" or interrupted_step is not None
            if needs_recovery:
                self._claim_revision(connection, run_id, expected_revision, now)
                connection.execute(
                    """
                    UPDATE research_steps
                    SET status = 'pending', error_code = '', updated_at = ?
                    WHERE run_id = ? AND status IN ('running', 'blocked')
                    """,
                    (now, run_id),
                )
                connection.execute(
                    """
                    UPDATE research_runs
                    SET status = 'running', current_step_id = NULL, stop_reason = ''
                    WHERE run_id = ?
                    """,
                    (run_id,),
                )
        return self.get_plan(run_id)

    def transition_step(
        self,
        run_id: str,
        step_id: str,
        transition: ResearchStepTransition,
        *,
        expected_revision: int,
    ) -> ResearchPlanSnapshot:
        if not isinstance(transition, ResearchStepTransition):
            raise TypeError("transition must be a ResearchStepTransition")
        run_id = clean_identifier(run_id, "run_id")
        step_id = clean_identifier(step_id, "step_id")
        status = validate_status(transition.status, STEP_STATUSES, "step status")
        expected_revision = validate_revision(expected_revision)
        result_summary = clean_text(transition.result_summary, "result_summary")
        error_code = clean_text(transition.error_code, "error_code", max_length=256)
        tool_call_count = validate_counter(
            transition.tool_call_count,
            "tool_call_count",
        )
        model_call_count = validate_counter(
            transition.model_call_count,
            "model_call_count",
        )
        if status == "completed":
            raise ResearchStateError("use commit_step to complete a research step")
        now = _utc_now()

        with self._lock, self._connect() as connection:
            run_row = self._require_run(connection, run_id)
            self._require_expected_revision(run_row, expected_revision)
            step_row = self._require_step(connection, run_id, step_id)
            current_status = step_row["status"]
            if status not in STEP_TRANSITIONS[current_status]:
                raise ResearchStateError(
                    f"invalid research step transition: {current_status} -> {status}"
                )
            if run_row["status"] not in {"planned", "running"}:
                raise ResearchStateError(
                    f"cannot transition a step while run is {run_row['status']}"
                )
            if status == "running":
                active = connection.execute(
                    """
                    SELECT step_id FROM research_steps
                    WHERE run_id = ? AND status = 'running' AND step_id != ?
                    """,
                    (run_id, step_id),
                ).fetchone()
                if active is not None:
                    raise ResearchStateError(f"step {active['step_id']} is already running")

            self._claim_revision(connection, run_id, expected_revision, now)
            attempt_increment = 1 if status == "running" else 0
            connection.execute(
                """
                UPDATE research_steps
                SET status = ?, attempt_count = attempt_count + ?,
                    result_summary = ?, error_code = ?, updated_at = ?
                WHERE step_id = ?
                """,
                (
                    status,
                    attempt_increment,
                    result_summary,
                    error_code,
                    now,
                    step_id,
                ),
            )
            connection.execute(
                """
                UPDATE research_runs
                SET tool_call_count = tool_call_count + ?,
                    model_call_count = model_call_count + ?
                WHERE run_id = ?
                """,
                (tool_call_count, model_call_count, run_id),
            )
            if status == "running":
                connection.execute(
                    """
                    UPDATE research_runs
                    SET status = 'running', current_step_id = ?, stop_reason = ''
                    WHERE run_id = ?
                    """,
                    (step_id, run_id),
                )
            elif status in {"blocked", "failed"}:
                run_status = "blocked" if status == "blocked" else "failed"
                connection.execute(
                    """
                    UPDATE research_runs
                    SET status = ?, current_step_id = NULL, stop_reason = ?
                    WHERE run_id = ?
                    """,
                    (run_status, error_code or result_summary, run_id),
                )
        return self.get_plan(run_id)

    def commit_step(
        self,
        run_id: str,
        step_id: str,
        commit: ResearchStepCommit,
        *,
        expected_revision: int,
    ) -> ResearchPlanSnapshot:
        if not isinstance(commit, ResearchStepCommit):
            raise TypeError("commit must be a ResearchStepCommit")
        run_id = clean_identifier(run_id, "run_id")
        step_id = clean_identifier(step_id, "step_id")
        expected_revision = validate_revision(expected_revision)
        result_summary = clean_text(commit.result_summary, "result_summary")
        commit_id = (
            clean_identifier(commit.commit_id, "commit_id")
            if commit.commit_id is not None
            else None
        )
        payload_fingerprint = step_commit_fingerprint(commit)
        tool_call_count = validate_counter(commit.tool_call_count, "tool_call_count")
        model_call_count = validate_counter(commit.model_call_count, "model_call_count")
        normalized_evidence = tuple(
            normalize_evidence_draft(draft) for draft in commit.evidence_refs
        )
        normalized_findings = tuple(
            normalize_finding_draft(draft) for draft in commit.findings
        )
        supplied_evidence_ids = {item[0] for item in normalized_evidence}
        if len(supplied_evidence_ids) != len(normalized_evidence):
            raise ValueError("evidence_id values must be unique")
        finding_ids = {item[0] for item in normalized_findings}
        if len(finding_ids) != len(normalized_findings):
            raise ValueError("finding_id values must be unique")
        now = _utc_now()

        with self._lock, self._connect() as connection:
            run_row = self._require_run(connection, run_id)
            step_row = self._require_step(connection, run_id, step_id)
            already_committed = self._is_step_commit_replay(
                connection,
                run_id,
                step_id,
                step_row["status"],
                (commit_id, payload_fingerprint),
            )

            if not already_committed:
                self._require_expected_revision(run_row, expected_revision)
                if run_row["status"] != "running" or step_row["status"] != "running":
                    raise ResearchStateError("only a running step can be committed")
                persisted_commit_id = commit_id or new_id("commit")
                self._require_unused_commit_id(
                    connection,
                    run_id,
                    persisted_commit_id,
                )

                self._claim_revision(connection, run_id, expected_revision, now)
                for evidence_id, draft in normalized_evidence:
                    connection.execute(
                        """
                        INSERT INTO research_evidence_refs(
                            evidence_id, run_id, step_id, source_id, locator,
                            chunk_order, chunk_strategy, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            evidence_id,
                            run_id,
                            step_id,
                            draft.source_id,
                            draft.locator,
                            draft.chunk_order,
                            draft.chunk_strategy,
                            now,
                        ),
                    )

                for finding_id, draft in normalized_findings:
                    self._require_evidence_ids(
                        connection,
                        run_id,
                        draft.evidence_ids,
                        required=draft.status == "verified",
                    )
                    primary_evidence_id = (
                        draft.evidence_ids[0] if draft.status == "verified" else None
                    )
                    connection.execute(
                        """
                        INSERT INTO research_findings(
                            finding_id, run_id, text, status, primary_evidence_id,
                            created_by_step_id, created_at, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            finding_id,
                            run_id,
                            draft.text,
                            draft.status,
                            primary_evidence_id,
                            step_id,
                            now,
                            now,
                        ),
                    )
                    connection.executemany(
                        """
                        INSERT INTO research_finding_evidence(
                            run_id, finding_id, evidence_id
                        )
                        VALUES (?, ?, ?)
                        """,
                        (
                            (run_id, finding_id, evidence_id)
                            for evidence_id in draft.evidence_ids
                        ),
                    )

                connection.execute(
                    """
                    UPDATE research_steps
                    SET status = 'completed', result_summary = ?,
                        error_code = '', updated_at = ?
                    WHERE step_id = ?
                    """,
                    (result_summary, now, step_id),
                )
                connection.execute(
                    """
                    UPDATE research_runs
                    SET current_step_id = NULL, no_progress_count = 0, stop_reason = '',
                        tool_call_count = tool_call_count + ?,
                        model_call_count = model_call_count + ?
                    WHERE run_id = ?
                    """,
                    (tool_call_count, model_call_count, run_id),
                )
                connection.execute(
                    """
                    INSERT INTO research_step_commits(
                        run_id, step_id, commit_id, payload_fingerprint,
                        committed_revision, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        step_id,
                        persisted_commit_id,
                        payload_fingerprint,
                        expected_revision + 1,
                        now,
                    ),
                )
        return self.get_plan(run_id)

    def transition_finding(
        self,
        run_id: str,
        finding_id: str,
        status: FindingStatus,
        *,
        expected_revision: int,
        evidence_ids: Iterable[str] | None = None,
    ) -> ResearchFinding:
        run_id = clean_identifier(run_id, "run_id")
        finding_id = clean_identifier(finding_id, "finding_id")
        status = validate_status(status, FINDING_STATUSES, "finding status")
        expected_revision = validate_revision(expected_revision)
        normalized_evidence_ids = (
            None
            if evidence_ids is None
            else tuple(clean_identifier(item, "evidence_id") for item in evidence_ids)
        )
        now = _utc_now()

        with self._lock, self._connect() as connection:
            run_row = self._require_run(connection, run_id)
            self._require_expected_revision(run_row, expected_revision)
            finding_row = connection.execute(
                "SELECT * FROM research_findings WHERE run_id = ? AND finding_id = ?",
                (run_id, finding_id),
            ).fetchone()
            if finding_row is None:
                raise ResearchNotFoundError(f"research finding not found: {finding_id}")
            current_status = finding_row["status"]
            if status not in FINDING_TRANSITIONS[current_status]:
                raise ResearchStateError(
                    f"invalid research finding transition: {current_status} -> {status}"
                )
            if normalized_evidence_ids is None:
                normalized_evidence_ids = tuple(
                    row["evidence_id"]
                    for row in connection.execute(
                        """
                        SELECT evidence_id FROM research_finding_evidence
                        WHERE run_id = ? AND finding_id = ?
                        ORDER BY evidence_id
                        """,
                        (run_id, finding_id),
                    ).fetchall()
                )
            self._require_evidence_ids(
                connection,
                run_id,
                normalized_evidence_ids,
                required=status == "verified",
            )

            self._claim_revision(connection, run_id, expected_revision, now)
            connection.execute(
                "DELETE FROM research_finding_evidence WHERE finding_id = ?",
                (finding_id,),
            )
            connection.executemany(
                """
                INSERT INTO research_finding_evidence(run_id, finding_id, evidence_id)
                VALUES (?, ?, ?)
                """,
                (
                    (run_id, finding_id, evidence_id)
                    for evidence_id in normalized_evidence_ids
                ),
            )
            primary_evidence_id = (
                normalized_evidence_ids[0] if status == "verified" else None
            )
            connection.execute(
                """
                UPDATE research_findings
                SET status = ?, primary_evidence_id = ?, updated_at = ?
                WHERE finding_id = ?
                """,
                (status, primary_evidence_id, now, finding_id),
            )
            row = connection.execute(
                "SELECT * FROM research_findings WHERE finding_id = ?",
                (finding_id,),
            ).fetchone()
        return finding_from_row(row, normalized_evidence_ids)

    @staticmethod
    def _require_run(connection: sqlite3.Connection, run_id: str) -> sqlite3.Row:
        row = connection.execute(
            "SELECT * FROM research_runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            raise ResearchNotFoundError(f"research run not found: {run_id}")
        return row

    @staticmethod
    def _require_step(
        connection: sqlite3.Connection,
        run_id: str,
        step_id: str,
    ) -> sqlite3.Row:
        row = connection.execute(
            "SELECT * FROM research_steps WHERE run_id = ? AND step_id = ?",
            (run_id, step_id),
        ).fetchone()
        if row is None:
            raise ResearchNotFoundError(f"research step not found: {step_id}")
        return row

    @staticmethod
    def _require_expected_revision(row: sqlite3.Row, expected_revision: int) -> None:
        actual = int(row["revision"])
        if actual != expected_revision:
            raise ResearchRevisionConflictError(row["run_id"], expected_revision, actual)

    @staticmethod
    def _claim_revision(
        connection: sqlite3.Connection,
        run_id: str,
        expected_revision: int,
        updated_at: str,
    ) -> None:
        cursor = connection.execute(
            """
            UPDATE research_runs
            SET revision = revision + 1, updated_at = ?
            WHERE run_id = ? AND revision = ?
            """,
            (updated_at, run_id, expected_revision),
        )
        if cursor.rowcount:
            return
        row = ResearchRunStore._require_run(connection, run_id)
        raise ResearchRevisionConflictError(
            run_id,
            expected_revision,
            int(row["revision"]),
        )

    @staticmethod
    def _require_evidence_ids(
        connection: sqlite3.Connection,
        run_id: str,
        evidence_ids: Sequence[str],
        *,
        required: bool,
    ) -> None:
        if required and not evidence_ids:
            raise ValueError("verified findings require at least one evidence_id")
        if not evidence_ids:
            return
        unique_ids = set(evidence_ids)
        if len(unique_ids) != len(evidence_ids):
            raise ValueError("finding evidence_ids must be unique")
        placeholders = ",".join("?" for _ in unique_ids)
        rows = connection.execute(
            f"""
            SELECT evidence_id FROM research_evidence_refs
            WHERE run_id = ? AND evidence_id IN ({placeholders})
            """,
            (run_id, *unique_ids),
        ).fetchall()
        found = {row["evidence_id"] for row in rows}
        missing = unique_ids - found
        if missing:
            raise ValueError(f"unknown evidence_ids for run {run_id}: {sorted(missing)}")

    @staticmethod
    def _is_step_commit_replay(
        connection: sqlite3.Connection,
        run_id: str,
        step_id: str,
        step_status: str,
        commit_identity: tuple[str | None, str],
    ) -> bool:
        commit_id, payload_fingerprint = commit_identity
        existing = connection.execute(
            """
            SELECT * FROM research_step_commits
            WHERE run_id = ? AND step_id = ?
            """,
            (run_id, step_id),
        ).fetchone()
        if existing is None:
            return step_status == "completed"
        if commit_id is None:
            return True
        if existing["commit_id"] != commit_id:
            raise ResearchStateError(
                f"research step {step_id} was committed with a different commit_id"
            )
        if existing["payload_fingerprint"] != payload_fingerprint:
            raise ResearchStateError(
                f"commit_id {commit_id} was reused with a different payload"
            )
        return True

    @staticmethod
    def _require_unused_commit_id(
        connection: sqlite3.Connection,
        run_id: str,
        commit_id: str,
    ) -> None:
        reused = connection.execute(
            """
            SELECT step_id FROM research_step_commits
            WHERE run_id = ? AND commit_id = ?
            """,
            (run_id, commit_id),
        ).fetchone()
        if reused is not None:
            raise ResearchStateError(
                f"commit_id {commit_id} already belongs to step {reused['step_id']}"
            )
