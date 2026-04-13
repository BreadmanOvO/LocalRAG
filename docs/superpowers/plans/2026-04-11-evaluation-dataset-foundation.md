# Evaluation Dataset Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first on-disk evaluation dataset contract for `v1.0 Baseline`, including shared taxonomy/source files, Gold/Synthetic dataset files, and a repeatable validator the repo can run before later evaluation scripts are added.

**Architecture:** Keep the repository’s current flat Python layout and add one focused module, `evaluation_dataset.py`, that owns path constants, JSON/JSONL loading, record validation, and repository-wide contract checks. Materialize the contract under `data/evaluation/` with small seed records and validate everything with `unittest` so the repo gains repeatable checks without introducing new dependencies or restructuring the app code.

**Tech Stack:** Python standard library (`json`, `pathlib`, `unittest`, `tempfile`), JSONL, JSON, Markdown, Git

---

## File Structure

- `evaluation_dataset.py` — central loader/validator for evaluation dataset files under `data/evaluation/`; exposes record validators and a repository-wide validation summary.
- `test/test_evaluation_dataset_contract.py` — `unittest` test suite covering JSONL loading, per-record validation, shared-file checks, and repository-level contract validation.
- `data/evaluation/shared/taxonomy.md` — human-readable canonical enum list for `topic`, `difficulty`, and `question_type`, plus quality rules.
- `data/evaluation/shared/source_registry.json` — source registry used by Gold/Synthetic records via `source_id`.
- `data/evaluation/gold/gold_set_schema.md` — Gold Set field contract and `review_status` rules.
- `data/evaluation/gold/manifest.json` — Gold dataset metadata and baseline filter (`review_status=approved`).
- `data/evaluation/gold/gold_set.jsonl` — seed Gold records that satisfy the approved schema.
- `data/evaluation/synthetic/synthetic_generation_spec.md` — Synthetic generation and `validation_status` rules.
- `data/evaluation/synthetic/manifest.json` — Synthetic dataset metadata and baseline filter (`validation_status=checked`).
- `data/evaluation/synthetic/synthetic_dataset.jsonl` — seed Synthetic records that satisfy the shared contract plus `generation_meta`.
- `test/README.md` — test command documentation for the new contract validator.

## Task 1: Add the validation module and record-level tests

**Files:**
- Create: `evaluation_dataset.py`
- Create: `test/test_evaluation_dataset_contract.py`

- [ ] **Step 1: Write the failing tests for JSONL loading and record validation**

```python
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from evaluation_dataset import load_jsonl, validate_gold_record, validate_synthetic_record


class LoadJsonlTests(unittest.TestCase):
    def test_load_jsonl_skips_blank_lines(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "records.jsonl"
            path.write_text('{"id": "row-1"}\n\n{"id": "row-2"}\n', encoding="utf-8")
            records = load_jsonl(path)
        self.assertEqual([{"id": "row-1"}, {"id": "row-2"}], records)


class RecordValidationTests(unittest.TestCase):
    def test_gold_record_requires_review_status(self):
        record = {
            "id": "gold-0001",
            "question": "什么是 BEV 感知？",
            "reference_answer": "BEV 感知将多传感器信息映射到鸟瞰视角统一建模。",
            "evidence": [
                {
                    "source_id": "apollo-doc-001",
                    "locator": "chapter=3/section=3.2",
                    "quote": "BEV 表示有助于统一空间尺度。"
                }
            ],
            "topic": "perception",
            "difficulty": "medium",
            "question_type": "definition",
            "keywords": ["BEV"],
            "language": "zh"
        }

        with self.assertRaisesRegex(ValueError, "review_status"):
            validate_gold_record(record, {"apollo-doc-001"})

    def test_synthetic_record_accepts_generation_meta(self):
        record = {
            "id": "syn-0001",
            "question": "为什么相机与激光雷达融合能提升检测稳定性？",
            "reference_answer": "相机提供纹理语义，激光雷达提供稳定几何信息，二者融合可以提升复杂场景鲁棒性。",
            "evidence": [
                {
                    "source_id": "paper-003",
                    "locator": "page=5/paragraph=2",
                    "quote": "Fusion combines semantic cues with geometry."
                }
            ],
            "topic": "sensor_fusion",
            "difficulty": "medium",
            "question_type": "why_analysis",
            "keywords": ["camera", "lidar", "fusion"],
            "language": "zh",
            "generation_meta": {
                "method": "llm_generated",
                "source_basis": ["paper-003"],
                "validation_status": "pending"
            }
        }

        validate_synthetic_record(record, {"paper-003"})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail because the module does not exist yet**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'evaluation_dataset'`

