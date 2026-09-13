"""D37 task-to-architecture router.

The router is deterministic and explainable. It chooses a bounded execution
shape from the task signal, while the Runtime remains the only component that
can execute or reject a strategy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Architecture = Literal["direct", "hierarchical", "swarm", "adversarial", "heterogeneous", "graph"]


@dataclass(frozen=True)
class RouteDecision:
    mode: Literal["direct", "delegate"]
    architecture: Architecture
    reason: str
    required_capabilities: tuple[str, ...] = ()
    max_agents: int = 1


class TaskRouter:
    """Select direct or delegated execution without calling a model."""

    def route(self, goal: str, *, requested_architecture: str = "auto", max_agents: int = 3) -> RouteDecision:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must not be empty")
        if type(max_agents) is not int or max_agents < 1:
            raise ValueError("max_agents must be positive")
        normalized = goal.strip().lower()
        if requested_architecture != "auto":
            if requested_architecture not in {"direct", "hierarchical", "swarm", "adversarial", "heterogeneous", "graph"}:
                raise ValueError(f"unsupported architecture: {requested_architecture}")
            mode = "direct" if requested_architecture == "direct" else "delegate"
            return RouteDecision(mode, requested_architecture, "用户显式指定协作策略", (), 1 if mode == "direct" else max(2, max_agents))
        if any(token in normalized for token in ("质疑", "反驳", "风险", "审查", "核验", "评审")):
            return RouteDecision("delegate", "adversarial", "目标包含独立复核或反例要求", ("review",), max(3, max_agents))
        if any(token in normalized for token in ("图片", "图像", "截图", "pdf", "视觉", "表格")):
            return RouteDecision("delegate", "heterogeneous", "目标需要视觉或异构能力", ("vision",), max(2, max_agents))
        if any(token in normalized for token in ("依赖", "流程图", "节点", "分支", "并行")):
            return RouteDecision("delegate", "graph", "目标显式包含步骤依赖或分支", (), max(2, max_agents))
        if any(token in normalized for token in ("各自", "多角度", "分别", "头脑风暴", "蜂群")):
            return RouteDecision("delegate", "swarm", "目标适合多个成员独立探索后汇总", (), max(2, max_agents))
        if len(normalized) <= 24:
            return RouteDecision("direct", "direct", "目标短且没有分解、复核或特殊模态信号", (), 1)
        return RouteDecision("delegate", "hierarchical", "目标长度或动词信号表明需要拆解和汇总", (), max(2, max_agents))
