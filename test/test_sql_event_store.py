from __future__ import annotations

import unittest
import tempfile
from concurrent.futures import ThreadPoolExecutor

from agent_platform.contracts.identity import RoomEventCursor
from agent_platform.runtime.sql_event_store import SqlAlchemyEventStore


class SqlEventStoreTests(unittest.TestCase):
    def test_append_idempotency_and_cursor_replay(self) -> None:
        store = SqlAlchemyEventStore(__import__("sqlalchemy").create_engine("sqlite://"))
        first = store.append("room-demo", "run_started", event_id="event-one", payload={"x": 1})
        replay = store.append("room-demo", "run_started", event_id="event-one", payload={"x": 9})
        self.assertEqual(first, replay)
        second = store.append("room-demo", "step_completed", payload={"x": 2})
        self.assertEqual([second.identity.event_id], [item.identity.event_id for item in store.read_after(RoomEventCursor("room-demo", 1))])
        self.assertEqual(2, store.snapshot("room-demo").cursor.room_sequence)

    def test_concurrent_room_appends_keep_gap_free_sequences(self) -> None:
        from sqlalchemy import create_engine
        with tempfile.TemporaryDirectory() as directory:
            store = SqlAlchemyEventStore(create_engine(f"sqlite:///{directory}/events.db", connect_args={"check_same_thread": False}))
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda index: store.append("room-concurrent", "step_completed", event_id=f"event-{index}"), range(20)))
            events = store.snapshot("room-concurrent").events
            self.assertEqual(list(range(1, 21)), [event.identity.room_sequence for event in events])
            store.engine.dispose()


if __name__ == "__main__":
    unittest.main()
