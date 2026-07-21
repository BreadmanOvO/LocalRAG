from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from utils.path_tools import get_abs_path, get_project_root


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


@dataclass(frozen=True)
class AgentEvent:
    kind: str
    tool_name: str = ""
    call_id: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    content: str = ""
    status: str = ""
    elapsed_ms: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return deepcopy(asdict(self))


def tool_label(tool_name: str) -> str:
    return TOOL_LABELS.get(tool_name, tool_name or "未知工具")


def build_source_observations(
    retrieval_snapshot,
    *,
    confirmed_sources: tuple[str, ...] | list[str] = (),
) -> list[dict[str, Any]]:
    if retrieval_snapshot is None:
        return []

    confirmed = {str(source_id) for source_id in confirmed_sources}
    observations = []
    seen = set()
    for document in getattr(retrieval_snapshot, "documents", ()) or ():
        source_id = str(document.get("source_id") or "unknown")
        locator = str(document.get("locator") or "unknown")
        chunk_order = document.get("chunk_order")
        chunk_strategy = str(document.get("chunk_strategy") or "unknown")
        key = (source_id, locator, chunk_order, chunk_strategy)
        if key in seen:
            continue
        seen.add(key)

        content = " ".join(str(document.get("content") or "").split())
        summary = content[:240] + ("..." if len(content) > 240 else "")
        observations.append(
            {
                "source_id": source_id,
                "locator": locator,
                "chunk_order": chunk_order,
                "chunk_strategy": chunk_strategy,
                "rank": document.get("rank"),
                "score": document.get("score"),
                "summary": summary,
                "evidence_status": "confirmed" if source_id in confirmed else "retrieved",
            }
        )
    return observations


def diff_task_memory(before, after) -> list[dict[str, str]]:
    if before is None or after is None:
        return []

    changes = []
    if before.topic != after.topic:
        if before.topic:
            changes.append(
                {
                    "action": "removed",
                    "field": "topic",
                    "label": MEMORY_FIELD_LABELS["topic"],
                    "value": before.topic,
                }
            )
        if after.topic:
            changes.append(
                {
                    "action": "added",
                    "field": "topic",
                    "label": MEMORY_FIELD_LABELS["topic"],
                    "value": after.topic,
                }
            )

    for field_name in (
        "searched_queries",
        "retrieved_sources",
        "confirmed_sources",
        "findings",
        "evidence_gaps",
        "open_questions",
    ):
        before_values = tuple(getattr(before, field_name))
        after_values = tuple(getattr(after, field_name))
        for value in before_values:
            if value not in after_values:
                changes.append(
                    {
                        "action": "removed",
                        "field": field_name,
                        "label": MEMORY_FIELD_LABELS[field_name],
                        "value": value,
                    }
                )
        for value in after_values:
            if value not in before_values:
                changes.append(
                    {
                        "action": "added",
                        "field": field_name,
                        "label": MEMORY_FIELD_LABELS[field_name],
                        "value": value,
                    }
                )
    return changes


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


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
        candidates.append(
            (
                str(manifest.get("created_at") or ""),
                run_dir.name,
                manifest,
                summary,
            )
        )

    if not candidates:
        return {"available": False, "error": "未找到 Agent 评测产物"}

    _created_at, run_id, manifest, summary = max(candidates, key=lambda item: item[:2])
    return {
        "available": True,
        "run_id": run_id,
        "created_at": manifest.get("created_at", ""),
        "runtime": manifest.get("runtime", {}),
        "corpus": manifest.get("corpus", {}),
        "summary": summary,
    }


def _resolve_project_path(path_value: str | Path, project_root: str | Path) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        path = Path(project_root) / path
    return path.resolve()


def combine_runtime_observability(
    *,
    current_corpus: dict[str, Any],
    latest_eval: dict[str, Any],
    current_persist_directory: str | Path,
    collection_name: str,
    project_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(project_root or get_project_root()).resolve()
    current_available = bool(current_corpus.get("available", True))
    eval_available = bool(latest_eval.get("available"))
    corpus_matches_eval = False

    if current_available and eval_available:
        evaluated_corpus = latest_eval.get("corpus", {})
        evaluated_path = evaluated_corpus.get("persist_directory")
        if evaluated_path:
            corpus_matches_eval = (
                _resolve_project_path(current_persist_directory, root)
                == _resolve_project_path(evaluated_path, root)
                and str(evaluated_corpus.get("collection_name") or "") == collection_name
            )

    latest_gate_pass = bool(latest_eval.get("summary", {}).get("gate_pass"))
    effective_gate_pass = current_available and corpus_matches_eval and latest_gate_pass
    if not current_available:
        gate_status = "corpus_unavailable"
        message = current_corpus.get("error", "当前知识库状态不可用")
    elif not eval_available:
        gate_status = "eval_unavailable"
        message = latest_eval.get("error", "未找到 Agent 评测结果")
    elif not corpus_matches_eval:
        gate_status = "corpus_mismatch"
        message = "当前知识库与最近一次 Agent 评测使用的知识库不一致"
    elif not latest_gate_pass:
        gate_status = "gate_failed"
        message = "当前知识库最近一次 Agent gate 未通过"
    else:
        gate_status = "passed"
        message = "当前知识库已通过 Agent gate"

    return {
        "current_corpus": deepcopy(current_corpus),
        "latest_eval": deepcopy(latest_eval),
        "corpus_matches_eval": corpus_matches_eval,
        "gate_pass": effective_gate_pass,
        "gate_status": gate_status,
        "message": message,
    }


def load_runtime_observability(
    *,
    persist_directory: str | Path,
    collection_name: str,
    registry_path: str | Path = "data/evaluation/shared/source_registry.json",
    results_dir: str | Path = "results/agent_eval",
) -> dict[str, Any]:
    absolute_persist_directory = _resolve_project_path(persist_directory, get_project_root())
    try:
        from eval.eval_agent import build_corpus_manifest

        current_corpus = build_corpus_manifest(
            registry_path=Path(get_abs_path(str(registry_path))),
            persist_directory=absolute_persist_directory,
            collection_name=collection_name,
        )
        current_corpus["available"] = True
    except Exception as exc:
        current_corpus = {
            "available": False,
            "persist_directory": str(absolute_persist_directory),
            "collection_name": collection_name,
            "error": f"{type(exc).__name__}: {exc}",
        }

    latest_eval = load_latest_agent_eval(get_abs_path(str(results_dir)))
    return combine_runtime_observability(
        current_corpus=current_corpus,
        latest_eval=latest_eval,
        current_persist_directory=absolute_persist_directory,
        collection_name=collection_name,
    )
