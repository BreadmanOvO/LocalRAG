import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from agent.research import (
    EvidenceRefDraft,
    ResearchControlError,
    ResearchExecutionIdentity,
    ResearchFindingDraft,
    ResearchRunService,
    ResearchRunStore,
    ResearchStateError,
    ResearchStepCommit,
    ResearchStepDraft,
    ResearchStepTransition,
)


class ResearchRunControlTests(unittest.TestCase):
    @staticmethod
    def _path(temp_dir: str) -> Path:
        return Path(temp_dir) / "task-memory.sqlite3"

    @staticmethod
    def _identity(
        *,
        corpus: str = "sha256:corpus-a",
        revision: str = "revision-a",
        dirty: bool = False,
    ) -> ResearchExecutionIdentity:
        return ResearchExecutionIdentity(
            corpus_fingerprint=corpus,
            registry_fingerprint="sha256:registry-a",
            code_revision=revision,
            code_dirty=dirty,
        )

    def _create_plan(self, path: Path):
        service = ResearchRunService(ResearchRunStore(path))
        plan = service.create_plan(
            "task-a",
            "Compare two perception methods",
            (
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
            ),
            identity=self._identity(),
            run_id="run-a",
        )
        return service, plan

    def test_a3_migration_and_execution_identity_are_persistent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            _, plan = self._create_plan(path)
            restored_identity = ResearchRunStore(path).get_identity(plan.run.run_id)
            with closing(sqlite3.connect(path)) as connection:
                migrations = connection.execute(
                    "SELECT version, name FROM agent_schema_migrations ORDER BY version"
                ).fetchall()
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    ).fetchall()
                }

        self.assertEqual(self._identity(), restored_identity)
        self.assertEqual(
            [
                (1, "v1.5-a2-research-state"),
                (2, "v1.5-a3-research-recovery"),
            ],
            migrations,
        )
        self.assertIn("research_run_identities", tables)
        self.assertIn("research_step_commits", tables)

    def test_a2_review_rejects_incomplete_direct_resume(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ResearchRunStore(self._path(temp_dir))
            store.create_plan(
                "task-a",
                "Inspect a source",
                (ResearchStepDraft("Inspect", "inspect_source"),),
                run_id="run-a",
            )
            started_run, step = store.start_next_step("run-a", expected_revision=0)
            blocked = store.transition_step(
                "run-a",
                step.step_id,
                ResearchStepTransition("blocked", error_code="evidence_missing"),
                expected_revision=started_run.revision,
            )

            with self.assertRaisesRegex(ResearchStateError, "blocked -> running"):
                store.transition_run(
                    "run-a",
                    "running",
                    expected_revision=blocked.run.revision,
                )
            restored = store.get_plan("run-a")

        self.assertEqual("blocked", restored.run.status)
        self.assertEqual("blocked", restored.steps[0].status)

    def test_a2_review_rejects_duplicate_finding_evidence_ids_before_write(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ResearchRunStore(self._path(temp_dir))
            store.create_plan(
                "task-a",
                "Inspect a source",
                (ResearchStepDraft("Inspect", "inspect_source"),),
                run_id="run-a",
            )
            started_run, step = store.start_next_step("run-a", expected_revision=0)
            with self.assertRaisesRegex(ValueError, "must be unique"):
                store.commit_step(
                    "run-a",
                    step.step_id,
                    ResearchStepCommit(
                        "invalid duplicate binding",
                        evidence_refs=(
                            EvidenceRefDraft("paper-001", evidence_id="evidence-a"),
                        ),
                        findings=(
                            ResearchFindingDraft(
                                "Duplicate evidence",
                                status="verified",
                                evidence_ids=("evidence-a", "evidence-a"),
                            ),
                        ),
                    ),
                    expected_revision=started_run.revision,
                )
            restored = store.get_plan("run-a")

        self.assertEqual(1, restored.run.revision)
        self.assertEqual("running", restored.steps[0].status)
        self.assertEqual((), restored.evidence_refs)

    def test_pause_and_restart_resume_retry_the_interrupted_step(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            service, plan = self._create_plan(path)
            started_run, first_step = service.claim_next_step(
                "run-a",
                expected_revision=plan.run.revision,
            )
            paused = service.pause_run(
                "run-a",
                expected_revision=started_run.revision,
            )

            restarted = ResearchRunService(ResearchRunStore(path))
            resumed = restarted.resume_run(
                "run-a",
                expected_revision=paused.revision,
                current_identity=self._identity(),
            )
            retried_run, retried_step = restarted.claim_next_step(
                "run-a",
                expected_revision=resumed.run.revision,
            )

        self.assertEqual("running", resumed.run.status)
        self.assertEqual("pending", resumed.steps[0].status)
        self.assertEqual(1, resumed.steps[0].attempt_count)
        self.assertEqual(first_step.step_id, retried_step.step_id)
        self.assertEqual(2, retried_step.attempt_count)
        self.assertEqual(4, retried_run.revision)

    def test_restart_recovers_a_running_step_without_an_explicit_pause(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            service, plan = self._create_plan(path)
            started_run, first_step = service.claim_next_step(
                "run-a",
                expected_revision=plan.run.revision,
            )

            restarted = ResearchRunService(ResearchRunStore(path))
            recovered = restarted.resume_run(
                "run-a",
                expected_revision=started_run.revision,
                current_identity=self._identity(),
            )
            retried_run, retried_step = restarted.claim_next_step(
                "run-a",
                expected_revision=recovered.run.revision,
            )

        self.assertEqual("pending", recovered.steps[0].status)
        self.assertIsNone(recovered.run.current_step_id)
        self.assertEqual(first_step.step_id, retried_step.step_id)
        self.assertEqual(2, retried_step.attempt_count)
        self.assertEqual(3, retried_run.revision)

    def test_restart_at_completed_step_boundary_does_not_replay_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            service, plan = self._create_plan(path)
            started_run, first_step = service.claim_next_step(
                "run-a",
                expected_revision=plan.run.revision,
            )
            committed = service.commit_step(
                "run-a",
                first_step.step_id,
                ResearchStepCommit("first complete", commit_id="commit-first"),
                expected_revision=started_run.revision,
            )

            restarted = ResearchRunService(ResearchRunStore(path))
            resumed = restarted.resume_run(
                "run-a",
                expected_revision=committed.run.revision,
                current_identity=self._identity(),
            )
            next_run, next_step = restarted.claim_next_step(
                "run-a",
                expected_revision=resumed.run.revision,
            )

        self.assertEqual(committed.run.revision, resumed.run.revision)
        self.assertEqual("completed", resumed.steps[0].status)
        self.assertEqual(2, next_step.position)
        self.assertEqual(3, next_run.revision)

    def test_repeated_step_commit_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            service, plan = self._create_plan(path)
            started_run, step = service.claim_next_step(
                "run-a",
                expected_revision=plan.run.revision,
            )
            commit = ResearchStepCommit(
                "source inspected",
                evidence_refs=(
                    EvidenceRefDraft("paper-001", evidence_id="evidence-a"),
                ),
                findings=(
                    ResearchFindingDraft(
                        "Method A uses temporal fusion.",
                        status="verified",
                        evidence_ids=("evidence-a",),
                        finding_id="finding-a",
                    ),
                ),
                commit_id="commit-a",
            )
            first = service.commit_step(
                "run-a",
                step.step_id,
                commit,
                expected_revision=started_run.revision,
            )
            repeated = service.commit_step(
                "run-a",
                step.step_id,
                commit,
                expected_revision=started_run.revision,
            )
            with self.assertRaisesRegex(ResearchStateError, "different payload"):
                service.commit_step(
                    "run-a",
                    step.step_id,
                    ResearchStepCommit("changed", commit_id="commit-a"),
                    expected_revision=started_run.revision,
                )
            with closing(sqlite3.connect(path)) as connection:
                commit_count = connection.execute(
                    "SELECT COUNT(*) FROM research_step_commits"
                ).fetchone()[0]

        self.assertEqual(first, repeated)
        self.assertEqual(2, repeated.run.revision)
        self.assertEqual(1, len(repeated.evidence_refs))
        self.assertEqual(1, len(repeated.findings))
        self.assertEqual(1, commit_count)

    def test_recoverable_service_requires_a_commit_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            service, plan = self._create_plan(path)
            started_run, step = service.claim_next_step(
                "run-a",
                expected_revision=plan.run.revision,
            )
            with self.assertRaises(ResearchControlError) as raised:
                service.commit_step(
                    "run-a",
                    step.step_id,
                    ResearchStepCommit("missing id"),
                    expected_revision=started_run.revision,
                )
            restored = ResearchRunStore(path).get_plan("run-a")

        self.assertEqual("research_commit_id_required", raised.exception.error_code)
        self.assertEqual(started_run.revision, restored.run.revision)
        self.assertEqual("running", restored.steps[0].status)

    def test_resume_rejects_changed_or_unstable_identity_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            service, plan = self._create_plan(path)
            started_run, step = service.claim_next_step(
                "run-a",
                expected_revision=plan.run.revision,
            )

            with self.assertRaises(ResearchControlError) as mismatch:
                service.resume_run(
                    "run-a",
                    expected_revision=started_run.revision,
                    current_identity=self._identity(corpus="sha256:changed"),
                )
            with self.assertRaises(ResearchControlError) as unstable:
                service.resume_run(
                    "run-a",
                    expected_revision=started_run.revision,
                    current_identity=self._identity(dirty=True),
                )
            restored = ResearchRunStore(path).get_plan("run-a")

        self.assertEqual("research_identity_mismatch", mismatch.exception.error_code)
        self.assertEqual("research_identity_unstable", unstable.exception.error_code)
        self.assertEqual(started_run.revision, restored.run.revision)
        self.assertEqual(step.step_id, restored.run.current_step_id)
        self.assertEqual("running", restored.steps[0].status)

    def test_cancelled_run_cannot_claim_more_work(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            service, plan = self._create_plan(path)
            cancelled = service.cancel_run(
                "run-a",
                expected_revision=plan.run.revision,
            )
            repeated = service.cancel_run("run-a", expected_revision=0)
            with self.assertRaises(ResearchControlError) as raised:
                service.claim_next_step(
                    "run-a",
                    expected_revision=cancelled.revision,
                )
            restored = ResearchRunStore(path).get_plan("run-a")

        self.assertEqual("cancelled", cancelled.status)
        self.assertEqual(cancelled, repeated)
        self.assertEqual("research_not_runnable", raised.exception.error_code)
        self.assertEqual(0, restored.steps[0].attempt_count)

    def test_storage_failure_has_stable_code_and_rolls_back_checkpoint(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            service, plan = self._create_plan(path)
            started_run, step = service.claim_next_step(
                "run-a",
                expected_revision=plan.run.revision,
            )
            with closing(sqlite3.connect(path)) as connection:
                connection.execute(
                    """
                    CREATE TRIGGER reject_research_evidence
                    BEFORE INSERT ON research_evidence_refs
                    BEGIN
                        SELECT RAISE(ABORT, 'forced checkpoint failure');
                    END
                    """
                )
                connection.commit()

            with self.assertRaises(ResearchControlError) as raised:
                service.commit_step(
                    "run-a",
                    step.step_id,
                    ResearchStepCommit(
                        "must roll back",
                        evidence_refs=(
                            EvidenceRefDraft("paper-001", evidence_id="evidence-a"),
                        ),
                        commit_id="commit-a",
                    ),
                    expected_revision=started_run.revision,
                )
            restored = ResearchRunStore(path).get_plan("run-a")
            with closing(sqlite3.connect(path)) as connection:
                commit_count = connection.execute(
                    "SELECT COUNT(*) FROM research_step_commits"
                ).fetchone()[0]

        self.assertEqual("research_storage_failed", raised.exception.error_code)
        self.assertEqual(started_run.revision, restored.run.revision)
        self.assertEqual("running", restored.steps[0].status)
        self.assertEqual((), restored.evidence_refs)
        self.assertEqual(0, commit_count)


if __name__ == "__main__":
    unittest.main()