- [ ] **Step 3: Create the minimal validator module**

```python
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATASET_ROOT = ROOT / "data" / "evaluation"
GOLD_DIR = DATASET_ROOT / "gold"
SYNTHETIC_DIR = DATASET_ROOT / "synthetic"
SHARED_DIR = DATASET_ROOT / "shared"

GOLD_JSONL_PATH = GOLD_DIR / "gold_set.jsonl"
GOLD_MANIFEST_PATH = GOLD_DIR / "manifest.json"
GOLD_SCHEMA_PATH = GOLD_DIR / "gold_set_schema.md"
SYNTHETIC_JSONL_PATH = SYNTHETIC_DIR / "synthetic_dataset.jsonl"
SYNTHETIC_MANIFEST_PATH = SYNTHETIC_DIR / "manifest.json"
SYNTHETIC_SPEC_PATH = SYNTHETIC_DIR / "synthetic_generation_spec.md"
TAXONOMY_PATH = SHARED_DIR / "taxonomy.md"
SOURCE_REGISTRY_PATH = SHARED_DIR / "source_registry.json"

TOPIC_VALUES = {
    "perception",
    "sensor_fusion",
    "planning_control",
    "safety",
    "system_architecture",
}
DIFFICULTY_VALUES = {"easy", "medium", "hard"}
QUESTION_TYPE_VALUES = {
    "definition",
    "principle_explanation",
    "why_analysis",
    "process_description",
    "comparison",
    "scenario_reasoning",
}
REVIEW_STATUS_VALUES = {"draft", "approved"}
VALIDATION_STATUS_VALUES = {"pending", "checked", "rejected"}


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue
            record = json.loads(line)
            if not isinstance(record, dict):
                raise ValueError(f"{path.name}:{line_number} must be a JSON object")
            records.append(record)
    return records


def _require_non_empty_string(record: dict, field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _require_enum(record: dict, field: str, allowed_values: set[str]) -> str:
    value = _require_non_empty_string(record, field)
    if value not in allowed_values:
        raise ValueError(f"{field} must be one of {sorted(allowed_values)}")
    return value


def _validate_evidence_list(record: dict, source_ids: set[str]) -> None:
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("evidence must be a non-empty list")

    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("evidence entries must be JSON objects")
        source_id = _require_non_empty_string(item, "source_id")
        if source_id not in source_ids:
            raise ValueError(f"unknown source_id: {source_id}")
        _require_non_empty_string(item, "locator")
        _require_non_empty_string(item, "quote")


def _validate_common_record_fields(record: dict, source_ids: set[str]) -> None:
    _require_non_empty_string(record, "id")
    _require_non_empty_string(record, "question")
    _require_non_empty_string(record, "reference_answer")
    _validate_evidence_list(record, source_ids)
    _require_enum(record, "topic", TOPIC_VALUES)
    _require_enum(record, "difficulty", DIFFICULTY_VALUES)
    _require_enum(record, "question_type", QUESTION_TYPE_VALUES)

    keywords = record.get("keywords")
    if not isinstance(keywords, list) or not keywords or not all(isinstance(item, str) and item.strip() for item in keywords):
        raise ValueError("keywords must be a non-empty list of strings")

    _require_enum(record, "language", {"zh"})


def validate_gold_record(record: dict, source_ids: set[str]) -> None:
    _validate_common_record_fields(record, source_ids)
    _require_enum(record, "review_status", REVIEW_STATUS_VALUES)



def validate_synthetic_record(record: dict, source_ids: set[str]) -> None:
    _validate_common_record_fields(record, source_ids)

    generation_meta = record.get("generation_meta")
    if not isinstance(generation_meta, dict):
        raise ValueError("generation_meta must be an object")

    _require_non_empty_string(generation_meta, "method")

    source_basis = generation_meta.get("source_basis")
    if not isinstance(source_basis, list) or not source_basis:
        raise ValueError("generation_meta.source_basis must be a non-empty list")
    for source_id in source_basis:
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError("generation_meta.source_basis must contain source_id strings")
        if source_id not in source_ids:
            raise ValueError(f"unknown source_basis source_id: {source_id}")

    _require_enum(generation_meta, "validation_status", VALIDATION_STATUS_VALUES)
```

