import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent.memory import SessionRetrievalMemory, TaskMemoryPolicy, TaskMemoryStore
from agent.tools.rag_search import build_rag_search_tool
from agent.tools.task_memory import build_show_task_memory_tool, build_update_task_memory_tool


class TaskMemoryStoreTests(unittest.TestCase):
    def _store(self, temp_dir: str) -> TaskMemoryStore:
        return TaskMemoryStore(Path(temp_dir) / "task-memory.sqlite3")

    def test_task_memory_persists_across_store_instances(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first_store = self._store(temp_dir)
            first_store.record_retrieval("task-a", "compare BEV methods", ["paper-001", "paper-002"])
            first_store.update_task(
                "task-a",
                topic="BEV method comparison",
                finding="Method A uses temporal features.",
                evidence_gap="No same-hardware latency comparison.",
                open_question="Which method fits the deployment budget?",
                confirmed_source="paper-001",
            )

            snapshot = self._store(temp_dir).get_task("task-a")

        self.assertEqual("BEV method comparison", snapshot.topic)
        self.assertEqual(("compare BEV methods",), snapshot.searched_queries)
        self.assertEqual(("paper-001", "paper-002"), snapshot.retrieved_sources)
        self.assertEqual(("paper-001",), snapshot.confirmed_sources)
        self.assertEqual(("Method A uses temporal features.",), snapshot.findings)
        self.assertEqual(("No same-hardware latency comparison.",), snapshot.evidence_gaps)
        self.assertEqual(("Which method fits the deployment budget?",), snapshot.open_questions)

    def test_task_memory_deduplicates_items_and_isolates_tasks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = self._store(temp_dir)
            store.record_retrieval("task-a", "query", ["paper-001", "paper-001"])
            store.record_retrieval("task-a", "query", ["paper-001"])
            store.record_retrieval("task-b", "other query", ["paper-002"])

            first = store.get_task("task-a")
            second = store.get_task("task-b")

        self.assertEqual(("query",), first.searched_queries)
        self.assertEqual(("paper-001",), first.retrieved_sources)
        self.assertEqual(("other query",), second.searched_queries)
        self.assertEqual(("paper-002",), second.retrieved_sources)

    def test_clear_task_removes_only_selected_task(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = self._store(temp_dir)
            store.update_task("task-a", finding="remove me")
            store.update_task("task-b", finding="keep me")

            store.clear_task("task-a")
            cleared = store.get_task("task-a")
            retained = store.get_task("task-b")

        self.assertTrue(cleared.is_empty)
        self.assertEqual(("keep me",), retained.findings)

    def test_replace_and_remove_item_support_ui_corrections(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = self._store(temp_dir)
            store.update_task(
                "task-a",
                topic="Original topic",
                finding="Original finding",
                evidence_gap="Remove this gap",
            )

            store.set_topic("task-a", "Corrected topic")
            store.replace_item(
                "task-a",
                "finding",
                "Original finding",
                "Corrected finding",
            )
            store.remove_item("task-a", "evidence_gap", "Remove this gap")
            snapshot = store.get_task("task-a")

        self.assertEqual("Corrected topic", snapshot.topic)
        self.assertEqual(("Corrected finding",), snapshot.findings)
        self.assertEqual((), snapshot.evidence_gaps)

    def test_replace_item_requires_non_empty_new_value(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = self._store(temp_dir)
            with self.assertRaises(ValueError):
                store.replace_item("task-a", "finding", "old", "")


class TaskMemoryToolTests(unittest.TestCase):
    def test_update_and_show_tools_share_persistent_task_memory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = TaskMemoryStore(Path(temp_dir) / "task-memory.sqlite3")
            policy = TaskMemoryPolicy(enabled=True)
            update_tool = build_update_task_memory_tool("task-a", store, policy)
            show_tool = build_show_task_memory_tool("task-a", store, policy)

            update_result = update_tool.invoke(
                {
                    "topic": "Camera-radar fusion",
                    "finding": "CRN uses camera and radar.",
                    "evidence_gap": "Deployment latency is unknown.",
                    "open_question": "What hardware was used?",
                    "confirmed_source": "paper-030",
                }
            )
            show_result = show_tool.invoke({})

        self.assertIn("Camera-radar fusion", update_result)
        self.assertIn("CRN uses camera and radar.", show_result)
        self.assertIn("paper-030", show_result)
        self.assertIn("Deployment latency is unknown.", show_result)

    def test_disabled_policy_blocks_reads_and_writes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = TaskMemoryStore(Path(temp_dir) / "task-memory.sqlite3")
            policy = TaskMemoryPolicy(enabled=False)
            update_tool = build_update_task_memory_tool("task-a", store, policy)
            show_tool = build_show_task_memory_tool("task-a", store, policy)

            self.assertIn("已禁用", update_tool.invoke({"finding": "must not persist"}))
            self.assertEqual("当前任务记忆已禁用。", show_tool.invoke({}))
            self.assertTrue(store.get_task("task-a").is_empty)

    def test_rag_search_records_retrieved_but_not_confirmed_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = TaskMemoryStore(Path(temp_dir) / "task-memory.sqlite3")
            policy = TaskMemoryPolicy(enabled=True)
            retrieval_memory = SessionRetrievalMemory()
            rag_service = mock.Mock()
            rag_service.answer_with_retrieval.return_value = {
                "answer": "answer",
                "retrieved_rows": [
                    {"source_id": "paper-030", "locator": "page=1", "content": "evidence"},
                    {"source_id": "paper-030", "locator": "page=2", "content": "more"},
                ],
            }
            rag_tool = build_rag_search_tool(
                "session-a",
                retrieval_memory,
                rag_service=rag_service,
                task_id="task-a",
                task_memory_store=store,
                task_memory_policy=policy,
            )

            rag_tool.invoke({"query": "CRN sensors"})
            snapshot = store.get_task("task-a")

            policy.enabled = False
            rag_tool.invoke({"query": "must not persist"})
            disabled_snapshot = store.get_task("task-a")

        self.assertEqual(("CRN sensors",), snapshot.searched_queries)
        self.assertEqual(("paper-030",), snapshot.retrieved_sources)
        self.assertEqual((), snapshot.confirmed_sources)
        self.assertEqual(("CRN sensors",), disabled_snapshot.searched_queries)


if __name__ == "__main__":
    unittest.main()
