import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field
from langgraph.errors import GraphRecursionError

from agent import react_agent
from agent.context.compressor import ConversationCompressor
from agent.context.middleware import ConversationContextMiddleware
from agent.context.store import ConversationContextStore
from agent.memory import SessionRetrievalMemory
from agent.tools.rag_search import build_rag_search_tool
from agent.tools.show_sources import build_show_sources_tool
from config.runtime_keys import (
    CloudModelConfig,
    EmbeddingModelConfig,
    LocalModelGatewayConfig,
    ModelRoleConfig,
    RuntimeProviderConfig,
)
from core.chat_history import (
    ChatHistoryCorruptionError,
    FileChatMessageHistory,
    message_identity,
)
from utils.session import validate_session_id, validate_task_id


class RecordingChatModel(BaseChatModel):
    calls: list[list] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "recording-chat-model"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.calls.append(list(messages))
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=f"turn-{len(self.calls)}"))]
        )


class TerminalRagChatModel(BaseChatModel):
    calls: list[list] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "terminal-rag-chat-model"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.calls.append(list(messages))
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": "rag_search",
                                "args": {"query": "BEVFormer"},
                                "id": f"rag-call-{len(self.calls)}",
                                "type": "tool_call",
                            }
                        ],
                    )
                )
            ]
        )


class SessionIdValidationTests(unittest.TestCase):
    def test_validate_session_id_accepts_project_session_formats(self):
        self.assertEqual("eval-session-sample-1", validate_session_id(" eval-session-sample-1 "))
        self.assertEqual("local_rag.v1-4", validate_session_id("local_rag.v1-4"))

    def test_validate_session_id_rejects_path_traversal(self):
        for session_id in ("../escape", "folder/session", "folder\\session", ""):
            with self.subTest(session_id=session_id):
                with self.assertRaises(ValueError):
                    validate_session_id(session_id)

    def test_validate_task_id_uses_same_safe_runtime_format(self):
        self.assertEqual("task.v1-4", validate_task_id(" task.v1-4 "))
        with self.assertRaises(ValueError):
            validate_task_id("../task")


