import unittest
from datetime import datetime, timedelta, timezone

from agent_platform.runtime import (
    ControlConflictError,
    LeaseConflictError,
    RunController,
    RunNotClaimableError,
)


class ManualClock:
    def __init__(self):
        self.value = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def __call__(self):
        return self.value

    def advance(self, seconds):
        self.value += timedelta(seconds=seconds)


class Day8RunControlTests(unittest.TestCase):
    def setUp(self):
        self.clock = ManualClock()
        self.controller = RunController(clock=self.clock)
        self.run = self.controller.register_run("run-control", plan_revision=1)
        self.run = self.controller.start("run-control", expected_row_version=self.run.row_version)

    def test_only_one_worker_can_lease_and_new_fence_rejects_old(self):
        attempt = self.controller.claim_attempt(
            "run-control", "step-one", "worker-a", expected_row_version=self.run.row_version, plan_revision=1, ttl_seconds=5
        )
        self.run = self.controller.get_run("run-control")
        with self.assertRaises(LeaseConflictError):
            self.controller.claim_attempt(
                "run-control", "step-one", "worker-b", expected_row_version=self.run.row_version, plan_revision=1, ttl_seconds=5
            )
        self.clock.advance(6)
        replacement = self.controller.claim_attempt(
            "run-control", "step-one", "worker-b", expected_row_version=self.run.row_version, plan_revision=1, ttl_seconds=5
        )
        self.assertGreater(replacement.fencing_token, attempt.fencing_token)
        late = self.controller.submit_attempt(attempt.attempt_id, result="old result")
        self.assertEqual("late_audit", late.status)
        self.assertEqual(1, len(self.controller.list_audit()))

    def test_pause_increments_control_epoch_and_late_result_is_audited(self):
        attempt = self.controller.claim_attempt(
            "run-control", "step-two", "worker-a", expected_row_version=self.run.row_version, plan_revision=1
        )
        running = self.controller.get_run("run-control")
        paused = self.controller.pause(
            "run-control", expected_row_version=running.row_version, expected_control_epoch=running.control_epoch
        )
        self.assertEqual("paused", paused.status)
        self.assertGreater(paused.control_epoch, attempt.control_epoch)
        late = self.controller.submit_attempt(attempt.attempt_id, result="arrived after pause")
        self.assertEqual("late_audit", late.status)

    def test_cancel_uses_both_cas_versions_and_stale_command_is_rejected(self):
        current = self.controller.get_run("run-control")
        with self.assertRaises(ControlConflictError):
            self.controller.cancel(
                "run-control", expected_row_version=current.row_version - 1, expected_control_epoch=current.control_epoch
            )
        cancelled = self.controller.cancel(
            "run-control", expected_row_version=current.row_version, expected_control_epoch=current.control_epoch
        )
        self.assertEqual("cancelled", cancelled.status)
        with self.assertRaises(RunNotClaimableError):
            self.controller.start("run-control", expected_row_version=cancelled.row_version)

    def test_attempt_submission_succeeds_only_with_live_lease(self):
        attempt = self.controller.claim_attempt(
            "run-control", "step-three", "worker-a", expected_row_version=self.run.row_version, plan_revision=1
        )
        completed = self.controller.submit_attempt(attempt.attempt_id, result="ok")
        self.assertEqual("succeeded", completed.status)
        self.assertEqual("ok", completed.result)


if __name__ == "__main__":
    unittest.main()
