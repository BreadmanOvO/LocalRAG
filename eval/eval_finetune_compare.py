from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.eval_finetune_behavior import (
    compare_summaries,
    evaluate_row,
    expected_behavior,
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


def _load_eval_metadata(eval_set_path: Path | None) -> dict[str, dict[str, Any]]:
    if eval_set_path is None:
        return {}
    payload = json.loads(eval_set_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("eval set must be a list of records")

    metadata_by_id: dict[str, dict[str, Any]] = {}
    for row in payload:
        if not isinstance(row, dict):
            continue
        row_id = str(row.get("id", ""))
        metadata = row.get("metadata", {})
        if row_id and isinstance(metadata, dict):
            metadata_by_id[row_id] = metadata
    return metadata_by_id


def _merge_eval_metadata(
    rows: list[dict[str, Any]],
    metadata_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    if not metadata_by_id:
        return rows

    merged_rows = []
    for row in rows:
        row_id = str(row.get("id", ""))
        eval_metadata = metadata_by_id.get(row_id)
        if not eval_metadata:
            merged_rows.append(row)
            continue

        merged_row = dict(row)
        row_metadata = row.get("metadata", {})
        if not isinstance(row_metadata, dict):
            row_metadata = {}
        merged_row["metadata"] = {
            **row_metadata,
            **eval_metadata,
        }
        merged_rows.append(merged_row)
    return merged_rows


_NUMBER_RE = re.compile(r"(?<![A-Za-z0-9])\d+(?:\.\d+)?(?:%|ms)?(?![A-Za-z])")
_PATH_RE = re.compile(r"/[A-Za-z0-9_./-]+")
_EN_TERM_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_+-]{2,}\b")
_STOP_TERMS = {
    "and",
    "are",
    "for",
    "from",
    "into",
    "not",
    "one",
    "the",
    "with",
    "within",
    "without",
}
_ANSWER_UP_MARKERS = ("提升", "提高", "上升", "增加", "improve", "improved", "increase", "increased")
_REFERENCE_DOWN_MARKERS = ("下降", "降低", "降到", "退化", "drops", "drop", "degraded", "worse")
_CITATION_MARKERS = ("引用：", "引用:")


def _normalize_number(value: str) -> str:
    return value.lower().removesuffix("ms").removesuffix("%")


def _numbers(text: str) -> list[str]:
    values: list[str] = []
    seen = set()
    for match in _NUMBER_RE.findall(str(text or "")):
        normalized = _normalize_number(match)
        if normalized not in seen:
            values.append(normalized)
            seen.add(normalized)
    return values


def _answer_claim_text(answer: str) -> str:
    claim_text = str(answer or "")
    marker_indexes = [
        index
        for marker in _CITATION_MARKERS
        if (index := claim_text.find(marker)) >= 0
    ]
    if marker_indexes:
        return claim_text[: min(marker_indexes)]
    return claim_text


def _number_supported(number: str, support_numbers: list[str]) -> bool:
    try:
        value = float(number)
    except ValueError:
        return number in support_numbers

    for support_number in support_numbers:
        try:
            support_value = float(support_number)
        except ValueError:
            if number == support_number:
                return True
            continue
        tolerance = max(0.05, abs(support_value) * 0.01)
        if abs(value - support_value) <= tolerance:
            return True
    return False


def _support_text(row: dict[str, Any]) -> str:
    fragments = [
        str(row.get("reference_answer", "")),
        str(row.get("retrieved_context", "")),
    ]
    fragments.extend(str(item.get("content", "")) for item in row.get("retrieved_rows", []))
    fragments.extend(str(item.get("quote", "")) for item in row.get("evidence", []))
    return "\n".join(fragment for fragment in fragments if fragment)


def _reference_terms(row: dict[str, Any]) -> list[str]:
    text = " ".join(
        [
            str(row.get("reference_answer", "")),
            " ".join(str(item.get("quote", "")) for item in row.get("evidence", [])),
        ]
    )
    terms: list[str] = []
    seen = set()
    for pattern in (_PATH_RE, _EN_TERM_RE):
        for match in pattern.findall(text):
            term = match.lower()
            if term in _STOP_TERMS or term in seen:
                continue
            terms.append(term)
            seen.add(term)
    return terms


def _answer_has_term(answer: str, term: str) -> bool:
    return term in answer.lower()


def _metadata_terms(row: dict[str, Any], key: str) -> list[str]:
    metadata = row.get("metadata", {})
    if not isinstance(metadata, dict):
        return []
    raw_value = metadata.get(key, [])
    if isinstance(raw_value, str):
        raw_values = [raw_value]
    elif isinstance(raw_value, list):
        raw_values = raw_value
    else:
        raw_values = []

    terms = []
    seen = set()
    for value in raw_values:
        term = str(value).strip().lower()
        if not term or term in seen:
            continue
        terms.append(term)
        seen.add(term)
    return terms


def analyze_answer_hardening(row: dict[str, Any]) -> dict[str, Any]:
    answer = str(row.get("answer", ""))
    behavior = evaluate_row(row)
    support_text = _support_text(row)
    support_numbers = _numbers(support_text)
    source_id_numbers = set()
    for item in row.get('retrieved_rows', []):
        for num in _numbers(str(item.get('source_id', ''))):
            source_id_numbers.add(num)
    unsupported_answer_numbers = [
        number for number in _numbers(_answer_claim_text(answer))
        if not _number_supported(number, support_numbers) and number not in source_id_numbers
    ]

    reference_terms = _reference_terms(row)
    missing_reference_terms = [
        term for term in reference_terms if not _answer_has_term(answer, term)
    ]
    reference_coverage_ratio = (
        round((len(reference_terms) - len(missing_reference_terms)) / len(reference_terms), 3)
        if reference_terms
        else 1.0
    )

    required_answer_terms = _metadata_terms(row, "required_answer_terms")
    forbidden_answer_terms = _metadata_terms(row, "forbidden_answer_terms")
    missing_required_terms = [
        term for term in required_answer_terms if not _answer_has_term(answer, term)
    ]
    present_forbidden_terms = [
        term for term in forbidden_answer_terms if _answer_has_term(answer, term)
    ]

    answer_lower = answer.lower()
    reference_lower = str(row.get("reference_answer", "")).lower()
    evidence_lower = " ".join(str(item.get("quote", "")) for item in row.get("evidence", [])).lower()
    directional_contradiction = any(marker in answer_lower for marker in _ANSWER_UP_MARKERS) and any(
        marker in f"{reference_lower}\n{evidence_lower}" for marker in _REFERENCE_DOWN_MARKERS
    )
    unsupported_numeric_claim = bool(unsupported_answer_numbers)
    correctly_refused = expected_behavior(row) == "refuse" and behavior["refusal"]
    reference_coverage_risk = (
        bool(reference_terms)
        and reference_coverage_ratio < 0.7
        and not correctly_refused
    )
    required_term_risk = bool(missing_required_terms)
    forbidden_term_risk = bool(present_forbidden_terms)
    answer_contract_risk = (
        unsupported_numeric_claim
        or directional_contradiction
        or required_term_risk
        or forbidden_term_risk
    )
    cites_evidence = behavior["answer_cites_evidence"]
    citation_support_risk = cites_evidence and answer_contract_risk

    return {
        "id": row.get("id", ""),
        "reference_terms": reference_terms,
        "missing_reference_terms": missing_reference_terms,
        "reference_coverage_ratio": reference_coverage_ratio,
        "reference_coverage_risk": reference_coverage_risk,
        "required_answer_terms": required_answer_terms,
        "missing_required_terms": missing_required_terms,
        "required_term_risk": required_term_risk,
        "forbidden_answer_terms": forbidden_answer_terms,
        "present_forbidden_terms": present_forbidden_terms,
        "forbidden_term_risk": forbidden_term_risk,
        "unsupported_answer_numbers": unsupported_answer_numbers,
        "unsupported_numeric_claim_risk": unsupported_numeric_claim,
        "directional_contradiction_risk": directional_contradiction,
        "answer_contract_risk": answer_contract_risk,
        "citation_support_risk": citation_support_risk,
    }


def summarize_hardening_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    risk_keys = [
        "reference_coverage_risk",
        "unsupported_numeric_claim_risk",
        "directional_contradiction_risk",
        "required_term_risk",
        "forbidden_term_risk",
        "answer_contract_risk",
        "citation_support_risk",
    ]
    summary: dict[str, Any] = {"sample_count": total}
    for key in risk_keys:
        count = sum(1 for row in rows if row[key])
        summary[f"{key}_count"] = count
        summary[f"{key}_ratio"] = round(count / total, 3) if total else 0.0
    coverage_values = [float(row["reference_coverage_ratio"]) for row in rows]
    summary["reference_coverage_ratio"] = (
        round(sum(coverage_values) / len(coverage_values), 3) if coverage_values else 0.0
    )
    return summary


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
        baseline_hardening = analyze_answer_hardening(baseline_row)
        candidate_hardening = analyze_answer_hardening(candidate_row)
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
                "baseline_hardening": baseline_hardening,
                "candidate_hardening": candidate_hardening,
            }
        )
    return rows


