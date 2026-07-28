import unittest
from unittest import mock

from langchain.agents.middleware import (
    AgentMiddleware,
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)
from langchain.agents.middleware.model_call_limit import ModelCallLimitExceededError
from langchain.agents.middleware.tool_call_limit import ToolCallLimitExceededError
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from agent import react_agent
from agent.execution import (
    AgentExecutionBudget,
    DEFAULT_AGENT_EXECUTION_BUDGET,
    DuplicateToolCallError,
    ExecutionGuardMiddleware,
    NoProgressLimitExceededError,
)
from agent.context.models import ConversationCompressionError


class LoopingToolChatModel(BaseChatModel):
    calls: list[int] = Field(default_factory=list)
    tool_name: str = "show_sources"
    vary_arguments: bool = False

    @property
    def _llm_type(self) -> str:
        return "looping-tool-chat-model"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.calls.append(len(self.calls) + 1)
        arguments = (
            {"source_id": f"missing-{len(self.calls)}"}
            if self.vary_arguments
            else {}
        )
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content="",
                        tool_calls=[
                            {
                                "name": self.tool_name,
                                "args": arguments,
                                "id": f"call-{len(self.calls)}",
                                "type": "tool_call",
                            }
                        ],
                    )
                )
            ]
        )


class MultiTurnGuardChatModel(BaseChatModel):
    calls: list[int] = Field(default_factory=list)

    @property
    def _llm_type(self) -> str:
        return "multi-turn-guard-chat-model"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.calls.append(len(self.calls) + 1)
        last_human_index = max(
            index for index, message in enumerate(messages) if message.type == "human"
        )
        current_messages = messages[last_human_index:]
        prompt = current_messages[0].content
        tool_result_count = sum(message.type == "tool" for message in current_messages)

        if prompt == "first turn" and tool_result_count == 0:
            tool_calls = [
                {
                    "name": "show_sources",
                    "args": {},
                    "id": "first-call",
                    "type": "tool_call",
                }
            ]
            content = ""
        elif prompt == "second turn" and tool_result_count < 2:
            tool_name = "inspect_source" if tool_result_count == 0 else "show_sources"
            arguments = {"source_id": "missing-source"} if tool_result_count == 0 else {}
            tool_calls = [
                {
                    "name": tool_name,
                    "args": arguments,
                    "id": f"second-call-{tool_result_count + 1}",
                    "type": "tool_call",
                }
            ]
            content = ""
        else:
            tool_calls = []
            content = f"completed {prompt}"

        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(content=content, tool_calls=tool_calls)
                )
            ]
        )


