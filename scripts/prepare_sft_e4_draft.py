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


DEFAULT_DATASET_VERSION = "v1.3-e4-draft"
E4_INSTRUCTION = (
    "请根据给定参考资料回答问题，只能使用资料中的信息；"
    "当问题同时询问多个指标时，只回答资料明确支持的指标；"
    "对资料未给出的指标，必须明确说明无法根据资料确定，不能猜测数值、提升/下降方向或结论；"
    "不要补充参考资料之外的数字、方向性结论或 source_id；"
    "答案末尾必须用“引用：”列出使用到的 source_id 和 locator。"
)


MULTI_METRIC_PARTIAL_CONTEXT_SPECS = [
    {
        "row_id": "e4-draft-multi-metric-001",
        "source_id": "train-001",
        "question": "使用 4096 个 Top-K 查询时，MFA 延迟、AP 和 ATE 分别发生什么变化？",
        "quote": "using 4096 size queries reduce the latency of MFA by 76.4%.",
        "supported_claim": "资料只说明 4096 个查询会让 MFA 延迟降低 76.4%。",
        "missing_metrics": ["AP", "ATE"],
        "review_focus": "multi_metric_partial_context_no_direction_guess",
    },
    {
        "row_id": "e4-draft-multi-metric-002",
        "source_id": "train-004",
        "question": "CSDP 的 mask ratio=0.2 时，NDS、mAP 和 mATE 分别是多少？",
        "quote": "mask ratio 0.2 achieves the best result with NDS 58.5 and mAP 50.5.",
        "supported_claim": "资料只说明 mask ratio 为 0.2 时 NDS 为 58.5、mAP 为 50.5。",
        "missing_metrics": ["mATE"],
        "review_focus": "multi_metric_partial_context_no_missing_value_guess",
    },
    {
        "row_id": "e4-draft-multi-metric-003",
        "source_id": "train-047",
        "question": "Cross-view Transformer 的推理速度、训练 GPU 小时和显存占用分别是多少？",
        "quote": "The model comfortably runs in real-time (35 FPS) on a single RTX 2080 Ti GPU and trains within 32 GPU hours.",
        "supported_claim": "资料说明推理速度为 35 FPS，训练需要 32 GPU 小时。",
        "missing_metrics": ["显存占用"],
        "review_focus": "multi_metric_partial_context_no_missing_value_guess",
    },
    {
        "row_id": "e4-draft-multi-metric-004",
        "source_id": "train-052",
        "question": "GaussianOcc 的训练速度、渲染速度和 mIoU 分别提升了多少？",
        "quote": "GaussianOcc has low computational cost with 2.7 times faster training and 5 times faster rendering.",
        "supported_claim": "资料说明 GaussianOcc 训练快 2.7 倍、渲染快 5 倍。",
        "missing_metrics": ["mIoU"],
        "review_focus": "multi_metric_partial_context_no_metric_improvement_guess",
    },
    {
        "row_id": "e4-draft-multi-metric-005",
        "source_id": "train-170",
        "question": "BEVDet4D-Base 的 NDS、mAP 和推理 FPS 分别是多少？",
        "quote": "BEVDet4D-Base scores high as 42.1% mAP and 54.5% NDS.",
        "supported_claim": "资料说明 BEVDet4D-Base 的 NDS 为 54.5%，mAP 为 42.1%。",
        "missing_metrics": ["推理 FPS"],
        "review_focus": "multi_metric_partial_context_no_missing_speed_guess",
    },
    {
        "row_id": "e4-draft-multi-metric-006",
        "source_id": "train-177",
        "question": "相机外参噪声等级为 4 时，BEVFormer 的 NDS 和 AP 分别下降多少？",
        "quote": "with the noise level being 4, BEVFormer only drops 14.3% NDS.",
        "supported_claim": "资料说明噪声等级为 4 时 BEVFormer 的 NDS 下降 14.3%。",
        "missing_metrics": ["AP"],
        "review_focus": "multi_metric_partial_context_no_direction_guess",
    },
    {
        "row_id": "e4-draft-multi-metric-007",
        "source_id": "train-186",
        "question": "PointPillars 的运行速度、mAP 和内存占用分别是多少？",
        "quote": "This detection performance is achieved while running at 62 Hz: a 2-4 fold runtime improvement.",
        "supported_claim": "资料说明 PointPillars 运行速度为 62 Hz，并带来 2-4 倍运行速度提升。",
        "missing_metrics": ["mAP", "内存占用"],
        "review_focus": "multi_metric_partial_context_no_missing_value_guess",
    },
    {
        "row_id": "e4-draft-multi-metric-008",
        "source_id": "train-192",
        "question": "NHTSA 进口豁免计划自 2016 年 10 月以来批准了多少辆 ADS 车辆？这些车辆的测试里程是多少？",
        "quote": "Since October 2016, 264 ADS-equipped vehicles have received temporary import permission.",
        "supported_claim": "资料说明自 2016 年 10 月以来有 264 辆 ADS 车辆获得临时进口许可。",
        "missing_metrics": ["测试里程"],
        "review_focus": "multi_metric_partial_context_no_missing_value_guess",
    },
]


