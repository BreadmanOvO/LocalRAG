import argparse
import json
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


REQUIRED_LLAMAFATORY_KEYS = {"instruction", "input", "output", "metadata"}
REQUIRED_METADATA_KEYS = {"source_sample_id", "data_type", "dataset_version"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _ratio(count: int, total: int) -> float:
    return round(count / total, 3) if total else 0.0


def _length_stats(values: list[int]) -> dict[str, Any]:
    if not values:
        return {"min": 0, "max": 0, "mean": 0.0, "median": 0.0}
    return {
        "min": min(values),
        "max": max(values),
        "mean": round(statistics.mean(values), 1),
        "median": round(statistics.median(values), 1),
    }


def _source_ids_from_training_rows(rows: list[dict[str, Any]]) -> set[str]:
    return {
        str(row.get("metadata", {}).get("source_sample_id", ""))
        for row in rows
        if row.get("metadata", {}).get("source_sample_id")
    }


def _dataset_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {str(row.get("id", "")) for row in load_json(path) if row.get("id")}


def validate_llamafactory_row(row: dict[str, Any]) -> list[str]:
    issues = []
    missing = REQUIRED_LLAMAFATORY_KEYS - row.keys()
    if missing:
        issues.append(f"missing top-level keys: {sorted(missing)}")

    for key in ("instruction", "input", "output"):
        value = row.get(key)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{key} must be a non-empty string")

    metadata = row.get("metadata")
    if not isinstance(metadata, dict):
        issues.append("metadata must be an object")
        return issues

    missing_metadata = REQUIRED_METADATA_KEYS - metadata.keys()
    if missing_metadata:
        issues.append(f"missing metadata keys: {sorted(missing_metadata)}")

    source_sample_id = metadata.get("source_sample_id")
    if not isinstance(source_sample_id, str) or not source_sample_id.strip():
        issues.append("metadata.source_sample_id must be a non-empty string")

    output = row.get("output", "")
    input_text = row.get("input", "")
    if "引用：" not in output:
        issues.append("output is missing citation section")
    if "source_id=" not in input_text:
        issues.append("input is missing source_id marker")
    if "locator=" not in input_text:
        issues.append("input is missing locator marker")
    if "参考资料：" not in input_text:
        issues.append("input is missing reference-material section")

    return issues


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    issue_rows = []
    source_ids = []
    doc_types = Counter()
    topics = Counter()
    difficulties = Counter()
    data_types = Counter()
    dataset_versions = Counter()

    for index, row in enumerate(rows, start=1):
        metadata = row.get("metadata", {}) if isinstance(row.get("metadata"), dict) else {}
        source_id = str(metadata.get("source_sample_id", ""))
        source_ids.append(source_id)
        if metadata.get("doc_type"):
            doc_types[str(metadata["doc_type"])] += 1
        if metadata.get("topic"):
            topics[str(metadata["topic"])] += 1
        if metadata.get("difficulty"):
            difficulties[str(metadata["difficulty"])] += 1
        if metadata.get("data_type"):
            data_types[str(metadata["data_type"])] += 1
        if metadata.get("dataset_version"):
            dataset_versions[str(metadata["dataset_version"])] += 1

        issues = validate_llamafactory_row(row)
        if issues:
            issue_rows.append({"index": index, "source_sample_id": source_id, "issues": issues})

    duplicate_ids = sorted(item for item, count in Counter(source_ids).items() if item and count > 1)
    output_citation_count = sum(1 for row in rows if "引用：" in row.get("output", ""))
    input_source_marker_count = sum(1 for row in rows if "source_id=" in row.get("input", ""))
    input_locator_marker_count = sum(1 for row in rows if "locator=" in row.get("input", ""))

    return {
        "record_count": total,
        "issue_count": len(issue_rows),
        "issue_rows": issue_rows[:50],
        "duplicate_source_sample_ids": duplicate_ids,
        "output_citation_count": output_citation_count,
        "output_citation_ratio": _ratio(output_citation_count, total),
        "input_source_marker_count": input_source_marker_count,
        "input_source_marker_ratio": _ratio(input_source_marker_count, total),
        "input_locator_marker_count": input_locator_marker_count,
        "input_locator_marker_ratio": _ratio(input_locator_marker_count, total),
        "instruction_length": _length_stats([len(row.get("instruction", "")) for row in rows]),
        "input_length": _length_stats([len(row.get("input", "")) for row in rows]),
        "output_length": _length_stats([len(row.get("output", "")) for row in rows]),
        "doc_type_distribution": dict(sorted(doc_types.items())),
        "topic_distribution": dict(sorted(topics.items())),
        "difficulty_distribution": dict(sorted(difficulties.items())),
        "data_type_distribution": dict(sorted(data_types.items())),
        "dataset_version_distribution": dict(sorted(dataset_versions.items())),
    }


def audit_sft_dataset(
    *,
    train_path: Path,
    validation_path: Path,
    eval_set_path: Path,
    generation_eval_set_path: Path,
) -> dict[str, Any]:
    train_rows = load_jsonl(train_path)
    validation_rows = load_jsonl(validation_path)
    train_ids = _source_ids_from_training_rows(train_rows)
    validation_ids = _source_ids_from_training_rows(validation_rows)
    eval_ids = _dataset_ids(eval_set_path)
    generation_eval_ids = _dataset_ids(generation_eval_set_path)
    all_sft_ids = train_ids | validation_ids

    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "train_path": str(train_path),
        "validation_path": str(validation_path),
        "eval_set_path": str(eval_set_path),
        "generation_eval_set_path": str(generation_eval_set_path),
        "train": summarize_rows(train_rows),
        "validation": summarize_rows(validation_rows),
        "split_overlap_source_sample_ids": sorted(train_ids & validation_ids),
        "eval_set_overlap_source_sample_ids": sorted(all_sft_ids & eval_ids),
        "generation_eval_set_overlap_source_sample_ids": sorted(all_sft_ids & generation_eval_ids),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def render_report(summary: dict[str, Any]) -> str:
    train = summary["train"]
    validation = summary["validation"]
    lines = [
        "# E1 SFT Dataset Audit",
        "",
        f"- Created at: `{summary['created_at']}`",
        f"- Train path: `{summary['train_path']}`",
        f"- Validation path: `{summary['validation_path']}`",
        f"- Train records: `{train['record_count']}`",
        f"- Validation records: `{validation['record_count']}`",
        f"- Train issue rows: `{train['issue_count']}`",
        f"- Validation issue rows: `{validation['issue_count']}`",
        f"- Train/validation ID overlap: `{len(summary['split_overlap_source_sample_ids'])}`",
        f"- Eval set ID overlap: `{len(summary['eval_set_overlap_source_sample_ids'])}`",
        f"- Generation eval set ID overlap: `{len(summary['generation_eval_set_overlap_source_sample_ids'])}`",
        "",
        "## Citation Checks",
        "",
        f"- Train output citation ratio: `{train['output_citation_ratio']}`",
        f"- Validation output citation ratio: `{validation['output_citation_ratio']}`",
        f"- Train input source marker ratio: `{train['input_source_marker_ratio']}`",
        f"- Validation input source marker ratio: `{validation['input_source_marker_ratio']}`",
        f"- Train input locator marker ratio: `{train['input_locator_marker_ratio']}`",
        f"- Validation input locator marker ratio: `{validation['input_locator_marker_ratio']}`",
        "",
        "## Length Stats",
        "",
        f"- Train input length: `{train['input_length']}`",
        f"- Train output length: `{train['output_length']}`",
        f"- Validation input length: `{validation['input_length']}`",
        f"- Validation output length: `{validation['output_length']}`",
        "",
        "## Train Distributions",
        "",
        f"- doc_type: `{train['doc_type_distribution']}`",
        f"- difficulty: `{train['difficulty_distribution']}`",
        f"- topics: `{train['topic_distribution']}`",
        "",
        "## Validation Distributions",
        "",
        f"- doc_type: `{validation['doc_type_distribution']}`",
        f"- difficulty: `{validation['difficulty_distribution']}`",
        f"- topics: `{validation['topic_distribution']}`",
        "",
    ]
    if train["issue_rows"] or validation["issue_rows"]:
        lines.extend(["## Issues", ""])
        for section_name, section in (("train", train), ("validation", validation)):
            for row in section["issue_rows"]:
                lines.append(f"- {section_name} #{row['index']} `{row['source_sample_id']}`: {', '.join(row['issues'])}")
    else:
        lines.extend(["## Issues", "", "No structural issues found."])
    return "\n".join(lines) + "\n"


def write_audit(summary: dict[str, Any], out_dir: Path) -> dict[str, str]:
    run_id = f"sft-e1-audit-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    run_dir = out_dir / run_id
    json_path = run_dir / "summary.json"
    report_path = run_dir / "report.md"
    write_json(json_path, summary)
    report_path.write_text(render_report(summary), encoding="utf-8")
    return {"run_dir": str(run_dir), "summary": str(json_path), "report": str(report_path)}


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Audit LocalRAG E1 SFT JSONL data quality.")
    parser.add_argument("--train", default=Path("finetune/datasets/localrag_sft_e1.jsonl"), type=Path)
    parser.add_argument("--validation", default=Path("finetune/datasets/localrag_sft_e1_validation.jsonl"), type=Path)
    parser.add_argument("--eval-set", default=Path("data/evaluation/gold/eval_set.json"), type=Path)
    parser.add_argument("--generation-eval-set", default=Path("data/evaluation/gold/generation_eval_set.json"), type=Path)
    parser.add_argument("--out-dir", default=Path("results/finetune_data_audit"), type=Path)
    args = parser.parse_args()

    summary = audit_sft_dataset(
        train_path=args.train,
        validation_path=args.validation,
        eval_set_path=args.eval_set,
        generation_eval_set_path=args.generation_eval_set,
    )
    artifacts = write_audit(summary, args.out_dir)
    output = {"summary": summary, "artifacts": artifacts}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