- [ ] **Step 4: Run the tests to verify the validator passes the record-level contract**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: PASS with `test_load_jsonl_skips_blank_lines ... ok`, `test_gold_record_requires_review_status ... ok`, and `test_synthetic_record_accepts_generation_meta ... ok`

- [ ] **Step 5: Commit the validator foundation**

```bash
git add evaluation_dataset.py test/test_evaluation_dataset_contract.py
git commit -m "test: add evaluation dataset contract validators"
```

## Task 2: Add shared taxonomy and source registry files

**Files:**
- Modify: `evaluation_dataset.py`
- Modify: `test/test_evaluation_dataset_contract.py`
- Create: `data/evaluation/shared/taxonomy.md`
- Create: `data/evaluation/shared/source_registry.json`

- [ ] **Step 1: Extend the tests to require the shared files and source registry contract**

```python
import unittest

from evaluation_dataset import (
    SOURCE_REGISTRY_PATH,
    TAXONOMY_PATH,
    TOPIC_VALUES,
    DIFFICULTY_VALUES,
    QUESTION_TYPE_VALUES,
    load_json,
    validate_source_registry,
)


class SharedContractTests(unittest.TestCase):
    def test_source_registry_contains_unique_source_ids(self):
        entries = load_json(SOURCE_REGISTRY_PATH)
        validate_source_registry(entries)
        self.assertEqual({"apollo-doc-001", "paper-003", "standard-001"}, {entry["source_id"] for entry in entries})

    def test_taxonomy_markdown_lists_current_enums(self):
        content = TAXONOMY_PATH.read_text(encoding="utf-8")
        for value in sorted(TOPIC_VALUES | DIFFICULTY_VALUES | QUESTION_TYPE_VALUES):
            self.assertIn(f"`{value}`", content)
```

- [ ] **Step 2: Run the tests to verify they fail because the shared files do not exist yet**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: FAIL with `FileNotFoundError` for `data/evaluation/shared/source_registry.json` or `data/evaluation/shared/taxonomy.md`

- [ ] **Step 3: Create the shared files and add source-registry loading/validation**

`evaluation_dataset.py`

```python
import json
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)



def validate_source_registry(entries: list[dict]) -> None:
    if not isinstance(entries, list) or not entries:
        raise ValueError("source registry must be a non-empty list")

    seen_source_ids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("source registry entries must be JSON objects")

        source_id = _require_non_empty_string(entry, "source_id")
        if source_id in seen_source_ids:
            raise ValueError(f"duplicate source_id: {source_id}")
        seen_source_ids.add(source_id)

        _require_non_empty_string(entry, "title")
        _require_non_empty_string(entry, "source_type")
        _require_enum(entry, "language", {"zh", "en"})
        _require_non_empty_string(entry, "path_or_url")
        _require_non_empty_string(entry, "version")
```

