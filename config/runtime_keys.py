from __future__ import annotations

import json
import math
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

SUPPORTED_PROVIDERS = (
    "bailian",
    "modelscope",
    "sensenova",
    "local_embedding",
    "local_sentence_transformer",
    "local_transformers",
)
MODEL_ROLES = ("planner", "rag", "summary")
MODEL_ROUTE_MODES = ("local", "cloud")
CONTRACT_VERSION = "localrag-runtime-v2"
DEFAULT_RUNTIME_CONFIG_NAME = "runtime_models.json"
LEGACY_RUNTIME_CONFIG_NAME = "key.json"
RUNTIME_CONFIG_ENV_VAR = "LOCALRAG_RUNTIME_CONFIG"
LOCAL_MODEL_ID = "localrag-qwen3-4b-e6.1"
_ENV_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class CloudModelConfig:
    provider: str
    base_url: str
    model: str
    api_key: str
    api_key_env: str = ""


@dataclass(frozen=True)
class LocalModelGatewayConfig:
    base_url: str
    model: str
    api_token: str
    rag_generation_enabled: bool = True
    conversation_summary_enabled: bool = True
    connect_timeout_seconds: float = 2.0
    read_timeout_seconds: float = 120.0
    circuit_failure_threshold: int = 3
    circuit_reset_seconds: float = 30.0
    api_token_env: str = ""
    tool_calling_verified: bool = False


@dataclass(frozen=True)
class ModelRoleConfig:
    route: str
    cloud: CloudModelConfig
    local: LocalModelGatewayConfig


@dataclass(frozen=True)
class EmbeddingModelConfig:
    provider: str
    model: str
    base_url: str = ""
    api_key: str = ""
    api_key_env: str = ""


@dataclass(frozen=True)
class RuntimeProviderConfig:
    # Keep the original flat fields available for historical experiment files.
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
    model_route_mode: str = "auto"
    roles: Mapping[str, ModelRoleConfig] | None = None
    embedding: EmbeddingModelConfig | None = None
    contract_version: str = "legacy"

    def role(self, name: str) -> ModelRoleConfig:
        if name not in MODEL_ROLES:
            raise ValueError(f"unknown model role: {name}")
        if self.roles is not None:
            return self.roles[name]
        cloud = CloudModelConfig(
            provider=self.provider,
            base_url=self.base_url,
            model=self.chat_model_name,
            api_key=self.api_key,
        )
        local = self.local_model_gateway or LocalModelGatewayConfig(
            base_url="http://127.0.0.1:8001/v1",
            model=LOCAL_MODEL_ID,
            api_token="",
            rag_generation_enabled=False,
            conversation_summary_enabled=False,
        )
        route = "cloud"
        if name == "rag" and local.rag_generation_enabled:
            route = "local" if self.model_route_mode != "cloud" else "cloud"
        if name == "summary" and local.conversation_summary_enabled:
            route = "local" if self.model_route_mode != "cloud" else "cloud"
        return ModelRoleConfig(route=route, cloud=cloud, local=local)


def get_default_runtime_config_path() -> Path:
    return Path(__file__).resolve().parent / DEFAULT_RUNTIME_CONFIG_NAME


def _get_legacy_runtime_config_path() -> Path:
    return Path(__file__).resolve().parent / LEGACY_RUNTIME_CONFIG_NAME


def get_runtime_config_path(
    path: Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> Path:
    runtime_environ = os.environ if environ is None else environ
    if path is not None:
        return Path(path)
    env_path = runtime_environ.get(RUNTIME_CONFIG_ENV_VAR)
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


def _required_string(
    raw_data: Mapping[str, Any],
    field: str,
    *,
    context: str = "runtime config",
    aliases: tuple[str, ...] = (),
) -> str:
    for candidate in (field, *aliases):
        if candidate not in raw_data:
            continue
        value = raw_data[candidate]
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"Empty required {context} field: {field}")
        return value.strip()
    raise RuntimeError(f"Missing required {context} field: {field}")


def _optional_string(raw_data: Mapping[str, Any], field: str, default: str) -> str:
    if field not in raw_data:
        return default
    value = raw_data[field]
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Empty optional runtime config field: {field}")
    return value.strip()


def _optional_nullable_string(
    raw_data: Mapping[str, Any], field: str
) -> str | None:
    if field not in raw_data:
        return None
    value = raw_data[field]
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Empty optional runtime config field: {field}")
    return value.strip()


def _positive_float(raw_data: Mapping[str, Any], field: str, default: float) -> float:
    value = raw_data.get(field, default)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise RuntimeError(f"Invalid local model gateway field: {field}")
    return float(value)


