import copy
import sqlite3
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent.context.compressor import (
    CompressionOutcome,
    ConversationCompressor,
    FallbackSummaryClient,
    SummaryClientResult,
    SummaryRequest,
    parse_and_validate_summary,
    parse_summary,
    validate_summary,
)
from agent.context.models import (
    CompressionPolicy,
    ConversationCompressionError,
    ConversationSummary,
    SummaryFinding,
)
from agent.context.store import (
    ConversationContextStore,
    ConversationRevisionConflictError,
    ConversationSummarySnapshot,
    SummaryCommitCommand,
)
from core.chat_history import message_identity


SUMMARY_FIELDS = {
    "goal",
    "user_constraints",
    "confirmed_findings",
    "decisions",
    "unresolved_questions",
    "failed_attempts",
    "referenced_source_ids",
}


def summary_payload(**overrides):
    payload = {
        "goal": "Answer the current question",
        "user_constraints": [],
        "confirmed_findings": [],
        "decisions": [],
        "unresolved_questions": [],
        "failed_attempts": [],
        "referenced_source_ids": [],
    }
    payload.update(overrides)
    return payload


def summary_request(*, previous=None, evidence=(), sources=(), messages=()):
    return SummaryRequest(
        previous_summary=previous,
        messages=tuple(messages),
        allowed_evidence_ids=frozenset(evidence),
        allowed_source_ids=frozenset(sources),
        input_token_limit=40960,
    )


class FakeSummaryClient:
    def __init__(self, payload=None, error=None, model_id="fake-summary", callback=None):
        self.payload = payload
        self.error = error
        self.model_id = model_id
        self.callback = callback
        self.requests = []

    def summarize(self, request):
        self.requests.append(request)
        if self.error is not None:
            raise self.error
        payload = self.callback(request) if self.callback else self.payload
        return SummaryClientResult(payload=payload, model_id=self.model_id)


class ScriptedConflictStore:
    def __init__(self, conflicts):
        self.conflicts = conflicts
        self.snapshot = None
        self.commit_calls = 0

    def get_summary(self, session_id):
        return self.snapshot

    def commit_summary(self, command, expected_revision):
        self.commit_calls += 1
        if self.commit_calls <= self.conflicts:
            revision = self.commit_calls
            self.snapshot = ConversationSummarySnapshot(
                session_id=command.session_id,
                revision=revision,
                summary=ConversationSummary(goal=f"persisted-{revision}"),
                covered_message_ids=(f"other-{revision}",),
                tokens_before=1,
                tokens_after=1,
                messages_before=1,
                messages_after=1,
                summary_model="concurrent-model",
                compression_reason="concurrent",
                fallback_reason="",
                created_at="2026-07-28T00:00:00+00:00",
                updated_at="2026-07-28T00:00:00+00:00",
            )
            raise ConversationRevisionConflictError(
                command.session_id,
                expected_revision,
                revision,
            )
        revision = expected_revision + 1
        self.snapshot = ConversationSummarySnapshot(
            session_id=command.session_id,
            revision=revision,
            summary=command.summary,
            covered_message_ids=command.covered_message_ids,
            tokens_before=command.tokens_before,
            tokens_after=command.tokens_after,
            messages_before=command.messages_before,
            messages_after=command.messages_after,
            summary_model=command.summary_model,
            compression_reason=command.compression_reason,
            fallback_reason=command.fallback_reason,
            created_at="2026-07-28T00:00:00+00:00",
            updated_at="2026-07-28T00:00:00+00:00",
        )
        return self.snapshot


class FailingCommitStore:
    def get_summary(self, session_id):
        return None

    def commit_summary(self, command, expected_revision):
        raise sqlite3.OperationalError("database unavailable")


class MutatingSummaryClient:
    def __init__(self):
        self.requests = []

    def summarize(self, request):
        self.requests.append(request)
        request.messages[0].content = "tampered content"
        request.messages[0].id = "tampered-id"
        request.messages[0].additional_kwargs["tampered"] = True
        return SummaryClientResult(summary_payload(), "mutating-client")


