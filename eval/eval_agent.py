from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
import time
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable
from uuid import uuid4

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings as config
from utils.path_tools import get_abs_path


CONTRACT_VERSION = "agent-eval-v1"
DEFAULT_DATASET_PATH = Path("data/evaluation/agent/agent_eval_set.json")
DEFAULT_REGISTRY_PATH = Path("data/evaluation/shared/source_registry.json")
DEFAULT_OUT_DIR = Path("results/agent_eval")
DEFAULT_MIN_CORPUS_COVERAGE = 1.0
DEFAULT_MIN_CASE_PASS_RATIO = 0.8
DEFAULT_MIN_TOOL_CONTRACT_RATIO = 0.9
DEFAULT_MIN_ANSWER_CONTRACT_RATIO = 0.8
CHROMA_BATCH_SIZE = 500

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
_TOOL_RESULT_RE = re.compile(r"^\[工具结果\]\s+([A-Za-z0-9_.-]+)\s+已完成\s*$")


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
    chunk_count = int(collection.count())
    offset = 0
    while offset < chunk_count:
        result = collection.get(
            include=["metadatas"],
            limit=CHROMA_BATCH_SIZE,
            offset=offset,
        )
        metadatas = result.get("metadatas") or []
        for metadata in metadatas:
            source_id = str((metadata or {}).get("source_id") or "").strip()
            if source_id:
                source_ids.add(source_id)
        if not metadatas:
            break
        offset += len(metadatas)

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
        "missing_source_ids": sorted(registry_source_ids - source_ids),
        "extra_source_ids": sorted(source_ids - registry_source_ids),
    }
    del client
    return manifest


def parse_agent_stream(chunks: Iterable[str]) -> tuple[list[str], str, list[str]]:
    tool_calls = []
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
        if _TOOL_RESULT_RE.fullmatch(stripped):
            continue
        answer_parts.append(chunk)
    return tool_calls, "".join(answer_parts).strip(), raw_chunks


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