def _positive_int(raw_data: Mapping[str, Any], field: str, default: int) -> int:
    value = raw_data.get(field, default)
    if type(value) is not int or value <= 0:
        raise RuntimeError(f"Invalid local model gateway field: {field}")
    return value


def _environment_value(
    environ: Mapping[str, str], variable_name: str, *, kind: str
) -> str:
    if not _ENV_NAME_PATTERN.fullmatch(variable_name):
        raise RuntimeError(f"Invalid {kind} environment variable name")
    value = environ.get(variable_name)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Missing {kind} environment variable: {variable_name}")
    return value.strip()


def normalize_model_route_mode(value: object) -> str:
    if not isinstance(value, str):
        raise RuntimeError("Invalid runtime config field: model route")
    normalized = value.strip().lower()
    # "auto" is accepted only for historical flat configs.
    if normalized not in {*MODEL_ROUTE_MODES, "auto"}:
        raise RuntimeError(
            "Invalid runtime config field: model route "
            f"(expected one of: {', '.join(MODEL_ROUTE_MODES)})"
        )
    return normalized


def _validate_provider(value: str) -> str:
    provider = value.strip().lower()
    if provider not in SUPPORTED_PROVIDERS:
        raise RuntimeError(f"Unsupported runtime provider: {provider}")
    return provider


def _validate_http_base_url(value: str, *, local_only: bool) -> str:
    parsed = urlsplit(value)
    valid_host = not local_only or parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or not valid_host
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path.rstrip("/") != "/v1"
    ):
        field = "local model gateway" if local_only else "cloud model"
        raise RuntimeError(f"Invalid {field} field: base_url")
    try:
        parsed.port
    except ValueError:
        field = "local model gateway" if local_only else "cloud model"
        raise RuntimeError(f"Invalid {field} field: base_url") from None
    return value.rstrip("/")


def _load_cloud_model(
    raw_value: object, environ: Mapping[str, str], *, role: str
) -> CloudModelConfig:
    if not isinstance(raw_value, Mapping):
        raise RuntimeError(f"Invalid runtime config field: roles.{role}.cloud")
    allowed = {"provider", "base_url", "model", "api_key_env"}
    unknown = set(raw_value) - allowed
    if unknown:
        raise RuntimeError(
            f"Unknown cloud model field for {role}: " + ", ".join(sorted(unknown))
        )
    provider = _validate_provider(
        _required_string(raw_value, "provider", context=f"roles.{role}.cloud")
    )
    base_url = _validate_http_base_url(
        _required_string(raw_value, "base_url", context=f"roles.{role}.cloud"),
        local_only=False,
    )
    model = _required_string(raw_value, "model", context=f"roles.{role}.cloud")
    api_key_env = _required_string(
        raw_value, "api_key_env", context=f"roles.{role}.cloud"
    )
    api_key = _environment_value(
        environ, api_key_env, kind=f"cloud model API key for {role}"
    )
    return CloudModelConfig(provider, base_url, model, api_key, api_key_env)


def _load_local_model(
    raw_value: object,
    environ: Mapping[str, str],
    *,
    role: str,
    require_token: bool,
) -> LocalModelGatewayConfig:
    if not isinstance(raw_value, Mapping):
        raise RuntimeError(f"Invalid runtime config field: roles.{role}.local")
    allowed = {
        "base_url",
        "model",
        "api_token_env",
        "tool_calling_verified",
        "connect_timeout_seconds",
        "read_timeout_seconds",
        "circuit_failure_threshold",
        "circuit_reset_seconds",
    }
    unknown = set(raw_value) - allowed
    if unknown:
        raise RuntimeError(
            f"Unknown local model field for {role}: " + ", ".join(sorted(unknown))
        )
    base_url = _validate_http_base_url(
        _required_string(raw_value, "base_url", context=f"roles.{role}.local"),
        local_only=True,
    )
    model = _required_string(raw_value, "model", context=f"roles.{role}.local")
    api_token_env = _required_string(
        raw_value, "api_token_env", context=f"roles.{role}.local"
    )
    if require_token:
        api_token = _environment_value(
            environ, api_token_env, kind=f"local model API token for {role}"
        )
    else:
        # A cloud-routed role never constructs a local client. Keep the
        # configured environment variable name for a later route switch, but
        # do not make a local secret a prerequisite for loading the config.
        api_token = environ.get(api_token_env, "").strip()
    verified = raw_value.get("tool_calling_verified", False)
    if type(verified) is not bool:
        raise RuntimeError(f"Invalid local model field for {role}: tool_calling_verified")
    return LocalModelGatewayConfig(
        base_url=base_url,
        model=model,
        api_token=api_token,
        api_token_env=api_token_env,
        tool_calling_verified=verified,
        connect_timeout_seconds=_positive_float(raw_value, "connect_timeout_seconds", 2.0),
        read_timeout_seconds=_positive_float(raw_value, "read_timeout_seconds", 120.0),
        circuit_failure_threshold=_positive_int(raw_value, "circuit_failure_threshold", 3),
        circuit_reset_seconds=_positive_float(raw_value, "circuit_reset_seconds", 30.0),
    )