class FileChatMessageHistoryTests(unittest.TestCase):
    def test_message_identity_prefers_stripped_explicit_id(self):
        first = HumanMessage(content="same", id=" message-1 ")
        second = HumanMessage(content="same", id="message-2")

        self.assertEqual("id:message-1", message_identity(first))
        self.assertEqual("id:message-2", message_identity(second))

    def test_message_identity_hashes_same_serialized_message_stably(self):
        first = HumanMessage(content="same semantic message")
        second = HumanMessage(content="same semantic message")

        self.assertEqual(message_identity(first), message_identity(second))
        self.assertRegex(message_identity(first), r"^sha256:[0-9a-f]{64}$")

    def test_file_history_is_isolated_by_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            first = FileChatMessageHistory("session-a", temp_dir)
            second = FileChatMessageHistory("session-b", temp_dir)

            first.add_messages([HumanMessage(content="first question")])
            second.add_messages([HumanMessage(content="second question")])
            first.add_messages([AIMessage(content="first answer")])

            self.assertEqual(
                ["first question", "first answer"],
                [message.content for message in first.messages],
            )
            self.assertEqual(
                ["second question"],
                [message.content for message in second.messages],
            )
            self.assertEqual(Path(temp_dir).resolve() / "session-a", first.file_path)

    def test_file_history_rejects_unsafe_session_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                FileChatMessageHistory("../escape", temp_dir)

    def test_file_history_serializes_concurrent_same_session_writes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            histories = [
                FileChatMessageHistory("session-a", temp_dir),
                FileChatMessageHistory("session-a", temp_dir),
            ]
            start = threading.Barrier(2)

            def add_batch(history, prefix):
                start.wait()
                for index in range(20):
                    history.add_messages([HumanMessage(content=f"{prefix}-{index}")])

            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [
                    executor.submit(add_batch, histories[0], "first"),
                    executor.submit(add_batch, histories[1], "second"),
                ]
                for future in futures:
                    future.result()

            contents = [message.content for message in histories[0].messages]

        self.assertEqual(40, len(contents))
        self.assertEqual(40, len(set(contents)))

    def test_unique_append_deduplicates_same_explicit_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)

            history.add_messages_unique(
                [
                    HumanMessage(content="first", id="m1"),
                    HumanMessage(content="duplicate in batch", id="m1"),
                ]
            )
            history.add_messages_unique([HumanMessage(content="replayed", id="m1")])

            self.assertEqual(1, len(history.messages))
            self.assertEqual("first", history.messages[0].content)

    def test_unique_append_skips_no_id_full_history_replay(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)
            messages = [
                HumanMessage(content="question-1"),
                AIMessage(content="answer-1"),
            ]

            history.add_messages_unique(messages)
            history.add_messages_unique(messages)

            self.assertEqual(
                ["question-1", "answer-1"],
                [message.content for message in history.messages],
            )

    def test_unique_append_preserves_adjacent_single_no_id_messages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)

            history.add_messages_unique([HumanMessage(content="same")])
            history.add_messages_unique([HumanMessage(content="same")])

            stored = history.messages
            self.assertEqual(["same", "same"], [message.content for message in stored])
            self.assertEqual([None, None], [message.id for message in stored])

    def test_unique_append_preserves_single_hash_overlap_before_new_tail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)
            history.add_messages_unique([HumanMessage(content="same")])

            history.add_messages_unique(
                [
                    HumanMessage(content="same"),
                    AIMessage(content="answer"),
                ]
            )

            self.assertEqual(
                ["same", "same", "answer"],
                [message.content for message in history.messages],
            )

    def test_unique_append_skips_mixed_id_full_history_replay(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)
            messages = [
                HumanMessage(content="question-1"),
                AIMessage(content="answer-1", id="a1"),
            ]

            history.add_messages_unique(messages)
            history.add_messages_unique(messages)

            self.assertEqual(
                ["question-1", "answer-1"],
                [message.content for message in history.messages],
            )

    def test_unique_append_skips_no_id_suffix_replay_and_appends_tail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)
            history.add_messages_unique(
                [
                    HumanMessage(content="older-question"),
                    AIMessage(content="older-answer"),
                    HumanMessage(content="question-1"),
                    AIMessage(content="answer-1"),
                ]
            )

            history.add_messages_unique(
                [
                    HumanMessage(content="question-1"),
                    AIMessage(content="answer-1"),
                    HumanMessage(content="question-2"),
                ]
            )

            self.assertEqual(
                [
                    "older-question",
                    "older-answer",
                    "question-1",
                    "answer-1",
                    "question-2",
                ],
                [message.content for message in history.messages],
            )

    def test_unique_append_skips_mixed_id_suffix_replay_and_appends_tail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)
            history.add_messages_unique(
                [
                    HumanMessage(content="question-1"),
                    AIMessage(content="answer-1", id="a1"),
                    HumanMessage(content="question-2"),
                    AIMessage(content="answer-2", id="a2"),
                ]
            )

            history.add_messages_unique(
                [
                    AIMessage(content="answer-1", id="a1"),
                    HumanMessage(content="question-2"),
                    AIMessage(content="answer-2", id="a2"),
                    HumanMessage(content="question-3"),
                ]
            )

            self.assertEqual(
                ["question-1", "answer-1", "question-2", "answer-2", "question-3"],
                [message.content for message in history.messages],
            )

    def test_unique_append_preserves_repeated_content_after_intervening_message(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)
            history.add_messages_unique(
                [
                    HumanMessage(content="repeat this question"),
                    AIMessage(content="first answer"),
                ]
            )

            history.add_messages_unique([HumanMessage(content="repeat this question")])

            self.assertEqual(
                ["repeat this question", "first answer", "repeat this question"],
                [message.content for message in history.messages],
            )

    def test_unique_append_does_not_write_when_replay_adds_nothing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)
            history.add_messages_unique([HumanMessage(content="question", id="m1")])

            with mock.patch.object(history, "_write_messages") as write_messages:
                history.add_messages_unique([HumanMessage(content="replay", id="m1")])

            write_messages.assert_not_called()

    def test_unique_append_serializes_concurrent_same_explicit_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            histories = [
                FileChatMessageHistory("session-a", temp_dir),
                FileChatMessageHistory("session-a", temp_dir),
            ]
            start = threading.Barrier(2)

            def add_message(history):
                start.wait()
                history.add_messages_unique(
                    [HumanMessage(content="same graph message", id="m1")]
                )

            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(add_message, history) for history in histories]
                for future in futures:
                    future.result()

            stored = histories[0].messages

        self.assertEqual(1, len(stored))
        self.assertEqual("m1", stored[0].id)

    def test_atomic_write_preserves_previous_history_when_replace_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)
            history.add_messages([HumanMessage(content="preserved")])

            with mock.patch.object(Path, "replace", side_effect=OSError("replace failed")):
                with self.assertRaisesRegex(OSError, "replace failed"):
                    history.add_messages([AIMessage(content="not committed")])

            self.assertEqual(["preserved"], [message.content for message in history.messages])
            self.assertEqual([], list(Path(temp_dir).glob("*.tmp")))

    def test_corrupt_history_is_reported_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history = FileChatMessageHistory("session-a", temp_dir)
            history.file_path.write_text("{broken", encoding="utf-8")

            with self.assertRaises(ChatHistoryCorruptionError):
                history.add_messages([HumanMessage(content="new")])

            self.assertEqual("{broken", history.file_path.read_text(encoding="utf-8"))


