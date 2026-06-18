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
from scripts.prepare_sft_dataset import DEFAULT_INSTRUCTION, build_llamafactory_record


DEFAULT_DATASET_VERSION = "v1.3-e2-draft"
E2_INSTRUCTION = (
    "请根据给定参考资料回答问题，只能使用资料中的信息；"
    "如果资料不足以支持问题中的任何具体结论，必须明确说明无法根据资料确定；"
    "如果参考资料包含干扰内容，只引用真正支持答案的资料；"
    "答案末尾必须用“引用：”列出使用到的 source_id 和 locator。"
)

REFUSAL_SPECS = [
    {
        "row_id": "e2-draft-refusal-001",
        "source_id": "train-001",
        "question": "资料是否说明使用 4096 个 Top-K 查询的稀疏聚合方案已经部署到量产车辆上？",
        "unsupported_focus": "量产车部署情况",
        "review_focus": "refusal_insufficient_context",
    },
    {
        "row_id": "e2-draft-refusal-002",
        "source_id": "train-085",
        "question": "资料是否给出了 SurroundOcc 生成 occupancy 标签时节省了多少人工标注成本？",
        "unsupported_focus": "人工标注成本金额",
        "review_focus": "refusal_insufficient_context",
    },
    {
        "row_id": "e2-draft-refusal-003",
        "source_id": "train-178",
        "question": "资料是否说明 Apollo 规划模块在不同 scenario 下的具体失败率？",
        "unsupported_focus": "不同 scenario 下的具体失败率",
        "review_focus": "refusal_insufficient_context",
    },
    {
        "row_id": "e2-draft-refusal-004",
        "source_id": "train-099",
        "question": "资料是否说明 ALKS 可以在允许行人和自行车混行的普通城市道路上激活？",
        "unsupported_focus": "允许在混行城市道路激活",
        "review_focus": "refusal_insufficient_context",
        "output": (
            "不能根据资料得出 ALKS 可以在允许行人和自行车混行的普通城市道路上激活。"
            "资料说明 ALKS 可在行人和自行车被禁止、且对向交通有物理隔离的道路条件下激活。"
        ),
    },
]

DISTRACTOR_SPECS = [
    {
        "row_id": "e2-draft-distractor-001",
        "target_id": "train-001",
        "distractor_id": "train-144",
        "question": "使用稀疏聚合时，把 Top-K 查询数从 All 减少到 4096，会让 MFA 延迟和 AP、ATE 指标发生什么变化？",
        "answer": "MFA 延迟降低 76.4%，从 21.01ms 降到 4.96ms；AP 从 56.9% 降到 54.0%，ATE 从 0.325 升到 0.367，说明延迟显著降低但检测回归相关指标下降。",
        "review_focus": "distractor_context_metric_change",
    },
    {
        "row_id": "e2-draft-distractor-002",
        "target_id": "train-178",
        "distractor_id": "train-136",
        "question": "Apollo 规划模块是如何按场景组织规划逻辑的？如果开发者要调整规划策略，应修改哪个配置路径？",
        "answer": "Apollo 规划模块基于场景（scenario-based）实现；开发者可以调整 apollo/modules/planning/conf/scenario/ 下的配置文件来调配任务组合。",
        "review_focus": "distractor_context_channel_or_module",
    },
    {
        "row_id": "e2-draft-distractor-003",
        "target_id": "train-045",
        "distractor_id": "train-038",
        "question": "Apollo 定位模块针对不同应用需求提供哪三种实现方式？",
        "answer": "Apollo 定位模块提供 RTK、MSF 和 NDT 三种实现方式。",
        "review_focus": "distractor_context_apollo_table",
    },
    {
        "row_id": "e2-draft-distractor-004",
        "target_id": "train-110",
        "distractor_id": "train-164",
        "question": "StreamPETR 与 BEV 时间方法的主要区别是什么？",
        "answer": "BEV 时间方法通常显式地将历史 BEV 特征 warp 到当前帧，用 BEV 特征做时序建模；StreamPETR 则使用稀疏 object queries 作为时间传播的 hidden states，进行 object-centric temporal modeling，以更好建模运动物体并保持效率。",
        "review_focus": "distractor_context_similar_topic",
    },
]

