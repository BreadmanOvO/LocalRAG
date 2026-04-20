# v1.0 Baseline Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the minimum executable v1.0 evaluation baseline for LocalRAG: seed Gold/Synthetic datasets, shared schema validation, runnable evaluation scripts, and saved baseline result artifacts on top of the current Chroma + Tongyi prototype.

**Architecture:** Keep the current Streamlit-oriented RAG path intact and add a lightweight offline evaluation path beside it. Define evaluation datasets under `data/evaluation/`, validate them with a shared schema module, run the current `RagService` in a one-question-at-a-time mode, and persist predictions, summary metrics, and judge-shaped comparison output under `results/`. Do not introduce v1.1/v1.2 retrieval changes in this plan.

**Tech Stack:** Python, LangChain, Chroma, DashScopeEmbeddings, Tongyi, JSON, unittest

---

## File Structure

- `data/evaluation/gold/gold_set.json` — seed Gold Set for trusted manual benchmark samples
- `data/evaluation/synthetic/synthetic_dataset.json` — seed Synthetic Set for broader coverage and regression runs
- `data/evaluation/shared/eval_schema.py` — shared dataset validation helpers for all evaluation records
- `data/evaluation/shared/source_registry.json` — existing source registry used as the canonical reference for valid source IDs in the seed datasets
- `eval_ragas.py` — minimal baseline evaluation runner that loads a dataset, invokes the baseline system, and writes prediction/metric artifacts
- `eval_llm_judge.py` — minimal judge scaffold that turns a predictions file into comparison-shaped output
- `results/baseline_predictions.json` — per-sample baseline outputs from the current system
- `results/baseline_metrics.json` — baseline summary counts and ratios
- `results/baseline_judge.json` — baseline judge scaffold output
- `test/test_eval_schema.py` — tests for schema validation and dataset file presence
- `test/test_eval_runners.py` — tests for runner helpers, result writing, prediction record shape, and judge summary shape
- `rag.py` — existing baseline RAG service; add one offline-friendly helper method only
- `README.md` — short baseline status note once the runnable path exists
- `docs/evaluation.md` — short note clarifying that v1.0 is currently a minimum executable baseline, not full real Ragas/judge yet

## Task 1: Add shared evaluation schema and validation tests

**Files:**
- Create: `data/evaluation/shared/eval_schema.py`
- Create: `test/test_eval_schema.py`

- [ ] **Step 1: Write the failing schema tests**

Create `test/test_eval_schema.py` with:

```python
import unittest

from data.evaluation.shared.eval_schema import validate_dataset, validate_record


class EvalSchemaTests(unittest.TestCase):
    def test_validate_record_accepts_minimum_gold_sample(self):
        record = {
            "id": "gold-001",
            "question": "Apollo Cyber RT 的作用是什么？",
            "reference_answer": "Apollo Cyber RT 是 Apollo 的实时通信与组件运行框架。",
            "evidence": [
                {
                    "quote": "Official Apollo runtime-framework material describing Cyber RT.",
                    "source_id": "apollo-doc-002",
                    "locator": "summary",
                }
            ],
            "metadata": {
                "difficulty": "basic",
                "topic": "system_architecture",
                "doc_type": "official_doc",
            },
        }
        validate_record(record)

    def test_validate_dataset_rejects_duplicate_ids(self):
        dataset = [
            {
                "id": "gold-001",
                "question": "Q1",
                "reference_answer": "A1",
                "evidence": [{"quote": "E1", "source_id": "apollo-doc-001", "locator": "summary"}],
                "metadata": {"difficulty": "basic", "topic": "perception", "doc_type": "official_doc"},
            },
            {
                "id": "gold-001",
                "question": "Q2",
                "reference_answer": "A2",
                "evidence": [{"quote": "E2", "source_id": "apollo-doc-002", "locator": "summary"}],
                "metadata": {"difficulty": "medium", "topic": "planning_control", "doc_type": "official_doc"},
            },
        ]
        with self.assertRaises(ValueError):
            validate_dataset(dataset)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the schema tests to verify they fail**

Run: `python -m unittest test.test_eval_schema -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'data.evaluation.shared.eval_schema'`

- [ ] **Step 3: Write the shared schema module**

Create `data/evaluation/shared/eval_schema.py` with:

```python
from __future__ import annotations