class SessionRetrievalMemoryTests(unittest.TestCase):
    def test_retrieval_memory_isolated_and_defensively_copied(self):
        memory = SessionRetrievalMemory()
        documents = [{"source_id": "paper-001", "locator": "page=1", "content": "alpha"}]
        memory.remember("session-a", "question a", documents)

        documents[0]["content"] = "mutated outside"
        first_snapshot = memory.recall("session-a")
        self.assertIsNotNone(first_snapshot)
        self.assertEqual("alpha", first_snapshot.documents[0]["content"])
        self.assertIsNone(memory.recall("session-b"))

        first_snapshot.documents[0]["content"] = "mutated recall"
        self.assertEqual("alpha", memory.recall("session-a").documents[0]["content"])

    def test_rag_and_source_tools_share_only_the_bound_session(self):
        memory = SessionRetrievalMemory()
        rag_service = mock.Mock()
        rag_service.answer_with_retrieval.return_value = {
            "answer": "grounded answer",
            "retrieved_rows": [
                {
                    "source_id": "paper-030",
                    "locator": "page=2",
                    "content": "MFA latency evidence",
                }
            ],
        }

        rag_tool = build_rag_search_tool("session-a", memory, rag_service=rag_service)
        source_tool_a = build_show_sources_tool("session-a", memory)
        source_tool_b = build_show_sources_tool("session-b", memory)

        self.assertEqual("grounded answer", rag_tool.invoke({"query": "MFA latency"}))
        rag_service.answer_with_retrieval.assert_called_once_with(
            "MFA latency",
            session_id="session-a",
        )
        self.assertIn("paper-030", source_tool_a.invoke({}))
        self.assertIn("page=2", source_tool_a.invoke({}))
        self.assertEqual("当前会话暂无检索记录，请先提问。", source_tool_b.invoke({}))

    def test_rag_tool_builds_lazy_service_once(self):
        memory = SessionRetrievalMemory()
        rag_service = mock.Mock()
        rag_service.answer_with_retrieval.return_value = {
            "answer": "grounded answer",
            "retrieved_rows": [],
        }
        factory = mock.Mock(return_value=rag_service)
        rag_tool = build_rag_search_tool(
            "session-a",
            memory,
            rag_service_factory=factory,
        )

        self.assertEqual("grounded answer", rag_tool.invoke({"query": "first"}))
        self.assertEqual("grounded answer", rag_tool.invoke({"query": "second"}))

        factory.assert_called_once_with()
        self.assertEqual(2, rag_service.answer_with_retrieval.call_count)

    def test_rag_tool_returns_trace_artifact_for_tool_call(self):
        memory = SessionRetrievalMemory()
        rag_service = mock.Mock()
        rag_service.answer_with_retrieval.return_value = {
            "answer": "grounded answer",
            "retrieved_rows": [
                {
                    "source_id": "paper-001",
                    "locator": "page=1",
                    "content": "evidence",
                    "rank": 1,
                }
            ],
            "retrieval_strategy": "rrf_rerank",
            "retrieval_fallback_reason": None,
            "retrieval_errors": [],
            "retrieval_final_count": 5,
            "retrieval_candidate_count": 20,
            "generation_context_count": 8,
            "generation_route": {"actual_model": "local"},
        }
        rag_tool = build_rag_search_tool("session-a", memory, rag_service=rag_service)

        message = rag_tool.invoke(
            {
                "type": "tool_call",
                "id": "call-rag",
                "name": "rag_search",
                "args": {"query": "question"},
            }
        )

        self.assertEqual("success", message.status)
        self.assertEqual("rrf_rerank", message.artifact["trace"]["retrieval_strategy"])
        self.assertEqual(5, message.artifact["trace"]["retrieval_final_count"])
        self.assertEqual(20, message.artifact["trace"]["retrieval_candidate_count"])
        self.assertEqual(8, message.artifact["trace"]["generation_context_count"])
        self.assertEqual("paper-001", message.artifact["source_observations"][0]["source_id"])

    def test_rag_tool_converts_internal_failure_to_safe_error_code(self):
        memory = SessionRetrievalMemory()
        rag_service = mock.Mock()
        rag_service.answer_with_retrieval.side_effect = RuntimeError("private chroma path")
        rag_tool = build_rag_search_tool("session-a", memory, rag_service=rag_service)

        message = rag_tool.invoke(
            {
                "type": "tool_call",
                "id": "call-rag-failed",
                "name": "rag_search",
                "args": {"query": "question"},
            }
        )

        self.assertEqual("error", message.status)
        self.assertIn("[error_code=rag_search_failed]", message.content)
        self.assertNotIn("private chroma path", message.content)

    def test_rag_tool_keeps_answer_when_session_memory_write_fails(self):
        memory = mock.Mock(spec=SessionRetrievalMemory)
        memory.remember.side_effect = RuntimeError("private session memory path")
        rag_service = mock.Mock()
        rag_service.answer_with_retrieval.return_value = {
            "answer": "grounded answer",
            "retrieved_rows": [],
        }
        rag_tool = build_rag_search_tool("session-a", memory, rag_service=rag_service)

        message = rag_tool.invoke(
            {
                "type": "tool_call",
                "id": "call-rag-memory-failed",
                "name": "rag_search",
                "args": {"query": "question"},
            }
        )

        self.assertEqual("success", message.status)
        self.assertEqual("grounded answer", message.content)
        self.assertEqual(
            ["session_memory_write_failed"],
            message.artifact["trace"]["memory_errors"],
        )
        self.assertNotIn("private session memory path", str(message.artifact))

    def test_show_sources_converts_memory_failure_to_safe_error_code(self):
        memory = mock.Mock(spec=SessionRetrievalMemory)
        memory.recall.side_effect = RuntimeError("private session memory path")
        source_tool = build_show_sources_tool("session-a", memory)

        message = source_tool.invoke(
            {
                "type": "tool_call",
                "id": "call-sources-failed",
                "name": "show_sources",
                "args": {},
            }
        )

        self.assertEqual("error", message.status)
        self.assertIn("[error_code=source_memory_read_failed]", message.content)
        self.assertNotIn("private session memory path", message.content)


