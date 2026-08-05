import logging
import time
from functools import partial

from langchain.agents import create_agent
from langchain.agents.middleware.model_call_limit import ModelCallLimitExceededError
from langchain.agents.middleware.tool_call_limit import ToolCallLimitExceededError
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError

from agent.context import ConversationCompressor
from agent.context.compressor import parse_and_validate_summary
from agent.context.middleware import ConversationContextMiddleware
from agent.context.store import ConversationContextStore
from agent.context.models import ConversationCompressionError
from agent.execution import (
    AgentExecutionBudget,
    DEFAULT_AGENT_EXECUTION_BUDGET,
    DuplicateToolCallError,
    NoProgressLimitExceededError,
)
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
from config.provider_factory import build_agent_chat_model, build_summary_chat_model
from core.chat_history import get_history
from core.source_evidence import SourceEvidenceService
from model_gateway import (
    CircuitBreaker,
    LocalModelGateway,
    OpenAICompatibleClient,
)
from utils.path_tools import get_abs_path
from utils.session import validate_session_id, validate_task_id


DEFAULT_AGENT_RECURSION_LIMIT = DEFAULT_AGENT_EXECUTION_BUDGET.recursion_limit
logger = logging.getLogger(__name__)


def _execution_error_code(exc: Exception) -> str:
    if isinstance(exc, ConversationCompressionError):
        return ConversationCompressionError.error_code
    if isinstance(exc, DuplicateToolCallError):
        return "duplicate_tool_call"
    if isinstance(exc, NoProgressLimitExceededError):
        return "no_progress_limit"
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
        model_event = AgentEvent(
            kind="model_completed",
            status="completed",
            elapsed_ms=_elapsed_ms(started_at),
        )
        tool_calls = getattr(message, "tool_calls", []) or []
        if tool_calls:
            events = [model_event]
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
                model_event,
                AgentEvent(
                    kind="answer_delta",
                    content=str(content),
                    status="streaming",
                    elapsed_ms=_elapsed_ms(started_at),
                )
            ]
        return [model_event]

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
        context_middleware: ConversationContextMiddleware | None = None,
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
            duplicate_tool_call_detection=budget.duplicate_tool_call_detection,
            no_progress_limit=budget.no_progress_limit,
            recursion_limit=(
                budget.recursion_limit if recursion_limit is None else int(recursion_limit)
            ),
        )
        self.recursion_limit = self.execution_budget.recursion_limit
        if context_middleware is not None and not isinstance(
            context_middleware,
            ConversationContextMiddleware,
        ):
            raise TypeError(
                "context_middleware must be a ConversationContextMiddleware or None"
            )
        if (
            context_middleware is not None
            and context_middleware.session_id != self.session_id
        ):
            raise ValueError("context_middleware session_id must match session_id")
        self.context_disabled_reason = ""
        self.local_model_gateway = None
        self.summary_client = None
        self.evidence_service = evidence_service or SourceEvidenceService()
        self.task_memory_store.ensure_task(self.task_id)

        runtime_config = None
        if chat_model is None or context_middleware is None:
            try:
                runtime_config = load_runtime_config()
            except Exception:
                if chat_model is None:
                    raise
                self.context_disabled_reason = "runtime_config_unavailable"

        if chat_model is None:
            assert runtime_config is not None
            chat_model = build_agent_chat_model(runtime_config, temperature=0.7)
        self.chat_model = chat_model

        self.local_model_gateway = self._build_local_model_gateway(runtime_config)
        rag_service_factory = None
        if (
            rag_service is None
            and self.local_model_gateway is not None
            and self._local_rag_enabled(runtime_config)
        ):
            rag_service_factory = partial(
                self._build_local_rag_service,
                runtime_config,
            )

        self.tools = [
            build_rag_search_tool(
                self.session_id,
                self.retrieval_memory,
                rag_service=rag_service,
                rag_service_factory=rag_service_factory,
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

        if context_middleware is None:
            context_middleware = self._build_context_middleware(runtime_config)
        self.context_middleware = context_middleware

        system_prompt = load_agent_system_prompt()
        self.agent_graph = create_agent(
            model=self.chat_model,
            tools=self.tools,
            system_prompt=system_prompt,
            checkpointer=checkpointer or InMemorySaver(),
            middleware=self.execution_budget.build_middleware(
                progress_token=self._execution_progress_token,
                prefix=(context_middleware,) if context_middleware is not None else (),
            ),
        )

    @staticmethod
    def _local_rag_enabled(runtime_config) -> bool:
        local_config = getattr(runtime_config, "local_model_gateway", None)
        return bool(
            local_config is not None
            and getattr(local_config, "rag_generation_enabled", False)
        )

    def _build_local_model_gateway(self, runtime_config):
        if runtime_config is None:
            return None
        local_config = getattr(runtime_config, "local_model_gateway", None)
        if local_config is None or not (
            getattr(local_config, "rag_generation_enabled", False)
            or getattr(local_config, "conversation_summary_enabled", False)
        ):
            return None
        try:
            client = OpenAICompatibleClient(
                local_config.base_url,
                model=local_config.model,
                api_token=local_config.api_token,
                connect_timeout_seconds=local_config.connect_timeout_seconds,
                read_timeout_seconds=local_config.read_timeout_seconds,
            )
            return LocalModelGateway(
                client,
                breaker=CircuitBreaker(
                    failure_threshold=local_config.circuit_failure_threshold,
                    reset_seconds=local_config.circuit_reset_seconds,
                ),
            )
        except Exception:
            logger.exception("Local model gateway setup failed")
            return None

    def _build_local_rag_service(self, runtime_config):
        from core.rag import RagService
        from model_gateway.langchain_adapter import LocalGatewayChatModel

        if self.local_model_gateway is None:
            raise RuntimeError("local model gateway is unavailable")
        fallback_model = build_agent_chat_model(runtime_config)
        return RagService(
            runtime_config=runtime_config,
            gateway=LocalGatewayChatModel(
                self.local_model_gateway,
                fallback_model,
            ),
        )

    def _build_context_middleware(self, runtime_config):
        if runtime_config is None:
            return None
        local_config = getattr(runtime_config, "local_model_gateway", None)
        if local_config is None or not local_config.conversation_summary_enabled:
            self.context_disabled_reason = "disabled_by_config"
            return None
        if self.local_model_gateway is None:
            self.context_disabled_reason = "context_setup_failed"
            return None

        try:
            from model_gateway.summary_adapter import LocalGatewaySummaryClient

            summary_client = LocalGatewaySummaryClient(
                self.local_model_gateway,
                build_summary_chat_model(runtime_config, temperature=0.0),
                summary_validator=parse_and_validate_summary,
                task_id=self.task_id,
            )
            store = ConversationContextStore()
            compressor = ConversationCompressor(store, summary_client)
            middleware = ConversationContextMiddleware(
                session_id=self.session_id,
                compressor=compressor,
                store=store,
                history=get_history(self.session_id),
                protected_source_ids=self._protected_source_ids,
            )
            self.summary_client = summary_client
            return middleware
        except Exception:
            self.context_disabled_reason = "context_setup_failed"
            logger.exception("Conversation context middleware setup failed")
            return None

    def _protected_source_ids(self) -> tuple[str, ...]:
        try:
            memory = self.task_memory_store.get_task(self.task_id)
        except Exception:
            return ()
        source_ids = (
            *getattr(memory, "retrieved_sources", ()),
            *getattr(memory, "confirmed_sources", ()),
        )
        return tuple(dict.fromkeys(str(source_id) for source_id in source_ids if source_id))

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

    def get_conversation_context(self):
        if self.context_middleware is None:
            return None
        return self.context_middleware.get_snapshot()

    def set_task_memory_enabled(self, enabled: bool) -> None:
        self.task_memory_policy.enabled = bool(enabled)

    def clear_task_memory(self) -> None:
        self.task_memory_store.clear_task(self.task_id)
        self.task_memory_store.ensure_task(self.task_id)

    def get_retrieval_snapshot(self):
        return self.retrieval_memory.recall(self.session_id)

    def _execution_progress_token(self) -> dict:
        task_memory = self.get_task_memory()

        def values(field_name: str) -> tuple[str, ...]:
            value = getattr(task_memory, field_name, ())
            if not isinstance(value, (list, tuple, set)):
                return ()
            return tuple(sorted(str(item) for item in value))

        topic = getattr(task_memory, "topic", "")
        memory_state = {
            "topic": topic if isinstance(topic, str) else "",
            "searched_queries": values("searched_queries"),
            "retrieved_sources": values("retrieved_sources"),
            "confirmed_sources": values("confirmed_sources"),
            "findings": values("findings"),
            "evidence_gaps": values("evidence_gaps"),
            "open_questions": values("open_questions"),
        }

        retrieval = self.get_retrieval_snapshot()
        document_fields = ("source_id", "locator", "chunk_order", "chunk_strategy")
        documents = [
            {field: document.get(field) for field in document_fields}
            for document in (getattr(retrieval, "documents", ()) or ())
            if isinstance(document, dict)
        ]
        documents.sort(
            key=lambda document: tuple(
                str(document.get(field) or "") for field in document_fields
            )
        )
        retrieval_state = {
            "query": str(getattr(retrieval, "query", "") or ""),
            "documents": documents,
        }
        return {"task_memory": memory_state, "retrieval": retrieval_state}

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
                "duplicate_tool_call",
                "no_progress_limit",
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