from typing import Iterable

REQUIRED_TOP_LEVEL_KEYS = {"id", "question", "reference_answer", "evidence", "metadata"}
REQUIRED_EVIDENCE_KEYS = {"quote", "source_id", "locator"}
REQUIRED_METADATA_KEYS = {"difficulty", "topic", "doc_type"}


def validate_record(record: dict) -> None:
    missing = REQUIRED_TOP_LEVEL_KEYS - set(record)
    if missing:
        raise ValueError(f"Missing required keys: {sorted(missing)}")

    if not isinstance(record["id"], str) or not record["id"].strip():
        raise ValueError("Record id must be a non-empty string")
    if not isinstance(record["question"], str) or not record["question"].strip():
        raise ValueError("Question must be a non-empty string")
    if not isinstance(record["reference_answer"], str) or not record["reference_answer"].strip():
        raise ValueError("Reference answer must be a non-empty string")

    evidence = record["evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("Evidence must be a non-empty list")
    for item in evidence:
        missing_evidence = REQUIRED_EVIDENCE_KEYS - set(item)
        if missing_evidence:
            raise ValueError(f"Missing evidence keys: {sorted(missing_evidence)}")

    metadata = record["metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dict")
    missing_metadata = REQUIRED_METADATA_KEYS - set(metadata)
    if missing_metadata:
        raise ValueError(f"Missing metadata keys: {sorted(missing_metadata)}")


def validate_dataset(records: Iterable[dict]) -> None:
    seen_ids: set[str] = set()
    for record in records:
        validate_record(record)
        record_id = record["id"]
        if record_id in seen_ids:
            raise ValueError(f"Duplicate record id: {record_id}")
        seen_ids.add(record_id)
```

- [ ] **Step 4: Run the schema tests to verify they pass**

Run: `python -m unittest test.test_eval_schema -v`
Expected: PASS with both tests green

- [ ] **Step 5: Commit the schema foundation**

```bash
git add data/evaluation/shared/eval_schema.py test/test_eval_schema.py
git commit -m "test: add evaluation dataset schema validation"
```

## Task 2: Add seed Gold Set and Synthetic Set files

**Files:**
- Create: `data/evaluation/gold/gold_set.json`
- Create: `data/evaluation/synthetic/synthetic_dataset.json`
- Modify: `test/test_eval_schema.py`

- [ ] **Step 1: Extend the schema tests to require loadable dataset files**

Replace `test/test_eval_schema.py` with:

```python
import json
import unittest
from pathlib import Path

from data.evaluation.shared.eval_schema import validate_dataset, validate_record


class EvalSchemaTests(unittest.TestCase):
    def test_validate_record_accepts_minimum_gold_sample(self):
        record = {
            "id": "gold-001",
            "question": "Apollo Cyber RT 的作用是什么？",
            "reference_answer": "Apollo Cyber RT 是 Apollo 的实时通信与组件运行框架。",
            "evidence": [
                {
                    "quote": "Official Apollo runtime-framework material describing Cyber RT.",
                    "source_id": "apollo-doc-002",
                    "locator": "summary",
                }
            ],
            "metadata": {
                "difficulty": "basic",
                "topic": "system_architecture",
                "doc_type": "official_doc",
            },
        }
        validate_record(record)

    def test_validate_dataset_rejects_duplicate_ids(self):
        dataset = [
            {
                "id": "gold-001",
                "question": "Q1",
                "reference_answer": "A1",
                "evidence": [{"quote": "E1", "source_id": "apollo-doc-001", "locator": "summary"}],
                "metadata": {"difficulty": "basic", "topic": "perception", "doc_type": "official_doc"},
            },
            {
                "id": "gold-001",
                "question": "Q2",
                "reference_answer": "A2",
                "evidence": [{"quote": "E2", "source_id": "apollo-doc-002", "locator": "summary"}],
                "metadata": {"difficulty": "medium", "topic": "planning_control", "doc_type": "official_doc"},
            },
        ]
        with self.assertRaises(ValueError):
            validate_dataset(dataset)


class EvalDatasetFileTests(unittest.TestCase):
    def test_gold_set_file_is_present_and_valid(self):
        path = Path("data/evaluation/gold/gold_set.json")
        self.assertTrue(path.exists(), path)
        records = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(records), 5)
        validate_dataset(records)

    def test_synthetic_set_file_is_present_and_valid(self):
        path = Path("data/evaluation/synthetic/synthetic_dataset.json")
        self.assertTrue(path.exists(), path)
        records = json.loads(path.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(records), 10)
        validate_dataset(records)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail because the dataset files do not exist yet**