class AgentExecutionBudgetTests(unittest.TestCase):
    def test_default_budget_builds_strict_run_limit_middleware(self):
        middleware = DEFAULT_AGENT_EXECUTION_BUDGET.build_middleware()
        tool_limiter = next(
            item for item in middleware if isinstance(item, ToolCallLimitMiddleware)
        )
        model_limiter = next(
            item for item in middleware if isinstance(item, ModelCallLimitMiddleware)
        )

        self.assertEqual(3, tool_limiter.run_limit)
        self.assertEqual("error", tool_limiter.exit_behavior)
        self.assertEqual(4, model_limiter.run_limit)
        self.assertEqual("error", model_limiter.exit_behavior)
        self.assertEqual(
            {
                "middleware": [
                    "ExecutionGuardMiddleware",
                    "ToolCallLimitMiddleware",
                    "ModelCallLimitMiddleware",
                ],
                "tool_call_run_limit": 3,
                "model_call_run_limit": 4,
                "duplicate_tool_call_detection": True,
                "no_progress_limit": 2,
                "limit_exit_behavior": "error",
                "recursion_limit": 28,
            },
            DEFAULT_AGENT_EXECUTION_BUDGET.to_manifest(),
        )

    def test_budget_rejects_non_positive_limits(self):
        for field_name in ("tool_call_limit", "model_call_limit", "recursion_limit"):
            values = {
                "tool_call_limit": 3,
                "model_call_limit": 4,
                "recursion_limit": 28,
            }
            values[field_name] = 0
            with self.subTest(field_name=field_name):
                with self.assertRaisesRegex(ValueError, field_name):
                    AgentExecutionBudget(**values)

        with self.assertRaisesRegex(ValueError, "no_progress_limit"):
            AgentExecutionBudget(no_progress_limit=0)

    def test_budget_accepts_strict_middleware_prefix_in_order(self):
        prefix = AgentMiddleware()

        middleware = DEFAULT_AGENT_EXECUTION_BUDGET.build_middleware(prefix=(prefix,))

        self.assertIs(prefix, middleware[0])
        self.assertEqual(
            [
                "AgentMiddleware",
                "ExecutionGuardMiddleware",
                "ToolCallLimitMiddleware",
                "ModelCallLimitMiddleware",
            ],
            [type(item).__name__ for item in middleware],
        )

    def test_budget_rejects_invalid_prefix_sequences_and_items(self):
        for prefix in ("middleware", 1, object()):
            with self.subTest(prefix=prefix):
                with self.assertRaisesRegex(TypeError, "prefix"):
                    DEFAULT_AGENT_EXECUTION_BUDGET.build_middleware(prefix=prefix)
        with self.assertRaisesRegex(TypeError, "AgentMiddleware"):
            DEFAULT_AGENT_EXECUTION_BUDGET.build_middleware(prefix=(object(),))

    def test_tool_limit_allows_boundary_and_blocks_next_call(self):
        limiter = ToolCallLimitMiddleware(run_limit=3, exit_behavior="error")
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
        limiter = ModelCallLimitMiddleware(run_limit=4, exit_behavior="error")

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

    def test_duplicate_call_is_exposed_as_structured_error_code(self):
        self.assertEqual(
            "[运行错误] duplicate_tool_call\n",
            self._stream_error(DuplicateToolCallError("show_sources", "signature")),
        )

    def test_no_progress_is_exposed_as_structured_error_code(self):
        self.assertEqual(
            "[运行错误] no_progress_limit\n",
            self._stream_error(NoProgressLimitExceededError(2, 2)),
        )

    def test_compression_failure_is_exposed_as_structured_error_code(self):
        self.assertEqual(
            "[运行错误] conversation_compression_failed\n",
            self._stream_error(ConversationCompressionError("hard limit")),
        )