STRICT_CITATION_SPECS = [
    {
        "row_id": "e2-draft-citation-001",
        "source_id": "train-007",
        "review_focus": "strict_citation_short_answer",
    },
    {
        "row_id": "e2-draft-citation-002",
        "source_id": "train-003",
        "review_focus": "strict_citation_standard_doc",
        "answer": "基础设施拥有者和运营者负责道路基础设施的规划、设计、建设、维护和运营。他们希望获得更多关于如何为自动化车辆在公共道路上的部署和测试做准备的信息与指导。",
    },
    {
        "row_id": "e2-draft-citation-003",
        "source_id": "train-164",
        "review_focus": "strict_citation_temporal_fusion",
        "answer": "BEVDet4D 会保留前一帧的中间 BEV 特征，再通过空间对齐操作和拼接操作，将前一帧保留的特征与当前帧对应特征融合；除此之外，框架大部分细节保持不变。",
    },
    {
        "row_id": "e2-draft-citation-004",
        "source_id": "train-149",
        "review_focus": "strict_citation_long_answer",
        "answer": "FMSPnP 的全称是 fusion aided modality-aware prediction and status-aware planning modules。相比 UniAD，它采用层次金字塔结构，使所有任务都能从中间感知特征中受益；同时该模块还包含渐进式交互与精炼，以及基于融合的碰撞损失建模。",
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
    target_source_id: str | None = None,
) -> dict[str, Any]:
    metadata = row["metadata"]
    metadata["source_sample_id"] = row_id
    metadata["data_type"] = data_type
    metadata["dataset_version"] = DEFAULT_DATASET_VERSION
    metadata["review_focus"] = review_focus
    metadata["source_record_ids"] = source_record_ids
    if target_source_id:
        metadata["target_source_id"] = target_source_id
    row["metadata"] = metadata
    return row


def build_refusal_row(
    *,
    row_id: str,
    source_record: dict[str, Any],
    unsupported_question: str,
    unsupported_focus: str,
    review_focus: str,
    answer_text: str | None = None,
) -> dict[str, Any]:
    evidence = [_first_evidence(source_record)]
    source_id = str(source_record["id"])
    answer = answer_text or (
        f"无法根据资料确定{unsupported_focus}。参考资料只说明了与问题相关的部分信息，"
        "但没有提供该具体结论。"
    )
    output = f"{answer}\n\n引用：\n{_citation_lines(evidence)}"
    row = {
        "instruction": E2_INSTRUCTION,
        "input": _build_input(unsupported_question, evidence),
        "output": output,
        "metadata": {
            **source_record.get("metadata", {}),
            "expected_behavior": "refuse",
        },
    }
    return _with_metadata(
        row,
        row_id=row_id,
        data_type="refusal_insufficient_context",
        review_focus=review_focus,
        source_record_ids=[source_id],
        target_source_id=evidence[0]["source_id"],
    )


def build_distractor_row(
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
        "instruction": E2_INSTRUCTION,
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
        data_type="distractor_context",
        review_focus=review_focus,
        source_record_ids=[str(target_record["id"]), str(distractor_record["id"])],
        target_source_id=target_evidence["source_id"],
    )


def build_strict_citation_row(
    *,
    row_id: str,
    source_record: dict[str, Any],
    review_focus: str,
    answer_text: str | None = None,
) -> dict[str, Any]:
    if answer_text is not None:
        evidence = source_record["evidence"]
        row = {
            "instruction": E2_INSTRUCTION,
            "input": build_llamafactory_record(
                source_record,
                instruction=E2_INSTRUCTION,
                dataset_version=DEFAULT_DATASET_VERSION,
                data_type="strict_citation_grounded_qa",
            )["input"],
            "output": f"{answer_text}\n\n引用：\n{_citation_lines(evidence)}",
            "metadata": {
                **source_record.get("metadata", {}),
            },
        }
        return _with_metadata(
            row,
            row_id=row_id,
            data_type="strict_citation_grounded_qa",
            review_focus=review_focus,
            source_record_ids=[str(source_record["id"])],
            target_source_id=_first_evidence(source_record)["source_id"],
        )

    row = build_llamafactory_record(
        source_record,
        instruction=E2_INSTRUCTION,
        dataset_version=DEFAULT_DATASET_VERSION,
        data_type="strict_citation_grounded_qa",
    )
    return _with_metadata(
        row,
        row_id=row_id,
        data_type="strict_citation_grounded_qa",
        review_focus=review_focus,
        source_record_ids=[str(source_record["id"])],
        target_source_id=_first_evidence(source_record)["source_id"],
    )


def build_e2_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = index_records(records)
    rows: list[dict[str, Any]] = []

    for spec in REFUSAL_SPECS:
        rows.append(
            build_refusal_row(
                row_id=spec["row_id"],
                source_record=by_id[spec["source_id"]],
                unsupported_question=spec["question"],
                unsupported_focus=spec["unsupported_focus"],
                review_focus=spec["review_focus"],
                answer_text=spec.get("output"),
            )
        )

    for spec in DISTRACTOR_SPECS:
        rows.append(
            build_distractor_row(
                row_id=spec["row_id"],
                target_record=by_id[spec["target_id"]],
                distractor_record=by_id[spec["distractor_id"]],
                question=spec["question"],
                answer=spec["answer"],
                review_focus=spec["review_focus"],
            )
        )

    for spec in STRICT_CITATION_SPECS:
        rows.append(
            build_strict_citation_row(
                row_id=spec["row_id"],
                source_record=by_id[spec["source_id"]],
                review_focus=spec["review_focus"],
                answer_text=spec.get("answer"),
            )
        )

    return rows


def summarize_rows(rows: list[dict[str, Any]], generation_eval_ids: set[str]) -> dict[str, Any]:
    source_record_ids = [
        source_id
        for row in rows
        for source_id in row["metadata"].get("source_record_ids", [])
    ]
    e2_ids = [row["metadata"]["source_sample_id"] for row in rows]
    data_types = Counter(row["metadata"]["data_type"] for row in rows)
    review_focuses = Counter(row["metadata"]["review_focus"] for row in rows)
    eval_overlap = sorted(set(source_record_ids) & generation_eval_ids)
    duplicate_e2_ids = sorted(item for item, count in Counter(e2_ids).items() if count > 1)
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "dataset_version": DEFAULT_DATASET_VERSION,
        "record_count": len(rows),
        "data_type_distribution": dict(sorted(data_types.items())),
        "review_focus_distribution": dict(sorted(review_focuses.items())),
        "source_record_ids": sorted(set(source_record_ids)),
        "duplicate_e2_source_sample_ids": duplicate_e2_ids,
        "generation_eval_source_record_overlap": eval_overlap,
        "output_citation_count": sum(1 for row in rows if "引用：" in row["output"]),
        "input_source_marker_count": sum(1 for row in rows if "source_id=" in row["input"]),
        "input_locator_marker_count": sum(1 for row in rows if "locator=" in row["input"]),
    }