def load_records(path: Path) -> list[dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    validate_dataset(records)
    return records


def index_records(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record["id"]): record for record in records}


def _first_evidence(record: dict[str, Any]) -> dict[str, str]:
    return record["evidence"][0]


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


def build_multi_metric_partial_context_row(
    *,
    row_id: str,
    source_record: dict[str, Any],
    question: str,
    supported_claim: str,
    missing_metrics: list[str],
    review_focus: str,
    quote: str | None = None,
) -> dict[str, Any]:
    evidence = dict(_first_evidence(source_record))
    if quote is not None:
        evidence["quote"] = quote
    missing_text = _join_missing_metrics(missing_metrics)
    answer = f"{supported_claim}不能根据资料确定 {missing_text} 是提升还是下降，也不能补充未给出的数值。"
    return {
        "instruction": E4_INSTRUCTION,
        "input": _build_input(question, [evidence]),
        "output": f"{answer}\n\n引用：\n{_citation_lines([evidence])}",
        "metadata": {
            **source_record.get("metadata", {}),
            "source_sample_id": row_id,
            "data_type": "multi_metric_partial_context_refusal",
            "dataset_version": DEFAULT_DATASET_VERSION,
            "review_focus": review_focus,
            "source_record_ids": [str(source_record["id"])],
            "target_source_id": evidence["source_id"],
            "missing_metrics": missing_metrics,
            "expected_behavior": "partial_refuse",
        },
    }


def build_e4_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = index_records(records)
    return [
        build_multi_metric_partial_context_row(
            row_id=spec["row_id"],
            source_record=by_id[spec["source_id"]],
            question=spec["question"],
            supported_claim=spec["supported_claim"],
            missing_metrics=spec["missing_metrics"],
            review_focus=spec["review_focus"],
            quote=spec["quote"],
        )
        for spec in MULTI_METRIC_PARTIAL_CONTEXT_SPECS
    ]


def summarize_rows(rows: list[dict[str, Any]], generation_eval_ids: set[str]) -> dict[str, Any]:
    source_record_ids = [
        source_id
        for row in rows
        for source_id in row["metadata"].get("source_record_ids", [])
    ]
    e4_ids = [row["metadata"]["source_sample_id"] for row in rows]
    data_types = Counter(row["metadata"]["data_type"] for row in rows)
    review_focuses = Counter(row["metadata"]["review_focus"] for row in rows)
    missing_metrics = Counter(
        metric
        for row in rows
        for metric in row["metadata"].get("missing_metrics", [])
    )
    eval_overlap = sorted(set(source_record_ids) & generation_eval_ids)
    duplicate_e4_ids = sorted(item for item, count in Counter(e4_ids).items() if count > 1)
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "dataset_version": DEFAULT_DATASET_VERSION,
        "record_count": len(rows),
        "data_type_distribution": dict(sorted(data_types.items())),
        "review_focus_distribution": dict(sorted(review_focuses.items())),
        "missing_metric_distribution": dict(sorted(missing_metrics.items())),
        "source_record_ids": sorted(set(source_record_ids)),
        "duplicate_e4_source_sample_ids": duplicate_e4_ids,
        "generation_eval_source_record_overlap": eval_overlap,
        "output_citation_count": sum(1 for row in rows if "引用：" in row["output"]),
        "input_source_marker_count": sum(1 for row in rows if "source_id=" in row["input"]),
        "input_locator_marker_count": sum(1 for row in rows if "locator=" in row["input"]),
    }


