from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.eval_finetune_behavior import (
    compare_summaries,
    evaluate_row,
    load_predictions,
    summarize_rows,
)
from eval.eval_ragas import write_json


def _prediction_ids(rows: list[dict[str, Any]]) -> list[str]:
    return [str(row.get("id", "")) for row in rows]


def _answer_length(row: dict[str, Any]) -> int:
    return len(str(row.get("answer", "")))


def _average(values: list[int]) -> float:
    return round(sum(values) / len(values), 1) if values else 0.0


def _source_ids(row: dict[str, Any]) -> str:
    source_ids = [
        str(item.get("source_id", ""))
        for item in row.get("retrieved_rows", [])
        if item.get("source_id")
    ]
    return ", ".join(source_ids) if source_ids else "none"


def _truncate(text: str, limit: int = 900) -> str:
    normalized = str(text or "").strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def build_side_by_side_rows(
    baseline_predictions: list[dict[str, Any]],
    candidate_predictions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if _prediction_ids(baseline_predictions) != _prediction_ids(candidate_predictions):
        raise ValueError("baseline and candidate predictions must contain the same sample ids in the same order")

    rows = []
    for baseline_row, candidate_row in zip(baseline_predictions, candidate_predictions):
        baseline_behavior = evaluate_row(baseline_row)
        candidate_behavior = evaluate_row(candidate_row)
        rows.append(
            {
                "id": str(candidate_row.get("id", "")),
                "question": candidate_row.get("question", baseline_row.get("question", "")),
                "category": (candidate_row.get("metadata") or {}).get(
                    "generation_category",
                    (baseline_row.get("metadata") or {}).get("generation_category", ""),
                ),
                "expected_behavior": (candidate_row.get("metadata") or {}).get(
                    "expected_behavior",
                    (baseline_row.get("metadata") or {}).get("expected_behavior", ""),
                ),
                "baseline_answer": baseline_row.get("answer", ""),
                "candidate_answer": candidate_row.get("answer", ""),
                "baseline_answer_length": _answer_length(baseline_row),
                "candidate_answer_length": _answer_length(candidate_row),
                "answer_length_delta": _answer_length(candidate_row) - _answer_length(baseline_row),
                "baseline_sources": _source_ids(baseline_row),
                "candidate_sources": _source_ids(candidate_row),
                "baseline_behavior": baseline_behavior,
                "candidate_behavior": candidate_behavior,
            }
        )
    return rows


def classify_verdict(comparison: dict[str, Any]) -> str:
    citation_delta = comparison.get("answer_cites_evidence_ratio_delta", 0.0)
    unsupported_delta = comparison.get("unsupported_claim_risk_ratio_delta", 0.0)
    over_refusal_delta = comparison.get("over_refusal_risk_ratio_delta", 0.0)
    refusal_delta = comparison.get("refusal_ratio_delta", 0.0)
    correct_refusal_delta = comparison.get("correct_refusal_ratio_delta", 0.0)

    if over_refusal_delta > 0 or (refusal_delta > 0.2 and correct_refusal_delta <= 0):
        return "over_refuses"
    if citation_delta > 0 and unsupported_delta <= 0 and over_refusal_delta <= 0:
        return "adapter_improved"
    if unsupported_delta > 0 or citation_delta < 0 or correct_refusal_delta < 0:
        return "mixed_or_regressed"
    if any(abs(value) > 0 for value in comparison.values() if isinstance(value, (int, float))):
        return "mixed"
    return "no_clear_change"


def _length_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    baseline_lengths = [row["baseline_answer_length"] for row in rows]
    candidate_lengths = [row["candidate_answer_length"] for row in rows]
    return {
        "baseline_avg_answer_length": _average(baseline_lengths),
        "candidate_avg_answer_length": _average(candidate_lengths),
        "avg_answer_length_delta": round(
            _average(candidate_lengths) - _average(baseline_lengths),
            1,
        ),
    }


def build_comparison_payload(
    *,
    baseline_predictions: list[dict[str, Any]],
    candidate_predictions: list[dict[str, Any]],
    baseline_label: str,
    candidate_label: str,
) -> dict[str, Any]:
    rows = build_side_by_side_rows(baseline_predictions, candidate_predictions)
    baseline_behavior_rows = [row["baseline_behavior"] for row in rows]
    candidate_behavior_rows = [row["candidate_behavior"] for row in rows]
    baseline_summary = summarize_rows(baseline_behavior_rows)
    candidate_summary = summarize_rows(candidate_behavior_rows)
    comparison = compare_summaries(baseline_summary, candidate_summary)

    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "baseline_label": baseline_label,
        "candidate_label": candidate_label,
        "sample_count": len(rows),
        "baseline_summary": baseline_summary,
        "candidate_summary": candidate_summary,
        "comparison": comparison,
        "answer_length_summary": _length_summary(rows),
        "verdict": classify_verdict(comparison),
        "side_by_side_rows": rows,
    }


def _format_bool(value: Any) -> str:
    return "是" if value else "否"


