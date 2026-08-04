from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from config.runtime_keys import LOCAL_MODEL_ID, load_runtime_config


class LocalModelConfigTests(unittest.TestCase):
    def _write_config(self, directory: str, local_config: object) -> Path:
        path = Path(directory) / "runtime.json"
        payload = {
            "provider": "modelscope",
            "api_key": "cloud-key",
            "base_url": "https://example.invalid/v1",
            "chat_model_name": "cloud-chat",
            "embedding_model_name": "local-embedding",
            "local_model_gateway": local_config,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    @staticmethod
    def _valid_local_config() -> dict[str, object]:
        return {
            "base_url": "http://127.0.0.1:8002/v1",
            "model": LOCAL_MODEL_ID,
            "api_token_env": "LOCALRAG_MODEL_API_TOKEN",
            "rag_generation_enabled": True,
            "conversation_summary_enabled": True,
            "connect_timeout_seconds": 2.0,
            "read_timeout_seconds": 120.0,
            "circuit_failure_threshold": 3,
            "circuit_reset_seconds": 30.0,
        }

    def test_valid_config_reads_local_token_from_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(directory, self._valid_local_config())
            config = load_runtime_config(
                path,
                environ={"LOCALRAG_MODEL_API_TOKEN": "secret"},
            )

        local = config.local_model_gateway
        self.assertIsNotNone(local)
        assert local is not None
        self.assertEqual("http://127.0.0.1:8002/v1", local.base_url)
        self.assertEqual(LOCAL_MODEL_ID, local.model)
        self.assertEqual("secret", local.api_token)
        self.assertTrue(local.rag_generation_enabled)
        self.assertTrue(local.conversation_summary_enabled)

    def test_missing_local_section_is_backward_compatible(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(directory, None)
            config = load_runtime_config(path, environ={})

        self.assertIsNone(config.local_model_gateway)

    def test_local_config_rejects_invalid_or_secret_bearing_fields(self):
        invalid_values = (
            ("base_url", "https://example.com/v1"),
            ("base_url", "http://127.0.0.1:8002/not-v1"),
            ("model", "other-model"),
            ("rag_generation_enabled", 1),
            ("conversation_summary_enabled", "true"),
            ("connect_timeout_seconds", 0),
            ("read_timeout_seconds", float("inf")),
            ("circuit_failure_threshold", True),
            ("circuit_reset_seconds", -1),
            ("api_token", "must-not-be-in-json"),
            ("unknown", "value"),
        )
        for field, value in invalid_values:
            with self.subTest(field=field, value=value):
                local = self._valid_local_config()
                local[field] = value
                with tempfile.TemporaryDirectory() as directory:
                    path = self._write_config(directory, local)
                    with self.assertRaises(RuntimeError):
                        load_runtime_config(
                            path,
                            environ={"LOCALRAG_MODEL_API_TOKEN": "secret"},
                        )

    def test_missing_token_names_variable_without_leaking_other_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_config(directory, self._valid_local_config())
            with self.assertRaises(RuntimeError) as raised:
                load_runtime_config(path, environ={"OTHER_SECRET": "do-not-leak"})

        message = str(raised.exception)
        self.assertIn("LOCALRAG_MODEL_API_TOKEN", message)
        self.assertNotIn("do-not-leak", message)


if __name__ == "__main__":
    unittest.main()
