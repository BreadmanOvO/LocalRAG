import json
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest import mock

from langchain_core.messages import AIMessage, HumanMessage

from agent.context import (
    CompressionDecision,
    CompressionPolicy,
    ConversationCompressionError,
    ConversationSummary,
    SummaryFinding,
    count_message_tokens,
    decide_compression,
)
from agent.context import __all__ as context_exports


class ConversationBudgetTests(unittest.TestCase):
    def test_policy_rejects_invalid_ratio_order(self):
        invalid_ratios = (
            {"target_ratio": 0},
            {"target_ratio": 0.70, "trigger_ratio": 0.70},
            {"trigger_ratio": 0.90, "hard_limit_ratio": 0.90},
            {"hard_limit_ratio": 1},
        )

        for overrides in invalid_ratios:
            with self.subTest(overrides=overrides):
                with self.assertRaisesRegex(
                    ValueError,
                    "target_ratio < trigger_ratio < hard_limit_ratio",
                ):
                    CompressionPolicy(**overrides)

    def test_policy_rejects_invalid_integer_limits(self):
        invalid_values = (
            ("context_limit", 0, "context_limit must be greater than 0"),
            ("context_limit", -1, "context_limit must be greater than 0"),
            ("fixed_overhead_tokens", -1, "fixed_overhead_tokens must be at least 0"),
            ("output_reserve_tokens", -1, "output_reserve_tokens must be at least 0"),
            ("recent_turns", 0, "recent_turns must be greater than 0"),
            ("recent_turns", -1, "recent_turns must be greater than 0"),
        )

        for field_name, value, message in invalid_values:
            with self.subTest(field_name=field_name, value=value):
                with self.assertRaisesRegex(ValueError, message):
                    CompressionPolicy(**{field_name: value})

    def test_policy_rejects_non_integer_limit_types(self):
        for field_name in (
            "context_limit",
            "fixed_overhead_tokens",
            "output_reserve_tokens",
            "recent_turns",
        ):
            for value in (True, 1.5):
                with self.subTest(field_name=field_name, value=value):
                    with self.assertRaisesRegex(TypeError, f"{field_name} must be an int"):
                        CompressionPolicy(**{field_name: value})

    def test_decision_triggers_at_configured_message_threshold(self):
        policy = CompressionPolicy(
            context_limit=1000,
            fixed_overhead_tokens=100,
            output_reserve_tokens=100,
            trigger_ratio=0.70,
            target_ratio=0.45,
            hard_limit_ratio=0.90,
        )

        decision = decide_compression(560, policy)

        self.assertEqual(
            CompressionDecision(
                should_compress=True,
                available_message_tokens=800,
                trigger_message_tokens=560,
                target_message_tokens=360,
                hard_message_tokens=720,
            ),
            decision,
        )

    def test_decision_does_not_trigger_below_threshold(self):
        policy = CompressionPolicy(
            context_limit=1000,
            fixed_overhead_tokens=100,
            output_reserve_tokens=100,
            trigger_ratio=0.70,
            target_ratio=0.45,
            hard_limit_ratio=0.90,
        )

        self.assertFalse(decide_compression(559, policy).should_compress)

    def test_decision_rejects_policy_without_message_budget(self):
        policy = CompressionPolicy(
            context_limit=1000,
            fixed_overhead_tokens=900,
            output_reserve_tokens=100,
        )

        with self.assertRaisesRegex(ValueError, "available message budget must be greater than 0"):
            decide_compression(0, policy)

    def test_decision_rejects_negative_message_tokens(self):
        with self.assertRaisesRegex(ValueError, "message_tokens must be at least 0"):
            decide_compression(-1, CompressionPolicy())

    def test_decision_rejects_non_integer_message_tokens(self):
        for value in (True, 1.5):
            with self.subTest(value=value):
                with self.assertRaisesRegex(TypeError, "message_tokens must be an int"):
                    decide_compression(value, CompressionPolicy())

    def test_count_message_tokens_returns_positive_integer_and_accepts_tools(self):
        messages = [
            HumanMessage(content="Compare the latency evidence for both retrieval methods."),
            AIMessage(content="Method A is faster in the reported benchmark."),
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "inspect_source",
                    "description": "Inspect one source by identifier.",
                    "parameters": {
                        "type": "object",
                        "properties": {"source_id": {"type": "string"}},
                        "required": ["source_id"],
                    },
                },
            }
        ]

        without_tools = count_message_tokens(messages)
        with_tools = count_message_tokens(messages, tools=tools)

        self.assertIs(type(without_tools), int)
        self.assertGreater(without_tools, 0)
        self.assertIs(type(with_tools), int)
        self.assertGreater(with_tools, without_tools)

    def test_count_message_tokens_rejects_impossible_negative_result(self):
        with mock.patch(
            "agent.context.budget.count_tokens_approximately",
            return_value=-1,
        ):
            with self.assertRaisesRegex(ValueError, "token count must be at least 0"):
                count_message_tokens([HumanMessage(content="hello")])

    def test_summary_models_and_decisions_are_immutable(self):
        finding = SummaryFinding("Latency improved.", ("evidence-001",))
        summary = ConversationSummary(
            goal="Compare retrieval latency.",
            confirmed_findings=(finding,),
        )
        decision = CompressionDecision(False, 100, 70, 45, 90)

        with self.assertRaises(FrozenInstanceError):
            finding.claim = "Changed."
        with self.assertRaises(FrozenInstanceError):
            summary.goal = "Changed."
        with self.assertRaises(FrozenInstanceError):
            decision.should_compress = True

    def test_summary_models_normalize_mutable_sequences_to_tuples(self):
        evidence_ids = ["evidence-001"]
        finding = SummaryFinding("Latency improved.", evidence_ids)
        user_constraints = ["Use the selected corpus."]
        confirmed_findings = [finding]
        decisions = ["Compare median latency."]
        unresolved_questions = ["Which GPU was used?"]
        failed_attempts = ["Source inspection timed out."]
        referenced_source_ids = ["source-001"]

        summary = ConversationSummary(
            goal="Compare retrieval latency.",
            user_constraints=user_constraints,
            confirmed_findings=confirmed_findings,
            decisions=decisions,
            unresolved_questions=unresolved_questions,
            failed_attempts=failed_attempts,
            referenced_source_ids=referenced_source_ids,
        )
        evidence_ids.append("evidence-002")
        user_constraints.append("This must not leak into the summary.")
        confirmed_findings.clear()
        decisions.clear()
        unresolved_questions.clear()
        failed_attempts.clear()
        referenced_source_ids.clear()

        self.assertEqual(("evidence-001",), finding.evidence_ids)
        self.assertEqual(("Use the selected corpus.",), summary.user_constraints)
        self.assertEqual((finding,), summary.confirmed_findings)
        self.assertEqual(("Compare median latency.",), summary.decisions)
        self.assertEqual(("Which GPU was used?",), summary.unresolved_questions)
        self.assertEqual(("Source inspection timed out.",), summary.failed_attempts)
        self.assertEqual(("source-001",), summary.referenced_source_ids)

    def test_summary_models_keep_valid_tuples_unchanged(self):
        evidence_ids = ("evidence-001",)
        finding = SummaryFinding("Latency improved.", evidence_ids)
        user_constraints = ("Use the selected corpus.",)
        confirmed_findings = (finding,)
        decisions = ("Compare median latency.",)
        unresolved_questions = ("Which GPU was used?",)
        failed_attempts = ("Source inspection timed out.",)
        referenced_source_ids = ("source-001",)

        summary = ConversationSummary(
            goal="Compare retrieval latency.",
            user_constraints=user_constraints,
            confirmed_findings=confirmed_findings,
            decisions=decisions,
            unresolved_questions=unresolved_questions,
            failed_attempts=failed_attempts,
            referenced_source_ids=referenced_source_ids,
        )

        self.assertIs(evidence_ids, finding.evidence_ids)
        self.assertIs(user_constraints, summary.user_constraints)
        self.assertIs(confirmed_findings, summary.confirmed_findings)
        self.assertIs(decisions, summary.decisions)
        self.assertIs(unresolved_questions, summary.unresolved_questions)
        self.assertIs(failed_attempts, summary.failed_attempts)
        self.assertIs(referenced_source_ids, summary.referenced_source_ids)

    def test_summary_models_reject_non_string_claim_and_goal(self):
        with self.assertRaisesRegex(TypeError, "claim must be a str"):
            SummaryFinding(123)
        with self.assertRaisesRegex(TypeError, "goal must be a str"):
            ConversationSummary(goal=123)

    def test_summary_models_reject_invalid_collection_items(self):
        invalid_values = (
            (
                "evidence_ids",
                lambda: SummaryFinding("claim", [123]),
                "evidence_ids must contain only str values",
            ),
            (
                "user_constraints",
                lambda: ConversationSummary("goal", user_constraints=[123]),
                "user_constraints must contain only str values",
            ),
            (
                "confirmed_findings",
                lambda: ConversationSummary("goal", confirmed_findings=["finding"]),
                "confirmed_findings must contain only SummaryFinding values",
            ),
            (
                "decisions",
                lambda: ConversationSummary("goal", decisions=[123]),
                "decisions must contain only str values",
            ),
            (
                "unresolved_questions",
                lambda: ConversationSummary("goal", unresolved_questions=[123]),
                "unresolved_questions must contain only str values",
            ),
            (
                "failed_attempts",
                lambda: ConversationSummary("goal", failed_attempts=[123]),
                "failed_attempts must contain only str values",
            ),
            (
                "referenced_source_ids",
                lambda: ConversationSummary("goal", referenced_source_ids=[123]),
                "referenced_source_ids must contain only str values",
            ),
        )

        for field_name, constructor, message in invalid_values:
            with self.subTest(field_name=field_name):
                with self.assertRaisesRegex(TypeError, message):
                    constructor()

    def test_public_defaults_and_error_code_are_stable(self):
        self.assertEqual(
            CompressionPolicy(
                context_limit=40960,
                fixed_overhead_tokens=4096,
                output_reserve_tokens=1024,
                trigger_ratio=0.70,
                target_ratio=0.45,
                hard_limit_ratio=0.90,
                recent_turns=4,
            ),
            CompressionPolicy(),
        )
        self.assertEqual(ConversationSummary(goal="goal"), ConversationSummary(goal="goal"))
        self.assertEqual(
            "conversation_compression_failed",
            ConversationCompressionError.error_code,
        )
        self.assertEqual(
            [
                "SummaryFinding",
                "ConversationSummary",
                "CompressionPolicy",
                "CompressionDecision",
                "ConversationCompressionError",
                "count_message_tokens",
                "decide_compression",
            ],
            context_exports,
        )


