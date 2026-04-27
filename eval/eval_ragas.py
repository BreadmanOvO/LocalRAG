import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.evaluation.shared.eval_schema import validate_dataset
from config.runtime_keys import load_runtime_config


def load_dataset(path: Path) -> list[dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    validate_dataset(records)
    return records


def write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _normalize_locator(locator: str | None) -> str:
    if not locator:
        return ""
    return " ".join(locator.strip().split())



def summarize_predictions(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    sample_count = len(predictions)
    answered_count = sum(1 for row in predictions if row.get("answer", "").strip())
    context_count = sum(1 for row in predictions if row.get("retrieved_context", "").strip())
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

    return {
        "sample_count": sample_count,
        "answered_count": answered_count,
        "answered_ratio": round(answered_count / sample_count, 3) if sample_count else 0.0,
        "context_hit_count": context_count,
        "context_hit_ratio": round(context_count / sample_count, 3) if sample_count else 0.0,
        "evidence_source_hit_count": evidence_source_hit_count,
        "evidence_source_hit_ratio": round(evidence_source_hit_count / sample_count, 3) if sample_count else 0.0,
        "evidence_locator_hit_count": evidence_locator_hit_count,
        "evidence_locator_hit_ratio": round(evidence_locator_hit_count / sample_count, 3) if sample_count else 0.0,
    }


def build_prediction_record(sample: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": sample["id"],
        "question": sample["question"],
        "reference_answer": sample["reference_answer"],
        "answer": result["answer"],
        "retrieved_context": result["retrieved_context"],
        "retrieved_rows": result.get("retrieved_rows", []),
        "retrieval_debug_candidates": result.get("retrieval_debug_candidates", []),
        "evidence": sample.get("evidence", []),
        "metadata": sample.get("metadata", {}),
    }


def build_session_id(sample: dict[str, Any]) -> str:
    sample_id = str(sample["id"])
    return f"eval-session-{sample_id}"


def require_runtime_config() -> None:
    load_runtime_config()


def run_baseline(
    dataset_path: Path | str, predictions_path: Path | str, metrics_path: Path | str
) -> dict[str, Any]:
    dataset_path = Path(dataset_path)
    predictions_path = Path(predictions_path)
    metrics_path = Path(metrics_path)

    dataset = load_dataset(dataset_path)
    require_runtime_config()

    from core.rag import RagService

    rag_service = RagService()
    predictions = []
    for sample in dataset:
        result = rag_service.answer_with_retrieval(
            str(sample["question"]), session_id=build_session_id(sample)
        )
        predictions.append(build_prediction_record(sample, result))

    summary = summarize_predictions(predictions)
    write_json(predictions_path, predictions)
    write_json(metrics_path, summary)
    return summary


def build_run_id(dataset_path: Path) -> str:
    return f"{dataset_path.stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def build_manifest(*, run_id: str, dataset_path: Path, runner_script: str) -> dict[str, Any]:
    return {
        "contract_version": "v1.1",
        "pipeline": "baseline_eval",
        "run_id": run_id,
        "dataset_path": str(dataset_path),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runner_script": runner_script,
    }


def run_baseline_to_dir(dataset_path: Path | str, out_dir: Path | str) -> dict[str, Any]:
    dataset_path = Path(dataset_path)
    out_dir = Path(out_dir)
    run_id = build_run_id(dataset_path)
    run_dir = out_dir / run_id
    summary = run_baseline(
        dataset_path,
        run_dir / "predictions.json",
        run_dir / "metrics.json",
    )
    write_json(
        run_dir / "manifest.json",
        build_manifest(
            run_id=run_id,
            dataset_path=dataset_path,
            runner_script="eval/eval_ragas.py",
        ),
    )
    return summary


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Run baseline RAG evaluation")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--predictions-out", required=True, type=Path)
    parser.add_argument("--metrics-out", required=True, type=Path)
    args = parser.parse_args()

    summary = run_baseline(args.dataset, args.predictions_out, args.metrics_out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    main()
