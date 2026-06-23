import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.evaluation.shared.eval_schema import validate_dataset


def _validated_record(record: dict[str, Any], line_number: int, path: Path) -> dict[str, Any]:
    if not isinstance(record.get("metadata"), dict):
        raise ValueError(f"{path}:{line_number} missing metadata object")
    if not isinstance(record.get("evidence"), list):
        raise ValueError(f"{path}:{line_number} missing evidence list")
    if "id" not in record:
        raise ValueError(f"{path}:{line_number} missing id")
    if "question" not in record:
        raise ValueError(f"{path}:{line_number} missing question")
    if "reference_answer" not in record:
        raise ValueError(f"{path}:{line_number} missing reference_answer")
    validate_dataset([
        {
            "id": record["id"],
            "question": record["question"],
            "reference_answer": record["reference_answer"],
            "evidence": record["evidence"],
            "metadata": record["metadata"],
        }
    ])
    return record


DEFAULT_DATASET_VERSION = "v1.3-e5"
E5_INSTRUCTION = (
    "请根据给定参考资料回答问题，只能使用资料中的信息；"
    "当问题同时给出完整上下文和部分上下文版本时，完整上下文版本应正常回答，部分上下文版本必须只回答已支持部分，并明确说明缺失部分无法根据资料确定；"
    "不要猜测缺失指标的数值、提升/下降方向或结论；"
    "答案末尾必须用“引用：”列出使用到的 source_id 和 locator。"
)


PAIRWISE_CONTRAST_SPECS = [
    {
        "pair_id": "e5-pairwise-001",
        "source_id": "train-001",
        "question": "使用 4096 个 Top-K 查询时，MFA 延迟、AP 和 ATE 分别发生什么变化？",
        "quote": "using 4096 size queries reduce the latency of MFA by 76.4% (21.01ms to 4.96ms) on 256 × 256 size BEV grid.",
        "complete_supported_claim": "资料说明 4096 个查询会让 MFA 延迟降低 76.4%，从 21.01ms 降到 4.96ms。",
        "partial_supported_claim": "资料只说明 4096 个查询会让 MFA 延迟降低 76.4%。",
        "missing_metrics": ["AP", "ATE"],
        "review_focus": "pairwise_complete_vs_partial_no_direction_guess",
    },
    {
        "pair_id": "e5-pairwise-002",
        "source_id": "train-004",
        "question": "CSDP 的 mask ratio=0.2 时，NDS、mAP 和 mATE 分别是多少？",
        "quote": "mask ratio 0.2 achieves the best result with NDS 58.5 and mAP 50.5.",
        "complete_supported_claim": "资料说明 mask ratio 为 0.2 时 NDS 为 58.5、mAP 为 50.5。",
        "partial_supported_claim": "资料只说明 mask ratio 为 0.2 时 NDS 为 58.5、mAP 为 50.5。",
        "missing_metrics": ["mATE"],
        "review_focus": "pairwise_complete_vs_partial_no_missing_value_guess",
    },
    {
        "pair_id": "e5-pairwise-003",
        "source_id": "train-047",
        "question": "Cross-view Transformer 的推理速度、训练 GPU 小时和显存占用分别是多少？",
        "quote": "The model comfortably runs in real-time (35 FPS) on a single RTX 2080 Ti GPU and trains within 32 GPU hours.",
        "complete_supported_claim": "资料说明推理速度为 35 FPS，训练需要 32 GPU 小时。",
        "partial_supported_claim": "资料说明推理速度为 35 FPS，训练需要 32 GPU 小时。",
        "missing_metrics": ["显存占用"],
        "review_focus": "pairwise_complete_vs_partial_no_missing_value_guess",
    },
    {
        "pair_id": "e5-pairwise-004",
        "source_id": "train-052",
        "question": "GaussianOcc 的训练速度、渲染速度和 mIoU 分别提升了多少？",
        "quote": "GaussianOcc has low computational cost with 2.7 times faster training and 5 times faster rendering.",
        "complete_supported_claim": "资料说明 GaussianOcc 训练快 2.7 倍、渲染快 5 倍。",
        "partial_supported_claim": "资料说明 GaussianOcc 训练快 2.7 倍、渲染快 5 倍。",
        "missing_metrics": ["mIoU"],
        "review_focus": "pairwise_complete_vs_partial_no_metric_improvement_guess",
    },
    {
        "pair_id": "e5-pairwise-005",
        "source_id": "train-170",
        "question": "BEVDet4D-Base 的 NDS、mAP 和推理 FPS 分别是多少？",
        "quote": "BEVDet4D-Base scores high as 42.1% mAP and 54.5% NDS.",
        "complete_supported_claim": "资料说明 BEVDet4D-Base 的 NDS 为 54.5%，mAP 为 42.1%。",
        "partial_supported_claim": "资料说明 BEVDet4D-Base 的 NDS 为 54.5%，mAP 为 42.1%。",
        "missing_metrics": ["推理 FPS"],
        "review_focus": "pairwise_complete_vs_partial_no_missing_speed_guess",
    },
    {
        "pair_id": "e5-pairwise-006",
        "source_id": "train-177",
        "question": "相机外参噪声等级为 4 时，BEVFormer 的 NDS 和 AP 分别下降多少？",
        "quote": "with the noise level being 4, BEVFormer only drops 14.3% NDS.",
        "complete_supported_claim": "资料说明噪声等级为 4 时 BEVFormer 的 NDS 下降 14.3%。",
        "partial_supported_claim": "资料说明噪声等级为 4 时 BEVFormer 的 NDS 下降 14.3%。",
        "missing_metrics": ["AP"],
        "review_focus": "pairwise_complete_vs_partial_no_direction_guess",
    },
    {
        "pair_id": "e5-pairwise-007",
        "source_id": "e4-draft-multi-metric-007",
        "question": "PointPillars 的运行速度、mAP 和内存占用分别是多少？",
        "quote": "This detection performance is achieved while running at 62 Hz: a 2-4 fold runtime improvement.",
        "complete_supported_claim": "资料说明 PointPillars 运行速度为 62 Hz，并带来 2-4 倍运行速度提升。",
        "partial_supported_claim": "资料说明 PointPillars 运行速度为 62 Hz，并带来 2-4 倍运行速度提升。",
        "missing_metrics": ["mAP", "内存占用"],
        "review_focus": "pairwise_complete_vs_partial_no_missing_value_guess",
    },
    {
        "pair_id": "e5-pairwise-008",
        "source_id": "e4-draft-multi-metric-008",
        "question": "NHTSA 进口豁免计划自 2016 年 10 月以来批准了多少辆 ADS 车辆？这些车辆的测试里程是多少？",
        "quote": "Since October 2016, 264 ADS-equipped vehicles have received temporary import permission.",
        "complete_supported_claim": "资料说明自 2016 年 10 月以来有 264 辆 ADS 车辆获得临时进口许可。",
        "partial_supported_claim": "资料说明自 2016 年 10 月以来有 264 辆 ADS 车辆获得临时进口许可。",
        "missing_metrics": ["测试里程"],
        "review_focus": "pairwise_complete_vs_partial_no_missing_value_guess",
    },
]


