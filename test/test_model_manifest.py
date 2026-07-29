from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from model_deployment.manifest import (
    FIXED_MODEL_INPUT_PATHS,
    ManifestMismatchError,
    build_manifest,
    load_manifest,
    sha256_file,
    validate_fixed_model_identity,
    validate_manifest,
    write_manifest,
)


class ModelManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name).resolve()

    def _write(self, relative_path: str, content: str = "fixture") -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _fixed_identity_fixture(self) -> None:
        for relative_path in FIXED_MODEL_INPUT_PATHS:
            self._write(relative_path)
        self._write(
            "models/Qwen3-4B/config.json",
            json.dumps(
                {
                    "architectures": ["Qwen3ForCausalLM"],
                    "max_position_embeddings": 40960,
                }
            ),
        )
        self._write(
            (
                "saves/Qwen3-4B-Thinking/lora/"
                "localrag_sft_e6_1_qlora_webui/adapter_config.json"
            ),
            json.dumps(
                {
                    "base_model_name_or_path": "models/Qwen3-4B",
                    "peft_type": "LORA",
                    "r": 8,
                    "lora_alpha": 16,
                    "lora_dropout": 0,
                    "target_modules": [
                        "q_proj",
                        "k_proj",
                        "v_proj",
                        "o_proj",
                        "gate_proj",
                        "up_proj",
                        "down_proj",
                    ],
                }
            ),
        )

    def test_hash_manifest_is_stable_relative_and_sorted(self):
        beta = self._write("nested/beta.bin", "beta")
        alpha = self._write("alpha.bin", "alpha")

        manifest = build_manifest(
            self.root,
            [Path("nested/beta.bin"), Path("alpha.bin")],
            kind="model-input",
        )

        self.assertEqual(hashlib.sha256(b"alpha").hexdigest(), sha256_file(alpha))
        self.assertEqual(
            ["alpha.bin", "nested/beta.bin"],
            [row["path"] for row in manifest["files"]],
        )
        self.assertEqual(
            [alpha.stat().st_size, beta.stat().st_size],
            [row["size"] for row in manifest["files"]],
        )
        self.assertNotIn(str(self.root), json.dumps(manifest))
        validate_manifest(self.root, manifest)

    def test_validate_manifest_detects_changed_artifact(self):
        self._write("config.json", '{"original": true}')
        manifest = build_manifest(
            self.root, [Path("config.json")], kind="model-input"
        )
        self._write("config.json", '{"changed": true}')

        with self.assertRaises(ManifestMismatchError):
            validate_manifest(self.root, manifest)

    def test_missing_and_escaping_files_fail_closed(self):
        for relative_path in (Path("missing.bin"), Path("../outside.bin")):
            with self.subTest(path=relative_path), self.assertRaises(
                ManifestMismatchError
            ):
                build_manifest(self.root, [relative_path], kind="model-input")

    def test_manifest_round_trip_rejects_absolute_machine_paths(self):
        self._write("artifact.bin")
        manifest = build_manifest(
            self.root, [Path("artifact.bin")], kind="model-input"
        )
        output = self.root / "manifest.json"
        write_manifest(output, manifest)

        loaded = load_manifest(output)

        self.assertEqual(manifest, loaded)
        loaded["files"][0]["path"] = str((self.root / "artifact.bin").resolve())
        with self.assertRaises(ManifestMismatchError):
            validate_manifest(self.root, loaded)

    def test_fixed_model_identity_and_input_file_set(self):
        self._fixed_identity_fixture()

        identity = validate_fixed_model_identity(self.root)

        self.assertEqual("Qwen3ForCausalLM", identity["architecture"])
        self.assertEqual(40960, identity["context_limit"])
        self.assertEqual(8, identity["adapter"]["r"])
        self.assertEqual(16, identity["adapter"]["alpha"])
        self.assertEqual(0, identity["adapter"]["dropout"])
        self.assertEqual(7, len(identity["adapter"]["target_modules"]))
        self.assertEqual(14, len(FIXED_MODEL_INPUT_PATHS))

    def test_fixed_identity_rejects_config_drift_and_missing_input(self):
        mutations = (
            ("model", "architectures", ["OtherModel"]),
            ("model", "max_position_embeddings", 8192),
            ("adapter", "base_model_name_or_path", "models/Other"),
            ("adapter", "r", 16),
            ("adapter", "lora_alpha", 32),
            ("adapter", "lora_dropout", 0.1),
            ("adapter", "target_modules", ["q_proj"]),
        )
        for scope, field, value in mutations:
            with self.subTest(scope=scope, field=field):
                self._fixed_identity_fixture()
                relative = (
                    "models/Qwen3-4B/config.json"
                    if scope == "model"
                    else (
                        "saves/Qwen3-4B-Thinking/lora/"
                        "localrag_sft_e6_1_qlora_webui/adapter_config.json"
                    )
                )
                payload = json.loads((self.root / relative).read_text(encoding="utf-8"))
                payload[field] = value
                (self.root / relative).write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(ManifestMismatchError):
                    validate_fixed_model_identity(self.root)

        self._fixed_identity_fixture()
        (self.root / FIXED_MODEL_INPUT_PATHS[-1]).unlink()
        with self.assertRaises(ManifestMismatchError):
            validate_fixed_model_identity(self.root)


if __name__ == "__main__":
    unittest.main()
