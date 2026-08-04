from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any


MANIFEST_CONTRACT_VERSION = "localrag-model-manifest-v1"
BASE_MODEL_PATH = "models/Qwen3-4B"
ADAPTER_PATH = (
    "saves/Qwen3-4B-Thinking/lora/localrag_sft_e6_1_qlora_webui"
)
FIXED_TARGET_MODULES = frozenset(
    {"q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"}
)
FIXED_MODEL_INPUT_PATHS = (
    f"{BASE_MODEL_PATH}/model-00001-of-00003.safetensors",
    f"{BASE_MODEL_PATH}/model-00002-of-00003.safetensors",
    f"{BASE_MODEL_PATH}/model-00003-of-00003.safetensors",
    f"{BASE_MODEL_PATH}/model.safetensors.index.json",
    f"{BASE_MODEL_PATH}/config.json",
    f"{BASE_MODEL_PATH}/generation_config.json",
    f"{BASE_MODEL_PATH}/tokenizer_config.json",
    f"{BASE_MODEL_PATH}/tokenizer.json",
    f"{BASE_MODEL_PATH}/vocab.json",
    f"{BASE_MODEL_PATH}/merges.txt",
    f"{ADAPTER_PATH}/adapter_model.safetensors",
    f"{ADAPTER_PATH}/adapter_config.json",
    f"{ADAPTER_PATH}/chat_template.jinja",
    f"{ADAPTER_PATH}/tokenizer_config.json",
)
_MANIFEST_FIELDS = frozenset({"contract_version", "kind", "files", "metadata"})
_FILE_FIELDS = frozenset({"path", "size", "sha256"})
_ARTIFACT_PROFILES = {
    "gguf_f16": {
        "kind": "model-gguf-f16",
        "dtype": "float16",
        "quantization": "none",
        "input_kind": "model-merged-bf16",
    },
    "gguf_q4_k_m": {
        "kind": "model-gguf-q4-k-m",
        "dtype": "float16",
        "quantization": "Q4_K_M",
        "input_kind": "model-gguf-f16",
    },
}


class ManifestMismatchError(ValueError):
    pass


def sha256_file(path: Path, chunk_size: int = 1048576) -> str:
    path = Path(path)
    if type(chunk_size) is not int or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(chunk_size):
                digest.update(chunk)
    except OSError as exc:
        raise ManifestMismatchError(f"cannot read manifest artifact: {path.name}") from exc
    return digest.hexdigest()


def _portable_relative_path(repo_root: Path, value: object, field_name: str) -> tuple[str, Path]:
    if not isinstance(value, (str, Path)):
        raise ManifestMismatchError(f"{field_name} must be a relative path")
    text = str(value)
    if not text.strip():
        raise ManifestMismatchError(f"{field_name} must be a relative path")
    path = Path(text)
    if path.is_absolute() or PureWindowsPath(text).is_absolute():
        raise ManifestMismatchError(f"{field_name} must not be absolute")
    lexical = Path(os.path.abspath(repo_root / path))
    try:
        lexical.relative_to(repo_root)
    except ValueError:
        raise ManifestMismatchError(f"{field_name} escapes the repository") from None
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        portable = path.as_posix()
        approved = False
        for anchor in (BASE_MODEL_PATH, ADAPTER_PATH):
            if portable == anchor or portable.startswith(f"{anchor}/"):
                anchor_path = (repo_root / anchor).resolve()
                try:
                    resolved.relative_to(anchor_path)
                except ValueError:
                    continue
                approved = True
                break
        if not approved:
            raise ManifestMismatchError(f"{field_name} escapes the repository") from None
    return path.as_posix(), resolved


