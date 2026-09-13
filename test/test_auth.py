from __future__ import annotations

import base64
import os
import unittest

from fastapi.testclient import TestClient

from agent_platform.api import create_app


class AuthBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app(auth_required=True, auth_tokens={"token-a": ["space-a"], "token-b": ["space-b"], "admin": ["*"]}))

    def test_health_is_public_but_api_requires_bearer(self) -> None:
        self.assertEqual(200, self.client.get("/health").status_code)
        response = self.client.get("/rooms")
        self.assertEqual(401, response.status_code)
        self.assertEqual("authentication_required", response.json()["code"])

    def test_space_isolation_covers_room_events_and_assets(self) -> None:
        headers_a = {"Authorization": "Bearer token-a"}
        headers_b = {"Authorization": "Bearer token-b"}
        room = self.client.post("/rooms", headers=headers_a, json={"space_id": "space-a", "title": "A"})
        self.assertEqual(201, room.status_code, room.text)
        room_id = room.json()["room_id"]
        self.assertEqual(403, self.client.get(f"/rooms/{room_id}", headers=headers_b).status_code)
        self.assertEqual(403, self.client.get(f"/rooms/{room_id}/events/stream", headers=headers_b).status_code)
        content = base64.b64encode(b"private").decode()
        upload = self.client.post("/assets", headers=headers_a, json={"space_id": "space-a", "filename": "x.txt", "content_base64": content})
        self.assertEqual(201, upload.status_code, upload.text)
        asset_id = upload.json()["asset_id"]
        self.assertEqual(403, self.client.get(f"/assets/{asset_id}", headers=headers_b).status_code)
        self.assertEqual(content, self.client.get(f"/assets/{asset_id}", headers=headers_a).json()["content_base64"])

    def test_production_auth_without_tokens_refuses_startup(self) -> None:
        old_env = os.environ.pop("LOCALRAG_AUTH_TOKENS_JSON", None)
        try:
            with self.assertRaises(RuntimeError):
                create_app(auth_required=True)
        finally:
            if old_env is not None:
                os.environ["LOCALRAG_AUTH_TOKENS_JSON"] = old_env


if __name__ == "__main__":
    unittest.main()

