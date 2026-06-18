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


DEFAULT_DATASET_VERSION = "v1.3-e3-draft"
E3_INSTRUCTION = (
    "请根据给定参考资料回答问题，只能使用资料中的信息；"
    "如果资料只支持问题的一部分，只回答被资料支持的部分，并明确说明其余部分无法根据资料确定；"
    "不要补充参考资料之外的数字、方向性结论或 source_id；"
    "如果参考资料包含干扰内容，只引用真正支持答案的资料；"
    "答案末尾必须用“引用：”列出使用到的 source_id 和 locator。"
)


PARTIAL_CONTEXT_SPECS = [
    {
        "row_id": "e3-draft-partial-001",
        "source_id": "train-001",
        "question": "使用 4096 个 Top-K 查询时，MFA 延迟和 AP、ATE 指标分别发生什么变化？",
        "quote": "using 4096 size queries reduce the latency of MFA by 76.4%.",
        "answer": "资料只说明 4096 个查询会让 MFA 延迟降低 76.4%；没有给出 AP 或 ATE 指标变化，不能根据资料确定这些指标是提升还是下降。",
        "review_focus": "partial_context_numeric_no_guess",
    },
    {
        "row_id": "e3-draft-partial-002",
        "source_id": "train-004",
        "question": "CSDP 的 mask ratio=0.2 时，NDS、mAP 和 mATE 分别是多少？",
        "quote": "mask ratio 0.2 achieves the best result with NDS 58.5 and mAP 50.5.",
        "answer": "资料只说明 mask ratio 为 0.2 时 NDS 为 58.5、mAP 为 50.5；没有给出 mATE，不能根据资料确定 mATE 数值。",
        "review_focus": "partial_context_numeric_no_guess",
    },
    {
        "row_id": "e3-draft-partial-003",
        "source_id": "train-047",
        "question": "Cross-view Transformer 的推理速度、训练 GPU 小时和显存占用分别是多少？",
        "quote": "The model comfortably runs in real-time (35 FPS) on a single RTX 2080 Ti GPU and trains within 32 GPU hours.",
        "answer": "资料说明推理速度为 35 FPS，训练需要 32 GPU 小时；资料没有给出显存占用，不能根据资料确定显存数值。",
        "review_focus": "partial_context_numeric_no_guess",
    },
    {
        "row_id": "e3-draft-partial-004",
        "source_id": "train-052",
        "question": "GaussianOcc 的训练速度、渲染速度和 mIoU 分别提升了多少？",
        "quote": "GaussianOcc achieves competitive performance with 2.7 times faster training and 5 times faster rendering.",
        "answer": "资料说明 GaussianOcc 训练快 2.7 倍、渲染快 5 倍；资料没有给出 mIoU 提升数值，不能根据资料确定 mIoU 变化。",
        "review_focus": "partial_context_numeric_no_guess",
    },
    {
        "row_id": "e3-draft-partial-005",
        "source_id": "train-170",
        "question": "BEVDet4D-Base 的 NDS、mAP 和推理 FPS 分别是多少？",
        "quote": "BEVDet4D-Base achieves 54.5% NDS and 42.1% mAP at the same inference speed.",
        "answer": "资料说明 BEVDet4D-Base 的 NDS 为 54.5%，mAP 为 42.1%；资料只说推理速度相同，没有给出具体 FPS，不能根据资料确定 FPS 数值。",
        "review_focus": "partial_context_numeric_no_guess",
    },
    {
        "row_id": "e3-draft-partial-006",
        "source_id": "train-177",
        "question": "相机外参噪声等级为 4 时，BEVFormer 的 NDS 下降多少？AP 会下降多少？",
        "quote": "At noise level 4, BEVFormer drops 14.3% in NDS.",
        "answer": "资料说明噪声等级为 4 时 BEVFormer 的 NDS 下降 14.3%；资料没有给出 AP 下降数值，不能根据资料确定 AP 变化。",
        "review_focus": "partial_context_numeric_no_guess",
    },
    {
        "row_id": "e3-draft-partial-007",
        "source_id": "train-186",
        "question": "PointPillars 的运行速度、mAP 和内存占用分别是多少？",
        "quote": "PointPillars runs at 62 Hz and is 2-4 times faster than existing methods.",
        "answer": "资料说明 PointPillars 运行速度为 62 Hz，并比现有方法快 2-4 倍；资料没有给出 mAP 或内存占用，不能根据资料确定这些数值。",
        "review_focus": "partial_context_numeric_no_guess",
    },
    {
        "row_id": "e3-draft-partial-008",
        "source_id": "train-192",
        "question": "NHTSA 进口豁免计划自 2016 年 10 月以来批准了多少辆车？这些车辆的测试里程是多少？",
        "quote": "Since October 2016, 264 vehicles equipped with automated driving systems have received temporary import permission.",
        "answer": "资料说明自 2016 年 10 月以来有 264 辆配备自动驾驶系统的车辆获得临时进口许可；资料没有给出测试里程，不能根据资料确定里程数。",
        "review_focus": "partial_context_numeric_no_guess",
    },
]

