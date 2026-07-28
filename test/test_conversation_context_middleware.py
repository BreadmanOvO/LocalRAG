import copy
import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from unittest import mock

from langchain.agents.middleware import ModelRequest, ModelResponse
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    message_to_dict,
)

from agent.context.compressor import CompressionOutcome, ConversationCompressor
from agent.context.middleware import ConversationContextMiddleware
from agent.context.models import ConversationSummary, SummaryFinding
from agent.context.store import (
    ConversationContextStore,
    ConversationSummarySnapshot,
    SummaryCommitCommand,
)
from core.chat_history import FileChatMessageHistory


def _summary() -> ConversationSummary:
    return ConversationSummary(
        goal="Answer the deployment question",
        user_constraints=("Use local inference",),
        confirmed_findings=(
            SummaryFinding(claim="The adapter is E6.1", evidence_ids=("e-1",)),
        ),
        decisions=("Use Q4_K_M",),
        unresolved_questions=("Measure P95 latency",),
        failed_attempts=("Base-only deployment was rejected",),
        referenced_source_ids=("s-1",),
    )


def _outcome(
    recent_messages,
    *,
    summary=None,
    revision=0,
    tokens_after=80,
) -> CompressionOutcome:
    return CompressionOutcome(
        status="compressed" if revision else "not_needed",
        summary=summary,
        recent_messages=tuple(recent_messages),
        revision=revision,
        tokens_before=160,
        tokens_after=tokens_after,
        messages_before=4,
        messages_after=len(recent_messages),
        summary_model="summary-model" if revision else "",
        fallback_reason="",
        error_code="",
    )


class ConversationContextMiddlewareTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.history = FileChatMessageHistory(
            "session-context",
            str(Path(self.temp_dir.name) / "history"),
        )
        self.compressor = mock.create_autospec(ConversationCompressor, instance=True)
        self.store = mock.create_autospec(ConversationContextStore, instance=True)

    def _middleware(self, **overrides):
        values = {
            "session_id": "session-context",
            "compressor": self.compressor,
            "store": self.store,
            "history": self.history,
        }
        values.update(overrides)
        return ConversationContextMiddleware(**values)

    @staticmethod
    def _request(messages, *, system_message=None, tools=None):
        return ModelRequest(
            model=mock.Mock(),
            messages=list(messages),
            system_message=system_message,
            tools=tools,
        )

    def test_real_request_override_preserves_original_and_complete_transcript(self):
        old = HumanMessage(content="old", id="human-old")
        recent = HumanMessage(
            content=[{"type": "text", "text": "recent"}],
            id="human-recent",
            additional_kwargs={"nested": {"value": 1}},
        )
        original_system = SystemMessage(
            content="original system",
            id="system-1",
            name="policy",
            additional_kwargs={"a": 1},
            response_metadata={"b": 2},
        )
        request = self._request(
            [old, recent],
            system_message=original_system,
            tools=[{"type": "function", "function": {"name": "lookup"}}],
        )
        original_messages = copy.deepcopy([message_to_dict(item) for item in request.messages])
        original_system_dict = copy.deepcopy(message_to_dict(request.system_message))
        self.compressor.prepare_model_view.return_value = _outcome(
            [recent],
            summary=_summary(),
            revision=2,
        )
        response_message = AIMessage(content="answer", id="response-1")
        response = ModelResponse(result=[response_message])
        received = []

        def handler(overridden):
            received.append(overridden)
            overridden.messages[0].additional_kwargs["nested"]["value"] = 99
            return response

        returned = self._middleware().wrap_model_call(request, handler)

        self.assertIs(response, returned)
        self.assertIsNot(request, received[0])
        self.assertEqual(["human-recent"], [item.id for item in received[0].messages])
        self.assertIn("Conversation summary revision 2", received[0].system_message.content)
        self.assertIn('"referenced_source_ids":["s-1"]', received[0].system_message.content)
        self.assertEqual("system-1", received[0].system_message.id)
        self.assertEqual("policy", received[0].system_message.name)
        self.assertEqual({"a": 1}, received[0].system_message.additional_kwargs)
        self.assertEqual({"b": 2}, received[0].system_message.response_metadata)
        self.assertEqual(original_messages, [message_to_dict(item) for item in request.messages])
        self.assertEqual(original_system_dict, message_to_dict(request.system_message))
        self.assertEqual(
            ["human-old", "human-recent", "response-1"],
            [item.id for item in self.history.messages],
        )
        call = self.compressor.prepare_model_view.call_args
        self.assertEqual("session-context", call.kwargs["session_id"])
        self.assertEqual(["human-old", "human-recent"], [m.id for m in call.kwargs["messages"]])
        self.assertEqual(request.tools, call.kwargs["tools"])

    def test_structured_system_content_remains_structured_and_metadata_is_preserved(self):
        system = SystemMessage(
            content=[{"type": "text", "text": "original"}],
            id="system-structured",
            additional_kwargs={"mode": "strict"},
        )
        human = HumanMessage(content="question", id="human-1")
        self.compressor.prepare_model_view.return_value = _outcome(
            [human], summary=_summary(), revision=1
        )
        received = []

        self._middleware().wrap_model_call(
            self._request([human], system_message=system),
            lambda request: received.append(request) or AIMessage(content="answer", id="a-1"),
        )

        content = received[0].system_message.content
        self.assertIsInstance(content, list)
        self.assertEqual({"type": "text", "text": "original"}, content[0])
        self.assertEqual("text", content[-1]["type"])
        self.assertIn("Conversation summary revision 1", content[-1]["text"])
        self.assertEqual("system-structured", received[0].system_message.id)
        self.assertEqual({"mode": "strict"}, received[0].system_message.additional_kwargs)

    def test_no_summary_deep_copies_system_and_keeps_none_unchanged(self):
        system = SystemMessage(
            content=[{"type": "text", "text": "original"}],
            id="system-1",
            additional_kwargs={"nested": {"value": 1}},
        )
        human = HumanMessage(content="question", id="human-1")
        self.compressor.prepare_model_view.return_value = _outcome([human])
        received = []
        original_system = copy.deepcopy(message_to_dict(system))

        def mutate_system(request):
            received.append(request)
            request.system_message.content[0]["text"] = "mutated"
            request.system_message.additional_kwargs["nested"]["value"] = 99
            return AIMessage(content="answer", id="a-1")

        self._middleware().wrap_model_call(
            self._request([human], system_message=system),
            mutate_system,
        )

        self.assertIsNot(system, received[0].system_message)
        self.assertEqual(original_system, message_to_dict(system))

        self._middleware().wrap_model_call(
            self._request([human], system_message=None),
            lambda request: received.append(request)
            or AIMessage(content="answer", id="a-2"),
        )
        self.assertIsNone(received[1].system_message)

    def test_same_session_middlewares_serialize_complete_turns(self):
        second_history = FileChatMessageHistory(
            "session-context",
            str(Path(self.temp_dir.name) / "history"),
        )
        first_compressor = mock.create_autospec(ConversationCompressor, instance=True)
        second_compressor = mock.create_autospec(ConversationCompressor, instance=True)
        for compressor in (first_compressor, second_compressor):
            compressor.prepare_model_view.side_effect = lambda **kwargs: _outcome(
                [kwargs["messages"][-1]]
            )
        first_middleware = self._middleware(compressor=first_compressor)
        second_middleware = self._middleware(
            compressor=second_compressor,
            history=second_history,
        )
        first_entered = threading.Event()
        second_entered = threading.Event()
        release_first = threading.Event()

        def first_handler(_):
            first_entered.set()
            if not release_first.wait(2):
                raise TimeoutError("first handler was not released")
            return AIMessage(content="a1", id="a1")

        def second_handler(_):
            second_entered.set()
            return AIMessage(content="a2", id="a2")

        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(
                first_middleware.wrap_model_call,
                self._request([HumanMessage(content="h1", id="h1")]),
                first_handler,
            )
            self.assertTrue(first_entered.wait(1))
            second = executor.submit(
                second_middleware.wrap_model_call,
                self._request([HumanMessage(content="h2", id="h2")]),
                second_handler,
            )
            second_entered_before_release = second_entered.wait(0.2)
            release_first.set()
            first.result(timeout=2)
            second.result(timeout=2)

        self.assertFalse(second_entered_before_release)
        self.assertEqual(
            ["h1", "a1", "h2", "a2"],
            [message.id for message in self.history.messages],
        )

    def test_different_sessions_do_not_share_turn_lock(self):
        first_history = FileChatMessageHistory(
            "session-parallel-1",
            str(Path(self.temp_dir.name) / "parallel-1"),
        )
        second_history = FileChatMessageHistory(
            "session-parallel-2",
            str(Path(self.temp_dir.name) / "parallel-2"),
        )

        def middleware(session_id, history):
            compressor = mock.create_autospec(ConversationCompressor, instance=True)
            compressor.prepare_model_view.side_effect = lambda **kwargs: _outcome(
                [kwargs["messages"][-1]]
            )
            return ConversationContextMiddleware(
                session_id=session_id,
                compressor=compressor,
                store=self.store,
                history=history,
            )

        first_middleware = middleware("session-parallel-1", first_history)
        second_middleware = middleware("session-parallel-2", second_history)
        first_entered = threading.Event()
        second_entered = threading.Event()
        release_first = threading.Event()

        def first_handler(_):
            first_entered.set()
            if not release_first.wait(2):
                raise TimeoutError("first handler was not released")
            return AIMessage(content="a1", id="a1")

        def second_handler(_):
            second_entered.set()
            return AIMessage(content="a2", id="a2")

        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(
                first_middleware.wrap_model_call,
                self._request([HumanMessage(content="h1", id="h1")]),
                first_handler,
            )
            self.assertTrue(first_entered.wait(1))
            second = executor.submit(
                second_middleware.wrap_model_call,
                self._request([HumanMessage(content="h2", id="h2")]),
                second_handler,
            )
            ran_in_parallel = second_entered.wait(1)
            release_first.set()
            first.result(timeout=2)
            second.result(timeout=2)

        self.assertTrue(ran_in_parallel)

    def test_model_response_and_direct_ai_message_replays_are_idempotent(self):
        human = HumanMessage(content="question", id="human-1")
        self.compressor.prepare_model_view.return_value = _outcome([human])
        middleware = self._middleware()
        request = self._request([human])
        wrapped = ModelResponse(result=[AIMessage(content="first", id="answer-1")])

        middleware.wrap_model_call(request, lambda _: wrapped)
        middleware.wrap_model_call(request, lambda _: wrapped)
        direct = AIMessage(content="second", id="answer-2")
        middleware.wrap_model_call(request, lambda _: direct)
        middleware.wrap_model_call(request, lambda _: direct)

        self.assertEqual(
            ["human-1", "answer-1", "answer-2"],
            [item.id for item in self.history.messages],
        )

    def test_valid_usage_is_recorded_for_model_response_and_direct_ai_message(self):
        human = HumanMessage(content="question", id="human-1")
        self.compressor.prepare_model_view.return_value = _outcome(
            [human], summary=_summary(), revision=3, tokens_after=77
        )
        middleware = self._middleware()
        request = self._request([human])

        middleware.wrap_model_call(
            request,
            lambda _: ModelResponse(
                result=[
                    AIMessage(
                        content="first",
                        id="response-1",
                        usage_metadata={
                            "input_tokens": 72,
                            "output_tokens": 8,
                            "total_tokens": 80,
                        },
                    )
                ]
            ),
        )
        middleware.wrap_model_call(
            request,
            lambda _: AIMessage(
                content="second",
                response_metadata={"request_id": "provider-request-2"},
                usage_metadata={
                    "input_tokens": 70,
                    "output_tokens": 9,
                    "total_tokens": 79,
                },
            ),
        )

        first, second = [call.args[0] for call in self.store.record_token_observation.call_args_list]
        self.assertEqual(
            ("session-context", 3, "revision-3:response-1"),
            (first.session_id, first.revision, first.request_id),
        )
        self.assertEqual((77, 72, 8), (first.estimated_input_tokens, first.actual_input_tokens, first.actual_output_tokens))
        self.assertEqual("revision-3:provider-request-2", second.request_id)

    def test_provider_request_id_is_idempotent_per_revision_in_real_store(self):
        database_path = Path(self.temp_dir.name) / "context.sqlite3"
        store = ConversationContextStore(database_path)
        for expected_revision, covered_ids in (
            (0, ("id:covered-1",)),
            (1, ("id:covered-1", "id:covered-2")),
        ):
            store.commit_summary(
                SummaryCommitCommand(
                    session_id="session-context",
                    summary=_summary(),
                    covered_message_ids=covered_ids,
                    tokens_before=160,
                    tokens_after=80,
                    messages_before=4,
                    messages_after=2,
                    summary_model="summary-model",
                    compression_reason="trigger_threshold",
                ),
                expected_revision=expected_revision,
            )

        compressor = mock.create_autospec(ConversationCompressor, instance=True)
        compressor.prepare_model_view.side_effect = [
            _outcome([], summary=_summary(), revision=1),
            _outcome([], summary=_summary(), revision=1),
            _outcome([], summary=_summary(), revision=2),
        ]
        middleware = self._middleware(compressor=compressor, store=store)
        answer = AIMessage(
            content="answer",
            id="provider-response",
            usage_metadata={"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
        )

        middleware.wrap_model_call(
            self._request([HumanMessage(content="h1", id="h1")]),
            lambda _: answer,
        )
        middleware.wrap_model_call(
            self._request([HumanMessage(content="h1", id="h1")]),
            lambda _: answer,
        )
        middleware.wrap_model_call(
            self._request([HumanMessage(content="h2", id="h2")]),
            lambda _: answer,
        )

        with closing(sqlite3.connect(database_path)) as connection:
            rows = connection.execute(
                """
                SELECT revision, request_id
                FROM conversation_token_observations
                ORDER BY revision
                """
            ).fetchall()
        self.assertEqual(
            [
                (1, "revision-1:provider-response"),
                (2, "revision-2:provider-response"),
            ],
            rows,
        )

    def test_long_provider_id_keeps_revision_namespace_when_hashed(self):
        human = HumanMessage(content="question", id="human-1")
        self.compressor.prepare_model_view.return_value = _outcome(
            [human], summary=_summary(), revision=5
        )
        answer = AIMessage(
            content="answer",
            id="x" * 300,
            usage_metadata={"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
        )

        self._middleware().wrap_model_call(self._request([human]), lambda _: answer)

        request_id = self.store.record_token_observation.call_args.args[0].request_id
        self.assertRegex(
            request_id,
            r"^revision-5:response-sha256:[0-9a-f]{64}$",
        )
        self.assertLessEqual(len(request_id), 256)

    def test_fallback_request_id_is_deterministic_and_replay_safe(self):
        human = HumanMessage(content="question", id="human-1")
        self.compressor.prepare_model_view.return_value = _outcome(
            [human], summary=_summary(), revision=4
        )
        middleware = self._middleware()
        answer = AIMessage(
            content="answer",
            usage_metadata={"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
        )

        middleware.wrap_model_call(self._request([human]), lambda _: answer)
        middleware.wrap_model_call(self._request([human]), lambda _: answer)

        commands = [call.args[0] for call in self.store.record_token_observation.call_args_list]
        self.assertEqual(commands[0].request_id, commands[1].request_id)
        self.assertLessEqual(len(commands[0].request_id), 256)
        self.assertIn("revision-4", commands[0].request_id)

    def test_missing_or_invalid_usage_skips_observation(self):
        human = HumanMessage(content="question", id="human-1")
        self.compressor.prepare_model_view.return_value = _outcome(
            [human], summary=_summary(), revision=2
        )
        middleware = self._middleware()
        invalid = AIMessage(
            content="invalid",
            usage_metadata={"input_tokens": -1, "output_tokens": 2, "total_tokens": 1},
        )

        middleware.wrap_model_call(self._request([human]), lambda _: AIMessage(content="missing"))
        middleware.wrap_model_call(self._request([human]), lambda _: invalid)

        self.store.record_token_observation.assert_not_called()

    def test_observation_failure_does_not_change_response_or_history(self):
        human = HumanMessage(content="question", id="human-1")
        self.compressor.prepare_model_view.return_value = _outcome(
            [human], summary=_summary(), revision=2
        )
        self.store.record_token_observation.side_effect = RuntimeError("database unavailable")
        answer = AIMessage(
            content="answer",
            id="answer-1",
            usage_metadata={"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
        )

        with self.assertLogs("agent.context.middleware", level="ERROR"):
            returned = self._middleware().wrap_model_call(
                self._request([human]), lambda _: answer
            )

        self.assertIs(answer, returned)
        self.assertEqual(["human-1", "answer-1"], [item.id for item in self.history.messages])

    def test_snapshot_and_protected_id_providers_are_forwarded(self):
        human = HumanMessage(content="question", id="human-1")
        self.compressor.prepare_model_view.return_value = _outcome([human])
        snapshot = mock.Mock(spec=ConversationSummarySnapshot)
        self.store.get_summary.return_value = snapshot
        middleware = self._middleware(
            protected_evidence_ids=lambda: ["e-1"],
            protected_source_ids=lambda: ("s-1",),
        )

        middleware.wrap_model_call(
            self._request([human]), lambda _: AIMessage(content="answer", id="a-1")
        )

        call = self.compressor.prepare_model_view.call_args
        self.assertEqual(("e-1",), call.kwargs["protected_evidence_ids"])
        self.assertEqual(("s-1",), call.kwargs["protected_source_ids"])
        self.assertIs(snapshot, middleware.get_snapshot())
        self.store.get_summary.assert_called_once_with("session-context")

    def test_constructor_and_provider_inputs_are_strict(self):
        with self.assertRaisesRegex(ValueError, "session_id"):
            ConversationContextMiddleware(
                session_id="../bad",
                compressor=self.compressor,
                store=self.store,
                history=self.history,
            )
        with self.assertRaisesRegex(ValueError, "history"):
            self._middleware(session_id="different-session")
        with self.assertRaisesRegex(TypeError, "compressor"):
            self._middleware(compressor=object())
        with self.assertRaisesRegex(TypeError, "store"):
            self._middleware(store=object())
        with self.assertRaisesRegex(TypeError, "history"):
            self._middleware(history=object())
        for field_name in ("protected_evidence_ids", "protected_source_ids"):
            with self.subTest(field_name=field_name):
                with self.assertRaisesRegex(TypeError, field_name):
                    self._middleware(**{field_name: 0})
        with self.assertRaisesRegex(TypeError, "protected_evidence_ids"):
            self._middleware(protected_evidence_ids=lambda: "e-1").wrap_model_call(
                self._request([HumanMessage(content="q", id="h-1")]),
                lambda _: AIMessage(content="a", id="a-1"),
            )
        with self.assertRaisesRegex(RuntimeError, "provider failed"):
            self._middleware(
                protected_source_ids=lambda: (_ for _ in ()).throw(
                    RuntimeError("provider failed")
                )
            ).wrap_model_call(
                self._request([HumanMessage(content="q", id="h-1")]),
                lambda _: AIMessage(content="a", id="a-1"),
            )


if __name__ == "__main__":
    unittest.main()
