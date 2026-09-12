"""Company role catalog and immutable persona versions for D15."""
from __future__ import annotations

from dataclasses import dataclass, replace
from threading import RLock
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class RoleSpec:
    role_id: str
    name: str
    department: str
    responsibilities: tuple[str, ...]
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class PersonaProfile:
    persona_id: str
    role_id: str
    version: int
    display_name: str
    system_prompt: str
    tone: str = "professional"


@dataclass(frozen=True)
class AgentBinding:
    binding_id: str
    persona_id: str
    role_id: str
    persona_version: int
    capabilities: tuple[str, ...]


class PersonaRegistry:
    """Versioned catalog; updates create a new profile and never mutate bindings."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._roles: dict[str, RoleSpec] = {}
        self._profiles: dict[str, list[PersonaProfile]] = {}
        self._bindings: dict[str, AgentBinding] = {}

    def add_role(self, role: RoleSpec) -> RoleSpec:
        with self._lock:
            self._roles[role.role_id] = role
            return role

    def list_roles(self) -> tuple[RoleSpec, ...]:
        with self._lock:
            return tuple(sorted(self._roles.values(), key=lambda item: item.role_id))

    def save_profile(self, profile: PersonaProfile) -> PersonaProfile:
        if profile.role_id not in self._roles:
            raise ValueError(f"unknown role: {profile.role_id}")
        if not profile.system_prompt.strip():
            raise ValueError("system_prompt must not be empty")
        with self._lock:
            versions = self._profiles.setdefault(profile.persona_id, [])
            if versions and profile.version <= versions[-1].version:
                raise ValueError("persona version must increase")
            versions.append(profile)
            return profile

    def latest(self, persona_id: str) -> PersonaProfile:
        with self._lock:
            return self._profiles[persona_id][-1]

    def bind(self, persona_id: str) -> AgentBinding:
        with self._lock:
            profile = self.latest(persona_id)
            role = self._roles[profile.role_id]
            binding = AgentBinding(f"binding-{uuid4().hex}", persona_id, role.role_id, profile.version, role.capabilities)
            self._bindings[binding.binding_id] = binding
            return binding

    def list_bindings(self) -> tuple[AgentBinding, ...]:
        with self._lock:
            return tuple(self._bindings.values())


def default_registry() -> PersonaRegistry:
    registry = PersonaRegistry()
    registry.add_role(RoleSpec("role-assistant", "总助理", "办公室", ("澄清目标", "汇总结果"), ("chat", "route")))
    registry.add_role(RoleSpec("role-researcher", "研究员", "研究部", ("检索资料", "整理证据"), ("rag", "analysis")))
    registry.add_role(RoleSpec("role-reviewer", "审查员", "质量部", ("交叉核验", "标记风险"), ("review", "analysis")))
    registry.save_profile(PersonaProfile("persona-assistant", "role-assistant", 1, "总助理", "你是负责澄清目标、分派工作并汇总结果的总助理。"))
    registry.save_profile(PersonaProfile("persona-researcher", "role-researcher", 1, "研究员", "你是重证据、重来源的研究员。"))
    registry.save_profile(PersonaProfile("persona-reviewer", "role-reviewer", 1, "审查员", "你是谨慎、独立的质量审查员。"))
    return registry
