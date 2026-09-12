import unittest

from agent_platform.contracts import (
    AttemptIdentity,
    MessageIdentity,
    OperationIdentity,
    RoomEventCursor,
    RoomEventIdentity,
    RunIdentity,
    new_identifier,
    validate_identifier,
)


class IdentityContractTests(unittest.TestCase):
    def test_message_can_be_saved_before_task_target_is_resolved(self):
        message = MessageIdentity(
            space_id="space-local",
            room_id="room-one",
            turn_id="turn-one",
            message_id="message-one",
        )

        self.assertIsNone(message.task_id)
        self.assertIsNone(message.target_run_id)

    def test_terminal_followup_creates_linked_new_run_in_same_room(self):
        original = RunIdentity(
            space_id="space-local",
            room_id="room-one",
            task_id="task-one",
            run_id="run-one",
            plan_id="plan-one",
        )
        followup = RunIdentity(
            space_id=original.space_id,
            room_id=original.room_id,
            task_id=original.task_id,
            run_id="run-two",
            plan_id="plan-two",
            source_run_id=original.run_id,
            trigger_turn_id="turn-two",
        )

        self.assertEqual(original.room_id, followup.room_id)
        self.assertNotEqual(original.run_id, followup.run_id)
        self.assertEqual(original.run_id, followup.source_run_id)

    def test_attempt_pins_plan_and_control_versions(self):
        attempt = AttemptIdentity(
            room_id="room-one",
            task_id="task-one",
            run_id="run-one",
            plan_id="plan-one",
            step_id="step-one",
            attempt_id="attempt-one",
            plan_revision=3,
            control_epoch=2,
        )

        self.assertEqual(3, attempt.plan_revision)
        self.assertEqual(2, attempt.control_epoch)

    def test_retry_keeps_operation_id_but_uses_new_attempt_id(self):
        first = OperationIdentity(
            room_id="room-one",
            task_id="task-one",
            run_id="run-one",
            step_id="step-one",
            attempt_id="attempt-one",
            operation_id="operation-one",
        )
        retry = OperationIdentity(
            room_id=first.room_id,
            task_id=first.task_id,
            run_id=first.run_id,
            step_id=first.step_id,
            attempt_id="attempt-two",
            operation_id=first.operation_id,
        )

        self.assertNotEqual(first.attempt_id, retry.attempt_id)
        self.assertEqual(first.operation_id, retry.operation_id)

    def test_room_event_sequence_is_positive_and_cursor_can_start_at_zero(self):
        event = RoomEventIdentity("room-one", "event-one", 1)
        cursor = RoomEventCursor("room-one")

        self.assertEqual(1, event.room_sequence)
        self.assertEqual(0, cursor.room_sequence)
        with self.assertRaises(ValueError):
            RoomEventIdentity("room-one", "event-two", 0)

    def test_identifier_namespace_and_versions_fail_closed(self):
        self.assertTrue(new_identifier("run").startswith("run-"))
        self.assertEqual("task-one", validate_identifier(" task-one ", "task"))
        with self.assertRaises(ValueError):
            validate_identifier("run-one", "task")
        with self.assertRaises(TypeError):
            RunIdentity(
                space_id="space-local",
                room_id="room-one",
                task_id="task-one",
                run_id="run-one",
                plan_id="plan-one",
                control_epoch=True,
            )
        with self.assertRaises(ValueError):
            RunIdentity(
                space_id="space-local",
                room_id="room-one",
                task_id="task-one",
                run_id="run-one",
                plan_id="plan-one",
                source_run_id="run-one",
            )


if __name__ == "__main__":
    unittest.main()