class ExecutionGuardMiddlewareTests(unittest.TestCase):
    def test_duplicate_signature_is_canonical_and_state_is_per_run(self):
        guard = ExecutionGuardMiddleware(
            duplicate_tool_call_detection=True,
            no_progress_limit=None,
        )
        first_message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "inspect_source",
                    "args": {"source_id": "paper-001", "max_chunks": 3},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        )
        reordered_message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "inspect_source",
                    "args": {"max_chunks": 3, "source_id": "paper-001"},
                    "id": "call-2",
                    "type": "tool_call",
                }
            ],
        )

        first_run = guard.after_model({"messages": [first_message]}, mock.Mock())
        second_run = guard.after_model({"messages": [first_message]}, mock.Mock())

        self.assertEqual(
            first_run["run_tool_call_signatures"],
            second_run["run_tool_call_signatures"],
        )
        with self.assertRaises(DuplicateToolCallError):
            guard.after_model(
                {
                    "messages": [reordered_message],
                    **first_run,
                },
                mock.Mock(),
            )

    def test_plan_revision_allows_the_same_tool_call_again(self):
        guard = ExecutionGuardMiddleware(
            duplicate_tool_call_detection=True,
            no_progress_limit=None,
        )
        message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "inspect_source",
                    "args": {"source_id": "paper-001"},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        )

        first_revision = guard.after_model(
            {"messages": [message], "plan_revision": 1},
            mock.Mock(),
        )
        second_revision = guard.after_model(
            {
                "messages": [message],
                "plan_revision": 2,
                **first_revision,
            },
            mock.Mock(),
        )

        self.assertEqual(2, len(second_revision["run_tool_call_signatures"]))

    def test_reordered_source_observations_do_not_count_as_new_progress(self):
        guard = ExecutionGuardMiddleware(
            duplicate_tool_call_detection=False,
            no_progress_limit=2,
        )
        first_ai_message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "inspect_source",
                    "args": {"source_id": "paper-001"},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        )
        next_ai_message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "inspect_source",
                    "args": {"source_id": "paper-002"},
                    "id": "call-2",
                    "type": "tool_call",
                }
            ],
        )
        observations = [
            {
                "source_id": "paper-001",
                "locator": "page-1",
                "chunk_order": 0,
                "chunk_strategy": "baseline",
                "evidence_status": "inspected",
            },
            {
                "source_id": "paper-002",
                "locator": "page-2",
                "chunk_order": 0,
                "chunk_strategy": "baseline",
                "evidence_status": "inspected",
            },
        ]

        initial_state = guard.after_model({"messages": [first_ai_message]}, mock.Mock())
        first_progress = guard.after_model(
            {
                "messages": [
                    first_ai_message,
                    ToolMessage(
                        content="result",
                        tool_call_id="call-1",
                        artifact={"source_observations": observations},
                    ),
                    next_ai_message,
                ],
                **initial_state,
            },
            mock.Mock(),
        )
        reordered = guard.after_model(
            {
                "messages": [
                    next_ai_message,
                    ToolMessage(
                        content="same result",
                        tool_call_id="call-2",
                        artifact={"source_observations": list(reversed(observations))},
                    ),
                    first_ai_message,
                ],
                **first_progress,
            },
            mock.Mock(),
        )

        self.assertEqual(2, len(reordered["run_progress_fingerprints"]))
        self.assertEqual(1, reordered["run_no_progress_count"])

    def test_historical_tool_messages_only_initialize_the_run_baseline(self):
        guard = ExecutionGuardMiddleware(
            duplicate_tool_call_detection=False,
            no_progress_limit=2,
        )
        historical_tool_message = ToolMessage(
            content="old result",
            tool_call_id="historical-call",
        )
        current_ai_message = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "show_sources",
                    "args": {},
                    "id": "current-call",
                    "type": "tool_call",
                }
            ],
        )

        baseline = guard.after_model(
            {"messages": [historical_tool_message, current_ai_message]},
            mock.Mock(),
        )

        self.assertEqual(("historical-call",), baseline["run_processed_tool_call_ids"])
        self.assertEqual(0, baseline["run_no_progress_count"])


