import argparse
import json
import shutil
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import config_data as config
from eval.eval_ragas import build_session_id, load_dataset, write_json
from knowledge_base import KnowledgeBaseService
from rag import RagService
from runtime_keys import load_bailian_runtime_config

REGISTRY_PATH = Path("data/evaluation/shared/source_registry.json")
STRATEGY_BASELINE = "baseline"
STRATEGY_DOC_TYPE_AWARE = "doc_type_aware"


def _empty_summary() -> dict[str, Any]:
    return {
        "sample_count": 0,
        "answered_count": 0,
        "answered_ratio": 0.0,
        "retrieved_row_count": 0,
        "evidence_source_hit_count": 0,
        "evidence_source_hit_ratio": 0.0,
        "evidence_locator_hit_count": 0,
        "evidence_locator_hit_ratio": 0.0,
    }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_source_registry(path: Path = REGISTRY_PATH) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def use_store_path(store_path: Path):
    original_persist_directory = config.persist_directory
    store_path.mkdir(parents=True, exist_ok=True)
    config.persist_directory = str(store_path)
    try:
        yield
    finally:
        config.persist_directory = original_persist_directory



def _build_source_metadata(entry: dict[str, Any]) -> dict[str, str]:
    return {
        "source": entry["path_or_url"],
        "source_id": entry["source_id"],
        "doc_type": entry["doc_type"],
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "operator": config.uploader,
    }


def _normalize_locator(locator: str | None) -> str:
    if not locator:
        return ""
    return " ".join(locator.strip().split())


