import json
import tempfile
import unittest
from pathlib import Path

from runtime_keys import BailianRuntimeConfig, load_bailian_runtime_config


class BailianRuntimeKeysTests(unittest.TestCase):
    def test_successfully_parses_all_required_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "key.json"
            path.write_text(
                json.dumps(
                    {
                        "dashscope_api_key": "  api-key  ",
                        "dashscope_base_url": " https://example.com/v1 ",
                        "chat_model_name": " gpt-5.4 ",
                        "embedding_model_name": " text-embedding-v4 ",
                    }
                ),
                encoding="utf-8",
            )

            config = load_bailian_runtime_config(path)

            self.assertEqual(
                BailianRuntimeConfig(
                    dashscope_api_key="api-key",
                    dashscope_base_url="https://example.com/v1",
                    chat_model_name="gpt-5.4",
                    embedding_model_name="text-embedding-v4",
                ),
                config,
            )

    def test_missing_file_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "key.json"

            with self.assertRaisesRegex(RuntimeError, r"Missing required root key\.json file"):
                load_bailian_runtime_config(path)

    def test_invalid_json_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "key.json"
            path.write_text("{not json}", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, r"Malformed key\.json"):
                load_bailian_runtime_config(path)

    def test_non_object_json_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "key.json"
            path.write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, r"Malformed key\.json"):
                load_bailian_runtime_config(path)

    def test_missing_embedding_model_name_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "key.json"
            path.write_text(
                json.dumps(
                    {
                        "dashscope_api_key": "api-key",
                        "dashscope_base_url": "https://example.com/v1",
                        "chat_model_name": "gpt-5.4",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                RuntimeError, r"Missing required key\.json field: embedding_model_name"
            ):
                load_bailian_runtime_config(path)

    def test_empty_dashscope_api_key_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "key.json"
            path.write_text(
                json.dumps(
                    {
                        "dashscope_api_key": "   ",
                        "dashscope_base_url": "https://example.com/v1",
                        "chat_model_name": "gpt-5.4",
                        "embedding_model_name": "text-embedding-v4",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                RuntimeError, r"Empty required key\.json field: dashscope_api_key"
            ):
                load_bailian_runtime_config(path)

    def test_non_string_dashscope_api_key_raises_runtime_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "key.json"
            path.write_text(
                json.dumps(
                    {
                        "dashscope_api_key": 123,
                        "dashscope_base_url": "https://example.com/v1",
                        "chat_model_name": "gpt-5.4",
                        "embedding_model_name": "text-embedding-v4",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                RuntimeError, r"Empty required key\.json field: dashscope_api_key"
            ):
                load_bailian_runtime_config(path)


if __name__ == "__main__":
    unittest.main()
