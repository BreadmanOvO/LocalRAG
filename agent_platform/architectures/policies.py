"""First executable hierarchical and graph planning policies for D17."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PolicyNode:
    node_id: str
    responsibility: str
    depends_on: tuple[str, ...] = ()

@dataclass(frozen=True)
class PolicyPlan:
    architecture: str
    nodes: tuple[PolicyNode, ...]

class HierarchicalPolicy:
    def plan(self, goal: str) -> PolicyPlan:
        if not goal.strip(): raise ValueError("goal must not be empty")
        return PolicyPlan("hierarchical", (PolicyNode("root", goal), PolicyNode("evidence", "collect evidence", ("root",)), PolicyNode("summary", "summarize", ("evidence",))))

class GraphPolicy:
    def plan(self, goal: str) -> PolicyPlan:
        if not goal.strip(): raise ValueError("goal must not be empty")
        return PolicyPlan("graph", (PolicyNode("input", goal), PolicyNode("compute", "deterministic analysis", ("input",)), PolicyNode("answer", "compose answer", ("compute",))))

def validate_dependencies(plan: PolicyPlan) -> None:
    ids = {node.node_id for node in plan.nodes}
    for node in plan.nodes:
        missing = set(node.depends_on) - ids
        if missing: raise ValueError(f"missing dependencies: {', '.join(sorted(missing))}")