def summarize_chunking_predictions(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    sample_count = len(predictions)
    answered_count = sum(1 for row in predictions if row.get("answer", "").strip())
    retrieved_row_count = sum(len(row.get("retrieved_rows", [])) for row in predictions)
    evidence_source_hit_count = 0
    evidence_locator_hit_count = 0

    for row in predictions:
        retrieved_rows = row.get("retrieved_rows", [])
        retrieved_sources = {item.get("source_id", "") for item in retrieved_rows}
        retrieved_locators = {_normalize_locator(item.get("locator", "")) for item in retrieved_rows}
        evidence = row.get("evidence", [])
        if any(item.get("source_id", "") in retrieved_sources for item in evidence):
            evidence_source_hit_count += 1
        if any(_normalize_locator(item.get("locator", "")) in retrieved_locators for item in evidence):
            evidence_locator_hit_count += 1

    summary = _empty_summary()
    summary.update(
        {
            "sample_count": sample_count,
            "answered_count": answered_count,
            "answered_ratio": round(answered_count / sample_count, 3) if sample_count else 0.0,
            "retrieved_row_count": retrieved_row_count,
            "evidence_source_hit_count": evidence_source_hit_count,
            "evidence_source_hit_ratio": round(evidence_source_hit_count / sample_count, 3) if sample_count else 0.0,
            "evidence_locator_hit_count": evidence_locator_hit_count,
            "evidence_locator_hit_ratio": round(evidence_locator_hit_count / sample_count, 3) if sample_count else 0.0,
        }
    )
    return summary


def _group_prediction_stats(predictions: list[dict[str, Any]], group_by: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in predictions:
        if group_by == "doc_type":
            key = row.get("metadata", {}).get("doc_type", "unknown")
        else:
            evidence = row.get("evidence", [])
            key = evidence[0].get("source_id", "unknown") if evidence else "unknown"
        grouped[key].append(row)
    return {key: summarize_chunking_predictions(rows) for key, rows in grouped.items()}


def _index_predictions(predictions: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in predictions}



def _build_error_case(baseline_row: dict[str, Any], candidate_row: dict[str, Any]) -> dict[str, Any] | None:
    baseline_sources = {item.get("source_id", "") for item in baseline_row.get("retrieved_rows", [])}
    candidate_sources = {item.get("source_id", "") for item in candidate_row.get("retrieved_rows", [])}
    baseline_locators = {_normalize_locator(item.get("locator", "")) for item in baseline_row.get("retrieved_rows", [])}
    candidate_locators = {_normalize_locator(item.get("locator", "")) for item in candidate_row.get("retrieved_rows", [])}
    evidence = baseline_row.get("evidence", [])
    evidence_sources = {item.get("source_id", "") for item in evidence}
    evidence_locators = {_normalize_locator(item.get("locator", "")) for item in evidence}
    baseline_hit = bool(evidence_sources & baseline_sources)
    candidate_hit = bool(evidence_sources & candidate_sources)
    baseline_locator_hit = bool(evidence_locators & baseline_locators)
    candidate_locator_hit = bool(evidence_locators & candidate_locators)

    if (
        baseline_row.get("answer", "").strip()
        and candidate_row.get("answer", "").strip()
        and baseline_hit == candidate_hit
        and baseline_locator_hit == candidate_locator_hit
    ):
        return None

    return {
        "id": baseline_row["id"],
        "question": baseline_row["question"],
        "baseline_answered": bool(baseline_row.get("answer", "").strip()),
        "doc_type_aware_answered": bool(candidate_row.get("answer", "").strip()),
        "baseline_source_hit": baseline_hit,
        "doc_type_aware_source_hit": candidate_hit,
        "baseline_locator_hit": baseline_locator_hit,
        "doc_type_aware_locator_hit": candidate_locator_hit,
    }



def _build_error_cases(baseline_predictions: list[dict[str, Any]], candidate_predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    baseline_by_id = _index_predictions(baseline_predictions)
    candidate_by_id = _index_predictions(candidate_predictions)
    if set(baseline_by_id) != set(candidate_by_id):
        raise ValueError("baseline and candidate predictions must contain the same sample ids")

    rows = []
    for sample_id in sorted(baseline_by_id):
        error_case = _build_error_case(baseline_by_id[sample_id], candidate_by_id[sample_id])
        if error_case is not None:
            rows.append(error_case)
    return rows


def build_comparison_artifacts(
    baseline_predictions: list[dict[str, Any]],
    candidate_predictions: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
    candidate_metrics: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    return {
        "summary": {
            "run_id": run_id,
            STRATEGY_BASELINE: baseline_metrics,
            STRATEGY_DOC_TYPE_AWARE: candidate_metrics,
        },
        "by_doc_type": {
            STRATEGY_BASELINE: _group_prediction_stats(baseline_predictions, "doc_type"),
            STRATEGY_DOC_TYPE_AWARE: _group_prediction_stats(candidate_predictions, "doc_type"),
        },
        "by_source_id": {
            STRATEGY_BASELINE: _group_prediction_stats(baseline_predictions, "source_id"),
            STRATEGY_DOC_TYPE_AWARE: _group_prediction_stats(candidate_predictions, "source_id"),
        },
        "error_cases": _build_error_cases(baseline_predictions, candidate_predictions),
    }


def _build_prediction_record(sample: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": sample["id"],
        "question": sample["question"],
        "reference_answer": sample["reference_answer"],
        "answer": result["answer"],
        "retrieved_context": result["retrieved_context"],
        "retrieved_rows": result["retrieved_rows"],
        "retrieval_debug_candidates": result["retrieval_debug_candidates"],
        "evidence": sample.get("evidence", []),
        "metadata": sample.get("metadata", {}),
    }


def _strategy_dir(run_dir: Path, strategy: str) -> Path:
    return run_dir / strategy


def render_chunking_report(
    *,
    run_id: str,
    dataset_path: Path,
    baseline_store_path: Path,
    candidate_store_path: Path,
    comparison: dict[str, Any],
) -> str:
    lines = [
        f"# Chunking evaluation report: {run_id}",
        "",
        "## Run metadata",
        f"- Dataset: {dataset_path}",
        f"- Baseline store: {baseline_store_path}",
        f"- Doc-type-aware store: {candidate_store_path}",
        "",
        "## Overall summary",
        f"- baseline answered ratio: {comparison['summary']['baseline']['answered_ratio']}",
        f"- doc_type_aware answered ratio: {comparison['summary']['doc_type_aware']['answered_ratio']}",
        f"- baseline evidence source hit ratio: {comparison['summary']['baseline']['evidence_source_hit_ratio']}",
        f"- doc_type_aware evidence source hit ratio: {comparison['summary']['doc_type_aware']['evidence_source_hit_ratio']}",
        f"- baseline evidence locator hit ratio: {comparison['summary']['baseline']['evidence_locator_hit_ratio']}",
        f"- doc_type_aware evidence locator hit ratio: {comparison['summary']['doc_type_aware']['evidence_locator_hit_ratio']}",
        "",
        "## Comparison by doc_type",
    ]

    doc_type_groups = set(comparison["by_doc_type"][STRATEGY_BASELINE]) | set(comparison["by_doc_type"][STRATEGY_DOC_TYPE_AWARE])
    for doc_type in sorted(doc_type_groups):
        baseline = comparison["by_doc_type"][STRATEGY_BASELINE].get(doc_type, _empty_summary())
        candidate = comparison["by_doc_type"][STRATEGY_DOC_TYPE_AWARE].get(doc_type, _empty_summary())
        lines.append(
            f"- {doc_type}: baseline={baseline['evidence_source_hit_ratio']} doc_type_aware={candidate['evidence_source_hit_ratio']}"
        )

    lines.extend([
        "",
        "## Metric notes",
        "- evidence source hit: whether any retrieved row matched the gold evidence source_id",
        "- evidence locator hit: whether any retrieved row matched the gold evidence locator after normalization",
        "",
        "## Error cases",
    ])
    if comparison["error_cases"]:
        for row in comparison["error_cases"][:10]:
            lines.append(
                f"- {row['id']}: baseline_source_hit={row['baseline_source_hit']}, doc_type_aware_source_hit={row['doc_type_aware_source_hit']}"
            )
    else:
        lines.append("- No highlighted error cases.")

    return "\n".join(lines) + "\n"


def write_chunking_run_artifacts(
    run_dir: Path,
    baseline_predictions: list[dict[str, Any]],
    baseline_metrics: dict[str, Any],
    candidate_predictions: list[dict[str, Any]],
    candidate_metrics: dict[str, Any],
    comparison: dict[str, Any],
    report: str,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(_strategy_dir(run_dir, STRATEGY_BASELINE) / "predictions.json", baseline_predictions)
    write_json(_strategy_dir(run_dir, STRATEGY_BASELINE) / "metrics.json", baseline_metrics)
    write_json(_strategy_dir(run_dir, STRATEGY_DOC_TYPE_AWARE) / "predictions.json", candidate_predictions)
    write_json(_strategy_dir(run_dir, STRATEGY_DOC_TYPE_AWARE) / "metrics.json", candidate_metrics)
    write_json(run_dir / "comparison" / "summary.json", comparison["summary"])
    write_json(run_dir / "comparison" / "by_doc_type.json", comparison["by_doc_type"])
    write_json(run_dir / "comparison" / "by_source_id.json", comparison["by_source_id"])
    write_json(run_dir / "comparison" / "error_cases.json", comparison["error_cases"])
    (run_dir / "report.md").write_text(report, encoding="utf-8")


def build_source_documents(store_path: Path, chunking_strategy: str, registry_path: Path = REGISTRY_PATH) -> None:
    registry_entries = load_source_registry(registry_path)
    if store_path.exists():
        shutil.rmtree(store_path)
    with use_store_path(store_path):
        knowledge_base_service = KnowledgeBaseService()
        for entry in registry_entries:
            source_path = Path(entry["path_or_url"])
            markdown = read_text(source_path)
            source_metadata = _build_source_metadata(entry)
            knowledge_base_service.ingest_document(
                markdown,
                source_metadata,
                chunking_strategy=chunking_strategy,
            )


def run_strategy_evaluation(dataset: list[dict[str, Any]], store_path: Path) -> list[dict[str, Any]]:
    with use_store_path(store_path):
        rag_service = RagService()
        predictions = []
        for sample in dataset:
            result = rag_service.answer_with_retrieval(
                str(sample["question"]),
                session_id=build_session_id(sample),
            )
            predictions.append(_build_prediction_record(sample, result))
    return predictions


def build_run_id(dataset_path: Path) -> str:
    return f"{dataset_path.stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def require_runtime_credentials() -> None:
    load_bailian_runtime_config()


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Run chunking strategy comparison")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--out-dir", default=Path("results/chunking_eval"), type=Path)
    parser.add_argument("--registry", default=REGISTRY_PATH, type=Path)
    args = parser.parse_args()

    require_runtime_credentials()
    dataset = load_dataset(args.dataset)
    run_id = build_run_id(args.dataset)
    stores_dir = args.out_dir / "stores" / run_id
    baseline_store_path = stores_dir / STRATEGY_BASELINE
    candidate_store_path = stores_dir / STRATEGY_DOC_TYPE_AWARE

    build_source_documents(baseline_store_path, STRATEGY_BASELINE, registry_path=args.registry)
    build_source_documents(candidate_store_path, STRATEGY_DOC_TYPE_AWARE, registry_path=args.registry)

    baseline_predictions = run_strategy_evaluation(dataset, baseline_store_path)
    candidate_predictions = run_strategy_evaluation(dataset, candidate_store_path)
    baseline_metrics = summarize_chunking_predictions(baseline_predictions)
    candidate_metrics = summarize_chunking_predictions(candidate_predictions)
    comparison = build_comparison_artifacts(
        baseline_predictions,
        candidate_predictions,
        baseline_metrics,
        candidate_metrics,
        run_id=run_id,
    )
    report = render_chunking_report(
        run_id=run_id,
        dataset_path=args.dataset,
        baseline_store_path=baseline_store_path,
        candidate_store_path=candidate_store_path,
        comparison=comparison,
    )
    run_dir = args.out_dir / run_id
    write_chunking_run_artifacts(
        run_dir,
        baseline_predictions,
        baseline_metrics,
        candidate_predictions,
        candidate_metrics,
        comparison,
        report,
    )
    print(json.dumps(comparison["summary"], ensure_ascii=False, indent=2))
    return comparison["summary"]


if __name__ == "__main__":
    main()
