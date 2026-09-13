from __future__ import annotations

import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from agent_platform.conversations import ConflictError, SqlAlchemyConversationRepository
from fastapi.testclient import TestClient
from agent_platform.api import create_app


class SqlConversationRepositoryTests(unittest.TestCase):
    def test_room_and_first_message_share_one_transaction(self) -> None:
        repo = SqlAlchemyConversationRepository.from_url("sqlite://")
        with self.assertRaises(ValueError):
            repo.create_room_with_message("space-demo", "empty", " ")
        self.assertEqual((), repo.list_rooms())
        room, message = repo.create_room_with_message("space-demo", "initial", "hello")
        self.assertEqual(1, room.room_sequence)
        self.assertEqual(room.room_id, message.room_id)

    def test_memory_sqlite_is_shared_across_threads(self) -> None:
        repo = SqlAlchemyConversationRepository.from_url("sqlite://")
        room = repo.create_room("space-demo", "共享")
        with ThreadPoolExecutor(max_workers=2) as pool:
            messages = list(pool.map(lambda value: repo.save_message(room.room_id, value), ("a", "b")))
        self.assertEqual({1, 2}, {message.room_sequence for message in messages})

    def test_concurrent_room_creation_reuses_space_without_false_conflict(self) -> None:
        repo = SqlAlchemyConversationRepository.from_url("sqlite://")
        with ThreadPoolExecutor(max_workers=2) as pool:
            rooms = list(pool.map(lambda title: repo.create_room("space-demo", title), ("a", "b")))
        self.assertEqual({"a", "b"}, {room.title for room in rooms})

    def test_sqlite_round_trip_and_idempotency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = SqlAlchemyConversationRepository.from_url(f"sqlite:///{Path(directory) / 'runtime.db'}")
            room = repo.create_room("space-demo", "研究")
            first = repo.save_message(room.room_id, "hello", idempotency_key="k1")
            replay = repo.save_message(room.room_id, "hello", idempotency_key="k1")
            self.assertEqual(first.message_id, replay.message_id)
            self.assertEqual(1, repo.get_room(room.room_id).room_sequence)
            self.assertEqual("hello", repo.list_messages(room.room_id)[0].content)

            with self.assertRaises(ConflictError):
                repo.save_message(room.room_id, "different", idempotency_key="k1")
            repo.close()

    def test_member_is_persisted(self) -> None:
        repo = SqlAlchemyConversationRepository.from_url("sqlite://")
        room = repo.create_room("space-demo")
        repo.join_member(room.room_id, "researcher")
        self.assertEqual(["researcher"], [item.agent_id for item in repo.list_members(room.room_id)])

    def test_api_can_select_sql_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            repo = SqlAlchemyConversationRepository.from_url(f"sqlite:///{Path(directory) / 'api.db'}")
            client = TestClient(create_app(repository=repo))
            response = client.post("/rooms", json={"space_id": "space-demo", "title": "sql"})
            self.assertEqual(201, response.status_code)
            room_id = response.json()["room_id"]
            message = client.post(f"/rooms/{room_id}/messages", json={"content": "persisted"})
            self.assertEqual(201, message.status_code)
            self.assertEqual("persisted", repo.list_messages(room_id)[0].content)
            repo.close()


if __name__ == "__main__":
    unittest.main()
