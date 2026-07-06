import argparse
import copy
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


DEFAULT_DATASET_VERSION = "v1.3-e6"
E6_INSTRUCTION = (
    "请根据给定参考资料回答问题，只能使用资料中的信息；"
    "当参考资料是表格、列表或 key-value 形式时，必须根据问题中的字段说明找到同一行对应的 channel 或字段值；"
    "不要选择相邻行、同段落中的干扰 channel，或其他模块的输出 channel；"
    "答案应简洁直接，答案末尾必须用“引用：”列出使用到的 source_id 和 locator。"
)


PLANNING_CHANNEL_EVIDENCE = {
    "source_id": "apollo-doc-008",
    "locator": "page=1",
    "quote": (
        "规划模块的输入 channel名称 输入channel说明 "
        "输入车身底盘反馈信息 /apollo/canbus/chassis "
        "输入车辆定位信息 /apollo/localization/pose "
        "/apollo/perception/traffic_light 输入是感知红绿灯信息 "
        "输入预测障碍物信息 /apollo/prediction "
        "局部地图信息 /apollo/relative_map "
        "/apollo/routing_response 输入导航routing信息 "
        "规划模块的输出 输出channel说明 channel名称 "
        "/apollo/planning 输出自动驾驶车辆的轨迹信息"
    ),
}

PREDICTION_CHANNEL_EVIDENCE = {
    "source_id": "apollo-doc-007",
    "locator": "page=1",
    "quote": (
        "预测模块的输入输出 channel名称 输入输出channel说明 "
        "/apollo/perception/obstacles 输入感知信息，包含障碍物的位置、朝向、速度、加速度 "
        "/apollo/localization/pose 定位信息，自车的位置、速度信息 "
        "/apollo/planning 规划信息，自车规划的轨迹信息 "
        "/apollo/prediction 预测轨迹，包含障碍物在预测时域内的未来轨迹信息"
    ),
}

FUSION_CHANNEL_EVIDENCE = {
    "source_id": "apollo-doc-005",
    "locator": "page=1",
    "quote": (
        "感知融合模块的相关参数 channel名称 channel说明 "
        "统一输入channel：各传感器感知的结果都会输出到 /perception/inner/PrefusedObjects，"
        "作为感知融合模块的源数据。"
        "感知融合模块的主要输出channel 是 /apollo/perception/obstacles，"
        "该 channel 输出的是多传感器融合之后的障碍物信息。"
    ),
}

CONTROL_CHANNEL_EVIDENCE = {
    "source_id": "apollo-doc-009",
    "locator": "page=1",
    "quote": (
        "控制模块输入channel 控制模块有三个输入channel："
        "/Apollo/planning 规划信息，自车规划的轨迹信息 "
        "/Apollo/localization/pose 定位信息，自车的位置 "
        "/Apollo/canbus/chassis 底盘信息，自车的方向盘、速度信息 "
        "控制模块输出channel 控制模块有一个输出channel："
        "/Apollo/control 输出控制信息，方向盘角度、油门刹车"
    ),
}

CYBERRT_FIELD_EVIDENCE = {
    "source_id": "apollo-doc-003",
    "locator": "page=1",
    "quote": (
        "打开 CyberMonitor 并进入特定数据通道，可以看到每个 Channel 中都有 "
        "ChannelName、MessageType、FrameRatio、MessageSize 数据字段。"
        "ChannelName 是数据通道的名字；MessageType 是通道内数据的消息类型；"
        "FrameRatio 是数据更新频率；MessageSize 是原始数据的大小。"
    ),
}