class LongContextDatasetContractTests(unittest.TestCase):
    DATASET_PATH = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "evaluation"
        / "agent"
        / "long_context_eval_set.json"
    )
    EXPECTED_IDS = [
        "constraint-retention-001",
        "evidence-retention-001",
        "unresolved-question-001",
        "failed-tool-001",
        "tool-pair-boundary-001",
        "rolling-summary-001",
        "session-resume-001",
        "revision-conflict-001",
        "local-summary-fallback-001",
        "dual-summary-failure-001",
    ]
    EXPECTED_FIELDS = {
        "id",
        "description",
        "required_constraints",
        "required_findings",
        "required_evidence_ids",
        "required_source_ids",
        "required_recent_message_ids",
        "expected_compression_count",
        "expected_error_code",
    }
    LIST_FIELDS = (
        "required_constraints",
        "required_findings",
        "required_evidence_ids",
        "required_source_ids",
        "required_recent_message_ids",
    )

    def test_long_context_dataset_has_exact_contract(self):
        payload = json.loads(self.DATASET_PATH.read_text(encoding="utf-8"))

        self.assertEqual({"contract_version", "cases"}, set(payload))
        self.assertEqual("long-context-eval-v1", payload["contract_version"])
        self.assertIs(type(payload["cases"]), list)
        self.assertEqual(self.EXPECTED_IDS, [case["id"] for case in payload["cases"]])

        for case in payload["cases"]:
            with self.subTest(case_id=case["id"]):
                self.assertIs(type(case), dict)
                self.assertEqual(self.EXPECTED_FIELDS, set(case))
                self.assertIs(type(case["id"]), str)
                self.assertIs(type(case["description"]), str)
                for field_name in self.LIST_FIELDS:
                    self.assertIs(type(case[field_name]), list)
                    self.assertTrue(all(type(item) is str for item in case[field_name]))
                self.assertIs(type(case["expected_compression_count"]), int)
                self.assertGreaterEqual(case["expected_compression_count"], 0)
                self.assertIs(type(case["expected_error_code"]), str)

        cases_by_id = {case["id"]: case for case in payload["cases"]}
        self.assertEqual(2, cases_by_id["rolling-summary-001"]["expected_compression_count"])
        self.assertEqual(1, cases_by_id["revision-conflict-001"]["expected_compression_count"])
        self.assertEqual(
            1,
            cases_by_id["local-summary-fallback-001"]["expected_compression_count"],
        )
        self.assertEqual(
            "conversation_compression_failed",
            cases_by_id["dual-summary-failure-001"]["expected_error_code"],
        )
        self.assertTrue(
            all(
                case["expected_error_code"] == ""
                for case in payload["cases"]
                if case["id"] != "dual-summary-failure-001"
            )
        )


if __name__ == "__main__":
    unittest.main()