def _load_embedding(
    raw_value: object, environ: Mapping[str, str]
) -> EmbeddingModelConfig:
    if not isinstance(raw_value, Mapping):
        raise RuntimeError("Invalid runtime config field: embedding")
    allowed = {"provider", "model", "base_url", "api_key_env"}
    unknown = set(raw_value) - allowed
    if unknown:
        raise RuntimeError("Unknown embedding field: " + ", ".join(sorted(unknown)))
    provider = _validate_provider(
        _required_string(raw_value, "provider", context="embedding")
    )
    model = _required_string(raw_value, "model", context="embedding")
    base_url = ""
    api_key_env = ""
    api_key = ""
    if provider in {"bailian", "modelscope"}:
        base_url = _validate_http_base_url(
            _required_string(raw_value, "base_url", context="embedding"),
            local_only=False,
        )
        api_key_env = _required_string(raw_value, "api_key_env", context="embedding")
        api_key = _environment_value(environ, api_key_env, kind="embedding API key")
    elif "base_url" in raw_value or "api_key_env" in raw_value:
        raise RuntimeError("Local embedding configuration must not contain cloud credentials")
    return EmbeddingModelConfig(provider, model, base_url, api_key, api_key_env)


def _load_v2_config(
    raw_data: Mapping[str, Any], environ: Mapping[str, str]
) -> RuntimeProviderConfig:
    allowed = {"contract_version", "roles", "embedding"}
    unknown = set(raw_data) - allowed
    if unknown:
        raise RuntimeError("Unknown runtime config field: " + ", ".join(sorted(unknown)))
    roles_value = raw_data.get("roles")
    if not isinstance(roles_value, Mapping):
        raise RuntimeError("Invalid runtime config field: roles")
    if set(roles_value) != set(MODEL_ROLES):
        raise RuntimeError("Runtime config roles must define planner, rag, and summary")
    roles: dict[str, ModelRoleConfig] = {}
    for role in MODEL_ROLES:
        role_value = roles_value[role]
        if not isinstance(role_value, Mapping) or set(role_value) != {
            "route",
            "cloud",
            "local",
        }:
            raise RuntimeError(f"Invalid runtime config field: roles.{role}")
        route = normalize_model_route_mode(role_value["route"])
        if route == "auto":
            raise RuntimeError(f"Invalid runtime config field: roles.{role}.route")
        roles[role] = ModelRoleConfig(
            route=route,
            cloud=_load_cloud_model(role_value["cloud"], environ, role=role),
            local=_load_local_model(
                role_value["local"],
                environ,
                role=role,
                require_token=route == "local",
            ),
        )
    embedding = _load_embedding(raw_data.get("embedding"), environ)
    planner_cloud = roles["planner"].cloud
    return RuntimeProviderConfig(
        provider=planner_cloud.provider,
        api_key=planner_cloud.api_key,
        base_url=planner_cloud.base_url,
        chat_model_name=planner_cloud.model,
        embedding_model_name=embedding.model,
        local_model_gateway=roles["rag"].local,
        model_route_mode=roles["rag"].route,
        roles=roles,
        embedding=embedding,
        contract_version=CONTRACT_VERSION,
    )


