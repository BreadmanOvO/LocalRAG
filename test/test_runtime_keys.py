import json
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from config.runtime_keys import (
    RuntimeProviderConfig,
    load_runtime_config,
    update_model_routes,
)


class RuntimeKeysTests(unittest.TestCase):
    @staticmethod
    def _v2_payload() -> dict:
        def role(route: str) -> dict:
            return {
                "route": route,
                "cloud": {
                    "provider": "sensenova",
                    "base_url": "https://example.com/v1",
                    "model": "cloud-chat",
                    "api_key_env": "CLOUD_KEY",
                },
                "local": {
                    "base_url": "http://127.0.0.1:8001/v1",
                    "model": "local-model",
                    "api_token_env": "LOCAL_TOKEN",
                    "tool_calling_verified": False,
                },
            }

        return {
            "contract_version": "localrag-runtime-v2",
            "roles": {
                "planner": role("cloud"),
                "rag": role("local"),
                "summary": role("local"),
            },
            "embedding": {
                "provider": "local_sentence_transformer",
                "model": "models/bge-m3",
            },
        }

    def test_v2_config_loads_independent_role_routes_and_env_secrets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(json.dumps(self._v2_payload()), encoding="utf-8")
            config = load_runtime_config(
                path,
                environ={"CLOUD_KEY": "cloud-secret", "LOCAL_TOKEN": "local-secret"},
            )

        self.assertEqual("cloud", config.role("planner").route)
        self.assertEqual("local", config.role("rag").route)
        self.assertEqual("local", config.role("summary").route)
        self.assertEqual("cloud-secret", config.role("rag").cloud.api_key)
        self.assertEqual("local-secret", config.role("summary").local.api_token)
        self.assertEqual("models/bge-m3", config.embedding.model)

    def test_v2_route_update_is_atomic_and_preserves_endpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            payload = self._v2_payload()
            path.write_text(json.dumps(payload), encoding="utf-8")
            environment = {"CLOUD_KEY": "cloud", "LOCAL_TOKEN": "local"}

            updated = update_model_routes(
                {"planner": "local", "rag": "cloud"},
                path,
                environ=environment,
            )
            loaded = load_runtime_config(path, environ=environment)
            raw = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(path, updated)
        self.assertEqual("local", loaded.role("planner").route)
        self.assertEqual("cloud", loaded.role("rag").route)
        self.assertEqual("local", loaded.role("summary").route)
        self.assertEqual(
            payload["roles"]["planner"]["cloud"],
            raw["roles"]["planner"]["cloud"],
        )
        self.assertNotIn("cloud", raw["roles"]["planner"]["cloud"].get("api_key_env", ""))

    def test_v2_cloud_only_config_does_not_require_local_token(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            payload = self._v2_payload()
            for role in payload["roles"].values():
                role["route"] = "cloud"
            path.write_text(json.dumps(payload), encoding="utf-8")

            config = load_runtime_config(
                path,
                environ={"CLOUD_KEY": "cloud-secret"},
            )

        self.assertEqual("cloud", config.role("planner").route)
        self.assertEqual("cloud", config.role("rag").route)
        self.assertEqual("cloud", config.role("summary").route)
        self.assertEqual("", config.role("rag").local.api_token)

    def test_switching_cloud_route_to_local_requires_local_token(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            payload = self._v2_payload()
            for role in payload["roles"].values():
                role["route"] = "cloud"
            path.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(
                RuntimeError, r"Missing local model API token for rag environment variable: LOCAL_TOKEN"
            ):
                update_model_routes(
                    {"rag": "local"},
                    path,
                    environ={"CLOUD_KEY": "cloud-secret"},
                )

    def test_successfully_parses_unified_runtime_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(
                json.dumps(
                    {
                        "provider": "  modelscope  ",
                        "api_key": "  api-key  ",
                        "base_url": " https://example.com/v1 ",
                        "chat_model_name": " qwen-max ",
                        "embedding_model_name": " text-embedding-v4 ",
                    }
                ),
                encoding="utf-8",
            )

            config = load_runtime_config(path)

            self.assertEqual(
                RuntimeProviderConfig(
                    provider="modelscope",
                    api_key="api-key",
                    base_url="https://example.com/v1",
                    chat_model_name="qwen-max",
                    embedding_model_name="text-embedding-v4",
                ),
                config,
            )

    def test_successfully_parses_legacy_bailian_shape(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "key.json"
            path.write_text(
                json.dumps(
                    {
                        "dashscope_api_key": "  api-key  ",
                        "dashscope_base_url": " https://example.com/v1 ",
                        "chat_model_name": " qwen-max ",
                        "embedding_model_name": " text-embedding-v4 ",
                    }
                ),
                encoding="utf-8",
            )

            config = load_runtime_config(path)

            self.assertEqual(
                RuntimeProviderConfig(
                    provider="bailian",
                    api_key="api-key",
                    base_url="https://example.com/v1",
                    chat_model_name="qwen-max",
                    embedding_model_name="text-embedding-v4",
                ),
                config,
            )

    def test_successfully_parses_local_embedding_provider(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(
                json.dumps(
                    {
                        "provider": "local_embedding",
                        "api_key": "api-key",
                        "base_url": "https://example.com/v1",
                        "chat_model_name": "deepseek-ai/DeepSeek-V3.2",
                        "embedding_model_name": "local-hash-embedding",
                    }
                ),
                encoding="utf-8",
            )

            config = load_runtime_config(path)

            self.assertEqual("local_embedding", config.provider)
            self.assertEqual("local-hash-embedding", config.embedding_model_name)
            self.assertIsNone(config.local_model_gateway)

    def test_successfully_parses_local_transformers_provider(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(
                json.dumps(
                    {
                        "provider": "local_transformers",
                        "api_key": "local",
                        "base_url": "local",
                        "chat_model_name": "models/Qwen3-4B",
                        "embedding_model_name": "models/bge-m3",
                        "device": "cuda",
                        "torch_dtype": "bfloat16",
                        "max_new_tokens": 256,
                        "adapter_path": "saves/Qwen3-4B-Thinking/lora/localrag_sft_e1_qlora_smoke",
                        "rag_system_prompt": "请只根据参考资料回答，并在末尾列出引用。",
                    }
                ),
                encoding="utf-8",
            )

            config = load_runtime_config(path)

            self.assertEqual("local_transformers", config.provider)
            self.assertEqual("models/Qwen3-4B", config.chat_model_name)
            self.assertEqual("models/bge-m3", config.embedding_model_name)
            self.assertEqual("cuda", config.device)
            self.assertEqual("bfloat16", config.torch_dtype)
            self.assertEqual(256, config.max_new_tokens)
            self.assertEqual(
                "saves/Qwen3-4B-Thinking/lora/localrag_sft_e1_qlora_smoke",
                config.adapter_path,
            )
            self.assertEqual("请只根据参考资料回答，并在末尾列出引用。", config.rag_system_prompt)

    def test_local_transformers_generation_options_have_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(
                json.dumps(
                    {
                        "provider": "local_transformers",
                        "api_key": "local",
                        "base_url": "local",
                        "chat_model_name": "models/Qwen3-4B",
                        "embedding_model_name": "models/bge-m3",
                    }
                ),
                encoding="utf-8",
            )

            config = load_runtime_config(path)

            self.assertEqual("auto", config.device)
            self.assertEqual("float16", config.torch_dtype)
            self.assertEqual(128, config.max_new_tokens)
            self.assertIsNone(config.adapter_path)
            self.assertIsNone(config.rag_system_prompt)

    def test_runtime_config_path_can_come_from_environment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(
                json.dumps(
                    {
                        "provider": "local_transformers",
                        "api_key": "local",
                        "base_url": "local",
                        "chat_model_name": "models/Qwen3-4B",
                        "embedding_model_name": "models/bge-m3",
                    }
                ),
                encoding="utf-8",
            )

            with unittest.mock.patch.dict("os.environ", {"LOCALRAG_RUNTIME_CONFIG": str(path)}):
                config = load_runtime_config()

            self.assertEqual("local_transformers", config.provider)

    def test_missing_file_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"

            with self.assertRaisesRegex(RuntimeError, r"Missing required runtime config file"):
                load_runtime_config(path)

    def test_invalid_json_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text("{not json}", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, r"Malformed runtime config file"):
                load_runtime_config(path)

    def test_non_object_json_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, r"Malformed runtime config file"):
                load_runtime_config(path)

    def test_missing_provider_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(
                json.dumps(
                    {
                        "api_key": "api-key",
                        "base_url": "https://example.com/v1",
                        "chat_model_name": "qwen-max",
                        "embedding_model_name": "text-embedding-v4",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, r"Missing required runtime config field: provider"):
                load_runtime_config(path)

    def test_unsupported_provider_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(
                json.dumps(
                    {
                        "provider": "custom",
                        "api_key": "api-key",
                        "base_url": "https://example.com/v1",
                        "chat_model_name": "qwen-max",
                        "embedding_model_name": "text-embedding-v4",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, r"Unsupported runtime provider: custom"):
                load_runtime_config(path)

    def test_missing_embedding_model_name_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(
                json.dumps(
                    {
                        "provider": "modelscope",
                        "api_key": "api-key",
                        "base_url": "https://example.com/v1",
                        "chat_model_name": "qwen-max",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                RuntimeError, r"Missing required runtime config field: embedding_model_name"
            ):
                load_runtime_config(path)

    def test_empty_api_key_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "runtime_models.json"
            path.write_text(
                json.dumps(
                    {
                        "provider": "modelscope",
                        "api_key": "   ",
                        "base_url": "https://example.com/v1",
                        "chat_model_name": "qwen-max",
                        "embedding_model_name": "text-embedding-v4",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                RuntimeError, r"Empty required runtime config field: api_key"
            ):
                load_runtime_config(path)


if __name__ == "__main__":
    unittest.main()