def render_side_by_side_report(payload: dict[str, Any]) -> str:
    baseline_label = payload["baseline_label"]
    candidate_label = payload["candidate_label"]
    comparison = payload["comparison"]
    length_summary = payload["answer_length_summary"]
    lines = [
        f"# 微调前后对比报告：{baseline_label} vs {candidate_label}",
        "",
        "## 结论摘要",
        "",
        f"- 样本数：`{payload['sample_count']}`",
        f"- 自动判定：`{payload['verdict']}`",
        f"- {baseline_label} 平均回答长度：`{length_summary['baseline_avg_answer_length']}`",
        f"- {candidate_label} 平均回答长度：`{length_summary['candidate_avg_answer_length']}`",
        f"- 平均回答长度变化：`{length_summary['avg_answer_length_delta']}`",
        "",
        "## 行为指标变化",
        "",
        "| 指标 delta | 数值 |",
        "| --- | ---: |",
    ]
    for key in sorted(comparison):
        lines.append(f"| `{key}` | `{comparison[key]}` |")

    lines.extend(
        [
            "",
            "## 人工复核重点",
            "",
            "- adapter 是否真的更会引用资料，而不是只改了措辞。",
            "- adapter 是否只是回答变短，导致看起来更保守。",
            "- adapter 是否对本来可回答的问题开始过度拒答。",
            "- hard case 中是否减少无依据扩展。",
            "",
            "## 逐样本并排对比",
            "",
        ]
    )

    for row in payload["side_by_side_rows"]:
        baseline_behavior = row["baseline_behavior"]
        candidate_behavior = row["candidate_behavior"]
        lines.extend(
            [
                f"### {row['id']}：{row.get('category') or 'uncategorized'}",
                "",
                f"- 预期行为：`{row.get('expected_behavior') or 'unknown'}`",
                f"- 问题：{row['question']}",
                f"- {baseline_label} 检索来源：`{row['baseline_sources']}`",
                f"- {candidate_label} 检索来源：`{row['candidate_sources']}`",
                f"- 回答长度变化：`{row['baseline_answer_length']} -> {row['candidate_answer_length']}`，delta `{row['answer_length_delta']}`",
                f"- {baseline_label} 引用证据：`{_format_bool(baseline_behavior['answer_cites_evidence'])}`；拒答：`{_format_bool(baseline_behavior['refusal'])}`；过度拒答风险：`{_format_bool(baseline_behavior['over_refusal_risk'])}`",
                f"- {candidate_label} 引用证据：`{_format_bool(candidate_behavior['answer_cites_evidence'])}`；拒答：`{_format_bool(candidate_behavior['refusal'])}`；过度拒答风险：`{_format_bool(candidate_behavior['over_refusal_risk'])}`",
                "",
                f"**{baseline_label} 回答**",
                "",
                "```text",
                _truncate(row["baseline_answer"]),
                "```",
                "",
                f"**{candidate_label} 回答**",
                "",
                "```text",
                _truncate(row["candidate_answer"]),
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def compare_predictions(
    *,
    baseline_predictions_path: Path,
    candidate_predictions_path: Path,
    out_dir: Path,
    baseline_label: str = "base",
    candidate_label: str = "adapter",
) -> dict[str, Any]:
    baseline_predictions = load_predictions(baseline_predictions_path)
    candidate_predictions = load_predictions(candidate_predictions_path)
    payload = build_comparison_payload(
        baseline_predictions=baseline_predictions,
        candidate_predictions=candidate_predictions,
        baseline_label=baseline_label,
        candidate_label=candidate_label,
    )

    run_id = f"finetune-compare-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    run_dir = out_dir / run_id
    write_json(run_dir / "summary.json", payload)
    (run_dir / "side_by_side_samples.md").write_text(
        render_side_by_side_report(payload),
        encoding="utf-8",
    )
    write_json(
        run_dir / "manifest.json",
        {
            "contract_version": "v1.1",
            "pipeline": "finetune_compare",
            "run_id": run_id,
            "created_at": payload["created_at"],
            "runner_script": "eval/eval_finetune_compare.py",
            "baseline_predictions_path": str(baseline_predictions_path),
            "candidate_predictions_path": str(candidate_predictions_path),
            "baseline_label": baseline_label,
            "candidate_label": candidate_label,
        },
    )
    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "summary": str(run_dir / "summary.json"),
        "side_by_side": str(run_dir / "side_by_side_samples.md"),
        "manifest": str(run_dir / "manifest.json"),
        "verdict": payload["verdict"],
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Compare base vs adapter generation predictions.")
    parser.add_argument("--baseline-predictions", required=True, type=Path)
    parser.add_argument("--candidate-predictions", required=True, type=Path)
    parser.add_argument("--out-dir", default=Path("results/finetune_compare"), type=Path)
    parser.add_argument("--baseline-label", default="base")
    parser.add_argument("--candidate-label", default="adapter")
    args = parser.parse_args()

    output = compare_predictions(
        baseline_predictions_path=args.baseline_predictions,
        candidate_predictions_path=args.candidate_predictions,
        out_dir=args.out_dir,
        baseline_label=args.baseline_label,
        candidate_label=args.candidate_label,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
