import json
import unittest
from pathlib import Path

from data.evaluation.shared.eval_schema import validate_dataset, validate_record

REPO_ROOT = Path(__file__).resolve().parents[1]


class EvalSchemaTests(unittest.TestCase):
    def test_validate_record_accepts_minimum_gold_sample(self):
        record = {
            "id": "eval-001",
            "question": "What is the minimum supported input?",
            "reference_answer": "A minimum gold sample.",
            "evidence": [
                {
                    "quote": "Minimum gold sample",
                    "source_id": "source-001",
                    "locator": "p.1",
                }
            ],
            "metadata": {
                "difficulty": "easy",
                "topic": "evaluation",
                "doc_type": "guide",
            },
        }

        validate_record(record)

    def test_validate_dataset_rejects_duplicate_ids(self):
        record = {
            "id": "eval-001",
            "question": "What is the minimum supported input?",
            "reference_answer": "A minimum gold sample.",
            "evidence": [
                {
                    "quote": "Minimum gold sample",
                    "source_id": "source-001",
                    "locator": "p.1",
                }
            ],
            "metadata": {
                "difficulty": "easy",
                "topic": "evaluation",
                "doc_type": "guide",
            },
        }

        with self.assertRaises(ValueError):
            validate_dataset([record, dict(record)])

    def test_validate_dataset_accepts_active_cleaned_dataset_files(self):
        datasets = {
            REPO_ROOT / "data" / "evaluation" / "gold" / "eval_set.json": 100,
            REPO_ROOT / "data" / "evaluation" / "gold" / "gold_set_100.json": 100,
            REPO_ROOT / "data" / "evaluation" / "gold" / "gold_set_extended.json": 100,
            REPO_ROOT / "data" / "evaluation" / "train" / "train_set.json": 203,
        }

        for path, expected_count in datasets.items():
            with self.subTest(path=path):
                records = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(len(records), expected_count)
                validate_dataset(records)

    def test_clean_eval_sets_cover_core_topics_and_report_doc_type(self):
        paths = [
            REPO_ROOT / "data" / "evaluation" / "gold" / "eval_set.json",
            REPO_ROOT / "data" / "evaluation" / "gold" / "gold_set_100.json",
            REPO_ROOT / "data" / "evaluation" / "gold" / "gold_set_extended.json",
        ]
        records = []
        for path in paths:
            records.extend(json.loads(path.read_text(encoding="utf-8")))

        topics = {record["metadata"]["topic"] for record in records}
        doc_types = {record["metadata"]["doc_type"] for record in records}

        self.assertTrue(
            {
                "system_architecture",
                "perception",
                "planning_control",
                "safety",
                "sensor_fusion",
            }.issubset(topics)
        )
        self.assertIn("paper", doc_types)

    def test_polluted_legacy_datasets_are_removed(self):
        legacy_paths = [
            REPO_ROOT / "data" / "evaluation" / "gold" / "gold_set.json",
            REPO_ROOT / "data" / "evaluation" / "synthetic" / "synthetic_dataset.json",
        ]

        for path in legacy_paths:
            self.assertFalse(path.exists(), f"Polluted legacy dataset still exists: {path}")


if __name__ == "__main__":
    unittest.main()
