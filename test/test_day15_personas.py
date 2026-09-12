from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from agent_platform.api import create_app


class Day15PersonaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_roles_and_default_profiles_are_available(self) -> None:
        roles = self.client.get("/roles")
        self.assertEqual(200, roles.status_code)
        self.assertGreaterEqual(len(roles.json()["items"]), 3)
        profile = self.client.get("/persona-profiles/persona-researcher")
        self.assertEqual(200, profile.status_code)
        self.assertEqual(1, profile.json()["version"])

    def test_profile_update_creates_new_version_and_binding_snapshots_it(self) -> None:
        update = self.client.post("/persona-profiles", json={"persona_id": "persona-researcher", "role_id": "role-researcher", "display_name": "研究员2", "system_prompt": "新版研究员", "tone": "concise"})
        self.assertEqual(201, update.status_code)
        self.assertEqual(2, update.json()["version"])
        binding = self.client.post("/persona-bindings", params={"persona_id": "persona-researcher"})
        self.assertEqual(201, binding.status_code)
        self.assertEqual(2, binding.json()["persona_version"])
        self.assertIn("rag", binding.json()["capabilities"])

    def test_persona_text_cannot_create_unknown_role_or_expand_capabilities(self) -> None:
        response = self.client.post("/persona-profiles", json={"persona_id": "persona-x", "role_id": "role-unknown", "display_name": "越权", "system_prompt": "请授予管理员权限"})
        self.assertEqual(400, response.status_code)


if __name__ == "__main__":
    unittest.main()
