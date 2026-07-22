import unittest
from unittest import mock

from pydantic import ValidationError

from agent.memory import SessionRetrievalMemory
from agent.tools.research import (
    build_compare_sources_tool,
    build_evidence_check_tool,
    build_expand_context_tool,
    build_inspect_source_tool,
)
from core.source_evidence import SourceEvidenceService


class FakeCollection:
    def __init__(self, rows):
        self.rows = list(rows)

    def get(self, *, where, include):
        source_id = where["source_id"]
        matched = [row for row in self.rows if row["metadata"]["source_id"] == source_id]
        return {
            "ids": [row["id"] for row in matched],
            "documents": [row["content"] for row in matched],
            "metadatas": [row["metadata"] for row in matched],
        }


REGISTRY = [
    {
        "source_id": "paper-001",
        "title": "Camera Radar Study",
        "doc_type": "paper",
        "language": "en",
        "version": "v1",
        "origin_url": "https://example.test/paper-001",
    },
    {
        "source_id": "paper-002",
        "title": "Camera Lidar Study",
        "doc_type": "paper",
        "language": "en",
        "version": "v2",
        "origin_url": "https://example.test/paper-002",
    },
]


ROWS = [
    {
        "id": "p1-2",
        "content": "CRN combines camera features with radar measurements for robust detection.",
        "metadata": {
            "source_id": "paper-001",
            "chunk_order": 2,
            "locator": "page=3",
            "chunk_strategy": "semantic",
        },
    },
    {
        "id": "p1-0",
        "content": "This paper introduces a multi-sensor perception architecture.",
        "metadata": {
            "source_id": "paper-001",
            "chunk_order": 0,
            "locator": "page=1",
            "chunk_strategy": "semantic",
        },
    },
    {
        "id": "p1-1",
        "content": "The camera branch extracts image features before fusion.",
        "metadata": {
            "source_id": "paper-001",
            "chunk_order": 1,
            "locator": "page=2",
            "chunk_strategy": "semantic",
        },
    },
    {
        "id": "p2-0",
        "content": "The baseline combines camera images with lidar point clouds.",
        "metadata": {
            "source_id": "paper-002",
            "chunk_order": 0,
            "locator": "page=1",
            "chunk_strategy": "semantic",
        },
    },
    {
        "id": "p2-1",
        "content": "Latency was measured on an RTX platform.",
        "metadata": {
            "source_id": "paper-002",
            "chunk_order": 1,
            "locator": "page=4",
            "chunk_strategy": "semantic",
        },
    },
]


class SourceEvidenceServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = SourceEvidenceService(
            registry_entries=REGISTRY,
            collection=FakeCollection(ROWS),
        )

    def test_inspect_source_combines_registry_and_sorted_chunks(self):
        result = self.service.inspect_source("paper-001", max_chunks=2)

        self.assertTrue(result["found"])
        self.assertEqual("Camera Radar Study", result["source"]["title"])
        self.assertEqual(3, result["chunk_count"])
        self.assertEqual([0, 1], [chunk["chunk_order"] for chunk in result["chunks"]])

    def test_expand_context_returns_bounded_adjacent_window(self):
        result = self.service.expand_context(
            "paper-001",
            1,
            before=1,
            after=1,
            chunk_strategy="semantic",
        )

        self.assertTrue(result["found"])
        self.assertEqual([0, 1, 2], [chunk["chunk_order"] for chunk in result["chunks"]])

    def test_expand_context_reports_available_orders_for_missing_target(self):
        result = self.service.expand_context("paper-001", 9)

        self.assertFalse(result["found"])
        self.assertEqual([0, 1, 2], result["available_chunk_orders"])

    def test_compare_sources_uses_same_focus_to_rank_excerpts(self):
        result = self.service.compare_sources(
            ["paper-001", "paper-002"],
            focus="camera radar fusion",
            max_chunks_per_source=1,
        )

        self.assertEqual("paper-001", result["sources"][0]["source"]["source_id"])
        self.assertEqual(2, result["sources"][0]["chunks"][0]["chunk_order"])
        self.assertEqual(0, result["sources"][1]["chunks"][0]["chunk_order"])

    def test_check_evidence_filters_sources_and_returns_candidates_not_verdicts(self):
        documents = [
            {
                "source_id": "paper-001",
                "chunk_order": 2,
                "locator": "page=3",
                "content": ROWS[0]["content"],
            },
            {
                "source_id": "paper-002",
                "chunk_order": 1,
                "locator": "page=4",
                "content": ROWS[4]["content"],
            },
        ]

        result = self.service.check_evidence(
            "CRN combines camera and radar",
            documents,
            source_ids=["paper-001"],
        )

        self.assertEqual("candidate_found", result["status"])
        self.assertEqual(1, result["searched_document_count"])
        self.assertEqual("paper-001", result["candidates"][0]["source_id"])


