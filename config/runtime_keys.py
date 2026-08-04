from __future__ import annotations

import json
import math
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

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
LOCAL_MODEL_ID = "localrag-qwen3-4b-e6.1"
LOCAL_MODEL_GATEWAY_FIELDS = frozenset(
    {
        "base_url",
        "model",
        "api_token_env",
        "rag_generation_enabled",
        "conversation_summary_enabled",
        "connect_timeout_seconds",
        "read_timeout_seconds",
        "circuit_failure_threshold",
        "circuit_reset_seconds",
    }
)


@dataclass(frozen=True)
class LocalModelGatewayConfig:
    base_url: str
    model: str
    api_token: str
    rag_generation_enabled: bool
    conversation_summary_enabled: bool
    connect_timeout_seconds: float = 2.0
    read_timeout_seconds: float = 120.0
    circuit_failure_threshold: int = 3
    circuit_reset_seconds: float = 30.0


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
    rag_system_prompt: str | None = None
    local_model_gateway: LocalModelGatewayConfig | None = None


def get_default_runtime_config_path() -> Path:
    return Path(__file__).resolve().parent / DEFAULT_RUNTIME_CONFIG_NAME


def _get_legacy_runtime_config_path() -> Path:
    return Path(__file__).resolve().parent / LEGACY_RUNTIME_CONFIG_NAME


def _resolve_runtime_config_path(
    path: Path | None,
    environ: Mapping[str, str],
) -> Path:
    if path is not None:
        return path

    env_path = environ.get(RUNTIME_CONFIG_ENV_VAR)
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


def _read_local_required_string(raw_data: Mapping[str, Any], field: str) -> str:
    value = raw_data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Invalid local model gateway field: {field}")
    return value.strip()


def _read_local_bool(raw_data: Mapping[str, Any], field: str) -> bool:
    value = raw_data.get(field)
    if type(value) is not bool:
        raise RuntimeError(f"Invalid local model gateway field: {field}")
    return value


def _read_local_positive_float(
    raw_data: Mapping[str, Any],
    field: str,
    default: float,
) -> float:
    value = raw_data.get(field, default)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise RuntimeError(f"Invalid local model gateway field: {field}")
    return float(value)


def _read_local_positive_int(
    raw_data: Mapping[str, Any],
    field: str,
    default: int,
) -> int:
    value = raw_data.get(field, default)
    if type(value) is not int or value <= 0:
        raise RuntimeError(f"Invalid local model gateway field: {field}")
    return value


def _validate_local_base_url(value: str) -> str:
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path.rstrip("/") != "/v1"
    ):
        raise RuntimeError("Invalid local model gateway field: base_url")
    try:
        parsed.port
    except ValueError:
        raise RuntimeError("Invalid local model gateway field: base_url") from None
    return value.rstrip("/")


def _load_local_model_gateway(
    raw_value: object,
    environ: Mapping[str, str],
) -> LocalModelGatewayConfig | None:
    if raw_value is None:
        return None
    if not isinstance(raw_value, Mapping):
        raise RuntimeError("Invalid runtime config field: local_model_gateway")
    unknown = set(raw_value) - LOCAL_MODEL_GATEWAY_FIELDS
    if unknown:
        raise RuntimeError(
            "Unknown local model gateway field: " + ", ".join(sorted(unknown))
        )
    base_url = _validate_local_base_url(
        _read_local_required_string(raw_value, "base_url")
    )
    model = _read_local_required_string(raw_value, "model")
    if model != LOCAL_MODEL_ID:
        raise RuntimeError("Invalid local model gateway field: model")
    api_token_env = _read_local_required_string(raw_value, "api_token_env")
    api_token = environ.get(api_token_env)
    if not isinstance(api_token, str) or not api_token.strip():
        raise RuntimeError(
            f"Missing local model API token environment variable: {api_token_env}"
        )
    return LocalModelGatewayConfig(
        base_url=base_url,
        model=model,
        api_token=api_token.strip(),
        rag_generation_enabled=_read_local_bool(
            raw_value,
            "rag_generation_enabled",
        ),
        conversation_summary_enabled=_read_local_bool(
            raw_value,
            "conversation_summary_enabled",
        ),
        connect_timeout_seconds=_read_local_positive_float(
            raw_value,
            "connect_timeout_seconds",
            2.0,
        ),
        read_timeout_seconds=_read_local_positive_float(
            raw_value,
            "read_timeout_seconds",
            120.0,
        ),
        circuit_failure_threshold=_read_local_positive_int(
            raw_value,
            "circuit_failure_threshold",
            3,
        ),
        circuit_reset_seconds=_read_local_positive_float(
            raw_value,
            "circuit_reset_seconds",
            30.0,
        ),
    )


def load_runtime_config(
    path: Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> RuntimeProviderConfig:
    runtime_environ = os.environ if environ is None else environ
    config_path = _resolve_runtime_config_path(path, runtime_environ)
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
        "rag_system_prompt": _read_optional_nullable_string(raw_data, "rag_system_prompt"),
        "local_model_gateway": _load_local_model_gateway(
            raw_data.get("local_model_gateway"),
            runtime_environ,
        ),
    }
    return RuntimeProviderConfig(**values)