_LEGACY_LOCAL_FIELDS = {
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


def _load_legacy_local_model(
    raw_value: object, environ: Mapping[str, str]
) -> LocalModelGatewayConfig | None:
    if raw_value is None:
        return None
    if not isinstance(raw_value, Mapping):
        raise RuntimeError("Invalid runtime config field: local_model_gateway")
    unknown = set(raw_value) - _LEGACY_LOCAL_FIELDS
    if unknown:
        raise RuntimeError("Unknown local model gateway field: " + ", ".join(sorted(unknown)))
    base_url = _validate_http_base_url(
        _required_string(raw_value, "base_url", context="local model gateway"),
        local_only=True,
    )
    model = _required_string(raw_value, "model", context="local model gateway")
    if model != LOCAL_MODEL_ID:
        raise RuntimeError("Invalid local model gateway field: model")
    api_token_env = _required_string(
        raw_value, "api_token_env", context="local model gateway"
    )
    api_token = _environment_value(environ, api_token_env, kind="local model API token")
    enabled: dict[str, bool] = {}
    for field in ("rag_generation_enabled", "conversation_summary_enabled"):
        value = raw_value.get(field)
        if type(value) is not bool:
            raise RuntimeError(f"Invalid local model gateway field: {field}")
        enabled[field] = value
    return LocalModelGatewayConfig(
        base_url=base_url,
        model=model,
        api_token=api_token,
        api_token_env=api_token_env,
        rag_generation_enabled=enabled["rag_generation_enabled"],
        conversation_summary_enabled=enabled["conversation_summary_enabled"],
        connect_timeout_seconds=_positive_float(raw_value, "connect_timeout_seconds", 2.0),
        read_timeout_seconds=_positive_float(raw_value, "read_timeout_seconds", 120.0),
        circuit_failure_threshold=_positive_int(raw_value, "circuit_failure_threshold", 3),
        circuit_reset_seconds=_positive_float(raw_value, "circuit_reset_seconds", 30.0),
    )


def _load_legacy_config(
    raw_data: Mapping[str, Any], environ: Mapping[str, str]
) -> RuntimeProviderConfig:
    provider_value = raw_data.get("provider")
    if provider_value is None and {
        "dashscope_api_key",
        "dashscope_base_url",
        "chat_model_name",
        "embedding_model_name",
    }.issubset(raw_data):
        provider_value = "bailian"
    if not isinstance(provider_value, str) or not provider_value.strip():
        raise RuntimeError("Missing required runtime config field: provider")
    provider = _validate_provider(provider_value)
    api_key_aliases = ("dashscope_api_key",) if provider == "bailian" else ()
    base_url_aliases = ("dashscope_base_url",) if provider == "bailian" else ()
    max_new_tokens = raw_data.get("max_new_tokens", 128)
    if type(max_new_tokens) is not int or max_new_tokens <= 0:
        raise RuntimeError("Invalid optional runtime config field: max_new_tokens")
    return RuntimeProviderConfig(
        provider=provider,
        api_key=_required_string(raw_data, "api_key", aliases=api_key_aliases),
        base_url=_required_string(raw_data, "base_url", aliases=base_url_aliases),
        chat_model_name=_required_string(raw_data, "chat_model_name"),
        embedding_model_name=_required_string(raw_data, "embedding_model_name"),
        device=_optional_string(raw_data, "device", "auto"),
        torch_dtype=_optional_string(raw_data, "torch_dtype", "float16"),
        max_new_tokens=max_new_tokens,
        adapter_path=_optional_nullable_string(raw_data, "adapter_path"),
        rag_system_prompt=_optional_nullable_string(raw_data, "rag_system_prompt"),
        local_model_gateway=_load_legacy_local_model(
            raw_data.get("local_model_gateway"), environ
        ),
        model_route_mode=normalize_model_route_mode(raw_data.get("model_route_mode", "auto")),
    )


def load_runtime_config(
    path: Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> RuntimeProviderConfig:
    runtime_environ = os.environ if environ is None else environ
    config_path = get_runtime_config_path(path, environ=runtime_environ)
    raw_data = _load_raw_json(config_path)
    version = raw_data.get("contract_version")
    if version is None:
        return _load_legacy_config(raw_data, runtime_environ)
    if version != CONTRACT_VERSION:
        raise RuntimeError(f"Unsupported runtime config contract: {version}")
    return _load_v2_config(raw_data, runtime_environ)


def update_model_routes(
    routes: Mapping[str, str],
    path: Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
) -> Path:
    if not isinstance(routes, Mapping) or not routes:
        raise ValueError("routes must be a non-empty mapping")
    unknown = set(routes) - set(MODEL_ROLES)
    if unknown:
        raise ValueError("unknown model role: " + ", ".join(sorted(unknown)))
    normalized: dict[str, str] = {}
    for role, value in routes.items():
        route = normalize_model_route_mode(value)
        if route == "auto":
            raise ValueError("route must be local or cloud")
        normalized[role] = route

    config_path = get_runtime_config_path(path, environ=environ).resolve()
    raw_data = _load_raw_json(config_path)
    if raw_data.get("contract_version") != CONTRACT_VERSION:
        raise RuntimeError("Route persistence requires a localrag-runtime-v2 config")
    roles = raw_data.get("roles")
    if not isinstance(roles, dict):
        raise RuntimeError("Invalid runtime config field: roles")
    for role, route in normalized.items():
        role_value = roles.get(role)
        if not isinstance(role_value, dict):
            raise RuntimeError(f"Invalid runtime config field: roles.{role}")
        role_value["route"] = route

    runtime_environ = os.environ if environ is None else environ
    _load_v2_config(raw_data, runtime_environ)
    temporary = config_path.with_name(f".{config_path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(
            json.dumps(raw_data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, config_path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return config_path
