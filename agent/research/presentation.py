from __future__ import annotations

import math
from collections.abc import Mapping
from typing import TypedDict

from agent.context.store import ConversationSummarySnapshot
from agent.research.control import RESEARCH_PAUSED
from agent.research.models import ResearchPlanSnapshot
from model_gateway.gateway import GatewaySnapshot, profile_name_for_route


RUN_STATUS_LABELS = {
    "planned": "待开始",
    "running": "执行中",
    "completed": "已完成",
    "blocked": "受阻",
    "cancelled": "已取消",
    "failed": "失败",
}


class ConversationContextFindingView(TypedDict):
    claim: str
    evidence_ids: tuple[str, ...]


class ConversationContextSummaryView(TypedDict):
    goal: str
    user_constraints: tuple[str, ...]
    confirmed_findings: tuple[ConversationContextFindingView, ...]
    decisions: tuple[str, ...]
    unresolved_questions: tuple[str, ...]
    failed_attempts: tuple[str, ...]
    referenced_source_ids: tuple[str, ...]


class ConversationContextView(TypedDict):
    available: bool
    status: str
    revision: int
    compression_count: int
    tokens_before: int
    tokens_after: int
    token_reduction: int
    token_reduction_ratio: float
    messages_before: int
    messages_after: int
    retained_messages: int
    summary_model: str
    fallback_reason: str
    summary: ConversationContextSummaryView


class ModelGatewayView(TypedDict):
    available: bool
    health: str
    ready: str
    profile: str
    backend: str
    quantization: str
    circuit_state: str
    primary_model: str
    actual_model: str
    fallback_reason: str
    request_id: str
    ttft_seconds: float | None
    latency_seconds: float | None
    input_tokens: int | None
    output_tokens: int | None


def _display_text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _display_float(value: object) -> float | None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        return None
    return float(value)


def _display_int(value: object) -> int | None:
    return value if type(value) is int and value >= 0 else None


def build_model_gateway_view(
    gateway_snapshot: GatewaySnapshot | None,
    last_route: Mapping[str, object] | None,
) -> ModelGatewayView:
    if gateway_snapshot is not None and not isinstance(
        gateway_snapshot,
        GatewaySnapshot,
    ):
        raise TypeError("gateway_snapshot must be a GatewaySnapshot or None")
    if last_route is not None and not isinstance(last_route, Mapping):
        raise TypeError("last_route must be a mapping or None")

    route = last_route or {}
    backend = _display_text(route.get("backend"))
    quantization = _display_text(route.get("quantization"))
    profile = _display_text(route.get("profile")) or profile_name_for_route(
        backend,
        quantization,
    )
    circuit_state = ""
    if gateway_snapshot is not None:
        circuit_state = _display_text(gateway_snapshot.circuit.state.value)

    return {
        "available": gateway_snapshot.available if gateway_snapshot else False,
        "health": _display_text(gateway_snapshot.health) if gateway_snapshot else "",
        "ready": _display_text(gateway_snapshot.ready) if gateway_snapshot else "",
        "profile": profile,
        "backend": backend,
        "quantization": quantization,
        "circuit_state": circuit_state,
        "primary_model": _display_text(route.get("primary_model"))
        or (
            _display_text(gateway_snapshot.primary_model)
            if gateway_snapshot is not None
            else ""
        ),
        "actual_model": _display_text(route.get("actual_model")),
        "fallback_reason": _display_text(route.get("fallback_reason")),
        "request_id": _display_text(route.get("request_id")),
        "ttft_seconds": _display_float(route.get("ttft_seconds")),
        "latency_seconds": _display_float(route.get("latency_seconds")),
        "input_tokens": _display_int(route.get("input_tokens")),
        "output_tokens": _display_int(route.get("output_tokens")),
    }


def build_conversation_context_view(
    snapshot: ConversationSummarySnapshot | None,
    event_count: int,
) -> ConversationContextView:
    if snapshot is not None and not isinstance(
        snapshot,
        ConversationSummarySnapshot,
    ):
        raise TypeError("snapshot must be a ConversationSummarySnapshot or None")
    if type(event_count) is not int:
        raise TypeError("event_count must be an int")
    if event_count < 0:
        raise ValueError("event_count must be non-negative")

    empty_summary: ConversationContextSummaryView = {
        "goal": "",
        "user_constraints": (),
        "confirmed_findings": (),
        "decisions": (),
        "unresolved_questions": (),
        "failed_attempts": (),
        "referenced_source_ids": (),
    }
    if snapshot is None:
        return {
            "available": False,
            "status": "",
            "revision": 0,
            "compression_count": event_count,
            "tokens_before": 0,
            "tokens_after": 0,
            "token_reduction": 0,
            "token_reduction_ratio": 0.0,
            "messages_before": 0,
            "messages_after": 0,
            "retained_messages": 0,
            "summary_model": "",
            "fallback_reason": "",
            "summary": empty_summary,
        }

    token_reduction = max(0, snapshot.tokens_before - snapshot.tokens_after)
    token_reduction_ratio = (
        token_reduction / snapshot.tokens_before
        if snapshot.tokens_before > 0 and token_reduction > 0
        else 0.0
    )
    summary = snapshot.summary
    summary_view: ConversationContextSummaryView = {
        "goal": summary.goal if summary.goal else "",
        "user_constraints": tuple(summary.user_constraints),
        "confirmed_findings": tuple(
            ConversationContextFindingView(
                claim=finding.claim if finding.claim else "",
                evidence_ids=tuple(finding.evidence_ids),
            )
            for finding in summary.confirmed_findings
        ),
        "decisions": tuple(summary.decisions),
        "unresolved_questions": tuple(summary.unresolved_questions),
        "failed_attempts": tuple(summary.failed_attempts),
        "referenced_source_ids": tuple(summary.referenced_source_ids),
    }
    return {
        "available": True,
        "status": "已压缩",
        "revision": snapshot.revision,
        "compression_count": event_count,
        "tokens_before": snapshot.tokens_before,
        "tokens_after": snapshot.tokens_after,
        "token_reduction": token_reduction,
        "token_reduction_ratio": token_reduction_ratio,
        "messages_before": snapshot.messages_before,
        "messages_after": snapshot.messages_after,
        "retained_messages": snapshot.messages_after,
        "summary_model": snapshot.summary_model or "",
        "fallback_reason": snapshot.fallback_reason or "",
        "summary": summary_view,
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
