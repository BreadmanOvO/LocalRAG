from __future__ import annotations

import json
import os
import socket
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

    def test_provider_model_name_with_slash_is_preserved_on_save(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            with TestClient(create_app(model_config_store=store)) as client:
                response = client.put("/settings/model-profiles/glm52", json={
                    "profile_id": "glm52", "provider": "modelscope",
                    "base_url": "https://api-inference.modelscope.cn/v1",
                    "model": "ZhipuAI/GLM-5.2", "api_key": "test-only-secret",
                    "enabled": True,
                })
                self.assertEqual(200, response.status_code)
                item = response.json()["profiles"][0]
                self.assertEqual("ZhipuAI/GLM-5.2", item["model"])
                self.assertTrue(item["has_api_key"])
                self.assertNotIn("test-only-secret", response.text)
                client.put("/settings/model-profiles/glm52", json={
                    "profile_id": "glm52", "provider": "modelscope",
                    "base_url": "https://api-inference.modelscope.cn/v1",
                    "model": "ZhipuAI/GLM-5.2", "api_key": "", "enabled": True,
                })
            reloaded = ModelConfigStore(store.path).load()["model_profiles"]["glm52"]
            self.assertEqual("test-only-secret", reloaded["api_key"])
            self.assertEqual("ZhipuAI/GLM-5.2", reloaded["model"])

    def test_clone_profile_keeps_secret_server_side_and_opens_as_disabled_copy(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            store.upsert_profile({
                "profile_id": "provider-model", "display_name": "主模型", "provider": "cloud",
                "base_url": "https://example.com/v1", "model": "model-a", "api_key": "secret",
                "capabilities": ["reasoning"], "enabled": True,
            })
            client = TestClient(create_app(model_config_store=store))
            response = client.post("/settings/model-profiles/provider-model/clone")
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual("provider-model-copy", response.json()["profile_id"])
            cloned = store.load()["model_profiles"]["provider-model-copy"]
            self.assertEqual("secret", cloned["api_key"])
            self.assertFalse(cloned["enabled"])
            self.assertNotIn("secret", response.text)

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
                with patch("agent_platform.integrations.model_config_store.ModelConfigStore._resolve_safe_discovery_host", return_value=("127.0.0.1",)):
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

    def test_discovery_allows_synthetic_dns_for_public_hostname_in_development(self) -> None:
        synthetic_result = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("198.18.1.57", 0))]
        with patch.dict(os.environ, {"LOCALRAG_ENV": "development", "LOCALRAG_ALLOW_SYNTHETIC_DNS": "1"}, clear=False):
            with patch("agent_platform.integrations.model_config_store.socket.getaddrinfo", return_value=synthetic_result):
                self.assertTrue(ModelConfigStore._is_safe_discovery_host("provider.example"))

    def test_discovery_allows_synthetic_dns_for_explicit_local_environment(self) -> None:
        synthetic_result = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("198.18.1.57", 0))]
        with patch.dict(os.environ, {"LOCALRAG_ENV": "development"}, clear=False):
            with patch.dict(os.environ, {"LOCALRAG_ALLOW_SYNTHETIC_DNS": ""}, clear=False):
                with patch("agent_platform.integrations.model_config_store.socket.getaddrinfo", return_value=synthetic_result):
                    self.assertTrue(ModelConfigStore._is_safe_discovery_host("provider.example"))

    def test_discovery_rejects_synthetic_dns_when_environment_is_missing_or_unknown(self) -> None:
        synthetic_result = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("198.18.1.57", 0))]
        for environment in ("", "staging", "production-like"):
            with self.subTest(environment=environment):
                with patch.dict(os.environ, {"LOCALRAG_ENV": environment, "LOCALRAG_ALLOW_SYNTHETIC_DNS": ""}, clear=False):
                    with patch("agent_platform.integrations.model_config_store.socket.getaddrinfo", return_value=synthetic_result):
                        with self.assertRaisesRegex(ModelConfigError, "private or local"):
                            ModelConfigStore._is_safe_discovery_host("provider.example")

    def test_discovery_pins_validated_dns_result_for_outbound_connection(self) -> None:
        calls: list[str] = []

        def changing_resolver(host, port, family=0, socktype=0, proto=0, flags=0):
            calls.append(str(host))
            address = "93.184.216.34" if str(host) == "provider.example" else str(host)
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, int(port or 443)))]

        with patch.dict(os.environ, {"LOCALRAG_ENV": "production", "LOCALRAG_ALLOW_SYNTHETIC_DNS": "0"}, clear=False):
            with patch("agent_platform.integrations.model_config_store.socket.getaddrinfo", side_effect=changing_resolver):
                addresses = ModelConfigStore._resolve_safe_discovery_host("provider.example")
                with ModelConfigStore._pin_discovery_resolution("provider.example", addresses):
                    result = socket.getaddrinfo("provider.example", 443)
        self.assertEqual(("93.184.216.34",), addresses)
        self.assertEqual("93.184.216.34", result[0][4][0])
        self.assertEqual(["provider.example", "93.184.216.34"], calls)

    def test_discovery_rejects_synthetic_dns_in_production(self) -> None:
        synthetic_result = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("198.18.1.57", 0))]
        with patch.dict(os.environ, {"LOCALRAG_ENV": "production", "LOCALRAG_ALLOW_SYNTHETIC_DNS": "1"}, clear=False):
            with patch("agent_platform.integrations.model_config_store.socket.getaddrinfo", return_value=synthetic_result):
                with self.assertRaisesRegex(ModelConfigError, "private or local"):
                    ModelConfigStore._is_safe_discovery_host("provider.example")

    def test_discovery_rejects_literal_benchmark_address_even_in_development(self) -> None:
        with patch.dict(os.environ, {"LOCALRAG_ENV": "development", "LOCALRAG_ALLOW_SYNTHETIC_DNS": "1"}, clear=False):
            with self.assertRaisesRegex(ModelConfigError, "private or local"):
                ModelConfigStore._is_safe_discovery_host("198.18.1.57")

    def test_discovery_rejects_non_global_special_addresses(self) -> None:
        for hostname in ("100.64.0.1", "224.0.0.1"):
            with self.subTest(hostname=hostname):
                with self.assertRaisesRegex(ModelConfigError, "private or local"):
                    ModelConfigStore._is_safe_discovery_host(hostname)

    def test_model_verification_rejects_private_hosts_before_provider_call(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            store.upsert_profile({
                "profile_id": "local", "provider": "local", "base_url": "http://127.0.0.1:9/v1",
                "model": "local-model", "api_key": "secret", "enabled": False,
            })
            client = TestClient(create_app(model_config_store=store))
            with patch("openai.OpenAI") as provider_client:
                response = client.post("/settings/model-profiles/local/verify")
            self.assertEqual(502, response.status_code, response.text)
            self.assertEqual("model_verification_failed", response.json()["code"])
            self.assertIn("private or local", response.json()["message"])
            provider_client.assert_not_called()

    def test_discovery_rejects_malformed_url_as_domain_error(self) -> None:
        with self.assertRaisesRegex(ModelConfigError, r"http\(s\)"):
            ModelConfigStore.discover_models("http://[broken/v1")

    def test_saved_key_cannot_be_forwarded_to_a_different_url(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            store.upsert_profile({"profile_id": "cloud", "base_url": "https://api.example.com/v1", "api_key": "saved-secret"})
            with self.assertRaisesRegex(ModelConfigError, "profile URL"):
                store.discovery_key("cloud", base_url="https://attacker.example.com/v1")

    def test_saved_key_cannot_be_forwarded_when_profile_url_is_empty(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            store.upsert_profile({"profile_id": "partial", "api_key": "saved-secret", "base_url": ""})
            with self.assertRaisesRegex(ModelConfigError, "profile URL"):
                store.discovery_key("partial", base_url="https://provider.example/v1")

    def test_discovery_requires_admin_scope_when_authentication_is_enabled(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            client = TestClient(create_app(model_config_store=store, auth_required=True, auth_tokens={"user-token": ["space-demo"], "admin-token": ["*"]}))
            user = client.post("/settings/model-discovery", headers={"Authorization": "Bearer user-token"}, json={"base_url": "https://api.example.com/v1"})
            self.assertEqual(403, user.status_code)
            self.assertEqual("admin_required", user.json()["code"])

    def test_model_catalog_mutations_require_admin_scope(self) -> None:
        with TemporaryDirectory() as directory:
            store = ModelConfigStore(Path(directory) / "multi_agent_models.json")
            client = TestClient(create_app(model_config_store=store, auth_required=True, auth_tokens={"user-token": ["space-demo"], "admin-token": ["*"]}))
            user_headers = {"Authorization": "Bearer user-token"}
            admin_headers = {"Authorization": "Bearer admin-token"}
            self.assertEqual(403, client.get("/settings/model-catalog", headers=user_headers).status_code)
            self.assertEqual(403, client.put("/settings/model-profiles/text", headers=user_headers, json={"profile_id": "text"}).status_code)
            self.assertEqual(200, client.get("/settings/model-catalog", headers=admin_headers).status_code)
            self.assertEqual(200, client.put("/settings/model-profiles/text", headers=admin_headers, json={"profile_id": "text"}).status_code)


if __name__ == "__main__":
    unittest.main()
