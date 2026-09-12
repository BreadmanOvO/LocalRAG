import unittest

from agent_platform.conversations import (
    ConflictError,
    ConversationRepository,
    RoomClosedError,
)


class Day6ConversationRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.repository = ConversationRepository()
        self.room = self.repository.create_room("space-demo", "Demo")

    def test_save_message_is_atomic_and_idempotent(self):
        first = self.repository.save_message(self.room.room_id, "hello", idempotency_key="req-1")
        replay = self.repository.save_message(self.room.room_id, "hello", idempotency_key="req-1")
        self.assertEqual(first, replay)
        self.assertEqual((1,), tuple(message.room_sequence for message in self.repository.list_messages(self.room.room_id)))
        with self.assertRaises(ConflictError):
            self.repository.save_message(self.room.room_id, "changed", idempotency_key="req-1")

    def test_tombstone_cannot_be_requeued(self):
        message = self.repository.save_message(self.room.room_id, "remove me", idempotency_key="req-2")
        tombstone = self.repository.tombstone_message(message.message_id)
        self.assertEqual("tombstoned", tombstone.status)
        with self.assertRaises(ConflictError):
            self.repository.update_message_status(message.message_id, "queued")
        with self.assertRaises(ConflictError):
            self.repository.save_message(self.room.room_id, "remove me", idempotency_key="req-2")

    def test_closed_room_rejects_new_messages_but_keeps_history(self):
        message = self.repository.save_message(self.room.room_id, "history")
        self.repository.archive_room(self.room.room_id)
        with self.assertRaises(RoomClosedError):
            self.repository.save_message(self.room.room_id, "new")
        self.assertEqual([message.message_id], [item.message_id for item in self.repository.list_messages(self.room.room_id)])

    def test_membership_leave_is_a_state_change_not_history_delete(self):
        membership = self.repository.join_member(self.room.room_id, "researcher")
        left = self.repository.leave_member(membership.membership_id)
        self.assertEqual("left", left.status)
        self.assertEqual(left.membership_id, self.repository.list_members(self.room.room_id)[0].membership_id)
        self.assertEqual(left, self.repository.leave_member(membership.membership_id))


if __name__ == "__main__":
    unittest.main()
