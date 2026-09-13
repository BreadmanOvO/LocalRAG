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


def _required_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Missing required multi-agent config field: {field}")
    return value.strip()


def _validate_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path.rstrip("/") != "/v1":
        raise RuntimeError("Invalid multi-agent cloud model field: base_url")
    return value.rstrip("/")


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
    result: dict[str, CloudAgentSpec] = {}
    for agent_id, value in agents.items():
        if not isinstance(agent_id, str) or not agent_id.strip() or not isinstance(value, dict):
            raise RuntimeError("Invalid multi-agent agent entry")
        allowed = {"display_name", "responsibility", "provider", "base_url", "model", "api_key_env", "capabilities", "system_prompt", "enabled"}
        unknown = set(value) - allowed
        if unknown:
            raise RuntimeError(f"Unknown multi-agent fields for {agent_id}: {', '.join(sorted(unknown))}")
        normalized_id = agent_id.strip()
        provider = _required_string(value.get("provider"), f"agents.{normalized_id}.provider").lower()
        if provider not in SUPPORTED_CLOUD_PROVIDERS:
            raise RuntimeError(f"Unsupported multi-agent provider: {provider}")
        base_url = _validate_url(_required_string(value.get("base_url"), f"agents.{normalized_id}.base_url"))
        model = _required_string(value.get("model"), f"agents.{normalized_id}.model")
        api_key_env = _required_string(value.get("api_key_env"), f"agents.{normalized_id}.api_key_env")
        enabled = value.get("enabled", True)
        if type(enabled) is not bool:
            raise RuntimeError(f"Invalid multi-agent field: agents.{normalized_id}.enabled")
        api_key = environment.get(api_key_env, "").strip()
        if enabled and not api_key:
            raise RuntimeError(f"Missing API key for enabled multi-agent: {api_key_env}")
        capabilities = value.get("capabilities", [])
        if not isinstance(capabilities, list) or not all(isinstance(item, str) and item.strip() for item in capabilities):
            raise RuntimeError(f"Invalid multi-agent capabilities: {normalized_id}")
        result[normalized_id] = CloudAgentSpec(
            agent_id=normalized_id,
            display_name=_required_string(value.get("display_name"), f"agents.{normalized_id}.display_name"),
            responsibility=_required_string(value.get("responsibility"), f"agents.{normalized_id}.responsibility"),
            provider=provider,
            base_url=base_url,
            model=model,
            api_key_env=api_key_env,
            api_key=api_key,
            capabilities=tuple(item.strip() for item in capabilities),
            system_prompt=str(value.get("system_prompt", "")).strip(),
            enabled=enabled,
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