class SummaryParsingTests(unittest.TestCase):
    def test_parse_summary_accepts_exact_contract_without_mutating_payload(self):
        payload = summary_payload(
            user_constraints=["Use Chinese"],
            confirmed_findings=[{"claim": "A is verified", "evidence_ids": ["e-1"]}],
            decisions=["Use A"],
            unresolved_questions=["What is the latency?"],
            failed_attempts=["Source timed out"],
            referenced_source_ids=["s-1"],
        )
        original = copy.deepcopy(payload)

        parsed = parse_summary(payload)

        self.assertEqual(original, payload)
        self.assertEqual("Answer the current question", parsed.goal)
        self.assertEqual(("Use Chinese",), parsed.user_constraints)
        self.assertEqual((SummaryFinding("A is verified", ("e-1",)),), parsed.confirmed_findings)
        self.assertEqual(("s-1",), parsed.referenced_source_ids)
        with self.assertRaises(FrozenInstanceError):
            parsed.goal = "changed"

    def test_parse_summary_requires_mapping_and_exact_seven_fields(self):
        self.assertEqual(SUMMARY_FIELDS, set(summary_payload()))
        invalid = [
            [],
            summary_payload(unknown=[]),
            {key: value for key, value in summary_payload().items() if key != "goal"},
        ]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises((TypeError, ValueError)):
                parse_summary(payload)

    def test_parse_summary_rejects_invalid_sequence_and_finding_shapes(self):
        invalid = [
            summary_payload(user_constraints="not-a-list"),
            summary_payload(decisions=[1]),
            summary_payload(confirmed_findings="not-a-list"),
            summary_payload(confirmed_findings=["not-a-finding"]),
            summary_payload(confirmed_findings=[{"claim": "x"}]),
            summary_payload(
                confirmed_findings=[{"claim": "x", "evidence_ids": "e-1"}]
            ),
            summary_payload(
                confirmed_findings=[
                    {"claim": "x", "evidence_ids": [], "unknown": True}
                ]
            ),
        ]
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises((TypeError, ValueError)):
                parse_summary(payload)

    def test_parse_summary_enforces_four_thousand_character_boundary(self):
        accepted = parse_summary(summary_payload(goal="x" * 4000))
        self.assertEqual(4000, len(accepted.goal))
        invalid = (
            summary_payload(goal="x" * 4001),
            summary_payload(user_constraints=["x" * 4001]),
            summary_payload(confirmed_findings=[{"claim": "x" * 4001, "evidence_ids": []}]),
            summary_payload(referenced_source_ids=["x" * 4001]),
        )
        for payload in invalid:
            with self.subTest(field=next(iter(payload))), self.assertRaises(ValueError):
                parse_summary(payload)

    def test_parse_summary_rejects_blank_or_duplicate_ids(self):
        invalid = (
            summary_payload(referenced_source_ids=[" "]),
            summary_payload(referenced_source_ids=["s-1", "s-1"]),
            summary_payload(confirmed_findings=[{"claim": "x", "evidence_ids": [""]}]),
            summary_payload(
                confirmed_findings=[{"claim": "x", "evidence_ids": ["e-1", "e-1"]}]
            ),
        )
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                parse_summary(payload)


