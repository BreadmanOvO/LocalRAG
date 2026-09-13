from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from agent_platform.api import create_app
from agent_platform.runtime import EventStore as RuntimeEventStore


class Day11ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events = RuntimeEventStore()
        self.client = TestClient(create_app(events=self.events))

    def test_room_and_message_idempotency(self) -> None:
        response = self.client.post(
            "/rooms",
            headers={"Idempotency-Key": "room-create-1"},
            json={"space_id": "space-demo", "title": "Demo"},
        )
        self.assertEqual(201, response.status_code)
        room_id = response.json()["room_id"]
        repeated = self.client.post(
            "/rooms",
            headers={"Idempotency-Key": "room-create-1"},
            json={"space_id": "space-demo", "title": "Demo"},
        )
        self.assertEqual(201, repeated.status_code)
        self.assertEqual(room_id, repeated.json()["room_id"])

        message = self.client.post(
            f"/rooms/{room_id}/messages",
            headers={"Idempotency-Key": "message-1"},
            json={"content": "hello"},
        )
        self.assertEqual(201, message.status_code)
        repeated_message = self.client.post(
            f"/rooms/{room_id}/messages",
            headers={"Idempotency-Key": "message-1"},
            json={"content": "hello"},
        )
        self.assertEqual(message.json()["message_id"], repeated_message.json()["message_id"])
        self.assertEqual(1, len(self.client.get(f"/rooms/{room_id}/messages").json()["items"]))

    def test_active_task_followup_and_stale_task_version(self) -> None:
        room = self.client.post("/rooms", json={"space_id": "space-demo", "title": "Task room"}).json()
        task = self.client.post("/tasks", json={"room_id": room["room_id"], "title": "Research"}).json()
        followup = self.client.post(f"/tasks/{task['task_id']}/followups", json={"content": "add sources"})
        self.assertEqual(200, followup.status_code)
        self.assertEqual("accepted", followup.json()["status"])
        stale = self.client.post(f"/tasks/{task['task_id']}/followups", json={"content": "stale", "expected_task_version": 1})
        self.assertEqual(409, stale.status_code)
        self.assertEqual("version_conflict", stale.json()["code"])
        self.assertIn("row_version", stale.json()["details"])

    def test_control_conflict_is_structured_and_command_is_idempotent(self) -> None:
        run = self.client.post("/runs", json={"run_id": "run-api-1"}).json()
        command = self.client.post(
            "/commands/operation-start-1",
            json={"action": "start", "run_id": "run-api-1", "expected_row_version": 1},
        )
        self.assertEqual(200, command.status_code)
        self.assertEqual("accepted", command.json()["status"])
        self.assertEqual(2, command.json()["run"]["row_version"])
        self.assertEqual(command.json(), self.client.post(
            "/commands/operation-start-1",
            json={"action": "start", "run_id": "run-api-1", "expected_row_version": 1},
        ).json())
        stale = self.client.post(
            "/commands/operation-pause-1",
            json={"action": "pause", "run_id": "run-api-1", "expected_row_version": 1, "expected_control_epoch": 0},
        )
        self.assertEqual(409, stale.status_code)
        self.assertEqual("version_conflict", stale.json()["code"])
        self.assertEqual(2, stale.json()["row_version"])
        self.assertEqual(1, stale.json()["control_epoch"])

    def test_events_and_unavailable_asset_contract(self) -> None:
        room = self.client.post("/rooms", json={"space_id": "space-demo", "title": "Events"}).json()
        room_id = room["room_id"]
        self.events.append(room_id, "message_saved", payload={"message_id": "message-event-1"})
        events = self.client.get(f"/rooms/{room_id}/events")
        self.assertEqual(200, events.status_code)
        self.assertEqual(1, len(events.json()["items"]))
        asset = self.client.get("/assets/asset-demo")
        self.assertEqual(404, asset.status_code)
        self.assertEqual("not_found", asset.json()["code"])


if __name__ == "__main__":
    unittest.main()
