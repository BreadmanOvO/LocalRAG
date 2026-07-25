from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid4

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings as config
from eval.agent_control_probes import run_control_probe
from eval.agent_eval_contract import (
    AGENT_EVAL_CONTRACT_VERSION,
    CONTROL_PROBE_NAMES,
    EVIDENCE_BINDING_CONTROL_PROBES,
    RESUME_CONTROL_PROBES,
)
from utils.path_tools import get_abs_path


CONTRACT_VERSION = AGENT_EVAL_CONTRACT_VERSION
DEFAULT_DATASET_PATH = Path("data/evaluation/agent/agent_eval_set.json")
DEFAULT_REGISTRY_PATH = Path("data/evaluation/shared/source_registry.json")
DEFAULT_OUT_DIR = Path("results/agent_eval")
DEFAULT_MIN_CORPUS_COVERAGE = 1.0
DEFAULT_MIN_CASE_PASS_RATIO = 1.0
DEFAULT_MIN_TOOL_CONTRACT_RATIO = 1.0
DEFAULT_MIN_ANSWER_CONTRACT_RATIO = 1.0
CHROMA_BATCH_SIZE = 500
EVAL_AGENT_TEMPERATURE = 0.0
EVAL_CASE_INFRASTRUCTURE_RETRIES = 1

KNOWN_TOOLS = {
    "rag_search",
    "show_sources",
    "inspect_source",
    "expand_context",
    "compare_sources",
    "evidence_check",
    "show_task_memory",
    "update_task_memory",
    "clarify_question",
}

_TOOL_TRACE_RE = re.compile(r"^\[工具\]\s+([A-Za-z0-9_.-]+)\s*$")
_TOOL_RESULT_RE = re.compile(
    r"^\[工具结果\]\s+([A-Za-z0-9_.-]+)\s+(已完成|失败)\s*$"
)
_AGENT_ERROR_RE = re.compile(r"^\[运行错误\]\s+([a-z_]+)\s*$")
RETRYABLE_CASE_ERRORS = {"model_request_failed"}
REQUIRED_CONTROL_PROBES = CONTROL_PROBE_NAMES
KNOWN_TERMINATION_CODES = frozenset(
    {
        "tool_call_limit_exceeded",
        "model_call_limit_exceeded",
        "duplicate_tool_call",
        "no_progress_limit",
        "graph_recursion_limit",
        "model_request_failed",
        "agent_execution_failed",
    }
)


def _require_non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _validate_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    result = []
    for index, item in enumerate(value):
        result.append(_require_non_empty_string(item, f"{field_name}[{index}]"))
    return result


def validate_agent_eval_dataset(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("agent eval dataset must be an object")
    dataset_version = _require_non_empty_string(
        payload.get("dataset_version"),
        "dataset_version",
    )
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")

    seen_case_ids = set()
    normalized_cases = []
    for case_index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"cases[{case_index}] must be an object")
        case_id = _require_non_empty_string(case.get("id"), f"cases[{case_index}].id")
        if case_id in seen_case_ids:
            raise ValueError(f"duplicate case id: {case_id}")
        seen_case_ids.add(case_id)
        category = _require_non_empty_string(
            case.get("category"),
            f"cases[{case_index}].category",
        )
        case_type = case.get("case_type", "conversation")
        if case_type not in {"conversation", "control_probe"}:
            raise ValueError(
                f"cases[{case_index}].case_type must be conversation or control_probe"
            )
        if case_type == "control_probe":
            probe = _require_non_empty_string(
                case.get("probe"),
                f"cases[{case_index}].probe",
            )
            if probe not in CONTROL_PROBE_NAMES:
                raise ValueError(f"cases[{case_index}] contains unknown control probe: {probe}")
            probe_turns = case.get("turns")
            if probe_turns is not None and probe_turns != []:
                raise ValueError(f"cases[{case_index}].turns must be empty for a control probe")
            normalized_cases.append(
                {
                    "id": case_id,
                    "category": category,
                    "case_type": case_type,
                    "probe": probe,
                    "turns": [],
                }
            )
            continue

        turns = case.get("turns")
        if not isinstance(turns, list) or not turns:
            raise ValueError(f"cases[{case_index}].turns must be a non-empty list")

        normalized_turns = []
        for turn_index, turn in enumerate(turns):
            prefix = f"cases[{case_index}].turns[{turn_index}]"
            if not isinstance(turn, dict):
                raise ValueError(f"{prefix} must be an object")
            prompt = _require_non_empty_string(turn.get("prompt"), f"{prefix}.prompt")
            required_tools = _validate_string_list(
                turn.get("required_tools", []),
                f"{prefix}.required_tools",
            )
            forbidden_tools = _validate_string_list(
                turn.get("forbidden_tools", []),
                f"{prefix}.forbidden_tools",
            )
            unknown_tools = (set(required_tools) | set(forbidden_tools)) - KNOWN_TOOLS
            if unknown_tools:
                raise ValueError(f"{prefix} contains unknown tools: {sorted(unknown_tools)}")
            overlap = set(required_tools) & set(forbidden_tools)
            if overlap:
                raise ValueError(f"{prefix} requires and forbids the same tools: {sorted(overlap)}")
            expected_source_ids = _validate_string_list(
                turn.get("expected_source_ids", []),
                f"{prefix}.expected_source_ids",
            )
            expected_terms = _validate_string_list(
                turn.get("expected_answer_terms_any", []),
                f"{prefix}.expected_answer_terms_any",
            )
            expected_terms_all = _validate_string_list(
                turn.get("expected_answer_terms_all", []),
                f"{prefix}.expected_answer_terms_all",
            )
            min_answer_chars = turn.get("min_answer_chars", 1)
            if isinstance(min_answer_chars, bool) or not isinstance(min_answer_chars, int):
                raise ValueError(f"{prefix}.min_answer_chars must be an integer")
            if not 1 <= min_answer_chars <= 10_000:
                raise ValueError(f"{prefix}.min_answer_chars must be between 1 and 10000")
            normalized_turns.append(
                {
                    "prompt": prompt,
                    "required_tools": required_tools,
                    "forbidden_tools": forbidden_tools,
                    "expected_source_ids": expected_source_ids,
                    "expected_answer_terms_any": expected_terms,
                    "expected_answer_terms_all": expected_terms_all,
                    "min_answer_chars": min_answer_chars,
                }
            )
        normalized_cases.append(
            {
                "id": case_id,
                "category": category,
                "case_type": case_type,
                "probe": "",
                "turns": normalized_turns,
            }
        )
    return {"dataset_version": dataset_version, "cases": normalized_cases}


