from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUPPORTED_PROVIDERS = (
    "bailian",
    "modelscope",
    "sensenova",
    "local_embedding",
    "local_sentence_transformer",
    "local_transformers",
)
UNIFIED_REQUIRED_FIELDS = (
    "provider",
    "api_key",
    "base_url",
    "chat_model_name",
    "embedding_model_name",
)
DEFAULT_RUNTIME_CONFIG_NAME = "runtime_models.json"
LEGACY_RUNTIME_CONFIG_NAME = "key.json"
RUNTIME_CONFIG_ENV_VAR = "LOCALRAG_RUNTIME_CONFIG"


@dataclass(frozen=True)
class RuntimeProviderConfig:
    provider: str
    api_key: str
    base_url: str
    chat_model_name: str
    embedding_model_name: str
    device: str = "auto"
    torch_dtype: str = "float16"
    max_new_tokens: int = 128
    adapter_path: str | None = None


def get_default_runtime_config_path() -> Path:
    return Path(__file__).resolve().parent / DEFAULT_RUNTIME_CONFIG_NAME


def _get_legacy_runtime_config_path() -> Path:
    return Path(__file__).resolve().parent / LEGACY_RUNTIME_CONFIG_NAME


def _resolve_runtime_config_path(path: Path | None) -> Path:
    if path is not None:
        return path

    env_path = os.environ.get(RUNTIME_CONFIG_ENV_VAR)
    if env_path:
        return Path(env_path)

    default_path = get_default_runtime_config_path()
    if default_path.exists():
        return default_path
    return _get_legacy_runtime_config_path()


def _load_raw_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError("Missing required runtime config file")

    try:
        raw_data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Malformed runtime config file") from exc

    if not isinstance(raw_data, dict):
        raise RuntimeError("Malformed runtime config file")
    return raw_data


def _normalize_provider(raw_data: dict[str, Any]) -> str:
    provider = raw_data.get("provider")
    if provider is None and {
        "dashscope_api_key",
        "dashscope_base_url",
        "chat_model_name",
        "embedding_model_name",
    }.issubset(raw_data):
        provider = "bailian"

    if not isinstance(provider, str) or not provider.strip():
        raise RuntimeError("Missing required runtime config field: provider")

    normalized_provider = provider.strip().lower()
    if normalized_provider not in SUPPORTED_PROVIDERS:
        raise RuntimeError(f"Unsupported runtime provider: {normalized_provider}")
    return normalized_provider


def _read_required_string(raw_data: dict[str, Any], field: str, aliases: tuple[str, ...] = ()) -> str:
    candidate_fields = (field, *aliases)
    for candidate_field in candidate_fields:
        if candidate_field not in raw_data:
            continue
        value = raw_data[candidate_field]
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"Empty required runtime config field: {field}")
        return value.strip()
    raise RuntimeError(f"Missing required runtime config field: {field}")


def _read_optional_string(raw_data: dict[str, Any], field: str, default: str) -> str:
    if field not in raw_data:
        return default
    value = raw_data[field]
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Empty optional runtime config field: {field}")
    return value.strip()


def _read_optional_nullable_string(raw_data: dict[str, Any], field: str) -> str | None:
    if field not in raw_data:
        return None
    value = raw_data[field]
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Empty optional runtime config field: {field}")
    return value.strip()


def _read_optional_int(raw_data: dict[str, Any], field: str, default: int) -> int:
    if field not in raw_data:
        return default
    value = raw_data[field]
    if not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"Invalid optional runtime config field: {field}")
    return value


def load_runtime_config(path: Path | None = None) -> RuntimeProviderConfig:
    config_path = _resolve_runtime_config_path(path)
    raw_data = _load_raw_json(config_path)
    provider = _normalize_provider(raw_data)

    api_key_aliases = ("dashscope_api_key",) if provider == "bailian" else ()
    base_url_aliases = ("dashscope_base_url",) if provider == "bailian" else ()

    values = {
        "provider": provider,
        "api_key": _read_required_string(raw_data, "api_key", aliases=api_key_aliases),
        "base_url": _read_required_string(raw_data, "base_url", aliases=base_url_aliases),
        "chat_model_name": _read_required_string(raw_data, "chat_model_name"),
        "embedding_model_name": _read_required_string(raw_data, "embedding_model_name"),
        "device": _read_optional_string(raw_data, "device", "auto"),
        "torch_dtype": _read_optional_string(raw_data, "torch_dtype", "float16"),
        "max_new_tokens": _read_optional_int(raw_data, "max_new_tokens", 128),
        "adapter_path": _read_optional_nullable_string(raw_data, "adapter_path"),
    }
    return RuntimeProviderConfig(**values)
