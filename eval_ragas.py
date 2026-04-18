import argparse
import json
import os
from pathlib import Path
from typing import Any

from data.evaluation.shared.eval_schema import validate_dataset


def load_dataset(path: Path) -> list[dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    validate_dataset(records)
    return records


def write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_predictions(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    sample_count = len(predictions)
    answered_count = sum(1 for row in predictions if row.get("answer", "").strip())
    context_count = sum(1 for row in predictions if row.get("retrieved_context", "").strip())

    return {
        "sample_count": sample_count,
        "answered_count": answered_count,
        "answered_ratio": round(answered_count / sample_count, 3) if sample_count else 0.0,
        "context_hit_count": context_count,
        "context_hit_ratio": round(context_count / sample_count, 3) if sample_count else 0.0,
    }


def build_prediction_record(
    sample: dict[str, Any], answer: str, retrieved_context: str
) -> dict[str, Any]:
    return {
        "id": sample["id"],
        "question": sample["question"],
        "reference_answer": sample["reference_answer"],
        "answer": answer,
        "retrieved_context": retrieved_context,
        "metadata": sample.get("metadata", {}),
    }


def build_session_id(sample: dict[str, Any]) -> str:
    sample_id = str(sample["id"])
    return f"eval-session-{sample_id}"


def run_baseline(
    dataset_path: Path | str, predictions_path: Path | str, metrics_path: Path | str
) -> dict[str, Any]:
    dataset_path = Path(dataset_path)
    predictions_path = Path(predictions_path)
    metrics_path = Path(metrics_path)

    dataset = load_dataset(dataset_path)

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Export the OpenAI API key before running baseline evaluation."
        )

    from rag import RagService

    rag_service = RagService()
    predictions = []
    for sample in dataset:
        answer = rag_service.answer_once(
            str(sample["question"]), session_id=build_session_id(sample)
        )
        predictions.append(build_prediction_record(sample, answer, ""))

    summary = summarize_predictions(predictions)
    write_json(predictions_path, predictions)
    write_json(metrics_path, summary)
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
