from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain.agents.middleware.tool_call_limit import ToolCallLimitExceededError
from langchain_core.messages import AIMessage, ToolMessage

from agent.execution import (
    AgentExecutionBudget,
    DuplicateToolCallError,
    ExecutionGuardMiddleware,
    NoProgressLimitExceededError,
)
from agent.research import (
    EvidenceRefDraft,
    ResearchControlError,
    ResearchExecutionIdentity,
    ResearchFindingDraft,
    ResearchRunService,
    ResearchRunStore,
    ResearchStepCommit,
    ResearchStepDraft,
)


CONTROL_PROBE_NAMES = frozenset(
    {
        "tool_budget_termination",
        "duplicate_call_block",
        "no_progress_termination",
        "insufficient_evidence_rejection",
        "verified_evidence_binding",
        "pause_resume_checkpoint",
        "cancel_run_control",
    }
)


def _tool_call(call_id: str, *, source_id: str = "paper-001") -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "inspect_source",
                "args": {"source_id": source_id},
                "id": call_id,
                "type": "tool_call",
            }
        ],
    )


def _base_result(probe: str) -> dict[str, Any]:
    return {
        "probe": probe,
        "turns": [],
        "attempts": [],
        "attempt_count": 1,
        "infrastructure_retry_count": 0,
        "error": "",
        "termination": {
            "applicable": False,
            "expected_code": "",
            "observed_code": "",
            "classified": True,
            "contract_pass": True,
        },
        "duplicate": {
            "applicable": False,
            "blocked": False,
            "violation": False,
            "contract_pass": True,
        },
        "evidence_binding": {
            "applicable": False,
            "verified_finding_count": 0,
            "bound_verified_finding_count": 0,
            "invalid_binding_rejected": False,
            "contract_pass": True,
        },
        "resume": {
            "applicable": False,
            "checkpoint_resume_pass": False,
            "contract_pass": True,
        },
        "control": {
            "applicable": False,
            "final_status": "",
            "contract_pass": True,
        },
    }


def _finish(result: dict[str, Any], passed: bool) -> dict[str, Any]:
    result["evaluation"] = {
        "tool_contract_pass": passed,
        "answer_contract_pass": passed,
        "probe_contract_pass": passed,
    }
    result["case_pass"] = passed
    result["attempts"] = [
        {
            "attempt": 1,
            "turns": [],
            "case_pass": passed,
            "retryable_errors": [],
        }
    ]
    return result


def _tool_budget_probe(_identity: ResearchExecutionIdentity, _root: Path) -> dict[str, Any]:
    result = _base_result("tool_budget_termination")
    limiter = next(
        item
        for item in AgentExecutionBudget(
            tool_call_limit=1,
            model_call_limit=4,
            duplicate_tool_call_detection=False,
            no_progress_limit=None,
        ).build_middleware()
        if isinstance(item, ToolCallLimitMiddleware)
    )
    message = _tool_call("tool-budget-call")
    boundary = limiter.after_model(
        {
            "messages": [message],
            "run_tool_call_count": {"__all__": 0},
        },
        None,
    )
    observed_code = ""
    try:
        limiter.after_model(
            {
                "messages": [message],
                "run_tool_call_count": {"__all__": 1},
            },
            None,
        )
    except ToolCallLimitExceededError:
        observed_code = "tool_call_limit_exceeded"

    passed = (
        boundary["run_tool_call_count"]["__all__"] == 1
        and observed_code == "tool_call_limit_exceeded"
    )
    result["termination"].update(
        {
            "applicable": True,
            "expected_code": "tool_call_limit_exceeded",
            "observed_code": observed_code,
            "classified": bool(observed_code),
            "contract_pass": passed,
        }
    )
    result["observed"] = {"allowed_call_count": 1, "blocked_call_count": 1}
    return _finish(result, passed)


def _duplicate_probe(_identity: ResearchExecutionIdentity, _root: Path) -> dict[str, Any]:
    result = _base_result("duplicate_call_block")
    guard = ExecutionGuardMiddleware(
        duplicate_tool_call_detection=True,
        no_progress_limit=None,
    )
    first = guard.after_model(
        {"messages": [_tool_call("duplicate-1")], "plan_revision": 1},
        None,
    )
    blocked = False
    observed_code = ""
    try:
        guard.after_model(
            {
                **first,
                "messages": [_tool_call("duplicate-2")],
                "plan_revision": 1,
            },
            None,
        )
    except DuplicateToolCallError:
        blocked = True
        observed_code = "duplicate_tool_call"

    passed = blocked and observed_code == "duplicate_tool_call"
    result["termination"].update(
        {
            "applicable": True,
            "expected_code": "duplicate_tool_call",
            "observed_code": observed_code,
            "classified": bool(observed_code),
            "contract_pass": passed,
        }
    )
    result["duplicate"].update(
        {
            "applicable": True,
            "blocked": blocked,
            "violation": not blocked,
            "contract_pass": passed,
        }
    )
    result["observed"] = {"attempted_call_count": 2, "executed_call_count": 1}
    return _finish(result, passed)


