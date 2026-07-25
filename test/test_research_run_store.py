import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from threading import Barrier

from agent.memory import TaskMemoryStore
from agent.research import (
    EvidenceRefDraft,
    ResearchFindingDraft,
    ResearchRevisionConflictError,
    ResearchRunStore,
    ResearchStateError,
    ResearchStepCommit,
    ResearchStepDraft,
    ResearchStepTransition,
)


class ResearchRunStoreTests(unittest.TestCase):
    def _path(self, temp_dir: str) -> Path:
        return Path(temp_dir) / "task-memory.sqlite3"

    def _create_plan(
        self,
        store: ResearchRunStore,
        *,
        task_id: str = "task-a",
        run_id: str = "run-a",
    ):
        return store.create_plan(
            task_id,
            "Compare two perception methods",
            [
                ResearchStepDraft(
                    "Inspect the first source",
                    "inspect_source",
                    {"source_id": "paper-001"},
                ),
                ResearchStepDraft(
                    "Compare the sources",
                    "compare_sources",
                    {"source_ids": ["paper-001", "paper-002"]},
                ),
            ],
            run_id=run_id,
        )

    def test_create_plan_persists_ordered_steps_and_selects_next_pending(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            plan = self._create_plan(ResearchRunStore(path))
            restored = ResearchRunStore(path).get_plan("run-a")
            next_step = ResearchRunStore(path).get_next_pending_step("run-a")

        self.assertEqual("planned", plan.run.status)
        self.assertEqual(0, plan.run.revision)
        self.assertEqual(1, plan.run.plan_revision)
        self.assertEqual([1, 2], [step.position for step in restored.steps])
        self.assertEqual(
            ["inspect_source", "compare_sources"],
            [step.action for step in restored.steps],
        )
        self.assertEqual(restored.steps[0].step_id, next_step.step_id)

    def test_migration_preserves_existing_task_memory_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            task_store = TaskMemoryStore(path)
            task_store.update_task("task-a", finding="legacy finding")

            ResearchRunStore(path)
            ResearchRunStore(path)
            snapshot = TaskMemoryStore(path).get_task("task-a")
            with closing(sqlite3.connect(path)) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    ).fetchall()
                }
                migration_count = connection.execute(
                    "SELECT COUNT(*) FROM agent_schema_migrations WHERE version = 1"
                ).fetchone()[0]

        self.assertEqual(("legacy finding",), snapshot.findings)
        self.assertTrue(
            {
                "tasks",
                "task_memory_items",
                "research_runs",
                "research_steps",
                "research_evidence_refs",
                "research_findings",
                "research_finding_evidence",
                "research_step_usage_events",
            }.issubset(tables)
        )
        self.assertEqual(1, migration_count)

    def test_start_and_commit_step_persist_verified_evidence_binding(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ResearchRunStore(self._path(temp_dir))
            plan = self._create_plan(store)
            started_run, started_step = store.start_next_step(
                plan.run.run_id,
                expected_revision=0,
            )
            evidence = EvidenceRefDraft(
                "paper-001",
                "page=4",
                7,
                "doc_type_aware",
                evidence_id="evidence-a",
            )
            finding = ResearchFindingDraft(
                "Method A uses temporal fusion.",
                status="verified",
                evidence_ids=("evidence-a",),
                finding_id="finding-a",
            )

            committed = store.commit_step(
                plan.run.run_id,
                started_step.step_id,
                ResearchStepCommit(
                    "Source inspected.",
                    evidence_refs=(evidence,),
                    findings=(finding,),
                ),
                expected_revision=started_run.revision,
            )

        self.assertEqual(2, committed.run.revision)
        self.assertIsNone(committed.run.current_step_id)
        self.assertEqual("completed", committed.steps[0].status)
        self.assertEqual(("evidence-a",), committed.steps[0].evidence_ids)
        self.assertEqual("verified", committed.findings[0].status)
        self.assertEqual(("evidence-a",), committed.findings[0].evidence_ids)

    def test_concurrent_usage_checkpoint_replay_counts_once(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            store = ResearchRunStore(path)
            plan = self._create_plan(store)
            _, step = store.start_next_step(
                plan.run.run_id,
                expected_revision=plan.run.revision,
            )

            def record_usage(_):
                return ResearchRunStore(path).record_step_usage(
                    plan.run.run_id,
                    step.step_id,
                    attempt_count=step.attempt_count,
                    event_index=1,
                    event_kind="tool_started",
                )

            with ThreadPoolExecutor(max_workers=4) as executor:
                results = list(executor.map(record_usage, range(4)))
            restored = ResearchRunStore(path).get_plan(plan.run.run_id)

        self.assertTrue(all(result.tool_call_count == 1 for result in results))
        self.assertEqual(1, restored.run.tool_call_count)
        self.assertEqual(0, restored.run.model_call_count)
        self.assertEqual(1, restored.run.revision)

    def test_late_usage_does_not_replace_the_latest_task_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ResearchRunStore(self._path(temp_dir))
            first = self._create_plan(store, run_id="run-a")
            started_run, step = store.start_next_step(
                first.run.run_id,
                expected_revision=first.run.revision,
            )
            store.transition_run(
                first.run.run_id,
                "cancelled",
                expected_revision=started_run.revision,
                stop_reason="research_cancelled",
            )
            second = self._create_plan(store, run_id="run-b")

            store.record_step_usage(
                first.run.run_id,
                step.step_id,
                attempt_count=step.attempt_count,
                event_index=1,
                event_kind="model_completed",
            )
            latest = store.get_latest_plan_for_task("task-a")

        self.assertEqual(second.run.run_id, latest.run.run_id)

    def test_verified_finding_without_valid_evidence_rolls_back_step_commit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ResearchRunStore(self._path(temp_dir))
            plan = self._create_plan(store)
            started_run, started_step = store.start_next_step(
                plan.run.run_id,
                expected_revision=0,
            )

            with self.assertRaisesRegex(ValueError, "evidence"):
                store.commit_step(
                    plan.run.run_id,
                    started_step.step_id,
                    ResearchStepCommit(
                        "must roll back",
                        findings=(
                            ResearchFindingDraft(
                                "Unsupported finding",
                                status="verified",
                                evidence_ids=("missing-evidence",),
                            ),
                        ),
                    ),
                    expected_revision=started_run.revision,
                )
            restored = store.get_plan(plan.run.run_id)

        self.assertEqual(1, restored.run.revision)
        self.assertEqual("running", restored.steps[0].status)
        self.assertEqual((), restored.findings)

    def test_verified_finding_rejects_evidence_from_another_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ResearchRunStore(self._path(temp_dir))
            first = self._create_plan(store, task_id="task-a", run_id="run-a")
            second = self._create_plan(store, task_id="task-b", run_id="run-b")
            first_run, first_step = store.start_next_step(
                first.run.run_id,
                expected_revision=0,
            )
            store.commit_step(
                first.run.run_id,
                first_step.step_id,
                ResearchStepCommit(
                    "first evidence",
                    evidence_refs=(
                        EvidenceRefDraft("paper-001", evidence_id="evidence-a"),
                    ),
                ),
                expected_revision=first_run.revision,
            )
            second_run, second_step = store.start_next_step(
                second.run.run_id,
                expected_revision=0,
            )

            with self.assertRaisesRegex(ValueError, "unknown evidence_ids"):
                store.commit_step(
                    second.run.run_id,
                    second_step.step_id,
                    ResearchStepCommit(
                        "invalid binding",
                        findings=(
                            ResearchFindingDraft(
                                "Cross-run finding",
                                status="verified",
                                evidence_ids=("evidence-a",),
                            ),
                        ),
                    ),
                    expected_revision=second_run.revision,
                )
            restored = store.get_run("run-b")

        self.assertEqual(1, restored.revision)

    def test_run_and_step_state_machines_reject_illegal_transitions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ResearchRunStore(self._path(temp_dir))
            self._create_plan(store)

            with self.assertRaisesRegex(ResearchStateError, "planned -> completed"):
                store.transition_run("run-a", "completed", expected_revision=0)

            started_run, started_step = store.start_next_step(
                "run-a",
                expected_revision=0,
            )
            blocked = store.transition_step(
                "run-a",
                started_step.step_id,
                ResearchStepTransition("blocked", error_code="evidence_missing"),
                expected_revision=started_run.revision,
            )
            with self.assertRaisesRegex(ResearchStateError, "blocked -> running"):
                store.transition_step(
                    "run-a",
                    started_step.step_id,
                    ResearchStepTransition("running"),
                    expected_revision=blocked.run.revision,
                )
            with self.assertRaisesRegex(ResearchStateError, "run is blocked"):
                store.transition_step(
                    "run-a",
                    blocked.steps[1].step_id,
                    ResearchStepTransition("running"),
                    expected_revision=blocked.run.revision,
                )

        self.assertEqual("blocked", blocked.run.status)
        self.assertEqual("evidence_missing", blocked.run.stop_reason)

    def test_run_completes_only_after_all_steps_are_terminal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ResearchRunStore(self._path(temp_dir))
            plan = self._create_plan(store)
            first_run, first_step = store.start_next_step("run-a", expected_revision=0)
            plan = store.commit_step(
                "run-a",
                first_step.step_id,
                ResearchStepCommit("done"),
                expected_revision=first_run.revision,
            )
            plan = store.transition_step(
                "run-a",
                plan.steps[1].step_id,
                ResearchStepTransition("skipped", result_summary="not needed"),
                expected_revision=plan.run.revision,
            )
            completed = store.transition_run(
                "run-a",
                "completed",
                expected_revision=plan.run.revision,
            )

        self.assertEqual("completed", completed.status)
        self.assertEqual(4, completed.revision)

    def test_finding_transition_requires_bound_evidence_for_verified_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ResearchRunStore(self._path(temp_dir))
            plan = self._create_plan(store)
            started_run, step = store.start_next_step("run-a", expected_revision=0)
            plan = store.commit_step(
                "run-a",
                step.step_id,
                ResearchStepCommit(
                    "candidate saved",
                    evidence_refs=(
                        EvidenceRefDraft(
                            "paper-001",
                            evidence_id="evidence-a",
                        ),
                    ),
                    findings=(
                        ResearchFindingDraft(
                            "Candidate finding",
                            finding_id="finding-a",
                        ),
                    ),
                ),
                expected_revision=started_run.revision,
            )
            with self.assertRaisesRegex(ValueError, "evidence"):
                store.transition_finding(
                    "run-a",
                    "finding-a",
                    "verified",
                    expected_revision=plan.run.revision,
                )
            verified = store.transition_finding(
                "run-a",
                "finding-a",
                "verified",
                expected_revision=plan.run.revision,
                evidence_ids=["evidence-a"],
            )

        self.assertEqual("verified", verified.status)
        self.assertEqual(("evidence-a",), verified.evidence_ids)

    def test_optimistic_lock_allows_one_concurrent_update(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            self._create_plan(ResearchRunStore(path))
            barrier = Barrier(2)

            def update(status: str) -> str:
                store = ResearchRunStore(path)
                barrier.wait()
                try:
                    store.transition_run(
                        "run-a",
                        status,
                        expected_revision=0,
                        stop_reason="concurrent update",
                    )
                    return "updated"
                except ResearchRevisionConflictError:
                    return "conflict"

            with ThreadPoolExecutor(max_workers=2) as executor:
                outcomes = list(executor.map(update, ("running", "cancelled")))
            restored = ResearchRunStore(path).get_run("run-a")

        self.assertEqual(["conflict", "updated"], sorted(outcomes))
        self.assertEqual(1, restored.revision)

    def test_clearing_task_cascades_research_state_only_for_that_task(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            store = ResearchRunStore(path)
            first = self._create_plan(store, task_id="task-a", run_id="run-a")
            self._create_plan(store, task_id="task-b", run_id="run-b")
            first_run, first_step = store.start_next_step(
                first.run.run_id,
                expected_revision=0,
            )
            store.commit_step(
                first.run.run_id,
                first_step.step_id,
                ResearchStepCommit(
                    "verified result",
                    evidence_refs=(
                        EvidenceRefDraft("paper-001", evidence_id="evidence-a"),
                    ),
                    findings=(
                        ResearchFindingDraft(
                            "Verified finding",
                            status="verified",
                            evidence_ids=("evidence-a",),
                        ),
                    ),
                ),
                expected_revision=first_run.revision,
            )

            TaskMemoryStore(path).clear_task("task-a")

            with self.assertRaisesRegex(LookupError, "run-a"):
                store.get_run("run-a")
            retained = store.get_run("run-b")
            with closing(sqlite3.connect(path)) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
                foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()

        self.assertEqual("task-b", retained.task_id)
        self.assertEqual([], foreign_key_errors)


if __name__ == "__main__":
    unittest.main()
