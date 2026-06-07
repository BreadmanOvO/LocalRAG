import json
import tempfile
import unittest
import unittest.mock
from pathlib import Path

from config.runtime_keys import RuntimeProviderConfig, load_runtime_config


class RuntimeKeysTests(unittest.TestCase):
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