`data/evaluation/shared/taxonomy.md`

```md
# Evaluation Dataset Taxonomy

## Topic
- `perception`
- `sensor_fusion`
- `planning_control`
- `safety`
- `system_architecture`

## Difficulty
- `easy`
- `medium`
- `hard`

## Question Type
- `definition`
- `principle_explanation`
- `why_analysis`
- `process_description`
- `comparison`
- `scenario_reasoning`

## Rules
1. Gold Set and Synthetic Set share the same `topic`, `difficulty`, and `question_type` enums.
2. Gold Set must cover all three difficulty levels.
3. Synthetic Set should target a 30/50/20 split across `easy`/`medium`/`hard`.
4. All records use `language=zh` in the first baseline version.
```

`data/evaluation/shared/source_registry.json`

```json
[
  {
    "source_id": "apollo-doc-001",
    "title": "Apollo 感知模块文档",
    "source_type": "doc",
    "language": "zh",
    "path_or_url": "https://apollo.auto/docs/",
    "version": "2026-04-10"
  },
  {
    "source_id": "paper-003",
    "title": "Multi-Sensor Fusion Reference Notes",
    "source_type": "paper",
    "language": "en",
    "path_or_url": "https://openaccess.thecvf.com/",
    "version": "2026-04-10"
  },
  {
    "source_id": "standard-001",
    "title": "ISO 21448 SOTIF Summary Notes",
    "source_type": "standard",
    "language": "en",
    "path_or_url": "https://www.iso.org/standard/70939.html",
    "version": "2026-04-10"
  }
]
```

- [ ] **Step 4: Run the tests to verify the shared contract is now valid**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: PASS with `test_source_registry_contains_unique_source_ids ... ok` and `test_taxonomy_markdown_lists_current_enums ... ok`

- [ ] **Step 5: Commit the shared dataset contract files**

```bash
git add evaluation_dataset.py test/test_evaluation_dataset_contract.py data/evaluation/shared/taxonomy.md data/evaluation/shared/source_registry.json
git commit -m "data: register evaluation taxonomy and sources"
```

## Task 3: Add Gold Set files and Gold-specific validation

**Files:**
- Modify: `evaluation_dataset.py`
- Modify: `test/test_evaluation_dataset_contract.py`
- Create: `data/evaluation/gold/gold_set_schema.md`
- Create: `data/evaluation/gold/manifest.json`
- Create: `data/evaluation/gold/gold_set.jsonl`

- [ ] **Step 1: Extend the tests to require Gold manifest and approved Gold seed records**

```python
import unittest

from evaluation_dataset import (
    GOLD_JSONL_PATH,
    GOLD_MANIFEST_PATH,
    SOURCE_REGISTRY_PATH,
    load_json,
    load_jsonl,
    validate_gold_manifest,
    validate_gold_record,
)


class GoldDatasetTests(unittest.TestCase):
    def test_gold_manifest_uses_review_status_filter(self):
        manifest = load_json(GOLD_MANIFEST_PATH)
        validate_gold_manifest(manifest)
        self.assertEqual("approved", manifest["filter_for_baseline"]["review_status"])

    def test_gold_seed_records_reference_registered_sources(self):
        source_entries = load_json(SOURCE_REGISTRY_PATH)
        source_ids = {entry["source_id"] for entry in source_entries}
        records = load_jsonl(GOLD_JSONL_PATH)

        self.assertEqual(2, len(records))
        for record in records:
            validate_gold_record(record, source_ids)
            self.assertEqual("approved", record["review_status"])
```

- [ ] **Step 2: Run the tests to verify they fail because the Gold files do not exist yet**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: FAIL with `FileNotFoundError` for `data/evaluation/gold/manifest.json` or `data/evaluation/gold/gold_set.jsonl`

- [ ] **Step 3: Create the Gold files and Gold-manifest validator**