class ReactAgentSessionTests(unittest.TestCase):
    def test_system_prompt_prioritizes_explicit_source_tools(self):
        prompt = react_agent.load_agent_system_prompt()

        self.assertIn("多个明确的 source_id", prompt)
        self.assertIn("不得用 rag_search", prompt)

    def test_langgraph_checkpointer_restores_previous_turn(self):
        chat_model = RecordingChatModel()
        agent = react_agent.ReactAgent(
            "session-a",
            task_id="task-a",
            task_memory_store=mock.Mock(),
            chat_model=chat_model,
            rag_service=mock.Mock(),
        )

        self.assertEqual("turn-1", agent.execute("first question"))
        self.assertEqual("turn-2", agent.execute("follow-up question"))

        second_turn_contents = [message.content for message in chat_model.calls[1]]
        self.assertIn("first question", second_turn_contents)
        self.assertIn("turn-1", second_turn_contents)
        self.assertIn("follow-up question", second_turn_contents)

    def test_constructor_binds_tools_and_checkpointer_to_session(self):
        fake_graph = mock.Mock()
        fake_checkpointer = object()

        with (
            mock.patch.object(react_agent, "create_agent", return_value=fake_graph) as create_agent,
            mock.patch.object(react_agent, "load_agent_system_prompt", return_value="system prompt"),
        ):
            agent = react_agent.ReactAgent(
                "session-a",
                task_id="task-a",
                task_memory_store=mock.Mock(),
                chat_model=object(),
                rag_service=mock.Mock(),
                checkpointer=fake_checkpointer,
            )

        self.assertEqual("session-a", agent.session_id)
        self.assertEqual("task-a", agent.task_id)
        self.assertEqual(
            [
                "rag_search",
                "show_sources",
                "inspect_source",
                "expand_context",
                "compare_sources",
                "evidence_check",
                "show_task_memory",
                "update_task_memory",
                "clarify_question",
            ],
            [tool.name for tool in agent.tools],
        )
        self.assertTrue(agent.tools[0].return_direct)
        self.assertIs(fake_checkpointer, create_agent.call_args.kwargs["checkpointer"])
        middleware = create_agent.call_args.kwargs["middleware"]
        self.assertEqual(
            [
                "ExecutionGuardMiddleware",
                "ToolCallLimitMiddleware",
                "ModelCallLimitMiddleware",
            ],
            [type(item).__name__ for item in middleware],
        )
        self.assertEqual(3, middleware[1].run_limit)
        self.assertEqual(4, middleware[2].run_limit)

    def test_constructor_injects_context_middleware_only_when_explicit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            context_middleware = ConversationContextMiddleware(
                session_id="session-a",
                compressor=mock.create_autospec(ConversationCompressor, instance=True),
                store=mock.create_autospec(ConversationContextStore, instance=True),
                history=FileChatMessageHistory("session-a", temp_dir),
            )
            with (
                mock.patch.object(react_agent, "create_agent", return_value=mock.Mock()) as create_agent,
                mock.patch.object(react_agent, "load_agent_system_prompt", return_value="system"),
            ):
                agent = react_agent.ReactAgent(
                    "session-a",
                    task_id="task-a",
                    task_memory_store=mock.Mock(),
                    chat_model=object(),
                    rag_service=mock.Mock(),
                    context_middleware=context_middleware,
                )

        middleware = create_agent.call_args.kwargs["middleware"]
        self.assertEqual(
            [
                "ConversationContextMiddleware",
                "ExecutionGuardMiddleware",
                "ToolCallLimitMiddleware",
                "ModelCallLimitMiddleware",
            ],
            [type(item).__name__ for item in middleware],
        )
        self.assertIs(context_middleware, agent.context_middleware)

    def test_constructor_auto_builds_context_middleware_when_summary_is_enabled(self):
        local_config = SimpleNamespace(
            base_url="http://127.0.0.1:8002/v1",
            model="localrag-qwen3-4b-e6.1",
            api_token="secret",
            conversation_summary_enabled=True,
            connect_timeout_seconds=2.0,
            read_timeout_seconds=120.0,
            circuit_failure_threshold=3,
            circuit_reset_seconds=30.0,
        )
        runtime_config = SimpleNamespace(local_model_gateway=local_config)
        context_middleware = ConversationContextMiddleware.__new__(
            ConversationContextMiddleware
        )
        task_store = mock.Mock()

        with (
            mock.patch.object(react_agent, "load_runtime_config", return_value=runtime_config),
            mock.patch.object(react_agent, "OpenAICompatibleClient") as http_client,
            mock.patch.object(react_agent, "CircuitBreaker") as circuit_breaker,
            mock.patch.object(react_agent, "LocalModelGateway") as gateway,
            mock.patch.object(react_agent, "build_summary_chat_model", return_value=mock.Mock()) as cloud,
            mock.patch.object(react_agent, "ConversationContextStore") as store_factory,
            mock.patch.object(react_agent, "ConversationCompressor") as compressor_factory,
            mock.patch.object(
                react_agent,
                "ConversationContextMiddleware",
                return_value=context_middleware,
            ) as middleware_factory,
            mock.patch.object(react_agent, "get_history", return_value=mock.Mock()) as history,
            mock.patch(
                "model_gateway.summary_adapter.LocalGatewaySummaryClient"
            ) as summary_client,
            mock.patch.object(react_agent, "create_agent", return_value=mock.Mock()) as create_agent,
            mock.patch.object(react_agent, "load_agent_system_prompt", return_value="system"),
        ):
            agent = react_agent.ReactAgent(
                "session-a",
                task_id="task-a",
                task_memory_store=task_store,
                chat_model=object(),
                rag_service=mock.Mock(),
            )

        http_client.assert_called_once_with(
            local_config.base_url,
            model=local_config.model,
            api_token=local_config.api_token,
            connect_timeout_seconds=2.0,
            read_timeout_seconds=120.0,
        )
        circuit_breaker.assert_called_once_with(
            failure_threshold=3,
            reset_seconds=30.0,
        )
        gateway.assert_called_once()
        cloud.assert_called_once_with(runtime_config, temperature=0.0)
        summary_client.assert_called_once()
        store_factory.assert_called_once_with()
        compressor_factory.assert_called_once()
        history.assert_called_once_with("session-a")
        middleware_factory.assert_called_once()
        self.assertIs(context_middleware, agent.context_middleware)
        self.assertEqual("", agent.context_disabled_reason)
        self.assertIs(gateway.return_value, agent.local_model_gateway)
        self.assertIs(summary_client.return_value, agent.summary_client)
        self.assertIs(context_middleware, create_agent.call_args.kwargs["middleware"][0])

    def test_local_gateway_status_distinguishes_configuration_states(self):
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)

        self.assertIsNone(agent._build_local_model_gateway(None))
        self.assertEqual("not_configured", agent.local_model_gateway_status)

        disabled_config = SimpleNamespace(
            local_model_gateway=SimpleNamespace(
                rag_generation_enabled=False,
                conversation_summary_enabled=False,
            )
        )
        self.assertIsNone(agent._build_local_model_gateway(disabled_config))
        self.assertEqual("disabled_by_config", agent.local_model_gateway_status)

    def test_local_gateway_status_marks_setup_failure_unhealthy(self):
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        local_config = SimpleNamespace(
            base_url="http://127.0.0.1:8002/v1",
            model="localrag-qwen3-4b-e6.1",
            api_token="secret",
            rag_generation_enabled=True,
            conversation_summary_enabled=False,
            connect_timeout_seconds=2.0,
            read_timeout_seconds=120.0,
            circuit_failure_threshold=3,
            circuit_reset_seconds=30.0,
        )

        with mock.patch.object(
            react_agent,
            "OpenAICompatibleClient",
            side_effect=RuntimeError("private setup details"),
        ):
            gateway = agent._build_local_model_gateway(
                SimpleNamespace(local_model_gateway=local_config)
            )

        self.assertIsNone(gateway)
        self.assertEqual("unhealthy", agent.local_model_gateway_status)

    def test_default_rag_tool_reuses_local_gateway_and_cloud_fallback(self):
        local_config = SimpleNamespace(
            base_url="http://127.0.0.1:8002/v1",
            model="localrag-qwen3-4b-e6.1",
            api_token="secret",
            rag_generation_enabled=True,
            conversation_summary_enabled=False,
            connect_timeout_seconds=2.0,
            read_timeout_seconds=120.0,
            circuit_failure_threshold=3,
            circuit_reset_seconds=30.0,
        )
        runtime_config = SimpleNamespace(local_model_gateway=local_config)
        rag_service = mock.Mock()
        rag_service.answer_with_retrieval.return_value = {
            "answer": "local answer",
            "retrieved_rows": [],
        }
        fallback_model = object()
        gateway_adapter = object()

        with (
            mock.patch.object(react_agent, "load_runtime_config", return_value=runtime_config),
            mock.patch.object(react_agent, "OpenAICompatibleClient"),
            mock.patch.object(react_agent, "CircuitBreaker"),
            mock.patch.object(react_agent, "LocalModelGateway") as gateway,
            mock.patch.object(
                react_agent,
                "build_agent_chat_model",
                return_value=fallback_model,
            ) as build_cloud,
            mock.patch(
                "model_gateway.langchain_adapter.LocalGatewayChatModel",
                return_value=gateway_adapter,
            ) as adapter,
            mock.patch("core.rag.RagService", return_value=rag_service) as rag_factory,
            mock.patch.object(react_agent, "create_agent", return_value=mock.Mock()),
            mock.patch.object(react_agent, "load_agent_system_prompt", return_value="system"),
        ):
            agent = react_agent.ReactAgent(
                "session-a",
                task_id="task-a",
                task_memory_store=mock.Mock(),
                chat_model=object(),
            )
            answer = agent.tools[0].invoke({"query": "question"})

        self.assertEqual("local answer", answer)
        gateway.assert_called_once()
        build_cloud.assert_called_once_with(runtime_config)
        adapter.assert_called_once_with(gateway.return_value, fallback_model)
        rag_factory.assert_called_once_with(
            runtime_config=runtime_config,
            gateway=gateway_adapter,
        )
        self.assertIs(gateway.return_value, agent.local_model_gateway)

    def test_cloud_route_mode_does_not_construct_local_gateway(self):
        runtime_config = SimpleNamespace(
            model_route_mode="cloud",
            local_model_gateway=SimpleNamespace(
                rag_generation_enabled=True,
                conversation_summary_enabled=True,
            ),
        )
        with (
            mock.patch.object(react_agent, "load_runtime_config", return_value=runtime_config),
            mock.patch.object(react_agent, "build_agent_chat_model", return_value=object()),
            mock.patch.object(react_agent, "LocalModelGateway") as gateway,
            mock.patch.object(react_agent, "create_agent", return_value=mock.Mock()),
            mock.patch.object(react_agent, "load_agent_system_prompt", return_value="system"),
        ):
            agent = react_agent.ReactAgent(
                "session-cloud-route",
                task_id="task-cloud-route",
                task_memory_store=mock.Mock(),
                chat_model=object(),
            )
        gateway.assert_not_called()
        self.assertEqual("cloud", agent.model_route_mode)
        self.assertEqual("disabled_by_route", agent.local_model_gateway_status)

    def test_v2_roles_build_independent_gateways_and_reuse_equal_local_config(self):
        cloud = CloudModelConfig(
            provider="sensenova",
            api_key="cloud-secret",
            base_url="https://example.invalid/v1",
            model="cloud-chat",
        )
        shared_local = LocalModelGatewayConfig(
            base_url="http://127.0.0.1:8001/v1",
            model="shared-local",
            api_token="local-secret",
        )
        planner_local = LocalModelGatewayConfig(
            base_url="http://127.0.0.1:8003/v1",
            model="planner-local",
            api_token="planner-secret",
        )
        runtime_config = RuntimeProviderConfig(
            provider="sensenova",
            api_key=cloud.api_key,
            base_url=cloud.base_url,
            chat_model_name=cloud.model,
            embedding_model_name="models/bge-m3",
            roles={
                "planner": ModelRoleConfig("local", cloud, planner_local),
                "rag": ModelRoleConfig("local", cloud, shared_local),
                "summary": ModelRoleConfig("local", cloud, shared_local),
            },
            embedding=EmbeddingModelConfig(
                provider="local_sentence_transformer",
                model="models/bge-m3",
            ),
        )
        context_middleware = ConversationContextMiddleware.__new__(
            ConversationContextMiddleware
        )

        with (
            mock.patch.object(react_agent, "load_runtime_config", return_value=runtime_config),
            mock.patch.object(react_agent, "build_agent_chat_model", return_value=object()) as planner,
            mock.patch.object(react_agent, "OpenAICompatibleClient") as http_client,
            mock.patch.object(react_agent, "CircuitBreaker"),
            mock.patch.object(react_agent, "LocalModelGateway") as gateway,
            mock.patch.object(react_agent, "build_summary_chat_model", return_value=object()),
            mock.patch.object(
                react_agent.ReactAgent,
                "_create_context_middleware",
                return_value=context_middleware,
            ),
            mock.patch("model_gateway.summary_adapter.LocalGatewaySummaryClient"),
            mock.patch.object(react_agent, "create_agent", return_value=mock.Mock()),
            mock.patch.object(react_agent, "load_agent_system_prompt", return_value="system"),
        ):
            agent = react_agent.ReactAgent(
                "session-v2-roles",
                task_id="task-v2-roles",
                task_memory_store=mock.Mock(),
                rag_service=mock.Mock(),
            )

        planner.assert_called_once()
        planner_runtime = planner.call_args.args[0]
        self.assertEqual(0.7, planner.call_args.kwargs["temperature"])
        self.assertEqual("local", planner_runtime.role("planner").route)
        self.assertEqual("local", planner_runtime.role("rag").route)
        self.assertEqual("local", planner_runtime.role("summary").route)
        self.assertEqual(1, http_client.call_count)
        self.assertEqual(1, gateway.call_count)
        self.assertIs(agent.local_model_gateways["rag"], gateway.return_value)
        self.assertIs(agent.local_model_gateways["summary"], gateway.return_value)
        self.assertEqual(
            {"planner": "local", "rag": "local", "summary": "local"},
            agent.model_routes,
        )
        self.assertEqual(
            {"rag": "configured", "summary": "configured"},
            agent.local_model_gateway_statuses,
        )

    def test_v2_roles_keep_distinct_rag_and_summary_gateways(self):
        cloud = CloudModelConfig(
            provider="sensenova",
            api_key="cloud-secret",
            base_url="https://example.invalid/v1",
            model="cloud-chat",
        )
        rag_local = LocalModelGatewayConfig(
            base_url="http://127.0.0.1:8001/v1",
            model="rag-local",
            api_token="rag-secret",
        )
        summary_local = LocalModelGatewayConfig(
            base_url="http://127.0.0.1:8002/v1",
            model="summary-local",
            api_token="summary-secret",
        )
        runtime_config = RuntimeProviderConfig(
            provider="sensenova",
            api_key=cloud.api_key,
            base_url=cloud.base_url,
            chat_model_name=cloud.model,
            embedding_model_name="models/bge-m3",
            roles={
                "planner": ModelRoleConfig("cloud", cloud, rag_local),
                "rag": ModelRoleConfig("local", cloud, rag_local),
                "summary": ModelRoleConfig("local", cloud, summary_local),
            },
            embedding=EmbeddingModelConfig(
                provider="local_sentence_transformer",
                model="models/bge-m3",
            ),
        )
        context_middleware = ConversationContextMiddleware.__new__(
            ConversationContextMiddleware
        )
        gateways = [mock.Mock(name="rag-gateway"), mock.Mock(name="summary-gateway")]

        with (
            mock.patch.object(react_agent, "load_runtime_config", return_value=runtime_config),
            mock.patch.object(react_agent, "build_agent_chat_model", return_value=object()),
            mock.patch.object(react_agent, "OpenAICompatibleClient"),
            mock.patch.object(react_agent, "CircuitBreaker"),
            mock.patch.object(react_agent, "LocalModelGateway", side_effect=gateways) as gateway,
            mock.patch.object(react_agent, "build_summary_chat_model", return_value=object()),
            mock.patch.object(
                react_agent.ReactAgent,
                "_create_context_middleware",
                return_value=context_middleware,
            ),
            mock.patch("model_gateway.summary_adapter.LocalGatewaySummaryClient"),
            mock.patch.object(react_agent, "create_agent", return_value=mock.Mock()),
            mock.patch.object(react_agent, "load_agent_system_prompt", return_value="system"),
        ):
            agent = react_agent.ReactAgent(
                "session-v2-separate",
                task_id="task-v2-separate",
                task_memory_store=mock.Mock(),
                rag_service=mock.Mock(),
            )

        self.assertEqual(2, gateway.call_count)
        self.assertIs(agent.local_model_gateways["rag"], gateways[0])
        self.assertIs(agent.local_model_gateways["summary"], gateways[1])

    def test_get_conversation_context_returns_snapshot_or_none(self):
        without_context = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        without_context.context_middleware = None
        self.assertIsNone(without_context.get_conversation_context())

        snapshot = object()
        with_context = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        with_context.context_middleware = mock.Mock()
        with_context.context_middleware.get_snapshot.return_value = snapshot
        self.assertIs(snapshot, with_context.get_conversation_context())

    def test_constructor_rejects_context_middleware_for_another_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            context_middleware = ConversationContextMiddleware(
                session_id="session-b",
                compressor=mock.create_autospec(ConversationCompressor, instance=True),
                store=mock.create_autospec(ConversationContextStore, instance=True),
                history=FileChatMessageHistory("session-b", temp_dir),
            )
            with self.assertRaisesRegex(ValueError, "context_middleware"):
                react_agent.ReactAgent(
                    "session-a",
                    task_id="task-a",
                    task_memory_store=mock.Mock(),
                    chat_model=object(),
                    rag_service=mock.Mock(),
                    context_middleware=context_middleware,
                )

    def test_execution_progress_token_ignores_memory_and_retrieval_order(self):
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        first_memory = SimpleNamespace(
            topic="topic",
            searched_queries=("query-b", "query-a"),
            retrieved_sources=("paper-002", "paper-001"),
            confirmed_sources=(),
            findings=("finding-b", "finding-a"),
            evidence_gaps=(),
            open_questions=(),
        )
        second_memory = SimpleNamespace(
            **{
                **vars(first_memory),
                "searched_queries": tuple(reversed(first_memory.searched_queries)),
                "retrieved_sources": tuple(reversed(first_memory.retrieved_sources)),
                "findings": tuple(reversed(first_memory.findings)),
            }
        )
        first_documents = (
            {
                "source_id": "paper-002",
                "locator": "page-2",
                "chunk_order": 2,
                "chunk_strategy": "baseline",
            },
            {
                "source_id": "paper-001",
                "locator": "page-1",
                "chunk_order": 1,
                "chunk_strategy": "baseline",
            },
        )
        agent.get_task_memory = mock.Mock(side_effect=[first_memory, second_memory])
        agent.get_retrieval_snapshot = mock.Mock(
            side_effect=[
                SimpleNamespace(query="query", documents=first_documents),
                SimpleNamespace(query="query", documents=tuple(reversed(first_documents))),
            ]
        )

        first_token = agent._execution_progress_token()
        second_token = agent._execution_progress_token()

        self.assertEqual(first_token, second_token)

    def test_execute_uses_session_as_langgraph_thread_id(self):
        fake_graph = mock.Mock()
        fake_graph.invoke.return_value = {
            "messages": [AIMessage(content="final answer")],
        }
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = fake_graph

        self.assertEqual("final answer", agent.execute("question"))
        fake_graph.invoke.assert_called_once_with(
            {"messages": [("user", "question")]},
            config={
                "configurable": {"thread_id": "session-a"},
                "recursion_limit": 28,
            },
        )

    def test_execute_stream_exposes_tool_trace_without_internal_reasoning(self):
        fake_graph = mock.Mock()
        fake_graph.stream.return_value = iter(
            [
                {
                    "model": {
                        "messages": [
                            SimpleNamespace(
                                type="ai",
                                content="hidden reasoning",
                                tool_calls=[{"name": "rag_search"}],
                            )
                        ]
                    }
                },
                {
                    "tools": {
                        "messages": [
                            SimpleNamespace(
                                type="tool",
                                name="rag_search",
                                content="grounded answer",
                            )
                        ]
                    }
                },
                {
                    "model": {
                        "messages": [SimpleNamespace(type="ai", content="final answer", tool_calls=[])]
                    }
                },
            ]
        )
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = fake_graph

        output = "".join(agent.execute_stream("question"))

        self.assertIn("[工具] rag_search", output)
        self.assertIn("[工具结果] rag_search 已完成", output)
        self.assertIn("grounded answer", output)
        self.assertNotIn("hidden reasoning", output)
        self.assertNotIn("final answer", output)
        fake_graph.stream.assert_called_once_with(
            {"messages": [("user", "question")]},
            config={
                "configurable": {"thread_id": "session-a"},
                "recursion_limit": 28,
            },
            stream_mode="updates",
        )

    def test_successful_rag_search_ends_the_real_agent_graph(self):
        chat_model = TerminalRagChatModel()
        rag_service = mock.Mock()
        rag_service.answer_with_retrieval.return_value = {
            "answer": "Grounded BEVFormer answer [paper-001]",
            "retrieved_rows": [
                {
                    "source_id": "paper-001",
                    "locator": "page=1",
                    "chunk_order": 0,
                    "chunk_strategy": "semantic",
                }
            ],
        }
        with mock.patch.object(
            react_agent,
            "load_runtime_config",
            side_effect=RuntimeError("not needed for this test"),
        ):
            agent = react_agent.ReactAgent(
                "session-terminal-rag",
                task_id="task-terminal-rag",
                task_memory_store=mock.Mock(),
                chat_model=chat_model,
                rag_service=rag_service,
            )

        events = list(agent.execute_events("介绍 BEVFormer"))

        self.assertEqual(1, len(chat_model.calls))
        self.assertEqual(
            ["model_completed", "tool_started", "tool_completed", "answer_delta"],
            [event.kind for event in events],
        )
        self.assertEqual("Grounded BEVFormer answer [paper-001]", events[-1].content)

    def test_execute_events_returns_structured_public_trace(self):
        fake_graph = mock.Mock()
        fake_graph.stream.return_value = iter(
            [
                {
                    "model": {
                        "messages": [
                            SimpleNamespace(
                                type="ai",
                                content="hidden reasoning",
                                tool_calls=[
                                    {
                                        "name": "inspect_source",
                                        "id": "call-1",
                                        "args": {"source_id": "paper-001"},
                                    }
                                ],
                            )
                        ]
                    }
                },
                {
                    "tools": {
                        "messages": [
                            SimpleNamespace(
                                type="tool",
                                name="inspect_source",
                                tool_call_id="call-1",
                                status="success",
                                content="private tool result",
                                artifact={
                                    "source_observations": [
                                        {
                                            "source_id": "paper-001",
                                            "locator": "page=1",
                                            "chunk_order": 0,
                                        }
                                    ]
                                },
                            )
                        ]
                    }
                },
                {
                    "model": {
                        "messages": [SimpleNamespace(type="ai", content="answer", tool_calls=[])]
                    }
                },
            ]
        )
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = fake_graph

        events = list(agent.execute_events("question"))

        self.assertEqual(
            [
                "model_completed",
                "tool_started",
                "tool_completed",
                "model_completed",
                "answer_delta",
            ],
            [event.kind for event in events],
        )
        self.assertEqual("call-1", events[1].call_id)
        self.assertEqual({"source_id": "paper-001"}, events[1].arguments)
        self.assertEqual("success", events[2].status)
        self.assertEqual("paper-001", events[2].observations[0]["source_id"])
        self.assertEqual("answer", events[4].content)
        self.assertNotIn("hidden reasoning", str([event.to_dict() for event in events]))
        self.assertNotIn("private tool result", str([event.to_dict() for event in events]))

    def test_execute_stream_marks_failed_tool_result(self):
        fake_graph = mock.Mock()
        fake_graph.stream.return_value = iter(
            [
                {
                    "tools": {
                        "messages": [
                            SimpleNamespace(
                                type="tool",
                                name="inspect_source",
                                tool_call_id="call-1",
                                status="error",
                                content="safe failure",
                            )
                        ]
                    }
                }
            ]
        )
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = fake_graph

        output = "".join(agent.execute_stream("question"))

        self.assertEqual("[工具结果] inspect_source 失败\n", output)

    def test_execute_events_extracts_tool_error_code_and_trace_details(self):
        fake_graph = mock.Mock()
        fake_graph.stream.return_value = iter(
            [
                {
                    "tools": {
                        "messages": [
                            SimpleNamespace(
                                type="tool",
                                name="rag_search",
                                tool_call_id="call-1",
                                status="error",
                                content="[error_code=tool_timeout] safe failure",
                                artifact={"trace": {"retrieval_strategy": "dense_rerank"}},
                            )
                        ]
                    }
                }
            ]
        )
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = fake_graph

        events = list(agent.execute_events("question"))

        self.assertEqual("tool_timeout", events[0].error_code)
        self.assertEqual("dense_rerank", events[0].details["retrieval_strategy"])

    def test_failed_rag_search_stops_before_an_unsupported_answer(self):
        fake_graph = mock.Mock()
        fake_graph.stream.return_value = iter(
            [
                {
                    "tools": {
                        "messages": [
                            ToolMessage(
                                name="rag_search",
                                tool_call_id="call-1",
                                status="error",
                                content="[error_code=rag_search_failed] safe failure",
                            )
                        ]
                    }
                },
                {
                    "model": {
                        "messages": [
                            AIMessage(content="unsupported answer", tool_calls=[])
                        ]
                    }
                },
            ]
        )
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = fake_graph

        events = list(agent.execute_events("question"))

        self.assertEqual(
            ["tool_completed", "error"],
            [event.kind for event in events],
        )
        self.assertEqual("rag_search_failed", events[-1].error_code)
        self.assertEqual(
            react_agent.RAG_SEARCH_UNAVAILABLE_MESSAGE,
            events[-1].content,
        )
        self.assertNotIn("unsupported answer", str([event.to_dict() for event in events]))

    def test_execute_with_a_failed_rag_search_hides_later_model_content(self):
        fake_graph = mock.Mock()
        fake_graph.invoke.return_value = {
            "messages": [
                ToolMessage(
                    name="rag_search",
                    tool_call_id="call-1",
                    status="error",
                    content="[error_code=tool_timeout] safe failure",
                ),
                AIMessage(content="unsupported answer"),
            ],
        }
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = fake_graph

        answer = agent.execute("question")

        self.assertEqual(react_agent.RAG_SEARCH_UNAVAILABLE_MESSAGE, answer)
        self.assertNotIn("unsupported answer", answer)

    def test_execute_does_not_reuse_a_prior_turn_rag_failure(self):
        fake_graph = mock.Mock()
        fake_graph.invoke.return_value = {
            "messages": [
                HumanMessage(content="old question"),
                ToolMessage(
                    name="rag_search",
                    tool_call_id="old-call",
                    status="error",
                    content="[error_code=rag_search_failed] safe failure",
                ),
                AIMessage(content="old failure message"),
                HumanMessage(content="new question"),
                AIMessage(content="current answer"),
            ],
        }
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = fake_graph

        self.assertEqual("current answer", agent.execute("new question"))

    def test_execute_stream_marks_graph_recursion_without_exposing_exception(self):
        fake_graph = mock.Mock()
        fake_graph.stream.side_effect = GraphRecursionError("private graph details")
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = fake_graph

        output = "".join(agent.execute_stream("question"))

        self.assertEqual("[运行错误] graph_recursion_limit\n", output)
        self.assertNotIn("private graph details", output)


if __name__ == "__main__":
    unittest.main()
