import unittest

from agent_platform.contracts.identity import RoomEventCursor
from agent_platform.runtime import EventConflictError, EventStore


class Day7EventStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = EventStore()
        self.room_id = "room-events"

    def test_append_assigns_gap_free_room_sequence_and_cursor_reads(self):
        first = self.store.append(self.room_id, "message_saved", payload={"text": "one"})
        second = self.store.append(self.room_id, "run_started", payload={"run": "new"})
        self.assertEqual((1, 2), (first.identity.room_sequence, second.identity.room_sequence))
        events = self.store.read_after(RoomEventCursor(self.room_id, 1))
        self.assertEqual((second.identity.event_id,), tuple(item.identity.event_id for item in events))

    def test_retrying_same_event_id_is_idempotent(self):
        event = self.store.append(self.room_id, "message_saved", event_id="event-fixed", payload={"x": 1})
        replay = self.store.append(self.room_id, "message_saved", event_id="event-fixed", payload={"x": 1})
        self.assertEqual(event, replay)
        with self.assertRaises(EventConflictError):
            self.store.append(self.room_id, "run_started", event_id="event-fixed")

    def test_commit_happens_before_publish(self):
        observed = []
        self.store.append_and_publish(
            lambda event: observed.append(self.store.read_after(RoomEventCursor(self.room_id, 0))),
            self.room_id,
            "message_saved",
        )
        self.assertEqual(1, len(observed[0]))

    def test_snapshot_and_replay_are_read_only(self):
        self.store.append(self.room_id, "message_saved")
        snapshot = self.store.snapshot(self.room_id)
        replayed = self.store.replay(snapshot)
        self.assertEqual(snapshot.events, replayed)
        self.assertEqual(1, self.store.snapshot(self.room_id).cursor.room_sequence)


if __name__ == "__main__":
    unittest.main()