CHANNEL_ALIGNMENT_SPECS = [
    {
        "row_id": "e6-channel-001",
        "question": "在规划模块输入表中，标注为“感知红绿灯信息”的 channel 是哪一个？",
        "answer": "标注为“感知红绿灯信息”的规划输入 channel 是 /apollo/perception/traffic_light。",
        "evidence": PLANNING_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/perception/traffic_light"],
        "forbidden_terms": ["/apollo/prediction"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_planning_traffic_light",
        "source_document": "data/sources/apollo/apollo-vision-plan-overview.md",
    },
    {
        "row_id": "e6-channel-002",
        "question": "规划模块输入表里，预测障碍物信息对应哪个 channel？",
        "answer": "预测障碍物信息对应的规划输入 channel 是 /apollo/prediction。",
        "evidence": PLANNING_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/prediction"],
        "forbidden_terms": ["/apollo/perception/traffic_light"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_planning_prediction",
        "source_document": "data/sources/apollo/apollo-vision-plan-overview.md",
    },
    {
        "row_id": "e6-channel-003",
        "question": "规划模块输入表中，车辆定位信息对应哪个 channel？",
        "answer": "车辆定位信息对应的规划输入 channel 是 /apollo/localization/pose。",
        "evidence": PLANNING_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/localization/pose"],
        "forbidden_terms": ["/apollo/canbus/chassis", "/apollo/perception/traffic_light"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_planning_localization",
        "source_document": "data/sources/apollo/apollo-vision-plan-overview.md",
    },
    {
        "row_id": "e6-channel-004",
        "question": "规划模块输入表中，局部地图信息对应哪个 channel？",
        "answer": "局部地图信息对应的规划输入 channel 是 /apollo/relative_map。",
        "evidence": PLANNING_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/relative_map"],
        "forbidden_terms": ["/apollo/routing_response"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_planning_relative_map",
        "source_document": "data/sources/apollo/apollo-vision-plan-overview.md",
    },
    {
        "row_id": "e6-channel-005",
        "question": "规划模块输入表中，导航 routing 信息对应哪个 channel？",
        "answer": "导航 routing 信息对应的规划输入 channel 是 /apollo/routing_response。",
        "evidence": PLANNING_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/routing_response"],
        "forbidden_terms": ["/apollo/relative_map"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_planning_routing",
        "source_document": "data/sources/apollo/apollo-vision-plan-overview.md",
    },
    {
        "row_id": "e6-channel-006",
        "question": "规划模块输出自动驾驶车辆轨迹信息时使用哪个 channel？",
        "answer": "规划模块输出自动驾驶车辆轨迹信息时使用 /apollo/planning。",
        "evidence": PLANNING_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/planning"],
        "forbidden_terms": ["/apollo/prediction", "/apollo/routing_response"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_planning_output",
        "source_document": "data/sources/apollo/apollo-vision-plan-overview.md",
    },
    {
        "row_id": "e6-channel-007",
        "question": "预测模块输入表中，感知信息对应哪个 channel？",
        "answer": "预测模块输入表中，感知信息对应 /apollo/perception/obstacles。",
        "evidence": PREDICTION_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/perception/obstacles"],
        "forbidden_terms": ["/apollo/prediction"],
        "topic": "perception",
        "review_focus": "same_row_channel_alignment_prediction_obstacles",
        "source_document": "data/sources/apollo/apollo-vision-prediction-overview.md",
    },
    {
        "row_id": "e6-channel-008",
        "question": "预测模块输入表中，自车的位置和速度信息对应哪个 channel？",
        "answer": "自车的位置和速度信息对应 /apollo/localization/pose。",
        "evidence": PREDICTION_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/localization/pose"],
        "forbidden_terms": ["/apollo/perception/obstacles", "/apollo/planning"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_prediction_localization",
        "source_document": "data/sources/apollo/apollo-vision-prediction-overview.md",
    },
    {
        "row_id": "e6-channel-009",
        "question": "预测模块输入表中，自车规划的轨迹信息对应哪个 channel？",
        "answer": "自车规划的轨迹信息对应 /apollo/planning。",
        "evidence": PREDICTION_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/planning"],
        "forbidden_terms": ["/apollo/prediction"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_prediction_planning_input",
        "source_document": "data/sources/apollo/apollo-vision-prediction-overview.md",
    },
    {
        "row_id": "e6-channel-010",
        "question": "预测模块输出障碍物未来预测轨迹时对应哪个 channel？",
        "answer": "预测模块输出障碍物未来预测轨迹时对应 /apollo/prediction。",
        "evidence": PREDICTION_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/prediction"],
        "forbidden_terms": ["/apollo/planning", "/apollo/perception/obstacles"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_prediction_output",
        "source_document": "data/sources/apollo/apollo-vision-prediction-overview.md",
    },
    {
        "row_id": "e6-channel-011",
        "question": "感知融合模块的统一输入 channel 是哪一个？",
        "answer": "感知融合模块的统一输入 channel 是 /perception/inner/PrefusedObjects。",
        "evidence": FUSION_CHANNEL_EVIDENCE,
        "required_terms": ["/perception/inner/PrefusedObjects"],
        "forbidden_terms": ["/apollo/perception/obstacles"],
        "topic": "sensor_fusion",
        "review_focus": "same_row_channel_alignment_fusion_input",
        "source_document": "data/sources/apollo/apollo-perception-fusion-overview.md",
    },
    {
        "row_id": "e6-channel-012",
        "question": "感知融合模块的主要输出 channel 是哪一个？",
        "answer": "感知融合模块的主要输出 channel 是 /apollo/perception/obstacles。",
        "evidence": FUSION_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/perception/obstacles"],
        "forbidden_terms": ["/perception/inner/PrefusedObjects"],
        "topic": "sensor_fusion",
        "review_focus": "same_row_channel_alignment_fusion_output",
        "source_document": "data/sources/apollo/apollo-perception-fusion-overview.md",
    },
    {
        "row_id": "e6-channel-013",
        "question": "各传感器感知结果会输出到哪个 channel 作为感知融合模块的源数据？",
        "answer": "各传感器感知结果会输出到 /perception/inner/PrefusedObjects，作为感知融合模块的源数据。",
        "evidence": FUSION_CHANNEL_EVIDENCE,
        "required_terms": ["/perception/inner/PrefusedObjects"],
        "forbidden_terms": ["/apollo/perception/obstacles"],
        "topic": "sensor_fusion",
        "review_focus": "same_row_channel_alignment_fusion_source_data",
        "source_document": "data/sources/apollo/apollo-perception-fusion-overview.md",
    },
    {
        "row_id": "e6-channel-014",
        "question": "多传感器融合后的障碍物信息由哪个 channel 输出？",
        "answer": "多传感器融合后的障碍物信息由 /apollo/perception/obstacles 输出。",
        "evidence": FUSION_CHANNEL_EVIDENCE,
        "required_terms": ["/apollo/perception/obstacles"],
        "forbidden_terms": ["/perception/inner/PrefusedObjects"],
        "topic": "sensor_fusion",
        "review_focus": "same_row_channel_alignment_fusion_obstacle_output",
        "source_document": "data/sources/apollo/apollo-perception-fusion-overview.md",
    },
    {
        "row_id": "e6-channel-015",
        "question": "控制模块输入表中，底盘信息对应哪个 channel？",
        "answer": "控制模块输入表中，底盘信息对应 /Apollo/canbus/chassis。",
        "evidence": CONTROL_CHANNEL_EVIDENCE,
        "required_terms": ["/Apollo/canbus/chassis"],
        "forbidden_terms": ["/Apollo/control", "/Apollo/planning"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_control_chassis",
        "source_document": "data/sources/apollo/apollo-vision-control-overview.md",
    },
    {
        "row_id": "e6-channel-016",
        "question": "控制模块输出方向盘角度、油门刹车控制信息时使用哪个 channel？",
        "answer": "控制模块输出方向盘角度、油门刹车控制信息时使用 /Apollo/control。",
        "evidence": CONTROL_CHANNEL_EVIDENCE,
        "required_terms": ["/Apollo/control"],
        "forbidden_terms": ["/Apollo/canbus/chassis", "/Apollo/planning"],
        "topic": "planning_control",
        "review_focus": "same_row_channel_alignment_control_output",
        "source_document": "data/sources/apollo/apollo-vision-control-overview.md",
    },
    {
        "row_id": "e6-channel-017",
        "question": "CyberRT Channel 数据字段里，表示数据通道名字的是哪个字段？",
        "answer": "表示数据通道名字的字段是 ChannelName。",
        "evidence": CYBERRT_FIELD_EVIDENCE,
        "required_terms": ["ChannelName"],
        "forbidden_terms": ["MessageType", "FrameRatio", "MessageSize"],
        "topic": "system_architecture",
        "review_focus": "key_value_field_alignment_cyberrt_channel_name",
        "source_document": "data/sources/apollo/apollo-channel-data-format.md",
    },
    {
        "row_id": "e6-channel-018",
        "question": "CyberRT Channel 数据字段里，表示通道内数据消息类型的是哪个字段？",
        "answer": "表示通道内数据消息类型的字段是 MessageType。",
        "evidence": CYBERRT_FIELD_EVIDENCE,
        "required_terms": ["MessageType"],
        "forbidden_terms": ["ChannelName", "FrameRatio", "MessageSize"],
        "topic": "system_architecture",
        "review_focus": "key_value_field_alignment_cyberrt_message_type",
        "source_document": "data/sources/apollo/apollo-channel-data-format.md",
    },
    {
        "row_id": "e6-channel-019",
        "question": "CyberRT Channel 数据字段里，表示数据更新频率的是哪个字段？",
        "answer": "表示数据更新频率的字段是 FrameRatio。",
        "evidence": CYBERRT_FIELD_EVIDENCE,
        "required_terms": ["FrameRatio"],
        "forbidden_terms": ["ChannelName", "MessageType", "MessageSize"],
        "topic": "system_architecture",
        "review_focus": "key_value_field_alignment_cyberrt_frame_ratio",
        "source_document": "data/sources/apollo/apollo-channel-data-format.md",
    },
    {
        "row_id": "e6-channel-020",
        "question": "CyberRT Channel 数据字段里，表示原始数据大小的是哪个字段？",
        "answer": "表示原始数据大小的字段是 MessageSize。",
        "evidence": CYBERRT_FIELD_EVIDENCE,
        "required_terms": ["MessageSize"],
        "forbidden_terms": ["ChannelName", "MessageType", "FrameRatio"],
        "topic": "system_architecture",
        "review_focus": "key_value_field_alignment_cyberrt_message_size",
        "source_document": "data/sources/apollo/apollo-channel-data-format.md",
    },
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number} is not a JSON object")
        rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


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


def _clone_with_e6_metadata(
    row: dict[str, Any],
    *,
    dataset_version: str,
    e6_source: str,
) -> dict[str, Any]:
    cloned = copy.deepcopy(row)
    metadata = cloned.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    metadata["dataset_version"] = dataset_version
    metadata["e6_source"] = e6_source
    cloned["metadata"] = metadata
    return cloned


def build_channel_alignment_row(spec: dict[str, Any], *, dataset_version: str = DEFAULT_DATASET_VERSION) -> dict[str, Any]:
    evidence = dict(spec["evidence"])
    metadata = {
        "source_sample_id": spec["row_id"],
        "data_type": "e6_table_channel_same_row",
        "dataset_version": dataset_version,
        "difficulty": "hard",
        "topic": spec["topic"],
        "doc_type": "official_doc",
        "expected_behavior": "answer",
        "review_focus": spec["review_focus"],
        "source_record_ids": [spec["source_document"]],
        "source_document": spec["source_document"],
        "target_source_id": evidence["source_id"],
        "required_answer_terms": spec["required_terms"],
        "forbidden_answer_terms": spec["forbidden_terms"],
        "e6_source": "e6_table_channel_hardcase_slice",
    }
    if spec["row_id"].startswith(("e6-channel-017", "e6-channel-018", "e6-channel-019", "e6-channel-020")):
        metadata["data_type"] = "e6_key_value_field_alignment"

    return {
        "instruction": E6_INSTRUCTION,
        "input": _build_input(spec["question"], [evidence]),
        "output": f"{spec['answer']}\n\n引用：\n{_citation_lines([evidence])}",
        "metadata": metadata,
    }


def build_e6_hardcase_rows(*, dataset_version: str = DEFAULT_DATASET_VERSION) -> list[dict[str, Any]]:
    return [
        build_channel_alignment_row(spec, dataset_version=dataset_version)
        for spec in CHANNEL_ALIGNMENT_SPECS
    ]


def build_e6_train_rows(
    *,
    e5_rows: list[dict[str, Any]],
    hardcase_rows: list[dict[str, Any]],
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> list[dict[str, Any]]:
    prior_rows = [
        _clone_with_e6_metadata(row, dataset_version=dataset_version, e6_source="e5_training_mix")
        for row in e5_rows
    ]
    return prior_rows + hardcase_rows


def build_e6_validation_rows(
    *,
    e5_validation_rows: list[dict[str, Any]],
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> list[dict[str, Any]]:
    return [
        _clone_with_e6_metadata(row, dataset_version=dataset_version, e6_source="e5_validation_holdout")
        for row in e5_validation_rows
    ]


def _source_sample_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {
        str(row.get("metadata", {}).get("source_sample_id", ""))
        for row in rows
        if row.get("metadata", {}).get("source_sample_id")
    }


def summarize(
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    hardcase_rows: list[dict[str, Any]],
    *,
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> dict[str, Any]:
    train_data_types = Counter(str(row.get("metadata", {}).get("data_type", "")) for row in train_rows)
    validation_data_types = Counter(str(row.get("metadata", {}).get("data_type", "")) for row in validation_rows)
    review_focuses = Counter(str(row.get("metadata", {}).get("review_focus", "")) for row in hardcase_rows)
    target_source_ids = Counter(str(row.get("metadata", {}).get("target_source_id", "")) for row in hardcase_rows)
    required_terms = Counter(
        term
        for row in hardcase_rows
        for term in row.get("metadata", {}).get("required_answer_terms", [])
    )
    forbidden_terms = Counter(
        term
        for row in hardcase_rows
        for term in row.get("metadata", {}).get("forbidden_answer_terms", [])
    )
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "dataset_version": dataset_version,
        "train_count": len(train_rows),
        "validation_count": len(validation_rows),
        "e5_prior_train_count": len(train_rows) - len(hardcase_rows),
        "e6_hardcase_count": len(hardcase_rows),
        "train_data_type_distribution": dict(sorted(train_data_types.items())),
        "validation_data_type_distribution": dict(sorted(validation_data_types.items())),
        "e6_review_focus_distribution": dict(sorted(review_focuses.items())),
        "e6_target_source_id_distribution": dict(sorted(target_source_ids.items())),
        "e6_required_term_distribution": dict(sorted(required_terms.items())),
        "e6_forbidden_term_distribution": dict(sorted(forbidden_terms.items())),
        "e6_hardcase_source_sample_ids": sorted(_source_sample_ids(hardcase_rows)),
        "train_validation_source_sample_overlap": sorted(_source_sample_ids(train_rows) & _source_sample_ids(validation_rows)),
        "train_output_citation_count": sum(1 for row in train_rows if "引用：" in row.get("output", "")),
        "validation_output_citation_count": sum(1 for row in validation_rows if "引用：" in row.get("output", "")),
    }


def render_report(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = [
        "# E6 表格 channel 精确抽取数据报告",
        "",
        "E6 目标是修复 E5.1 剩余的 Apollo channel 相邻行干扰问题。",
        "这些样本强调按问题中的说明字段定位同一行 channel，不能被邻近 channel 或其他模块输出带偏。",
        "",
        "## 摘要",
        "",
        f"- 版本：`{summary['dataset_version']}`",
        f"- 训练样本数：`{summary['train_count']}`",
        f"- E5 保留样本数：`{summary['e5_prior_train_count']}`",
        f"- E6 hardcase 样本数：`{summary['e6_hardcase_count']}`",
        f"- 验证样本数：`{summary['validation_count']}`",
        f"- 训练数据类型分布：`{summary['train_data_type_distribution']}`",
        "",
        "## 设计原则",
        "",
        "- 继续保留 E5 的 pairwise 数值/方向拒答样本，避免 E6 覆盖掉已修复能力。",
        "- E6 hardcase 只训练表格、channel、key-value 的字段对齐行为。",
        "- 每条 hardcase 都写入 `required_answer_terms` 和 `forbidden_answer_terms`，便于后续 gate 复核。",
        "",
        "## E6 Hardcase 清单",
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
                f"- 目标 source_id：`{metadata['target_source_id']}`",
                f"- 必须包含：`{metadata['required_answer_terms']}`",
                f"- 禁止包含：`{metadata['forbidden_answer_terms']}`",
                f"- 来源文档：`{metadata['source_document']}`",
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


def prepare_e6_dataset(
    *,
    e5_train_path: Path,
    e5_validation_path: Path,
    train_output_path: Path,
    validation_output_path: Path,
    summary_path: Path,
    report_path: Path,
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> dict[str, Any]:
    e5_rows = load_jsonl(e5_train_path)
    e5_validation_rows = load_jsonl(e5_validation_path)
    hardcase_rows = build_e6_hardcase_rows(dataset_version=dataset_version)
    train_rows = build_e6_train_rows(
        e5_rows=e5_rows,
        hardcase_rows=hardcase_rows,
        dataset_version=dataset_version,
    )
    validation_rows = build_e6_validation_rows(
        e5_validation_rows=e5_validation_rows,
        dataset_version=dataset_version,
    )
    summary = summarize(
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
        }
    )
    write_jsonl(train_output_path, train_rows)
    write_jsonl(validation_output_path, validation_rows)
    write_json(summary_path, summary)
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
    parser = argparse.ArgumentParser(description="Build E6 table/channel alignment SFT data.")
    parser.add_argument("--e5-train", default=Path("finetune/datasets/localrag_sft_e5.jsonl"), type=Path)
    parser.add_argument(
        "--e5-validation",
        default=Path("finetune/datasets/localrag_sft_e5_validation.jsonl"),
        type=Path,
    )
    parser.add_argument("--train-output", default=Path("finetune/datasets/localrag_sft_e6.jsonl"), type=Path)
    parser.add_argument(
        "--validation-output",
        default=Path("finetune/datasets/localrag_sft_e6_validation.jsonl"),
        type=Path,
    )
    parser.add_argument(
        "--summary",
        default=Path("results/finetune_data_audit/e6-dataset-summary.json"),
        type=Path,
    )
    parser.add_argument(
        "--report",
        default=Path("results/finetune_data_audit/e6-draft-review.md"),
        type=Path,
    )
    parser.add_argument("--dataset-version", default=DEFAULT_DATASET_VERSION)
    args = parser.parse_args()

    output = prepare_e6_dataset(
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
