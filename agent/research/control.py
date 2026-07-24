from __future__ import annotations

import sqlite3
from collections.abc import Callable, Sequence
from typing import TypeVar

from agent.research.models import (
    ResearchExecutionIdentity,
    ResearchPlanSnapshot,
    ResearchRun,
    ResearchStep,
    ResearchStepCommit,
    ResearchStepDraft,
)
from agent.research.store import ResearchRunStore
from agent.research.validation import normalize_execution_identity


RESEARCH_PAUSED = "research_paused"
_T = TypeVar("_T")


class ResearchControlError(RuntimeError):
    def __init__(self, error_code: str, message: str) -> None:
        self.error_code = error_code
        super().__init__(message)


class ResearchRunService:
    """Coordinate recoverable research runs above the transactional store."""

    def __init__(self, store: ResearchRunStore) -> None:
        if not isinstance(store, ResearchRunStore):
            raise TypeError("store must be a ResearchRunStore")
        self.store = store

    def create_plan(
        self,
        task_id: str,
        goal: str,
        steps: Sequence[ResearchStepDraft],
        *,
        identity: ResearchExecutionIdentity,
        run_id: str | None = None,
    ) -> ResearchPlanSnapshot:
        identity = self._require_stable_identity(identity)
        return self._storage_call(
            lambda: self.store.create_plan(
                task_id,
                goal,
                steps,
                run_id=run_id,
                identity=identity,
            )
        )

    def pause_run(self, run_id: str, *, expected_revision: int) -> ResearchRun:
        run = self._storage_call(lambda: self.store.get_run(run_id))
        if run.status == "blocked" and run.stop_reason == RESEARCH_PAUSED:
            return run
        if run.status not in {"planned", "running"}:
            raise ResearchControlError(
                "research_not_pausable",
                f"cannot pause a run while it is {run.status}",
            )
        return self._storage_call(
            lambda: self.store.transition_run(
                run_id,
                "blocked",
                expected_revision=expected_revision,
                stop_reason=RESEARCH_PAUSED,
            )
        )

    def resume_run(
        self,
        run_id: str,
        *,
        expected_revision: int,
        current_identity: ResearchExecutionIdentity,
    ) -> ResearchPlanSnapshot:
        current_identity = self._require_stable_identity(current_identity)
        stored_identity = self._storage_call(lambda: self.store.get_identity(run_id))
        if stored_identity is None:
            raise ResearchControlError(
                "research_identity_unavailable",
                "research run has no persisted execution identity",
            )
        if stored_identity != current_identity:
            raise ResearchControlError(
                "research_identity_mismatch",
                "current corpus or code identity does not match the research checkpoint",
            )
        run = self._storage_call(lambda: self.store.get_run(run_id))
        if run.status not in {"planned", "running", "blocked"}:
            raise ResearchControlError(
                "research_not_resumable",
                f"cannot resume a run while it is {run.status}",
            )
        return self._storage_call(
            lambda: self.store.prepare_resume(
                run_id,
                expected_revision=expected_revision,
            )
        )

    def cancel_run(self, run_id: str, *, expected_revision: int) -> ResearchRun:
        run = self._storage_call(lambda: self.store.get_run(run_id))
        if run.status == "cancelled":
            return run
        if run.status not in {"planned", "running", "blocked"}:
            raise ResearchControlError(
                "research_not_cancellable",
                f"cannot cancel a run while it is {run.status}",
            )
        return self._storage_call(
            lambda: self.store.transition_run(
                run_id,
                "cancelled",
                expected_revision=expected_revision,
                stop_reason="research_cancelled",
            )
        )

    def claim_next_step(
        self,
        run_id: str,
        *,
        expected_revision: int,
    ) -> tuple[ResearchRun, ResearchStep] | None:
        run = self._storage_call(lambda: self.store.get_run(run_id))
        if run.status not in {"planned", "running"}:
            raise ResearchControlError(
                "research_not_runnable",
                f"cannot claim work while run is {run.status}",
            )
        return self._storage_call(
            lambda: self.store.start_next_step(
                run_id,
                expected_revision=expected_revision,
            )
        )

    def ensure_step_active(self, run_id: str, step_id: str) -> ResearchRun:
        run = self._storage_call(lambda: self.store.get_run(run_id))
        if run.status == "running" and run.current_step_id == step_id:
            return run
        error_code = run.stop_reason or "research_execution_stopped"
        raise ResearchControlError(
            error_code,
            f"research step {step_id} is no longer active",
        )

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
        if commit.commit_id is None:
            raise ResearchControlError(
                "research_commit_id_required",
                "recoverable step commits require a stable commit_id",
            )
        return self._storage_call(
            lambda: self.store.commit_step(
                run_id,
                step_id,
                commit,
                expected_revision=expected_revision,
            )
        )

    @staticmethod
    def _require_stable_identity(
        identity: ResearchExecutionIdentity,
    ) -> ResearchExecutionIdentity:
        identity = normalize_execution_identity(identity)
        if identity.code_dirty:
            raise ResearchControlError(
                "research_identity_unstable",
                "recoverable research runs require a clean code identity",
            )
        return identity

    @staticmethod
    def _storage_call(operation: Callable[[], _T]) -> _T:
        try:
            return operation()
        except (sqlite3.Error, OSError) as exc:
            raise ResearchControlError(
                "research_storage_failed",
                "research checkpoint storage is unavailable",
            ) from exc
