from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from agent_platform.api import create_app

class Day18TraceTests(unittest.TestCase):
    def test_event_detail_and_failure_location(self) -> None:
        app = create_app(); client = TestClient(app)
        room = client.post("/rooms", json={"space_id": "space-demo", "title": "追溯"}).json(); room_id = room["room_id"]
        event = app.state.events.append(room_id, "run_failed", step_id="step-x", attempt_id="attempt-x", payload={"error": "tool_call_limit_exceeded"})
        response = client.get(f"/rooms/{room_id}/events/{event.identity.event_id}")
        self.assertEqual(200, response.status_code)
        self.assertEqual("step-x", response.json()["step_id"])
        self.assertEqual("tool_call_limit_exceeded", response.json()["payload"]["error"])

if __name__ == "__main__": unittest.main()