def build_manifest(
    repo_root: Path,
    relative_paths: Sequence[Path],
    kind: str,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    if not isinstance(kind, str) or not kind.strip():
        raise ManifestMismatchError("manifest kind must be a non-empty string")
    if isinstance(relative_paths, (str, bytes)) or not isinstance(
        relative_paths, Sequence
    ):
        raise ManifestMismatchError("relative_paths must be a sequence")

    resolved_rows: list[tuple[str, Path]] = []
    for index, relative_path in enumerate(relative_paths):
        portable, resolved = _portable_relative_path(
            repo_root, relative_path, f"relative_paths[{index}]"
        )
        if not resolved.is_file():
            raise ManifestMismatchError(f"manifest artifact is missing: {portable}")
        resolved_rows.append((portable, resolved))
    portable_paths = [portable for portable, _ in resolved_rows]
    if not portable_paths or len(portable_paths) != len(set(portable_paths)):
        raise ManifestMismatchError("manifest paths must be non-empty and unique")

    return {
        "contract_version": MANIFEST_CONTRACT_VERSION,
        "kind": kind.strip(),
        "files": [
            {
                "path": portable,
                "size": resolved.stat().st_size,
                "sha256": sha256_file(resolved),
            }
            for portable, resolved in sorted(resolved_rows)
        ],
        "metadata": {},
    }


def _validate_portable_path_fields(value: object, key: str = "") -> None:
    if isinstance(value, Mapping):
        for nested_key, nested in value.items():
            if not isinstance(nested_key, str):
                raise ManifestMismatchError("manifest object keys must be strings")
            _validate_portable_path_fields(nested, nested_key)
        return
    if isinstance(value, list):
        for item in value:
            _validate_portable_path_fields(item, key)
        return
    if key == "path" or key.endswith("_path"):
        if isinstance(value, str) and (
            Path(value).is_absolute() or PureWindowsPath(value).is_absolute()
        ):
            raise ManifestMismatchError("manifest contains an absolute machine path")


def write_manifest(path: Path, payload: Mapping[str, object]) -> None:
    if not isinstance(payload, Mapping):
        raise TypeError("payload must be a mapping")
    _validate_portable_path_fields(payload)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(payload), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestMismatchError("manifest is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ManifestMismatchError("manifest must be an object")
    return payload


def validate_manifest(repo_root: Path, payload: Mapping[str, object]) -> None:
    repo_root = Path(repo_root).resolve()
    if not isinstance(payload, Mapping) or set(payload) != _MANIFEST_FIELDS:
        raise ManifestMismatchError("manifest fields do not match the contract")
    if payload["contract_version"] != MANIFEST_CONTRACT_VERSION:
        raise ManifestMismatchError("manifest contract version is invalid")
    if not isinstance(payload["kind"], str) or not str(payload["kind"]).strip():
        raise ManifestMismatchError("manifest kind is invalid")
    if not isinstance(payload["metadata"], Mapping):
        raise ManifestMismatchError("manifest metadata must be an object")
    _validate_portable_path_fields(payload)

    files = payload["files"]
    if not isinstance(files, list) or not files:
        raise ManifestMismatchError("manifest files must be a non-empty list")
    observed_paths: list[str] = []
    for index, raw_row in enumerate(files):
        if not isinstance(raw_row, Mapping) or set(raw_row) != _FILE_FIELDS:
            raise ManifestMismatchError("manifest file record is invalid")
        portable, resolved = _portable_relative_path(
            repo_root, raw_row["path"], f"files[{index}].path"
        )
        observed_paths.append(portable)
        if not resolved.is_file():
            raise ManifestMismatchError(f"manifest artifact is missing: {portable}")
        size = raw_row["size"]
        sha256 = raw_row["sha256"]
        if type(size) is not int or size < 0:
            raise ManifestMismatchError("manifest file size is invalid")
        if (
            not isinstance(sha256, str)
            or len(sha256) != 64
            or any(character not in "0123456789abcdef" for character in sha256)
        ):
            raise ManifestMismatchError("manifest SHA-256 is invalid")
        if resolved.stat().st_size != size or sha256_file(resolved) != sha256:
            raise ManifestMismatchError(f"manifest artifact changed: {portable}")
    if observed_paths != sorted(observed_paths) or len(observed_paths) != len(
        set(observed_paths)
    ):
        raise ManifestMismatchError("manifest file paths must be sorted and unique")


def _read_json_object(path: Path, field_name: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestMismatchError(f"{field_name} is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ManifestMismatchError(f"{field_name} must be an object")
    return payload


def validate_fixed_model_identity(repo_root: Path) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    missing = [
        relative_path
        for relative_path in FIXED_MODEL_INPUT_PATHS
        if not (repo_root / relative_path).is_file()
    ]
    if missing:
        raise ManifestMismatchError(f"fixed model input is missing: {missing[0]}")

    model_config = _read_json_object(
        repo_root / BASE_MODEL_PATH / "config.json", "model config"
    )
    adapter_config = _read_json_object(
        repo_root / ADAPTER_PATH / "adapter_config.json", "adapter config"
    )
    if model_config.get("architectures") != ["Qwen3ForCausalLM"]:
        raise ManifestMismatchError("model architecture is not Qwen3ForCausalLM")
    if model_config.get("max_position_embeddings") != 40960:
        raise ManifestMismatchError("model context limit is not 40960")
    if adapter_config.get("base_model_name_or_path") != BASE_MODEL_PATH:
        raise ManifestMismatchError("adapter base model path is invalid")
    if adapter_config.get("peft_type") != "LORA":
        raise ManifestMismatchError("adapter type is not LoRA")
    if type(adapter_config.get("r")) is not int or adapter_config["r"] != 8:
        raise ManifestMismatchError("adapter rank is not 8")
    if adapter_config.get("lora_alpha") != 16:
        raise ManifestMismatchError("adapter alpha is not 16")
    if adapter_config.get("lora_dropout") != 0:
        raise ManifestMismatchError("adapter dropout is not 0")
    target_modules = adapter_config.get("target_modules")
    if (
        not isinstance(target_modules, list)
        or len(target_modules) != len(set(target_modules))
        or set(target_modules) != FIXED_TARGET_MODULES
    ):
        raise ManifestMismatchError("adapter target modules do not match E6.1")
    return {
        "model_id": "localrag-qwen3-4b-e6.1",
        "architecture": "Qwen3ForCausalLM",
        "context_limit": 40960,
        "base_model_path": BASE_MODEL_PATH,
        "adapter_path": ADAPTER_PATH,
        "adapter": {
            "type": "LORA",
            "r": 8,
            "alpha": 16,
            "dropout": 0,
            "target_modules": sorted(FIXED_TARGET_MODULES),
        },
    }


def build_derived_artifact_manifest(
    *,
    repo_root: Path,
    artifact: Path,
    artifact_profile: str,
    input_manifest: Path,
    tool_version: str,
    elapsed_seconds: float,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    if artifact_profile not in _ARTIFACT_PROFILES:
        raise ManifestMismatchError("artifact profile is invalid")
    if not isinstance(tool_version, str) or not tool_version.strip():
        raise ManifestMismatchError("tool version is invalid")
    if not isinstance(elapsed_seconds, (int, float)) or elapsed_seconds < 0:
        raise ManifestMismatchError("elapsed seconds is invalid")
    artifact_portable, artifact_path = _portable_relative_path(
        repo_root, artifact, "artifact"
    )
    if artifact_path.suffix.lower() != ".gguf" or not artifact_path.is_file():
        raise ManifestMismatchError("artifact must be an existing GGUF file")
    input_portable, input_path = _portable_relative_path(
        repo_root, input_manifest, "input_manifest"
    )
    input_payload = load_manifest(input_path)
    validate_manifest(repo_root, input_payload)
    profile = _ARTIFACT_PROFILES[artifact_profile]
    if input_payload.get("kind") != profile["input_kind"]:
        raise ManifestMismatchError("artifact input manifest kind is invalid")
    input_metadata = input_payload.get("metadata")
    input_identity = (
        input_metadata.get("model_identity")
        if isinstance(input_metadata, Mapping)
        else None
    )
    if (
        not isinstance(input_identity, Mapping)
        or input_identity.get("model_id") != "localrag-qwen3-4b-e6.1"
        or input_identity.get("architecture") != "Qwen3ForCausalLM"
        or input_identity.get("context_limit") != 40960
    ):
        raise ManifestMismatchError("artifact input identity is invalid")

    manifest = build_manifest(
        repo_root,
        [Path(artifact_portable)],
        kind=str(profile["kind"]),
    )
    manifest["metadata"] = {
        "model_identity": {
            "model_id": "localrag-qwen3-4b-e6.1",
            "architecture": "Qwen3ForCausalLM",
            "context_limit": 40960,
            "dtype": profile["dtype"],
            "quantization": profile["quantization"],
            "artifact_path": artifact_portable,
        },
        "input_manifest_path": input_portable,
        "input_manifest_sha256": sha256_file(input_path),
        "tool": {
            "name": "llama.cpp",
            "version": tool_version.strip(),
        },
        "build": {
            "artifact_profile": artifact_profile,
            "elapsed_seconds": round(float(elapsed_seconds), 3),
        },
    }
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build or verify model manifests.")
    parser.add_argument("--repo-root", type=Path, required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--out", type=Path)
    action.add_argument("--verify", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--artifact-profile", choices=tuple(_ARTIFACT_PROFILES))
    parser.add_argument("--input-manifest", type=Path)
    parser.add_argument("--tool-version")
    parser.add_argument("--elapsed-seconds", type=float)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    repo_root = args.repo_root.resolve()
    if args.out is not None:
        artifact_values = (
            args.artifact,
            args.artifact_profile,
            args.input_manifest,
            args.tool_version,
            args.elapsed_seconds,
        )
        if any(value is not None for value in artifact_values):
            if any(value is None for value in artifact_values):
                raise ManifestMismatchError("artifact manifest arguments are incomplete")
            manifest = build_derived_artifact_manifest(
                repo_root=repo_root,
                artifact=args.artifact,
                artifact_profile=args.artifact_profile,
                input_manifest=args.input_manifest,
                tool_version=args.tool_version,
                elapsed_seconds=args.elapsed_seconds,
            )
        else:
            identity = validate_fixed_model_identity(repo_root)
            manifest = build_manifest(
                repo_root,
                [Path(path) for path in FIXED_MODEL_INPUT_PATHS],
                kind="model-input",
            )
            manifest["metadata"] = {"model_identity": identity}
        write_manifest(args.out, manifest)
        validate_manifest(repo_root, manifest)
        print("model_identity=valid")
        print(f"files={len(manifest['files'])}")
        print(f"manifest_path={args.out}")
        return

    manifest = load_manifest(args.verify)
    validate_manifest(repo_root, manifest)
    if manifest.get("kind") == "model-input":
        identity = validate_fixed_model_identity(repo_root)
        metadata = manifest.get("metadata")
        if not isinstance(metadata, Mapping) or metadata.get("model_identity") != identity:
            raise ManifestMismatchError("manifest model identity does not match local inputs")
    print("model_identity=valid")
    print(f"files={len(manifest['files'])}")
    print(f"kind={manifest['kind']}")
    print("manifest_valid=true")


if __name__ == "__main__":
    main()
