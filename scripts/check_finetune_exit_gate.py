from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.eval_finetune_behavior import evaluate_row, load_predictions, summarize_rows
from eval.eval_finetune_compare import analyze_answer_hardening, summarize_hardening_rows
from eval.eval_ragas import write_json


SAFETY_RISK_KEYS = (
    "unsupported_claim_risk",
    "unsupported_numeric_claim_risk",
    "directional_contradiction_risk",
    "required_term_risk",
    "forbidden_term_risk",
    "answer_contract_risk",
    "citation_support_risk",
)


def _risk_ids(rows: list[dict[str, Any]], key: str) -> list[str]:
    return [str(row.get("id", "")) for row in rows if row.get(key)]


def _metric(summary: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = summary.get(key, default)
    return float(value) if isinstance(value, (int, float)) else default


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object JSON: {path}")
    return payload


def _extract_summary(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", payload)
    return summary if isinstance(summary, dict) else {}


def evaluate_finetune_exit_gate(
    predictions: list[dict[str, Any]],
    *,
    behavior_summary: dict[str, Any] | None = None,
    compare_summary: dict[str, Any] | None = None,
    max_over_refusal_risk_ratio: float = 0.0,
    min_evidence_source_hit_ratio: float = 1.0,
) -> dict[str, Any]:
    behavior_rows = [evaluate_row(row) for row in predictions]
    hardening_rows = [analyze_answer_hardening(row) for row in predictions]
    computed_behavior_summary = summarize_rows(behavior_rows)
    computed_hardening_summary = summarize_hardening_rows(hardening_rows)

    external_behavior_summary = behavior_summary or {}
    compare_summary = compare_summary or {}
    candidate_summary = compare_summary.get("candidate_summary", {})
    if not isinstance(candidate_summary, dict):
        candidate_summary = {}

    # Gate decisions must use the exact prediction file being checked. Older
    # behavior/compare summaries are retained only as external evidence.
    merged_summary = {
        **computed_behavior_summary,
        **computed_hardening_summary,
    }

    safety_failures = {
        key: _risk_ids(
            hardening_rows if key != "unsupported_claim_risk" else behavior_rows,
            key,
        )
        for key in SAFETY_RISK_KEYS
    }
    active_safety_failures = {
        key: ids for key, ids in safety_failures.items() if ids
    }
    over_refusal_ids = _risk_ids(behavior_rows, "over_refusal_risk")

    source_hit_ratio = _metric(merged_summary, "evidence_source_hit_ratio")
    over_refusal_ratio = _metric(merged_summary, "over_refusal_risk_ratio")
    training_exit_pass = not active_safety_failures and source_hit_ratio >= min_evidence_source_hit_ratio
    product_goal_pass = training_exit_pass and over_refusal_ratio <= max_over_refusal_risk_ratio

    if source_hit_ratio < min_evidence_source_hit_ratio:
        decision = "stop_training_fix_retrieval"
    elif active_safety_failures:
        decision = "review_before_next_targeted_training"
    elif not product_goal_pass:
        decision = "stop_training_fix_engineering"
    else:
        decision = "training_goal_met"

    return {
        "training_exit_pass": training_exit_pass,
        "product_goal_pass": product_goal_pass,
        "decision": decision,
        "sample_count": len(predictions),
        "metrics": {
            "evidence_source_hit_ratio": source_hit_ratio,
            "over_refusal_risk_ratio": over_refusal_ratio,
            "max_over_refusal_risk_ratio": max_over_refusal_risk_ratio,
            "answer_contract_risk_ratio": _metric(merged_summary, "answer_contract_risk_ratio"),
            "citation_support_risk_ratio": _metric(merged_summary, "citation_support_risk_ratio"),
            "unsupported_claim_risk_ratio": _metric(merged_summary, "unsupported_claim_risk_ratio"),
            "required_term_risk_ratio": _metric(merged_summary, "required_term_risk_ratio"),
            "forbidden_term_risk_ratio": _metric(merged_summary, "forbidden_term_risk_ratio"),
        },
        "risk_ids": {
            **active_safety_failures,
            "over_refusal_risk": over_refusal_ids,
        },
        "external_evidence": {
            "computed_behavior_summary": computed_behavior_summary,
            "provided_behavior_summary": external_behavior_summary,
            "compare_candidate_summary": candidate_summary,
            "compare_verdict": compare_summary.get("verdict"),
        },
        "recommended_next_step": _recommend_next_step(decision),
    }


def _recommend_next_step(decision: str) -> str:
    if decision == "training_goal_met":
        return "停止当前微调循环，进入验收或工程化收口。"
    if decision == "stop_training_fix_engineering":
        return "停止新增 SFT 训练，优先处理回答充分性、检索上下文或引用 locator。"
    if decision == "stop_training_fix_retrieval":
        return "停止新增 SFT 训练，先修检索命中和证据上下文。"
    return "先做失败样本归因；只有确认是模型能力缺口时，才允许下一轮定向微调。"


def run_exit_gate(
    *,
    predictions_path: Path,
    behavior_summary_path: Path | None = None,
    compare_summary_path: Path | None = None,
    out_path: Path | None = None,
    max_over_refusal_risk_ratio: float = 0.0,
    min_evidence_source_hit_ratio: float = 1.0,
) -> dict[str, Any]:
    behavior_payload = _load_json(behavior_summary_path)
    compare_payload = _load_json(compare_summary_path)
    payload = {
        "pipeline": "finetune_exit_gate",
        "predictions_path": str(predictions_path),
        "behavior_summary_path": str(behavior_summary_path) if behavior_summary_path else None,
        "compare_summary_path": str(compare_summary_path) if compare_summary_path else None,
        "result": evaluate_finetune_exit_gate(
            load_predictions(predictions_path),
            behavior_summary=_extract_summary(behavior_payload),
            compare_summary=compare_payload,
            max_over_refusal_risk_ratio=max_over_refusal_risk_ratio,
            min_evidence_source_hit_ratio=min_evidence_source_hit_ratio,
        ),
    }
    if out_path is not None:
        write_json(out_path, payload)
    return payload


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Check whether the current fine-tuning loop should stop.")
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--behavior-summary", default=None, type=Path)
    parser.add_argument("--compare-summary", default=None, type=Path)
    parser.add_argument("--out", default=None, type=Path)
    parser.add_argument("--max-over-refusal-risk-ratio", default=0.0, type=float)
    parser.add_argument("--min-evidence-source-hit-ratio", default=1.0, type=float)
    args = parser.parse_args()

    payload = run_exit_gate(
        predictions_path=args.predictions,
        behavior_summary_path=args.behavior_summary,
        compare_summary_path=args.compare_summary,
        out_path=args.out,
        max_over_refusal_risk_ratio=args.max_over_refusal_risk_ratio,
        min_evidence_source_hit_ratio=args.min_evidence_source_hit_ratio,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not payload["result"]["training_exit_pass"]:
        raise SystemExit(1)
    return payload


if __name__ == "__main__":
    main()
