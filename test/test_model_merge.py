from __future__ import annotations

from contextlib import ExitStack
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import torch

from model_deployment.manifest import ManifestMismatchError, load_manifest
from model_deployment.merge_adapter import ModelMergeError, merge_adapter
from model_deployment.verify_model import (
    ModelVerificationError,
    verify_saved_model_metadata,
)


IDENTITY = {
    "model_id": "localrag-qwen3-4b-e6.1",
    "architecture": "Qwen3ForCausalLM",
    "context_limit": 40960,
}


class FakeParameter:
    dtype = torch.bfloat16

    def is_floating_point(self):
        return True


class ModelMergeTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name).resolve()
        self.base = self.root / "models/Qwen3-4B"
        self.adapter = self.root / (
            "saves/Qwen3-4B-Thinking/lora/localrag_sft_e6_1_qlora_webui"
        )
        self.base.mkdir(parents=True)
        self.adapter.mkdir(parents=True)
        (self.adapter / "chat_template.jinja").write_text(
            "{{ messages }}",
            encoding="utf-8",
        )
        self.input_manifest = (
            self.root / "model_deployment/manifests/e6_1_input_manifest.json"
        )
        self.input_manifest.parent.mkdir(parents=True)
        self.input_manifest.write_text(
            json.dumps(
                {
                    "contract_version": "localrag-model-manifest-v1",
                    "kind": "model-input",
                    "files": [
                        {
                            "path": "fixture.bin",
                            "size": 1,
                            "sha256": "a" * 64,
                        }
                    ],
                    "metadata": {"model_identity": IDENTITY},
                }
            ),
            encoding="utf-8",
        )
        self.output = Path("artifacts/models/qwen3-4b-e6.1-merged-bf16")
        self.output_manifest = Path(
            "model_deployment/manifests/e6_1_merged_bf16_manifest.json"
        )

        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(
            mock.patch("model_deployment.merge_adapter.validate_manifest")
        )
        self.stack.enter_context(
            mock.patch(
                "model_deployment.merge_adapter.validate_fixed_model_identity",
                return_value=IDENTITY,
            )
        )
        self.tokenizer = mock.MagicMock()
        self.base_model = mock.MagicMock()
        self.adapter_model = mock.MagicMock()
        self.merged_model = mock.MagicMock()
        self.merged_model.parameters.return_value = [FakeParameter()]
        self.merged_model.config.architectures = ["Qwen3ForCausalLM"]
        self.merged_model.config.max_position_embeddings = 40960
        self.adapter_model.merge_and_unload.return_value = self.merged_model
        self.auto_tokenizer = self.stack.enter_context(
            mock.patch("model_deployment.merge_adapter.AutoTokenizer")
        )
        self.auto_tokenizer.from_pretrained.return_value = self.tokenizer
        self.auto_model = self.stack.enter_context(
            mock.patch("model_deployment.merge_adapter.AutoModelForCausalLM")
        )
        self.auto_model.from_pretrained.return_value = self.base_model
        self.peft_model = self.stack.enter_context(
            mock.patch("model_deployment.merge_adapter.PeftModel")
        )
        self.peft_model.from_pretrained.return_value = self.adapter_model
        self.stack.enter_context(
            mock.patch(
                "model_deployment.merge_adapter.verify_saved_model_metadata",
                return_value={
                    "architecture": "Qwen3ForCausalLM",
                    "context_limit": 40960,
                    "chat_template": "valid",
                },
            )
        )

        def save_model(path, **kwargs):
            path.mkdir(parents=True, exist_ok=True)
            (path / "model.safetensors").write_bytes(b"model")
            (path / "config.json").write_text("{}", encoding="utf-8")

        def save_tokenizer(path):
            (path / "tokenizer.json").write_text("{}", encoding="utf-8")

        self.merged_model.save_pretrained.side_effect = save_model
        self.tokenizer.save_pretrained.side_effect = save_tokenizer

    def _merge(self, **overrides):
        values = {
            "repo_root": self.root,
            "base": Path("models/Qwen3-4B"),
            "adapter": Path(
                "saves/Qwen3-4B-Thinking/lora/localrag_sft_e6_1_qlora_webui"
            ),
            "input_manifest": Path(
                "model_deployment/manifests/e6_1_input_manifest.json"
            ),
            "output": self.output,
            "output_manifest": self.output_manifest,
        }
        values.update(overrides)
        return merge_adapter(**values)

    def test_merge_uses_bf16_safe_merge_and_writes_manifest(self):
        result = self._merge()

        self.auto_model.from_pretrained.assert_called_once_with(
            self.base.resolve(),
            dtype=torch.bfloat16,
            local_files_only=True,
            trust_remote_code=False,
            low_cpu_mem_usage=True,
        )
        self.peft_model.from_pretrained.assert_called_once_with(
            self.base_model,
            self.adapter.resolve(),
            local_files_only=True,
            is_trainable=False,
        )
        self.adapter_model.merge_and_unload.assert_called_once_with(safe_merge=True)
        self.merged_model.save_pretrained.assert_called_once_with(
            self.root / self.output,
            safe_serialization=True,
            max_shard_size="4GB",
        )
        manifest = load_manifest(self.root / self.output_manifest)
        self.assertEqual("model-merged-bf16", manifest["kind"])
        self.assertEqual("bfloat16", manifest["metadata"]["model_identity"]["dtype"])
        self.assertTrue(manifest["metadata"]["merge"]["safe_merge"])
        self.assertNotIn(str(self.root), json.dumps(manifest))
        self.assertEqual("bfloat16", result["dtype"])

    def test_invalid_manifest_fails_before_model_loading(self):
        validator = self.stack.enter_context(
            mock.patch(
                "model_deployment.merge_adapter.validate_manifest",
                side_effect=ManifestMismatchError("changed"),
            )
        )

        with self.assertRaises(ManifestMismatchError):
            self._merge()

        validator.assert_called_once()
        self.auto_model.from_pretrained.assert_not_called()

    def test_existing_output_requires_explicit_empty_override(self):
        output = self.root / self.output
        output.mkdir(parents=True)

        with self.assertRaises(ModelMergeError):
            self._merge()

        result = self._merge(overwrite_empty=True)
        self.assertEqual("Qwen3ForCausalLM", result["architecture"])

    def test_non_bf16_parameters_fail_closed(self):
        parameter = FakeParameter()
        parameter.dtype = torch.float32
        self.merged_model.parameters.return_value = [parameter]

        with self.assertRaises(ModelMergeError):
            self._merge()

    def test_paths_are_fixed_and_outputs_stay_in_build_roots(self):
        invalid = (
            {"base": Path("models/Other")},
            {"adapter": Path("saves/Other")},
            {"output": Path("outside/model")},
            {"output_manifest": Path("outside.json")},
        )
        for overrides in invalid:
            with self.subTest(overrides=overrides), self.assertRaises(ModelMergeError):
                self._merge(**overrides)


class ModelMetadataVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.model = Path(self.temp_dir.name)
        (self.model / "chat_template.jinja").write_text(
            "{{ messages }}",
            encoding="utf-8",
        )

    @mock.patch("model_deployment.verify_model.AutoTokenizer")
    @mock.patch("model_deployment.verify_model.AutoConfig")
    def test_saved_metadata_requires_identity_and_template(self, auto_config, tokenizer):
        auto_config.from_pretrained.return_value.architectures = [
            "Qwen3ForCausalLM"
        ]
        auto_config.from_pretrained.return_value.max_position_embeddings = 40960
        tokenizer.from_pretrained.return_value.chat_template = "{{ messages }}"

        result = verify_saved_model_metadata(self.model)

        self.assertEqual("Qwen3ForCausalLM", result["architecture"])
        self.assertEqual("valid", result["chat_template"])

    @mock.patch("model_deployment.verify_model.AutoTokenizer")
    @mock.patch("model_deployment.verify_model.AutoConfig")
    def test_saved_metadata_rejects_identity_drift(self, auto_config, tokenizer):
        auto_config.from_pretrained.return_value.architectures = ["OtherModel"]
        auto_config.from_pretrained.return_value.max_position_embeddings = 40960
        tokenizer.from_pretrained.return_value.chat_template = "{{ messages }}"

        with self.assertRaises(ModelVerificationError):
            verify_saved_model_metadata(self.model)


if __name__ == "__main__":
    unittest.main()
