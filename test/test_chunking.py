import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import config_data as config
import knowledge_base
from chunking import (
    ChunkRecord,
    build_locator,
    choose_chunking_strategy,
    chunk_text_baseline,
    chunk_text_doc_type_aware,
    extract_page_aware_segments,
)


class ChunkingTests(unittest.TestCase):
    def setUp(self):
        self.source_metadata = {
            "source": "sample.md",
            "source_id": "sample-001",
            "doc_type": "untyped",
            "create_time": "2026-04-21 10:00:00",
            "operator": "tester",
        }

    def test_baseline_chunking_emits_required_metadata(self):
        text = "段落一。" * 60
        with (
            mock.patch.object(config, "chunk_size", 40),
            mock.patch.object(config, "chunk_overlap", 5),
            mock.patch.object(config, "min_split_length", 10),
        ):
            chunks = chunk_text_baseline(text, source_metadata=self.source_metadata)

        self.assertGreater(len(chunks), 1)
        for index, chunk in enumerate(chunks):
            self.assertIsInstance(chunk, ChunkRecord)
            self.assertEqual(index, chunk.metadata["chunk_order"])
            self.assertEqual("baseline", chunk.metadata["chunk_strategy"])
            self.assertEqual("sample-001", chunk.metadata["source_id"])
            self.assertEqual("untyped", chunk.metadata["doc_type"])
            self.assertEqual("sample.md", chunk.metadata["source"])
            self.assertEqual("tester", chunk.metadata["operator"])

    def test_short_text_still_keeps_provenance_metadata(self):
        with mock.patch.object(config, "min_split_length", 9999):
            chunks = chunk_text_baseline("短文本", source_metadata=self.source_metadata)

        self.assertEqual(1, len(chunks))
        self.assertEqual(0, chunks[0].metadata["chunk_order"])
        self.assertEqual("baseline", chunks[0].metadata["chunk_strategy"])
        self.assertEqual("sample-001", chunks[0].metadata["source_id"])

    def test_extract_page_aware_segments_reads_page_and_section(self):
        text = "# Intro\n\n[p.1] Alpha paragraph.\n\n## Details\n\n[p.2] Beta paragraph."
        segments = extract_page_aware_segments(text)

        self.assertEqual(2, len(segments))
        self.assertEqual(1, segments[0]["page_start"])
        self.assertEqual("Intro", segments[0]["section_path"])
        self.assertEqual(2, segments[1]["page_start"])
        self.assertEqual("Intro > Details", segments[1]["section_path"])

    def test_build_locator_combines_page_and_section(self):
        locator = build_locator(page_start=2, section_path="Intro > Details")
        self.assertEqual("p.2 | § Intro > Details", locator)

    def test_choose_chunking_strategy_falls_back_for_untyped(self):
        self.assertEqual("baseline", choose_chunking_strategy("untyped", "doc_type_aware"))
        self.assertEqual("baseline", choose_chunking_strategy("official_doc", "baseline"))
        self.assertEqual("doc_type_aware", choose_chunking_strategy("official_doc", "doc_type_aware"))

    def test_doc_type_aware_standard_produces_fewer_chunks_than_official_doc(self):
        text = ("# Clause\n[p.1] This is a structured paragraph for autonomous driving systems.\n\n" * 20)
        official_meta = {**self.source_metadata, "doc_type": "official_doc"}
        standard_meta = {**self.source_metadata, "doc_type": "standard"}
        chunking_config = {
            "official_doc": {"chunk_size": 80, "chunk_overlap": 10},
            "standard": {"chunk_size": 160, "chunk_overlap": 20},
            "paper": {"chunk_size": 120, "chunk_overlap": 15},
            "report": {"chunk_size": 120, "chunk_overlap": 15},
        }
        with (
            mock.patch.object(config, "min_split_length", 10),
            mock.patch.object(config, "doc_type_chunking", chunking_config),
        ):
            official_chunks = chunk_text_doc_type_aware(text, source_metadata=official_meta)
            standard_chunks = chunk_text_doc_type_aware(text, source_metadata=standard_meta)

        self.assertGreater(len(official_chunks), len(standard_chunks))
        self.assertTrue(all(chunk.metadata["chunk_strategy"] == "doc_type_aware" for chunk in official_chunks))
        self.assertTrue(all(chunk.metadata["chunk_strategy"] == "doc_type_aware" for chunk in standard_chunks))

    def test_doc_type_aware_chunking_emits_canonical_locator_and_provenance(self):
        text = "# Intro\n\n[p.2] Alpha paragraph.\n\n## Details\n\n[p.3] Beta paragraph."
        source_metadata = {
            "source": "apollo.md",
            "source_id": "apollo-doc-001",
            "doc_type": "official_doc",
            "create_time": "2026-04-23 10:00:00",
            "operator": "tester",
        }

        chunks = chunk_text_doc_type_aware(text, source_metadata=source_metadata)

        self.assertGreaterEqual(len(chunks), 2)
        first = chunks[0].metadata
        self.assertEqual("apollo.md", first["source"])
        self.assertEqual("apollo-doc-001", first["source_id"])
        self.assertEqual("official_doc", first["doc_type"])
        self.assertEqual("doc_type_aware", first["chunk_strategy"])
        self.assertIn("chunk_order", first)
        self.assertEqual("p.2 | § Intro", first["locator"])

    def test_knowledge_base_service_uses_runtime_embedding_settings(self):
        runtime_config = SimpleNamespace(
            embedding_model_name="text-embedding-v4",
            dashscope_api_key="test-key",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                mock.patch.object(knowledge_base, "load_bailian_runtime_config", return_value=runtime_config),
                mock.patch.object(knowledge_base, "DashScopeEmbeddings", return_value=object()) as mock_embeddings,
                mock.patch.object(knowledge_base, "Chroma", return_value=mock.Mock()),
                mock.patch.object(config, "persist_directory", temp_dir),
            ):
                knowledge_base.KnowledgeBaseService()

        mock_embeddings.assert_called_once_with(
            model="text-embedding-v4",
            dashscope_api_key="test-key",
        )

    def test_upload_by_str_writes_per_chunk_metadata(self):
        mock_chroma = mock.Mock()
        text = "知识库文本。" * 60

        runtime_config = SimpleNamespace(
            embedding_model_name="text-embedding-v4",
            dashscope_api_key="test-key",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                mock.patch.object(knowledge_base, "load_bailian_runtime_config", return_value=runtime_config),
                mock.patch.object(knowledge_base, "Chroma", return_value=mock_chroma),
                mock.patch.object(knowledge_base, "DashScopeEmbeddings", return_value=object()),
                mock.patch.object(knowledge_base, "check_md5", return_value=False),
                mock.patch.object(knowledge_base, "save_md5"),
                mock.patch.object(config, "persist_directory", temp_dir),
                mock.patch.object(config, "chunking_strategy", "doc_type_aware"),
                mock.patch.object(config, "chunk_size", 40),
                mock.patch.object(config, "chunk_overlap", 5),
                mock.patch.object(config, "min_split_length", 10),
            ):
                service = knowledge_base.KnowledgeBaseService()
                result = service.upload_by_str(text, "sample.txt")

        self.assertEqual("【成功】向数据库更新成功", result)
        mock_chroma.add_texts.assert_called_once()
        texts = mock_chroma.add_texts.call_args.kwargs["texts"]
        metadatas = mock_chroma.add_texts.call_args.kwargs["metadatas"]
        self.assertEqual(len(texts), len(metadatas))
        self.assertGreater(len(texts), 1)
        for index, metadata in enumerate(metadatas):
            self.assertEqual("sample.txt", metadata["source"])
            self.assertEqual("upload::sample.txt", metadata["source_id"])
            self.assertEqual("untyped", metadata["doc_type"])
            self.assertEqual(index, metadata["chunk_order"])
            self.assertEqual("baseline", metadata["chunk_strategy"])


if __name__ == "__main__":
    unittest.main()