def load_records(path: Path) -> list[dict[str, Any]]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"{path}:{line_number} is not a JSON object")
        records.append(_validated_record(record, line_number, path))
    return records


def _record_id(record: dict[str, Any]) -> str:
    metadata = record.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("record metadata must be a JSON object")
    source_sample_id = metadata.get("source_sample_id")
    if not source_sample_id:
        raise ValueError("record is missing metadata.source_sample_id")
    return str(source_sample_id)


def _source_record_ids(record: dict[str, Any]) -> list[str]:
    metadata = record.get("metadata", {})
    if not isinstance(metadata, dict):
        return []
    source_record_ids = metadata.get("source_record_ids", [])
    return [str(item) for item in source_record_ids if item]


def _first_evidence(record: dict[str, Any]) -> dict[str, str]:
    metadata = record.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("record metadata must be a JSON object")
    source_sample_id = metadata.get("source_sample_id")
    if not source_sample_id:
        raise ValueError("record is missing metadata.source_sample_id")
    source_id = metadata.get("target_source_id")
    locator = "page=1"
    quote = None
    input_text = str(record.get("input", ""))
    for line in input_text.splitlines():
        if line.startswith("[1] ") and "source_id=" in line and "locator=" in line:
            parts = line.split()
            for part in parts:
                if part.startswith("source_id="):
                    source_id = part.split("=", 1)[1]
                elif part.startswith("locator="):
                    locator = part.split("=", 1)[1]
        elif line and not line.startswith("问题：") and not line.startswith("参考资料：") and not line.startswith("[1] "):
            quote = line
            break
    if not source_id:
        raise ValueError(f"cannot infer source_id from {source_sample_id}")
    evidence = {"source_id": str(source_id), "locator": locator}
    if quote:
        evidence["quote"] = quote
    return evidence


