import importlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from langchain_core.documents import Document

import config_data as config
import knowledge_base
import rag


class RegistryBackedIngestionTests(unittest.TestCase):
    def test_ingest_document_uses_explicit_source_metadata(self):
        self.assertTrue(hasattr(knowledge_base.KnowledgeBaseService, "ingest_document"))

        mock_chroma = mock.Mock()
        text = "# Intro\n\n[p.1] Alpha paragraph for autonomous driving systems.\n\n" * 12
        source_metadata = {
            "source": "data/sources/apollo/sample.md",
            "source_id": "apollo-doc-001",
            "doc_type": "official_doc",
            "create_time": "2026-04-21 12:00:00",
            "operator": "tester",
        }
        chunking_config = {
            "official_doc": {"chunk_size": 80, "chunk_overlap": 10},
            "standard": {"chunk_size": 120, "chunk_overlap": 20},
            "paper": {"chunk_size": 120, "chunk_overlap": 20},
            "report": {"chunk_size": 120, "chunk_overlap": 20},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                mock.patch.object(knowledge_base, "Chroma", return_value=mock_chroma),
                mock.patch.object(knowledge_base, "DashScopeEmbeddings", return_value=object()),
                mock.patch.object(config, "persist_directory", temp_dir),
                mock.patch.object(config, "chunk_size", 40),
                mock.patch.object(config, "chunk_overlap", 5),
                mock.patch.object(config, "min_split_length", 10),
                mock.patch.object(config, "doc_type_chunking", chunking_config),
            ):
                service = knowledge_base.KnowledgeBaseService()
                chunk_records = service.ingest_document(
                    text,
                    source_metadata,
                    chunking_strategy="doc_type_aware",
                )

        self.assertGreater(len(chunk_records), 1)
        mock_chroma.add_texts.assert_called_once()
        metadatas = mock_chroma.add_texts.call_args.kwargs["metadatas"]
        self.assertEqual("apollo-doc-001", metadatas[0]["source_id"])
        self.assertEqual("official_doc", metadatas[0]["doc_type"])
        self.assertEqual("doc_type_aware", metadatas[0]["chunk_strategy"])
        self.assertEqual("data/sources/apollo/sample.md", metadatas[0]["source"])


class RagEvaluationHelperTests(unittest.TestCase):
    def test_answer_with_retrieval_returns_normalized_rows(self):
        self.assertTrue(hasattr(rag.RagService, "answer_with_retrieval"))

        service = object.__new__(rag.RagService)
        documents = [
            Document(
                page_content="Alpha chunk",
                metadata={
                    "source_id": "apollo-doc-001",
                    "doc_type": "official_doc",
                    "locator": "p.1 | § Intro",
                    "chunk_strategy": "baseline",
                },
            )
        ]
        service.retrieve_documents = mock.Mock(return_value=documents)
        service.answer_from_documents = mock.Mock(return_value="Alpha answer")

        result = rag.RagService.answer_with_retrieval(
            service,
            "What is Alpha?",
            session_id="eval-session-sample-1",
        )

        self.assertEqual("Alpha answer", result["answer"])
        self.assertIn("Alpha chunk", result["retrieved_context"])
        self.assertEqual(1, len(result["retrieved_rows"]))
        self.assertEqual("apollo-doc-001", result["retrieved_rows"][0]["source_id"])
        self.assertEqual("official_doc", result["retrieved_rows"][0]["doc_type"])
        self.assertEqual("p.1 | § Intro", result["retrieved_rows"][0]["locator"])
        self.assertEqual("baseline", result["retrieved_rows"][0]["chunk_strategy"])
        service.retrieve_documents.assert_called_once_with("What is Alpha?")
        service.answer_from_documents.assert_called_once_with(
            "What is Alpha?",
            documents,
            session_id="eval-session-sample-1",
        )