class AgentExecutionIntegrationTests(unittest.TestCase):
    @staticmethod
    def _progressing_evidence_service():
        service = mock.Mock()

        def inspect_source(source_id, max_chunks=3):
            chunk_order = int(source_id.rsplit("-", 1)[-1])
            return {
                "found": True,
                "source_id": source_id,
                "source": {
                    "source_id": source_id,
                    "title": source_id,
                    "doc_type": "paper",
                    "language": "zh",
                    "version": "1",
                    "origin_url": "local",
                },
                "chunk_count": 1,
                "chunks": [
                    {
                        "source_id": source_id,
                        "locator": f"page-{chunk_order}",
                        "chunk_order": chunk_order,
                        "chunk_strategy": "probe",
                        "content": source_id,
                    }
                ],
            }

        service.inspect_source.side_effect = inspect_source
        return service

    def _build_agent(
        self,
        budget: AgentExecutionBudget,
        *,
        chat_model: LoopingToolChatModel | None = None,
        evidence_service=None,
    ) -> tuple:
        chat_model = chat_model or LoopingToolChatModel()
        agent = react_agent.ReactAgent(
            "session-budget-test",
            task_id="task-budget-test",
            task_memory_store=mock.Mock(),
            evidence_service=evidence_service or mock.Mock(),
            chat_model=chat_model,
            rag_service=mock.Mock(),
            execution_budget=budget,
        )
        return agent, chat_model

    def test_graph_blocks_fourth_tool_call(self):
        chat_model = LoopingToolChatModel(
            tool_name="inspect_source",
            vary_arguments=True,
        )
        agent, chat_model = self._build_agent(
            AgentExecutionBudget(
                tool_call_limit=3,
                model_call_limit=10,
            ),
            chat_model=chat_model,
            evidence_service=self._progressing_evidence_service(),
        )

        output = "".join(agent.execute_stream("repeat the tool"))

        self.assertEqual(4, len(chat_model.calls))
        self.assertEqual(4, output.count("[工具] inspect_source"))
        self.assertEqual(3, output.count("[工具结果] inspect_source 已完成"))
        self.assertIn("[运行错误] tool_call_limit_exceeded", output)

    def test_graph_blocks_fifth_model_call(self):
        chat_model = LoopingToolChatModel(
            tool_name="inspect_source",
            vary_arguments=True,
        )
        agent, chat_model = self._build_agent(
            AgentExecutionBudget(
                tool_call_limit=10,
                model_call_limit=4,
            ),
            chat_model=chat_model,
            evidence_service=self._progressing_evidence_service(),
        )

        output = "".join(agent.execute_stream("repeat the tool"))

        self.assertEqual(4, len(chat_model.calls))
        self.assertEqual(4, output.count("[工具] inspect_source"))
        self.assertEqual(4, output.count("[工具结果] inspect_source 已完成"))
        self.assertIn("[运行错误] model_call_limit_exceeded", output)

    def test_graph_blocks_duplicate_tool_call_before_second_execution(self):
        agent, chat_model = self._build_agent(
            AgentExecutionBudget(tool_call_limit=10, model_call_limit=10)
        )

        output = "".join(agent.execute_stream("repeat the tool"))

        self.assertEqual(2, len(chat_model.calls))
        self.assertEqual(2, output.count("[工具] show_sources"))
        self.assertEqual(1, output.count("[工具结果] show_sources 已完成"))
        self.assertIn("[运行错误] duplicate_tool_call", output)

    def test_graph_stops_after_two_no_progress_results(self):
        chat_model = LoopingToolChatModel(
            tool_name="inspect_source",
            vary_arguments=True,
        )
        evidence_service = mock.Mock()
        evidence_service.inspect_source.side_effect = (
            lambda source_id, max_chunks=3: {
                "found": False,
                "source_id": source_id,
            }
        )
        agent, chat_model = self._build_agent(
            AgentExecutionBudget(tool_call_limit=10, model_call_limit=10),
            chat_model=chat_model,
            evidence_service=evidence_service,
        )

        output = "".join(agent.execute_stream("inspect missing sources"))

        self.assertEqual(3, len(chat_model.calls))
        self.assertEqual(3, output.count("[工具] inspect_source"))
        self.assertEqual(2, output.count("[工具结果] inspect_source 已完成"))
        self.assertIn("[运行错误] no_progress_limit", output)

    def test_new_run_ignores_tool_messages_from_the_same_thread_history(self):
        chat_model = MultiTurnGuardChatModel()
        evidence_service = mock.Mock()
        evidence_service.inspect_source.return_value = {
            "found": False,
            "source_id": "missing-source",
        }
        agent, _ = self._build_agent(
            AgentExecutionBudget(tool_call_limit=3, model_call_limit=4),
            chat_model=chat_model,
            evidence_service=evidence_service,
        )

        first_output = "".join(agent.execute_stream("first turn"))
        second_output = "".join(agent.execute_stream("second turn"))

        self.assertIn("completed first turn", first_output)
        self.assertIn("completed second turn", second_output)
        self.assertEqual(2, second_output.count("[工具结果]"))
        self.assertNotIn("[运行错误]", second_output)


if __name__ == "__main__":
    unittest.main()
