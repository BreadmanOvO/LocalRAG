from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path, PureWindowsPath
from types import MappingProxyType
from typing import Literal, Mapping, cast


PROFILE_CONTRACT_VERSION = "localrag-model-profile-v1"
_PROFILE_NAMES = frozenset({"e6_1_adapter_bf16", "e6_1_q4_k_m"})
_TOP_LEVEL_FIELDS = frozenset({"contract_version", "profiles"})
_PROFILE_FIELDS = frozenset(
    {
        "model_id",
        "backend",
        "base_model_path",
        "adapter_path",
        "artifact_path",
        "dtype",
        "quantization",
        "context_limit",
        "max_new_tokens",
        "enable_thinking",
        "manifest_path",
    }
)
_MODEL_ID = "localrag-qwen3-4b-e6.1"
_APPROVED_JUNCTION_ROOTS = (
    "models/Qwen3-4B",
    "saves/Qwen3-4B-Thinking/lora/localrag_sft_e6_1_qlora_webui",
)
_BF16_EXPECTED = {
    "backend": "transformers",
    "base_model_path": "models/Qwen3-4B",
    "adapter_path": (
        "saves/Qwen3-4B-Thinking/lora/localrag_sft_e6_1_qlora_webui"
    ),
    "artifact_path": None,
    "dtype": "bfloat16",
    "quantization": "none",
    "manifest_path": "model_deployment/manifests/e6_1_input_manifest.json",
}
_Q4_EXPECTED = {
    "backend": "llama_cpp",
    "base_model_path": None,
    "adapter_path": None,
    "artifact_path": "artifacts/models/qwen3-4b-e6.1-q4_k_m.gguf",
    "dtype": "float16",
    "quantization": "Q4_K_M",
    "manifest_path": "model_deployment/manifests/e6_1_q4_k_m_manifest.json",
}


class ProfileValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ModelServingProfile:
    name: str
    model_id: str
    backend: Literal["transformers", "llama_cpp"]
    base_model_path: str | None
    adapter_path: str | None
    artifact_path: str | None
    dtype: str
    quantization: str
    context_limit: int
    max_new_tokens: int
    enable_thinking: bool
    manifest_path: str


class ModelServingProfiles:
    def __init__(self, profiles: Mapping[str, ModelServingProfile]) -> None:
        self._profiles = MappingProxyType(dict(profiles))

    def require(self, name: str) -> ModelServingProfile:
        if not isinstance(name, str) or not name.strip():
            raise ProfileValidationError("profile name must be a non-empty string")
        try:
            return self._profiles[name]
        except KeyError:
            raise ProfileValidationError(f"unknown model serving profile: {name}") from None

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._profiles))


def _exact_mapping(value: object, fields: frozenset[str], field_name: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise ProfileValidationError(f"{field_name} fields do not match the contract")
    return value


def _text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProfileValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def _relative_path(
    value: object,
    field_name: str,
    repo_root: Path,
    *,
    allow_none: bool,
) -> str | None:
    if value is None and allow_none:
        return None
    text = _text(value, field_name)
    path = Path(text)
    if path.is_absolute() or PureWindowsPath(text).is_absolute():
        raise ProfileValidationError(f"{field_name} must be repository-relative")
    lexical = Path(os.path.abspath(repo_root / path))
    try:
        lexical.relative_to(repo_root)
    except ValueError:
        raise ProfileValidationError(f"{field_name} escapes the repository") from None
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        portable = path.as_posix()
        approved = False
        for anchor in _APPROVED_JUNCTION_ROOTS:
            if portable == anchor or portable.startswith(f"{anchor}/"):
                try:
                    resolved.relative_to((repo_root / anchor).resolve())
                except ValueError:
                    continue
                approved = True
                break
        if not approved:
            raise ProfileValidationError(f"{field_name} escapes the repository") from None
    return path.as_posix()


def _positive_int(value: object, field_name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ProfileValidationError(f"{field_name} must be a positive integer")
    return value


def _parse_profile(
    name: str,
    value: object,
    *,
    repo_root: Path,
) -> ModelServingProfile:
    raw = _exact_mapping(value, _PROFILE_FIELDS, f"profiles.{name}")
    model_id = _text(raw["model_id"], f"profiles.{name}.model_id")
    if model_id != _MODEL_ID:
        raise ProfileValidationError(f"profiles.{name}.model_id is not the E6.1 identity")

    context_limit = _positive_int(
        raw["context_limit"], f"profiles.{name}.context_limit"
    )
    max_new_tokens = _positive_int(
        raw["max_new_tokens"], f"profiles.{name}.max_new_tokens"
    )
    if context_limit > 40960 or max_new_tokens >= context_limit:
        raise ProfileValidationError(f"profiles.{name} exceeds the fixed context contract")
    if raw["enable_thinking"] is not False:
        raise ProfileValidationError(f"profiles.{name}.enable_thinking must be false")

    parsed = {
        "backend": _text(raw["backend"], f"profiles.{name}.backend"),
        "base_model_path": _relative_path(
            raw["base_model_path"],
            f"profiles.{name}.base_model_path",
            repo_root,
            allow_none=True,
        ),
        "adapter_path": _relative_path(
            raw["adapter_path"],
            f"profiles.{name}.adapter_path",
            repo_root,
            allow_none=True,
        ),
        "artifact_path": _relative_path(
            raw["artifact_path"],
            f"profiles.{name}.artifact_path",
            repo_root,
            allow_none=True,
        ),
        "dtype": _text(raw["dtype"], f"profiles.{name}.dtype"),
        "quantization": _text(
            raw["quantization"], f"profiles.{name}.quantization"
        ),
        "manifest_path": _relative_path(
            raw["manifest_path"],
            f"profiles.{name}.manifest_path",
            repo_root,
            allow_none=False,
        ),
    }
    expected = _BF16_EXPECTED if name == "e6_1_adapter_bf16" else _Q4_EXPECTED
    if parsed != expected:
        raise ProfileValidationError(f"profiles.{name} does not match the fixed identity")
    if name == "e6_1_q4_k_m" and not str(parsed["artifact_path"]).endswith(
        ".gguf"
    ):
        raise ProfileValidationError("Q4 artifact must be a GGUF file")

    return ModelServingProfile(
        name=name,
        model_id=model_id,
        backend=cast(Literal["transformers", "llama_cpp"], parsed["backend"]),
        base_model_path=parsed["base_model_path"],
        adapter_path=parsed["adapter_path"],
        artifact_path=parsed["artifact_path"],
        dtype=cast(str, parsed["dtype"]),
        quantization=cast(str, parsed["quantization"]),
        context_limit=context_limit,
        max_new_tokens=max_new_tokens,
        enable_thinking=False,
        manifest_path=cast(str, parsed["manifest_path"]),
    )


def load_profiles(path: Path, *, repo_root: Path) -> ModelServingProfiles:
    path = Path(path)
    repo_root = Path(repo_root).resolve()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ProfileValidationError("profile file is not valid JSON") from exc
    top = _exact_mapping(payload, _TOP_LEVEL_FIELDS, "profile document")
    if top["contract_version"] != PROFILE_CONTRACT_VERSION:
        raise ProfileValidationError("profile contract version is invalid")
    raw_profiles = top["profiles"]
    if not isinstance(raw_profiles, dict) or set(raw_profiles) != _PROFILE_NAMES:
        raise ProfileValidationError("profile set must contain the fixed release profiles")
    return ModelServingProfiles(
        {
            name: _parse_profile(name, raw_profiles[name], repo_root=repo_root)
            for name in sorted(_PROFILE_NAMES)
        }
    )
