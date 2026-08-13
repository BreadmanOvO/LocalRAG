from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from utils.path_tools import get_abs_path, get_project_root
from utils.git_identity import CODE_IDENTITY_PATHSPEC


TOOL_LABELS = {
    "rag_search": "检索知识库",
    "show_sources": "查看检索来源",
    "inspect_source": "检查来源",
    "expand_context": "扩展上下文",
    "compare_sources": "对比来源",
    "evidence_check": "核验证据",
    "show_task_memory": "读取任务记忆",
    "update_task_memory": "更新任务记忆",
    "clarify_question": "澄清问题",
}

MEMORY_FIELD_LABELS = {
    "topic": "主题",
    "searched_queries": "已检索问题",
    "retrieved_sources": "检索命中来源",
    "confirmed_sources": "已确认来源",
    "findings": "阶段结论",
    "evidence_gaps": "证据缺口",
    "open_questions": "待解决问题",
}

EMPTY_ANSWER_MESSAGE = "抱歉，未生成有效回答，请重试。"


@dataclass(frozen=True)
class AgentEvent:
    kind: str
    tool_name: str = ""
    call_id: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    content: str = ""
    status: str = ""
    error_code: str = ""
    elapsed_ms: int | None = None
    observations: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(asdict(self))


@dataclass
class _ToolCallPair:
    started: dict[str, Any]
    completed: dict[str, Any] | None = None


def tool_label(tool_name: str) -> str:
    return TOOL_LABELS.get(tool_name, tool_name or "未知工具")


def finalize_agent_answer(answer_parts: list[str], *, has_error: bool) -> tuple[str, bool]:
    answer = "".join(answer_parts).strip()
    if answer:
        return answer, has_error
    return EMPTY_ANSWER_MESSAGE, True


def _tool_calls_match(started: dict[str, Any], completed: dict[str, Any]) -> bool:
    completed_call_id = completed.get("call_id")
    if completed_call_id:
        return started.get("call_id") == completed_call_id
    return started.get("tool_name") == completed.get("tool_name")


def _pair_tool_calls(trace: list[dict[str, Any]]) -> list[_ToolCallPair]:
    pairs = []
    pending = []
    for event in trace:
        kind = event.get("kind")
        if kind == "tool_started":
            pair = _ToolCallPair(started=event)
            pairs.append(pair)
            pending.append(pair)
            continue
        if kind != "tool_completed":
            continue
        match = next(
            (pair for pair in pending if _tool_calls_match(pair.started, event)),
            None,
        )
        if match is not None:
            match.completed = event
            pending.remove(match)
    return pairs


def has_pending_tool_calls(trace: list[dict[str, Any]]) -> bool:
    return any(pair.completed is None for pair in _pair_tool_calls(trace))


def build_tool_trace_rows(
    trace: list[dict[str, Any]],
    *,
    mark_pending_interrupted: bool = False,
) -> list[dict[str, str]]:
    rows = []
    for pair in _pair_tool_calls(trace):
        started = pair.started
        completed = pair.completed
        if completed is None:
            status = "中断" if mark_pending_interrupted else "运行中"
            elapsed = ""
        else:
            status = "失败" if completed.get("status") in {"error", "failed"} else "完成"
            elapsed_ms = max(
                0,
                (completed.get("elapsed_ms") or 0) - (started.get("elapsed_ms") or 0),
            )
            elapsed = f"{elapsed_ms / 1000:.2f}s"
        rows.append(
            {
                "工具": tool_label(str(started.get("tool_name") or "unknown")),
                "状态": status,
                "耗时": elapsed,
                "参数": json.dumps(started.get("arguments") or {}, ensure_ascii=False),
                "错误码": str(completed.get("error_code") or "") if completed else "",
            }
        )
    return rows


