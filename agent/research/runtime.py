from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agent.observability import AgentEvent
from agent.research.control import ResearchControlError, ResearchRunService
from agent.research.models import (
    EvidenceRefDraft,
    ResearchExecutionIdentity,
    ResearchFindingDraft,
    ResearchPlanSnapshot,
    ResearchStepCommit,
    ResearchStepDraft,
    ResearchStepTransition,
)
from agent.research.store import (
    ResearchRevisionConflictError,
    ResearchStateError,
)


TERMINAL_RUN_STATUSES = frozenset({"completed", "cancelled", "failed"})
_MAX_CHECKPOINT_TEXT = 4000


def execution_identity_from_observability(
    runtime_status: dict[str, Any],
) -> ResearchExecutionIdentity:
    corpus = runtime_status.get("current_corpus") or {}
    revision = str(runtime_status.get("current_git_revision") or "")
    dirty = runtime_status.get("current_git_dirty")
    corpus_fingerprint = str(corpus.get("corpus_fingerprint") or "")
    registry_fingerprint = str(corpus.get("registry_fingerprint") or "")
    if (
        not corpus.get("available")
        or not isinstance(dirty, bool)
        or not corpus_fingerprint
        or not registry_fingerprint
        or not revision
    ):
        raise ResearchControlError(
            "research_identity_unavailable",
            "current corpus or code identity is unavailable",
        )
    return ResearchExecutionIdentity(
        corpus_fingerprint=corpus_fingerprint,
        registry_fingerprint=registry_fingerprint,
        code_revision=revision,
        code_dirty=dirty,
    )


@dataclass
class _AttemptState:
    answer_parts: list[str] = field(default_factory=list)
    observations: list[dict[str, Any]] = field(default_factory=list)
    tool_call_count: int = 0
    model_call_count: int = 0
    retrieval_completed: bool = False
    error_code: str = ""

    def record(self, event: AgentEvent) -> None:
        if event.kind == "model_completed":
            self.model_call_count += 1
        elif event.kind == "tool_started":
            self.tool_call_count += 1
        elif event.kind == "tool_completed":
            self.observations.extend(event.observations)
            if event.tool_name == "rag_search" and event.status not in {
                "error",
                "failed",
            }:
                self.retrieval_completed = True
        elif event.kind == "answer_delta":
            self.answer_parts.append(event.content)
        elif event.kind == "error":
            self.error_code = event.error_code or "agent_execution_failed"

    @property
    def answer(self) -> str:
        return "".join(self.answer_parts).strip()