def classify_verdict(
    comparison: dict[str, Any],
    candidate_summary: dict[str, Any] | None = None,
) -> str:
    citation_delta = comparison.get("answer_cites_evidence_ratio_delta", 0.0)
    unsupported_delta = comparison.get("unsupported_claim_risk_ratio_delta", 0.0)
    over_refusal_delta = comparison.get("over_refusal_risk_ratio_delta", 0.0)
    refusal_delta = comparison.get("refusal_ratio_delta", 0.0)
    correct_refusal_delta = comparison.get("correct_refusal_ratio_delta", 0.0)
    unsupported_numeric_delta = comparison.get("unsupported_numeric_claim_risk_ratio_delta", 0.0)
    contradiction_delta = comparison.get("directional_contradiction_risk_ratio_delta", 0.0)
    citation_support_delta = comparison.get("citation_support_risk_ratio_delta", 0.0)
    answer_contract_delta = comparison.get("answer_contract_risk_ratio_delta", 0.0)
    candidate_contract_risk_count = (
        int(candidate_summary.get("answer_contract_risk_count", 0))
        if candidate_summary
        else 0
    )

    if over_refusal_delta > 0 or (refusal_delta > 0.2 and correct_refusal_delta <= 0):
        return "over_refuses"
    if (
        unsupported_numeric_delta > 0
        or contradiction_delta > 0
        or answer_contract_delta > 0
        or citation_support_delta > 0
    ):
        return "mixed_or_regressed"
    if candidate_contract_risk_count > 0:
        return "mixed_with_unresolved_contract_risk"
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
    baseline_hardening_rows = [row["baseline_hardening"] for row in rows]
    candidate_hardening_rows = [row["candidate_hardening"] for row in rows]
    baseline_summary = summarize_rows(baseline_behavior_rows)
    baseline_summary.update(summarize_hardening_rows(baseline_hardening_rows))
    candidate_summary = summarize_rows(candidate_behavior_rows)
    candidate_summary.update(summarize_hardening_rows(candidate_hardening_rows))
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
        "verdict": classify_verdict(comparison, candidate_summary),
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
        baseline_hardening = row["baseline_hardening"]
        candidate_hardening = row["candidate_hardening"]
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
                f"- {baseline_label} 参考覆盖率：`{baseline_hardening['reference_coverage_ratio']}`；无来源数字：`{', '.join(baseline_hardening['unsupported_answer_numbers']) or '无'}`；答案合同风险：`{_format_bool(baseline_hardening['answer_contract_risk'])}`；引用支持风险：`{_format_bool(baseline_hardening['citation_support_risk'])}`",
                f"- {candidate_label} 参考覆盖率：`{candidate_hardening['reference_coverage_ratio']}`；无来源数字：`{', '.join(candidate_hardening['unsupported_answer_numbers']) or '无'}`；答案合同风险：`{_format_bool(candidate_hardening['answer_contract_risk'])}`；引用支持风险：`{_format_bool(candidate_hardening['citation_support_risk'])}`",
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
    eval_set_path: Path | None = None,
) -> dict[str, Any]:
    eval_metadata = _load_eval_metadata(eval_set_path)
    baseline_predictions = load_predictions(baseline_predictions_path)
    candidate_predictions = load_predictions(candidate_predictions_path)
    baseline_predictions = _merge_eval_metadata(baseline_predictions, eval_metadata)
    candidate_predictions = _merge_eval_metadata(candidate_predictions, eval_metadata)
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
            "eval_set_path": str(eval_set_path) if eval_set_path else None,
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
    parser.add_argument("--eval-set", default=None, type=Path)
    args = parser.parse_args()

    output = compare_predictions(
        baseline_predictions_path=args.baseline_predictions,
        candidate_predictions_path=args.candidate_predictions,
        out_dir=args.out_dir,
        baseline_label=args.baseline_label,
        candidate_label=args.candidate_label,
        eval_set_path=args.eval_set,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()

