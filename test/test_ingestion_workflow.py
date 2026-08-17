import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from core.chunking import chunk_text_baseline
from core.ingestion_workflow import IngestionWorkflow, normalize_text
from core.knowledge_base import KnowledgeBaseService


class _FakeCollection:
    name = "rag"


class _FakeChroma:
    def __init__(self, persist_directory: Path):
        self._persist_directory = str(persist_directory)
        self._collection = _FakeCollection()
        self.rows = {}

    def add_texts(self, *, texts, metadatas, ids=None):
        ids = ids or [str(index) for index in range(len(texts))]
        for record_id, text, metadata in zip(ids, texts, metadatas):
            if record_id in self.rows:
                raise ValueError("duplicate id")
            self.rows[record_id] = (text, metadata)

    def delete(self, *, ids):
        for record_id in ids:
            self.rows.pop(record_id, None)


class IngestionWorkflowTests(unittest.TestCase):
    def test_normalize_text_rejects_empty_and_keeps_paragraphs(self):
        self.assertEqual("甲\n\n乙", normalize_text("\ufeff 甲\r\n\r\n\r\n乙 "))
        with self.assertRaises(ValueError):
            normalize_text(" \r\n\t")

    def test_stage_preview_and_optional_evaluation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            chroma = _FakeChroma(root / "store")
            kb = mock.Mock()
            kb.chroma = chroma
            kb._chunk_upload.side_effect = lambda text, metadata, chunking_strategy=None: chunk_text_baseline(
                text,
                source_metadata=metadata,
            )
            kb.chunk_record_id.side_effect = KnowledgeBaseService.chunk_record_id
            calls = []

            def manifest_builder(**kwargs):
                calls.append(kwargs)
                return {
                    "registry_source_count": 1,
                    "chunk_count": len(chroma.rows),
                    "corpus_fingerprint": "a" * 64,
                    "registry_fingerprint": "sha256:" + "b" * 64,
                }

            workflow = IngestionWorkflow(
                knowledge_base=kb,
                staging_directory=root / "staging",
                registry_path=root / "registry.json",
                active_profile_path=root / "active.json",
                uploaded_documents_directory=root / "uploads",
                manifest_builder=manifest_builder,
                refresh_callback=lambda: calls.append("refresh"),
            )
            staged = workflow.stage_text("第一段。\r\n\r\n第二段。", "sample.txt")
            self.assertTrue(staged.manifest_path.exists())
            self.assertEqual(staged.source_id, workflow.stage_text("第一段。\r\n\r\n第二段。", "other.txt").source_id)
            preview = workflow.preview(staged)
            self.assertEqual(staged.chunk_count, preview["chunk_count"])

            evaluator = mock.Mock(return_value={"passed": True})
            result = workflow.publish(staged, evaluate=False, evaluator=evaluator)
            self.assertTrue(result.published)
            evaluator.assert_not_called()
            self.assertEqual("refresh", calls[-1])
            self.assertEqual(1, len(json.loads((root / "registry.json").read_text(encoding="utf-8"))))
            profile = json.loads((root / "active.json").read_text(encoding="utf-8"))
            self.assertEqual(1, profile["source_count"])
            self.assertTrue(profile["corpus_fingerprint"].startswith("sha256:"))

            duplicate = workflow.publish(staged)
            self.assertFalse(duplicate.published)
            self.assertEqual("already_published", duplicate.reason)

    def test_evaluate_callback_is_invoked_when_requested(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            chroma = _FakeChroma(root / "store")
            kb = mock.Mock()
            kb.chroma = chroma
            kb._chunk_upload.side_effect = lambda text, metadata, chunking_strategy=None: chunk_text_baseline(
                text, source_metadata=metadata
            )
            kb.chunk_record_id.side_effect = KnowledgeBaseService.chunk_record_id
            workflow = IngestionWorkflow(
                knowledge_base=kb,
                staging_directory=root / "staging",
                registry_path=root / "registry.json",
                active_profile_path=root / "active.json",
                uploaded_documents_directory=root / "uploads",
                manifest_builder=lambda **kwargs: {
                    "registry_source_count": 1,
                    "chunk_count": 1,
                    "corpus_fingerprint": "a" * 64,
                    "registry_fingerprint": "sha256:" + "b" * 64,
                },
            )
            staged = workflow.stage_text("可评测内容", "eval.txt")
            evaluator = mock.Mock(return_value={"score": 0.9})
            result = workflow.publish(staged, evaluate=True, evaluator=evaluator)
            evaluator.assert_called_once_with(staged)
            self.assertEqual({"score": 0.9}, result.evaluation_result)


if __name__ == "__main__":
    unittest.main()