def load_agent_eval_dataset(path: Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_agent_eval_dataset(payload)


def _load_registry_source_ids(path: Path) -> set[str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("source registry must contain a list")
    source_ids = set()
    for index, entry in enumerate(payload):
        if not isinstance(entry, dict):
            raise ValueError(f"source registry entry {index} must be an object")
        source_ids.add(
            _require_non_empty_string(entry.get("source_id"), f"registry[{index}].source_id")
        )
    return source_ids


def _canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def _json_file_fingerprint(path: Path) -> str:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return _sha256(_canonical_json_bytes(payload))


def get_git_revision(project_root: Path | None = None) -> str:
    root = Path(project_root or Path(__file__).resolve().parents[1])
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.stdout.strip()


def get_git_dirty(project_root: Path | None = None) -> bool | None:
    root = Path(project_root or Path(__file__).resolve().parents[1])
    try:
        result = subprocess.run(
            [
                "git",
                "status",
                "--porcelain",
                "--",
                ".",
                ":(exclude)results/**",
                ":(exclude)RAG_md/**",
            ],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return bool(result.stdout.strip())


def _open_collection(persist_directory: Path, collection_name: str):
    import chromadb

    client = chromadb.PersistentClient(path=str(Path(persist_directory).resolve()))
    return client, client.get_collection(collection_name)


def build_corpus_manifest(
    *,
    registry_path: Path,
    persist_directory: Path,
    collection_name: str,
    collection=None,
) -> dict[str, Any]:
    registry_source_ids = _load_registry_source_ids(registry_path)
    client = None
    if collection is None:
        client, collection = _open_collection(persist_directory, collection_name)

    source_ids = set()
    record_digests = []
    chunk_count = int(collection.count())
    offset = 0
    while offset < chunk_count:
        result = collection.get(
            include=["documents", "metadatas"],
            limit=CHROMA_BATCH_SIZE,
            offset=offset,
        )
        ids = result.get("ids") or []
        documents = result.get("documents") or []
        metadatas = result.get("metadatas") or []
        if not ids:
            break
        if len(ids) != len(documents) or len(ids) != len(metadatas):
            raise ValueError("Chroma corpus scan returned inconsistent record fields")
        for record_id, document, metadata in zip(ids, documents, metadatas):
            source_id = str((metadata or {}).get("source_id") or "").strip()
            if source_id:
                source_ids.add(source_id)
            record_digests.append(
                hashlib.sha256(
                    _canonical_json_bytes(
                        {
                            "id": str(record_id),
                            "document": document,
                            "metadata": metadata,
                        }
                    )
                ).hexdigest()
            )
        offset += len(ids)

    if len(record_digests) != chunk_count:
        raise ValueError(
            f"Chroma corpus scan expected {chunk_count} records, got {len(record_digests)}"
        )

    covered = registry_source_ids & source_ids
    coverage_ratio = round(len(covered) / len(registry_source_ids), 3) if registry_source_ids else 0.0
    manifest = {
        "persist_directory": str(Path(persist_directory)),
        "collection_name": collection_name,
        "registry_source_count": len(registry_source_ids),
        "chroma_source_count": len(source_ids),
        "covered_source_count": len(covered),
        "coverage_ratio": coverage_ratio,
        "chunk_count": chunk_count,
        "corpus_fingerprint": _sha256("\n".join(sorted(record_digests)).encode("ascii")),
        "registry_fingerprint": _json_file_fingerprint(registry_path),
        "missing_source_ids": sorted(registry_source_ids - source_ids),
        "extra_source_ids": sorted(source_ids - registry_source_ids),
    }
    del client
    return manifest


def parse_agent_stream(
    chunks: Iterable[str],
) -> tuple[list[str], list[str], str, str, list[str]]:
    tool_calls = []
    failed_tools = []
    execution_error = ""
    answer_parts = []
    raw_chunks = []
    for raw_chunk in chunks:
        chunk = str(raw_chunk)
        raw_chunks.append(chunk)
        stripped = chunk.strip()
        tool_match = _TOOL_TRACE_RE.fullmatch(stripped)
        if tool_match:
            tool_calls.append(tool_match.group(1))
            continue
        result_match = _TOOL_RESULT_RE.fullmatch(stripped)
        if result_match:
            if result_match.group(2) == "失败":
                failed_tools.append(result_match.group(1))
            continue
        error_match = _AGENT_ERROR_RE.fullmatch(stripped)
        if error_match:
            execution_error = error_match.group(1)
            continue
        answer_parts.append(chunk)
    return tool_calls, failed_tools, execution_error, "".join(answer_parts).strip(), raw_chunks


def _is_ordered_subsequence(expected: list[str], actual: list[str]) -> bool:
    if not expected:
        return True
    expected_index = 0
    for item in actual:
        if item == expected[expected_index]:
            expected_index += 1
            if expected_index == len(expected):
                return True
    return False


def evaluate_turn(
    turn: dict[str, Any],
    tool_calls: list[str],
    answer: str,
    failed_tools: list[str] | None = None,
) -> dict[str, Any]:
    required_tools = turn["required_tools"]
    forbidden_tools = turn["forbidden_tools"]
    expected_source_ids = turn["expected_source_ids"]
    expected_terms = turn["expected_answer_terms_any"]
    expected_terms_all = turn["expected_answer_terms_all"]
    failed_tools = failed_tools or []

    required_tools_pass = all(tool in tool_calls for tool in required_tools)
    tool_success_pass = not any(tool in failed_tools for tool in required_tools)
    tool_order_pass = _is_ordered_subsequence(required_tools, tool_calls)
    forbidden_tools_pass = not any(tool in tool_calls for tool in forbidden_tools)
    source_ids_pass = all(source_id in answer for source_id in expected_source_ids)
    answer_lower = answer.lower()
    answer_terms_pass = (
        (not expected_terms or any(term.lower() in answer_lower for term in expected_terms))
        and all(term.lower() in answer_lower for term in expected_terms_all)
    )
    answer_length_pass = len(answer) >= turn["min_answer_chars"]
    tool_contract_pass = (
        required_tools_pass and tool_success_pass and tool_order_pass and forbidden_tools_pass
    )
    answer_contract_pass = source_ids_pass and answer_terms_pass and answer_length_pass
    return {
        "required_tools_pass": required_tools_pass,
        "tool_success_pass": tool_success_pass,
        "tool_order_pass": tool_order_pass,
        "forbidden_tools_pass": forbidden_tools_pass,
        "source_ids_pass": source_ids_pass,
        "answer_terms_pass": answer_terms_pass,
        "answer_length_pass": answer_length_pass,
        "tool_contract_pass": tool_contract_pass,
        "answer_contract_pass": answer_contract_pass,
        "turn_pass": tool_contract_pass and answer_contract_pass,
    }


def _ratio(count: int, total: int) -> float:
    return round(count / total, 3) if total else 0.0


def _attempts_for_case(row: dict[str, Any]) -> list[dict[str, Any]]:
    attempts = row.get("attempts")
    if isinstance(attempts, list) and attempts:
        return [attempt for attempt in attempts if isinstance(attempt, dict)] or [row]
    return [row]


def _execution_diagnostics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    error_counts: Counter[str] = Counter()
    retryable_error_count = 0
    retry_case_count = 0
    total_attempt_count = 0
    for row in rows:
        row_error = str(row.get("error") or "")
        if row_error:
            error_counts[row_error] += 1
        attempts = _attempts_for_case(row)
        total_attempt_count += len(attempts)
        if len(attempts) > 1:
            retry_case_count += 1
        for attempt in attempts:
            for turn in attempt.get("turns", []):
                error = str(turn.get("error") or "")
                if not error:
                    continue
                error_counts[error] += 1
                if error in RETRYABLE_CASE_ERRORS:
                    retryable_error_count += 1
    return {
        "execution_error_count": sum(error_counts.values()),
        "execution_error_counts": dict(sorted(error_counts.items())),
        "retryable_error_count": retryable_error_count,
        "infrastructure_retry_count": sum(
            max(0, int(row.get("attempt_count", 1)) - 1) for row in rows
        ),
        "infrastructure_retry_case_count": retry_case_count,
        "total_attempt_count": total_attempt_count,
        "max_attempt_count": max(
            (int(row.get("attempt_count", 1)) for row in rows),
            default=0,
        ),
    }


def _case_contract_pass(row: dict[str, Any], contract: str) -> bool:
    if row.get("case_type") == "control_probe":
        evaluation = row.get("evaluation")
        return isinstance(evaluation, dict) and evaluation.get(contract) is True
    turns = row.get("turns")
    return isinstance(turns, list) and bool(turns) and all(
        isinstance(turn, dict)
        and isinstance(turn.get("evaluation"), dict)
        and turn["evaluation"].get(contract) is True
        for turn in turns
    )


def _metric_rows(
    rows: list[dict[str, Any]],
    metric: str,
) -> list[dict[str, Any]]:
    return [
        value
        for row in rows
        if isinstance((value := row.get(metric)), dict)
        and value.get("applicable") is True
    ]


def _termination_codes(rows: list[dict[str, Any]]) -> list[str]:
    codes = []
    for row in rows:
        termination = row.get("termination")
        if isinstance(termination, dict) and termination.get("applicable") is True:
            code = str(termination.get("observed_code") or "")
            if code:
                codes.append(code)
        row_error = str(row.get("error") or "")
        if row_error:
            codes.append(row_error)
        for attempt in _attempts_for_case(row):
            for turn in attempt.get("turns", []):
                error = str(turn.get("error") or "")
                if error:
                    codes.append(error)
    return codes


def summarize_agent_eval(
    rows: list[dict[str, Any]],
    *,
    corpus_manifest: dict[str, Any],
    min_corpus_coverage: float = DEFAULT_MIN_CORPUS_COVERAGE,
    min_case_pass_ratio: float = DEFAULT_MIN_CASE_PASS_RATIO,
    min_tool_contract_ratio: float = DEFAULT_MIN_TOOL_CONTRACT_RATIO,
    min_answer_contract_ratio: float = DEFAULT_MIN_ANSWER_CONTRACT_RATIO,
    expected_case_count: int | None = None,
    expected_turn_count: int | None = None,
    expected_probe_types: set[str] | frozenset[str] | None = None,
    skipped: bool = False,
) -> dict[str, Any]:
    turns = [turn for row in rows for turn in row.get("turns", [])]
    passed_cases = sum(1 for row in rows if row.get("case_pass"))
    case_tool_contract_count = sum(
        1 for row in rows if _case_contract_pass(row, "tool_contract_pass")
    )
    case_answer_contract_count = sum(
        1 for row in rows if _case_contract_pass(row, "answer_contract_pass")
    )
    turn_tool_contract_count = sum(
        1 for turn in turns if turn["evaluation"]["tool_contract_pass"]
    )
    turn_answer_contract_count = sum(
        1 for turn in turns if turn["evaluation"]["answer_contract_pass"]
    )
    forbidden_violation_count = sum(
        1 for turn in turns if not turn["evaluation"]["forbidden_tools_pass"]
    )
    case_pass_ratio = _ratio(passed_cases, len(rows))
    tool_contract_ratio = _ratio(case_tool_contract_count, len(rows))
    answer_contract_ratio = _ratio(case_answer_contract_count, len(rows))
    diagnostics = _execution_diagnostics(rows)
    expected_probe_types = frozenset(expected_probe_types or ())
    executed_probe_types = {
        str(row.get("probe"))
        for row in rows
        if row.get("case_type") == "control_probe" and row.get("probe")
    }
    termination_metrics = _metric_rows(rows, "termination")
    termination_codes = _termination_codes(rows)
    classified_termination_count = sum(
        1 for code in termination_codes if code in KNOWN_TERMINATION_CODES
    )
    unclassified_termination_count = len(termination_codes) - classified_termination_count
    graph_recursion_error_count = sum(
        1
        for code in termination_codes
        if "graph_recursion" in code.lower() or "graphrecursionerror" in code.lower()
    )
    termination_contract_pass_count = sum(
        1 for metric in termination_metrics if metric.get("contract_pass") is True
    )
    duplicate_metrics = _metric_rows(rows, "duplicate")
    duplicate_tool_violation_count = sum(
        1 for metric in duplicate_metrics if metric.get("violation") is True
    )
    evidence_metrics = _metric_rows(rows, "evidence_binding")
    verified_finding_count = sum(
        int(metric.get("verified_finding_count", 0)) for metric in evidence_metrics
    )
    bound_verified_finding_count = sum(
        int(metric.get("bound_verified_finding_count", 0))
        for metric in evidence_metrics
    )
    evidence_binding_required = bool(
        EVIDENCE_BINDING_CONTROL_PROBES & expected_probe_types
    )
    evidence_binding_ratio = (
        _ratio(bound_verified_finding_count, verified_finding_count)
        if verified_finding_count
        else 0.0 if evidence_binding_required else 1.0
    )
    resume_metrics = _metric_rows(rows, "resume")
    checkpoint_resume_pass_count = sum(
        1 for metric in resume_metrics if metric.get("checkpoint_resume_pass") is True
    )
    resume_required = bool(RESUME_CONTROL_PROBES & expected_probe_types)
    checkpoint_resume_ratio = (
        _ratio(checkpoint_resume_pass_count, len(resume_metrics))
        if resume_metrics
        else 0.0 if resume_required else 1.0
    )
    control_metrics = _metric_rows(rows, "control")
    expected_case_count = len(rows) if expected_case_count is None else expected_case_count
    expected_turn_count = len(turns) if expected_turn_count is None else expected_turn_count
    gate_checks = {
        "corpus_coverage": corpus_manifest["coverage_ratio"] >= min_corpus_coverage,
        "case_pass_ratio": case_pass_ratio >= min_case_pass_ratio,
        "tool_contract_ratio": tool_contract_ratio >= min_tool_contract_ratio,
        "answer_contract_ratio": answer_contract_ratio >= min_answer_contract_ratio,
        "forbidden_tool_violations": forbidden_violation_count == 0,
        "graph_recursion_errors": graph_recursion_error_count == 0,
        "classified_termination": unclassified_termination_count == 0,
        "termination_contracts": all(
            metric.get("contract_pass") is True for metric in termination_metrics
        ),
        "duplicate_tool_violations": (
            duplicate_tool_violation_count == 0
            and all(metric.get("contract_pass") is True for metric in duplicate_metrics)
        ),
        "verified_finding_evidence_binding": (
            evidence_binding_ratio == 1.0
            and (not evidence_binding_required or verified_finding_count > 0)
            and all(metric.get("contract_pass") is True for metric in evidence_metrics)
        ),
        "checkpoint_resume": (
            checkpoint_resume_ratio == 1.0
            and (not resume_required or bool(resume_metrics))
            and all(metric.get("contract_pass") is True for metric in resume_metrics)
        ),
        "control_contracts": all(
            metric.get("contract_pass") is True for metric in control_metrics
        ),
        "control_probe_coverage": expected_probe_types <= executed_probe_types,
        "evaluation_executed": not skipped and bool(rows),
        "evaluation_complete": (
            not skipped
            and len(rows) == expected_case_count
            and len(turns) == expected_turn_count
        ),
    }
    return {
        "case_count": len(rows),
        "expected_case_count": expected_case_count,
        "turn_count": len(turns),
        "expected_turn_count": expected_turn_count,
        "passed_case_count": passed_cases,
        "case_pass_ratio": case_pass_ratio,
        "tool_contract_pass_count": case_tool_contract_count,
        "tool_contract_pass_ratio": tool_contract_ratio,
        "answer_contract_pass_count": case_answer_contract_count,
        "answer_contract_pass_ratio": answer_contract_ratio,
        "case_tool_contract_pass_count": case_tool_contract_count,
        "case_answer_contract_pass_count": case_answer_contract_count,
        "turn_tool_contract_pass_count": turn_tool_contract_count,
        "turn_tool_contract_pass_ratio": _ratio(turn_tool_contract_count, len(turns)),
        "turn_answer_contract_pass_count": turn_answer_contract_count,
        "turn_answer_contract_pass_ratio": _ratio(turn_answer_contract_count, len(turns)),
        "forbidden_tool_violation_count": forbidden_violation_count,
        "termination_case_count": len(termination_metrics),
        "termination_contract_pass_count": termination_contract_pass_count,
        "classified_termination_count": classified_termination_count,
        "unclassified_termination_count": unclassified_termination_count,
        "graph_recursion_error_count": graph_recursion_error_count,
        "duplicate_probe_case_count": len(duplicate_metrics),
        "duplicate_tool_violation_count": duplicate_tool_violation_count,
        "evidence_binding_case_count": len(evidence_metrics),
        "verified_finding_count": verified_finding_count,
        "bound_verified_finding_count": bound_verified_finding_count,
        "verified_finding_evidence_binding_ratio": evidence_binding_ratio,
        "checkpoint_resume_case_count": len(resume_metrics),
        "checkpoint_resume_pass_count": checkpoint_resume_pass_count,
        "checkpoint_resume_pass_ratio": checkpoint_resume_ratio,
        "expected_probe_types": sorted(expected_probe_types),
        "executed_probe_types": sorted(executed_probe_types),
        "corpus_coverage_ratio": corpus_manifest["coverage_ratio"],
        **diagnostics,
        "skipped": skipped,
        "gate_thresholds": {
            "min_corpus_coverage": min_corpus_coverage,
            "min_case_pass_ratio": min_case_pass_ratio,
            "min_tool_contract_ratio": min_tool_contract_ratio,
            "min_answer_contract_ratio": min_answer_contract_ratio,
        },
        "gate_checks": gate_checks,
        "gate_pass": all(gate_checks.values()),
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _default_agent_factory(
    session_id: str,
    task_id: str,
    task_memory_store,
    *,
    rag_service=None,
    evidence_service=None,
    chat_model=None,
    execution_budget=None,
    recursion_limit: int | None = None,
):
    from agent import ReactAgent

    options = {}
    if execution_budget is not None:
        options["execution_budget"] = execution_budget
    elif recursion_limit is not None:
        options["recursion_limit"] = recursion_limit
    return ReactAgent(
        session_id=session_id,
        task_id=task_id,
        task_memory_store=task_memory_store,
        task_memory_enabled=False,
        rag_service=rag_service,
        evidence_service=evidence_service,
        chat_model=chat_model,
        **options,
    )


def run_agent_eval(
    *,
    dataset_path: Path,
    registry_path: Path,
    persist_directory: Path,
    out_dir: Path,
    collection_name: str = "rag",
    allow_stale_corpus: bool = False,
    max_cases: int | None = None,
    case_ids: list[str] | None = None,
    run_id: str | None = None,
    agent_factory: Callable[[str, str, Any], Any] | None = None,
    collection=None,
    progress_callback: Callable[[int, int, str, bool], None] | None = None,
    case_infrastructure_retries: int | None = None,
) -> dict[str, Any]:
    dataset = load_agent_eval_dataset(dataset_path)
    if case_ids:
        requested_case_ids = set(case_ids)
        available_case_ids = {case["id"] for case in dataset["cases"]}
        unknown_case_ids = requested_case_ids - available_case_ids
        if unknown_case_ids:
            raise ValueError(f"unknown case ids: {sorted(unknown_case_ids)}")
        selected_cases = [case for case in dataset["cases"] if case["id"] in requested_case_ids]
    else:
        selected_cases = dataset["cases"]
    if max_cases is not None and max_cases <= 0:
        raise ValueError("max_cases must be greater than zero")
    if case_infrastructure_retries is not None and case_infrastructure_retries < 0:
        raise ValueError("case_infrastructure_retries must not be negative")
    cases = selected_cases[:max_cases] if max_cases is not None else selected_cases
    expected_case_count = len(dataset["cases"])
    expected_turn_count = sum(len(case["turns"]) for case in dataset["cases"])
    expected_probe_types = {
        case["probe"]
        for case in dataset["cases"]
        if case["case_type"] == "control_probe"
    }
    selected_turn_count = sum(len(case["turns"]) for case in cases)
    selected_case_ids = [case["id"] for case in cases]
    selected_probe_types = {
        case["probe"] for case in cases if case["case_type"] == "control_probe"
    }
    selection_complete = len(cases) == expected_case_count
    run_id = run_id or f"agent-eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    run_dir = Path(out_dir) / run_id
    corpus_manifest = build_corpus_manifest(
        registry_path=registry_path,
        persist_directory=persist_directory,
        collection_name=collection_name,
        collection=collection,
    )
    corpus_ready = corpus_manifest["coverage_ratio"] >= DEFAULT_MIN_CORPUS_COVERAGE
    rows = []
    git_revision = get_git_revision()
    git_dirty = get_git_dirty()

    from agent.research import ResearchExecutionIdentity

    probe_identity = ResearchExecutionIdentity(
        corpus_fingerprint=corpus_manifest["corpus_fingerprint"],
        registry_fingerprint=corpus_manifest["registry_fingerprint"],
        code_revision=git_revision or CONTRACT_VERSION,
        code_dirty=False,
    )

    runtime = {"provider": "injected", "chat_model_name": "injected"}
    execution = {
        "mode": "injected",
        "agent_temperature": None,
        "request_timeout_seconds": None,
        "max_retries": None,
        "middleware": None,
        "tool_call_run_limit": None,
        "model_call_run_limit": None,
        "duplicate_tool_call_detection": None,
        "no_progress_limit": None,
        "limit_exit_behavior": None,
        "recursion_limit": None,
        "case_infrastructure_retries": case_infrastructure_retries or 0,
    }
    execution_budget = None
    runtime_config = None
    if agent_factory is None:
        from agent.execution import DEFAULT_AGENT_EXECUTION_BUDGET
        from config.provider_factory import (
            DEFAULT_CHAT_MAX_RETRIES,
            DEFAULT_CHAT_TIMEOUT_SECONDS,
        )
        from config.runtime_keys import load_runtime_config

        execution_budget = DEFAULT_AGENT_EXECUTION_BUDGET
        runtime_config = load_runtime_config()
        runtime = {
            "provider": runtime_config.provider,
            "chat_model_name": runtime_config.chat_model_name,
            "embedding_model_name": runtime_config.embedding_model_name,
        }
        execution = {
            "mode": "formal",
            "agent_temperature": EVAL_AGENT_TEMPERATURE,
            "request_timeout_seconds": DEFAULT_CHAT_TIMEOUT_SECONDS,
            "max_retries": DEFAULT_CHAT_MAX_RETRIES,
            **execution_budget.to_manifest(),
            "case_infrastructure_retries": (
                EVAL_CASE_INFRASTRUCTURE_RETRIES
                if case_infrastructure_retries is None
                else case_infrastructure_retries
            ),
        }

    previous_persist_directory = config.persist_directory
    try:
        config.persist_directory = str(Path(persist_directory).resolve())
        if corpus_ready or allow_stale_corpus:
            if agent_factory is None:
                from config.provider_factory import build_chat_model
                from core.rag import RagService
                from core.source_evidence import SourceEvidenceService

                shared_chat_model = build_chat_model(
                    runtime_config,
                    temperature=EVAL_AGENT_TEMPERATURE,
                )
                shared_rag_service = RagService(chat_model=shared_chat_model)
                shared_evidence_service = SourceEvidenceService()

                def factory(session_id, task_id, task_memory_store):
                    return _default_agent_factory(
                        session_id,
                        task_id,
                        task_memory_store,
                        rag_service=shared_rag_service,
                        evidence_service=shared_evidence_service,
                        chat_model=shared_chat_model,
                        execution_budget=execution_budget,
                    )
            else:
                factory = agent_factory
            temp_context = tempfile.TemporaryDirectory()
            with temp_context as temp_dir:
                task_memory_store = None
                if agent_factory is None:
                    from agent.memory import TaskMemoryStore

                    task_memory_store = TaskMemoryStore(Path(temp_dir) / "task-memory.sqlite3")
                for case_index, case in enumerate(cases, start=1):
                    if case["case_type"] == "control_probe":
                        probe_result = run_control_probe(
                            case["probe"],
                            probe_identity,
                            Path(temp_dir) / f"probe-{case_index:03d}",
                        )
                        case_row = {
                            "id": case["id"],
                            "category": case["category"],
                            "case_type": case["case_type"],
                            **probe_result,
                        }
                        rows.append(case_row)
                        if progress_callback is not None:
                            progress_callback(
                                case_index,
                                len(cases),
                                case["id"],
                                case_row["case_pass"],
                            )
                        continue

                    attempt_count = 0
                    max_attempts = 1 + execution["case_infrastructure_retries"]
                    attempt_history = []
                    while True:
                        attempt_count += 1
                        session_id = f"agent-eval-{uuid4().hex}"
                        task_id = f"agent-eval-{uuid4().hex}"
                        agent = None
                        agent_error = ""
                        try:
                            agent = factory(session_id, task_id, task_memory_store)
                        except Exception as exc:
                            agent_error = f"{type(exc).__name__}: {exc}"
                        turn_rows = []
                        for turn_index, turn in enumerate(case["turns"], start=1):
                            started = time.perf_counter()
                            error = agent_error
                            if agent is None:
                                tool_calls, failed_tools, answer, raw_chunks = [], [], "", []
                            else:
                                try:
                                    (
                                        tool_calls,
                                        failed_tools,
                                        execution_error,
                                        answer,
                                        raw_chunks,
                                    ) = parse_agent_stream(agent.execute_stream(turn["prompt"]))
                                    if execution_error:
                                        error = execution_error
                                except Exception as exc:
                                    tool_calls, failed_tools, answer, raw_chunks = [], [], "", []
                                    error = f"{type(exc).__name__}: {exc}"
                            evaluation = evaluate_turn(
                                turn,
                                tool_calls,
                                answer,
                                failed_tools=failed_tools,
                            )
                            if error:
                                evaluation["turn_pass"] = False
                                evaluation["answer_contract_pass"] = False
                            turn_rows.append(
                                {
                                    "turn_index": turn_index,
                                    "prompt": turn["prompt"],
                                    "expected": {
                                        key: turn[key]
                                        for key in (
                                            "required_tools",
                                            "forbidden_tools",
                                            "expected_source_ids",
                                            "expected_answer_terms_any",
                                            "expected_answer_terms_all",
                                            "min_answer_chars",
                                        )
                                    },
                                    "tool_calls": tool_calls,
                                    "failed_tools": failed_tools,
                                    "answer": answer,
                                    "raw_stream": raw_chunks,
                                    "elapsed_seconds": round(
                                        time.perf_counter() - started,
                                        3,
                                    ),
                                    "error": error,
                                    "evaluation": evaluation,
                                }
                            )
                        infrastructure_failed = any(
                            turn["error"] in RETRYABLE_CASE_ERRORS for turn in turn_rows
                        )
                        attempt_history.append(
                            {
                                "attempt": attempt_count,
                                "turns": turn_rows,
                                "case_pass": all(
                                    turn["evaluation"]["turn_pass"] for turn in turn_rows
                                ),
                                "retryable_errors": sorted(
                                    {
                                        turn["error"]
                                        for turn in turn_rows
                                        if turn["error"] in RETRYABLE_CASE_ERRORS
                                    }
                                ),
                            }
                        )
                        if not infrastructure_failed or attempt_count >= max_attempts:
                            break
                    case_row = {
                        "id": case["id"],
                        "category": case["category"],
                        "case_type": case["case_type"],
                        "turns": turn_rows,
                        "attempts": attempt_history,
                        "case_pass": all(
                            turn["evaluation"]["turn_pass"] for turn in turn_rows
                        ),
                        "attempt_count": attempt_count,
                        "infrastructure_retry_count": attempt_count - 1,
                    }
                    case_row["evaluation"] = {
                        "tool_contract_pass": all(
                            turn["evaluation"]["tool_contract_pass"]
                            for turn in turn_rows
                        ),
                        "answer_contract_pass": all(
                            turn["evaluation"]["answer_contract_pass"]
                            for turn in turn_rows
                        ),
                    }
                    rows.append(case_row)
                    if progress_callback is not None:
                        progress_callback(
                            case_index,
                            len(cases),
                            case["id"],
                            case_row["case_pass"],
                        )
    finally:
        config.persist_directory = previous_persist_directory

    skipped = not rows
    summary = summarize_agent_eval(
        rows,
        corpus_manifest=corpus_manifest,
        expected_case_count=expected_case_count,
        expected_turn_count=expected_turn_count,
        expected_probe_types=expected_probe_types,
        skipped=skipped,
    )

    manifest = {
        "contract_version": CONTRACT_VERSION,
        "pipeline": "agent_eval",
        "run_id": run_id,
        "dataset_path": str(Path(dataset_path)),
        "dataset_version": dataset["dataset_version"],
        "registry_path": str(Path(registry_path)),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runner_script": "eval/eval_agent.py",
        "git_revision": git_revision,
        "git_dirty": git_dirty,
        "runtime": runtime,
        "execution": execution,
        "allow_stale_corpus": allow_stale_corpus,
        "max_cases": max_cases,
        "case_ids": case_ids,
        "evaluation_scope": {
            "expected_case_count": expected_case_count,
            "expected_turn_count": expected_turn_count,
            "selected_case_count": len(cases),
            "selected_turn_count": selected_turn_count,
            "executed_case_count": len(rows),
            "executed_turn_count": sum(len(row["turns"]) for row in rows),
            "selected_case_ids": selected_case_ids,
            "expected_probe_types": sorted(expected_probe_types),
            "selected_probe_types": sorted(selected_probe_types),
            "executed_probe_types": sorted(
                str(row.get("probe"))
                for row in rows
                if row.get("case_type") == "control_probe" and row.get("probe")
            ),
            "probe_selection_complete": expected_probe_types <= selected_probe_types,
            "selection_complete": selection_complete,
            "evaluation_complete": summary["gate_checks"]["evaluation_complete"],
        },
        "corpus": corpus_manifest,
    }
    write_json(run_dir / "manifest.json", manifest)
    write_json(run_dir / "predictions.json", rows)
    write_json(run_dir / "summary.json", summary)
    return {
        "run_dir": run_dir,
        "manifest": manifest,
        "predictions": rows,
        "summary": summary,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the v1.5 controlled Agent evaluation.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument(
        "--chroma-path",
        type=Path,
        default=Path(get_abs_path(config.persist_directory)),
    )
    parser.add_argument("--collection", default=config.collection_name)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--allow-stale-corpus", action="store_true")
    parser.add_argument("--max-cases", type=int, default=None)
    parser.add_argument("--case-id", action="append", dest="case_ids", default=None)
    return parser


def main() -> dict[str, Any]:
    args = build_parser().parse_args()

    def report_progress(index: int, total: int, case_id: str, passed: bool) -> None:
        status = "PASS" if passed else "FAIL"
        print(f"[{index}/{total}] {status}: {case_id}", flush=True)

    result = run_agent_eval(
        dataset_path=args.dataset,
        registry_path=args.registry,
        persist_directory=args.chroma_path,
        out_dir=args.out_dir,
        collection_name=args.collection,
        allow_stale_corpus=args.allow_stale_corpus,
        max_cases=args.max_cases,
        case_ids=args.case_ids,
        progress_callback=report_progress,
    )
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"run_dir={result['run_dir']}")
    return result


if __name__ == "__main__":
    run_result = main()
    raise SystemExit(0 if run_result["summary"]["gate_pass"] else 1)
