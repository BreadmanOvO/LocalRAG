from __future__ import annotations

import argparse
import importlib.metadata
import os
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

import peft
import torch
import transformers
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from .manifest import (
    ADAPTER_PATH,
    BASE_MODEL_PATH,
    ManifestMismatchError,
    build_manifest,
    load_manifest,
    sha256_file,
    validate_fixed_model_identity,
    validate_manifest,
    write_manifest,
)
from .verify_model import ModelVerificationError, verify_saved_model_metadata


REPO_ROOT = Path(__file__).resolve().parents[1]
MERGED_KIND = "model-merged-bf16"


class ModelMergeError(RuntimeError):
    pass


def _fixed_input_directory(
    repo_root: Path, value: Path, expected: str, field_name: str
) -> Path:
    text = str(value)
    path = Path(text)
    if path.is_absolute() or PureWindowsPath(text).is_absolute():
        raise ModelMergeError(f"{field_name} must be repository-relative")
    if path.as_posix() != expected:
        raise ModelMergeError(f"{field_name} does not match the fixed E6.1 identity")
    resolved = (repo_root / path).resolve()
    if not resolved.is_dir():
        raise ModelMergeError(f"{field_name} directory is missing")
    return resolved


def _repository_file(repo_root: Path, value: Path, field_name: str) -> Path:
    text = str(value)
    path = Path(text)
    if path.is_absolute() or PureWindowsPath(text).is_absolute():
        raise ModelMergeError(f"{field_name} must be repository-relative")
    lexical = Path(os.path.abspath(repo_root / path))
    try:
        lexical.relative_to(repo_root)
    except ValueError:
        raise ModelMergeError(f"{field_name} escapes the repository") from None
    if not lexical.is_file():
        raise ModelMergeError(f"{field_name} is missing")
    return lexical


def _output_directory(repo_root: Path, value: Path) -> tuple[str, Path]:
    text = str(value)
    path = Path(text)
    if path.is_absolute() or PureWindowsPath(text).is_absolute():
        raise ModelMergeError("output must be repository-relative")
    portable = path.as_posix()
    if not portable.startswith("artifacts/models/"):
        raise ModelMergeError("output must be inside artifacts/models")
    lexical = Path(os.path.abspath(repo_root / path))
    try:
        lexical.relative_to(repo_root / "artifacts" / "models")
    except ValueError:
        raise ModelMergeError("output escapes artifacts/models") from None
    return portable, lexical


def _output_manifest_path(repo_root: Path, value: Path) -> Path:
    text = str(value)
    path = Path(text)
    if path.is_absolute() or PureWindowsPath(text).is_absolute():
        raise ModelMergeError("output manifest must be repository-relative")
    lexical = Path(os.path.abspath(repo_root / path))
    manifests_root = repo_root / "model_deployment" / "manifests"
    try:
        lexical.relative_to(manifests_root)
    except ValueError:
        raise ModelMergeError("output manifest must be inside model_deployment/manifests") from None
    if lexical.suffix.lower() != ".json":
        raise ModelMergeError("output manifest must be JSON")
    return lexical


def _prepare_output(path: Path, *, overwrite_empty: bool) -> None:
    if path.exists():
        if not path.is_dir():
            raise ModelMergeError("output exists and is not a directory")
        if any(path.iterdir()) or not overwrite_empty:
            raise ModelMergeError("output directory already exists")
    else:
        path.mkdir(parents=True)


