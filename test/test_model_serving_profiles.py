from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from model_serving.profiles import ProfileValidationError, load_profiles


def _profile_payload() -> dict:
    return {
        "contract_version": "localrag-model-profile-v1",
        "profiles": {
            "e6_1_adapter_bf16": {
                "model_id": "localrag-qwen3-4b-e6.1",
                "backend": "transformers",
                "base_model_path": "models/Qwen3-4B",
                "adapter_path": (
                    "saves/Qwen3-4B-Thinking/lora/"
                    "localrag_sft_e6_1_qlora_webui"
                ),
                "artifact_path": None,
                "dtype": "bfloat16",
                "quantization": "none",
                "context_limit": 40960,
                "max_new_tokens": 1024,
                "enable_thinking": False,
                "manifest_path": (
                    "model_deployment/manifests/e6_1_input_manifest.json"
                ),
            },
            "e6_1_q4_k_m": {
                "model_id": "localrag-qwen3-4b-e6.1",
                "backend": "llama_cpp",
                "base_model_path": None,
                "adapter_path": None,
                "artifact_path": (
                    "artifacts/models/qwen3-4b-e6.1-q4_k_m.gguf"
                ),
                "dtype": "float16",
                "quantization": "Q4_K_M",
                "context_limit": 40960,
                "max_new_tokens": 1024,
                "enable_thinking": False,
                "manifest_path": (
                    "model_deployment/manifests/e6_1_q4_k_m_manifest.json"
                ),
            },
        },
    }


class ModelServingProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.repo_root = Path(self.temp_dir.name).resolve()
        self.profile_path = self.repo_root / "profiles.json"

    def _write(self, payload: dict) -> None:
        self.profile_path.write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    def test_release_profiles_keep_fixed_e6_1_identity(self):
        self._write(_profile_payload())

        profiles = load_profiles(self.profile_path, repo_root=self.repo_root)
        bf16 = profiles.require("e6_1_adapter_bf16")
        q4 = profiles.require("e6_1_q4_k_m")

        self.assertEqual("models/Qwen3-4B", bf16.base_model_path)
        self.assertTrue(
            bf16.adapter_path.endswith("localrag_sft_e6_1_qlora_webui")
        )
        self.assertEqual("bfloat16", bf16.dtype)
        self.assertEqual(40960, bf16.context_limit)
        self.assertEqual("Q4_K_M", q4.quantization)
        self.assertEqual(bf16.model_id, q4.model_id)
        self.assertFalse(bf16.enable_thinking)
        self.assertFalse(q4.enable_thinking)
        with self.assertRaises(ProfileValidationError):
            profiles.require("missing")

    def test_top_level_and_profile_fields_are_exact(self):
        for mutation in ("top", "profile"):
            payload = _profile_payload()
            if mutation == "top":
                payload["unknown"] = True
            else:
                payload["profiles"]["e6_1_adapter_bf16"]["unknown"] = True
            self._write(payload)

            with self.subTest(mutation=mutation), self.assertRaises(
                ProfileValidationError
            ):
                load_profiles(self.profile_path, repo_root=self.repo_root)

    def test_profile_set_is_fixed(self):
        for mutation in ("missing", "extra"):
            payload = _profile_payload()
            if mutation == "missing":
                del payload["profiles"]["e6_1_q4_k_m"]
            else:
                payload["profiles"]["unexpected"] = copy.deepcopy(
                    payload["profiles"]["e6_1_q4_k_m"]
                )
            self._write(payload)

            with self.subTest(mutation=mutation), self.assertRaises(
                ProfileValidationError
            ):
                load_profiles(self.profile_path, repo_root=self.repo_root)

    def test_paths_must_be_repo_relative_and_cannot_escape(self):
        invalid_paths = ("../outside", str((self.repo_root / "absolute").resolve()))
        for invalid_path in invalid_paths:
            payload = _profile_payload()
            payload["profiles"]["e6_1_adapter_bf16"][
                "base_model_path"
            ] = invalid_path
            self._write(payload)

            with self.subTest(path=invalid_path), self.assertRaises(
                ProfileValidationError
            ):
                load_profiles(self.profile_path, repo_root=self.repo_root)

    def test_context_thinking_and_backend_identity_fail_closed(self):
        mutations = {
            "context": ("e6_1_adapter_bf16", "context_limit", 40961),
            "thinking": ("e6_1_q4_k_m", "enable_thinking", True),
            "dtype": ("e6_1_adapter_bf16", "dtype", "float16"),
            "quantization": ("e6_1_q4_k_m", "quantization", "Q4_0"),
            "artifact": (
                "e6_1_q4_k_m",
                "artifact_path",
                "artifacts/models/not-gguf.bin",
            ),
        }
        for name, (profile_name, field, value) in mutations.items():
            payload = _profile_payload()
            payload["profiles"][profile_name][field] = value
            self._write(payload)

            with self.subTest(name=name), self.assertRaises(
                ProfileValidationError
            ):
                load_profiles(self.profile_path, repo_root=self.repo_root)


if __name__ == "__main__":
    unittest.main()
