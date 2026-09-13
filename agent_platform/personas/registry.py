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
    roles = (
        RoleSpec("role-assistant", "总助理", "办公室", ("澄清目标", "协调分工", "汇总结果"), ("chat", "route", "summarization")),
        RoleSpec("role-project-manager", "项目经理", "项目管理部", ("拆解里程碑", "跟踪依赖", "管理风险"), ("planning", "coordination")),
        RoleSpec("role-researcher", "研究员", "研究部", ("检索资料", "整理证据", "识别缺口"), ("rag", "analysis")),
        RoleSpec("role-architect", "架构师", "技术部", ("设计边界", "评估取舍", "制定接口"), ("architecture", "reasoning")),
        RoleSpec("role-engineer", "工程师", "技术部", ("实现方案", "编写测试", "修复缺陷"), ("coding", "testing")),
        RoleSpec("role-data-analyst", "数据分析师", "数据部", ("处理表格", "计算指标", "解释数据"), ("data", "table", "analysis")),
        RoleSpec("role-visual-analyst", "视觉分析师", "多模态部", ("理解图片", "读取图表", "定位视觉证据"), ("vision", "ocr", "visual_grounding")),
        RoleSpec("role-reviewer", "审查员", "质量部", ("交叉核验", "寻找反例", "标记风险"), ("review", "analysis")),
        RoleSpec("role-security-auditor", "安全审计员", "安全部", ("检查权限", "识别注入", "评估数据风险"), ("security", "review")),
        RoleSpec("role-writer", "报告撰写员", "交付部", ("组织结构", "统一表达", "生成交付物"), ("writing", "summarization")),
    )
    for role in roles:
        registry.add_role(role)
    registry.save_profile(PersonaProfile("persona-assistant", "role-assistant", 1, "总助理", "你是负责澄清目标、分派工作并汇总结果的总助理。"))
    registry.save_profile(PersonaProfile("persona-researcher", "role-researcher", 1, "研究员", "你是重证据、重来源的研究员。"))
    registry.save_profile(PersonaProfile("persona-reviewer", "role-reviewer", 1, "审查员", "你是谨慎、独立的质量审查员。"))
    return registry