def render_review_report(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = [
        "# E2 数据草案人工复核表",
        "",
        "这不是正式 E2 训练集，而是给用户逐条复核的草案。",
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
        "- refusal 样本：问题问到资料没有支持的具体结论时，答案必须明确说无法根据资料确定。",
        "- distractor 样本：参考资料里有干扰段，答案只能引用真正支持答案的资料。",
        "- strict citation 样本：答案必须保留 `引用：`，且引用只能是 `source_id locator`，不能把正文塞进引用。",
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


def prepare_e2_draft(
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
    rows = build_e2_rows(records)
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
    parser = argparse.ArgumentParser(description="Prepare a small auditable E2 SFT draft dataset.")
    parser.add_argument("--train-set", default=Path("data/evaluation/train/train_set.json"), type=Path)
    parser.add_argument(
        "--generation-eval-set",
        default=Path("data/evaluation/gold/generation_eval_set.json"),
        type=Path,
    )
    parser.add_argument(
        "--output",
        default=Path("finetune/datasets/localrag_sft_e2_draft.jsonl"),
        type=Path,
    )
    parser.add_argument(
        "--summary",
        default=Path("results/finetune_data_audit/e2-draft-summary.json"),
        type=Path,
    )
    parser.add_argument(
        "--review-report",
        default=Path("RAG_md/docs/finetune_e2_data_review.md"),
        type=Path,
    )
    args = parser.parse_args()

    output = prepare_e2_draft(
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