Run: `python -m unittest test.test_eval_schema -v`
Expected: FAIL with missing file assertions for `gold_set.json` and `synthetic_dataset.json`

- [ ] **Step 3: Create the initial dataset files with valid source IDs from the existing registry**

Create `data/evaluation/gold/gold_set.json` with:

```json
[
  {
    "id": "gold-001",
    "question": "Apollo Cyber RT 的核心作用是什么？",
    "reference_answer": "Apollo Cyber RT 是 Apollo 的实时通信与组件运行框架，用于支持自动驾驶系统中的低延迟消息传递与模块协同。",
    "evidence": [
      {
        "quote": "Official Apollo runtime-framework material describing Cyber RT, its component model, scheduling model, and how it supports low-latency autonomous-driving workloads.",
        "source_id": "apollo-doc-002",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "system_architecture",
      "doc_type": "official_doc"
    }
  },
  {
    "id": "gold-002",
    "question": "Apollo 感知融合能力的目标是什么？",
    "reference_answer": "Apollo 感知融合能力的目标是整合多传感器信息，形成更稳定的环境理解结果，并为后续自动驾驶任务提供更可靠的感知输入。",
    "evidence": [
      {
        "quote": "Official Apollo perception-fusion material describing the multi-sensor fusion workflow and the role of fused perception in downstream driving tasks.",
        "source_id": "apollo-doc-005",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "sensor_fusion",
      "doc_type": "official_doc"
    }
  },
  {
    "id": "gold-003",
    "question": "UN R155 主要关注什么？",
    "reference_answer": "UN R155 主要关注车辆网络安全要求以及网络安全管理体系。",
    "evidence": [
      {
        "quote": "Official UNECE regulation text covering vehicle cyber-security requirements and the cyber-security management system.",
        "source_id": "standard-007",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "safety",
      "doc_type": "standard"
    }
  },
  {
    "id": "gold-004",
    "question": "BEVFormer 这类方法主要服务于自动驾驶中的哪一类问题？",
    "reference_answer": "BEVFormer 主要服务于自动驾驶感知问题，通过构建鸟瞰图表示来支持环境理解与下游感知任务。",
    "evidence": [
      {
        "quote": "Research paper on bird’s-eye-view perception that uses spatiotemporal transformers to build BEV features for autonomous-driving perception tasks.",
        "source_id": "paper-001",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "perception",
      "doc_type": "paper"
    }
  },
  {
    "id": "gold-005",
    "question": "Apollo Localization 的定位能力在系统中扮演什么角色？",
    "reference_answer": "它提供高精度位置估计和地图对齐能力，是规划与控制稳定运行的基础。",
    "evidence": [
      {
        "quote": "Official Apollo localization material describing the localization stack, map alignment, and the role of high-precision position estimation in autonomous driving.",
        "source_id": "apollo-doc-010",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "system_architecture",
      "doc_type": "official_doc"
    }
  }
]
```

Create `data/evaluation/synthetic/synthetic_dataset.json` with:

