import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from eval import eval_chunking
from eval import eval_llm_judge as judge_runner
from eval import eval_ragas as ragas_runner
from eval.eval_llm_judge import summarize_judgements
from eval.eval_ragas import (
    build_prediction_record,
    build_session_id,
    require_runtime_config,
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
                "evidence": [{"quote": "LocalRAG", "source_id": "doc-1", "locator": "p1"}],
                "metadata": {"source": "gold"},
            },
            {
                "answer": "A local retrieval augmented generation project.",
                "retrieved_context": "ctx-1",
                "retrieved_rows": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
                "retrieval_debug_candidates": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
            },
        )

        self.assertEqual(record["id"], "sample-1")
        self.assertEqual(record["answer"], "A local retrieval augmented generation project.")
        self.assertEqual(record["retrieved_context"], "ctx-1")
        self.assertEqual(record["retrieved_rows"][0]["source_id"], "doc-1")
        self.assertEqual(record["evidence"][0]["locator"], "p1")
        self.assertEqual(
            record["reference_answer"],
            "A local retrieval augmented generation project.",
        )

    def test_build_session_id_isolated_per_sample(self):
        self.assertEqual(build_session_id({"id": "sample-1"}), "eval-session-sample-1")
        self.assertEqual(build_session_id({"id": 42}), "eval-session-42")

    def test_summarize_predictions_counts_answered_context_and_evidence_hits(self):
        summary = summarize_predictions(
            [
                {
                    "id": 1,
                    "answer": "Answer 1",
                    "retrieved_context": "C1",
                    "retrieved_rows": [{"source_id": "doc-1", "locator": "p1"}],
                    "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}],
                },
                {
                    "id": 2,
                    "answer": "",
                    "retrieved_context": "",
                    "retrieved_rows": [{"source_id": "doc-x", "locator": "p9"}],
                    "evidence": [{"quote": "q2", "source_id": "doc-2", "locator": "p2"}],
                },
                {
                    "id": 3,
                    "answer": "   ",
                    "retrieved_context": "C2",
                    "retrieved_rows": [{"source_id": "doc-3", "locator": "p3   sec=1"}],
                    "evidence": [{"quote": "q3", "source_id": "doc-9", "locator": "p3 sec=1"}],
                },
            ]
        )

        self.assertEqual(summary["sample_count"], 3)
        self.assertEqual(summary["answered_count"], 1)
        self.assertEqual(summary["answered_ratio"], 0.333)
        self.assertEqual(summary["context_hit_count"], 2)
        self.assertEqual(summary["context_hit_ratio"], 0.667)
        self.assertEqual(summary["evidence_source_hit_count"], 1)
        self.assertEqual(summary["evidence_source_hit_ratio"], 0.333)
        self.assertEqual(summary["evidence_locator_hit_count"], 2)
        self.assertEqual(summary["evidence_locator_hit_ratio"], 0.667)

    def test_summarize_predictions_adds_objective_metrics(self):
        summary = summarize_predictions(
            [
                {
                    "id": "sample-1",
                    "reference_answer": "Apollo planning module",
                    "answer": "Apollo planning module",
                    "retrieved_context": "ctx-1",
                    "retrieved_rows": [{"source_id": "doc-1", "locator": "p1"}, {"source_id": "doc-2", "locator": "p2"}],
                    "retrieval_debug_candidates": [{"source_id": "doc-1"}, {"source_id": "doc-2"}],
                    "evidence": [{"quote": "Apollo planning module", "source_id": "doc-1", "locator": "p1"}],
                },
                {
                    "id": "sample-2",
                    "reference_answer": "Perception safety report",
                    "answer": " perception   safety report ",
                    "retrieved_context": "",
                    "retrieved_rows": [],
                    "retrieval_debug_candidates": [],
                    "evidence": [{"quote": "Perception safety report", "source_id": "doc-2", "locator": "p2"}],
                },
            ]
        )

        self.assertEqual(1, summary["exact_match_count"])
        self.assertEqual(0.5, summary["exact_match_ratio"])
        self.assertEqual(2, summary["normalized_exact_match_count"])
        self.assertEqual(1.0, summary["normalized_exact_match_ratio"])
        self.assertEqual(2, summary["retrieved_row_count"])
        self.assertEqual(1.0, summary["avg_retrieved_row_count"])
        self.assertEqual(2, summary["retrieval_debug_candidate_count"])
        self.assertEqual(1.0, summary["avg_retrieval_debug_candidate_count"])
        self.assertEqual(2, summary["reference_substring_hit_count"])
        self.assertEqual(1.0, summary["reference_substring_hit_ratio"])

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

    def test_run_pairwise_judge_aligns_by_id_and_uses_llm_verdicts(self):
        baseline_predictions = [
            {
                "id": "sample-1",
                "question": "Q1",
                "reference_answer": "R1",
                "answer": "baseline-1",
                "retrieved_rows": [{"source_id": "doc-x", "locator": "p9"}],
                "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}],
                "metadata": {"topic": "rag"},
            },
            {
                "id": "sample-2",
                "question": "Q2",
                "reference_answer": "R2",
                "answer": "baseline-2",
                "retrieved_rows": [{"source_id": "doc-2", "locator": "p2"}],
                "evidence": [{"quote": "q2", "source_id": "doc-2", "locator": "p2"}],
                "metadata": {"topic": "eval"},
            },
        ]
        candidate_predictions = [
            {
                "id": "sample-2",
                "question": "Q2",
                "reference_answer": "R2",
                "answer": "candidate-2",
                "retrieved_rows": [{"source_id": "doc-x", "locator": "p9"}],
                "evidence": [{"quote": "q2", "source_id": "doc-2", "locator": "p2"}],
                "metadata": {"topic": "eval"},
            },
            {
                "id": "sample-1",
                "question": "Q1",
                "reference_answer": "R1",
                "answer": "candidate-1",
                "retrieved_rows": [{"source_id": "doc-1", "locator": "p1"}],
                "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}],
                "metadata": {"topic": "rag"},
            },
        ]

        fake_runtime_config = types.SimpleNamespace(
            api_key="test-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            chat_model_name="qwen3-max",
            embedding_model_name="text-embedding-v4",
        )
        fake_chat_model = mock.Mock()
        fake_chat_model.invoke.side_effect = [
            '{"winner":"candidate","reason":"candidate answer uses better evidence"}',
            '{"winner":"baseline","reason":"baseline answer is more accurate"}',
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            output_path = temp_dir / "judgements.json"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with (
                mock.patch.object(judge_runner, "load_runtime_config", return_value=fake_runtime_config),
                mock.patch.object(judge_runner, "build_chat_model", return_value=fake_chat_model) as mock_chat,
            ):
                summary = judge_runner.run_pairwise_judge(baseline_path, candidate_path, output_path)

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(2, summary["sample_count"])
            self.assertEqual(1, payload["summary"]["candidate_win_count"])
            self.assertEqual(1, payload["summary"]["baseline_win_count"])
            self.assertEqual("sample-1", payload["rows"][0]["id"])
            self.assertEqual("baseline-1", payload["rows"][0]["baseline_answer"])
            self.assertEqual("candidate-1", payload["rows"][0]["candidate_answer"])
            self.assertEqual("candidate", payload["rows"][0]["winner"])
            self.assertEqual("candidate answer uses better evidence", payload["rows"][0]["reason"])
            self.assertEqual("baseline", payload["rows"][1]["winner"])
            mock_chat.assert_called_once_with(fake_runtime_config, temperature=0)
            self.assertEqual(2, fake_chat_model.invoke.call_count)

    def test_run_pairwise_judge_builds_model_with_deterministic_settings(self):
        baseline_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "b1", "retrieved_rows": [], "evidence": []}]
        candidate_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "c1", "retrieved_rows": [], "evidence": []}]
        fake_runtime_config = types.SimpleNamespace(
            provider="modelscope",
            api_key="test-key",
            base_url="https://api-inference.modelscope.cn/v1",
            chat_model_name="Qwen/Qwen2.5-72B-Instruct",
            embedding_model_name="Qwen/Qwen3-Embedding-8B",
        )
        fake_chat_model = mock.Mock()
        fake_chat_model.invoke.return_value = '{"winner":"candidate","reason":"candidate is more accurate"}'

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            output_path = temp_dir / "judgements.json"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with (
                mock.patch.object(judge_runner, "load_runtime_config", return_value=fake_runtime_config),
                mock.patch.object(judge_runner, "build_chat_model", return_value=fake_chat_model) as mock_chat,
            ):
                judge_runner.run_pairwise_judge(baseline_path, candidate_path, output_path)

            mock_chat.assert_called_once_with(fake_runtime_config, temperature=0)

    def test_run_pairwise_judge_accepts_wrapped_json_response(self):
        baseline_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "b1", "retrieved_rows": [], "evidence": []}]
        candidate_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "c1", "retrieved_rows": [], "evidence": []}]
        fake_runtime_config = types.SimpleNamespace(
            provider="modelscope",
            api_key="test-key",
            base_url="https://api-inference.modelscope.cn/v1",
            chat_model_name="Qwen/Qwen2.5-72B-Instruct",
            embedding_model_name="Qwen/Qwen3-Embedding-8B",
        )
        fake_chat_model = mock.Mock()
        fake_chat_model.invoke.return_value = "裁判结果如下\n{\"winner\":\"candidate\",\"reason\":\"candidate is more faithful to the reference answer\"}\n谢谢"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            output_path = temp_dir / "judgements.json"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with (
                mock.patch.object(judge_runner, "load_runtime_config", return_value=fake_runtime_config),
                mock.patch.object(judge_runner, "build_chat_model", return_value=fake_chat_model),
            ):
                judge_runner.run_pairwise_judge(baseline_path, candidate_path, output_path)

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual("candidate", payload["rows"][0]["winner"])
            self.assertEqual(
                "candidate is more faithful to the reference answer",
                payload["rows"][0]["reason"],
            )

    def test_run_pairwise_judge_rejects_mismatched_ids(self):
        baseline_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "b1"}]
        candidate_predictions = [{"id": "sample-2", "question": "Q2", "reference_answer": "R2", "answer": "c2"}]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            output_path = temp_dir / "judgements.json"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "same sample ids"):
                judge_runner.run_pairwise_judge(baseline_path, candidate_path, output_path)

    def test_run_pairwise_judge_to_dir_writes_manifest_bundle(self):
        baseline_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "", "retrieved_rows": [], "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}]}]
        candidate_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "c1", "retrieved_rows": [{"source_id": "doc-1", "locator": "p1"}], "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}]}]
        fake_runtime_config = types.SimpleNamespace(
            provider="modelscope",
            api_key="test-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            chat_model_name="qwen3-max",
            embedding_model_name="text-embedding-v4",
        )
        fake_chat_model = mock.Mock()
        fake_chat_model.invoke.return_value = '{"winner":"candidate","reason":"candidate is better"}'

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            out_dir = temp_dir / "judge_eval"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with (
                mock.patch.object(judge_runner, "load_runtime_config", return_value=fake_runtime_config),
                mock.patch.object(judge_runner, "build_chat_model", return_value=fake_chat_model),
            ):
                summary = judge_runner.run_pairwise_judge_to_dir(baseline_path, candidate_path, out_dir)

            run_dirs = list(out_dir.iterdir())
            self.assertEqual(1, len(run_dirs))
            run_dir = run_dirs[0]
            self.assertEqual(1, summary["sample_count"])
            self.assertTrue((run_dir / "judgements.json").exists())
            self.assertTrue((run_dir / "summary.json").exists())
            self.assertTrue((run_dir / "manifest.json").exists())
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("v1.1", manifest["contract_version"])
            self.assertEqual("judge_eval", manifest["pipeline"])
            self.assertEqual("modelscope", manifest["provider"])
            self.assertEqual("qwen3-max", manifest["chat_model_name"])
            self.assertEqual("v1.1-pairwise-judge", manifest["judge_prompt_version"])

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
            fake_rag_service.answer_with_retrieval.side_effect = [
                {
                    "answer": "answer-1",
                    "retrieved_context": "ctx-1",
                    "retrieved_rows": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
                    "retrieval_debug_candidates": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
                },
                {
                    "answer": "answer-2",
                    "retrieved_context": "ctx-2",
                    "retrieved_rows": [{"source_id": "doc-2", "locator": "p2", "content": "ctx-2"}],
                    "retrieval_debug_candidates": [{"source_id": "doc-2", "locator": "p2", "content": "ctx-2"}],
                },
            ]
            fake_rag_module.RagService = mock.Mock(return_value=fake_rag_service)

            with (
                mock.patch.dict(sys.modules, {"core.rag": fake_rag_module}),
                mock.patch("eval.eval_ragas.load_runtime_config", return_value=None),
            ):
                summary = run_baseline(dataset_path, predictions_path, metrics_path)

            self.assertEqual(summary["sample_count"], 2)
            self.assertEqual(summary["evidence_source_hit_count"], 2)
            self.assertEqual(summary["evidence_locator_hit_count"], 2)
            self.assertEqual(fake_rag_module.RagService.call_count, 1)
            fake_rag_service.answer_with_retrieval.assert_has_calls(
                [
                    mock.call("What is LocalRAG?", session_id="eval-session-sample-1"),
                    mock.call("What does it test?", session_id="eval-session-sample-2"),
                ]
            )
            self.assertEqual(
                [call.kwargs["session_id"] for call in fake_rag_service.answer_with_retrieval.call_args_list],
                ["eval-session-sample-1", "eval-session-sample-2"],
            )
            predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
            self.assertEqual("ctx-1", predictions[0]["retrieved_context"])
            self.assertEqual("doc-1", predictions[0]["retrieved_rows"][0]["source_id"])
            self.assertEqual("p2", predictions[1]["evidence"][0]["locator"])
            self.assertTrue(predictions_path.exists())
            self.assertTrue(metrics_path.exists())

    def test_run_baseline_to_dir_writes_manifest_bundle(self):
        samples = [
            {
                "id": "sample-1",
                "question": "What is LocalRAG?",
                "reference_answer": "A local RAG project.",
                "evidence": [
                    {"quote": "LocalRAG", "source_id": "doc-1", "locator": "p1"}
                ],
                "metadata": {"difficulty": "easy", "topic": "rag", "doc_type": "guide"},
            }
        ]
        fake_runtime_config = types.SimpleNamespace(
            provider="modelscope",
            api_key="test-key",
            base_url="https://api-inference.modelscope.cn/v1",
            chat_model_name="Qwen/Qwen2.5-72B-Instruct",
            embedding_model_name="Qwen/Qwen3-Embedding-8B",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            dataset_path = temp_dir / "gold_set.json"
            out_dir = temp_dir / "results"
            dataset_path.write_text(json.dumps(samples), encoding="utf-8")

            fake_rag_module = types.SimpleNamespace()
            fake_rag_service = mock.Mock()
            fake_rag_service.answer_with_retrieval.return_value = {
                "answer": "answer-1",
                "retrieved_context": "ctx-1",
                "retrieved_rows": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
                "retrieval_debug_candidates": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
            }
            fake_rag_module.RagService = mock.Mock(return_value=fake_rag_service)

            with (
                mock.patch.dict(sys.modules, {"core.rag": fake_rag_module}),
                mock.patch("eval.eval_ragas.load_runtime_config", return_value=fake_runtime_config),
            ):
                summary = ragas_runner.run_baseline_to_dir(dataset_path, out_dir)

            run_dirs = list(out_dir.iterdir())
            self.assertEqual(1, len(run_dirs))
            run_dir = run_dirs[0]
            self.assertEqual(1, summary["sample_count"])
            self.assertTrue((run_dir / "predictions.json").exists())
            self.assertTrue((run_dir / "metrics.json").exists())
            self.assertTrue((run_dir / "manifest.json").exists())
            metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(1, metrics["evidence_source_hit_count"])
            self.assertEqual(1, metrics["evidence_locator_hit_count"])
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("v1.1", manifest["contract_version"])
            self.assertEqual("baseline_eval", manifest["pipeline"])
            self.assertEqual(str(dataset_path), manifest["dataset_path"])
            self.assertEqual("modelscope", manifest["provider"])
            self.assertEqual("Qwen/Qwen2.5-72B-Instruct", manifest["chat_model_name"])
            self.assertEqual("Qwen/Qwen3-Embedding-8B", manifest["embedding_model_name"])

    def test_require_runtime_config_calls_runtime_config_loader(self):
        with mock.patch("eval.eval_ragas.load_runtime_config", return_value=None) as loader:
            require_runtime_config()

        loader.assert_called_once_with()

    def test_require_chunking_runtime_credentials_calls_runtime_config_loader(self):
        with mock.patch("eval.eval_chunking.load_runtime_config", return_value=None) as loader:
            eval_chunking.require_runtime_config()

        loader.assert_called_once_with()

    def test_require_runtime_config_surfaces_loader_runtime_error(self):
        with mock.patch(
            "eval.eval_ragas.load_runtime_config",
            side_effect=RuntimeError("Missing runtime credentials"),
        ):
            with self.assertRaisesRegex(RuntimeError, "Missing runtime credentials"):
                require_runtime_config()

    def test_require_chunking_runtime_credentials_surfaces_loader_runtime_error(self):
        with mock.patch(
            "eval.eval_chunking.load_runtime_config",
            side_effect=RuntimeError("Missing runtime credentials"),
        ):
            with self.assertRaisesRegex(RuntimeError, "Missing runtime credentials"):
                eval_chunking.require_runtime_config()

    def test_eval_scripts_support_direct_python_execution_import_path(self):
        eval_dir = Path(__file__).resolve().parents[1] / "eval"
        for file_name in ("eval_ragas.py", "eval_llm_judge.py", "eval_chunking.py"):
            content = (eval_dir / file_name).read_text(encoding="utf-8")
            self.assertIn("if __package__ in {None, \"\"}", content)
            self.assertIn("sys.path.insert(0, str(Path(__file__).resolve().parents[1]))", content)

    def test_write_json_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "nested" / "results" / "baseline.json"

            write_json(path, {"status": "ok"})

            self.assertTrue(path.exists())
            self.assertTrue(path.parent.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
