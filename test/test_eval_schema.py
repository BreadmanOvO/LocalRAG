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

    def test_validate_dataset_accepts_gold_set_file(self):
        path = REPO_ROOT / "data" / "evaluation" / "gold" / "gold_set.json"
        records = json.loads(path.read_text(encoding="utf-8"))

        self.assertGreaterEqual(len(records), 5)
        validate_dataset(records)

    def test_validate_dataset_accepts_synthetic_dataset_file(self):
        path = REPO_ROOT / "data" / "evaluation" / "synthetic" / "synthetic_dataset.json"
        records = json.loads(path.read_text(encoding="utf-8"))

        self.assertGreaterEqual(len(records), 10)
        validate_dataset(records)


if __name__ == "__main__":
    unittest.main()
