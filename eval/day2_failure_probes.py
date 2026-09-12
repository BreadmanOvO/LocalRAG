"""Deterministic D02 probes for the historical v1.7 failure modes.

The probes exercise existing production boundaries without starting Streamlit,
an external model service, or a network request. They classify the observed
state; they do not claim that the v1.8 fixes are implemented.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from agent.context.compressor import ConversationCompressor, SummaryClientResult
from agent.context.models import CompressionPolicy
from agent.context.store import ConversationContextStore
from agent.memory.task import TaskMemoryStore
from agent.react_agent import _execution_error_code
from agent.research import (
    ResearchAgentRuntime,
    ResearchControlError,
    ResearchExecutionIdentity,
    ResearchRunService,
    ResearchRunStore,
    ResearchStepDraft,
)
from eval.agent_control_probes import run_control_probe


class _SummaryClient:
    model_id = "d02-fake-summary"

    def summarize(self, request):
        previous = request.previous_summary
        return SummaryClientResult(
            payload={
                "goal": previous.goal if previous else "D02 compression probe",
                "user_constraints": [],
                "confirmed_findings": [],
                "decisions": [],
                "unresolved_questions": [],
                "failed_attempts": [],
                "referenced_source_ids": [],
            },
            model_id=self.model_id,
            fallback_reason="",
        )


class _NoopAgent:
    task_id = "d02-task"

    def execute_events(self, _query: str):
        if False:
            yield None


def _identity() -> ResearchExecutionIdentity:
    return ResearchExecutionIdentity(
        corpus_fingerprint="sha256:d02-corpus",
        registry_fingerprint="sha256:d02-registry",
        code_revision="d02-probe-revision",
        code_dirty=False,
    )


def _result(name: str, *, passed: bool, **values: Any) -> dict[str, Any]:
    return {
        "probe": name,
        "case_pass": passed,
        **values,
    }


def probe_model_request_failed() -> dict[str, Any]:
    observed = {
        type(exc).__name__: _execution_error_code(exc)
        for exc in (TimeoutError("timeout"), ConnectionError("offline"))
    }
    passed = all(code == "model_request_failed" for code in observed.values())
    return _result(
        "model_request_failed",
        passed=passed,
        trigger={"exceptions": list(observed)},
        observed={"error_codes": observed},
        impact="模型请求未成功时，UI 只能展示结构化失败，不能伪装成知识库答案",
    )


def probe_research_run_active(root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    service = ResearchRunService(ResearchRunStore(root / "research.sqlite3"))
    runtime = ResearchAgentRuntime(_NoopAgent(), service, _identity())
    first = runtime.create_run("D02 active run")
    observed_code = ""
    try:
        runtime.create_run("D02 different goal")
    except ResearchControlError as exc:
        observed_code = exc.error_code
    passed = observed_code == "research_run_active" and first.run.status == "planned"
    return _result(
        "research_run_active",
        passed=passed,
        trigger={"first_goal": first.run.goal, "second_goal": "D02 different goal"},
        observed={"error_code": observed_code, "run_id": first.run.run_id},
        impact="活动研究运行阻止第二个不同目标，避免并发写入同一任务状态",
    )


def probe_tool_call_limit(root: Path) -> dict[str, Any]:
    result = run_control_probe("tool_budget_termination", _identity(), root / "tool-limit")
    termination = result["termination"]
    passed = bool(result["case_pass"]) and termination["observed_code"] == "tool_call_limit_exceeded"
    return _result(
        "tool_call_limit_exceeded",
        passed=passed,
        trigger={"tool_call_limit": 1, "attempted_calls": 2},
        observed=termination,
        impact="工具预算耗尽时终止 Planner，避免无限工具循环",
    )


def probe_compression_followup(root: Path) -> dict[str, Any]:
    store = ConversationContextStore(root / "conversation.sqlite3")
    policy = CompressionPolicy(
        context_limit=5000,
        fixed_overhead_tokens=0,
        output_reserve_tokens=0,
        trigger_ratio=0.20,
        target_ratio=0.15,
        hard_limit_ratio=0.90,
        recent_turns=1,
    )
    compressor = ConversationCompressor(
        store,
        _SummaryClient(),
        policy=policy,
        target_model_context_limit=5000,
        summary_model_context_limit=5000,
    )
    messages = (
        HumanMessage(content="old question " + "x" * 1400, id="d02-m1"),
        AIMessage(content="old answer " + "y" * 1400, id="d02-m2"),
        HumanMessage(content="recent question", id="d02-m3"),
        AIMessage(content="recent answer", id="d02-m4"),
    )
    first = compressor.prepare_model_view("d02-session", messages)
    second = compressor.prepare_model_view("d02-session", messages)
    passed = (
        first.status == "compressed"
        and second.status == "not_needed"
        and second.summary is not None
        and tuple(message.id for message in second.recent_messages) == ("d02-m3", "d02-m4")
    )
    return _result(
        "compression_followup",
        passed=passed,
        trigger={"message_ids": ["d02-m1", "d02-m2", "d02-m3", "d02-m4"], "second_turn": True},
        observed={
            "first_status": first.status,
            "second_status": second.status,
            "summary_revision": second.revision,
            "second_recent_message_ids": [message.id for message in second.recent_messages],
        },
        impact="压缩后追问复用已持久化摘要，不重复压缩或丢失最近消息",
    )


def probe_empty_task_memory(root: Path) -> dict[str, Any]:
    store = TaskMemoryStore(root / "task-memory.sqlite3")
    snapshot = store.get_task("d02-empty-task")
    payload = snapshot.to_dict()
    expected_empty = {
        "topic": "",
        "searched_queries": [],
        "retrieved_sources": [],
        "confirmed_sources": [],
        "findings": [],
        "evidence_gaps": [],
        "open_questions": [],
    }
    observed = {key: payload[key] for key in expected_empty}
    passed = snapshot.is_empty and observed == expected_empty
    return _result(
        "empty_task_memory",
        passed=passed,
        trigger={"task_id": "d02-empty-task", "operation": "read_before_update"},
        observed={"is_empty": snapshot.is_empty, "payload": observed},
        impact="新任务读取为空记忆是合法初始状态，UI 应提供可操作的写入入口而非报错",
    )


def run_d02_probes(work_dir: str | Path) -> dict[str, Any]:
    root = Path(work_dir)
    root.mkdir(parents=True, exist_ok=True)
    probes = (
        probe_model_request_failed(),
        probe_research_run_active(root / "research-active"),
        probe_tool_call_limit(root),
        probe_compression_followup(root / "compression"),
        probe_empty_task_memory(root / "empty-memory"),
    )
    return {
        "day": "D02",
        "status": "observed",
        "probes": list(probes),
        "all_pass": all(probe["case_pass"] for probe in probes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic D02 failure probes")
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_d02_probes(args.work_dir)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output is None:
        print(payload, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    return 0 if result["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