`evaluation_dataset.py`

```python
def _validate_manifest(manifest: dict, dataset_name: str, baseline_field: str) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a JSON object")
    if manifest.get("dataset_name") != dataset_name:
        raise ValueError(f"dataset_name must be {dataset_name}")
    _require_non_empty_string(manifest, "dataset_version")

    sample_count = manifest.get("sample_count")
    if not isinstance(sample_count, int) or sample_count <= 0:
        raise ValueError("sample_count must be a positive integer")

    _require_enum(manifest, "language", {"zh"})

    filter_for_baseline = manifest.get("filter_for_baseline")
    if not isinstance(filter_for_baseline, dict):
        raise ValueError("filter_for_baseline must be an object")
    if baseline_field not in filter_for_baseline:
        raise ValueError(f"filter_for_baseline must include {baseline_field}")


def validate_gold_manifest(manifest: dict) -> None:
    _validate_manifest(manifest, "gold_set", "review_status")
```

`data/evaluation/gold/gold_set_schema.md`

```md
# Gold Set Schema

## Required Fields
- `id`
- `question`
- `reference_answer`
- `evidence`
- `topic`
- `difficulty`
- `question_type`
- `keywords`
- `language`
- `review_status`

## Evidence Shape
Each `evidence` entry must contain:
- `source_id`
- `locator`
- `quote`

## Rules
1. `review_status` must be `draft` or `approved`.
2. Only `review_status=approved` records enter the baseline gate.
3. Gold records must reference registered `source_id` values from `data/evaluation/shared/source_registry.json`.
4. Gold records bind to original evidence locations, not transient chunk identifiers.
```

`data/evaluation/gold/manifest.json`

```json
{
  "dataset_name": "gold_set",
  "dataset_version": "v1",
  "sample_count": 2,
  "language": "zh",
  "filter_for_baseline": {
    "review_status": "approved"
  }
}
```

`data/evaluation/gold/gold_set.jsonl`

```json
{"id": "gold-0001", "question": "什么是 BEV 感知，它相对前视视角感知的主要优势是什么？", "reference_answer": "BEV 感知将多传感器信息统一映射到鸟瞰空间表示，主要优势是空间尺度更一致，更适合做多目标关系建模、占用理解和规划协同。", "evidence": [{"source_id": "apollo-doc-001", "locator": "chapter=3/section=3.2", "quote": "BEV representation helps normalize spatial scale across the scene."}], "topic": "perception", "difficulty": "medium", "question_type": "principle_explanation", "keywords": ["BEV", "bird's-eye-view", "空间表示"], "language": "zh", "review_status": "approved"}
{"id": "gold-0002", "question": "SOTIF 与 ISO 26262 在自动驾驶安全工作中的关注重点有什么区别？", "reference_answer": "ISO 26262 主要关注由系统故障引发的功能安全风险，而 SOTIF 主要关注系统在无故障情况下由于感知能力、场景边界或预期功能局限带来的安全风险。", "evidence": [{"source_id": "standard-001", "locator": "section=1/overview", "quote": "SOTIF addresses hazards caused by functional insufficiencies in the absence of faults."}], "topic": "safety", "difficulty": "hard", "question_type": "comparison", "keywords": ["SOTIF", "ISO 26262", "功能安全"], "language": "zh", "review_status": "approved"}
```

- [ ] **Step 4: Run the tests to verify the Gold contract passes**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: PASS with `test_gold_manifest_uses_review_status_filter ... ok` and `test_gold_seed_records_reference_registered_sources ... ok`

- [ ] **Step 5: Commit the Gold dataset scaffold**

```bash
git add evaluation_dataset.py test/test_evaluation_dataset_contract.py data/evaluation/gold/gold_set_schema.md data/evaluation/gold/manifest.json data/evaluation/gold/gold_set.jsonl
git commit -m "data: scaffold gold evaluation set"
```

