import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.modules.setdefault("knowledge_base", types.SimpleNamespace(KnowledgeBaseService=object))
sys.modules.setdefault("rag", types.SimpleNamespace(RagService=object))

import eval_chunking
from eval_llm_judge import summarize_judgements
from eval_ragas import (
    build_prediction_record,
    build_session_id,
    require_runtime_keys,
    run_baseline,
    summarize_predictions,
    write_json,
)


class EvalRunnerTests(unittest.TestCase):
    def test_build_prediction_record_includes_required_fields(self):
        record = build_prediction_record(
            {
                "id": "sample-1",
                "question": "What is LocalRAG?",
                "reference_answer": "A local retrieval augmented generation project.",
                "metadata": {"source": "gold"},
            },
            "A local retrieval augmented generation project.",
            "",
        )

        self.assertEqual(record["id"], "sample-1")
        self.assertEqual(record["answer"], "A local retrieval augmented generation project.")
        self.assertEqual(record["retrieved_context"], "")
        self.assertEqual(
            record["reference_answer"],
            "A local retrieval augmented generation project.",
        )

    def test_build_session_id_isolated_per_sample(self):
        self.assertEqual(build_session_id({"id": "sample-1"}), "eval-session-sample-1")
        self.assertEqual(build_session_id({"id": 42}), "eval-session-42")

    def test_summarize_predictions_counts_answered_and_context_hits(self):
        summary = summarize_predictions(
            [
                {"id": 1, "answer": "Answer 1", "retrieved_context": "C1"},
                {"id": 2, "answer": "", "retrieved_context": ""},
                {"id": 3, "answer": "   ", "retrieved_context": "C2"},
            ]
        )

        self.assertEqual(summary["sample_count"], 3)
        self.assertEqual(summary["answered_count"], 1)
        self.assertEqual(summary["answered_ratio"], 0.333)
        self.assertEqual(summary["context_hit_count"], 2)
        self.assertEqual(summary["context_hit_ratio"], 0.667)

    def test_summarize_judgements_counts_winners_and_ties(self):
        summary = summarize_judgements(
            [
                {"id": "sample-1", "winner": "candidate", "reason": "c1"},
                {"id": "sample-2", "winner": "baseline", "reason": "b1"},
                {"id": "sample-3", "winner": "tie", "reason": "t1"},
                {"id": "sample-4", "winner": "candidate", "reason": "c2"},
            ]
        )

        self.assertEqual(summary["sample_count"], 4)
        self.assertEqual(summary["candidate_win_count"], 2)
        self.assertEqual(summary["baseline_win_count"], 1)
        self.assertEqual(summary["tie_count"], 1)

    def test_run_baseline_uses_distinct_session_ids_per_sample(self):
        samples = [
            {
                "id": "sample-1",
                "question": "What is LocalRAG?",
                "reference_answer": "A local RAG project.",
                "evidence": [
                    {"quote": "LocalRAG", "source_id": "doc-1", "locator": "p1"}
                ],
                "metadata": {"difficulty": "easy", "topic": "rag", "doc_type": "guide"},
            },
            {
                "id": "sample-2",
                "question": "What does it test?",
                "reference_answer": "Baseline evaluation.",
                "evidence": [
                    {"quote": "baseline", "source_id": "doc-2", "locator": "p2"}
                ],
                "metadata": {"difficulty": "easy", "topic": "evaluation", "doc_type": "guide"},
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            dataset_path = temp_dir / "dataset.json"
            predictions_path = temp_dir / "predictions.json"
            metrics_path = temp_dir / "metrics.json"
            dataset_path.write_text(json.dumps(samples), encoding="utf-8")

            fake_rag_module = types.SimpleNamespace()
            fake_rag_service = mock.Mock()
            fake_rag_service.answer_once.side_effect = ["answer-1", "answer-2"]
            fake_rag_module.RagService = mock.Mock(return_value=fake_rag_service)

            with (
                mock.patch.dict(sys.modules, {"rag": fake_rag_module}),
                mock.patch("eval_ragas.load_bailian_runtime_config", return_value=None),
            ):
                summary = run_baseline(dataset_path, predictions_path, metrics_path)

            self.assertEqual(summary["sample_count"], 2)
            self.assertEqual(fake_rag_module.RagService.call_count, 1)
            fake_rag_service.answer_once.assert_has_calls(
                [
                    mock.call("What is LocalRAG?", session_id="eval-session-sample-1"),
                    mock.call("What does it test?", session_id="eval-session-sample-2"),
                ]
            )
            self.assertEqual(
                [call.kwargs["session_id"] for call in fake_rag_service.answer_once.call_args_list],
                ["eval-session-sample-1", "eval-session-sample-2"],
            )
            self.assertTrue(predictions_path.exists())
            self.assertTrue(metrics_path.exists())

    def test_require_runtime_keys_calls_runtime_config_loader(self):
        with mock.patch("eval_ragas.load_bailian_runtime_config", return_value=None) as loader:
            require_runtime_keys()

        loader.assert_called_once_with()

    def test_require_chunking_runtime_credentials_calls_runtime_config_loader(self):
        with mock.patch("eval_chunking.load_bailian_runtime_config", return_value=None) as loader:
            eval_chunking.require_runtime_credentials()

        loader.assert_called_once_with()

    def test_require_runtime_keys_surfaces_loader_runtime_error(self):
        with mock.patch(
            "eval_ragas.load_bailian_runtime_config",
            side_effect=RuntimeError("Missing runtime credentials"),
        ):
            with self.assertRaisesRegex(RuntimeError, "Missing runtime credentials"):
                require_runtime_keys()

    def test_require_chunking_runtime_credentials_surfaces_loader_runtime_error(self):
        with mock.patch(
            "eval_chunking.load_bailian_runtime_config",
            side_effect=RuntimeError("Missing runtime credentials"),
        ):
            with self.assertRaisesRegex(RuntimeError, "Missing runtime credentials"):
                eval_chunking.require_runtime_credentials()

    def test_write_json_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "nested" / "results" / "baseline.json"

            write_json(path, {"status": "ok"})

            self.assertTrue(path.exists())
            self.assertTrue(path.parent.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
