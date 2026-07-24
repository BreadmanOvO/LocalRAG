import unittest
from unittest import mock

from langchain.agents.middleware.model_call_limit import ModelCallLimitExceededError
from langchain.agents.middleware.tool_call_limit import ToolCallLimitExceededError
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from agent import react_agent
from agent.execution import AgentExecutionBudget, DEFAULT_AGENT_EXECUTION_BUDGET


class LoopingToolChatModel(BaseChatModel):
    calls: list[int] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "looping-tool-chat-model"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.calls.append(len(self.calls) + 1)
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": "show_sources",
                                "args": {},
                                "id": f"call-{len(self.calls)}",
                                "type": "tool_call",
                            }
                        ],
                    )
                )
            ]
        )


class AgentExecutionBudgetTests(unittest.TestCase):
    def test_default_budget_builds_strict_run_limit_middleware(self):
        middleware = DEFAULT_AGENT_EXECUTION_BUDGET.build_middleware()

        self.assertEqual(3, middleware[0].run_limit)
        self.assertEqual("error", middleware[0].exit_behavior)
        self.assertEqual(4, middleware[1].run_limit)
        self.assertEqual("error", middleware[1].exit_behavior)
        self.assertEqual(
            {
                "middleware": [
                    "ToolCallLimitMiddleware",
                    "ModelCallLimitMiddleware",
                ],
                "tool_call_run_limit": 3,
                "model_call_run_limit": 4,
                "limit_exit_behavior": "error",
                "recursion_limit": 24,
            },
            DEFAULT_AGENT_EXECUTION_BUDGET.to_manifest(),
        )

    def test_budget_rejects_non_positive_limits(self):
        for field_name in ("tool_call_limit", "model_call_limit", "recursion_limit"):
            values = {
                "tool_call_limit": 3,
                "model_call_limit": 4,
                "recursion_limit": 24,
            }
            values[field_name] = 0
            with self.subTest(field_name=field_name):
                with self.assertRaisesRegex(ValueError, field_name):
                    AgentExecutionBudget(**values)

    def test_tool_limit_allows_boundary_and_blocks_next_call(self):
        limiter = AgentExecutionBudget(tool_call_limit=3).build_middleware()[0]
        message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "inspect_source",
                    "args": {"source_id": "paper-001"},
                    "id": "call-3",
                    "type": "tool_call",
                }
            ],
        )

        update = limiter.after_model(
            {
                "messages": [message],
                "run_tool_call_count": {"__all__": 2},
            },
            mock.Mock(),
        )
        self.assertEqual(3, update["run_tool_call_count"]["__all__"])

        with self.assertRaises(ToolCallLimitExceededError):
            limiter.after_model(
                {
                    "messages": [message],
                    "run_tool_call_count": {"__all__": 3},
                },
                mock.Mock(),
            )

    def test_model_limit_allows_four_calls_and_blocks_fifth(self):
        limiter = AgentExecutionBudget(model_call_limit=4).build_middleware()[1]

        self.assertIsNone(limiter.before_model({"run_model_call_count": 3}, mock.Mock()))
        self.assertEqual(
            4,
            limiter.after_model(
                {"thread_model_call_count": 0, "run_model_call_count": 3},
                mock.Mock(),
            )["run_model_call_count"],
        )
        with self.assertRaises(ModelCallLimitExceededError):
            limiter.before_model({"run_model_call_count": 4}, mock.Mock())


class AgentExecutionErrorTests(unittest.TestCase):
    def _stream_error(self, exc: Exception) -> str:
        agent = react_agent.ReactAgent.__new__(react_agent.ReactAgent)
        agent.session_id = "session-a"
        agent.agent_graph = mock.Mock()
        agent.agent_graph.stream.side_effect = exc
        return "".join(agent.execute_stream("question"))

    def test_tool_limit_is_exposed_as_structured_error_code(self):
        error = ToolCallLimitExceededError(
            thread_count=4,
            run_count=4,
            thread_limit=None,
            run_limit=3,
        )

        self.assertEqual(
            "[运行错误] tool_call_limit_exceeded\n",
            self._stream_error(error),
        )

    def test_model_limit_is_exposed_as_structured_error_code(self):
        error = ModelCallLimitExceededError(
            thread_count=4,
            run_count=4,
            thread_limit=None,
            run_limit=4,
        )

        self.assertEqual(
            "[运行错误] model_call_limit_exceeded\n",
            self._stream_error(error),
        )


class AgentExecutionIntegrationTests(unittest.TestCase):
    def _build_agent(self, budget: AgentExecutionBudget) -> tuple:
        chat_model = LoopingToolChatModel()
        agent = react_agent.ReactAgent(
            "session-budget-test",
            task_id="task-budget-test",
            task_memory_store=mock.Mock(),
            evidence_service=mock.Mock(),
            chat_model=chat_model,
            rag_service=mock.Mock(),
            execution_budget=budget,
        )
        return agent, chat_model

    def test_graph_blocks_fourth_tool_call(self):
        agent, chat_model = self._build_agent(
            AgentExecutionBudget(tool_call_limit=3, model_call_limit=10)
        )

        output = "".join(agent.execute_stream("repeat the tool"))

        self.assertEqual(4, len(chat_model.calls))
        self.assertEqual(4, output.count("[工具] show_sources"))
        self.assertEqual(3, output.count("[工具结果] show_sources 已完成"))
        self.assertIn("[运行错误] tool_call_limit_exceeded", output)

    def test_graph_blocks_fifth_model_call(self):
        agent, chat_model = self._build_agent(
            AgentExecutionBudget(tool_call_limit=10, model_call_limit=4)
        )

        output = "".join(agent.execute_stream("repeat the tool"))

        self.assertEqual(4, len(chat_model.calls))
        self.assertEqual(4, output.count("[工具] show_sources"))
        self.assertEqual(4, output.count("[工具结果] show_sources 已完成"))
        self.assertIn("[运行错误] model_call_limit_exceeded", output)


if __name__ == "__main__":
    unittest.main()