## Task 4: Add Synthetic Set files and repository-wide validation

**Files:**
- Modify: `evaluation_dataset.py`
- Modify: `test/test_evaluation_dataset_contract.py`
- Create: `data/evaluation/synthetic/synthetic_generation_spec.md`
- Create: `data/evaluation/synthetic/manifest.json`
- Create: `data/evaluation/synthetic/synthetic_dataset.jsonl`

- [ ] **Step 1: Extend the tests to require Synthetic files and a repository-wide validation summary**

```python
import unittest

from evaluation_dataset import (
    SYNTHETIC_JSONL_PATH,
    SYNTHETIC_MANIFEST_PATH,
    load_json,
    load_jsonl,
    validate_repository_contract,
    validate_synthetic_manifest,
)


class SyntheticDatasetTests(unittest.TestCase):
    def test_synthetic_manifest_uses_checked_filter(self):
        manifest = load_json(SYNTHETIC_MANIFEST_PATH)
        validate_synthetic_manifest(manifest)
        self.assertEqual("checked", manifest["filter_for_baseline"]["validation_status"])

    def test_repository_contract_returns_seed_counts(self):
        summary = validate_repository_contract()
        self.assertEqual(2, summary["gold_records"])
        self.assertEqual(3, summary["synthetic_records"])
        self.assertEqual(3, summary["sources"])

    def test_synthetic_seed_records_include_generation_meta(self):
        records = load_jsonl(SYNTHETIC_JSONL_PATH)
        self.assertEqual(3, len(records))
        self.assertEqual({"checked", "pending"}, {record["generation_meta"]["validation_status"] for record in records})
```

- [ ] **Step 2: Run the tests to verify they fail because the Synthetic files and repository validator do not exist yet**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: FAIL with `FileNotFoundError` for `data/evaluation/synthetic/manifest.json` or `AttributeError/ImportError` for `validate_repository_contract`

- [ ] **Step 3: Create the Synthetic files and repository-wide validation functions**

`evaluation_dataset.py`

```python
def validate_synthetic_manifest(manifest: dict) -> None:
    _validate_manifest(manifest, "synthetic_dataset", "validation_status")



def validate_repository_contract() -> dict[str, int]:
    source_entries = load_json(SOURCE_REGISTRY_PATH)
    validate_source_registry(source_entries)
    source_ids = {entry["source_id"] for entry in source_entries}

    gold_manifest = load_json(GOLD_MANIFEST_PATH)
    validate_gold_manifest(gold_manifest)
    gold_records = load_jsonl(GOLD_JSONL_PATH)
    if len(gold_records) != gold_manifest["sample_count"]:
        raise ValueError("gold manifest sample_count does not match gold_set.jsonl")
    for record in gold_records:
        validate_gold_record(record, source_ids)

    synthetic_manifest = load_json(SYNTHETIC_MANIFEST_PATH)
    validate_synthetic_manifest(synthetic_manifest)
    synthetic_records = load_jsonl(SYNTHETIC_JSONL_PATH)
    if len(synthetic_records) != synthetic_manifest["sample_count"]:
        raise ValueError("synthetic manifest sample_count does not match synthetic_dataset.jsonl")
    for record in synthetic_records:
        validate_synthetic_record(record, source_ids)

    return {
        "gold_records": len(gold_records),
        "synthetic_records": len(synthetic_records),
        "sources": len(source_entries),
    }
```

`data/evaluation/synthetic/synthetic_generation_spec.md`

```md
# Synthetic Dataset Generation Spec

## Required Fields
Synthetic records reuse all Gold Set common fields and add `generation_meta`.

## generation_meta
- `method`
- `source_basis`
- `validation_status`

## Rules
1. `validation_status` must be `pending`, `checked`, or `rejected`.
2. Only `validation_status=checked` records enter baseline reporting.
3. Every Synthetic record must reference registered `source_id` values both in `evidence` and `generation_meta.source_basis`.
4. Synthetic records can be generated in batch, but they cannot enter formal evaluation without traceable evidence.
```