class ResearchAgentRuntime:
    """Run one existing ReactAgent turn behind a recoverable research step."""

    def __init__(
        self,
        agent,
        service: ResearchRunService,
        identity: ResearchExecutionIdentity,
    ) -> None:
        self.agent = agent
        self.service = service
        self.identity = identity
        self.task_id = agent.task_id

    def get_latest_plan(self) -> ResearchPlanSnapshot | None:
        return self.service.get_latest_plan(self.task_id)

    def create_run(self, goal: str) -> ResearchPlanSnapshot:
        latest = self.get_latest_plan()
        if latest is not None and latest.run.status not in TERMINAL_RUN_STATUSES:
            if latest.run.goal == goal.strip():
                return latest
            raise ResearchControlError(
                "research_run_active",
                "finish or cancel the current research run before starting another",
            )
        return self.service.create_plan(
            self.task_id,
            goal,
            (
                ResearchStepDraft(
                    objective=goal,
                    action="react_agent",
                    arguments={"query": goal},
                ),
            ),
            identity=self.identity,
        )

    def execute_events(self, run_id: str):
        try:
            plan = self._prepare_run(run_id)
            claimed = self.service.claim_next_step(
                run_id,
                expected_revision=plan.run.revision,
            )
            if claimed is None:
                self._complete_if_finished(plan)
                return
            started_run, step = claimed
            query = str(step.arguments.get("query") or plan.run.goal)
            attempt = _AttemptState()
            events = iter(self.agent.execute_events(query))
            while True:
                self.service.ensure_step_active(
                    run_id,
                    step.step_id,
                    expected_revision=started_run.revision,
                )
                try:
                    event = next(events)
                except StopIteration:
                    break
                attempt.record(event)
                yield event
        except (ResearchControlError, ResearchRevisionConflictError, ResearchStateError) as exc:
            error_code = getattr(exc, "error_code", "research_execution_stopped")
            yield self._control_error_event(error_code)
            return

        error_code = attempt.error_code
        if not error_code and not attempt.answer:
            error_code = "empty_agent_answer"
            yield self._control_error_event(error_code)
        try:
            if error_code:
                self.service.transition_step(
                    run_id,
                    step.step_id,
                    ResearchStepTransition(
                        "blocked",
                        result_summary=attempt.answer,
                        error_code=error_code,
                        tool_call_count=attempt.tool_call_count,
                        model_call_count=attempt.model_call_count,
                    ),
                    expected_revision=started_run.revision,
                )
                return
            evidence = self._build_evidence(run_id, attempt)
            commit = self._build_commit(
                run_id,
                step.step_id,
                attempt,
                evidence,
            )
            committed = self.service.commit_step(
                run_id,
                step.step_id,
                commit,
                expected_revision=started_run.revision,
            )
            self._complete_if_finished(committed)
        except (ResearchControlError, ResearchRevisionConflictError, ResearchStateError) as exc:
            error_code = getattr(exc, "error_code", "research_execution_stopped")
            yield self._control_error_event(error_code)

    def pause_run(self, run_id: str, *, expected_revision: int):
        return self.service.pause_run(run_id, expected_revision=expected_revision)

    def cancel_run(self, run_id: str, *, expected_revision: int):
        return self.service.cancel_run(run_id, expected_revision=expected_revision)

    def _prepare_run(self, run_id: str) -> ResearchPlanSnapshot:
        plan = self.service.get_plan(run_id)
        if plan.run.status in TERMINAL_RUN_STATUSES:
            raise ResearchControlError(
                "research_not_runnable",
                f"cannot execute a run while it is {plan.run.status}",
            )
        if plan.run.status in {"planned", "running", "blocked"}:
            return self.service.resume_run(
                run_id,
                expected_revision=plan.run.revision,
                current_identity=self.identity,
            )
        return plan

    def _complete_if_finished(self, plan: ResearchPlanSnapshot) -> None:
        if not plan.steps or any(
            step.status not in {"completed", "skipped"} for step in plan.steps
        ):
            return
        self.service.complete_run(
            plan.run.run_id,
            expected_revision=plan.run.revision,
        )

    def _build_evidence(
        self,
        run_id: str,
        attempt: _AttemptState,
    ) -> tuple[EvidenceRefDraft, ...]:
        candidates = list(attempt.observations)
        if attempt.retrieval_completed:
            snapshot = self.agent.get_retrieval_snapshot()
            candidates.extend(getattr(snapshot, "documents", ()) or ())
        evidence = {}
        for item in candidates:
            draft = self._evidence_from_observation(run_id, item)
            if draft is not None:
                evidence[draft.evidence_id] = draft
        return tuple(evidence.values())

    @staticmethod
    def _evidence_from_observation(
        run_id: str,
        observation: dict[str, Any],
    ) -> EvidenceRefDraft | None:
        if not isinstance(observation, dict):
            return None
        source_id = str(observation.get("source_id") or "").strip()
        if not source_id:
            return None
        locator = str(observation.get("locator") or "unknown").strip() or "unknown"
        strategy = (
            str(observation.get("chunk_strategy") or "unknown").strip() or "unknown"
        )
        chunk_order = observation.get("chunk_order")
        if isinstance(chunk_order, bool) or not isinstance(chunk_order, int):
            chunk_order = None
        identity = json.dumps(
            [run_id, source_id, locator, chunk_order, strategy],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        evidence_id = f"evidence-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:24]}"
        return EvidenceRefDraft(
            source_id=source_id,
            locator=locator,
            chunk_order=chunk_order,
            chunk_strategy=strategy,
            evidence_id=evidence_id,
        )

    @staticmethod
    def _build_commit(
        run_id: str,
        step_id: str,
        attempt: _AttemptState,
        evidence: tuple[EvidenceRefDraft, ...],
    ) -> ResearchStepCommit:
        answer = attempt.answer[:_MAX_CHECKPOINT_TEXT]
        evidence_ids = tuple(item.evidence_id for item in evidence if item.evidence_id)
        finding_hash = hashlib.sha256(
            f"{run_id}:{step_id}:{answer}".encode("utf-8")
        ).hexdigest()[:24]
        commit_hash = hashlib.sha256(f"{run_id}:{step_id}".encode("utf-8")).hexdigest()[:24]
        finding = ResearchFindingDraft(
            text=answer,
            status="verified" if evidence_ids else "candidate",
            evidence_ids=evidence_ids,
            finding_id=f"finding-{finding_hash}",
        )
        return ResearchStepCommit(
            result_summary=answer,
            evidence_refs=evidence,
            findings=(finding,),
            commit_id=f"commit-{commit_hash}",
            tool_call_count=attempt.tool_call_count,
            model_call_count=attempt.model_call_count,
        )

    @staticmethod
    def _control_error_event(error_code: str) -> AgentEvent:
        return AgentEvent(
            kind="error",
            content="研究执行已停止，请检查任务状态后重试。",
            status="error",
            error_code=error_code,
        )
