from __future__ import annotations

from dataclasses import dataclass

from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)


LIMIT_EXIT_BEHAVIOR = "error"


@dataclass(frozen=True)
class AgentExecutionBudget:
    """Hard per-run limits applied by the Agent graph."""

    tool_call_limit: int = 3
    model_call_limit: int = 4
    recursion_limit: int = 24

    def __post_init__(self) -> None:
        for field_name in ("tool_call_limit", "model_call_limit", "recursion_limit"):
            if getattr(self, field_name) <= 0:
                raise ValueError(f"{field_name} must be greater than zero")

    def build_middleware(self) -> list:
        return [
            ToolCallLimitMiddleware(
                run_limit=self.tool_call_limit,
                exit_behavior=LIMIT_EXIT_BEHAVIOR,
            ),
            ModelCallLimitMiddleware(
                run_limit=self.model_call_limit,
                exit_behavior=LIMIT_EXIT_BEHAVIOR,
            ),
        ]

    def to_manifest(self) -> dict:
        return {
            "middleware": [
                "ToolCallLimitMiddleware",
                "ModelCallLimitMiddleware",
            ],
            "tool_call_run_limit": self.tool_call_limit,
            "model_call_run_limit": self.model_call_limit,
            "limit_exit_behavior": LIMIT_EXIT_BEHAVIOR,
            "recursion_limit": self.recursion_limit,
        }


DEFAULT_AGENT_EXECUTION_BUDGET = AgentExecutionBudget()
