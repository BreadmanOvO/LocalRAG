import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import prepare_sft_e6_dataset as e6


DEFAULT_DATASET_VERSION = "v1.3-e6.1"
E6_1_INSTRUCTION = (
    e6.E6_INSTRUCTION
    + " 对 OCR 黏连文本要特别注意：如果 channel 后面紧跟“输入是/对应/说明”，"
    + "该说明通常描述前一个 channel，不要跳到后一个相邻 channel。"
)


NOISY_PLANNING_CHANNEL_EVIDENCE = {
    "source_id": "apollo-doc-008",
    "locator": "unknown",
    "quote": (
        "1] 规划模块的输入输出 规划模块的输入 channel名称 输入channel说明 "
        "输入车身底盘反馈信息 /apollo/canbus/chassis "
        "输入车辆定位信息 /apollo/localization/pose "
        "/apollo/perception/traffic_light输入是 感知红绿灯信息 "
        "输入预测障碍物信息 /apollo/prediction "
        "局部地图信息 /apollo/relative_map "
        "/apollo/routing_response 输入导航routing信息 "
        "规划模块的输出 输出channel说明 channel名称 "
        "/apollo/planning输出自动驾驶车辆的轨迹信息"
    ),
}


NOISY_CHANNEL_ALIGNMENT_SPECS = [
    {
        "row_id": "e6-1-noisy-channel-001",
        "question": "这段 OCR 黏连文本中，“感知红绿灯信息”前面对应的规划输入 channel 是什么？",
        "answer": "“感知红绿灯信息”对应前面的规划输入 channel：/apollo/perception/traffic_light。",
        "required_terms": ["/apollo/perception/traffic_light"],
        "forbidden_terms": ["/apollo/prediction"],
        "review_focus": "noisy_same_row_planning_traffic_light_before_prediction",
    },
    {
        "row_id": "e6-1-noisy-channel-002",
        "question": "在“/apollo/perception/traffic_light输入是 感知红绿灯信息 输入预测障碍物信息 /apollo/prediction”这段里，感知红绿灯信息属于哪个 channel？",
        "answer": "感知红绿灯信息属于 /apollo/perception/traffic_light，不是后面的 /apollo/prediction。",
        "required_terms": ["/apollo/perception/traffic_light"],
        "forbidden_terms": [],
        "review_focus": "noisy_inline_planning_traffic_light_segment",
    },
    {
        "row_id": "e6-1-noisy-channel-003",
        "question": "如果问题问的是规划模块输入里的红绿灯信息，应从这段资料抽取哪个 channel？",
        "answer": "应抽取 /apollo/perception/traffic_light；该项说明的是感知红绿灯信息。",
        "required_terms": ["/apollo/perception/traffic_light"],
        "forbidden_terms": ["/apollo/prediction"],
        "review_focus": "noisy_same_row_planning_traffic_light_not_prediction",
    },
    {
        "row_id": "e6-1-noisy-channel-004",
        "question": "这段规划模块输入资料同时出现 traffic_light 和 prediction。与“感知红绿灯信息”同一项的是哪个 channel？",
        "answer": "与“感知红绿灯信息”同一项的是 /apollo/perception/traffic_light。",
        "required_terms": ["/apollo/perception/traffic_light"],
        "forbidden_terms": ["/apollo/prediction"],
        "review_focus": "noisy_same_row_planning_traffic_light_distractor",
    },
    {
        "row_id": "e6-1-noisy-channel-005",
        "question": "在规划模块输入列表里，/apollo/perception/traffic_light 这一项说明的是什么信息？",
        "answer": "/apollo/perception/traffic_light 这一项说明的是感知红绿灯信息。",
        "required_terms": ["/apollo/perception/traffic_light", "感知红绿灯信息"],
        "forbidden_terms": ["/apollo/prediction"],
        "review_focus": "noisy_reverse_lookup_planning_traffic_light",
    },
    {
        "row_id": "e6-1-noisy-channel-006",
        "question": "规划模块输入中的“输入预测障碍物信息”对应哪个 channel？",
        "answer": "“输入预测障碍物信息”对应 /apollo/prediction。",
        "required_terms": ["/apollo/prediction"],
        "forbidden_terms": ["/apollo/perception/traffic_light"],
        "review_focus": "noisy_same_row_planning_prediction",
    },
    {
        "row_id": "e6-1-noisy-channel-007",
        "question": "规划模块输入资料里，/apollo/prediction 这一项说明的是什么？",
        "answer": "/apollo/prediction 这一项说明的是输入预测障碍物信息。",
        "required_terms": ["/apollo/prediction", "预测障碍物信息"],
        "forbidden_terms": ["/apollo/perception/traffic_light"],
        "review_focus": "noisy_reverse_lookup_planning_prediction",
    },
    {
        "row_id": "e6-1-noisy-channel-008",
        "question": "规划模块输入中的局部地图信息和导航 routing 信息分别对应哪些 channel？",
        "answer": "局部地图信息对应 /apollo/relative_map；导航 routing 信息对应 /apollo/routing_response。",
        "required_terms": ["/apollo/relative_map", "/apollo/routing_response"],
        "forbidden_terms": ["/apollo/prediction"],
        "review_focus": "noisy_adjacent_planning_relative_map_routing",
    },
    {
        "row_id": "e6-1-noisy-channel-009",
        "question": "规划模块输入中的车辆定位信息对应哪个 channel？",
        "answer": "车辆定位信息对应 /apollo/localization/pose。",
        "required_terms": ["/apollo/localization/pose"],
        "forbidden_terms": ["/apollo/perception/traffic_light", "/apollo/prediction"],
        "review_focus": "noisy_same_row_planning_localization",
    },
    {
        "row_id": "e6-1-noisy-channel-010",
        "question": "规划模块输入中的车身底盘反馈信息对应哪个 channel？",
        "answer": "车身底盘反馈信息对应 /apollo/canbus/chassis。",
        "required_terms": ["/apollo/canbus/chassis"],
        "forbidden_terms": ["/apollo/localization/pose"],
        "review_focus": "noisy_same_row_planning_chassis",
    },
    {
        "row_id": "e6-1-noisy-channel-011",
        "question": "规划模块输出自动驾驶车辆轨迹信息时，应该引用输入表中的 prediction 还是输出表中的 planning channel？",
        "answer": "应引用输出表中的 /apollo/planning；它输出自动驾驶车辆的轨迹信息。",
        "required_terms": ["/apollo/planning"],
        "forbidden_terms": ["/apollo/prediction"],
        "review_focus": "noisy_input_output_boundary_planning_output",
    },
    {
        "row_id": "e6-1-noisy-channel-012",
        "question": "只根据这段资料，能否把“感知红绿灯信息”的 channel 说成 /apollo/prediction？",
        "answer": "不能。资料中“感知红绿灯信息”对应 /apollo/perception/traffic_light，/apollo/prediction 对应的是预测障碍物信息。",
        "required_terms": ["/apollo/perception/traffic_light"],
        "forbidden_terms": [],
        "review_focus": "noisy_explicit_contrast_traffic_light_prediction",
    },
]


