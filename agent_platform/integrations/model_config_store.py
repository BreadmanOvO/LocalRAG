"""Persistent, UI-editable model and Agent configuration.

The store is deliberately permissive: a profile may start with empty provider,
URL, and model fields so the Company page can be used as the first setup step.
Execution remains strict in ``load_cloud_agents`` and refuses enabled entries
that are not ready.
"""

from __future__ import annotations

import json
import os
import ipaddress
import socket
import tempfile
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .multi_agent_config import CloudModelProfile, DEFAULT_CONFIG, profile_matches_requirements


class ModelConfigError(ValueError):
    pass


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ModelConfigError("model discovery redirects are not allowed")


def _id(value: str, field: str) -> str:
    normalized = str(value or "").strip()
    if not normalized or len(normalized) > 100 or "/" in normalized or "\\" in normalized:
        raise ModelConfigError(f"{field} must be a non-empty short identifier")
    return normalized


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ModelConfigError("list fields must contain non-empty strings")
    return [item.strip() for item in value]


class ModelConfigStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or os.environ.get("LOCALRAG_MULTI_AGENT_CONFIG", DEFAULT_CONFIG)).resolve()

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"contract_version": "agent-platform-cloud-v1", "model_profiles": {}, "agents": {}}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ModelConfigError("multi-agent config is malformed") from exc
        if not isinstance(raw, dict) or raw.get("contract_version") != "agent-platform-cloud-v1":
            raise ModelConfigError("unsupported multi-agent config contract")
        raw.setdefault("model_profiles", {})
        raw.setdefault("agents", {})
        if not isinstance(raw["model_profiles"], dict) or not isinstance(raw["agents"], dict):
            raise ModelConfigError("model_profiles and agents must be objects")
        return raw

    def save(self, raw: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix="multi-agent-", suffix=".json", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(raw, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def public(self) -> dict[str, Any]:
        raw = self.load()
        profiles = []
        for profile_id, value in raw["model_profiles"].items():
            item = dict(value)
            item["profile_id"] = profile_id
            item["api_key"] = ""
            env_name = str(value.get("api_key_env", "")).strip()
            item["has_api_key"] = bool(value.get("api_key") or (env_name and os.environ.get(env_name, "").strip()))
            item.setdefault("display_name", profile_id)
            item.setdefault("provider", "")
            item.setdefault("base_url", "")
            item.setdefault("model", "")
            item.setdefault("api_key_env", "")
            item.setdefault("capabilities", [])
            item.setdefault("modalities", ["text"])
            item.setdefault("scenarios", [])
            item.setdefault("tier", "standard")
            item.setdefault("max_concurrency", 4)
            item.setdefault("enabled", False)
            issues = self._profile_issues(item)
            if not item.get("enabled", False):
                issues.append("未启用")
            item["ready"] = not issues
            item["readiness_issues"] = issues
            profiles.append(item)
        agents = []
        for agent_id, value in raw["agents"].items():
            item = dict(value)
            item["agent_id"] = agent_id
            item.pop("api_key", None)
            item.setdefault("display_name", agent_id)
            item.setdefault("responsibility", "")
            item.setdefault("model_binding_mode", "fixed")
            item.setdefault("model_profile", "")
            item.setdefault("tier", "standard")
            item.setdefault("capabilities", [])
            item.setdefault("modalities", ["text"])
            item.setdefault("auto_tier", "")
            item.setdefault("auto_capabilities", [])
            item.setdefault("auto_modalities", [])
            item.setdefault("auto_scenarios", [])
            item.setdefault("system_prompt", "")
            item.setdefault("enabled", False)
            issues = self._agent_issues(item, raw["model_profiles"])
            item["ready"] = not issues
            item["readiness_issues"] = issues
            agents.append(item)
        return {"contract_version": raw["contract_version"], "profiles": profiles, "agents": agents}

    @staticmethod
    def _profile_issues(item: Mapping[str, Any]) -> list[str]:
        labels = {"provider": "提供商", "base_url": "URL", "model": "模型名称"}
        issues = [f"未设置{label}" for field, label in labels.items() if not str(item.get(field, "")).strip()]
        if not item.get("has_api_key"):
            issues.append("未设置 API Key")
        return issues

    @staticmethod
    def _agent_issues(item: Mapping[str, Any], profiles: Mapping[str, Any]) -> list[str]:
        issues: list[str] = []
        if not item.get("enabled", False):
            issues.append("未启用")
        binding_mode = str(item.get("model_binding_mode", "fixed")).strip().lower() or "fixed"
        if binding_mode not in {"fixed", "auto"}:
            issues.append("模型绑定方式无效")
            return issues
        profile_id = str(item.get("model_profile", "")).strip()
        if not str(item.get("display_name", "")).strip():
            issues.append("未设置显示名称")
        if not str(item.get("responsibility", "")).strip():
            issues.append("未设置职责")
        if binding_mode == "fixed":
            if not profile_id:
                issues.append("未绑定模型")
            elif profile_id not in profiles:
                issues.append("绑定模型不存在")
            else:
                profile = dict(profiles[profile_id])
                env_name = str(profile.get("api_key_env", "")).strip()
                profile["has_api_key"] = bool(profile.get("api_key") or (env_name and os.environ.get(env_name, "").strip()))
                if ModelConfigStore._profile_issues(profile):
                    issues.append("绑定模型尚未就绪")
                if not profile.get("enabled", False):
                    issues.append("绑定模型未启用")
        elif profile_id:
            issues.append("自动路由不能绑定固定模型")
        elif not ModelConfigStore._matching_auto_profiles(item, profiles):
            issues.append("没有符合自动路由条件的已就绪模型")
        return issues

    @staticmethod
    def _matching_auto_profiles(item: Mapping[str, Any], profiles: Mapping[str, Any]) -> list[str]:
        """Use the same explicit constraints as Runtime without reading keys."""
        matches: list[str] = []
        for profile_id, raw_profile in profiles.items():
            if not isinstance(raw_profile, Mapping):
                continue
            profile = dict(profiles[profile_id])
            env_name = str(profile.get("api_key_env", "")).strip()
            profile["has_api_key"] = bool(profile.get("api_key") or (env_name and os.environ.get(env_name, "").strip()))
            if not profile.get("enabled", False) or ModelConfigStore._profile_issues(profile):
                continue
            candidate = CloudModelProfile(
                profile_id=str(profile_id),
                display_name=str(profile.get("display_name", profile_id)),
                provider=str(profile.get("provider", "")),
                base_url=str(profile.get("base_url", "")),
                model=str(profile.get("model", "")),
                api_key_env=env_name,
                api_key="",
                capabilities=tuple(_list(profile.get("capabilities", []))),
                modalities=tuple(_list(profile.get("modalities", ["text"])) or ["text"]),
                scenarios=tuple(_list(profile.get("scenarios", []))),
                tier=str(profile.get("tier", "standard")).strip() or "standard",
                max_concurrency=int(profile.get("max_concurrency", 4)),
                enabled=True,
            )
            if profile_matches_requirements(
                candidate,
                tier=str(item.get("auto_tier", "")).strip(),
                capabilities=_list(item.get("auto_capabilities", [])),
                modalities=_list(item.get("auto_modalities", [])),
                scenarios=_list(item.get("auto_scenarios", [])),
            ):
                matches.append(str(profile_id))
        return matches

    def upsert_profile(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        profile_id = _id(str(payload.get("profile_id", "")), "profile_id")
        raw = self.load()
        current = raw["model_profiles"].get(profile_id, {})
        item = {
            "display_name": str(payload.get("display_name", current.get("display_name", profile_id))).strip(),
            "provider": str(payload.get("provider", current.get("provider", ""))).strip(),
            "base_url": self._normalize_base_url(str(payload.get("base_url", current.get("base_url", ""))).strip()),
            "model": str(payload.get("model", current.get("model", ""))).strip(),
            "api_key_env": str(payload.get("api_key_env", current.get("api_key_env", ""))).strip(),
            "api_key": "" if payload.get("clear_api_key") else (str(payload.get("api_key", "")) or current.get("api_key", "")),
            "capabilities": _list(payload.get("capabilities", current.get("capabilities", []))),
            "modalities": _list(payload.get("modalities", current.get("modalities", ["text"]))) or ["text"],
            "scenarios": _list(payload.get("scenarios", current.get("scenarios", []))),
            "tier": str(payload.get("tier", current.get("tier", "standard"))).strip() or "standard",
            "max_concurrency": int(payload.get("max_concurrency", current.get("max_concurrency", 4))),
            "enabled": bool(payload.get("enabled", current.get("enabled", False))),
        }
        if item["max_concurrency"] < 1:
            raise ModelConfigError("max_concurrency must be positive")
        raw["model_profiles"][profile_id] = item
        self.save(raw)
        return self.public()

    def delete_profile(self, profile_id: str) -> dict[str, Any]:
        profile_id = _id(profile_id, "profile_id")
        raw = self.load()
        if profile_id not in raw["model_profiles"]:
            raise KeyError(profile_id)
        if any(
            value.get("model_profile") == profile_id
            and str(value.get("model_binding_mode", "fixed")).strip().lower() != "auto"
            for value in raw["agents"].values()
        ):
            raise ModelConfigError("model profile is still bound to an agent")
        del raw["model_profiles"][profile_id]
        self.save(raw)
        return self.public()

    def upsert_agent(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        agent_id = _id(str(payload.get("agent_id", "")), "agent_id")
        raw = self.load()
        current = raw["agents"].get(agent_id, {})
        binding_mode = str(payload.get("model_binding_mode", current.get("model_binding_mode", "fixed"))).strip().lower() or "fixed"
        if binding_mode not in {"fixed", "auto"}:
            raise ModelConfigError("model_binding_mode must be fixed or auto")
        profile_id = str(payload.get("model_profile", current.get("model_profile", ""))).strip()
        if binding_mode == "auto" and profile_id:
            raise ModelConfigError("automatic model binding cannot set model_profile")
        if binding_mode == "fixed" and profile_id and profile_id not in raw["model_profiles"]:
            raise ModelConfigError(f"unknown model profile: {profile_id}")
        raw["agents"][agent_id] = {
            "display_name": str(payload.get("display_name", current.get("display_name", agent_id))).strip() or agent_id,
            "responsibility": str(payload.get("responsibility", current.get("responsibility", ""))).strip(),
            "model_binding_mode": binding_mode,
            "model_profile": profile_id,
            "tier": str(payload.get("tier", current.get("tier", "standard"))).strip() or "standard",
            "capabilities": _list(payload.get("capabilities", current.get("capabilities", []))),
            "modalities": _list(payload.get("modalities", current.get("modalities", ["text"]))) or ["text"],
            "auto_tier": str(payload.get("auto_tier", current.get("auto_tier", ""))).strip(),
            "auto_capabilities": _list(payload.get("auto_capabilities", current.get("auto_capabilities", []))),
            "auto_modalities": _list(payload.get("auto_modalities", current.get("auto_modalities", []))),
            "auto_scenarios": _list(payload.get("auto_scenarios", current.get("auto_scenarios", []))),
            "system_prompt": str(payload.get("system_prompt", current.get("system_prompt", ""))).strip(),
            "enabled": bool(payload.get("enabled", current.get("enabled", False))),
        }
        self.save(raw)
        return self.public()

    def delete_agent(self, agent_id: str) -> dict[str, Any]:
        agent_id = _id(agent_id, "agent_id")
        raw = self.load()
        if agent_id not in raw["agents"]:
            raise KeyError(agent_id)
        del raw["agents"][agent_id]
        self.save(raw)
        return self.public()

    def discovery_key(self, profile_id: str = "", supplied_key: str = "") -> str:
        if supplied_key.strip():
            return supplied_key.strip()
        if not profile_id.strip():
            return ""
        raw = self.load()
        profile = raw["model_profiles"].get(_id(profile_id, "profile_id"))
        if not isinstance(profile, dict):
            raise ModelConfigError("model profile not found")
        inline = str(profile.get("api_key", "")).strip()
        env_name = str(profile.get("api_key_env", "")).strip()
        return inline or (os.environ.get(env_name, "").strip() if env_name else "")

    @staticmethod
    def _normalize_base_url(value: str) -> str:
        if not value:
            return ""
        parsed = urlsplit(value.rstrip("/"))
        if parsed.query or parsed.fragment:
            raise ModelConfigError("base_url must not contain query or fragment")
        path = parsed.path.rstrip("/")
        if path.endswith("/models"):
            path = path[:-7].rstrip("/")
        return parsed._replace(path=path).geturl().rstrip("/")

    @staticmethod
    def _is_safe_discovery_host(hostname: str) -> bool:
        try:
            addresses = {info[4][0] for info in socket.getaddrinfo(hostname, None)}
        except OSError as exc:
            raise ModelConfigError("model discovery host cannot be resolved") from exc
        if not addresses:
            raise ModelConfigError("model discovery host cannot be resolved")
        for address in addresses:
            parsed = ipaddress.ip_address(address)
            if parsed.is_private or parsed.is_loopback or parsed.is_link_local or parsed.is_reserved or parsed.is_unspecified:
                raise ModelConfigError("model discovery does not allow private or local addresses")
        return True

    @staticmethod
    def discover_models(base_url: str, api_key: str = "", timeout: float = 15.0) -> list[dict[str, str]]:
        value = str(base_url or "").strip().rstrip("/")
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ModelConfigError("base_url must be an http(s) URL")
        ModelConfigStore._is_safe_discovery_host(parsed.hostname)
        normalized = ModelConfigStore._normalize_base_url(value)
        url = normalized + "/models"
        request = Request(url, headers={"Accept": "application/json", **({"Authorization": f"Bearer {api_key}"} if api_key else {})})
        try:
            with build_opener(_NoRedirect).open(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise ModelConfigError(f"model discovery failed: {type(exc).__name__}") from exc
        rows = payload.get("data", payload) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            raise ModelConfigError("model discovery response has no data list")
        return [{"id": str(item.get("id", "")), "owned_by": str(item.get("owned_by", ""))} for item in rows if isinstance(item, dict) and item.get("id")]