```json
[
  {
    "id": "syn-001",
    "question": "Apollo Open Platform overview 主要描述什么？",
    "reference_answer": "它主要描述 Apollo 的软硬件栈以及感知、定位、规划、控制和仿真等模块边界。",
    "evidence": [
      {
        "quote": "Official platform-overview material describing Apollo’s software stack, hardware stack, and module boundaries across perception, localization, planning, control, and simulation.",
        "source_id": "apollo-doc-004",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "system_architecture",
      "doc_type": "official_doc"
    }
  },
  {
    "id": "syn-002",
    "question": "Apollo Prediction 模块的作用是什么？",
    "reference_answer": "它用于预测周围交通参与者的行为，并把预测结果提供给规划模块。",
    "evidence": [
      {
        "quote": "Official Apollo prediction material describing how the system predicts surrounding-agent behavior and feeds that forecast into planning.",
        "source_id": "apollo-doc-007",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "planning_control",
      "doc_type": "official_doc"
    }
  },
  {
    "id": "syn-003",
    "question": "Apollo Planning 模块负责什么？",
    "reference_answer": "它负责基于场景进行规划，输出后续控制模块可执行的轨迹或规划结果。",
    "evidence": [
      {
        "quote": "Official Apollo planning material describing scenario-based planning, planner responsibilities, and the inputs and outputs of the planning module.",
        "source_id": "apollo-doc-008",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "planning_control",
      "doc_type": "official_doc"
    }
  },
  {
    "id": "syn-004",
    "question": "Apollo Control 模块负责把什么转换成什么？",
    "reference_answer": "Apollo Control 模块负责把规划轨迹转换成转向、油门和制动等控制指令。",
    "evidence": [
      {
        "quote": "Official Apollo control material describing how planned trajectories are converted into steering, throttle, and brake commands.",
        "source_id": "apollo-doc-009",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "planning_control",
      "doc_type": "official_doc"
    }
  },
  {
    "id": "syn-005",
    "question": "Apollo Channel Data Format 文档主要说明什么？",
    "reference_answer": "它主要说明 Apollo 模块如何通过 Cyber RT channel 进行通信，以及感知、预测、规划和控制中使用的消息类型。",
    "evidence": [
      {
        "quote": "Official Apollo channel-format material describing how modules communicate through Cyber RT channels and which message types are used for perception, prediction, planning, and control.",
        "source_id": "apollo-doc-003",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "medium",
      "topic": "system_architecture",
      "doc_type": "official_doc"
    }
  },
  {
    "id": "syn-006",
    "question": "BEVFusion 的核心方向是什么？",
    "reference_answer": "BEVFusion 的核心方向是统一相机和激光雷达等多模态输入，在鸟瞰图空间中进行融合感知。",
    "evidence": [
      {
        "quote": "Research paper on unified BEV fusion across LiDAR and camera inputs for robust autonomous-driving perception.",
        "source_id": "paper-002",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "medium",
      "topic": "sensor_fusion",
      "doc_type": "paper"
    }
  },
  {
    "id": "syn-007",
    "question": "Occupancy Flow Fields 主要连接了哪两类能力？",
    "reference_answer": "它连接了场景理解和下游运动预测能力。",
    "evidence": [
      {
        "quote": "Research paper on occupancy-based motion forecasting for autonomous driving, connecting scene understanding to downstream behavior prediction.",
        "source_id": "paper-003",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "medium",
      "topic": "planning_control",
      "doc_type": "paper"
    }
  },
  {
    "id": "syn-008",
    "question": "VAD 的向量化场景表示主要面向哪类目标？",
    "reference_answer": "主要面向把感知、预测和规划更高效地连接起来。",
    "evidence": [
      {
        "quote": "End-to-end autonomous-driving research paper using vectorized scene representation to connect perception, prediction, and planning efficiently.",
        "source_id": "paper-005",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "medium",
      "topic": "planning_control",
      "doc_type": "paper"
    }
  },
  {
    "id": "syn-009",
    "question": "UN R156 主要关注什么？",
    "reference_answer": "UN R156 主要关注软件更新要求以及软件更新管理体系。",
    "evidence": [
      {
        "quote": "Official UNECE regulation text covering software update requirements and the software update management system.",
        "source_id": "standard-008",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "safety",
      "doc_type": "standard"
    }
  },
  {
    "id": "syn-010",
    "question": "UN R157 主要规范哪类自动驾驶功能？",
    "reference_answer": "它主要规范自动车道保持系统及其适用运行条件。",
    "evidence": [
      {
        "quote": "Official UNECE regulation text covering automated lane keeping systems and the operating conditions for that automated-driving function.",
        "source_id": "standard-009",
        "locator": "summary"
      }
    ],
    "metadata": {
      "difficulty": "basic",
      "topic": "safety",
      "doc_type": "standard"
    }
  }
]
```