def build_noisy_channel_alignment_row(
    spec: dict[str, Any],
    *,
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> dict[str, Any]:
    evidence = dict(NOISY_PLANNING_CHANNEL_EVIDENCE)
    return {
        "instruction": E6_1_INSTRUCTION,
        "input": e6._build_input(spec["question"], [evidence]),
        "output": f"{spec['answer']}\n\n引用：\n{e6._citation_lines([evidence])}",
        "metadata": {
            "source_sample_id": spec["row_id"],
            "data_type": "e6_1_noisy_table_channel_same_row",
            "dataset_version": dataset_version,
            "difficulty": "hard",
            "topic": "planning_control",
            "doc_type": "official_doc",
            "expected_behavior": "answer",
            "review_focus": spec["review_focus"],
            "source_record_ids": ["data/sources/apollo/apollo-vision-plan-overview.md"],
            "source_document": "data/sources/apollo/apollo-vision-plan-overview.md",
            "target_source_id": evidence["source_id"],
            "required_answer_terms": spec["required_terms"],
            "forbidden_answer_terms": spec["forbidden_terms"],
            "e6_source": "e6_1_noisy_retrieval_hardcase_slice",
        },
    }


def build_e6_1_hardcase_rows(*, dataset_version: str = DEFAULT_DATASET_VERSION) -> list[dict[str, Any]]:
    hardcases = e6.build_e6_hardcase_rows(dataset_version=dataset_version)
    hardcases.extend(
        build_noisy_channel_alignment_row(spec, dataset_version=dataset_version)
        for spec in NOISY_CHANNEL_ALIGNMENT_SPECS
    )
    return hardcases


def render_report(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    report = e6.render_report(rows, summary)
    return report.replace(
        "# E6 表格 channel 精确抽取数据报告",
        "# E6.1 表格 channel 精确抽取数据报告",
        1,
    ).replace(
        "E6 目标是修复 E5.1 剩余的 Apollo channel 相邻行干扰问题。",
        "E6.1 目标是在 E6 未关闭 gen-eval-007 后，补齐更接近真实检索 chunk 的 OCR 黏连 channel 样本。",
        1,
    )


def prepare_e6_1_dataset(
    *,
    e5_train_path: Path,
    e5_validation_path: Path,
    train_output_path: Path,
    validation_output_path: Path,
    summary_path: Path,
    report_path: Path,
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> dict[str, Any]:
    e5_rows = e6.load_jsonl(e5_train_path)
    e5_validation_rows = e6.load_jsonl(e5_validation_path)
    hardcase_rows = build_e6_1_hardcase_rows(dataset_version=dataset_version)
    train_rows = e6.build_e6_train_rows(
        e5_rows=e5_rows,
        hardcase_rows=hardcase_rows,
        dataset_version=dataset_version,
    )
    validation_rows = e6.build_e6_validation_rows(
        e5_validation_rows=e5_validation_rows,
        dataset_version=dataset_version,
    )
    summary = e6.summarize(
        train_rows,
        validation_rows,
        hardcase_rows,
        dataset_version=dataset_version,
    )
    summary.update(
        {
            "e5_train_path": str(e5_train_path),
            "e5_validation_path": str(e5_validation_path),
            "train_output_path": str(train_output_path),
            "validation_output_path": str(validation_output_path),
            "report_path": str(report_path),
            "e6_1_noisy_hardcase_count": len(NOISY_CHANNEL_ALIGNMENT_SPECS),
        }
    )
    e6.write_jsonl(train_output_path, train_rows)
    e6.write_jsonl(validation_output_path, validation_rows)
    e6.write_json(summary_path, summary)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(hardcase_rows, summary), encoding="utf-8")
    return {
        "summary": summary,
        "artifacts": {
            "train": str(train_output_path),
            "validation": str(validation_output_path),
            "summary": str(summary_path),
            "report": str(report_path),
        },
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Build E6.1 noisy table/channel alignment SFT data.")
    parser.add_argument("--e5-train", default=Path("finetune/datasets/localrag_sft_e5.jsonl"), type=Path)
    parser.add_argument(
        "--e5-validation",
        default=Path("finetune/datasets/localrag_sft_e5_validation.jsonl"),
        type=Path,
    )
    parser.add_argument("--train-output", default=Path("finetune/datasets/localrag_sft_e6_1.jsonl"), type=Path)
    parser.add_argument(
        "--validation-output",
        default=Path("finetune/datasets/localrag_sft_e6_1_validation.jsonl"),
        type=Path,
    )
    parser.add_argument(
        "--summary",
        default=Path("results/finetune_data_audit/e6_1-dataset-summary.json"),
        type=Path,
    )
    parser.add_argument(
        "--report",
        default=Path("results/finetune_data_audit/e6_1-draft-review.md"),
        type=Path,
    )
    parser.add_argument("--dataset-version", default=DEFAULT_DATASET_VERSION)
    args = parser.parse_args()

    output = prepare_e6_1_dataset(
        e5_train_path=args.e5_train,
        e5_validation_path=args.e5_validation,
        train_output_path=args.train_output,
        validation_output_path=args.validation_output,
        summary_path=args.summary,
        report_path=args.report,
        dataset_version=args.dataset_version,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