class SummaryValidationTests(unittest.TestCase):
    def test_validate_rejects_fabricated_evidence_and_source_ids(self):
        invalid = (
            ConversationSummary(
                goal="g",
                confirmed_findings=(SummaryFinding("claim", ("fabricated",)),),
            ),
            ConversationSummary(goal="g", referenced_source_ids=("fabricated",)),
        )
        request = summary_request(evidence=("e-1",), sources=("s-1",))
        for summary in invalid:
            with self.subTest(summary=summary), self.assertRaises(ValueError):
                validate_summary(summary, request)

    def test_validate_preserves_previous_constraints_and_failed_attempts(self):
        previous = ConversationSummary(
            goal="g",
            user_constraints=("Use Chinese",),
            failed_attempts=("Timeout",),
        )
        for candidate in (
            ConversationSummary(goal="g", failed_attempts=("Timeout",)),
            ConversationSummary(goal="g", user_constraints=("Use Chinese",)),
        ):
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                validate_summary(candidate, summary_request(previous=previous))

    def test_validate_finding_can_be_equivalently_retained_or_exactly_decided(self):
        previous = ConversationSummary(
            goal="g",
            confirmed_findings=(SummaryFinding("A   is FAST", ("e-1",)),),
        )
        retained = ConversationSummary(
            goal="g",
            confirmed_findings=(SummaryFinding("a is fast", ("e-1",)),),
        )
        decided = ConversationSummary(goal="g", decisions=("A   is FAST",))

        validate_summary(retained, summary_request(previous=previous, evidence=("e-1",)))
        validate_summary(decided, summary_request(previous=previous, evidence=("e-1",)))
        with self.assertRaises(ValueError):
            validate_summary(
                ConversationSummary(goal="g", decisions=("a is fast",)),
                summary_request(previous=previous, evidence=("e-1",)),
            )

    def test_validate_removed_question_must_be_exact_decision_or_finding_claim(self):
        previous = ConversationSummary(goal="g", unresolved_questions=("Why?",))
        validate_summary(
            ConversationSummary(goal="g", decisions=("Why?",)),
            summary_request(previous=previous),
        )
        validate_summary(
            ConversationSummary(
                goal="g",
                confirmed_findings=(SummaryFinding("Why?"),),
            ),
            summary_request(previous=previous),
        )
        with self.assertRaises(ValueError):
            validate_summary(
                ConversationSummary(goal="g", decisions=("why?",)),
                summary_request(previous=previous),
            )

    def test_parse_and_validate_uses_the_same_contract(self):
        parsed = parse_and_validate_summary(
            summary_payload(
                confirmed_findings=[{"claim": "verified", "evidence_ids": ["e-1"]}],
                referenced_source_ids=["s-1"],
            ),
            summary_request(evidence=("e-1",), sources=("s-1",)),
        )
        self.assertEqual(("s-1",), parsed.referenced_source_ids)


class FallbackSummaryClientTests(unittest.TestCase):
    def test_primary_valid_result_does_not_call_fallback(self):
        primary = FakeSummaryClient(summary_payload(), model_id="primary")
        fallback = FakeSummaryClient(summary_payload(), model_id="fallback")
        client = FallbackSummaryClient(primary, fallback)

        result = client.summarize(summary_request())

        self.assertEqual("primary", result.model_id)
        self.assertEqual("", result.fallback_reason)
        self.assertEqual(1, len(primary.requests))
        self.assertEqual(0, len(fallback.requests))

    def test_primary_error_or_invalid_payload_calls_fallback_once(self):
        primaries = (
            FakeSummaryClient(error=TimeoutError("secret timeout")),
            FakeSummaryClient(summary_payload(unknown=[])),
        )
        for primary in primaries:
            with self.subTest(primary=primary):
                fallback = FakeSummaryClient(summary_payload(), model_id="cloud-fallback")
                result = FallbackSummaryClient(primary, fallback).summarize(summary_request())
                self.assertEqual("cloud-fallback", result.model_id)
                self.assertTrue(result.fallback_reason)
                self.assertNotIn("secret", result.fallback_reason)
                self.assertEqual(1, len(primary.requests))
                self.assertEqual(1, len(fallback.requests))

    def test_both_clients_fail_with_stable_sanitized_error(self):
        client = FallbackSummaryClient(
            FakeSummaryClient(error=ConnectionError("primary secret")),
            FakeSummaryClient(error=TimeoutError("fallback secret")),
        )
        with self.assertRaises(ConversationCompressionError) as raised:
            client.summarize(summary_request())
        self.assertEqual("conversation_compression_failed", raised.exception.error_code)
        self.assertNotIn("secret", str(raised.exception))

    def test_primary_programming_error_propagates_without_fallback(self):
        primary = FakeSummaryClient(error=AttributeError("primary bug"))
        fallback = FakeSummaryClient(summary_payload())

        with self.assertRaisesRegex(AttributeError, "primary bug"):
            FallbackSummaryClient(primary, fallback).summarize(summary_request())

        self.assertEqual(1, len(primary.requests))
        self.assertEqual(0, len(fallback.requests))

    def test_primary_runtime_error_propagates_without_fallback(self):
        primary = FakeSummaryClient(
            error=RuntimeError("programming runtime sentinel")
        )
        fallback = FakeSummaryClient(summary_payload())

        with self.assertRaisesRegex(RuntimeError, "programming runtime sentinel"):
            FallbackSummaryClient(primary, fallback).summarize(summary_request())

        self.assertEqual(1, len(primary.requests))
        self.assertEqual(0, len(fallback.requests))

    def test_fallback_programming_error_propagates(self):
        primary = FakeSummaryClient(error=TimeoutError("primary unavailable"))
        fallback = FakeSummaryClient(error=AttributeError("fallback bug"))

        with self.assertRaisesRegex(AttributeError, "fallback bug"):
            FallbackSummaryClient(primary, fallback).summarize(summary_request())

        self.assertEqual(1, len(primary.requests))
        self.assertEqual(1, len(fallback.requests))

    def test_invalid_fallback_contract_becomes_stable_error(self):
        client = FallbackSummaryClient(
            FakeSummaryClient(error=OSError("primary unavailable")),
            FakeSummaryClient(summary_payload(unknown=[])),
        )

        with self.assertRaises(ConversationCompressionError) as raised:
            client.summarize(summary_request())

        self.assertEqual("conversation_compression_failed", raised.exception.error_code)


