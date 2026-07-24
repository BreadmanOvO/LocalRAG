import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field
from langgraph.errors import GraphRecursionError

from agent import react_agent
from agent.memory import SessionRetrievalMemory
from agent.tools.rag_search import build_rag_search_tool
from agent.tools.show_sources import build_show_sources_tool
from core.chat_history import ChatHistoryCorruptionError, FileChatMessageHistory
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
        self.assertIs(fake_checkpointer, create_agent.call_args.kwargs["checkpointer"])
        middleware = create_agent.call_args.kwargs["middleware"]
        self.assertEqual(3, middleware[0].run_limit)
        self.assertEqual(4, middleware[1].run_limit)

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
                "recursion_limit": 24,
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
                            SimpleNamespace(type="tool", name="rag_search", content="tool result")
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
        self.assertIn("final answer", output)
        self.assertNotIn("hidden reasoning", output)
        self.assertNotIn("tool result", output)
        fake_graph.stream.assert_called_once_with(
            {"messages": [("user", "question")]},
            config={
                "configurable": {"thread_id": "session-a"},
                "recursion_limit": 24,
            },
            stream_mode="updates",
        )

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
            ["tool_started", "tool_completed", "answer_delta"],
            [event.kind for event in events],
        )
        self.assertEqual("call-1", events[0].call_id)
        self.assertEqual({"source_id": "paper-001"}, events[0].arguments)
        self.assertEqual("success", events[1].status)
        self.assertEqual("paper-001", events[1].observations[0]["source_id"])
        self.assertEqual("answer", events[2].content)
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
