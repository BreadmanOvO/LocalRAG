"""Cloud model configuration and lazy clients for the v1.8 team runtime."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI


SUPPORTED_CLOUD_PROVIDERS = {"modelscope", "sensenova", "bailian"}
DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "multi_agent_models.json"


@dataclass(frozen=True)
class CloudAgentSpec:
    agent_id: str
    display_name: str
    responsibility: str
    provider: str
    base_url: str
    model: str
    api_key_env: str
    api_key: str = field(repr=False)
    capabilities: tuple[str, ...] = ()
    system_prompt: str = ""
    enabled: bool = True
    tier: str = "standard"
    model_profile: str = ""
    modalities: tuple[str, ...] = ("text",)
    max_concurrency: int = 4


@dataclass(frozen=True)
class CloudModelProfile:
    profile_id: str
    provider: str
    base_url: str
    model: str
    api_key_env: str
    api_key: str = field(repr=False)
    capabilities: tuple[str, ...] = ()
    modalities: tuple[str, ...] = ("text",)
    max_concurrency: int = 4


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Missing required multi-agent config field: {field}")
    return value.strip()


def _validate_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path.rstrip("/") != "/v1":
        raise RuntimeError("Invalid multi-agent cloud model field: base_url")
    return value.rstrip("/")


def _string_tuple(value: Any, field_name: str, *, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    if value is None:
        return default
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise RuntimeError(f"Invalid multi-agent field: {field_name}")
    return tuple(item.strip() for item in value)


def _positive_int(value: Any, field_name: str, *, default: int = 4) -> int:
    if value is None:
        return default
    if type(value) is not int or value < 1:
        raise RuntimeError(f"Invalid multi-agent field: {field_name}")
    return value


def load_cloud_agents(path: Path | None = None, *, environ: Mapping[str, str] | None = None) -> dict[str, CloudAgentSpec]:
    environment = os.environ if environ is None else environ
    config_path = Path(path or environment.get("LOCALRAG_MULTI_AGENT_CONFIG", DEFAULT_CONFIG))
    if not config_path.exists():
        raise RuntimeError(f"Missing multi-agent config file: {config_path}")
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Malformed multi-agent config file") from exc
    if not isinstance(raw, dict) or raw.get("contract_version") != "agent-platform-cloud-v1":
        raise RuntimeError("Unsupported multi-agent config contract")
    agents = raw.get("agents")
    if not isinstance(agents, dict) or not agents:
        raise RuntimeError("Multi-agent config must define agents")
    profiles: dict[str, CloudModelProfile] = {}
    raw_profiles = raw.get("model_profiles", {})
    if not isinstance(raw_profiles, dict):
        raise RuntimeError("model_profiles must be an object")
    for profile_id, profile in raw_profiles.items():
        if not isinstance(profile_id, str) or not profile_id.strip() or not isinstance(profile, dict):
            raise RuntimeError("Invalid model profile entry")
        provider = _required_string(profile.get("provider"), f"model_profiles.{profile_id}.provider").lower()
        if provider not in SUPPORTED_CLOUD_PROVIDERS:
            raise RuntimeError(f"Unsupported model profile provider: {provider}")
        api_key_env = _required_string(profile.get("api_key_env", ""), f"model_profiles.{profile_id}.api_key_env")
        inline_api_key = profile.get("api_key", "")
        if not isinstance(inline_api_key, str):
            raise RuntimeError(f"Invalid model profile field: model_profiles.{profile_id}.api_key")
        api_key = inline_api_key.strip() or environment.get(api_key_env, "").strip()
        enabled = profile.get("enabled", True)
        if enabled and not api_key:
            raise RuntimeError(f"Missing API key for enabled model profile: {api_key_env}")
        profiles[profile_id.strip()] = CloudModelProfile(
            profile_id.strip(), provider,
            _validate_url(_required_string(profile.get("base_url"), f"model_profiles.{profile_id}.base_url")),
            _required_string(profile.get("model"), f"model_profiles.{profile_id}.model"),
            api_key_env, api_key,
            _string_tuple(profile.get("capabilities"), f"model_profiles.{profile_id}.capabilities"),
            _string_tuple(profile.get("modalities"), f"model_profiles.{profile_id}.modalities", default=("text",)),
            _positive_int(profile.get("max_concurrency"), f"model_profiles.{profile_id}.max_concurrency"),
        )
    result: dict[str, CloudAgentSpec] = {}
    for agent_id, value in agents.items():
        if not isinstance(agent_id, str) or not agent_id.strip() or not isinstance(value, dict):
            raise RuntimeError("Invalid multi-agent agent entry")
        allowed = {"display_name", "responsibility", "provider", "base_url", "model", "model_profile", "api_key_env", "api_key", "capabilities", "modalities", "max_concurrency", "tier", "system_prompt", "enabled"}
        unknown = set(value) - allowed
        if unknown:
            raise RuntimeError(f"Unknown multi-agent fields for {agent_id}: {', '.join(sorted(unknown))}")
        normalized_id = agent_id.strip()
        profile_id = str(value.get("model_profile", "")).strip()
        profile = profiles.get(profile_id) if profile_id else None
        if profile_id and profile is None:
            raise RuntimeError(f"Unknown model profile for agent {normalized_id}: {profile_id}")
        provider = _required_string(value.get("provider", profile.provider if profile else ""), f"agents.{normalized_id}.provider").lower()
        if provider not in SUPPORTED_CLOUD_PROVIDERS:
            raise RuntimeError(f"Unsupported multi-agent provider: {provider}")
        base_url = _validate_url(_required_string(value.get("base_url", profile.base_url if profile else ""), f"agents.{normalized_id}.base_url"))
        model = _required_string(value.get("model", profile.model if profile else ""), f"agents.{normalized_id}.model")
        inline_api_key = value.get("api_key", "")
        if not isinstance(inline_api_key, str):
            raise RuntimeError(f"Invalid multi-agent field: agents.{normalized_id}.api_key")
        raw_api_key_env = str(value.get("api_key_env", profile.api_key_env if profile else "")).strip()
        if not raw_api_key_env and not inline_api_key.strip() and not (profile and profile.api_key):
            raise RuntimeError(f"Missing API key source for agents.{normalized_id}")
        api_key_env = raw_api_key_env
        enabled = value.get("enabled", True)
        if type(enabled) is not bool:
            raise RuntimeError(f"Invalid multi-agent field: agents.{normalized_id}.enabled")
        # The ignored local config may contain an inline key for convenience.
        # The example config does not.  Environment variables remain the
        # preferred deployment path and win only when no inline key is set.
        api_key = inline_api_key.strip() or (profile.api_key if profile else "") or environment.get(api_key_env, "").strip()
        if enabled and not api_key:
            raise RuntimeError(f"Missing API key for enabled multi-agent: {api_key_env}")
        capabilities = _string_tuple(value.get("capabilities", list(profile.capabilities) if profile else []), f"agents.{normalized_id}.capabilities")
        modalities = _string_tuple(value.get("modalities", list(profile.modalities) if profile else ["text"]), f"agents.{normalized_id}.modalities", default=("text",))
        result[normalized_id] = CloudAgentSpec(
            agent_id=normalized_id,
            display_name=_required_string(value.get("display_name"), f"agents.{normalized_id}.display_name"),
            responsibility=_required_string(value.get("responsibility"), f"agents.{normalized_id}.responsibility"),
            provider=provider,
            base_url=base_url,
            model=model,
            api_key_env=api_key_env,
            api_key=api_key,
            capabilities=capabilities,
            system_prompt=str(value.get("system_prompt", "")).strip(),
            enabled=enabled,
            tier=str(value.get("tier", "standard")).strip() or "standard",
            model_profile=profile_id,
            modalities=modalities,
            max_concurrency=_positive_int(value.get("max_concurrency", profile.max_concurrency if profile else 4), f"agents.{normalized_id}.max_concurrency"),
        )
    return result


class CloudAgentClient:
    """Lazy OpenAI-compatible client; construction never performs a request."""

    def __init__(self, spec: CloudAgentSpec, *, timeout_seconds: float = 60.0) -> None:
        self.spec = spec
        self._model = ChatOpenAI(model=spec.model, api_key=spec.api_key, base_url=spec.base_url, timeout=timeout_seconds, max_retries=1)

    def invoke(self, messages: Sequence[BaseMessage]) -> str:
        response = self._model.invoke(list(messages))
        content = response.content if isinstance(response, AIMessage) else getattr(response, "content", response)
        if isinstance(content, list):
            content = "".join(item.get("text", "") if isinstance(item, dict) else str(item) for item in content)
        text = content.strip() if isinstance(content, str) else ""
        if not text:
            raise RuntimeError(f"Cloud agent returned an empty response: {self.spec.agent_id}")
        return text
