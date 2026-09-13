"""Executable cloud multi-agent team orchestration with shared context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from langchain_core.messages import HumanMessage, SystemMessage

from agent_platform.integrations.multi_agent_config import CloudAgentClient, CloudAgentSpec, load_cloud_agents


ARCHITECTURES = {"direct", "hierarchical", "swarm", "adversarial", "heterogeneous", "graph"}


@dataclass(frozen=True)
class AgentTurn:
    agent_id: str
    responsibility: str
    prompt: str
    content: str
    sequence: int


@dataclass(frozen=True)
class TeamRunResult:
    architecture: str
    status: str
    turns: tuple[AgentTurn, ...]
    final: str


Invoker = Callable[[CloudAgentSpec, Sequence[object]], str]


class CloudTeamRuntime:
    """Run bounded team strategies while passing a versioned shared brief."""

    def __init__(self, agents: Mapping[str, CloudAgentSpec], *, invoker: Invoker | None = None) -> None:
        enabled = {key: value for key, value in agents.items() if value.enabled}
        if not enabled:
            raise RuntimeError("No enabled cloud agents are configured")
        self.agents = enabled
        self._clients = {key: CloudAgentClient(value) for key, value in enabled.items()}
        self._invoker = invoker or self._invoke_client

    @classmethod
    def from_config(cls, path=None, *, environ=None) -> "CloudTeamRuntime":
        return cls(load_cloud_agents(path, environ=environ))

    def _invoke_client(self, spec: CloudAgentSpec, messages: Sequence[object]) -> str:
        return self._clients[spec.agent_id].invoke(messages)  # type: ignore[arg-type]

    def _agent(self, preferred: str, fallback: str | None = None) -> CloudAgentSpec:
        if preferred in self.agents:
            return self.agents[preferred]
        if fallback and fallback in self.agents:
            return self.agents[fallback]
        return next(iter(self.agents.values()))

    def _turn(self, spec: CloudAgentSpec, prompt: str, sequence: int) -> AgentTurn:
        messages = []
        if spec.system_prompt:
            messages.append(SystemMessage(content=spec.system_prompt))
        messages.append(HumanMessage(content=prompt))
        content = self._invoker(spec, messages)
        return AgentTurn(spec.agent_id, spec.responsibility, prompt, content, sequence)

    def execute(self, goal: str, *, architecture: str = "hierarchical", max_agents: int = 3) -> TeamRunResult:
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must not be empty")
        if architecture not in ARCHITECTURES:
            raise ValueError(f"unsupported architecture: {architecture}")
        if type(max_agents) is not int or max_agents < 1:
            raise ValueError("max_agents must be positive")
        normalized_goal = goal.strip()
        turns: list[AgentTurn] = []
        chair = self._agent("chairperson", "assistant")
        researcher = self._agent("researcher", "analyst")
        reviewer = self._agent("reviewer", "critic")
        if architecture == "direct" or max_agents == 1:
            turns.append(self._turn(chair, f"直接完成任务：{normalized_goal}\n只输出给用户的最终答复。", 1))
        elif architecture == "swarm":
            turns.append(self._turn(researcher, f"独立探索任务：{normalized_goal}\n列出事实、证据缺口和建议。", 1))
            if max_agents >= 3:
                turns.append(self._turn(reviewer, f"独立审查任务：{normalized_goal}\n提出可能的反例、风险和需要核验的点。", 2))
            shared = "\n\n".join(f"[{turn.agent_id}]\n{turn.content}" for turn in turns)
            turns.append(self._turn(chair, f"汇总蜂群共享黑板。\n目标：{normalized_goal}\n共享记录：\n{shared}\n给出有证据边界的最终结论。", len(turns) + 1))
        elif architecture == "adversarial":
            turns.append(self._turn(researcher, f"提出任务方案：{normalized_goal}\n明确依据、假设和可证伪点。", 1))
            turns.append(self._turn(reviewer, f"对以下方案逐条质疑并给出反例：\n{turns[0].content}", 2))
            turns.append(self._turn(chair, f"裁决任务：{normalized_goal}\n提案：{turns[0].content}\n质疑：{turns[1].content}\n区分已确认事实、保留争议和下一步。", 3))
        else:
            turns.append(self._turn(chair, f"为任务建立{architecture}执行计划：{normalized_goal}\n给出步骤、依赖和验收条件。", 1))
            if max_agents >= 2:
                turns.append(self._turn(researcher, f"执行以下计划中与你负责部分相关的工作，并返回事实、证据和缺口：\n{turns[0].content}", 2))
            if max_agents >= 3:
                shared = "\n\n".join(f"[{turn.agent_id}]\n{turn.content}" for turn in turns)
                turns.append(self._turn(reviewer, f"审核任务结果并汇总：{normalized_goal}\n共享记录：\n{shared}\n只输出带边界说明的最终答复。", 3))
        return TeamRunResult(architecture, "completed", tuple(turns), turns[-1].content)