def build_source_observation(
    document: dict[str, Any],
    *,
    evidence_status: str,
) -> dict[str, Any]:
    content = " ".join(str(document.get("content") or "").split())
    return {
        "source_id": str(document.get("source_id") or "unknown"),
        "locator": str(document.get("locator") or "unknown"),
        "chunk_order": document.get("chunk_order"),
        "chunk_strategy": str(document.get("chunk_strategy") or "unknown"),
        "rank": document.get("rank"),
        "score": document.get("score"),
        "dense_rank": document.get("dense_rank"),
        "bm25_rank": document.get("bm25_rank"),
        "rrf_rank": document.get("rrf_rank"),
        "rerank_rank": document.get("rerank_rank"),
        "retrieval_stage": document.get("retrieval_stage"),
        "summary": content[:240] + ("..." if len(content) > 240 else ""),
        "evidence_status": evidence_status,
    }


def merge_source_observations(
    *groups: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    observations = []
    seen = set()
    for source in (source for group in groups for source in group):
        key = tuple(
            source.get(field)
            for field in ("source_id", "locator", "chunk_order", "chunk_strategy")
        )
        if key not in seen:
            seen.add(key)
            observations.append(source)
    return observations


def build_source_observations(
    retrieval_snapshot,
    *,
    confirmed_sources: tuple[str, ...] | list[str] = (),
) -> list[dict[str, Any]]:
    if retrieval_snapshot is None:
        return []

    confirmed = {str(source_id) for source_id in confirmed_sources}
    observations = []
    for document in getattr(retrieval_snapshot, "documents", ()) or ():
        source_id = str(document.get("source_id") or "unknown")
        observations.append(
            build_source_observation(
                document,
                evidence_status="confirmed" if source_id in confirmed else "retrieved",
            )
        )
    return merge_source_observations(observations)


def diff_task_memory(before, after) -> list[dict[str, str]]:
    if before is None or after is None:
        return []

    changes: list[dict[str, str]] = []
    for field_name, label in MEMORY_FIELD_LABELS.items():
        before_value = getattr(before, field_name)
        after_value = getattr(after, field_name)
        before_values = (before_value,) if field_name == "topic" and before_value else tuple(before_value)
        after_values = (after_value,) if field_name == "topic" and after_value else tuple(after_value)
        for action, values, other_values in (
            ("removed", before_values, after_values),
            ("added", after_values, before_values),
        ):
            changes.extend(
                {
                    "action": action,
                    "field": field_name,
                    "label": label,
                    "value": value,
                }
                for value in values
                if value not in other_values
            )
    return changes


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _is_formal_eval(manifest: dict[str, Any]) -> bool:
    scope = manifest.get("evaluation_scope")
    if isinstance(scope, dict) and "selection_complete" in scope:
        return bool(scope["selection_complete"])
    return manifest.get("max_cases") is None and not manifest.get("case_ids")


def load_latest_agent_eval(results_dir: str | Path) -> dict[str, Any]:
    candidates = []
    for run_dir in Path(results_dir).glob("agent-eval-*"):
        manifest_path = run_dir / "manifest.json"
        summary_path = run_dir / "summary.json"
        if not manifest_path.is_file() or not summary_path.is_file():
            continue
        try:
            manifest = _read_json_object(manifest_path)
            summary = _read_json_object(summary_path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if not _is_formal_eval(manifest):
            continue
        candidates.append(
            (
                str(manifest.get("created_at") or ""),
                run_dir.name,
                manifest,
                summary,
            )
        )

    if not candidates:
        return {"available": False, "error": "未找到完整的 Agent 评测产物"}

    _created_at, run_id, manifest, summary = max(candidates, key=lambda item: item[:2])
    return {
        "available": True,
        "run_id": run_id,
        "created_at": manifest.get("created_at", ""),
        "runtime": manifest.get("runtime", {}),
        "git_revision": manifest.get("git_revision", ""),
        "git_dirty": manifest.get("git_dirty"),
        "evaluation_scope": manifest.get("evaluation_scope", {}),
        "corpus": manifest.get("corpus", {}),
        "summary": summary,
    }


def _resolve_project_path(path_value: str | Path, project_root: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = Path(project_root) / path
    return path.resolve()


def _git_revisions_compatible(
    evaluated_revision: str,
    current_revision: str,
    project_root: Path,
) -> bool:
    if evaluated_revision == current_revision:
        return True
    try:
        result = subprocess.run(
            [
                "git",
                "diff",
                "--quiet",
                evaluated_revision,
                current_revision,
                "--",
                *CODE_IDENTITY_PATHSPEC,
            ],
            cwd=project_root,
            check=False,
            capture_output=True,
        )
    except OSError:
        return False
    return result.returncode == 0


def combine_runtime_observability(
    *,
    current_corpus: dict[str, Any],
    latest_eval: dict[str, Any],
    current_persist_directory: str | Path,
    collection_name: str,
    current_git_revision: str = "",
    current_git_dirty: bool | None = None,
    project_root: str | Path | None = None,
    stability_gate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = Path(project_root or get_project_root()).resolve()
    current_available = bool(current_corpus.get("available", True))
    active_profile_matches = bool(current_corpus.get("active_profile_matches", True))
    eval_available = bool(latest_eval.get("available"))
    corpus_matches_eval = False
    code_matches_eval = False
    identity_complete = False
    code_clean = False

    if current_available and eval_available:
        evaluated_corpus = latest_eval.get("corpus", {})
        evaluated_path = evaluated_corpus.get("persist_directory")
        evaluated_revision = str(latest_eval.get("git_revision") or "")
        evaluated_dirty = latest_eval.get("git_dirty")
        identity_complete = (
            all(
                (
                    current_corpus.get("corpus_fingerprint"),
                    current_corpus.get("registry_fingerprint"),
                    evaluated_corpus.get("corpus_fingerprint"),
                    evaluated_corpus.get("registry_fingerprint"),
                    evaluated_revision,
                    current_git_revision,
                )
            )
            and isinstance(evaluated_dirty, bool)
            and isinstance(current_git_dirty, bool)
        )
        code_clean = evaluated_dirty is False and current_git_dirty is False
        if evaluated_path and identity_complete and code_clean:
            corpus_matches_eval = (
                _resolve_project_path(current_persist_directory, root)
                == _resolve_project_path(evaluated_path, root)
                and str(evaluated_corpus.get("collection_name") or "") == collection_name
                and current_corpus["corpus_fingerprint"]
                == evaluated_corpus["corpus_fingerprint"]
                and current_corpus["registry_fingerprint"]
                == evaluated_corpus["registry_fingerprint"]
            )
            code_matches_eval = _git_revisions_compatible(
                evaluated_revision,
                current_git_revision,
                root,
            )

    latest_gate_pass = bool(latest_eval.get("summary", {}).get("gate_pass"))
    stability_gate_pass = (
        bool(stability_gate.get("gate_pass")) if stability_gate is not None else True
    )
    stability_reasons = ", ".join((stability_gate or {}).get("failure_reasons", []))
    gate_conditions = (
        (
            current_available,
            "corpus_unavailable",
            current_corpus.get("error", "当前知识库状态不可用"),
        ),
        (
            active_profile_matches,
            "active_profile_mismatch",
            "当前知识库内容与活动 corpus profile 的指纹不一致",
        ),
        (
            eval_available,
            "eval_unavailable",
            latest_eval.get("error", "未找到 Agent 评测结果"),
        ),
        (
            identity_complete,
            "legacy_eval",
            "最近一次完整 Agent 评测缺少数据或代码身份信息，请重新评测",
        ),
        (
            code_clean,
            "code_dirty",
            "当前或被评测的 Agent 代码存在未提交修改",
        ),
        (
            corpus_matches_eval,
            "corpus_mismatch",
            "当前知识库与最近一次 Agent 评测使用的知识库不一致",
        ),
        (
            code_matches_eval,
            "code_mismatch",
            "当前 Agent 代码与最近一次评测版本不一致",
        ),
        (latest_gate_pass, "gate_failed", "当前知识库最近一次 Agent gate 未通过"),
        (
            stability_gate_pass,
            "stability_gate_failed",
            f"Agent 连续稳定性 Gate 未通过：{stability_reasons or 'unknown'}",
        ),
    )
    failed_gate = next(
        ((status, reason) for passed, status, reason in gate_conditions if not passed),
        None,
    )
    gate_status, message = failed_gate or ("passed", "当前知识库已通过 Agent gate")
    effective_gate_pass = failed_gate is None

    return {
        "current_corpus": deepcopy(current_corpus),
        "current_git_revision": current_git_revision,
        "current_git_dirty": current_git_dirty,
        "active_profile_matches": active_profile_matches,
        "latest_eval": deepcopy(latest_eval),
        "stability_gate": deepcopy(stability_gate),
        "corpus_matches_eval": corpus_matches_eval,
        "code_matches_eval": code_matches_eval,
        "identity_complete": identity_complete,
        "code_clean": code_clean,
        "gate_pass": effective_gate_pass,
        "gate_status": gate_status,
        "message": message,
    }


def matches_active_corpus_profile(
    current_corpus: dict[str, Any],
    *,
    expected_corpus_fingerprint: str = "",
    expected_registry_fingerprint: str = "",
    expected_source_count: int | None = None,
    expected_chunk_count: int | None = None,
) -> bool:
    return all(
        (
            not expected_corpus_fingerprint
            or current_corpus.get("corpus_fingerprint") == expected_corpus_fingerprint,
            not expected_registry_fingerprint
            or current_corpus.get("registry_fingerprint") == expected_registry_fingerprint,
            expected_source_count is None
            or current_corpus.get("chroma_source_count") == expected_source_count,
            expected_chunk_count is None
            or current_corpus.get("chunk_count") == expected_chunk_count,
        )
    )


def load_runtime_observability(
    *,
    persist_directory: str | Path,
    collection_name: str,
    registry_path: str | Path = "data/evaluation/shared/source_registry.json",
    results_dir: str | Path = "results/agent_eval",
    expected_corpus_fingerprint: str = "",
    expected_registry_fingerprint: str = "",
    expected_source_count: int | None = None,
    expected_chunk_count: int | None = None,
) -> dict[str, Any]:
    absolute_persist_directory = _resolve_project_path(persist_directory, get_project_root())
    try:
        from eval.eval_agent import build_corpus_manifest, get_git_dirty, get_git_revision

        current_corpus = build_corpus_manifest(
            registry_path=Path(get_abs_path(str(registry_path))),
            persist_directory=absolute_persist_directory,
            collection_name=collection_name,
        )
        current_corpus["available"] = True
        current_corpus["active_profile_matches"] = matches_active_corpus_profile(
            current_corpus,
            expected_corpus_fingerprint=expected_corpus_fingerprint,
            expected_registry_fingerprint=expected_registry_fingerprint,
            expected_source_count=expected_source_count,
            expected_chunk_count=expected_chunk_count,
        )
        current_git_revision = get_git_revision()
        current_git_dirty = get_git_dirty()
    except Exception as exc:
        current_corpus = {
            "available": False,
            "persist_directory": str(absolute_persist_directory),
            "collection_name": collection_name,
            "error": f"{type(exc).__name__}: {exc}",
        }
        current_git_revision = ""
        current_git_dirty = None

    absolute_results_dir = get_abs_path(str(results_dir))
    latest_eval = load_latest_agent_eval(absolute_results_dir)
    try:
        from eval.release_gate import evaluate_agent_stability_gate

        stability_gate = evaluate_agent_stability_gate(absolute_results_dir)
    except Exception as exc:
        stability_gate = {
            "gate_pass": False,
            "failure_reasons": [f"{type(exc).__name__}: {exc}"],
        }
    return combine_runtime_observability(
        current_corpus=current_corpus,
        latest_eval=latest_eval,
        current_persist_directory=absolute_persist_directory,
        collection_name=collection_name,
        current_git_revision=current_git_revision,
        current_git_dirty=current_git_dirty,
        stability_gate=stability_gate,
    )
