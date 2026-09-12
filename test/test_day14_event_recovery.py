from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from agent_platform.api import create_app


class Day14EventRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_message_history_cursor_and_limit(self) -> None:
        room = self.client.post("/rooms", json={"space_id": "space-demo", "title": "分页"}).json()
        room_id = room["room_id"]
        for index in range(3):
            self.client.post(f"/rooms/{room_id}/messages", json={"content": f"m{index}"})
        page = self.client.get(f"/rooms/{room_id}/messages", params={"after": 1, "limit": 1})
        self.assertEqual(200, page.status_code)
        self.assertEqual([2], [item["room_sequence"] for item in page.json()["items"]])
        self.assertEqual(2, page.json()["next"])

    def test_sse_after_cursor_does_not_replay_older_events(self) -> None:
        room = self.client.post("/rooms", json={"space_id": "space-demo", "title": "事件"}).json()
        room_id = room["room_id"]
        self.app.state.events.append(room_id, "message_saved", payload={"label": "first"})
        self.app.state.events.append(room_id, "run_started", payload={"label": "second"})
        response = self.client.get(f"/rooms/{room_id}/events/stream", params={"after": 1})
        self.assertEqual("text/event-stream; charset=utf-8", response.headers["content-type"])
        self.assertNotIn('"label":"first"', response.text)
        self.assertIn('"label":"second"', response.text)


if __name__ == "__main__":
    unittest.main()