- [ ] **Step 4: Run the schema tests to verify both dataset files pass validation**

Run: `python -m unittest test.test_eval_schema -v`
Expected: PASS with the schema tests and file-presence tests green

- [ ] **Step 5: Commit the initial evaluation datasets**

```bash
git add data/evaluation/gold/gold_set.json data/evaluation/synthetic/synthetic_dataset.json test/test_eval_schema.py
git commit -m "feat: add initial baseline evaluation datasets"
```

## Task 3: Add runner utilities and helper tests

**Files:**
- Create: `eval_ragas.py`
- Create: `test/test_eval_runners.py`

- [ ] **Step 1: Write the failing runner tests**

Create `test/test_eval_runners.py` with:

```python
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from eval_ragas import summarize_predictions, write_json


class EvalRunnerTests(unittest.TestCase):
    def test_summarize_predictions_counts_answered_samples(self):
        predictions = [
            {"id": "gold-001", "answer": "A", "retrieved_context": "C1"},
            {"id": "gold-002", "answer": "", "retrieved_context": ""},
        ]
        summary = summarize_predictions(predictions)
        self.assertEqual(2, summary["sample_count"])
        self.assertEqual(1, summary["answered_count"])
        self.assertEqual(1, summary["context_hit_count"])

    def test_write_json_creates_parent_directory(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "results" / "baseline_metrics.json"
            write_json(path, {"ok": True})
            data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual({"ok": True}, data)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the runner tests to verify they fail**

Run: `python -m unittest test.test_eval_runners -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_ragas'`

- [ ] **Step 3: Write the minimal baseline runner utilities**

Create `eval_ragas.py` with:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from data.evaluation.shared.eval_schema import validate_dataset