class ConversationCompressorTests(unittest.TestCase):
    @staticmethod
    def _policy(*, context_limit=5000, target_ratio=0.15, hard_ratio=0.9):
        return CompressionPolicy(
            context_limit=context_limit,
            fixed_overhead_tokens=0,
            output_reserve_tokens=0,
            trigger_ratio=0.20,
            target_ratio=target_ratio,
            hard_limit_ratio=hard_ratio,
            recent_turns=1,
        )

    @staticmethod
    def _messages(*, long_size=1400):
        return (
            HumanMessage(content="old question " + "x" * long_size, id="m1"),
            AIMessage(content="old answer " + "y" * long_size, id="m2"),
            HumanMessage(content="recent question", id="m3"),
            AIMessage(content="recent answer", id="m4"),
        )

    @staticmethod
    def _adaptive_payload(request):
        previous = request.previous_summary
        return summary_payload(
            goal=previous.goal if previous else "Compressed goal",
            user_constraints=list(previous.user_constraints) if previous else [],
            confirmed_findings=[
                {"claim": finding.claim, "evidence_ids": list(finding.evidence_ids)}
                for finding in (previous.confirmed_findings if previous else ())
            ],
            decisions=list(previous.decisions) if previous else [],
            unresolved_questions=list(previous.unresolved_questions) if previous else [],
            failed_attempts=list(previous.failed_attempts) if previous else [],
            referenced_source_ids=list(previous.referenced_source_ids) if previous else [],
        )

    def _compressor(self, store, client, **kwargs):
        return ConversationCompressor(
            store=store,
            summary_client=client,
            policy=kwargs.pop("policy", self._policy()),
            target_model_context_limit=kwargs.pop("target_limit", 6000),
            summary_model_context_limit=kwargs.pop("summary_limit", 40960),
            **kwargs,
        )

    def test_not_needed_does_not_call_client_or_commit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            client = FakeSummaryClient(summary_payload())
            messages = (HumanMessage(content="short", id="m1"),)

            outcome = self._compressor(store, client).prepare_model_view(
                "session-a", messages
            )

        self.assertEqual("not_needed", outcome.status)
        self.assertIsNone(outcome.summary)
        self.assertEqual(messages, outcome.recent_messages)
        self.assertEqual(0, outcome.revision)
        self.assertEqual(outcome.tokens_before, outcome.tokens_after)
        self.assertEqual(1, outcome.messages_before)
        self.assertEqual(1, outcome.messages_after)
        self.assertEqual([], client.requests)

    def test_not_needed_restores_latest_summary_and_excludes_covered_messages(self):
        messages = self._messages()
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            first = self._compressor(
                store,
                FakeSummaryClient(summary_payload(goal="Persisted summary")),
            ).prepare_model_view("session-a", messages)
            unused_client = FakeSummaryClient(error=AssertionError("must not run"))

            restored = self._compressor(store, unused_client).prepare_model_view(
                "session-a", messages
            )

        self.assertEqual("compressed", first.status)
        self.assertEqual("not_needed", restored.status)
        self.assertEqual("Persisted summary", restored.summary.goal)
        self.assertEqual(1, restored.revision)
        self.assertEqual(("m3", "m4"), tuple(m.id for m in restored.recent_messages))
        self.assertEqual([], unused_client.requests)

    def test_successful_compression_persists_metrics_allowlists_and_recent_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            client = FakeSummaryClient(
                summary_payload(
                    confirmed_findings=[{"claim": "verified", "evidence_ids": ["e-1"]}],
                    referenced_source_ids=["s-1"],
                ),
                model_id="local-summary",
            )
            messages = self._messages()
            original = copy.deepcopy(messages)

            outcome = self._compressor(store, client).prepare_model_view(
                "session-a",
                messages,
                protected_evidence_ids=("e-1",),
                protected_source_ids=("s-1",),
            )
            snapshot = store.get_summary("session-a")

        self.assertEqual("compressed", outcome.status)
        self.assertEqual(1, outcome.revision)
        self.assertEqual("local-summary", outcome.summary_model)
        self.assertEqual(("m3", "m4"), tuple(message.id for message in outcome.recent_messages))
        self.assertEqual(original, messages)
        self.assertEqual(frozenset({"e-1"}), client.requests[0].allowed_evidence_ids)
        self.assertEqual(frozenset({"s-1"}), client.requests[0].allowed_source_ids)
        self.assertEqual(5000, client.requests[0].input_token_limit)
        self.assertEqual("session-a", client.requests[0].session_id)
        self.assertEqual(
            (message_identity(messages[0]), message_identity(messages[1])),
            snapshot.covered_message_ids,
        )
        self.assertEqual(outcome.tokens_after, snapshot.tokens_after)
        self.assertLess(outcome.tokens_after, self._policy().context_limit * 0.15)

    def test_structured_prefix_fields_extend_evidence_and_source_allowlists(self):
        evidence_ids = {
            "e-additional",
            "e-content",
            "e-tool",
            "e-artifact",
            "e-response",
        }
        source_ids = {
            "s-additional",
            "s-content",
            "s-tool",
            "s-artifact",
            "s-response",
        }
        messages = (
            HumanMessage(
                content=[
                    {"type": "text", "text": "old question " + "x" * 2200},
                    {
                        "type": "context",
                        "evidence_id": "e-content",
                        "source_ids": ["s-content"],
                    },
                ],
                additional_kwargs={
                    "evidence_ids": ["e-additional"],
                    "source_id": "s-additional",
                },
                id="m1",
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "collect",
                        "args": {
                            "evidence_id": "e-tool",
                            "source_ids": ["s-tool"],
                        },
                        "id": "call-1",
                    }
                ],
                id="m2",
            ),
            ToolMessage(
                content="structured result",
                artifact={
                    "evidence_ids": ["e-artifact"],
                    "source_id": "s-artifact",
                },
                tool_call_id="call-1",
                id="m3",
            ),
            AIMessage(
                content="old answer " + "y" * 700,
                response_metadata={
                    "evidence_id": "e-response",
                    "source_ids": ["s-response"],
                },
                id="m4",
            ),
            HumanMessage(content="recent question", id="m5"),
            AIMessage(content="recent answer", id="m6"),
        )
        client = FakeSummaryClient(
            summary_payload(
                confirmed_findings=[
                    {
                        "claim": "All structured evidence is retained",
                        "evidence_ids": sorted(evidence_ids),
                    }
                ],
                referenced_source_ids=sorted(source_ids),
            )
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            outcome = self._compressor(
                ConversationContextStore(Path(temp_dir) / "memory.sqlite3"),
                client,
            ).prepare_model_view("session-a", messages)

        self.assertEqual("compressed", outcome.status)
        self.assertEqual(frozenset(evidence_ids), client.requests[0].allowed_evidence_ids)
        self.assertEqual(frozenset(source_ids), client.requests[0].allowed_source_ids)

    def test_free_text_id_spelling_does_not_extend_allowlists(self):
        messages = (
            HumanMessage(
                content="source_id=s-text evidence_id=e-text " + "x" * 2800,
                id="m1",
            ),
            AIMessage(content="old answer " + "y" * 500, id="m2"),
            HumanMessage(content="recent question", id="m3"),
            AIMessage(content="recent answer", id="m4"),
        )
        client = FakeSummaryClient(
            summary_payload(
                confirmed_findings=[
                    {"claim": "Guessed", "evidence_ids": ["e-text"]}
                ],
                referenced_source_ids=["s-text"],
            )
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            outcome = self._compressor(store, client).prepare_model_view(
                "session-a", messages
            )
            snapshot = store.get_summary("session-a")

        self.assertEqual("skipped_with_error", outcome.status)
        self.assertEqual(frozenset(), client.requests[0].allowed_evidence_ids)
        self.assertEqual(frozenset(), client.requests[0].allowed_source_ids)
        self.assertIsNone(snapshot)

    def test_successful_compression_keeps_tool_exchange_atomic_in_recent_tail(self):
        messages = (
            HumanMessage(content="old " + "x" * 2500, id="m1"),
            AIMessage(content="old result " + "y" * 1000, id="m2"),
            HumanMessage(content="use tool", id="m3"),
            AIMessage(
                content="",
                id="m4",
                tool_calls=[{"name": "search", "args": {"q": "x"}, "id": "call-1"}],
            ),
            ToolMessage(content="result", tool_call_id="call-1", id="m5"),
            AIMessage(content="tool answer", id="m6"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            outcome = self._compressor(
                store,
                FakeSummaryClient(summary_payload()),
            ).prepare_model_view("session-a", messages, tools=({"name": "search"},))

        self.assertEqual("compressed", outcome.status)
        self.assertEqual(("m3", "m4", "m5", "m6"), tuple(m.id for m in outcome.recent_messages))
        self.assertIsInstance(outcome.recent_messages[1], AIMessage)
        self.assertIsInstance(outcome.recent_messages[2], ToolMessage)

    def test_successful_fallback_persists_actual_model_and_reason(self):
        client = FallbackSummaryClient(
            FakeSummaryClient(error=TimeoutError("local unavailable")),
            FakeSummaryClient(summary_payload(), model_id="cloud-summary"),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            outcome = self._compressor(store, client).prepare_model_view(
                "session-a", self._messages()
            )
            snapshot = store.get_summary("session-a")

        self.assertEqual("compressed", outcome.status)
        self.assertEqual("cloud-summary", outcome.summary_model)
        self.assertTrue(outcome.fallback_reason)
        self.assertEqual(outcome.summary_model, snapshot.summary_model)
        self.assertEqual(outcome.fallback_reason, snapshot.fallback_reason)

    def test_target_still_exceeded_skips_without_commit(self):
        client = FakeSummaryClient(summary_payload(goal="z" * 4000))
        policy = self._policy(context_limit=5000, target_ratio=0.10)
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            outcome = self._compressor(store, client, policy=policy).prepare_model_view(
                "session-a", self._messages()
            )
            snapshot = store.get_summary("session-a")

        self.assertEqual("skipped_with_error", outcome.status)
        self.assertIsNone(snapshot)
        self.assertEqual(0, outcome.revision)
        self.assertEqual(self._messages(), outcome.recent_messages)
        self.assertEqual("conversation_compression_failed", outcome.error_code)

    def test_no_safe_compression_boundary_skips_without_calling_client(self):
        messages = (
            HumanMessage(content="question " + "x" * 1400, id="m1"),
            AIMessage(content="answer " + "y" * 1400, id="m2"),
        )
        client = FakeSummaryClient(summary_payload())
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            outcome = self._compressor(store, client).prepare_model_view(
                "session-a", messages
            )

        self.assertEqual("skipped_with_error", outcome.status)
        self.assertEqual(messages, outcome.recent_messages)
        self.assertEqual([], client.requests)

    def test_oversized_summary_request_is_not_sent_to_client(self):
        client = FakeSummaryClient(summary_payload())
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            with self.assertRaises(ConversationCompressionError):
                self._compressor(
                    store,
                    client,
                    target_limit=100,
                ).prepare_model_view("session-a", self._messages())

        self.assertEqual([], client.requests)

    def test_target_window_controls_trigger_target_and_hard_thresholds(self):
        policy = self._policy(context_limit=5000, target_ratio=0.15)
        messages = self._messages(long_size=400)
        with tempfile.TemporaryDirectory() as temp_dir:
            outcome = self._compressor(
                ConversationContextStore(Path(temp_dir) / "memory.sqlite3"),
                FakeSummaryClient(summary_payload()),
                policy=policy,
                target_limit=1200,
            ).prepare_model_view("session-a", messages)

        self.assertEqual("compressed", outcome.status)
        self.assertLess(outcome.tokens_after, int(1200 * policy.target_ratio))

    def test_client_receives_message_snapshot_and_cannot_change_covered_identity(self):
        messages = self._messages()
        messages[0].additional_kwargs["original"] = {"nested": ["value"]}
        original = copy.deepcopy(messages)
        original_prefix_ids = tuple(message_identity(message) for message in messages[:2])
        client = MutatingSummaryClient()
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            outcome = self._compressor(store, client).prepare_model_view(
                "session-a", messages
            )
            snapshot = store.get_summary("session-a")

        self.assertEqual("compressed", outcome.status)
        self.assertEqual(original, messages)
        self.assertEqual(("m3", "m4"), tuple(m.id for m in outcome.recent_messages))
        self.assertEqual(original_prefix_ids, snapshot.covered_message_ids)
        self.assertEqual("tampered-id", client.requests[0].messages[0].id)

    def test_client_failure_at_hard_limit_fails_closed_without_commit(self):
        policy = self._policy(context_limit=1000, target_ratio=0.10, hard_ratio=0.50)
        messages = self._messages(long_size=5000)
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            compressor = self._compressor(
                store,
                FakeSummaryClient(
                    error=ConversationCompressionError("internal detail")
                ),
                policy=policy,
            )
            with self.assertRaises(ConversationCompressionError) as raised:
                compressor.prepare_model_view("session-a", messages)

            snapshot = store.get_summary("session-a")

        self.assertEqual("conversation_compression_failed", raised.exception.error_code)
        self.assertNotIn("internal detail", str(raised.exception))
        self.assertIsNone(snapshot)

    def test_client_programming_error_is_not_disguised_as_compression_skip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            compressor = self._compressor(
                ConversationContextStore(Path(temp_dir) / "memory.sqlite3"),
                FakeSummaryClient(error=AttributeError("client bug")),
            )

            with self.assertRaisesRegex(AttributeError, "client bug"):
                compressor.prepare_model_view("session-a", self._messages())

    def test_client_runtime_error_is_not_disguised_as_compression_skip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            compressor = self._compressor(
                ConversationContextStore(Path(temp_dir) / "memory.sqlite3"),
                FakeSummaryClient(
                    error=RuntimeError("programming runtime sentinel")
                ),
            )

            with self.assertRaisesRegex(RuntimeError, "programming runtime sentinel"):
                compressor.prepare_model_view("session-a", self._messages())

    def test_store_error_is_not_disguised_as_compression_skip(self):
        with self.assertRaisesRegex(sqlite3.OperationalError, "database unavailable"):
            self._compressor(
                FailingCommitStore(),
                FakeSummaryClient(summary_payload()),
            ).prepare_model_view("session-a", self._messages())

    def test_first_revision_conflict_retries_full_attempt(self):
        store = ScriptedConflictStore(conflicts=1)
        client = FakeSummaryClient(callback=self._adaptive_payload)

        outcome = self._compressor(store, client).prepare_model_view(
            "session-a", self._messages()
        )

        self.assertEqual("compressed", outcome.status)
        self.assertEqual(2, outcome.revision)
        self.assertEqual(2, len(client.requests))
        self.assertIsNone(client.requests[0].previous_summary)
        self.assertEqual("persisted-1", client.requests[1].previous_summary.goal)
        self.assertEqual(2, store.commit_calls)

    def test_second_revision_conflict_returns_only_persisted_state(self):
        store = ScriptedConflictStore(conflicts=2)
        client = FakeSummaryClient(callback=self._adaptive_payload)
        messages = self._messages()

        outcome = self._compressor(store, client).prepare_model_view("session-a", messages)

        self.assertEqual("skipped_with_error", outcome.status)
        self.assertEqual(2, outcome.revision)
        self.assertEqual("persisted-2", outcome.summary.goal)
        self.assertNotEqual("Compressed goal", outcome.summary.goal)
        self.assertEqual(messages, outcome.recent_messages)
        self.assertEqual(2, len(client.requests))

    def test_resume_excludes_covered_messages_and_merges_previous_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            first_client = FakeSummaryClient(
                summary_payload(
                    confirmed_findings=[{"claim": "old finding", "evidence_ids": ["e-old"]}],
                    referenced_source_ids=["s-old"],
                )
            )
            messages = self._messages()
            first = self._compressor(store, first_client).prepare_model_view(
                "session-a",
                messages,
                protected_evidence_ids=("e-old",),
                protected_source_ids=("s-old",),
            )
            extended = (
                *messages,
                HumanMessage(content="new old question " + "x" * 1600, id="m5"),
                AIMessage(content="new old answer " + "y" * 1600, id="m6"),
                HumanMessage(content="new recent question", id="m7"),
                AIMessage(content="new recent answer", id="m8"),
            )
            second_client = FakeSummaryClient(callback=self._adaptive_payload)
            second = self._compressor(store, second_client).prepare_model_view(
                "session-a",
                extended,
                protected_evidence_ids=("e-new",),
                protected_source_ids=("s-new",),
            )

        self.assertEqual("compressed", first.status)
        self.assertEqual("compressed", second.status)
        self.assertNotIn("m1", tuple(message.id for message in second_client.requests[0].messages))
        self.assertNotIn("m2", tuple(message.id for message in second_client.requests[0].messages))
        self.assertEqual(frozenset({"e-old", "e-new"}), second_client.requests[0].allowed_evidence_ids)
        self.assertEqual(frozenset({"s-old", "s-new"}), second_client.requests[0].allowed_source_ids)

    def test_covered_hash_consumes_only_one_matching_no_id_message(self):
        first = HumanMessage(content="same")
        repeated = HumanMessage(content="same")
        covered_id = message_identity(first)
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(Path(temp_dir) / "memory.sqlite3")
            store.commit_summary(
                SummaryCommitCommand(
                    session_id="session-a",
                    summary=ConversationSummary(goal="Existing summary"),
                    covered_message_ids=(covered_id,),
                    tokens_before=20,
                    tokens_after=10,
                    messages_before=1,
                    messages_after=0,
                    summary_model="summary-model",
                    compression_reason="trigger_ratio",
                ),
                expected_revision=0,
            )
            client = FakeSummaryClient(error=AssertionError("must not run"))
            outcome = self._compressor(store, client).prepare_model_view(
                "session-a", (first, repeated)
            )

        self.assertEqual("not_needed", outcome.status)
        self.assertEqual((repeated,), outcome.recent_messages)
        self.assertEqual([], client.requests)

    def test_public_inputs_are_strict_and_dataclasses_are_frozen(self):
        client = FakeSummaryClient(summary_payload())
        with tempfile.TemporaryDirectory() as temp_dir:
            compressor = self._compressor(
                ConversationContextStore(Path(temp_dir) / "memory.sqlite3"),
                client,
            )
            invalid_calls = (
                ("../bad", (), (), (), ()),
                ("session-a", "messages", (), (), ()),
                ("session-a", (object(),), (), (), ()),
                ("session-a", (), "tools", (), ()),
                ("session-a", (), (object(),), (), ()),
                ("session-a", (), (), "e-1", ()),
                ("session-a", (), (), ("e-1", "e-1"), ()),
                ("session-a", (), (), (), (" ",)),
            )
            for session_id, messages, tools, evidence, sources in invalid_calls:
                with self.subTest(session_id=session_id), self.assertRaises((TypeError, ValueError)):
                    compressor.prepare_model_view(
                        session_id,
                        messages,
                        tools=tools,
                        protected_evidence_ids=evidence,
                        protected_source_ids=sources,
                    )

        request = summary_request()
        outcome = CompressionOutcome(
            "not_needed", None, (), 0, 0, 0, 0, 0, "", "", ""
        )
        with self.assertRaises(FrozenInstanceError):
            request.input_token_limit = 1
        with self.assertRaises(FrozenInstanceError):
            outcome.revision = 1


class ConversationContextPublicApiTests(unittest.TestCase):
    def test_star_import_exposes_task5_public_api(self):
        namespace = {}
        exec("from agent.context import *", namespace)

        expected = {
            "SummaryClient",
            "SummaryRequest",
            "SummaryClientResult",
            "CompressionOutcome",
            "FallbackSummaryClient",
            "ConversationCompressor",
            "parse_summary",
            "validate_summary",
            "parse_and_validate_summary",
        }
        self.assertTrue(expected.issubset(namespace))


if __name__ == "__main__":
    unittest.main()