def _citation_lines(evidence_items: list[dict[str, str]]) -> str:
    return "\n".join(f"- {item['source_id']} {item['locator']}" for item in evidence_items)


def _format_evidence_block(index: int, evidence: dict[str, str]) -> str:
    return "\n".join(
        [
            f"[{index}] source_id={evidence['source_id']} locator={evidence['locator']}",
            evidence["quote"],
        ]
    )


def _build_input(question: str, evidence_items: list[dict[str, str]]) -> str:
    evidence_text = "\n\n".join(
        _format_evidence_block(index, item)
        for index, item in enumerate(evidence_items, start=1)
    )
    return f"问题：{question}\n\n参考资料：\n{evidence_text}"


def _join_missing_metrics(metrics: list[str]) -> str:
    if len(metrics) == 1:
        return metrics[0]
    return "、".join(metrics[:-1]) + " 或 " + metrics[-1]


def build_pairwise_contrast_rows(
    *,
    row_id: str,
    source_record: dict[str, Any],
    question: str,
    complete_supported_claim: str,
    partial_supported_claim: str,
    missing_metrics: list[str],
    review_focus: str,
    quote: str | None = None,
) -> list[dict[str, Any]]:
    evidence = dict(_first_evidence(source_record))
    if quote is not None:
        evidence["quote"] = quote
    missing_text = _join_missing_metrics(missing_metrics)
    source_record_ids = _source_record_ids(source_record)
    common_metadata = {
        **source_record.get("metadata", {}),
        "dataset_version": DEFAULT_DATASET_VERSION,
        "review_focus": review_focus,
        "source_record_ids": source_record_ids,
        "target_source_id": evidence["source_id"],
        "pair_id": row_id,
    }
    complete_row = {
        "instruction": E5_INSTRUCTION,
        "input": _build_input(question, [evidence]),
        "output": f"{complete_supported_claim}\n\n引用：\n{_citation_lines([evidence])}",
        "metadata": {
            **common_metadata,
            "source_sample_id": f"{row_id}-complete",
            "data_type": "pairwise_complete_context",
            "missing_metrics": [],
            "expected_behavior": "complete_answer",
        },
    }
    partial_row = {
        "instruction": E5_INSTRUCTION,
        "input": _build_input(question, [evidence]),
        "output": f"{partial_supported_claim}不能根据资料确定 {missing_text} 是提升还是下降，也不能补充未给出的数值。\n\n引用：\n{_citation_lines([evidence])}",
        "metadata": {
            **common_metadata,
            "source_sample_id": f"{row_id}-partial",
            "data_type": "pairwise_partial_context_refusal",
            "missing_metrics": missing_metrics,
            "expected_behavior": "partial_refuse",
        },
    }
    return [complete_row, partial_row]


def build_pairwise_contrast_row(
    *,
    row_id: str,
    source_record: dict[str, Any],
    question: str,
    complete_supported_claim: str,
    partial_supported_claim: str,
    missing_metrics: list[str],
    review_focus: str,
    quote: str | None = None,
) -> dict[str, Any]:
    complete_row, partial_row = build_pairwise_contrast_rows(
        row_id=row_id,
        source_record=source_record,
        question=question,
        complete_supported_claim=complete_supported_claim,
        partial_supported_claim=partial_supported_claim,
        missing_metrics=missing_metrics,
        review_focus=review_focus,
        quote=quote,
    )
    row = dict(complete_row)
    row["contrast_output"] = {
        "data_type": partial_row["metadata"]["data_type"],
        "output": partial_row["output"],
        "metadata": partial_row["metadata"],
    }
    return row


def build_e5_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {_record_id(record): record for record in records}
    source_records = {spec["source_id"]: by_id[spec["source_id"]] for spec in PAIRWISE_CONTRAST_SPECS}
    rows = []
    for spec in PAIRWISE_CONTRAST_SPECS:
        rows.extend(
            build_pairwise_contrast_rows(
                row_id=spec["pair_id"],
                source_record=source_records[spec["source_id"]],
                question=spec["question"],
                complete_supported_claim=spec["complete_supported_claim"],
                partial_supported_claim=spec["partial_supported_claim"],
                missing_metrics=spec["missing_metrics"],
                review_focus=spec["review_focus"],
                quote=spec["quote"],
            )
        )
    return rows


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    data_types = Counter(row["metadata"]["data_type"] for row in rows)
    review_focuses = Counter(row["metadata"]["review_focus"] for row in rows)
    missing_metrics = Counter(
        metric
        for row in rows
        for metric in row["metadata"].get("missing_metrics", [])
    )
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "dataset_version": DEFAULT_DATASET_VERSION,
        "record_count": len(rows),
        "pair_count": len({row["metadata"].get("pair_id") for row in rows}),
        "data_type_distribution": dict(sorted(data_types.items())),
        "review_focus_distribution": dict(sorted(review_focuses.items())),
        "missing_metric_distribution": dict(sorted(missing_metrics.items())),
        "source_record_ids": sorted({sid for row in rows for sid in row["metadata"].get("source_record_ids", [])}),
        "output_citation_count": sum(1 for row in rows if "引用：" in row["output"]),
    }


