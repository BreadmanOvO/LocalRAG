import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from agent.observability import (
    build_source_observations,
    combine_runtime_observability,
    diff_task_memory,
    finalize_agent_answer,
    has_pending_tool_calls,
    load_latest_agent_eval,
    matches_active_corpus_profile,
)


class SourceObservationTests(unittest.TestCase):
    def test_sources_include_locator_chunk_and_evidence_status(self):
        snapshot = SimpleNamespace(
            documents=(
                {
                    "source_id": "paper-001",
                    "locator": "page=2",
                    "chunk_order": 3,
                    "chunk_strategy": "doc_type_aware",
                    "rank": 1,
                    "score": 0.91,
                    "content": "  multi-line\n evidence  ",
                },
                {
                    "source_id": "paper-002",
                    "locator": "page=4",
                    "chunk_order": 7,
                    "content": "candidate",
                },
            )
        )

        rows = build_source_observations(snapshot, confirmed_sources=("paper-001",))

        self.assertEqual("confirmed", rows[0]["evidence_status"])
        self.assertEqual("retrieved", rows[1]["evidence_status"])
        self.assertEqual("page=2", rows[0]["locator"])
        self.assertEqual(3, rows[0]["chunk_order"])
        self.assertEqual("multi-line evidence", rows[0]["summary"])


class TaskMemoryDiffTests(unittest.TestCase):
    def test_diff_reports_added_and_removed_memory(self):
        before = SimpleNamespace(
            topic="Old topic",
            searched_queries=(),
            retrieved_sources=(),
            confirmed_sources=(),
            findings=("Old finding",),
            evidence_gaps=(),
            open_questions=(),
        )
        after = SimpleNamespace(
            topic="New topic",
            searched_queries=("query",),
            retrieved_sources=("paper-001",),
            confirmed_sources=(),
            findings=("New finding",),
            evidence_gaps=(),
            open_questions=(),
        )

        changes = diff_task_memory(before, after)

        self.assertIn(
            {"action": "removed", "field": "topic", "label": "主题", "value": "Old topic"},
            changes,
        )
        self.assertIn(
            {
                "action": "added",
                "field": "findings",
                "label": "阶段结论",
                "value": "New finding",
            },
            changes,
        )


class RunStatusTests(unittest.TestCase):
    def test_empty_answer_is_a_failed_run(self):
        answer, failed = finalize_agent_answer([], has_error=False)

        self.assertTrue(failed)
        self.assertIn("未生成有效回答", answer)

    def test_unfinished_tool_call_is_pending(self):
        trace = [
            {"kind": "tool_started", "tool_name": "inspect_source", "call_id": "call-1"}
        ]

        self.assertTrue(has_pending_tool_calls(trace))
        self.assertFalse(
            has_pending_tool_calls(
                [
                    *trace,
                    {
                        "kind": "tool_completed",
                        "tool_name": "inspect_source",
                        "call_id": "call-1",
                    },
                ]
            )
        )


