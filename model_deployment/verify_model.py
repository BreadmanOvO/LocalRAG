from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import torch
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from .manifest import ManifestMismatchError, load_manifest, validate_manifest


EXPECTED_ARCHITECTURE = "Qwen3ForCausalLM"
EXPECTED_CONTEXT_LIMIT = 40960
EXPECTED_DTYPE = "bfloat16"


class ModelVerificationError(RuntimeError):
    pass


def verify_saved_model_metadata(model_path: Path) -> dict[str, Any]:
    model_path = Path(model_path)
    if not model_path.is_dir():
        raise ModelVerificationError("merged model directory is missing")
    chat_template_path = model_path / "chat_template.jinja"
    if not chat_template_path.is_file():
        raise ModelVerificationError("merged chat template is missing")
    try:
        chat_template = chat_template_path.read_text(encoding="utf-8")
        config = AutoConfig.from_pretrained(
            model_path,
            local_files_only=True,
            trust_remote_code=False,
        )
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True,
            trust_remote_code=False,
        )
    except (OSError, ValueError) as exc:
        raise ModelVerificationError("merged model metadata could not be loaded") from exc
    if getattr(config, "architectures", None) != [EXPECTED_ARCHITECTURE]:
        raise ModelVerificationError("merged model architecture is invalid")
    if getattr(config, "max_position_embeddings", None) != EXPECTED_CONTEXT_LIMIT:
        raise ModelVerificationError("merged model context limit is invalid")
    if not chat_template.strip() or getattr(tokenizer, "chat_template", None) != chat_template:
        raise ModelVerificationError("merged chat template is invalid")
    return {
        "architecture": EXPECTED_ARCHITECTURE,
        "context_limit": EXPECTED_CONTEXT_LIMIT,
        "chat_template": "valid",
    }


def _manifest_artifact_path(manifest: Mapping[str, object]) -> str:
    metadata = manifest.get("metadata")
    if not isinstance(metadata, Mapping):
        raise ModelVerificationError("merged manifest metadata is invalid")
    identity = metadata.get("model_identity")
    if not isinstance(identity, Mapping):
        raise ModelVerificationError("merged manifest identity is invalid")
    if (
        identity.get("model_id") != "localrag-qwen3-4b-e6.1"
        or identity.get("architecture") != EXPECTED_ARCHITECTURE
        or identity.get("context_limit") != EXPECTED_CONTEXT_LIMIT
        or identity.get("dtype") != EXPECTED_DTYPE
        or identity.get("quantization") != "none"
    ):
        raise ModelVerificationError("merged manifest identity does not match E6.1 BF16")
    artifact_path = identity.get("artifact_path")
    if not isinstance(artifact_path, str) or not artifact_path:
        raise ModelVerificationError("merged manifest artifact path is invalid")
    return artifact_path


def verify_model(
    *,
    repo_root: Path,
    model_path: Path,
    manifest_path: Path,
    prompt: str,
    max_new_tokens: int,
    device: str,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    model_path = Path(model_path)
    manifest_path = Path(manifest_path)
    if not model_path.is_absolute():
        model_path = repo_root / model_path
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path
    if not isinstance(prompt, str) or not prompt.strip():
        raise ModelVerificationError("prompt must be non-empty")
    if type(max_new_tokens) is not int or max_new_tokens <= 0:
        raise ModelVerificationError("max_new_tokens must be positive")
    if device not in {"cpu", "cuda"}:
        raise ModelVerificationError("device must be cpu or cuda")
    if device == "cuda" and not torch.cuda.is_available():
        raise ModelVerificationError("CUDA is unavailable")

    manifest = load_manifest(manifest_path)
    validate_manifest(repo_root, manifest)
    expected_artifact = (repo_root / _manifest_artifact_path(manifest)).resolve()
    if expected_artifact != model_path.resolve():
        raise ModelVerificationError("model path does not match merged manifest")
    metadata = verify_saved_model_metadata(model_path)

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True,
            trust_remote_code=False,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            dtype=torch.bfloat16,
            local_files_only=True,
            trust_remote_code=False,
            low_cpu_mem_usage=True,
        )
        model.eval()
        model.to(device)
        rendered = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = tokenizer(
            rendered,
            return_tensors="pt",
            add_special_tokens=False,
        )
        inputs = {
            key: value.to(device) if callable(getattr(value, "to", None)) else value
            for key, value in inputs.items()
        }
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=None,
                top_p=None,
                top_k=None,
            )
        input_tokens = int(inputs["input_ids"].shape[-1])
        generated = output[0, input_tokens:]
        text = tokenizer.decode(generated, skip_special_tokens=True)
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise ModelVerificationError("CUDA out of memory during merged smoke") from None
    except (OSError, RuntimeError, ValueError) as exc:
        raise ModelVerificationError("merged greedy smoke failed") from exc
    if not text.strip():
        raise ModelVerificationError("merged greedy smoke returned empty text")
    return {
        **metadata,
        "dtype": EXPECTED_DTYPE,
        "manifest_valid": True,
        "smoke_valid": True,
        "output_tokens": int(generated.shape[-1]),
        "text": text,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify an E6.1 merged BF16 model.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=16)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        result = verify_model(
            repo_root=args.repo_root,
            model_path=args.model,
            manifest_path=args.manifest,
            prompt=args.prompt,
            max_new_tokens=args.max_new_tokens,
            device=args.device,
        )
    except ManifestMismatchError as exc:
        raise ModelVerificationError("merged manifest verification failed") from exc
    for key in (
        "manifest_valid",
        "architecture",
        "context_limit",
        "dtype",
        "smoke_valid",
        "output_tokens",
        "text",
    ):
        print(f"{key}={result[key]}")


if __name__ == "__main__":
    main()