def render_report(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = [
        "# E5 pairwise context-contrast 数据报告",
        "",
        "E5 的目标是用同题 pairwise 样本，直接修正 E4 在 topk2 下的臆测问题。",
        "",
        "## 摘要",
        "",
        f"- 版本：`{summary['dataset_version']}`",
        f"- 样本数：`{summary['record_count']}`",
        f"- 数据类型分布：{summary['data_type_distribution']}",
        f"- 缺失指标分布：{summary['missing_metric_distribution']}",
        "",
        "## 设计原则",
        "",
        "- 完整上下文版本必须正常回答资料明确支持的全部指标。",
        "- 部分上下文版本必须只回答已支持指标，并明确拒答缺失指标。",
        "- 不能猜测缺失指标的数值、方向或结论。",
        "",
        "## 样本清单",
        "",
    ]
    for pair_id in sorted({row["metadata"].get("pair_id") for row in rows}):
        pair_rows = [row for row in rows if row["metadata"].get("pair_id") == pair_id]
        complete = next(row for row in pair_rows if row["metadata"]["data_type"] == "pairwise_complete_context")
        partial = next(row for row in pair_rows if row["metadata"]["data_type"] == "pairwise_partial_context_refusal")
        metadata = complete["metadata"]
        lines.extend(
            [
                f"### {len([line for line in lines if line.startswith('### ')]) + 1}. {pair_id}",
                "",
                f"- 完整样本：`{complete['metadata']['source_sample_id']}`",
                f"- 部分样本：`{partial['metadata']['source_sample_id']}`",
                f"- 复核重点：`{metadata['review_focus']}`",
                f"- 部分上下文缺失指标：`{partial['metadata'].get('missing_metrics', [])}`",
                f"- 来源训练样本：`{metadata['source_record_ids']}`",
                f"- 目标 source_id：`{metadata.get('target_source_id', '')}`",
                "",
                "**输入**",
                "",
                "```text",
                complete["input"],
                "```",
                "",
                "**完整上下文输出**",
                "",
                "```text",
                complete["output"],
                "```",
                "",
                "**部分上下文输出**",
                "",
                "```text",
                partial["output"],
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def prepare_e5_dataset(
    *,
    e4_train_path: Path,
    train_output_path: Path,
    summary_path: Path,
    report_path: Path,
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> dict[str, Any]:
    records = []
    for line_number, line in enumerate(e4_train_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError(f"{e4_train_path}:{line_number} is not a JSON object")
        records.append(record)
    rows = build_e5_rows(records)
    summary = summarize_rows(rows)
    summary.update(
        {
            "e4_train_path": str(e4_train_path),
            "train_output_path": str(train_output_path),
            "report_path": str(report_path),
        }
    )
    write_jsonl(train_output_path, rows)
    write_json(summary_path, summary)
    write_report(report_path, render_report(rows, summary))
    return {
        "summary": summary,
        "artifacts": {
            "train": str(train_output_path),
            "summary": str(summary_path),
            "report": str(report_path),
        },
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Build E5 pairwise context-contrast SFT data.")
    parser.add_argument("--e4-train", default=Path("finetune/datasets/localrag_sft_e4.jsonl"), type=Path)
    parser.add_argument("--train-output", default=Path("finetune/datasets/localrag_sft_e5.jsonl"), type=Path)
    parser.add_argument(
        "--summary",
        default=Path("results/finetune_data_audit/e5-dataset-summary.json"),
        type=Path,
    )
    parser.add_argument(
        "--report",
        default=Path("results/finetune_data_audit/e5-draft-review.md"),
        type=Path,
    )
    parser.add_argument("--dataset-version", default=DEFAULT_DATASET_VERSION)
    args = parser.parse_args()

    output = prepare_e5_dataset(
        e4_train_path=args.e4_train,
        train_output_path=args.train_output,
        summary_path=args.summary,
        report_path=args.report,
        dataset_version=args.dataset_version,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