class ChunkingEvaluationContractTests(unittest.TestCase):
    def _load_module(self):
        spec = importlib.util.find_spec("eval_chunking")
        self.assertIsNotNone(spec)
        return importlib.import_module("eval_chunking")

    def _build_prediction(self, *, sample_id, doc_type, source_id, locator, answer, retrieved_rows):
        return {
            "id": sample_id,
            "question": f"Question {sample_id}",
            "reference_answer": f"Reference {sample_id}",
            "answer": answer,
            "retrieved_context": "\n".join(row["content"] for row in retrieved_rows),
            "retrieved_rows": retrieved_rows,
            "evidence": [{"quote": "Evidence", "source_id": source_id, "locator": locator}],
            "metadata": {"difficulty": "easy", "topic": "apollo", "doc_type": doc_type},
        }

    def test_summarize_chunking_predictions_counts_evidence_hits(self):
        eval_chunking = self._load_module()
        self.assertTrue(hasattr(eval_chunking, "summarize_chunking_predictions"))

        predictions = [
            self._build_prediction(
                sample_id="sample-1",
                doc_type="official_doc",
                source_id="apollo-doc-001",
                locator="p.1",
                answer="Answer 1",
                retrieved_rows=[
                    {
                        "source_id": "apollo-doc-001",
                        "doc_type": "official_doc",
                        "locator": "p.1",
                        "chunk_strategy": "baseline",
                        "content": "Alpha",
                    }
                ],
            ),
            self._build_prediction(
                sample_id="sample-2",
                doc_type="standard",
                source_id="std-doc-001",
                locator="p.9",
                answer="",
                retrieved_rows=[
                    {
                        "source_id": "other-doc",
                        "doc_type": "standard",
                        "locator": "p.2",
                        "chunk_strategy": "baseline",
                        "content": "Beta",
                    }
                ],
            ),
        ]

        summary = eval_chunking.summarize_chunking_predictions(predictions)

        self.assertEqual(2, summary["sample_count"])
        self.assertEqual(1, summary["answered_count"])
        self.assertEqual(0.5, summary["answered_ratio"])
        self.assertEqual(1, summary["evidence_source_hit_count"])
        self.assertEqual(0.5, summary["evidence_source_hit_ratio"])
        self.assertEqual(1, summary["evidence_locator_hit_count"])
        self.assertEqual(0.5, summary["evidence_locator_hit_ratio"])

    def test_build_store_and_run_strategy_use_registry_backed_paths(self):
        eval_chunking = self._load_module()
        self.assertTrue(hasattr(eval_chunking, "build_source_documents"))
        self.assertTrue(hasattr(eval_chunking, "run_strategy_evaluation"))

        dataset = [
            {
                "id": "gold-001",
                "question": "What is Apollo Cyber RT?",
                "reference_answer": "Framework answer",
                "evidence": [{"quote": "Cyber RT", "source_id": "apollo-doc-002", "locator": "chapter=1/overview"}],
                "metadata": {"difficulty": "easy", "topic": "system_architecture", "doc_type": "official_doc"},
            }
        ]
        registry_entries = [
            {
                "source_id": "apollo-doc-002",
                "doc_type": "official_doc",
                "path_or_url": "data/sources/apollo/apollo-cyber-rt.md",
            }
        ]
        fake_rag_service = mock.Mock()
        fake_rag_service.answer_with_retrieval.return_value = {
            "answer": "Framework answer",
            "retrieved_context": "Alpha chunk",
            "retrieved_rows": [
                {
                    "source_id": "apollo-doc-002",
                    "doc_type": "official_doc",
                    "locator": "chapter=1/overview",
                    "chunk_strategy": "baseline",
                    "content": "Alpha chunk",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            store_path = Path(temp_dir) / "baseline-store"
            with (
                mock.patch.object(eval_chunking, "load_source_registry", return_value=registry_entries),
                mock.patch.object(eval_chunking, "read_text", return_value="# Cyber RT\n\n[p.1] Alpha chunk"),
                mock.patch.object(eval_chunking, "KnowledgeBaseService") as mock_kb_cls,
                mock.patch.object(eval_chunking, "RagService", return_value=fake_rag_service),
            ):
                mock_kb = mock.Mock()
                mock_kb.ingest_document.return_value = []
                mock_kb_cls.return_value = mock_kb

                eval_chunking.build_source_documents(store_path, "baseline")
                predictions = eval_chunking.run_strategy_evaluation(dataset, store_path)

        self.assertEqual(1, len(predictions))
        ingest_call = mock_kb.ingest_document.call_args
        self.assertEqual("official_doc", ingest_call.args[1]["doc_type"])
        self.assertEqual("apollo-doc-002", ingest_call.args[1]["source_id"])
        self.assertEqual("baseline", ingest_call.kwargs["chunking_strategy"])
        self.assertEqual("Framework answer", predictions[0]["answer"])
        self.assertEqual("apollo-doc-002", predictions[0]["retrieved_rows"][0]["source_id"])

    def test_build_comparison_artifacts_matches_rows_by_sample_id(self):
        eval_chunking = self._load_module()

        baseline_predictions = [
            self._build_prediction(
                sample_id="sample-1",
                doc_type="official_doc",
                source_id="apollo-doc-001",
                locator="p.1",
                answer="Baseline one",
                retrieved_rows=[
                    {
                        "source_id": "apollo-doc-001",
                        "doc_type": "official_doc",
                        "locator": "p.1",
                        "chunk_strategy": "baseline",
                        "content": "Alpha",
                    }
                ],
            ),
            self._build_prediction(
                sample_id="sample-2",
                doc_type="standard",
                source_id="standard-001",
                locator="p.2",
                answer="Baseline two",
                retrieved_rows=[
                    {
                        "source_id": "standard-001",
                        "doc_type": "standard",
                        "locator": "p.2",
                        "chunk_strategy": "baseline",
                        "content": "Beta",
                    }
                ],
            ),
        ]
        candidate_predictions = [
            self._build_prediction(
                sample_id="sample-2",
                doc_type="standard",
                source_id="standard-001",
                locator="p.2",
                answer="Candidate two",
                retrieved_rows=[
                    {
                        "source_id": "standard-001",
                        "doc_type": "standard",
                        "locator": "p.2",
                        "chunk_strategy": "doc_type_aware",
                        "content": "Beta",
                    }
                ],
            ),
            self._build_prediction(
                sample_id="sample-1",
                doc_type="official_doc",
                source_id="apollo-doc-001",
                locator="p.1",
                answer="",
                retrieved_rows=[],
            ),
        ]

        comparison = eval_chunking.build_comparison_artifacts(
            baseline_predictions,
            candidate_predictions,
            eval_chunking.summarize_chunking_predictions(baseline_predictions),
            eval_chunking.summarize_chunking_predictions(candidate_predictions),
            run_id="gold-20260421-120000",
        )

        error_case = next(row for row in comparison["error_cases"] if row["id"] == "sample-1")
        self.assertFalse(error_case["doc_type_aware_answered"])
        self.assertFalse(error_case["doc_type_aware_source_hit"])

    def test_write_chunking_run_artifacts_writes_expected_files(self):
        eval_chunking = self._load_module()
        self.assertTrue(hasattr(eval_chunking, "build_comparison_artifacts"))
        self.assertTrue(hasattr(eval_chunking, "write_chunking_run_artifacts"))
        self.assertTrue(hasattr(eval_chunking, "render_chunking_report"))

        baseline_predictions = [
            self._build_prediction(
                sample_id="sample-1",
                doc_type="official_doc",
                source_id="apollo-doc-001",
                locator="p.1",
                answer="Baseline answer",
                retrieved_rows=[
                    {
                        "source_id": "apollo-doc-001",
                        "doc_type": "official_doc",
                        "locator": "p.1",
                        "chunk_strategy": "baseline",
                        "content": "Alpha",
                    }
                ],
            )
        ]
        candidate_predictions = [
            self._build_prediction(
                sample_id="sample-1",
                doc_type="official_doc",
                source_id="apollo-doc-001",
                locator="p.1",
                answer="Candidate answer",
                retrieved_rows=[
                    {
                        "source_id": "apollo-doc-001",
                        "doc_type": "official_doc",
                        "locator": "p.1",
                        "chunk_strategy": "doc_type_aware",
                        "content": "Alpha",
                    }
                ],
            )
        ]

        baseline_metrics = eval_chunking.summarize_chunking_predictions(baseline_predictions)
        candidate_metrics = eval_chunking.summarize_chunking_predictions(candidate_predictions)
        comparison = eval_chunking.build_comparison_artifacts(
            baseline_predictions,
            candidate_predictions,
            baseline_metrics,
            candidate_metrics,
            run_id="gold-20260421-120000",
        )
        report = eval_chunking.render_chunking_report(
            run_id="gold-20260421-120000",
            dataset_path=Path("data/evaluation/gold/gold_set.json"),
            baseline_store_path=Path("results/chunking_eval/stores/baseline"),
            candidate_store_path=Path("results/chunking_eval/stores/doc_type_aware"),
            comparison=comparison,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "results" / "chunking_eval" / "gold-20260421-120000"
            eval_chunking.write_chunking_run_artifacts(
                run_dir,
                baseline_predictions,
                baseline_metrics,
                candidate_predictions,
                candidate_metrics,
                comparison,
                report,
            )

            self.assertTrue((run_dir / "baseline" / "predictions.json").exists())
            self.assertTrue((run_dir / "baseline" / "metrics.json").exists())
            self.assertTrue((run_dir / "doc_type_aware" / "predictions.json").exists())
            self.assertTrue((run_dir / "doc_type_aware" / "metrics.json").exists())
            self.assertTrue((run_dir / "comparison" / "summary.json").exists())
            self.assertTrue((run_dir / "comparison" / "by_doc_type.json").exists())
            self.assertTrue((run_dir / "comparison" / "by_source_id.json").exists())
            self.assertTrue((run_dir / "comparison" / "error_cases.json").exists())
            self.assertTrue((run_dir / "report.md").exists())

            summary = json.loads((run_dir / "comparison" / "summary.json").read_text(encoding="utf-8"))
            report_text = (run_dir / "report.md").read_text(encoding="utf-8")

        self.assertEqual("gold-20260421-120000", summary["run_id"])
        self.assertIn("doc_type_aware", report_text)
        self.assertIn("official_doc", report_text)

    def test_repo_usage_guide_files_exist_and_link_core_entrypoints(self):
        repo_root = Path(__file__).resolve().parents[1]
        repo_guide = repo_root / "docs" / "repo_guide.md"
        self.assertTrue(repo_guide.exists())

        readme_text = (repo_root / "README.md").read_text(encoding="utf-8")
        guide_text = repo_guide.read_text(encoding="utf-8")

        self.assertIn("docs/repo_guide.md", readme_text)
        self.assertIn("eval_chunking.py", readme_text)
        self.assertIn("工程/运行文件", guide_text)
        self.assertIn("实验/评测脚本", guide_text)
        self.assertIn("results/chunking_eval/<run_id>/", guide_text)


if __name__ == "__main__":
    unittest.main()