def evaluate_turn(turn: dict[str, Any], tool_calls: list[str], answer: str) -> dict[str, Any]:
    required_tools = turn["required_tools"]
    forbidden_tools = turn["forbidden_tools"]
    expected_source_ids = turn["expected_source_ids"]
    expected_terms = turn["expected_answer_terms_any"]
    expected_terms_all = turn["expected_answer_terms_all"]

    required_tools_pass = all(tool in tool_calls for tool in required_tools)
    tool_order_pass = _is_ordered_subsequence(required_tools, tool_calls)
    forbidden_tools_pass = not any(tool in tool_calls for tool in forbidden_tools)
    source_ids_pass = all(source_id in answer for source_id in expected_source_ids)
    answer_lower = answer.lower()
    answer_terms_pass = (
        (not expected_terms or any(term.lower() in answer_lower for term in expected_terms))
        and all(term.lower() in answer_lower for term in expected_terms_all)
    )
    answer_length_pass = len(answer) >= turn["min_answer_chars"]
    tool_contract_pass = required_tools_pass and tool_order_pass and forbidden_tools_pass
    answer_contract_pass = source_ids_pass and answer_terms_pass and answer_length_pass
    return {
        "required_tools_pass": required_tools_pass,
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


def summarize_agent_eval(
    rows: list[dict[str, Any]],
    *,
    corpus_manifest: dict[str, Any],
    min_corpus_coverage: float = DEFAULT_MIN_CORPUS_COVERAGE,
    min_case_pass_ratio: float = DEFAULT_MIN_CASE_PASS_RATIO,
    min_tool_contract_ratio: float = DEFAULT_MIN_TOOL_CONTRACT_RATIO,
    min_answer_contract_ratio: float = DEFAULT_MIN_ANSWER_CONTRACT_RATIO,
    skipped: bool = False,
) -> dict[str, Any]:
    turns = [turn for row in rows for turn in row.get("turns", [])]
    passed_cases = sum(1 for row in rows if row.get("case_pass"))
    tool_contract_count = sum(1 for turn in turns if turn["evaluation"]["tool_contract_pass"])
    answer_contract_count = sum(1 for turn in turns if turn["evaluation"]["answer_contract_pass"])
    forbidden_violation_count = sum(
        1 for turn in turns if not turn["evaluation"]["forbidden_tools_pass"]
    )
    case_pass_ratio = _ratio(passed_cases, len(rows))
    tool_contract_ratio = _ratio(tool_contract_count, len(turns))
    answer_contract_ratio = _ratio(answer_contract_count, len(turns))
    gate_checks = {
        "corpus_coverage": corpus_manifest["coverage_ratio"] >= min_corpus_coverage,
        "case_pass_ratio": case_pass_ratio >= min_case_pass_ratio,
        "tool_contract_ratio": tool_contract_ratio >= min_tool_contract_ratio,
        "answer_contract_ratio": answer_contract_ratio >= min_answer_contract_ratio,
        "forbidden_tool_violations": forbidden_violation_count == 0,
        "evaluation_executed": not skipped and bool(rows),
    }
    return {
        "case_count": len(rows),
        "turn_count": len(turns),
        "passed_case_count": passed_cases,
        "case_pass_ratio": case_pass_ratio,
        "tool_contract_pass_count": tool_contract_count,
        "tool_contract_pass_ratio": tool_contract_ratio,
        "answer_contract_pass_count": answer_contract_count,
        "answer_contract_pass_ratio": answer_contract_ratio,
        "forbidden_tool_violation_count": forbidden_violation_count,
        "corpus_coverage_ratio": corpus_manifest["coverage_ratio"],
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


def _default_agent_factory(session_id: str, task_id: str, task_memory_store):
    from agent import ReactAgent

    return ReactAgent(
        session_id=session_id,
        task_id=task_id,
        task_memory_store=task_memory_store,
        task_memory_enabled=False,
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
    cases = selected_cases[:max_cases] if max_cases is not None else selected_cases
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

    previous_persist_directory = config.persist_directory
    try:
        config.persist_directory = str(Path(persist_directory).resolve())
        if corpus_ready or allow_stale_corpus:
            factory = agent_factory or _default_agent_factory
            temp_context = (
                tempfile.TemporaryDirectory() if agent_factory is None else nullcontext(None)
            )
            with temp_context as temp_dir:
                task_memory_store = None
                if temp_dir is not None:
                    from agent.memory import TaskMemoryStore

                    task_memory_store = TaskMemoryStore(Path(temp_dir) / "task-memory.sqlite3")
                for case in cases:
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
                            tool_calls, answer, raw_chunks = [], "", []
                        else:
                            try:
                                tool_calls, answer, raw_chunks = parse_agent_stream(
                                    agent.execute_stream(turn["prompt"])
                                )
                            except Exception as exc:
                                tool_calls, answer, raw_chunks = [], "", []
                                error = f"{type(exc).__name__}: {exc}"
                        evaluation = evaluate_turn(turn, tool_calls, answer)
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
                                "answer": answer,
                                "raw_stream": raw_chunks,
                                "elapsed_seconds": round(time.perf_counter() - started, 3),
                                "error": error,
                                "evaluation": evaluation,
                            }
                        )
                    rows.append(
                        {
                            "id": case["id"],
                            "category": case["category"],
                            "turns": turn_rows,
                            "case_pass": all(turn["evaluation"]["turn_pass"] for turn in turn_rows),
                        }
                    )
    finally:
        config.persist_directory = previous_persist_directory

    skipped = not rows
    summary = summarize_agent_eval(
        rows,
        corpus_manifest=corpus_manifest,
        skipped=skipped,
    )

    runtime = {"provider": "injected", "chat_model_name": "injected"}
    if agent_factory is None:
        from config.runtime_keys import load_runtime_config

        runtime_config = load_runtime_config()
        runtime = {
            "provider": runtime_config.provider,
            "chat_model_name": runtime_config.chat_model_name,
            "embedding_model_name": runtime_config.embedding_model_name,
        }

    manifest = {
        "contract_version": CONTRACT_VERSION,
        "pipeline": "agent_eval",
        "run_id": run_id,
        "dataset_path": str(Path(dataset_path)),
        "dataset_version": dataset["dataset_version"],
        "registry_path": str(Path(registry_path)),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runner_script": "eval/eval_agent.py",
        "runtime": runtime,
        "allow_stale_corpus": allow_stale_corpus,
        "max_cases": max_cases,
        "case_ids": case_ids,
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
    parser = argparse.ArgumentParser(description="Run the v1.4 Agent behavior evaluation.")
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
    result = run_agent_eval(
        dataset_path=args.dataset,
        registry_path=args.registry,
        persist_directory=args.chroma_path,
        out_dir=args.out_dir,
        collection_name=args.collection,
        allow_stale_corpus=args.allow_stale_corpus,
        max_cases=args.max_cases,
        case_ids=args.case_ids,
    )
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"run_dir={result['run_dir']}")
    return result


if __name__ == "__main__":
    run_result = main()
    raise SystemExit(0 if run_result["summary"]["gate_pass"] else 1)
