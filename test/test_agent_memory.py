import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from agent import react_agent
from agent.memory import SessionRetrievalMemory
from agent.tools.rag_search import build_rag_search_tool
from agent.tools.show_sources import build_show_sources_tool
from core.chat_history import FileChatMessageHistory
from utils.session import validate_session_id


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
    def test_langgraph_checkpointer_restores_previous_turn(self):
        chat_model = RecordingChatModel()
        agent = react_agent.ReactAgent(
            "session-a",
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
                chat_model=object(),
                rag_service=mock.Mock(),
                checkpointer=fake_checkpointer,
            )

        self.assertEqual("session-a", agent.session_id)
        self.assertEqual(
            ["rag_search", "show_sources", "clarify_question"],
            [tool.name for tool in agent.tools],
        )
        self.assertIs(fake_checkpointer, create_agent.call_args.kwargs["checkpointer"])

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
            config={"configurable": {"thread_id": "session-a"}},
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
            config={"configurable": {"thread_id": "session-a"}},
            stream_mode="updates",
        )


if __name__ == "__main__":
    unittest.main()
