import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.eval_ragas import write_json


REFUSAL_MARKERS = (
    "无法从给定证据",
    "无法从现有资料",
    "证据不足",
    "无法确认",
    "不能确认",
    "无法判断",
    "未提供",
    "未提及",
    "并未提及",
    "没有给出",
    "未明确给出",
    "not enough evidence",
    "cannot determine",
    "not provided",
)


def load_predictions(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "predictions" in payload:
        return payload["predictions"]
    raise ValueError("predictions must be a list or a dict with a predictions field")


def _normalize_locator(locator: str | None) -> str:
    if not locator:
        return ""
    return " ".join(locator.strip().split())


def is_refusal(answer: str) -> bool:
    normalized = answer.lower()
    return any(marker.lower() in normalized for marker in REFUSAL_MARKERS)


def has_evidence_source_hit(row: dict[str, Any]) -> bool:
    retrieved_sources = {
        item.get("source_id", "") for item in row.get("retrieved_rows", [])
    }
    return any(
        item.get("source_id", "") in retrieved_sources for item in row.get("evidence", [])
    )


def has_evidence_locator_hit(row: dict[str, Any]) -> bool:
    retrieved_locators = {
        _normalize_locator(item.get("locator", "")) for item in row.get("retrieved_rows", [])
    }
    return any(
        _normalize_locator(item.get("locator", "")) in retrieved_locators
        for item in row.get("evidence", [])
    )


def answer_mentions_evidence(row: dict[str, Any]) -> bool:
    answer = row.get("answer", "")
    for item in row.get("evidence", []):
        source_id = item.get("source_id", "")
        locator = item.get("locator", "")
        if source_id and source_id in answer:
            return True
        if locator and locator in answer:
            return True
    return False


def expected_behavior(row: dict[str, Any]) -> str:
    metadata = row.get("metadata", {})
    value = metadata.get("expected_behavior", "answer") if isinstance(metadata, dict) else "answer"
    return value if value in {"answer", "refuse"} else "answer"


def evaluate_row(row: dict[str, Any]) -> dict[str, Any]:
    answer = row.get("answer", "").strip()
    answered = bool(answer)
    refused = is_refusal(answer) if answered else False
    source_hit = has_evidence_source_hit(row)
    locator_hit = has_evidence_locator_hit(row)
    cites_evidence = answer_mentions_evidence(row) if answered else False
    expects_refusal = expected_behavior(row) == "refuse"

    return {
        "id": row.get("id", ""),
        "answered": answered,
        "refusal": refused,
        "evidence_source_hit": source_hit,
        "evidence_locator_hit": locator_hit,
        "answer_cites_evidence": cites_evidence,
        "unsupported_claim_risk": answered and not refused and not source_hit,
        "over_refusal_risk": refused and source_hit and not expects_refusal,
        "correct_refusal": refused and (not source_hit or expects_refusal),
    }


def _ratio(count: int, total: int) -> float:
    return round(count / total, 3) if total else 0.0


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    keys = [
        "answered",
        "refusal",
        "evidence_source_hit",
        "evidence_locator_hit",
        "answer_cites_evidence",
        "unsupported_claim_risk",
        "over_refusal_risk",
        "correct_refusal",
    ]
    summary: dict[str, Any] = {"sample_count": total}
    for key in keys:
        count = sum(1 for row in rows if row[key])
        summary[f"{key}_count"] = count
        summary[f"{key}_ratio"] = _ratio(count, total)
    return summary


def _prediction_ids(rows: list[dict[str, Any]]) -> list[str]:
    return [str(row.get("id", "")) for row in rows]


def compare_summaries(
    baseline_summary: dict[str, Any],
    candidate_summary: dict[str, Any],
) -> dict[str, Any]:
    comparison: dict[str, Any] = {}
    for key, candidate_value in candidate_summary.items():
        if not key.endswith("_ratio"):
            continue
        baseline_value = baseline_summary.get(key)
        if isinstance(baseline_value, (int, float)) and isinstance(candidate_value, (int, float)):
            comparison[f"{key}_delta"] = round(candidate_value - baseline_value, 3)
    return comparison


def evaluate_predictions(
    predictions_path: Path,
    out_dir: Path,
    baseline_predictions_path: Path | None = None,
) -> dict[str, Any]:
    predictions = load_predictions(predictions_path)
    rows = [evaluate_row(row) for row in predictions]
    summary = summarize_rows(rows)

    output = {
        "summary": summary,
        "rows": rows,
    }

    if baseline_predictions_path is not None:
        baseline_predictions = load_predictions(baseline_predictions_path)
        if _prediction_ids(baseline_predictions) != _prediction_ids(predictions):
            raise ValueError("baseline and candidate predictions must contain the same sample ids in the same order")
        baseline_rows = [evaluate_row(row) for row in baseline_predictions]
        baseline_summary = summarize_rows(baseline_rows)
        output["baseline_summary"] = baseline_summary
        output["comparison"] = compare_summaries(baseline_summary, summary)

    run_id = f"finetune-behavior-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    run_dir = out_dir / run_id
    write_json(run_dir / "summary.json", output)
    write_json(
        run_dir / "manifest.json",
        {
            "contract_version": "v1.1",
            "pipeline": "finetune_behavior_eval",
            "run_id": run_id,
            "predictions_path": str(predictions_path),
            "baseline_predictions_path": str(baseline_predictions_path)
            if baseline_predictions_path
            else None,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "runner_script": "eval/eval_finetune_behavior.py",
        },
    )
    return output


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Evaluate fine-tuned RAG answer behavior offline.")
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--baseline-predictions", default=None, type=Path)
    parser.add_argument("--out-dir", default=Path("results/finetune_behavior_eval"), type=Path)
    args = parser.parse_args()

    output = evaluate_predictions(
        predictions_path=args.predictions,
        out_dir=args.out_dir,
        baseline_predictions_path=args.baseline_predictions,
    )
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
