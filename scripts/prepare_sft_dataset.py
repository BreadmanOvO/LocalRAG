import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.evaluation.shared.eval_schema import validate_dataset


DEFAULT_SYSTEM_PROMPT = (
    "你是自动驾驶感知算法领域的 RAG 助手。回答必须只依据用户提供的证据；"
    "证据不足时要明确说明无法从给定证据确认，不要编造。"
)
DEFAULT_INSTRUCTION = (
    "请根据给定参考资料回答问题，只能使用资料中的信息；"
    "资料不足时请说明无法确定。"
)


def load_records(path: Path) -> list[dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    validate_dataset(records)
    return records


def build_user_prompt(record: dict[str, Any]) -> str:
    evidence_blocks = []
    for index, item in enumerate(record["evidence"], start=1):
        evidence_blocks.append(
            "\n".join(
                [
                    f"[{index}] source_id={item['source_id']} locator={item['locator']}",
                    item["quote"],
                ]
            )
        )
    evidence_text = "\n\n".join(evidence_blocks)
    return (
        f"问题：{record['question']}\n\n"
        f"可用证据：\n{evidence_text}\n\n"
        "请基于证据给出简洁回答，并在答案末尾列出引用。"
    )


def build_assistant_message(record: dict[str, Any]) -> str:
    citations = "\n".join(
        f"- {item['source_id']} {item['locator']}" for item in record["evidence"]
    )
    return f"{record['reference_answer']}\n\n引用：\n{citations}"


def build_sft_record(record: dict[str, Any], system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> dict[str, Any]:
    return {
        "id": record["id"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_user_prompt(record)},
            {"role": "assistant", "content": build_assistant_message(record)},
        ],
        "metadata": record.get("metadata", {}),
        "evidence": record.get("evidence", []),
    }


def build_llamafactory_input(record: dict[str, Any]) -> str:
    evidence_blocks = []
    for index, item in enumerate(record["evidence"], start=1):
        evidence_blocks.append(
            "\n".join(
                [
                    f"[{index}] source_id={item['source_id']} locator={item['locator']}",
                    item["quote"],
                ]
            )
        )
    return (
        f"问题：{record['question']}\n\n"
        f"参考资料：\n{'\n\n'.join(evidence_blocks)}"
    )


def build_llamafactory_record(
    record: dict[str, Any],
    *,
    instruction: str = DEFAULT_INSTRUCTION,
    dataset_version: str = "v1.3-e1",
    data_type: str = "normal_grounded_qa",
) -> dict[str, Any]:
    return {
        "instruction": instruction,
        "input": build_llamafactory_input(record),
        "output": build_assistant_message(record),
        "metadata": {
            "source_sample_id": record["id"],
            "data_type": data_type,
            "dataset_version": dataset_version,
            **record.get("metadata", {}),
        },
    }


def build_output_record(
    record: dict[str, Any],
    *,
    output_format: str,
    system_prompt: str,
    instruction: str,
    dataset_version: str,
    data_type: str,
) -> dict[str, Any]:
    if output_format == "chat_jsonl":
        return build_sft_record(record, system_prompt)
    if output_format == "llamafactory":
        return build_llamafactory_record(
            record,
            instruction=instruction,
            dataset_version=dataset_version,
            data_type=data_type,
        )
    raise ValueError(f"unsupported output format: {output_format}")


def split_records(
    records: list[dict[str, Any]],
    validation_count: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if validation_count < 0:
        raise ValueError("validation_count must be non-negative")
    if validation_count >= len(records):
        raise ValueError("validation_count must be smaller than record count")
    if validation_count == 0:
        return records, []
    return records[:-validation_count], records[-validation_count:]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def prepare_sft_dataset(
    *,
    input_path: Path,
    train_output_path: Path,
    validation_output_path: Path | None = None,
    validation_count: int = 0,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    output_format: str = "chat_jsonl",
    instruction: str = DEFAULT_INSTRUCTION,
    dataset_version: str = "v1.3-e1",
    data_type: str = "normal_grounded_qa",
) -> dict[str, Any]:
    records = load_records(input_path)
    train_records, validation_records = split_records(records, validation_count)
    train_sft_records = [
        build_output_record(
            record,
            output_format=output_format,
            system_prompt=system_prompt,
            instruction=instruction,
            dataset_version=dataset_version,
            data_type=data_type,
        )
        for record in train_records
    ]
    validation_sft_records = [
        build_output_record(
            record,
            output_format=output_format,
            system_prompt=system_prompt,
            instruction=instruction,
            dataset_version=dataset_version,
            data_type=data_type,
        )
        for record in validation_records
    ]

    write_jsonl(train_output_path, train_sft_records)
    if validation_output_path is not None:
        write_jsonl(validation_output_path, validation_sft_records)

    return {
        "input_path": str(input_path),
        "train_output_path": str(train_output_path),
        "validation_output_path": str(validation_output_path) if validation_output_path else None,
        "source_count": len(records),
        "train_count": len(train_sft_records),
        "validation_count": len(validation_sft_records),
        "format": output_format,
        "dataset_version": dataset_version,
        "data_type": data_type,
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Prepare LocalRAG train_set as chat JSONL for SFT/QLoRA.")
    parser.add_argument(
        "--input",
        default=Path("data/evaluation/train/train_set.json"),
        type=Path,
        help="Input LocalRAG training dataset.",
    )
    parser.add_argument(
        "--train-output",
        default=Path("data/finetuning/sft_train.jsonl"),
        type=Path,
        help="Output JSONL path for training samples.",
    )
    parser.add_argument(
        "--validation-output",
        default=None,
        type=Path,
        help="Optional output JSONL path for validation samples.",
    )
    parser.add_argument(
        "--validation-count",
        default=0,
        type=int,
        help="Hold out the last N samples for validation.",
    )
    parser.add_argument(
        "--system-prompt",
        default=DEFAULT_SYSTEM_PROMPT,
        help="System prompt written into each chat sample.",
    )
    parser.add_argument(
        "--format",
        default="chat_jsonl",
        choices=("chat_jsonl", "llamafactory"),
        help="Output record format.",
    )
    parser.add_argument(
        "--instruction",
        default=DEFAULT_INSTRUCTION,
        help="Instruction used for LLaMA-Factory style records.",
    )
    parser.add_argument(
        "--dataset-version",
        default="v1.3-e1",
        help="Dataset version written to metadata.",
    )
    parser.add_argument(
        "--data-type",
        default="normal_grounded_qa",
        help="Data type written to metadata.",
    )
    args = parser.parse_args()

    summary = prepare_sft_dataset(
        input_path=args.input,
        train_output_path=args.train_output,
        validation_output_path=args.validation_output,
        validation_count=args.validation_count,
        system_prompt=args.system_prompt,
        output_format=args.format,
        instruction=args.instruction,
        dataset_version=args.dataset_version,
        data_type=args.data_type,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    main()
