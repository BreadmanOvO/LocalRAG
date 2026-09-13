from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from agent_platform.api import create_app
from agent_platform.integrations.model_config_store import ModelConfigError, ModelConfigStore


class _ModelsHandler(BaseHTTPRequestHandler):
    received_authorization = ""

    def do_GET(self):  # noqa: N802
        type(self).received_authorization = self.headers.get("Authorization", "")
        body = json.dumps({"data": [{"id": "text-model", "owned_by": "local"}, {"id": "vision-model", "owned_by": "cloud"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):  # noqa: A002
        return


class ModelConfigStoreTests(unittest.TestCase):
    def test_empty_config_is_page_manageable_and_key_is_redacted(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "multi_agent_models.json"
            store = ModelConfigStore(path)
            self.assertEqual([], store.public()["profiles"])
            store.upsert_profile({"profile_id": "vision", "provider": "", "base_url": "", "model": "", "api_key": "secret", "enabled": False})
            public = store.public()["profiles"][0]
            self.assertEqual("", public["api_key"])
            self.assertTrue(public["has_api_key"])
            self.assertFalse(public["ready"])
            store.upsert_profile({"profile_id": "vision", "api_key": "", "clear_api_key": False})
            self.assertEqual("secret", store.load()["model_profiles"]["vision"]["api_key"])

    def test_api_crud_and_discovery_use_injected_local_store(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            client = TestClient(create_app(model_config_store=store))
            self.assertEqual({"profiles": [], "agents": [], "contract_version": "agent-platform-cloud-v1"}, client.get("/settings/model-catalog").json())
            saved = client.put("/settings/model-profiles/vision", json={"profile_id": "vision", "api_key": "local-secret", "enabled": False}).json()
            self.assertNotIn("api_key", saved["profiles"][0])
            self.assertEqual(200, client.put("/settings/agents/reviewer", json={"agent_id": "reviewer", "display_name": "审查员", "responsibility": "核验", "model_profile": "vision"}).status_code)
            self.assertEqual(409, client.delete("/settings/model-profiles/vision").status_code)
            self.assertEqual(200, client.delete("/settings/agents/reviewer").status_code)

    def test_auto_agent_persists_constraints_and_reports_no_silent_fallback(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            store.upsert_profile({
                "profile_id": "text", "display_name": "文本模型", "provider": "mock",
                "base_url": "https://example.com/v1", "model": "text-model", "api_key": "secret",
                "tier": "standard", "capabilities": ["chat"], "modalities": ["text"],
                "scenarios": ["chat"], "enabled": True,
            })
            public = store.upsert_agent({
                "agent_id": "reviewer", "display_name": "审查员", "responsibility": "图片审查",
                "model_binding_mode": "auto", "model_profile": "", "enabled": True,
                "auto_tier": "strong", "auto_capabilities": ["vision"],
                "auto_modalities": ["image"], "auto_scenarios": ["vision-review"],
            })
            agent = public["agents"][0]
            self.assertEqual("auto", agent["model_binding_mode"])
            self.assertFalse(agent["ready"])
            self.assertIn("没有符合自动路由条件的已就绪模型", agent["readiness_issues"])
            raw_agent = store.load()["agents"]["reviewer"]
            self.assertEqual(["image"], raw_agent["auto_modalities"])
            with self.assertRaisesRegex(ModelConfigError, "cannot set model_profile"):
                store.upsert_agent({
                    "agent_id": "reviewer", "model_binding_mode": "auto", "model_profile": "text",
                })

    def test_auto_agent_becomes_ready_only_when_one_profile_matches_all_constraints(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            store.upsert_profile({
                "profile_id": "vision", "display_name": "视觉推理", "provider": "mock",
                "base_url": "https://example.com/v1", "model": "vision-model", "api_key": "secret",
                "tier": "strong", "capabilities": ["reasoning", "vision"],
                "modalities": ["text", "image"], "scenarios": ["vision-review"],
                "max_concurrency": 3, "enabled": True,
            })
            public = store.upsert_agent({
                "agent_id": "reviewer", "display_name": "审查员", "responsibility": "图片审查",
                "model_binding_mode": "auto", "enabled": True, "auto_tier": "strong",
                "auto_capabilities": ["reasoning", "vision"], "auto_modalities": ["image"],
                "auto_scenarios": ["vision-review"],
            })
            agent = public["agents"][0]
            self.assertTrue(agent["ready"], agent["readiness_issues"])
            self.assertEqual("", agent["model_profile"])

    def test_discovery_reads_saved_profile_key_without_returning_it(self) -> None:
        server = HTTPServer(("127.0.0.1", 0), _ModelsHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with TemporaryDirectory() as directory:
                store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
                store.upsert_profile({"profile_id": "local", "base_url": f"http://127.0.0.1:{server.server_port}/v1", "api_key": "saved-secret", "enabled": False})
                client = TestClient(create_app(model_config_store=store))
                with patch("agent_platform.integrations.model_config_store.ModelConfigStore._is_safe_discovery_host", return_value=True):
                    response = client.post("/settings/model-discovery", json={"profile_id": "local", "base_url": f"http://127.0.0.1:{server.server_port}/v1"})
                self.assertEqual(200, response.status_code, response.text)
                self.assertEqual(["text-model", "vision-model"], [item["id"] for item in response.json()["items"]])
                self.assertEqual("Bearer saved-secret", _ModelsHandler.received_authorization)
                self.assertNotIn("saved-secret", response.text)
        finally:
            server.shutdown()

    def test_discovery_rejects_private_hosts(self) -> None:
        with self.assertRaisesRegex(ModelConfigError, "private or local"):
            ModelConfigStore.discover_models("http://127.0.0.1:9/v1")

    def test_saved_key_cannot_be_forwarded_to_a_different_url(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            store.upsert_profile({"profile_id": "cloud", "base_url": "https://api.example.com/v1", "api_key": "saved-secret"})
            with self.assertRaisesRegex(ModelConfigError, "profile URL"):
                store.discovery_key("cloud", base_url="https://attacker.example.com/v1")

    def test_discovery_requires_admin_scope_when_authentication_is_enabled(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            client = TestClient(create_app(model_config_store=store, auth_required=True, auth_tokens={"user-token": ["space-demo"], "admin-token": ["*"]}))
            user = client.post("/settings/model-discovery", headers={"Authorization": "Bearer user-token"}, json={"base_url": "https://api.example.com/v1"})
            self.assertEqual(403, user.status_code)
            self.assertEqual("admin_required", user.json()["code"])


if __name__ == "__main__":
    unittest.main()
