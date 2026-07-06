from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.channel_context import CHANNEL_TABLE_HEADER
from eval.eval_finetune_compare import _metadata_terms, _merge_eval_metadata
from eval.eval_finetune_behavior import load_predictions
from eval.eval_ragas import write_json


DEFAULT_SAMPLE_ID = "gen-eval-007"
DEFAULT_REQUIRED_CONTEXT_TERMS = [
    CHANNEL_TABLE_HEADER,
    "说明: 感知红绿灯信息 | channel: /apollo/perception/traffic_light",
]


def load_eval_metadata(eval_set_path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(eval_set_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("eval set must be a list")

    metadata_by_id: dict[str, dict[str, Any]] = {}
    for row in payload:
        if not isinstance(row, dict):
            continue
        row_id = str(row.get("id", ""))
        metadata = row.get("metadata", {})
        if row_id and isinstance(metadata, dict):
            metadata_by_id[row_id] = metadata
    return metadata_by_id


def find_prediction(rows: list[dict[str, Any]], sample_id: str) -> dict[str, Any]:
    for row in rows:
        if str(row.get("id", "")) == sample_id:
            return row
    raise ValueError(f"sample not found in predictions: {sample_id}")


def _answer_has_term(answer: str, term: str) -> bool:
    return term.lower() in answer.lower()


def evaluate_e7_gate(
    row: dict[str, Any],
    *,
    required_context_terms: list[str] | None = None,
) -> dict[str, Any]:
    answer = str(row.get("answer", ""))
    retrieved_context = str(row.get("retrieved_context", ""))
    required_answer_terms = _metadata_terms(row, "required_answer_terms")
    forbidden_answer_terms = _metadata_terms(row, "forbidden_answer_terms")
    required_context_terms = required_context_terms or DEFAULT_REQUIRED_CONTEXT_TERMS

    missing_required_answer_terms = [
        term for term in required_answer_terms if not _answer_has_term(answer, term)
    ]
    present_forbidden_answer_terms = [
        term for term in forbidden_answer_terms if _answer_has_term(answer, term)
    ]
    missing_required_context_terms = [
        term for term in required_context_terms if term not in retrieved_context
    ]

    passed = (
        bool(answer.strip())
        and not missing_required_answer_terms
        and not present_forbidden_answer_terms
        and not missing_required_context_terms
    )
    return {
        "id": row.get("id", ""),
        "passed": passed,
        "answer": answer,
        "required_answer_terms": required_answer_terms,
        "missing_required_answer_terms": missing_required_answer_terms,
        "forbidden_answer_terms": forbidden_answer_terms,
        "present_forbidden_answer_terms": present_forbidden_answer_terms,
        "required_context_terms": required_context_terms,
        "missing_required_context_terms": missing_required_context_terms,
    }


def run_gate(
    *,
    predictions_path: Path,
    eval_set_path: Path,
    out_path: Path | None = None,
    sample_id: str = DEFAULT_SAMPLE_ID,
) -> dict[str, Any]:
    predictions = load_predictions(predictions_path)
    predictions = _merge_eval_metadata(predictions, load_eval_metadata(eval_set_path))
    target_row = find_prediction(predictions, sample_id)
    result = evaluate_e7_gate(target_row)
    payload = {
        "pipeline": "e7_regression_gate",
        "sample_id": sample_id,
        "predictions_path": str(predictions_path),
        "eval_set_path": str(eval_set_path),
        "result": result,
    }
    if out_path is not None:
        write_json(out_path, payload)
    return payload


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Check E7 local regression gate for gen-eval-007.")
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--eval-set", required=True, type=Path)
    parser.add_argument("--out", default=None, type=Path)
    parser.add_argument("--sample-id", default=DEFAULT_SAMPLE_ID)
    args = parser.parse_args()

    payload = run_gate(
        predictions_path=args.predictions,
        eval_set_path=args.eval_set,
        out_path=args.out,
        sample_id=args.sample_id,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not payload["result"]["passed"]:
        raise SystemExit(1)
    return payload


if __name__ == "__main__":
    main()