`data/evaluation/synthetic/manifest.json`

```json
{
  "dataset_name": "synthetic_dataset",
  "dataset_version": "v1",
  "sample_count": 3,
  "language": "zh",
  "filter_for_baseline": {
    "validation_status": "checked"
  }
}
```

`data/evaluation/synthetic/synthetic_dataset.jsonl`

```json
{"id": "syn-0001", "question": "为什么相机与激光雷达融合可以提升目标检测稳定性？", "reference_answer": "相机提供纹理和语义信息，激光雷达提供稳定的几何与距离信息，二者融合可以在遮挡、弱光和远距离场景中提升检测鲁棒性。", "evidence": [{"source_id": "paper-003", "locator": "page=5/paragraph=2", "quote": "Fusion combines semantic cues with geometric robustness."}], "topic": "sensor_fusion", "difficulty": "medium", "question_type": "why_analysis", "keywords": ["camera", "lidar", "fusion"], "language": "zh", "generation_meta": {"method": "llm_generated", "source_basis": ["paper-003"], "validation_status": "checked"}}
{"id": "syn-0002", "question": "自动驾驶系统为什么需要把感知输出与规划控制模块协同设计？", "reference_answer": "因为规划控制依赖稳定、结构化且时序一致的环境理解结果，如果感知输出和下游接口脱节，就会放大误检、漏检和延迟对决策链路的影响。", "evidence": [{"source_id": "apollo-doc-001", "locator": "chapter=1/section=1.1", "quote": "Perception quality directly affects downstream planning stability."}], "topic": "planning_control", "difficulty": "medium", "question_type": "process_description", "keywords": ["规划控制", "感知输出", "接口协同"], "language": "zh", "generation_meta": {"method": "llm_generated", "source_basis": ["apollo-doc-001"], "validation_status": "checked"}}
{"id": "syn-0003", "question": "在没有硬件故障的情况下，为什么系统仍可能触发 SOTIF 风险？", "reference_answer": "因为即使硬件和软件都按设计运行，系统仍可能因为感知边界、场景覆盖不足或功能假设失效，在特定条件下产生不安全行为。", "evidence": [{"source_id": "standard-001", "locator": "section=2/examples", "quote": "Hazards may arise from functional insufficiencies even when no fault is present."}], "topic": "safety", "difficulty": "hard", "question_type": "scenario_reasoning", "keywords": ["SOTIF", "功能不足", "无故障风险"], "language": "zh", "generation_meta": {"method": "llm_generated", "source_basis": ["standard-001"], "validation_status": "pending"}}
```

- [ ] **Step 4: Run the tests to verify the repository-wide contract now passes**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: PASS with `test_synthetic_manifest_uses_checked_filter ... ok`, `test_repository_contract_returns_seed_counts ... ok`, and `test_synthetic_seed_records_include_generation_meta ... ok`

- [ ] **Step 5: Commit the Synthetic dataset scaffold**

```bash
git add evaluation_dataset.py test/test_evaluation_dataset_contract.py data/evaluation/synthetic/synthetic_generation_spec.md data/evaluation/synthetic/manifest.json data/evaluation/synthetic/synthetic_dataset.jsonl
git commit -m "data: scaffold synthetic evaluation set"
```

## Task 5: Add a CLI validation entrypoint and document the commands

**Files:**
- Modify: `evaluation_dataset.py`
- Modify: `test/test_evaluation_dataset_contract.py`
- Modify: `test/README.md`

- [ ] **Step 1: Add a failing test that expects the validator module to print a summary when run as a script**