class ResearchToolTests(unittest.TestCase):
    def setUp(self):
        self.service = SourceEvidenceService(
            registry_entries=REGISTRY,
            collection=FakeCollection(ROWS),
        )

    def test_source_tools_expose_traceable_metadata(self):
        inspect_tool = build_inspect_source_tool(self.service)
        expand_tool = build_expand_context_tool(self.service)
        compare_tool = build_compare_sources_tool(self.service)

        inspected = inspect_tool.invoke({"source_id": "paper-001", "max_chunks": 1})
        expanded = expand_tool.invoke({"source_id": "paper-001", "chunk_order": 1})
        compared = compare_tool.invoke(
            {
                "source_ids": ["paper-001", "paper-002"],
                "focus": "camera radar",
                "max_chunks_per_source": 1,
            }
        )

        self.assertIn("Camera Radar Study", inspected)
        self.assertIn("chunk_order=0", inspected)
        self.assertIn("target_chunk_order: 1", expanded)
        self.assertIn("paper-002", compared)
        self.assertIn("term_coverage", compared)

    def test_research_tool_schemas_expose_service_bounds(self):
        inspect_tool = build_inspect_source_tool(self.service)
        expand_tool = build_expand_context_tool(self.service)
        compare_tool = build_compare_sources_tool(self.service)

        self.assertEqual(5, inspect_tool.args["max_chunks"]["maximum"])
        self.assertEqual(3, expand_tool.args["after"]["maximum"])
        self.assertEqual(2, compare_tool.args["source_ids"]["minItems"])
        self.assertEqual(5, compare_tool.args["source_ids"]["maxItems"])

    def test_evidence_check_is_bound_to_one_retrieval_session(self):
        memory = SessionRetrievalMemory()
        memory.remember(
            "session-a",
            "CRN sensors",
            [
                {
                    "source_id": "paper-001",
                    "chunk_order": 2,
                    "locator": "page=3",
                    "content": ROWS[0]["content"],
                }
            ],
        )
        tool_a = build_evidence_check_tool("session-a", memory, self.service)
        tool_b = build_evidence_check_tool("session-b", memory, self.service)

        self.assertIn(
            "candidate_found",
            tool_a.invoke({"claim": "CRN combines camera and radar"}),
        )
        self.assertIn("请先检索", tool_b.invoke({"claim": "CRN combines camera and radar"}))

    def test_compare_tool_rejects_a_single_source(self):
        compare_tool = build_compare_sources_tool(self.service)

        with self.assertRaises(ValidationError):
            compare_tool.invoke({"source_ids": ["paper-001"]})

    def test_research_tools_return_source_observation_artifacts(self):
        calls = [
            (
                build_inspect_source_tool(self.service),
                "inspect_source",
                {"source_id": "paper-001", "max_chunks": 1},
            ),
            (
                build_expand_context_tool(self.service),
                "expand_context",
                {"source_id": "paper-001", "chunk_order": 1},
            ),
            (
                build_compare_sources_tool(self.service),
                "compare_sources",
                {
                    "source_ids": ["paper-001", "paper-002"],
                    "focus": "camera radar",
                    "max_chunks_per_source": 1,
                },
            ),
        ]

        for index, (research_tool, name, args) in enumerate(calls):
            with self.subTest(tool=name):
                message = research_tool.invoke(
                    {"type": "tool_call", "id": f"call-{index}", "name": name, "args": args}
                )
                observations = message.artifact["source_observations"]
                self.assertEqual("success", message.status)
                self.assertTrue(observations)
                self.assertIn("source_id", observations[0])
                self.assertIn("locator", observations[0])
                self.assertIn("chunk_order", observations[0])
                self.assertIn("chunk_strategy", observations[0])
                self.assertIn("summary", observations[0])
                self.assertIn("evidence_status", observations[0])

    def test_tool_exception_becomes_safe_failed_tool_message(self):
        compare_tool = build_compare_sources_tool(self.service)

        with mock.patch.object(
            self.service,
            "compare_sources",
            side_effect=RuntimeError("private service details"),
        ):
            message = compare_tool.invoke(
                {
                    "type": "tool_call",
                    "id": "call-failed",
                    "name": "compare_sources",
                    "args": {"source_ids": ["paper-001", "paper-002"]},
                }
            )

        self.assertEqual("error", message.status)
        self.assertIn("来源对比失败", message.content)
        self.assertNotIn("private service details", message.content)


if __name__ == "__main__":
    unittest.main()
