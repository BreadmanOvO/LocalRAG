from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from agent.memory import SessionRetrievalMemory, TaskMemoryPolicy, TaskMemoryStore
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


def load_agent_system_prompt() -> str:
    """加载 Agent 系统提示词"""
    prompt_path = get_abs_path("prompts/agent_system.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


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
    ):
        self.session_id = validate_session_id(session_id)
        self.task_id = validate_task_id(task_id or session_id)
        self.retrieval_memory = SessionRetrievalMemory()
        self.task_memory_store = task_memory_store or TaskMemoryStore()
        self.task_memory_policy = TaskMemoryPolicy(enabled=task_memory_enabled)
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
        )

    def _graph_config(self) -> dict:
        return {"configurable": {"thread_id": self.session_id}}

    def get_task_memory(self):
        return self.task_memory_store.get_task(self.task_id)

    def set_task_memory_enabled(self, enabled: bool) -> None:
        self.task_memory_policy.enabled = bool(enabled)

    def clear_task_memory(self) -> None:
        self.task_memory_store.clear_task(self.task_id)
        self.task_memory_store.ensure_task(self.task_id)

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
        """流式执行问答，逐步返回结果"""
        try:
            for chunk in self.agent_graph.stream(
                {"messages": [("user", query)]},
                config=self._graph_config(),
                stream_mode="updates",
            ):
                for _node_name, node_output in chunk.items():
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            if msg.type == "ai":
                                tool_calls = getattr(msg, "tool_calls", []) or []
                                if tool_calls:
                                    for tool_call in tool_calls:
                                        yield f"[工具] {tool_call.get('name', 'unknown')}\n"
                                elif getattr(msg, "content", None):
                                    yield msg.content
                            elif msg.type == "tool":
                                tool_name = getattr(msg, "name", None) or "unknown"
                                yield f"[工具结果] {tool_name} 已完成\n"
        except Exception:
            yield "抱歉，处理过程中出现错误，请重试。"
