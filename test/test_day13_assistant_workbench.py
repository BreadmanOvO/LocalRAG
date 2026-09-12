from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from agent_platform.api import create_app


class Day13AssistantWorkbenchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_assistant_first_message_atomically_creates_room(self) -> None:
        response = self.client.post(
            "/assistant/messages",
            headers={"Idempotency-Key": "assistant-first-1"},
            json={"space_id": "space-demo", "content": "介绍 BEVFormer", "title": "研究任务"},
        )
        self.assertEqual(201, response.status_code)
        payload = response.json()
        self.assertTrue(payload["created"])
        self.assertEqual(payload["room"]["room_id"], payload["message"]["room_id"])
        self.assertEqual(1, payload["room"]["room_sequence"])
        self.assertEqual("user", payload["message"]["role"])

    def test_assistant_first_message_idempotent_replay(self) -> None:
        request = {"space_id": "space-demo", "content": "同一个问题"}
        first = self.client.post("/assistant/messages", headers={"Idempotency-Key": "assistant-replay-1"}, json=request)
        second = self.client.post("/assistant/messages", headers={"Idempotency-Key": "assistant-replay-1"}, json=request)
        self.assertEqual(201, first.status_code)
        self.assertEqual(201, second.status_code)
        self.assertFalse(second.json()["created"])
        self.assertEqual(first.json()["room"]["room_id"], second.json()["room"]["room_id"])
        room_id = first.json()["room"]["room_id"]
        self.assertEqual(1, len(self.client.get(f"/rooms/{room_id}/messages").json()["items"]))

    def test_assistant_idempotency_key_cannot_change_payload(self) -> None:
        headers = {"Idempotency-Key": "assistant-conflict-1"}
        self.client.post("/assistant/messages", headers=headers, json={"space_id": "space-demo", "content": "原问题"})
        conflict = self.client.post("/assistant/messages", headers=headers, json={"space_id": "space-demo", "content": "改写问题"})
        self.assertEqual(409, conflict.status_code)
        self.assertEqual("idempotency_conflict", conflict.json()["code"])

    def test_room_list_and_members_contract(self) -> None:
        room = self.client.post("/rooms", json={"space_id": "space-a", "title": "A"}).json()
        room_id = room["room_id"]
        members = self.app.state.repository.join_member(room_id, "researcher")
        listed = self.client.get("/rooms", params={"space_id": "space-a"})
        self.assertEqual(200, listed.status_code)
        self.assertEqual([room_id], [item["room_id"] for item in listed.json()["items"]])
        member_list = self.client.get(f"/rooms/{room_id}/members")
        self.assertEqual(200, member_list.status_code)
        self.assertEqual(members.membership_id, member_list.json()["items"][0]["membership_id"])

    def test_existing_room_message_and_openapi_routes(self) -> None:
        room = self.client.post("/rooms", json={"space_id": "space-demo", "title": "继续"}).json()
        response = self.client.post(f"/assistant/messages", json={"space_id": "space-demo", "room_id": room["room_id"], "content": "补充约束"})
        self.assertEqual(201, response.status_code)
        self.assertFalse(response.json()["created"])
        self.assertEqual(1, len(self.client.get(f"/rooms/{room['room_id']}/messages").json()["items"]))
        spec = self.client.get("/openapi.json").json()
        for path in ("/rooms", "/rooms/{room_id}/members", "/assistant/messages"):
            self.assertIn(path, spec["paths"])


if __name__ == "__main__":
    unittest.main()
