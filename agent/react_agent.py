import logging
import time

from langchain.agents import create_agent
from langchain.agents.middleware.model_call_limit import ModelCallLimitExceededError
from langchain.agents.middleware.tool_call_limit import ToolCallLimitExceededError
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError

from agent.execution import AgentExecutionBudget, DEFAULT_AGENT_EXECUTION_BUDGET
from agent.memory import SessionRetrievalMemory, TaskMemoryPolicy, TaskMemoryStore
from agent.observability import AgentEvent
from agent.tools import (
    build_rag_search_tool,
    build_compare_sources_tool,
    build_evidence_check_tool,
    build_expand_context_tool,
    build_inspect_source_tool,
    build_show_sources_tool,
    build_show_task_memory_tool,
    build_update_task_memory_tool,
    clarify_question,
)
from config.runtime_keys import load_runtime_config
from config.provider_factory import build_chat_model
from core.source_evidence import SourceEvidenceService
from utils.path_tools import get_abs_path
from utils.session import validate_session_id, validate_task_id


DEFAULT_AGENT_RECURSION_LIMIT = DEFAULT_AGENT_EXECUTION_BUDGET.recursion_limit
logger = logging.getLogger(__name__)


def _execution_error_code(exc: Exception) -> str:
    if isinstance(exc, ToolCallLimitExceededError):
        return "tool_call_limit_exceeded"
    if isinstance(exc, ModelCallLimitExceededError):
        return "model_call_limit_exceeded"
    if isinstance(exc, GraphRecursionError):
        return "graph_recursion_limit"
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return "model_request_failed"
    error_type = type(exc)
    if error_type.__module__.split(".", 1)[0] in {"httpcore", "httpx", "openai"} and (
        "timeout" in error_type.__name__.lower()
        or "connection" in error_type.__name__.lower()
        or error_type.__name__ in {"APIError", "InternalServerError", "RateLimitError"}
    ):
        return "model_request_failed"
    return "agent_execution_failed"