def _version(distribution: str, fallback: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return fallback


def merge_adapter(
    *,
    repo_root: Path,
    base: Path,
    adapter: Path,
    input_manifest: Path,
    output: Path,
    output_manifest: Path,
    overwrite_empty: bool = False,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    base_path = _fixed_input_directory(repo_root, base, BASE_MODEL_PATH, "base")
    adapter_path = _fixed_input_directory(
        repo_root, adapter, ADAPTER_PATH, "adapter"
    )
    input_manifest_path = _repository_file(
        repo_root, input_manifest, "input manifest"
    )
    output_portable, output_path = _output_directory(repo_root, output)
    output_manifest_path = _output_manifest_path(repo_root, output_manifest)
    if output_manifest_path.exists():
        raise ModelMergeError("output manifest already exists")

    input_payload = load_manifest(input_manifest_path)
    validate_manifest(repo_root, input_payload)
    identity = validate_fixed_model_identity(repo_root)
    metadata = input_payload.get("metadata")
    if not isinstance(metadata, Mapping) or metadata.get("model_identity") != identity:
        raise ManifestMismatchError("input manifest model identity is invalid")

    _prepare_output(output_path, overwrite_empty=overwrite_empty)
    chat_template_path = adapter_path / "chat_template.jinja"
    try:
        chat_template = chat_template_path.read_text(encoding="utf-8")
        tokenizer = AutoTokenizer.from_pretrained(
            base_path,
            local_files_only=True,
            trust_remote_code=False,
        )
        tokenizer.chat_template = chat_template
        base_model = AutoModelForCausalLM.from_pretrained(
            base_path,
            dtype=torch.bfloat16,
            local_files_only=True,
            trust_remote_code=False,
            low_cpu_mem_usage=True,
        )
        adapter_model = PeftModel.from_pretrained(
            base_model,
            adapter_path,
            local_files_only=True,
            is_trainable=False,
        )
        merged_model = adapter_model.merge_and_unload(safe_merge=True)
        floating_dtypes = {
            parameter.dtype
            for parameter in merged_model.parameters()
            if parameter.is_floating_point()
        }
        if floating_dtypes != {torch.bfloat16}:
            raise ModelMergeError("merged parameters are not uniformly bfloat16")
        config = merged_model.config
        if (
            getattr(config, "architectures", None) != ["Qwen3ForCausalLM"]
            or getattr(config, "max_position_embeddings", None) != 40960
        ):
            raise ModelMergeError("merged model identity changed")
        merged_model.save_pretrained(
            output_path,
            safe_serialization=True,
            max_shard_size="4GB",
        )
        tokenizer.save_pretrained(output_path)
        (output_path / "chat_template.jinja").write_text(
            chat_template,
            encoding="utf-8",
        )
        verified = verify_saved_model_metadata(output_path)
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise ModelMergeError("CUDA out of memory while merging adapter") from None
    except (OSError, RuntimeError, ValueError, ModelVerificationError) as exc:
        if isinstance(exc, ModelMergeError):
            raise
        raise ModelMergeError("adapter merge failed") from exc

    relative_files = [
        path.relative_to(repo_root)
        for path in output_path.rglob("*")
        if path.is_file()
    ]
    manifest = build_manifest(repo_root, relative_files, kind=MERGED_KIND)
    manifest["metadata"] = {
        "model_identity": {
            "model_id": identity["model_id"],
            "architecture": verified["architecture"],
            "context_limit": verified["context_limit"],
            "dtype": "bfloat16",
            "quantization": "none",
            "artifact_path": output_portable,
        },
        "input_manifest_path": Path(input_manifest).as_posix(),
        "input_manifest_sha256": sha256_file(input_manifest_path),
        "merge": {
            "safe_merge": True,
            "safe_serialization": True,
            "max_shard_size": "4GB",
        },
        "tool_versions": {
            "torch": torch.__version__,
            "transformers": _version("transformers", transformers.__version__),
            "peft": _version("peft", peft.__version__),
        },
    }
    write_manifest(output_manifest_path, manifest)
    validate_manifest(repo_root, manifest)
    return {
        "safe_merge": True,
        "dtype": "bfloat16",
        "architecture": verified["architecture"],
        "context_limit": verified["context_limit"],
        "files": len(manifest["files"]),
        "output": output_portable,
        "output_manifest": output_manifest_path.relative_to(repo_root).as_posix(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge the fixed E6.1 LoRA into BF16.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--overwrite-empty", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = merge_adapter(
        repo_root=args.repo_root,
        base=args.base,
        adapter=args.adapter,
        input_manifest=args.input_manifest,
        output=args.output,
        output_manifest=args.output_manifest,
        overwrite_empty=args.overwrite_empty,
    )
    for key in (
        "safe_merge",
        "dtype",
        "architecture",
        "context_limit",
        "files",
        "output",
        "output_manifest",
    ):
        print(f"{key}={result[key]}")


if __name__ == "__main__":
    main()