```python
import subprocess
import sys
import unittest


class ValidationCliTests(unittest.TestCase):
    def test_cli_prints_repository_summary(self):
        completed = subprocess.run(
            [sys.executable, "evaluation_dataset.py"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Validated evaluation dataset contract", completed.stdout)
        self.assertIn("gold=2", completed.stdout)
        self.assertIn("synthetic=3", completed.stdout)
        self.assertIn("sources=3", completed.stdout)
```

- [ ] **Step 2: Run the tests to verify they fail because the module has no CLI output yet**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: FAIL with an assertion error because `completed.stdout` is empty

- [ ] **Step 3: Add `main()` to the validator and document the commands in `test/README.md`**

`evaluation_dataset.py`

```python
def main() -> None:
    summary = validate_repository_contract()
    print(
        "Validated evaluation dataset contract: "
        f"gold={summary['gold_records']} "
        f"synthetic={summary['synthetic_records']} "
        f"sources={summary['sources']}"
    )


if __name__ == "__main__":
    main()
```

`test/README.md`

```md
# test 脚本目录

本目录用于存放 LocalRAG 的测试与评估脚本。

## 1) chunk 参数测试

脚本：`chunk_benchmark.py`

用途：快速比较不同 `chunk_size/chunk_overlap` 的切分结果统计，辅助选择候选参数。

示例：

```bash
python test/chunk_benchmark.py --input data/your_doc.txt
```

自定义参数组：

```bash
python test/chunk_benchmark.py --input data/your_doc.txt --pairs "500:80,800:120,1000:150"
```

输出 JSON 报告：

```bash
python test/chunk_benchmark.py --input data/your_doc.txt --out test/chunk_report.json
```

## 2) 评估数据契约校验

模块：`evaluation_dataset.py`

测试：`test/test_evaluation_dataset_contract.py`

用途：校验 `data/evaluation/` 下的 taxonomy、source registry、manifest 和 JSONL 样本文件是否满足当前 baseline 契约。

运行单元测试：

```bash
python -m unittest test.test_evaluation_dataset_contract -v
```

运行仓库级校验：

```bash
python evaluation_dataset.py
```
```

- [ ] **Step 4: Run the tests and CLI to verify the full contract is executable**

Run: `python -m unittest test.test_evaluation_dataset_contract -v`
Expected: PASS with all contract tests green

Run: `python evaluation_dataset.py`
Expected: `Validated evaluation dataset contract: gold=2 synthetic=3 sources=3`

- [ ] **Step 5: Commit the executable validation workflow**

```bash
git add evaluation_dataset.py test/test_evaluation_dataset_contract.py test/README.md
git commit -m "docs: add evaluation dataset validation workflow"
```

## Self-Review

### Spec coverage
- **Directory structure** — covered by Tasks 2, 3, and 4 through `data/evaluation/shared`, `gold`, and `synthetic` file creation.
- **Gold schema** — covered by Task 3 via `gold_set_schema.md`, `manifest.json`, `gold_set.jsonl`, and `validate_gold_manifest()` / `validate_gold_record()`.
- **Synthetic schema** — covered by Task 4 via `synthetic_generation_spec.md`, `manifest.json`, `synthetic_dataset.jsonl`, and `validate_synthetic_manifest()` / `validate_synthetic_record()`.
- **Taxonomy and source registry** — covered by Task 2.
- **Quality rules and baseline filters** — covered by Tasks 3 and 4 through `review_status` / `validation_status` filters and validator checks.
- **Future script interface stability** — covered by Tasks 1, 3, and 4 through the explicit shared contract and repository-level validator.

### Placeholder scan
- No `TODO`, `TBD`, or deferred placeholders remain.
- Every code-changing step includes concrete code or full file contents.
- Every verification step includes an exact command and expected output.

### Type consistency
- `review_status` is used consistently for Gold records and Gold manifest filtering.
- `validation_status` is used consistently for Synthetic records and Synthetic manifest filtering.
- Shared enum names (`topic`, `difficulty`, `question_type`) match between validators, tests, and markdown docs.
- File paths are consistent across all tasks and match the spec.