def load_agent_system_prompt() -> str:
    """加载 Agent 系统提示词"""
    prompt_path = get_abs_path("prompts/agent_system.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def _elapsed_ms(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)


def _events_from_message(message, started_at: float) -> list[AgentEvent]:
    if message.type == "ai":
        tool_calls = getattr(message, "tool_calls", []) or []
        if tool_calls:
            events = []
            for tool_call in tool_calls:
                arguments = tool_call.get("args") or {}
                if not isinstance(arguments, dict):
                    arguments = {"value": str(arguments)}
                events.append(
                    AgentEvent(
                        kind="tool_started",
                        tool_name=tool_call.get("name", "unknown"),
                        call_id=str(tool_call.get("id") or ""),
                        arguments=arguments,
                        status="running",
                        elapsed_ms=_elapsed_ms(started_at),
                    )
                )
            return events
        content = getattr(message, "content", None)
        if content:
            return [
                AgentEvent(
                    kind="answer_delta",
                    content=str(content),
                    status="streaming",
                    elapsed_ms=_elapsed_ms(started_at),
                )
            ]
        return []

    if message.type != "tool":
        return []
    artifact = getattr(message, "artifact", None)
    raw_observations = (
        artifact.get("source_observations") or []
        if isinstance(artifact, dict)
        else []
    )
    observations = tuple(item for item in raw_observations if isinstance(item, dict))
    return [
        AgentEvent(
            kind="tool_completed",
            tool_name=getattr(message, "name", None) or "unknown",
            call_id=str(getattr(message, "tool_call_id", None) or ""),
            status=str(getattr(message, "status", None) or "success"),
            elapsed_ms=_elapsed_ms(started_at),
            observations=observations,
        )
    ]


class ReactAgent:
    def __init__(
        self,
        session_id: str,
        *,
        task_id: str | None = None,
        task_memory_store: TaskMemoryStore | None = None,
        task_memory_enabled: bool = True,
        evidence_service: SourceEvidenceService | None = None,
        chat_model=None,
        rag_service=None,
        checkpointer=None,
        execution_budget: AgentExecutionBudget | None = None,
        recursion_limit: int | None = None,
    ):
        self.session_id = validate_session_id(session_id)
        self.task_id = validate_task_id(task_id or session_id)
        self.retrieval_memory = SessionRetrievalMemory()
        self.task_memory_store = task_memory_store or TaskMemoryStore()
        self.task_memory_policy = TaskMemoryPolicy(enabled=task_memory_enabled)
        budget = execution_budget or DEFAULT_AGENT_EXECUTION_BUDGET
        self.execution_budget = AgentExecutionBudget(
            tool_call_limit=budget.tool_call_limit,
            model_call_limit=budget.model_call_limit,
            recursion_limit=(
                budget.recursion_limit if recursion_limit is None else int(recursion_limit)
            ),
        )
        self.recursion_limit = self.execution_budget.recursion_limit
        self.evidence_service = evidence_service or SourceEvidenceService()
        self.task_memory_store.ensure_task(self.task_id)

        if chat_model is None:
            runtime_config = load_runtime_config()
            chat_model = build_chat_model(runtime_config, temperature=0.7)
        self.chat_model = chat_model

        self.tools = [
            build_rag_search_tool(
                self.session_id,
                self.retrieval_memory,
                rag_service=rag_service,
                task_id=self.task_id,
                task_memory_store=self.task_memory_store,
                task_memory_policy=self.task_memory_policy,
            ),
            build_show_sources_tool(self.session_id, self.retrieval_memory),
            build_inspect_source_tool(self.evidence_service),
            build_expand_context_tool(self.evidence_service),
            build_compare_sources_tool(self.evidence_service),
            build_evidence_check_tool(
                self.session_id,
                self.retrieval_memory,
                self.evidence_service,
            ),
            build_show_task_memory_tool(
                self.task_id,
                self.task_memory_store,
                self.task_memory_policy,
            ),
            build_update_task_memory_tool(
                self.task_id,
                self.task_memory_store,
                self.task_memory_policy,
            ),
            clarify_question,
        ]

        system_prompt = load_agent_system_prompt()
        self.agent_graph = create_agent(
            model=self.chat_model,
            tools=self.tools,
            system_prompt=system_prompt,
            checkpointer=checkpointer or InMemorySaver(),
            middleware=self.execution_budget.build_middleware(),
        )

    def _graph_config(self) -> dict:
        return {
            "configurable": {"thread_id": self.session_id},
            "recursion_limit": getattr(
                self,
                "recursion_limit",
                DEFAULT_AGENT_RECURSION_LIMIT,
            ),
        }

    def get_task_memory(self):
        return self.task_memory_store.get_task(self.task_id)

    def set_task_memory_enabled(self, enabled: bool) -> None:
        self.task_memory_policy.enabled = bool(enabled)

    def clear_task_memory(self) -> None:
        self.task_memory_store.clear_task(self.task_id)
        self.task_memory_store.ensure_task(self.task_id)

    def get_retrieval_snapshot(self):
        return self.retrieval_memory.recall(self.session_id)

    def replace_task_memory_entry(
        self,
        category: str,
        old_value: str,
        new_value: str,
    ) -> None:
        if category == "topic":
            self.task_memory_store.set_topic(self.task_id, new_value)
            return
        self.task_memory_store.replace_item(
            self.task_id,
            category,
            old_value,
            new_value,
        )

    def delete_task_memory_entry(self, category: str, value: str) -> None:
        if category == "topic":
            self.task_memory_store.set_topic(self.task_id, "")
            return
        self.task_memory_store.remove_item(self.task_id, category, value)

    def execute(self, query: str) -> str:
        """执行单次问答"""
        result = self.agent_graph.invoke(
            {"messages": [("user", query)]},
            config=self._graph_config(),
        )
        messages = result.get("messages", [])
        if messages:
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.type == "ai":
                    return msg.content
        return "抱歉，处理过程中出现错误。"

    def execute_stream(self, query: str):
        """保留 M4 runner 使用的文本流协议。"""
        for event in self.execute_events(query):
            if event.kind == "tool_started":
                yield f"[工具] {event.tool_name}\n"
            elif event.kind == "tool_completed":
                result_text = "失败" if event.status in {"error", "failed"} else "已完成"
                yield f"[工具结果] {event.tool_name} {result_text}\n"
            elif event.kind == "answer_delta":
                yield event.content
            elif event.kind == "error":
                yield f"[运行错误] {event.error_code or 'agent_execution_failed'}\n"

    def execute_events(self, query: str):
        """流式执行问答，仅公开可展示的结构化运行事件。"""
        started_at = time.perf_counter()
        try:
            for chunk in self.agent_graph.stream(
                {"messages": [("user", query)]},
                config=self._graph_config(),
                stream_mode="updates",
            ):
                for _node_name, node_output in chunk.items():
                    if not isinstance(node_output, dict):
                        continue
                    for msg in node_output.get("messages") or []:
                        yield from _events_from_message(msg, started_at)
        except Exception as exc:
            error_code = _execution_error_code(exc)
            if error_code in {
                "tool_call_limit_exceeded",
                "model_call_limit_exceeded",
            }:
                logger.info("Agent execution stopped: %s", error_code)
            else:
                logger.exception("Agent graph execution failed")
            yield AgentEvent(
                kind="error",
                content="抱歉，处理过程中出现错误，请重试。",
                status="error",
                error_code=error_code,
                elapsed_ms=_elapsed_ms(started_at),
            )
