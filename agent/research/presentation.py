from __future__ import annotations

from agent.research.control import RESEARCH_PAUSED
from agent.research.models import ResearchPlanSnapshot


RUN_STATUS_LABELS = {
    "planned": "待开始",
    "running": "执行中",
    "completed": "已完成",
    "blocked": "受阻",
    "cancelled": "已取消",
    "failed": "失败",
}


def run_status_label(plan: ResearchPlanSnapshot) -> str:
    if plan.run.status == "blocked" and plan.run.stop_reason == RESEARCH_PAUSED:
        return "已暂停"
    return RUN_STATUS_LABELS.get(plan.run.status, plan.run.status)
STEP_STATUS_LABELS = {
    "pending": "等待",
    "running": "执行中",
    "completed": "完成",
    "blocked": "暂停",
    "skipped": "跳过",
    "failed": "失败",
}


def is_active_plan(plan: ResearchPlanSnapshot | None) -> bool:
    return plan is not None and plan.run.status not in {
        "completed",
        "cancelled",
        "failed",
    }


def research_progress(plan: ResearchPlanSnapshot) -> float:
    if not plan.steps:
        return 0.0
    finished = sum(
        step.status in {"completed", "skipped"} for step in plan.steps
    )
    return finished / len(plan.steps)


def build_step_rows(plan: ResearchPlanSnapshot) -> list[dict[str, object]]:
    return [
        {
            "步骤": step.position,
            "目标": step.objective,
            "状态": STEP_STATUS_LABELS.get(step.status, step.status),
            "尝试": step.attempt_count,
            "结果": step.result_summary,
            "错误码": step.error_code,
        }
        for step in plan.steps
    ]


def build_evidence_rows(plan: ResearchPlanSnapshot) -> list[dict[str, object]]:
    return [
        {
            "证据 ID": evidence.evidence_id,
            "来源": evidence.source_id,
            "位置": evidence.locator,
            "片段": evidence.chunk_order,
            "策略": evidence.chunk_strategy,
        }
        for evidence in plan.evidence_refs
    ]


def build_finding_rows(plan: ResearchPlanSnapshot) -> list[dict[str, object]]:
    evidence_by_id = {
        evidence.evidence_id: f"{evidence.source_id} · {evidence.locator}"
        for evidence in plan.evidence_refs
    }
    return [
        {
            "状态": finding.status,
            "结论": finding.text,
            "证据": "\n".join(
                evidence_by_id.get(evidence_id, evidence_id)
                for evidence_id in finding.evidence_ids
            ),
        }
        for finding in plan.findings
    ]
