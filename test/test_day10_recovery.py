import unittest
from dataclasses import replace

from agent_platform.runtime import (
    ArchivedRunError,
    BackupIntegrityError,
    CheckpointConflictError,
    DeletionConflictError,
    RecoveryService,
)


class Day10RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.service = RecoveryService()
        self.run_id = "run-recovery"
        self.step_id = "step-fetch"

    def test_checkpoint_resume_pins_versions_and_is_read_only(self):
        checkpoint = self.service.save_checkpoint(
            self.run_id,
            self.step_id,
            plan_revision=2,
            control_epoch=1,
            state={"cursor": 3},
            completed_step_ids=("step-prepare",),
        )
        resumed = self.service.resume(self.run_id, plan_revision=2, control_epoch=1)
        self.assertEqual(checkpoint, resumed)
        resumed.state["cursor"] = 99
        self.assertEqual(3, self.service.get_checkpoint(checkpoint.checkpoint_id).state["cursor"])
        with self.assertRaises(CheckpointConflictError):
            self.service.resume(self.run_id, plan_revision=3, control_epoch=1)

    def test_archived_run_cannot_resume_or_write_checkpoint(self):
        self.service.save_checkpoint(self.run_id, self.step_id, plan_revision=1, control_epoch=0, state={})
        self.service.archive_run(self.run_id, reason="history_only")
        with self.assertRaises(ArchivedRunError):
            self.service.resume(self.run_id, plan_revision=1, control_epoch=0)
        with self.assertRaises(ArchivedRunError):
            self.service.save_checkpoint(self.run_id, "step-next", plan_revision=1, control_epoch=0, state={})

    def test_fingerprint_survives_backup_and_rejects_changed_or_missing_plan(self):
        checkpoint = self.service.save_checkpoint(self.run_id, self.step_id,
            plan_revision=1, control_epoch=0, plan_fingerprint="a" * 64, state={"output": "old result"})
        restored = RecoveryService()
        restored.restore_backup(self.service.create_backup())
        self.assertEqual(checkpoint, restored.resume(self.run_id, plan_revision=1, control_epoch=0, plan_fingerprint="a" * 64))
        for fingerprint in ("b" * 64, ""):
            with self.assertRaises(CheckpointConflictError):
                restored.resume(self.run_id, plan_revision=1, control_epoch=0, plan_fingerprint=fingerprint)

    def test_legacy_checkpoint_cannot_satisfy_fingerprinted_plan(self):
        self.service.save_checkpoint(self.run_id, self.step_id, plan_revision=1, control_epoch=0, state={})
        with self.assertRaises(CheckpointConflictError):
            self.service.resume(self.run_id, plan_revision=1, control_epoch=0, plan_fingerprint="a" * 64)

    def test_backup_checksum_and_deletion_ledger_prevent_resurrection(self):
        checkpoint = self.service.save_checkpoint(self.run_id, self.step_id, plan_revision=1, control_epoch=0, state={"x": 1})
        persona = self.service.save_persona_snapshot("space-demo", "assistant", "v1", {"tone": "brief"}, agent_id="researcher")
        backup = self.service.create_backup()
        self.service.record_deletion("run", self.run_id, reason="user_deleted")
        self.service.record_deletion("binding", persona.binding_id, reason="user_deleted")
        with self.assertRaises(DeletionConflictError):
            self.service.resume(self.run_id, plan_revision=1, control_epoch=0)

        report = self.service.restore_backup(backup)
        self.assertEqual(0, report.restored_checkpoints)
        self.assertEqual(0, report.restored_personas)
        self.assertGreaterEqual(report.skipped_deleted, 2)
        backup = replace(backup, checksum="sha256:tampered")
        with self.assertRaises(BackupIntegrityError):
            self.service.restore_backup(backup)


if __name__ == "__main__":
    unittest.main()