def _no_progress_probe(_identity: ResearchExecutionIdentity, _root: Path) -> dict[str, Any]:
    result = _base_result("no_progress_termination")
    guard = ExecutionGuardMiddleware(
        duplicate_tool_call_detection=False,
        no_progress_limit=2,
    )
    first_ai = _tool_call("no-progress-1", source_id="missing-1")
    baseline = guard.after_model({"messages": [first_ai]}, None)
    first_tool = ToolMessage(content="not found", tool_call_id="no-progress-1")
    second_ai = _tool_call("no-progress-2", source_id="missing-2")
    after_first = guard.after_model(
        {**baseline, "messages": [first_tool, second_ai]},
        None,
    )
    second_tool = ToolMessage(content="not found", tool_call_id="no-progress-2")
    third_ai = _tool_call("no-progress-3", source_id="missing-3")
    observed_code = ""
    try:
        guard.after_model(
            {
                **after_first,
                "messages": [first_tool, second_tool, third_ai],
            },
            None,
        )
    except NoProgressLimitExceededError:
        observed_code = "no_progress_limit"

    passed = (
        after_first["run_no_progress_count"] == 1
        and observed_code == "no_progress_limit"
    )
    result["termination"].update(
        {
            "applicable": True,
            "expected_code": "no_progress_limit",
            "observed_code": observed_code,
            "classified": bool(observed_code),
            "contract_pass": passed,
        }
    )
    result["observed"] = {"completed_no_progress_results": 2}
    return _finish(result, passed)


def _create_research_plan(
    root: Path,
    identity: ResearchExecutionIdentity,
) -> tuple[ResearchRunService, Any]:
    root.mkdir(parents=True, exist_ok=True)
    service = ResearchRunService(ResearchRunStore(root / "research-runs.sqlite3"))
    plan = service.create_plan(
        "agent-eval-task",
        "Inspect source evidence",
        (ResearchStepDraft("Inspect source", "inspect_source"),),
        identity=identity,
        run_id="agent-eval-run",
    )
    return service, plan


def _insufficient_evidence_probe(
    identity: ResearchExecutionIdentity,
    root: Path,
) -> dict[str, Any]:
    result = _base_result("insufficient_evidence_rejection")
    service, plan = _create_research_plan(root, identity)
    started_run, step = service.claim_next_step(
        plan.run.run_id,
        expected_revision=plan.run.revision,
    )
    rejected = False
    try:
        service.commit_step(
            plan.run.run_id,
            step.step_id,
            ResearchStepCommit(
                "Unsupported finding",
                findings=(
                    ResearchFindingDraft(
                        "Unsupported finding",
                        status="verified",
                        evidence_ids=(),
                    ),
                ),
                commit_id="commit-insufficient",
            ),
            expected_revision=started_run.revision,
        )
    except (ValueError, ResearchControlError):
        rejected = True
    snapshot = service.get_plan(plan.run.run_id)
    passed = (
        rejected
        and not snapshot.evidence_refs
        and not snapshot.findings
        and snapshot.steps[0].status == "running"
    )
    result["evidence_binding"].update(
        {
            "applicable": True,
            "invalid_binding_rejected": rejected,
            "contract_pass": passed,
        }
    )
    result["observed"] = {
        "persisted_evidence_count": len(snapshot.evidence_refs),
        "persisted_finding_count": len(snapshot.findings),
        "step_status": snapshot.steps[0].status,
    }
    return _finish(result, passed)


def _verified_binding_probe(
    identity: ResearchExecutionIdentity,
    root: Path,
) -> dict[str, Any]:
    result = _base_result("verified_evidence_binding")
    service, plan = _create_research_plan(root, identity)
    started_run, step = service.claim_next_step(
        plan.run.run_id,
        expected_revision=plan.run.revision,
    )
    snapshot = service.commit_step(
        plan.run.run_id,
        step.step_id,
        ResearchStepCommit(
            "Finding is supported",
            evidence_refs=(
                EvidenceRefDraft(
                    "paper-001",
                    locator="page-1",
                    chunk_order=1,
                    chunk_strategy="probe",
                    evidence_id="evidence-a",
                ),
            ),
            findings=(
                ResearchFindingDraft(
                    "Finding is supported",
                    status="verified",
                    evidence_ids=("evidence-a",),
                    finding_id="finding-a",
                ),
            ),
            commit_id="commit-bound",
        ),
        expected_revision=started_run.revision,
    )
    evidence_by_id = {item.evidence_id: item for item in snapshot.evidence_refs}
    verified = [item for item in snapshot.findings if item.status == "verified"]
    bound = [
        item
        for item in verified
        if item.evidence_ids
        and all(
            evidence_id in evidence_by_id
            and evidence_by_id[evidence_id].run_id == item.run_id == snapshot.run.run_id
            for evidence_id in item.evidence_ids
        )
    ]
    passed = len(verified) == 1 and len(bound) == 1
    result["evidence_binding"].update(
        {
            "applicable": True,
            "verified_finding_count": len(verified),
            "bound_verified_finding_count": len(bound),
            "contract_pass": passed,
        }
    )
    result["observed"] = {
        "run_id": snapshot.run.run_id,
        "evidence_ids": sorted(evidence_by_id),
        "finding_ids": [item.finding_id for item in verified],
    }
    return _finish(result, passed)