def load_dataset(path: Path) -> list[dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    validate_dataset(records)
    return records


def write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_predictions(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    answered_count = sum(1 for row in predictions if row.get("answer", "").strip())
    context_count = sum(1 for row in predictions if row.get("retrieved_context", "").strip())
    sample_count = len(predictions)
    return {
        "sample_count": sample_count,
        "answered_count": answered_count,
        "answered_ratio": round(answered_count / sample_count, 3) if sample_count else 0.0,
        "context_hit_count": context_count,
        "context_hit_ratio": round(context_count / sample_count, 3) if sample_count else 0.0,
    }
```

- [ ] **Step 4: Run the runner tests to verify they pass**

Run: `python -m unittest test.test_eval_runners -v`
Expected: PASS with both runner tests green

- [ ] **Step 5: Commit the runner utility foundation**

```bash
git add eval_ragas.py test/test_eval_runners.py
git commit -m "feat: add baseline evaluation runner utilities"
```

## Task 4: Wire the runner to the current RAG stack and save baseline results

**Files:**
- Modify: `rag.py`
- Modify: `eval_ragas.py`
- Modify: `test/test_eval_runners.py`

- [ ] **Step 1: Extend the runner tests to require a normalized prediction record helper**

Replace `test/test_eval_runners.py` with:

```python
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from eval_ragas import build_prediction_record, summarize_predictions, write_json


class EvalRunnerTests(unittest.TestCase):
    def test_summarize_predictions_counts_answered_samples(self):
        predictions = [
            {"id": "gold-001", "answer": "A", "retrieved_context": "C1"},
            {"id": "gold-002", "answer": "", "retrieved_context": ""},
        ]
        summary = summarize_predictions(predictions)
        self.assertEqual(2, summary["sample_count"])
        self.assertEqual(1, summary["answered_count"])
        self.assertEqual(1, summary["context_hit_count"])

    def test_write_json_creates_parent_directory(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "results" / "baseline_metrics.json"
            write_json(path, {"ok": True})
            data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual({"ok": True}, data)


class EvalPredictionRecordTests(unittest.TestCase):
    def test_build_prediction_record_contains_required_fields(self):
        record = build_prediction_record(
            sample={
                "id": "gold-001",
                "question": "Q",
                "reference_answer": "A_ref",
                "evidence": [{"quote": "E", "source_id": "apollo-doc-001", "locator": "summary"}],
                "metadata": {"difficulty": "basic", "topic": "perception", "doc_type": "official_doc"},
            },
            answer="A_pred",
            retrieved_context="ctx",
        )
        self.assertEqual("gold-001", record["id"])
        self.assertEqual("Q", record["question"])
        self.assertEqual("A_ref", record["reference_answer"])
        self.assertEqual("A_pred", record["answer"])
        self.assertEqual("ctx", record["retrieved_context"])
        self.assertIn("metadata", record)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail because the prediction helper does not exist yet**

Run: `python -m unittest test.test_eval_runners -v`
Expected: FAIL with `ImportError` for `build_prediction_record`

- [ ] **Step 3: Add one offline-friendly RAG entrypoint and complete the baseline runner**

Append this method to `RagService` in `rag.py`:

```python
    def answer_once(self, question: str, session_id: str = "eval-session") -> str:
        return self.chain.invoke(
            {"question": question},
            config={"configurable": {"session_id": session_id}},
        )
```

Replace `eval_ragas.py` with:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from data.evaluation.shared.eval_schema import validate_dataset


def load_dataset(path: Path) -> list[dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    validate_dataset(records)
    return records


def write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def summarize_predictions(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    answered_count = sum(1 for row in predictions if row.get("answer", "").strip())
    context_count = sum(1 for row in predictions if row.get("retrieved_context", "").strip())
    sample_count = len(predictions)
    return {
        "sample_count": sample_count,
        "answered_count": answered_count,
        "answered_ratio": round(answered_count / sample_count, 3) if sample_count else 0.0,
        "context_hit_count": context_count,
        "context_hit_ratio": round(context_count / sample_count, 3) if sample_count else 0.0,
    }


def build_prediction_record(sample: dict[str, Any], answer: str, retrieved_context: str) -> dict[str, Any]:
    return {
        "id": sample["id"],
        "question": sample["question"],
        "reference_answer": sample["reference_answer"],
        "answer": answer,
        "retrieved_context": retrieved_context,
        "metadata": sample["metadata"],
    }


def run_baseline(dataset_path: Path, predictions_path: Path, metrics_path: Path) -> dict[str, Any]:
    from rag import RagService

    dataset = load_dataset(dataset_path)
    rag = RagService()
    predictions: list[dict[str, Any]] = []

    for sample in dataset:
        answer = rag.answer_once(sample["question"], session_id="baseline-eval")
        predictions.append(
            build_prediction_record(
                sample=sample,
                answer=answer,
                retrieved_context="",
            )
        )

    summary = summarize_predictions(predictions)
    summary["dataset_path"] = dataset_path.as_posix()
    summary["predictions_path"] = predictions_path.as_posix()

    write_json(predictions_path, predictions)
    write_json(metrics_path, summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LocalRAG baseline evaluation.")
    parser.add_argument("--dataset", required=True, help="Path to gold or synthetic dataset json.")
    parser.add_argument("--predictions-out", required=True, help="Path to save per-sample predictions.")
    parser.add_argument("--metrics-out", required=True, help="Path to save summary metrics.")
    args = parser.parse_args()

    summary = run_baseline(
        dataset_path=Path(args.dataset),
        predictions_path=Path(args.predictions_out),
        metrics_path=Path(args.metrics_out),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to verify the runner helpers pass**

Run: `python -m unittest test.test_eval_runners -v`
Expected: PASS with all runner tests green

- [ ] **Step 5: Run the first baseline on the Gold Set**

Run: `python eval_ragas.py --dataset data/evaluation/gold/gold_set.json --predictions-out results/baseline_predictions.json --metrics-out results/baseline_metrics.json`
Expected: PASS with JSON summary printed and both result files written under `results/`

- [ ] **Step 6: Commit the runnable baseline evaluation path**

```bash
git add rag.py eval_ragas.py test/test_eval_runners.py results/baseline_predictions.json results/baseline_metrics.json
git commit -m "feat: run baseline evaluation on current rag stack"
```

## Task 5: Add the minimal judge scaffold and output file

**Files:**
- Create: `eval_llm_judge.py`
- Modify: `test/test_eval_runners.py`

- [ ] **Step 1: Extend the tests to require a judge summary helper**

Replace `test/test_eval_runners.py` with:

```python
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from eval_llm_judge import summarize_judgements
from eval_ragas import build_prediction_record, summarize_predictions, write_json


class EvalRunnerTests(unittest.TestCase):
    def test_summarize_predictions_counts_answered_samples(self):
        predictions = [
            {"id": "gold-001", "answer": "A", "retrieved_context": "C1"},
            {"id": "gold-002", "answer": "", "retrieved_context": ""},
        ]
        summary = summarize_predictions(predictions)
        self.assertEqual(2, summary["sample_count"])
        self.assertEqual(1, summary["answered_count"])
        self.assertEqual(1, summary["context_hit_count"])

    def test_write_json_creates_parent_directory(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "results" / "baseline_metrics.json"
            write_json(path, {"ok": True})
            data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual({"ok": True}, data)


class EvalPredictionRecordTests(unittest.TestCase):
    def test_build_prediction_record_contains_required_fields(self):
        record = build_prediction_record(
            sample={
                "id": "gold-001",
                "question": "Q",
                "reference_answer": "A_ref",
                "evidence": [{"quote": "E", "source_id": "apollo-doc-001", "locator": "summary"}],
                "metadata": {"difficulty": "basic", "topic": "perception", "doc_type": "official_doc"},
            },
            answer="A_pred",
            retrieved_context="ctx",
        )
        self.assertEqual("gold-001", record["id"])
        self.assertEqual("Q", record["question"])
        self.assertEqual("A_ref", record["reference_answer"])
        self.assertEqual("A_pred", record["answer"])
        self.assertEqual("ctx", record["retrieved_context"])
        self.assertIn("metadata", record)


class EvalJudgeTests(unittest.TestCase):
    def test_summarize_judgements_counts_wins_losses_and_ties(self):
        summary = summarize_judgements(
            [
                {"winner": "candidate"},
                {"winner": "baseline"},
                {"winner": "tie"},
            ]
        )
        self.assertEqual(3, summary["sample_count"])
        self.assertEqual(1, summary["candidate_win_count"])
        self.assertEqual(1, summary["baseline_win_count"])
        self.assertEqual(1, summary["tie_count"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail because the judge module does not exist yet**

Run: `python -m unittest test.test_eval_runners -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'eval_llm_judge'`

- [ ] **Step 3: Write the minimal judge script**

Create `eval_llm_judge.py` with:

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_predictions(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_judgements(rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_win_count = sum(1 for row in rows if row.get("winner") == "candidate")
    baseline_win_count = sum(1 for row in rows if row.get("winner") == "baseline")
    tie_count = sum(1 for row in rows if row.get("winner") == "tie")
    total = len(rows)
    return {
        "sample_count": total,
        "candidate_win_count": candidate_win_count,
        "baseline_win_count": baseline_win_count,
        "tie_count": tie_count,
    }


def run_self_comparison(predictions_path: Path, output_path: Path) -> dict[str, Any]:
    predictions = load_predictions(predictions_path)
    rows = []
    for row in predictions:
        rows.append(
            {
                "id": row["id"],
                "winner": "tie",
                "reason": "Self-comparison baseline run",
            }
        )

    summary = summarize_judgements(rows)
    payload = {"summary": summary, "rows": rows}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LocalRAG pairwise baseline judge.")
    parser.add_argument("--predictions", required=True, help="Prediction json path.")
    parser.add_argument("--out", required=True, help="Judge output json path.")
    args = parser.parse_args()

    summary = run_self_comparison(Path(args.predictions), Path(args.out))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to verify the judge helpers pass**

Run: `python -m unittest test.test_eval_runners -v`
Expected: PASS with the judge test included

- [ ] **Step 5: Run the judge script on the baseline predictions file**

Run: `python eval_llm_judge.py --predictions results/baseline_predictions.json --out results/baseline_judge.json`
Expected: PASS with JSON summary printed and `results/baseline_judge.json` written

- [ ] **Step 6: Commit the judge scaffold**

```bash
git add eval_llm_judge.py test/test_eval_runners.py results/baseline_judge.json
git commit -m "feat: add baseline pairwise judge scaffold"
```

## Task 6: Run the complete v1.0 bundle and document the current state

**Files:**
- Modify: `README.md`
- Modify: `docs/evaluation.md`
- Modify: `results/baseline_metrics.json`
- Modify: `results/baseline_predictions.json`
- Modify: `results/baseline_judge.json`

- [ ] **Step 1: Run the full baseline command sequence**

Run: `python -m unittest test.test_eval_schema test.test_eval_runners -v`
Expected: PASS with schema and runner tests green

Run: `python eval_ragas.py --dataset data/evaluation/gold/gold_set.json --predictions-out results/baseline_predictions.json --metrics-out results/baseline_metrics.json`
Expected: PASS with baseline outputs updated

Run: `python eval_llm_judge.py --predictions results/baseline_predictions.json --out results/baseline_judge.json`
Expected: PASS with judge output updated

- [ ] **Step 2: Add a baseline status note to `README.md`**

Insert this bullet under the current-phase section in `README.md`:

```md
- baseline 状态：Gold Set / Synthetic Set / `eval_ragas.py` / `eval_llm_judge.py` 已具备首个可执行版本，后续继续扩样本与补充真实 Ragas 指标。
```

- [ ] **Step 3: Add an implementation-status note to `docs/evaluation.md`**

Append this sentence to the usage section in `docs/evaluation.md`:

```md
当前阶段的目标是先跑通最小可执行 baseline：先产出可复用的数据集文件、预测结果文件和基线指标文件，再逐步补充更完整的 Ragas 指标与真实 pairwise judge 流程。
```

- [ ] **Step 4: Commit the complete v1.0 baseline bundle**

```bash
git add README.md docs/evaluation.md results/baseline_metrics.json results/baseline_predictions.json results/baseline_judge.json
git commit -m "feat: establish executable v1 baseline evaluation"
```

## Self-Review Checklist

- Spec coverage: this plan covers the minimum v1.0 baseline outputs from the spec — Gold Set, Synthetic Set, schema validation, executable evaluation runner, judge scaffold, result artifacts, and contract-focused tests.
- Placeholder scan: there are no `TODO`, `TBD`, “similar to Task N”, or undefined file references in the plan.
- Type consistency: the dataset shape is consistent across `eval_schema.py`, dataset JSON files, `build_prediction_record`, and the judge input/output steps. The runner imports `RagService` lazily inside `run_baseline`, so helper tests can import `eval_ragas.py` without constructing the full model stack.
