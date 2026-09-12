"""Task profiling and execution-plan compilation for D16."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

Mode = Literal["auto", "direct", "delegate"]

@dataclass(frozen=True)
class TaskProfile:
    task_id: str
    goal: str
    requires_decomposition: bool = False
    required_capabilities: tuple[str, ...] = ()
    budget_units: int = 100

@dataclass(frozen=True)
class ArchitectureSpec:
    architecture: Literal["direct", "hierarchical", "graph"]
    max_agents: int = 1
    allow_parallel: bool = False

@dataclass(frozen=True)
class ExecutionPlan:
    plan_id: str
    task_id: str
    mode: Literal["direct", "delegate"]
    architecture: str
    members: tuple[str, ...]
    steps: tuple[str, ...]
    budget_units: int

class PlanCompiler:
    def compile(self, profile: TaskProfile, spec: ArchitectureSpec, *, mode: Mode = "auto", available_capabilities: set[str] | None = None) -> ExecutionPlan:
        if not profile.goal.strip(): raise ValueError("goal must not be empty")
        if profile.budget_units < 1: raise ValueError("budget_units must be positive")
        if spec.max_agents < 1: raise ValueError("max_agents must be positive")
        missing = set(profile.required_capabilities) - (available_capabilities or set())
        if missing and mode in {"auto", "delegate"}: raise ValueError(f"missing capabilities: {', '.join(sorted(missing))}")
        delegated = mode == "delegate" or (mode == "auto" and profile.requires_decomposition)
        if delegated and spec.max_agents < 2: raise ValueError("delegate requires max_agents >= 2")
        if not delegated and mode == "direct" and spec.architecture != "direct": raise ValueError("direct mode requires direct architecture")
        return ExecutionPlan(f"plan-{profile.task_id}", profile.task_id, "delegate" if delegated else "direct", spec.architecture if delegated else "direct", ("assistant", "researcher") if delegated else ("assistant",), ("dispatch", "collect", "summarize") if delegated else ("answer",), profile.budget_units)