def _pause_resume_probe(
    identity: ResearchExecutionIdentity,
    root: Path,
) -> dict[str, Any]:
    result = _base_result("pause_resume_checkpoint")
    service, plan = _create_research_plan(root, identity)
    started_run, first_step = service.claim_next_step(
        plan.run.run_id,
        expected_revision=plan.run.revision,
    )
    paused = service.pause_run(
        plan.run.run_id,
        expected_revision=started_run.revision,
    )
    restarted = ResearchRunService(ResearchRunStore(root / "research-runs.sqlite3"))
    resumed = restarted.resume_run(
        plan.run.run_id,
        expected_revision=paused.revision,
        current_identity=identity,
    )
    retried_run, retried_step = restarted.claim_next_step(
        plan.run.run_id,
        expected_revision=resumed.run.revision,
    )
    passed = (
        paused.status == "blocked"
        and resumed.run.status == "running"
        and resumed.steps[0].status == "pending"
        and first_step.step_id == retried_step.step_id
        and retried_step.attempt_count == 2
        and retried_run.current_step_id == retried_step.step_id
    )
    result["resume"].update(
        {
            "applicable": True,
            "checkpoint_resume_pass": passed,
            "contract_pass": passed,
        }
    )
    result["control"].update(
        {
            "applicable": True,
            "final_status": retried_run.status,
            "contract_pass": passed,
        }
    )
    result["observed"] = {
        "paused_revision": paused.revision,
        "resumed_revision": resumed.run.revision,
        "retried_revision": retried_run.revision,
        "retried_attempt_count": retried_step.attempt_count,
    }
    return _finish(result, passed)


def _cancel_probe(identity: ResearchExecutionIdentity, root: Path) -> dict[str, Any]:
    result = _base_result("cancel_run_control")
    service, plan = _create_research_plan(root, identity)
    started_run, step = service.claim_next_step(
        plan.run.run_id,
        expected_revision=plan.run.revision,
    )
    cancelled = service.cancel_run(
        plan.run.run_id,
        expected_revision=started_run.revision,
    )
    observed_code = ""
    try:
        service.ensure_step_active(plan.run.run_id, step.step_id)
    except ResearchControlError as exc:
        observed_code = exc.error_code
    snapshot = service.get_plan(plan.run.run_id)
    passed = (
        cancelled.status == "cancelled"
        and snapshot.run.status == "cancelled"
        and observed_code == "research_cancelled"
    )
    result["control"].update(
        {
            "applicable": True,
            "final_status": snapshot.run.status,
            "contract_pass": passed,
        }
    )
    result["observed"] = {
        "stop_reason": snapshot.run.stop_reason,
        "active_step_error": observed_code,
        "step_status": snapshot.steps[0].status,
    }
    return _finish(result, passed)


_PROBE_RUNNERS: dict[
    str,
    Callable[[ResearchExecutionIdentity, Path], dict[str, Any]],
] = {
    "tool_budget_termination": _tool_budget_probe,
    "duplicate_call_block": _duplicate_probe,
    "no_progress_termination": _no_progress_probe,
    "insufficient_evidence_rejection": _insufficient_evidence_probe,
    "verified_evidence_binding": _verified_binding_probe,
    "pause_resume_checkpoint": _pause_resume_probe,
    "cancel_run_control": _cancel_probe,
}


def run_control_probe(
    probe: str,
    identity: ResearchExecutionIdentity,
    work_dir: str | Path,
) -> dict[str, Any]:
    if probe not in _PROBE_RUNNERS:
        raise ValueError(f"unknown control probe: {probe}")
    try:
        return _PROBE_RUNNERS[probe](identity, Path(work_dir))
    except Exception as exc:
        result = _base_result(probe)
        result["error"] = f"{type(exc).__name__}: {exc}"
        return _finish(result, False)