class RuntimeObservabilityTests(unittest.TestCase):
    def test_active_profile_checks_counts_and_fingerprints(self):
        current = {
            "corpus_fingerprint": "sha256:corpus",
            "registry_fingerprint": "sha256:registry",
            "chroma_source_count": 100,
            "chunk_count": 7339,
        }

        self.assertTrue(
            matches_active_corpus_profile(
                current,
                expected_corpus_fingerprint="sha256:corpus",
                expected_registry_fingerprint="sha256:registry",
                expected_source_count=100,
                expected_chunk_count=7339,
            )
        )
        self.assertFalse(
            matches_active_corpus_profile(
                current,
                expected_corpus_fingerprint="sha256:corpus",
                expected_registry_fingerprint="sha256:registry",
                expected_source_count=100,
                expected_chunk_count=7338,
            )
        )

    def test_gate_rejects_active_profile_fingerprint_mismatch(self):
        result = combine_runtime_observability(
            current_corpus={
                "available": True,
                "active_profile_matches": False,
                "corpus_fingerprint": "sha256:corpus",
                "registry_fingerprint": "sha256:registry",
            },
            latest_eval={"available": False},
            current_persist_directory="evaluated",
            collection_name="rag",
            project_root="C:/project",
        )

        self.assertEqual("active_profile_mismatch", result["gate_status"])
        self.assertFalse(result["gate_pass"])

    def _write_run(
        self,
        root: Path,
        run_id: str,
        created_at: str,
        corpus_path: str,
        gate: bool,
        *,
        selection_complete: bool = True,
    ):
        run_dir = root / run_id
        run_dir.mkdir()
        (run_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "created_at": created_at,
                    "corpus": {
                        "persist_directory": corpus_path,
                        "collection_name": "rag",
                        "corpus_fingerprint": "sha256:corpus",
                        "registry_fingerprint": "sha256:registry",
                    },
                    "git_revision": "revision-1",
                    "git_dirty": False,
                    "evaluation_scope": {"selection_complete": selection_complete},
                    "runtime": {"provider": "test"},
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "summary.json").write_text(
            json.dumps({"gate_pass": gate}),
            encoding="utf-8",
        )

    def test_latest_eval_uses_manifest_timestamp(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-z", "2026-01-01T00:00:00", "old", False)
            self._write_run(root, "agent-eval-a", "2026-02-01T00:00:00", "new", True)

            latest = load_latest_agent_eval(root)

        self.assertEqual("agent-eval-a", latest["run_id"])
        self.assertTrue(latest["summary"]["gate_pass"])

    def test_latest_eval_ignores_newer_partial_diagnostic_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-formal", "2026-01-01T00:00:00", "full", True)
            self._write_run(
                root,
                "agent-eval-partial",
                "2026-02-01T00:00:00",
                "partial",
                True,
                selection_complete=False,
            )

            latest = load_latest_agent_eval(root)

        self.assertEqual("agent-eval-formal", latest["run_id"])

    def test_gate_only_applies_when_current_corpus_matches(self):
        current = {
            "available": True,
            "coverage_ratio": 0.26,
            "chunk_count": 298,
            "corpus_fingerprint": "sha256:corpus",
            "registry_fingerprint": "sha256:registry",
        }
        latest = {
            "available": True,
            "corpus": {
                "persist_directory": "evaluated",
                "collection_name": "rag",
                "corpus_fingerprint": "sha256:corpus",
                "registry_fingerprint": "sha256:registry",
            },
            "git_revision": "revision-1",
            "git_dirty": False,
            "summary": {"gate_pass": True},
        }

        mismatch = combine_runtime_observability(
            current_corpus=current,
            latest_eval=latest,
            current_persist_directory="current",
            collection_name="rag",
            current_git_revision="revision-1",
            current_git_dirty=False,
            project_root="C:/project",
        )
        matched = combine_runtime_observability(
            current_corpus=current,
            latest_eval=latest,
            current_persist_directory="evaluated",
            collection_name="rag",
            current_git_revision="revision-1",
            current_git_dirty=False,
            project_root="C:/project",
        )

        self.assertEqual("corpus_mismatch", mismatch["gate_status"])
        self.assertFalse(mismatch["gate_pass"])
        self.assertEqual("passed", matched["gate_status"])
        self.assertTrue(matched["gate_pass"])

    def test_gate_rejects_changed_corpus_fingerprint(self):
        current = {
            "available": True,
            "corpus_fingerprint": "sha256:changed",
            "registry_fingerprint": "sha256:registry",
        }
        latest = {
            "available": True,
            "corpus": {
                "persist_directory": "evaluated",
                "collection_name": "rag",
                "corpus_fingerprint": "sha256:evaluated",
                "registry_fingerprint": "sha256:registry",
            },
            "git_revision": "revision-1",
            "git_dirty": False,
            "summary": {"gate_pass": True},
        }

        result = combine_runtime_observability(
            current_corpus=current,
            latest_eval=latest,
            current_persist_directory="evaluated",
            collection_name="rag",
            current_git_revision="revision-1",
            current_git_dirty=False,
            project_root="C:/project",
        )

        self.assertEqual("corpus_mismatch", result["gate_status"])
        self.assertFalse(result["gate_pass"])

    def test_gate_marks_old_artifact_as_legacy(self):
        result = combine_runtime_observability(
            current_corpus={"available": True},
            latest_eval={
                "available": True,
                "corpus": {"persist_directory": "evaluated", "collection_name": "rag"},
                "summary": {"gate_pass": True},
            },
            current_persist_directory="evaluated",
            collection_name="rag",
            current_git_revision="revision-1",
            current_git_dirty=False,
            project_root="C:/project",
        )

        self.assertEqual("legacy_eval", result["gate_status"])
        self.assertFalse(result["gate_pass"])

    def test_gate_rejects_dirty_current_code(self):
        result = combine_runtime_observability(
            current_corpus={
                "available": True,
                "corpus_fingerprint": "sha256:corpus",
                "registry_fingerprint": "sha256:registry",
            },
            latest_eval={
                "available": True,
                "corpus": {
                    "persist_directory": "evaluated",
                    "collection_name": "rag",
                    "corpus_fingerprint": "sha256:corpus",
                    "registry_fingerprint": "sha256:registry",
                },
                "git_revision": "revision-1",
                "git_dirty": False,
                "summary": {"gate_pass": True},
            },
            current_persist_directory="evaluated",
            collection_name="rag",
            current_git_revision="revision-1",
            current_git_dirty=True,
            project_root="C:/project",
        )

        self.assertEqual("code_dirty", result["gate_status"])
        self.assertFalse(result["gate_pass"])

    def test_gate_requires_consecutive_stability_result(self):
        result = combine_runtime_observability(
            current_corpus={
                "available": True,
                "corpus_fingerprint": "sha256:corpus",
                "registry_fingerprint": "sha256:registry",
            },
            latest_eval={
                "available": True,
                "corpus": {
                    "persist_directory": "evaluated",
                    "collection_name": "rag",
                    "corpus_fingerprint": "sha256:corpus",
                    "registry_fingerprint": "sha256:registry",
                },
                "git_revision": "revision-1",
                "git_dirty": False,
                "summary": {"gate_pass": True},
            },
            current_persist_directory="evaluated",
            collection_name="rag",
            current_git_revision="revision-1",
            current_git_dirty=False,
            project_root="C:/project",
            stability_gate={
                "gate_pass": False,
                "failure_reasons": ["identity_consistent"],
            },
        )

        self.assertEqual("stability_gate_failed", result["gate_status"])
        self.assertFalse(result["gate_pass"])
        self.assertEqual(
            ["identity_consistent"],
            result["stability_gate"]["failure_reasons"],
        )


if __name__ == "__main__":
    unittest.main()
