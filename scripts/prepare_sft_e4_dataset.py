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


DEFAULT_DATASET_VERSION = "v1.3-e4"


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


def _clone_with_metadata(row: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    new_row = copy.deepcopy(row)
    metadata = new_row.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}
    metadata.update(updates)
    new_row["metadata"] = metadata
    return new_row


def build_e4_train_rows(
    *,
    e3_rows: list[dict[str, Any]],
    hardcase_rows: list[dict[str, Any]],
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> list[dict[str, Any]]:
    prior_rows = [
        _clone_with_metadata(
            row,
            {
                "dataset_version": dataset_version,
                "data_type": row.get("metadata", {}).get("data_type", "normal_grounded_qa"),
                "e4_source": "e3_training_mix",
            },
        )
        for row in e3_rows
    ]
    hardcase_output = []
    for row in hardcase_rows:
        original_data_type = str(row.get("metadata", {}).get("data_type", "hardcase"))
        hardcase_output.append(
            _clone_with_metadata(
                row,
                {
                    "dataset_version": dataset_version,
                    "data_type": f"e4_hardcase_{original_data_type}",
                    "e4_source": "e4_hardcase_slice",
                },
            )
        )
    return prior_rows + hardcase_output


def build_e4_validation_rows(
    *,
    validation_rows: list[dict[str, Any]],
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> list[dict[str, Any]]:
    return [
        _clone_with_metadata(
            row,
            {
                "dataset_version": dataset_version,
                "data_type": "normal_grounded_qa_validation",
                "e4_source": "e3_validation_holdout",
            },
        )
        for row in validation_rows
    ]


def _source_ids(rows: list[dict[str, Any]]) -> set[str]:
    return {
        str(row.get("metadata", {}).get("source_sample_id", ""))
        for row in rows
        if row.get("metadata", {}).get("source_sample_id")
    }


def summarize(train_rows: list[dict[str, Any]], validation_rows: list[dict[str, Any]]) -> dict[str, Any]:
    train_data_types = Counter(str(row.get("metadata", {}).get("data_type", "")) for row in train_rows)
    validation_data_types = Counter(str(row.get("metadata", {}).get("data_type", "")) for row in validation_rows)
    missing_metrics = Counter(
        metric
        for row in train_rows
        for metric in row.get("metadata", {}).get("missing_metrics", [])
    )
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "dataset_version": DEFAULT_DATASET_VERSION,
        "train_count": len(train_rows),
        "validation_count": len(validation_rows),
        "train_data_type_distribution": dict(sorted(train_data_types.items())),
        "validation_data_type_distribution": dict(sorted(validation_data_types.items())),
        "missing_metric_distribution": dict(sorted(missing_metrics.items())),
        "train_validation_source_sample_overlap": sorted(_source_ids(train_rows) & _source_ids(validation_rows)),
        "train_output_citation_count": sum(1 for row in train_rows if "引用：" in row.get("output", "")),
        "validation_output_citation_count": sum(1 for row in validation_rows if "引用：" in row.get("output", "")),
    }


def prepare_e4_dataset(
    *,
    e3_train_path: Path,
    e3_validation_path: Path,
    e4_hardcase_path: Path,
    train_output_path: Path,
    validation_output_path: Path,
    summary_path: Path,
    dataset_version: str = DEFAULT_DATASET_VERSION,
) -> dict[str, Any]:
    e3_rows = load_jsonl(e3_train_path)
    validation_rows = load_jsonl(e3_validation_path)
    hardcase_rows = load_jsonl(e4_hardcase_path)
    train_rows = build_e4_train_rows(
        e3_rows=e3_rows,
        hardcase_rows=hardcase_rows,
        dataset_version=dataset_version,
    )
    e4_validation_rows = build_e4_validation_rows(
        validation_rows=validation_rows,
        dataset_version=dataset_version,
    )
    write_jsonl(train_output_path, train_rows)
    write_jsonl(validation_output_path, e4_validation_rows)
    summary = summarize(train_rows, e4_validation_rows)
    summary.update(
        {
            "e3_train_path": str(e3_train_path),
            "e3_validation_path": str(e3_validation_path),
            "e4_hardcase_path": str(e4_hardcase_path),
            "train_output_path": str(train_output_path),
            "validation_output_path": str(validation_output_path),
        }
    )
    write_json(summary_path, summary)
    return {
        "summary": summary,
        "artifacts": {
            "train": str(train_output_path),
            "validation": str(validation_output_path),
            "summary": str(summary_path),
        },
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Merge E3 SFT data with reviewed E4 hard-case slice.")
    parser.add_argument("--e3-train", default=Path("finetune/datasets/localrag_sft_e3.jsonl"), type=Path)
    parser.add_argument(
        "--e3-validation",
        default=Path("finetune/datasets/localrag_sft_e3_validation.jsonl"),
        type=Path,
    )
    parser.add_argument(
        "--e4-hardcase",
        default=Path("finetune/datasets/localrag_sft_e4_draft.jsonl"),
        type=Path,
    )
    parser.add_argument("--train-output", default=Path("finetune/datasets/localrag_sft_e4.jsonl"), type=Path)
    parser.add_argument(
        "--validation-output",
        default=Path("finetune/datasets/localrag_sft_e4_validation.jsonl"),
        type=Path,
    )
    parser.add_argument(
        "--summary",
        default=Path("results/finetune_data_audit/e4-dataset-summary.json"),
        type=Path,
    )
    parser.add_argument("--dataset-version", default=DEFAULT_DATASET_VERSION)
    args = parser.parse_args()

    output = prepare_e4_dataset(
        e3_train_path=args.e3_train,
        e3_validation_path=args.e3_validation,
        e4_hardcase_path=args.e4_hardcase,
        train_output_path=args.train_output,
        validation_output_path=args.validation_output,
        summary_path=args.summary,
        dataset_version=args.dataset_version,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