def render_review_report(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = [
        "# E4 数据草案人工复核表",
        "",
        "这不是正式训练记录，而是 E4 multi-metric partial-context hard-case slice 的可复核草案。",
        "",
        "## 摘要",
        "",
        f"- 版本：`{summary['dataset_version']}`",
        f"- 样本数：`{summary['record_count']}`",
        f"- 数据类型分布：`{summary['data_type_distribution']}`",
        f"- 缺失指标分布：`{summary['missing_metric_distribution']}`",
        f"- generation_eval_set 源样本重叠：`{summary['generation_eval_source_record_overlap']}`",
        "",
        "## 复核标准",
        "",
        "- multi-metric partial-context 样本：问题同时询问多个指标，但资料只支持其中一部分。",
        "- 期望输出必须回答已支持指标，并明确说明缺失指标无法根据资料确定。",
        "- 期望输出不能猜测缺失指标的数值、提升/下降方向或结论。",
        "",
        "## 样本清单",
        "",
    ]
    for index, row in enumerate(rows, start=1):
        metadata = row["metadata"]
        lines.extend(
            [
                f"### {index}. {metadata['source_sample_id']}",
                "",
                f"- 类型：`{metadata['data_type']}`",
                f"- 复核重点：`{metadata['review_focus']}`",
                f"- 缺失指标：`{metadata.get('missing_metrics', [])}`",
                f"- 来源训练样本：`{metadata['source_record_ids']}`",
                f"- 目标 source_id：`{metadata.get('target_source_id', '')}`",
                "",
                "**输入**",
                "",
                "```text",
                row["input"],
                "```",
                "",
                "**期望输出**",
                "",
                "```text",
                row["output"],
                "```",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def prepare_e4_draft(
    *,
    train_set_path: Path,
    generation_eval_set_path: Path,
    output_path: Path,
    summary_path: Path,
    review_report_path: Path,
) -> dict[str, Any]:
    records = load_records(train_set_path)
    generation_eval_ids = {
        str(record["id"])
        for record in load_records(generation_eval_set_path)
    }
    rows = build_e4_rows(records)
    summary = summarize_rows(rows, generation_eval_ids)
    write_jsonl(output_path, rows)
    write_json(summary_path, summary)
    review_report_path.parent.mkdir(parents=True, exist_ok=True)
    review_report_path.write_text(render_review_report(rows, summary), encoding="utf-8")
    return {
        "summary": summary,
        "artifacts": {
            "dataset": str(output_path),
            "summary": str(summary_path),
            "review_report": str(review_report_path),
        },
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Prepare a focused auditable E4 SFT draft dataset.")
    parser.add_argument("--train-set", default=Path("data/evaluation/train/train_set.json"), type=Path)
    parser.add_argument(
        "--generation-eval-set",
        default=Path("data/evaluation/gold/generation_eval_set.json"),
        type=Path,
    )
    parser.add_argument(
        "--output",
        default=Path("finetune/datasets/localrag_sft_e4_draft.jsonl"),
        type=Path,
    )
    parser.add_argument(
        "--summary",
        default=Path("results/finetune_data_audit/e4-draft-summary.json"),
        type=Path,
    )
    parser.add_argument(
        "--review-report",
        default=Path("results/finetune_data_audit/e4-draft-review.md"),
        type=Path,
    )
    args = parser.parse_args()

    output = prepare_e4_draft(
        train_set_path=args.train_set,
        generation_eval_set_path=args.generation_eval_set,
        output_path=args.output,
        summary_path=args.summary,
        review_report_path=args.review_report,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
