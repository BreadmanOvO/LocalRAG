import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from agent.observability import AgentEvent
from agent.research import (
    ResearchAgentRuntime,
    ResearchControlError,
    ResearchExecutionIdentity,
    ResearchRunService,
    ResearchRunStore,
    build_evidence_rows,
    build_finding_rows,
    build_step_rows,
    execution_identity_from_observability,
    is_active_plan,
    research_progress,
    run_status_label,
)


class FakeResearchAgent:
    def __init__(self, event_runs, *, documents=()) -> None:
        self.task_id = "task-a"
        self.event_runs = list(event_runs)
        self.documents = tuple(documents)
        self.queries = []
        self.execute_count = 0
        self.execution_budget = SimpleNamespace(
            tool_call_limit=3,
            model_call_limit=4,
        )

    def execute_events(self, query: str):
        self.execute_count += 1
        self.queries.append(query)
        for event in self.event_runs.pop(0):
            yield event

    def get_retrieval_snapshot(self):
        return SimpleNamespace(documents=self.documents)


class ResearchAgentRuntimeTests(unittest.TestCase):
    @staticmethod
    def _path(temp_dir: str) -> Path:
        return Path(temp_dir) / "task-memory.sqlite3"

    @staticmethod
    def _identity(*, revision: str = "revision-a") -> ResearchExecutionIdentity:
        return ResearchExecutionIdentity(
            corpus_fingerprint="sha256:corpus-a",
            registry_fingerprint="sha256:registry-a",
            code_revision=revision,
            code_dirty=False,
        )

    def _runtime(self, path: Path, agent: FakeResearchAgent, *, identity=None):
        service = ResearchRunService(ResearchRunStore(path))
        runtime = ResearchAgentRuntime(
            agent,
            service,
            identity or self._identity(),
        )
        return runtime, service

    def test_observability_identity_requires_complete_runtime_state(self):
        identity = execution_identity_from_observability(
            {
                "current_corpus": {
                    "available": True,
                    "corpus_fingerprint": "sha256:corpus-a",
                    "registry_fingerprint": "sha256:registry-a",
                },
                "current_git_revision": "revision-a",
                "current_git_dirty": False,
            }
        )
        with self.assertRaises(ResearchControlError) as raised:
            execution_identity_from_observability(
                {
                    "current_corpus": {"available": False},
                    "current_git_revision": "",
                    "current_git_dirty": None,
                }
            )

        self.assertEqual(self._identity(), identity)
        self.assertEqual("research_identity_unavailable", raised.exception.error_code)

    def test_refresh_reuses_the_same_active_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            runtime, _ = self._runtime(path, FakeResearchAgent([()]))
            first = runtime.create_run("Compare methods")
            repeated = ResearchAgentRuntime(
                runtime.agent,
                ResearchRunService(ResearchRunStore(path)),
                self._identity(),
            ).create_run("Compare methods")
            with self.assertRaises(ResearchControlError) as raised:
                runtime.create_run("A different question")
            with closing(sqlite3.connect(path)) as connection:
                run_count = connection.execute(
                    "SELECT COUNT(*) FROM research_runs"
                ).fetchone()[0]
            runtime.pause_run(
                first.run.run_id,
                expected_revision=first.run.revision,
            )
            paused = runtime.get_latest_plan()

        self.assertEqual(first.run.run_id, repeated.run.run_id)
        self.assertEqual(1, run_count)
        self.assertEqual("research_run_active", raised.exception.error_code)
        self.assertEqual("已暂停", run_status_label(paused))

    def test_successful_turn_commits_evidence_finding_and_budgets(self):
        events = (
            AgentEvent(kind="model_completed", status="completed"),
            AgentEvent(kind="tool_started", tool_name="inspect_source"),
            AgentEvent(
                kind="tool_completed",
                tool_name="inspect_source",
                observations=(
                    {
                        "source_id": "paper-001",
                        "locator": "page=4",
                        "chunk_order": 7,
                        "chunk_strategy": "doc_type_aware",
                    },
                ),
            ),
            AgentEvent(kind="model_completed", status="completed"),
            AgentEvent(kind="answer_delta", content="Grounded answer"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            agent = FakeResearchAgent([events])
            runtime, _ = self._runtime(path, agent)
            plan = runtime.create_run("Compare methods")
            output = list(runtime.execute_events(plan.run.run_id))
            restored = runtime.get_latest_plan()

        self.assertEqual(list(events), output)
        self.assertEqual("completed", restored.run.status)
        self.assertEqual(1, restored.run.tool_call_count)
        self.assertEqual(2, restored.run.model_call_count)
        self.assertEqual("completed", restored.steps[0].status)
        self.assertEqual(1, restored.steps[0].attempt_count)
        self.assertEqual(1, len(restored.evidence_refs))
        self.assertEqual("verified", restored.findings[0].status)
        self.assertEqual(restored.evidence_refs[0].evidence_id, restored.findings[0].evidence_ids[0])
        self.assertFalse(is_active_plan(restored))
        self.assertEqual(1.0, research_progress(restored))
        self.assertEqual("完成", build_step_rows(restored)[0]["状态"])
        self.assertEqual("paper-001", build_evidence_rows(restored)[0]["来源"])
        self.assertIn("paper-001", build_finding_rows(restored)[0]["证据"])

    def test_blocked_attempt_resumes_without_losing_usage_counts(self):
        failed_events = (
            AgentEvent(kind="model_completed", status="completed"),
            AgentEvent(kind="tool_started", tool_name="rag_search"),
            AgentEvent(
                kind="error",
                content="failed",
                status="error",
                error_code="model_request_failed",
            ),
        )
        successful_events = (
            AgentEvent(kind="model_completed", status="completed"),
            AgentEvent(kind="answer_delta", content="Recovered answer"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            agent = FakeResearchAgent([failed_events, successful_events])
            runtime, _ = self._runtime(path, agent)
            created = runtime.create_run("Recover this task")

            list(runtime.execute_events(created.run.run_id))
            blocked = runtime.get_latest_plan()
            list(runtime.execute_events(created.run.run_id))
            completed = runtime.get_latest_plan()

        self.assertEqual("blocked", blocked.run.status)
        self.assertEqual("受阻", run_status_label(blocked))
        self.assertEqual("model_request_failed", blocked.run.stop_reason)
        self.assertEqual(1, blocked.run.tool_call_count)
        self.assertEqual(1, blocked.run.model_call_count)
        self.assertEqual("completed", completed.run.status)
        self.assertEqual(1, completed.run.tool_call_count)
        self.assertEqual(2, completed.run.model_call_count)
        self.assertEqual(2, completed.steps[0].attempt_count)

    def test_failed_rag_search_never_commits_a_later_unsupported_answer(self):
        events = (
            AgentEvent(kind="model_completed", status="completed"),
            AgentEvent(kind="tool_started", tool_name="rag_search"),
            AgentEvent(
                kind="tool_completed",
                tool_name="rag_search",
                status="error",
                error_code="rag_search_failed",
            ),
            AgentEvent(kind="answer_delta", content="Unsupported answer"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime, _ = self._runtime(
                self._path(temp_dir),
                FakeResearchAgent([events]),
            )
            plan = runtime.create_run("Retrieve before answering")

            output = list(runtime.execute_events(plan.run.run_id))
            restored = runtime.get_latest_plan()

        self.assertEqual(list(events), output)
        self.assertEqual("blocked", restored.run.status)
        self.assertEqual("rag_search_failed", restored.run.stop_reason)
        self.assertEqual("blocked", restored.steps[0].status)
        self.assertEqual((), restored.evidence_refs)
        self.assertEqual((), restored.findings)

    def test_pause_after_model_event_preserves_partial_usage(self):
        events = (
            AgentEvent(kind="model_completed", status="completed"),
            AgentEvent(kind="answer_delta", content="Too late"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime, service = self._runtime(
                self._path(temp_dir),
                FakeResearchAgent([events]),
            )
            created = runtime.create_run("Pause after the model call")
            execution = runtime.execute_events(created.run.run_id)

            self.assertEqual(events[0], next(execution))
            active = service.get_plan(created.run.run_id)
            service.pause_run(
                created.run.run_id,
                expected_revision=active.run.revision,
            )
            stopped = next(execution)
            restored = service.get_plan(created.run.run_id)

        self.assertEqual("research_paused", stopped.error_code)
        self.assertEqual("blocked", restored.run.status)
        self.assertEqual(0, restored.run.tool_call_count)
        self.assertEqual(1, restored.run.model_call_count)

    def test_cancel_after_tool_event_preserves_partial_usage(self):
        events = (
            AgentEvent(kind="model_completed", status="completed"),
            AgentEvent(kind="tool_started", tool_name="rag_search"),
            AgentEvent(kind="tool_completed", tool_name="rag_search"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime, service = self._runtime(
                self._path(temp_dir),
                FakeResearchAgent([events]),
            )
            created = runtime.create_run("Cancel after the tool call")
            execution = runtime.execute_events(created.run.run_id)

            self.assertEqual(events[0], next(execution))
            self.assertEqual(events[1], next(execution))
            active = service.get_plan(created.run.run_id)
            service.cancel_run(
                created.run.run_id,
                expected_revision=active.run.revision,
            )
            stopped = next(execution)
            restored = service.get_plan(created.run.run_id)

        self.assertEqual("research_cancelled", stopped.error_code)
        self.assertEqual("cancelled", restored.run.status)
        self.assertEqual(1, restored.run.tool_call_count)
        self.assertEqual(1, restored.run.model_call_count)

    def test_repeated_evidence_is_scoped_to_each_run(self):
        events = (
            AgentEvent(kind="model_completed", status="completed"),
            AgentEvent(
                kind="tool_completed",
                tool_name="inspect_source",
                observations=(
                    {
                        "source_id": "paper-001",
                        "locator": "page=4",
                        "chunk_order": 7,
                        "chunk_strategy": "doc_type_aware",
                    },
                ),
            ),
            AgentEvent(kind="answer_delta", content="Same grounded answer"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime, service = self._runtime(
                self._path(temp_dir),
                FakeResearchAgent([events, events]),
            )
            first = runtime.create_run("First question")
            list(runtime.execute_events(first.run.run_id))
            first_result = service.get_plan(first.run.run_id)
            second = runtime.create_run("Second question")
            list(runtime.execute_events(second.run.run_id))
            second_result = service.get_plan(second.run.run_id)

        self.assertEqual("completed", second_result.run.status)
        self.assertNotEqual(
            first_result.evidence_refs[0].evidence_id,
            second_result.evidence_refs[0].evidence_id,
        )
        self.assertNotEqual(
            first_result.findings[0].finding_id,
            second_result.findings[0].finding_id,
        )

    def test_answer_without_current_evidence_does_not_reuse_old_snapshot(self):
        documents = (
            {
                "source_id": "paper-001",
                "locator": "page=4",
                "chunk_order": 7,
                "chunk_strategy": "doc_type_aware",
            },
        )
        events = (
            AgentEvent(kind="model_completed", status="completed"),
            AgentEvent(kind="answer_delta", content="Ungrounded answer"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime, _ = self._runtime(
                self._path(temp_dir),
                FakeResearchAgent([events], documents=documents),
            )
            plan = runtime.create_run("Do not reuse stale evidence")
            list(runtime.execute_events(plan.run.run_id))
            restored = runtime.get_latest_plan()

        self.assertEqual((), restored.evidence_refs)
        self.assertEqual("candidate", restored.findings[0].status)

    def test_cancelled_claim_is_checked_before_agent_advances(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            agent = FakeResearchAgent(
                [[AgentEvent(kind="model_completed", status="completed")]]
            )
            runtime, service = self._runtime(path, agent)
            created = runtime.create_run("Cancel this task")
            wrapped_service = mock.Mock(wraps=service)

            def cancel_before_advance(run_id, step_id, *, expected_revision):
                run = service.store.get_run(run_id)
                service.cancel_run(run_id, expected_revision=run.revision)
                return service.ensure_step_active(
                    run_id,
                    step_id,
                    expected_revision=expected_revision,
                )

            wrapped_service.ensure_step_active.side_effect = cancel_before_advance
            runtime.service = wrapped_service
            output = list(runtime.execute_events(created.run.run_id))
            restored = service.get_plan(created.run.run_id)

        self.assertEqual(0, agent.execute_count)
        self.assertEqual("research_cancelled", output[0].error_code)
        self.assertEqual("cancelled", restored.run.status)

    def test_replaced_claim_stops_the_old_executor_before_agent_advances(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            agent = FakeResearchAgent(
                [[AgentEvent(kind="model_completed", status="completed")]]
            )
            runtime, service = self._runtime(path, agent)
            created = runtime.create_run("Replace this claim")
            wrapped_service = mock.Mock(wraps=service)

            def replace_before_advance(run_id, step_id, *, expected_revision):
                service.store.prepare_resume(
                    run_id,
                    expected_revision=expected_revision,
                )
                replacement = service.store.start_next_step(
                    run_id,
                    expected_revision=expected_revision + 1,
                )
                self.assertIsNotNone(replacement)
                return service.ensure_step_active(
                    run_id,
                    step_id,
                    expected_revision=expected_revision,
                )

            wrapped_service.ensure_step_active.side_effect = replace_before_advance
            runtime.service = wrapped_service
            output = list(runtime.execute_events(created.run.run_id))

        self.assertEqual(0, agent.execute_count)
        self.assertEqual("research_revision_changed", output[0].error_code)

    def test_planned_run_revalidates_identity_before_claim(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            agent = FakeResearchAgent([()])
            runtime, service = self._runtime(path, agent)
            created = runtime.create_run("Do not reuse stale identity")
            changed = ResearchAgentRuntime(
                agent,
                service,
                self._identity(revision="revision-b"),
            )

            output = list(changed.execute_events(created.run.run_id))
            restored = service.get_plan(created.run.run_id)

        self.assertEqual("research_identity_mismatch", output[0].error_code)
        self.assertEqual(0, agent.execute_count)
        self.assertEqual("planned", restored.run.status)
        self.assertEqual(0, restored.run.revision)


if __name__ == "__main__":
    unittest.main()
