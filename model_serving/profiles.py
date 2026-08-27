from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path, PureWindowsPath
from types import MappingProxyType
from typing import Literal, Mapping, cast


PROFILE_CONTRACT_VERSION = "localrag-model-profile-v1"
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
_APPROVED_JUNCTION_ROOTS = (
    "models",
    "saves",
    "artifacts",
    "model_deployment/manifests",
)


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

    context_limit = _positive_int(
        raw["context_limit"], f"profiles.{name}.context_limit"
    )
    max_new_tokens = _positive_int(
        raw["max_new_tokens"], f"profiles.{name}.max_new_tokens"
    )
    if context_limit > 131072 or max_new_tokens >= context_limit:
        raise ProfileValidationError(f"profiles.{name} exceeds the context contract")
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
    backend = parsed["backend"]
    if backend == "transformers":
        if (
            parsed["base_model_path"] is None
            or parsed["adapter_path"] is None
            or parsed["artifact_path"] is not None
            or parsed["dtype"] != "bfloat16"
            or parsed["quantization"] != "none"
        ):
            raise ProfileValidationError(
                f"profiles.{name} is not a valid Transformers adapter profile"
            )
    elif backend == "llama_cpp":
        if (
            parsed["base_model_path"] is not None
            or parsed["adapter_path"] is not None
            or not str(parsed["artifact_path"]).endswith(".gguf")
            or parsed["dtype"] != "float16"
            or parsed["quantization"] != "Q4_K_M"
        ):
            raise ProfileValidationError(
                f"profiles.{name} is not a valid llama.cpp Q4_K_M profile"
            )
    else:
        raise ProfileValidationError(f"profiles.{name}.backend is unsupported")

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
    if not isinstance(raw_profiles, dict) or not raw_profiles:
        raise ProfileValidationError("profile set must be a non-empty object")
    if any(not isinstance(name, str) or not name.strip() for name in raw_profiles):
        raise ProfileValidationError("profile names must be non-empty strings")
    return ModelServingProfiles(
        {
            name: _parse_profile(name, raw_profiles[name], repo_root=repo_root)
            for name in sorted(raw_profiles)
        }
    )