STRICT_DISTRACTOR_SPECS = [
    {
        "row_id": "e3-draft-distractor-001",
        "target_id": "train-201",
        "distractor_id": "train-063",
        "question": "Apollo 感知融合模块的主要输出 channel 是什么？",
        "answer": "Apollo 感知融合模块的主要输出 channel 是 /apollo/perception/obstacles，用于输出多传感器融合后的障碍物信息。",
        "review_focus": "strict_target_only_citation",
    },
    {
        "row_id": "e3-draft-distractor-002",
        "target_id": "train-063",
        "distractor_id": "train-201",
        "question": "Apollo 预测模块至少有哪些输入 channel？",
        "answer": "Apollo 预测模块的输入 channel 包括 /apollo/perception/obstacles 和 /apollo/localization/pose。",
        "review_focus": "strict_target_only_citation",
    },
    {
        "row_id": "e3-draft-distractor-003",
        "target_id": "train-202",
        "distractor_id": "train-201",
        "question": "Apollo 控制模块有哪些输入 channel？",
        "answer": "Apollo 控制模块的输入 channel 包括 /Apollo/planning、/Apollo/localization/pose 和 /Apollo/canbus/chassis。",
        "review_focus": "strict_target_only_citation",
    },
    {
        "row_id": "e3-draft-distractor-004",
        "target_id": "train-060",
        "distractor_id": "train-177",
        "question": "Cross-view Transformer 如何利用相机内参和外参实现多相机到地图视图的映射？",
        "answer": "它为每个相机使用依赖内参和外参生成的位置嵌入，使 Transformer 在不显式建模几何关系的情况下学习不同视图之间的映射。",
        "review_focus": "strict_target_only_citation",
    },
    {
        "row_id": "e3-draft-distractor-005",
        "target_id": "train-177",
        "distractor_id": "train-060",
        "question": "相机外参噪声鲁棒性实验中，哪些因素提高了 BEVFormer 的鲁棒性？",
        "answer": "提高鲁棒性的因素包括在参考点周围采样特征的可变形注意力、融合时序信息，以及使用噪声外参训练模型。",
        "review_focus": "strict_target_only_citation",
    },
    {
        "row_id": "e3-draft-distractor-006",
        "target_id": "train-178",
        "distractor_id": "train-148",
        "question": "开发者如果要调整 Apollo 规划策略，应修改哪个配置路径？",
        "answer": "开发者可以调整 apollo/modules/planning/conf/scenario/ 下的配置文件，以调配任务组合实现自己的规划要求。",
        "review_focus": "strict_target_only_citation",
    },
    {
        "row_id": "e3-draft-distractor-007",
        "target_id": "train-164",
        "distractor_id": "train-184",
        "question": "BEVDet4D 如何融合前一帧和当前帧的特征？",
        "answer": "BEVDet4D 保留前一帧的中间 BEV 特征，再通过空间对齐操作和拼接操作，将前一帧特征与当前帧对应特征融合。",
        "review_focus": "strict_target_only_citation",
    },
    {
        "row_id": "e3-draft-distractor-008",
        "target_id": "train-184",
        "distractor_id": "train-164",
        "question": "StreamMapNet 采用哪种时序融合策略处理视频输入？",
        "answer": "StreamMapNet 采用 Streaming 策略，逐帧处理并跨时间传播隐藏状态以保留时序信息。",
        "review_focus": "strict_target_only_citation",
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


def _with_metadata(
    row: dict[str, Any],
    *,
    row_id: str,
    data_type: str,
    review_focus: str,
    source_record_ids: list[str],
    target_source_id: str,
) -> dict[str, Any]:
    metadata = row["metadata"]
    metadata["source_sample_id"] = row_id
    metadata["data_type"] = data_type
    metadata["dataset_version"] = DEFAULT_DATASET_VERSION
    metadata["review_focus"] = review_focus
    metadata["source_record_ids"] = source_record_ids
    metadata["target_source_id"] = target_source_id
    row["metadata"] = metadata
    return row


def build_partial_context_row(
    *,
    row_id: str,
    source_record: dict[str, Any],
    question: str,
    answer: str,
    review_focus: str,
    quote: str | None = None,
) -> dict[str, Any]:
    evidence = dict(_first_evidence(source_record))
    if quote is not None:
        evidence["quote"] = quote
    row = {
        "instruction": E3_INSTRUCTION,
        "input": _build_input(question, [evidence]),
        "output": f"{answer}\n\n引用：\n{_citation_lines([evidence])}",
        "metadata": {
            **source_record.get("metadata", {}),
            "expected_behavior": "partial_refuse",
        },
    }
    return _with_metadata(
        row,
        row_id=row_id,
        data_type="partial_context_insufficient_metric",
        review_focus=review_focus,
        source_record_ids=[str(source_record["id"])],
        target_source_id=evidence["source_id"],
    )


def build_strict_distractor_row(
    *,
    row_id: str,
    target_record: dict[str, Any],
    distractor_record: dict[str, Any],
    question: str,
    answer: str,
    review_focus: str,
) -> dict[str, Any]:
    target_evidence = _first_evidence(target_record)
    distractor_evidence = _first_evidence(distractor_record)
    row = {
        "instruction": E3_INSTRUCTION,
        "input": _build_input(question, [target_evidence, distractor_evidence]),
        "output": f"{answer}\n\n引用：\n{_citation_lines([target_evidence])}",
        "metadata": {
            **target_record.get("metadata", {}),
            "expected_behavior": "answer",
        },
    }
    return _with_metadata(
        row,
        row_id=row_id,
        data_type="strict_distractor_target_only_citation",
        review_focus=review_focus,
        source_record_ids=[str(target_record["id"]), str(distractor_record["id"])],
        target_source_id=target_evidence["source_id"],
    )


def build_e3_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = index_records(records)
    rows: list[dict[str, Any]] = []

    for spec in PARTIAL_CONTEXT_SPECS:
        rows.append(
            build_partial_context_row(
                row_id=spec["row_id"],
                source_record=by_id[spec["source_id"]],
                question=spec["question"],
                answer=spec["answer"],
                review_focus=spec["review_focus"],
                quote=spec["quote"],
            )
        )

    for spec in STRICT_DISTRACTOR_SPECS:
        rows.append(
            build_strict_distractor_row(
                row_id=spec["row_id"],
                target_record=by_id[spec["target_id"]],
                distractor_record=by_id[spec["distractor_id"]],
                question=spec["question"],
                answer=spec["answer"],
                review_focus=spec["review_focus"],
            )
        )

    return rows


def summarize_rows(rows: list[dict[str, Any]], generation_eval_ids: set[str]) -> dict[str, Any]:
    source_record_ids = [
        source_id
        for row in rows
        for source_id in row["metadata"].get("source_record_ids", [])
    ]
    e3_ids = [row["metadata"]["source_sample_id"] for row in rows]
    data_types = Counter(row["metadata"]["data_type"] for row in rows)
    review_focuses = Counter(row["metadata"]["review_focus"] for row in rows)
    eval_overlap = sorted(set(source_record_ids) & generation_eval_ids)
    duplicate_e3_ids = sorted(item for item, count in Counter(e3_ids).items() if count > 1)
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "dataset_version": DEFAULT_DATASET_VERSION,
        "record_count": len(rows),
        "data_type_distribution": dict(sorted(data_types.items())),
        "review_focus_distribution": dict(sorted(review_focuses.items())),
        "source_record_ids": sorted(set(source_record_ids)),
        "duplicate_e3_source_sample_ids": duplicate_e3_ids,
        "generation_eval_source_record_overlap": eval_overlap,
        "output_citation_count": sum(1 for row in rows if "引用：" in row["output"]),
        "input_source_marker_count": sum(1 for row in rows if "source_id=" in row["input"]),
        "input_locator_marker_count": sum(1 for row in rows if "locator=" in row["input"]),
    }


def render_review_report(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = [
        "# E3 数据草案人工复核表",
        "",
        "这不是正式训练记录，而是 E3 hard-case slice 的可复核草案。",
        "",
        "## 摘要",
        "",
        f"- 版本：`{summary['dataset_version']}`",
        f"- 样本数：`{summary['record_count']}`",
        f"- 数据类型分布：`{summary['data_type_distribution']}`",
        f"- generation_eval_set 源样本重叠：`{summary['generation_eval_source_record_overlap']}`",
        "",
        "## 复核标准",
        "",
        "- partial-context 样本：资料只支持部分问题时，回答只能覆盖已支持部分，并明确拒绝未给出的数字或方向性结论。",
        "- strict-distractor 样本：参考资料里有相似干扰段，答案只能引用目标资料，不能引用干扰 source_id。",
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


def prepare_e3_draft(
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
    rows = build_e3_rows(records)
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
    parser = argparse.ArgumentParser(description="Prepare a small auditable E3 SFT draft dataset.")
    parser.add_argument("--train-set", default=Path("data/evaluation/train/train_set.json"), type=Path)
    parser.add_argument(
        "--generation-eval-set",
        default=Path("data/evaluation/gold/generation_eval_set.json"),
        type=Path,
    )
    parser.add_argument(
        "--output",
        default=Path("finetune/datasets/localrag_sft_e3_draft.jsonl"),
        type=Path,
    )
    parser.add_argument(
        "--summary",
        default=Path("results/finetune_data_audit/e3-draft-summary.json"),
        type=Path,
    )
    parser.add_argument(
        "--review-report",
        default=Path("RAG_md/docs/finetune_e3_data_review.md"),
        type=Path,
    )
    args = parser.parse_args()

    output = prepare_e3_draft(
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
