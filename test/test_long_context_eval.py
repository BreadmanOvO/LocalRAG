from __future__ import annotations

import copy
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
from typing import Any
import unittest
from unittest import mock

import eval.eval_long_context as long_context_eval
from eval.eval_long_context import (
    evaluate_case,
    main,
    run_long_context_eval,
    summarize_long_context,
    validate_dataset,
)


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "evaluation" / "agent" / "long_context_eval_set.json"
EXPECTED_CASE_IDS = (
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
)


def _load_payload() -> dict[str, Any]:
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def _message(
    message_id: str,
    role: str,
    content: str,
    *,
    evidence_ids: list[str] | None = None,
    source_ids: list[str] | None = None,
    tool_calls: list[dict] | None = None,
    tool_call_id: str = "",
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": message_id,
        "role": role,
        "content": content,
        "evidence_ids": list(evidence_ids or []),
        "source_ids": list(source_ids or []),
    }
    if tool_calls is not None:
        row["tool_calls"] = tool_calls
    if tool_call_id:
        row["tool_call_id"] = tool_call_id
    return row


def _passing_execution_trace(case: dict[str, Any]) -> list[dict[str, Any]]:
    observations = case["fixture"]["expected_observations"]
    trace: list[dict[str, Any]] = []
    resumed_revision = observations["resumed_revision"]
    if resumed_revision:
        trace.append({"type": "session_resumed", "revision": resumed_revision})
    failed_call_ids = set(observations["failed_tool_call_ids"])
    for call_id in observations["tool_pair_call_ids"]:
        trace.extend(
            [
                {"type": "tool_call", "call_id": call_id},
                {
                    "type": "tool_result",
                    "call_id": call_id,
                    "status": "failed" if call_id in failed_call_ids else "succeeded",
                },
            ]
        )
    attempt_count = max(1, observations["compression_round_count"])
    for round_number in range(1, attempt_count + 1):
        trace.append(
            {
                "type": "summary_attempt",
                "round": round_number,
                "provider": "local",
                "status": observations["local_summary_status"],
            }
        )
        fallback_status = observations["fallback_summary_status"]
        if fallback_status != "not_used":
            trace.append(
                {
                    "type": "summary_attempt",
                    "round": round_number,
                    "provider": "fallback",
                    "status": fallback_status,
                }
            )
        if round_number == 1:
            for index in range(observations["revision_conflict_count"]):
                trace.append(
                    {
                        "type": "revision_conflict",
                        "round": round_number,
                        "expected_revision": resumed_revision + index,
                        "actual_revision": resumed_revision + index + 1,
                    }
                )
        if round_number <= observations["compression_round_count"]:
            trace.append({"type": "compression_committed", "round": round_number})
    return trace


def _passing_outcome(case: dict[str, Any]) -> dict[str, Any]:
    original_messages = copy.deepcopy(case["fixture"]["messages"])
    original_by_id = {message["id"]: message for message in original_messages}
    dual_failure = case["id"] == "dual-summary-failure-001"
    model_messages = copy.deepcopy(original_messages) if dual_failure else [
        _message(
            f"summary-{case['id']}",
            "system",
            f"Compressed summary for {case['id']}.",
        ),
        *(
            copy.deepcopy(original_by_id[message_id])
            for message_id in case["required_recent_message_ids"]
        ),
    ]
    answer_contract = case["answer_contract"]
    answer_parts = [
        "The compressed conversation preserves",
        *answer_contract["required_terms"],
        *answer_contract["required_source_ids"],
        "with verified context and no unsupported claims.",
    ]
    answer = " ".join(answer_parts).replace("unsupported", "unverified")
    expected_summary = case["fixture"]["expected_summary"]
    return {
        "compression_triggered": True,
        "compression_count": case["expected_compression_count"],
        "summary": None
        if dual_failure
        else {
            "goal": case["description"],
            "user_constraints": list(case["required_constraints"]),
            "confirmed_findings": [
                {"claim": finding, "evidence_ids": case["required_evidence_ids"]}
                for finding in case["required_findings"]
            ],
            "decisions": [],
            "unresolved_questions": list(
                expected_summary["unresolved_questions"]
            ),
            "failed_attempts": list(expected_summary["failed_attempts"]),
            "referenced_source_ids": list(case["required_source_ids"]),
        },
        "original_messages": original_messages,
        "audit_messages": copy.deepcopy(original_messages),
        "model_messages": model_messages,
        "tokens_before": 1,
        "tokens_after": 1,
        "answer": answer,
        "observations": copy.deepcopy(case["fixture"]["expected_observations"]),
        "execution_trace": _passing_execution_trace(case),
        "error_code": case["expected_error_code"],
        "summary_model": "deterministic-summary-v1",
        "fallback_reason": (
            "primary_summary_failed"
            if case["id"] == "local-summary-fallback-001"
            else ""
        ),
    }


setattr(_passing_outcome, "evaluation_mode", "formal")
setattr(_passing_outcome, "counter_identity", "agent.context.budget.count_message_tokens")
setattr(_passing_outcome, "summary_client_identity", "test-formal-adapter-v1")


class LongContextDatasetTests(unittest.TestCase):
    def test_validate_dataset_accepts_exact_frozen_contract(self):
        dataset = validate_dataset(_load_payload())

        self.assertEqual("long-context-eval-v1", dataset["contract_version"])
        self.assertEqual(EXPECTED_CASE_IDS, tuple(case["id"] for case in dataset["cases"]))

    def test_dataset_freezes_messages_scenarios_and_answer_contracts(self):
        dataset = validate_dataset(_load_payload())
        cases = {case["id"]: case for case in dataset["cases"]}

        for case in dataset["cases"]:
            with self.subTest(case_id=case["id"]):
                self.assertGreaterEqual(len(case["fixture"]["messages"]), 5)
                self.assertEqual(
                    {
                        "messages",
                        "previous_summary",
                        "expected_observations",
                        "expected_summary",
                    },
                    set(case["fixture"]),
                )
                self.assertEqual(
                    {
                        "failed_tool_call_ids",
                        "tool_pair_call_ids",
                        "compression_round_count",
                        "resumed_revision",
                        "revision_conflict_count",
                        "local_summary_status",
                        "fallback_summary_status",
                    },
                    set(case["fixture"]["expected_observations"]),
                )
                self.assertEqual(
                    {
                        "required_terms",
                        "forbidden_terms",
                        "min_chars",
                        "required_source_ids",
                    },
                    set(case["answer_contract"]),
                )

        failed = cases["failed-tool-001"]
        self.assertEqual(
            ["call-failed-tool-001"],
            failed["fixture"]["expected_observations"]["failed_tool_call_ids"],
        )
        failed_results = [
            message
            for message in failed["fixture"]["messages"]
            if message["role"] == "tool"
        ]
        self.assertEqual("failed", failed_results[0]["tool_status"])
        self.assertEqual(
            2,
            cases["rolling-summary-001"]["fixture"]["expected_observations"][
                "compression_round_count"
            ],
        )
        self.assertGreater(
            cases["session-resume-001"]["fixture"]["expected_observations"][
                "resumed_revision"
            ],
            0,
        )
        self.assertEqual(
            1,
            cases["revision-conflict-001"]["fixture"]["expected_observations"][
                "revision_conflict_count"
            ],
        )
        self.assertEqual(
            ("failed", "success"),
            (
                cases["local-summary-fallback-001"]["fixture"]
                ["expected_observations"]["local_summary_status"],
                cases["local-summary-fallback-001"]["fixture"]
                ["expected_observations"]["fallback_summary_status"],
            ),
        )
        self.assertEqual(
            ("failed", "failed"),
            (
                cases["dual-summary-failure-001"]["fixture"]
                ["expected_observations"]["local_summary_status"],
                cases["dual-summary-failure-001"]["fixture"]
                ["expected_observations"]["fallback_summary_status"],
            ),
        )

    def test_nested_fixture_contract_rejects_unknown_fields(self):
        payload = _load_payload()
        payload["cases"][0]["fixture"]["unexpected"] = True

        with self.assertRaisesRegex(ValueError, "exact fixture contract"):
            validate_dataset(payload)

    def test_missing_case_fails_closed(self):
        payload = _load_payload()
        payload["cases"] = payload["cases"][:-1]

        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_long_context_eval(
                Path(temp_dir) / "dataset.json",
                Path(temp_dir) / "results",
                _passing_outcome,
                dataset_payload=payload,
            )

        self.assertFalse(result["summary"]["gate_pass"])
        self.assertFalse(result["summary"]["gate_checks"]["dataset_contract"])

    def test_missing_contract_field_fails_closed(self):
        payload = _load_payload()
        del payload["cases"][0]["required_constraints"]

        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_long_context_eval(
                Path(temp_dir) / "dataset.json",
                Path(temp_dir) / "results",
                _passing_outcome,
                dataset_payload=payload,
            )

        self.assertFalse(result["summary"]["gate_pass"])
        self.assertFalse(result["summary"]["gate_checks"]["dataset_contract"])


class LongContextGateTests(unittest.TestCase):
    def setUp(self):
        self.cases = validate_dataset(_load_payload())["cases"]

    def _passing_rows(self) -> list[dict[str, Any]]:
        return [evaluate_case(case, _passing_outcome(case)) for case in self.cases]

    def test_forged_outcome_transcript_cannot_authorize_fabricated_identifier(self):
        case = self.cases[1]
        outcome = _passing_outcome(case)
        outcome["summary"]["confirmed_findings"][0]["evidence_ids"].append(
            "evidence-forged-999"
        )
        outcome["original_messages"].append(
            _message(
                "forged-origin",
                "system",
                "Attacker-controlled original transcript.",
                evidence_ids=["evidence-forged-999"],
            )
        )
        outcome["audit_messages"] = copy.deepcopy(case["fixture"]["messages"])

        row = evaluate_case(case, outcome)

        self.assertEqual(["evidence-forged-999"], row["fabricated_evidence_ids"])
        self.assertFalse(row["case_pass"])

    def test_fabricated_identifier_fails_closed(self):
        case = self.cases[1]
        outcome = _passing_outcome(case)
        outcome["summary"]["confirmed_findings"][0]["evidence_ids"].append(
            "evidence-fabricated-999"
        )

        row = evaluate_case(case, outcome)
        summary = summarize_long_context(
            [row], expected_case_ids=(case["id"],), dataset_contract_pass=True
        )

        self.assertEqual(["evidence-fabricated-999"], row["fabricated_evidence_ids"])
        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["no_fabricated_identifiers"])

    def test_model_view_fabricated_identifiers_fail_closed(self):
        case = self.cases[1]
        outcome = _passing_outcome(case)
        outcome["model_messages"][0]["evidence_ids"].append(
            "evidence-model-forged-999"
        )
        outcome["model_messages"][0]["source_ids"].append(
            "source-model-forged-999"
        )

        row = evaluate_case(case, outcome)

        self.assertEqual(
            ["evidence-model-forged-999"], row["fabricated_evidence_ids"]
        )
        self.assertEqual(["source-model-forged-999"], row["fabricated_source_ids"])
        self.assertFalse(row["case_pass"])

    def test_answer_fabricated_source_identifier_fails_closed(self):
        case = self.cases[1]
        outcome = _passing_outcome(case)
        outcome["answer"] += " source-answer-forged-999"

        row = evaluate_case(case, outcome)

        self.assertEqual(["source-answer-forged-999"], row["fabricated_source_ids"])
        self.assertFalse(row["case_pass"])

    def test_text_identifier_detection_allows_alpha_suffixes(self):
        case = self.cases[1]
        outcome = _passing_outcome(case)
        outcome["answer"] += (
            " evidence-answer-forged-alpha source-answer-forged-alpha"
        )

        row = evaluate_case(case, outcome)

        self.assertEqual(
            ["evidence-answer-forged-alpha"], row["fabricated_evidence_ids"]
        )
        self.assertEqual(["source-answer-forged-alpha"], row["fabricated_source_ids"])
        self.assertFalse(row["case_pass"])

    def test_text_fields_cannot_hide_fabricated_identifiers(self):
        case = self.cases[1]
        outcome = _passing_outcome(case)
        outcome["model_messages"][0]["content"] += (
            " evidence-model-text-forged-999 source-model-text-forged-999"
        )
        outcome["summary"]["decisions"].append(
            "Use evidence-summary-text-forged-999 from "
            "source-summary-text-forged-999."
        )

        row = evaluate_case(case, outcome)

        self.assertEqual(
            [
                "evidence-model-text-forged-999",
                "evidence-summary-text-forged-999",
            ],
            row["fabricated_evidence_ids"],
        )
        self.assertEqual(
            ["source-model-text-forged-999", "source-summary-text-forged-999"],
            row["fabricated_source_ids"],
        )
        self.assertFalse(row["case_pass"])

    def test_token_reduction_of_39_9_percent_fails_closed(self):
        case = self.cases[0]
        outcome = _passing_outcome(case)
        with mock.patch(
            "eval.eval_long_context.count_message_tokens",
            side_effect=(1000, 601),
        ):
            row = evaluate_case(case, outcome)

        self.assertEqual(0.399, row["token_reduction_ratio"])
        self.assertFalse(row["token_reduction_pass"])
        self.assertFalse(row["case_pass"])

    def test_forged_low_tokens_and_full_transcript_fail_closed(self):
        case = self.cases[0]
        outcome = _passing_outcome(case)
        outcome["model_messages"] = copy.deepcopy(case["fixture"]["messages"])
        outcome["tokens_before"] = 1000
        outcome["tokens_after"] = 1

        row = evaluate_case(case, outcome)

        self.assertEqual(row["tokens_before"], row["tokens_after"])
        self.assertFalse(row["compressed_view_pass"])
        self.assertFalse(row["token_reduction_pass"])
        self.assertFalse(row["case_pass"])

    def test_orphan_tool_message_fails_closed(self):
        case = self.cases[4]
        outcome = _passing_outcome(case)
        outcome["model_messages"] = [
            message
            for message in outcome["model_messages"]
            if message["id"] != "msg-tool-call-001"
        ]

        row = evaluate_case(case, outcome)
        summary = summarize_long_context(
            [row], expected_case_ids=(case["id"],), dataset_contract_pass=True
        )

        self.assertEqual(["msg-tool-result-001"], row["orphan_tool_message_ids"])
        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["no_orphan_tool_messages"])

    def test_recent_messages_must_keep_exact_order(self):
        case = self.cases[0]
        outcome = _passing_outcome(case)
        outcome["model_messages"][-2:] = reversed(outcome["model_messages"][-2:])

        row = evaluate_case(case, outcome)

        self.assertFalse(row["recent_message_retention_pass"])
        self.assertFalse(row["case_pass"])

    def test_tool_result_cannot_precede_its_call(self):
        case = self.cases[4]
        outcome = _passing_outcome(case)
        model_messages = outcome["model_messages"]
        call_index = next(
            index
            for index, message in enumerate(model_messages)
            if message["id"] == "msg-tool-call-001"
        )
        result_index = next(
            index
            for index, message in enumerate(model_messages)
            if message["id"] == "msg-tool-result-001"
        )
        model_messages[call_index], model_messages[result_index] = (
            model_messages[result_index],
            model_messages[call_index],
        )

        row = evaluate_case(case, outcome)

        self.assertEqual(
            {"msg-tool-call-001", "msg-tool-result-001"},
            set(row["orphan_tool_message_ids"]),
        )
        self.assertFalse(row["case_pass"])

    def test_answer_contract_failure_fails_closed(self):
        case = self.cases[0]
        outcome = _passing_outcome(case)
        outcome["answer"] = "unsupported"

        row = evaluate_case(case, outcome)
        summary = summarize_long_context(
            [row], expected_case_ids=(case["id"],), dataset_contract_pass=True
        )

        self.assertFalse(row["answer_contract_pass"])
        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["answer_contract"])

    def test_answer_contract_is_case_specific_and_requires_sources(self):
        case = self.cases[1]
        outcome = _passing_outcome(case)
        outcome["answer"] = "Compression retained the required conversation contract."

        row = evaluate_case(case, outcome)

        self.assertFalse(row["answer_contract_pass"])

    def test_runtime_observations_must_match_executable_scenario(self):
        case = self.cases[7]
        outcome = _passing_outcome(case)
        outcome["execution_trace"] = [
            event
            for event in outcome["execution_trace"]
            if event["type"] != "revision_conflict"
        ]

        row = evaluate_case(case, outcome)

        self.assertFalse(row["scenario_contract_pass"])
        self.assertFalse(row["case_pass"])

    def test_self_reported_observations_without_execution_trace_fail_closed(self):
        case = self.cases[7]
        outcome = _passing_outcome(case)
        del outcome["execution_trace"]
        outcome["observations"] = copy.deepcopy(
            case["fixture"]["expected_observations"]
        )

        row = evaluate_case(case, outcome)

        self.assertFalse(row["scenario_contract_pass"])
        self.assertFalse(row["case_pass"])

    def test_execution_trace_requires_causal_event_order(self):
        case = self.cases[7]
        outcome = _passing_outcome(case)
        conflict_index = next(
            index
            for index, event in enumerate(outcome["execution_trace"])
            if event["type"] == "revision_conflict"
        )
        summary_index = next(
            index
            for index, event in enumerate(outcome["execution_trace"])
            if event["type"] == "summary_attempt"
        )
        outcome["execution_trace"][conflict_index], outcome["execution_trace"][
            summary_index
        ] = (
            outcome["execution_trace"][summary_index],
            outcome["execution_trace"][conflict_index],
        )

        row = evaluate_case(case, outcome)

        self.assertFalse(row["scenario_contract_pass"])
        self.assertFalse(row["case_pass"])

    def test_structured_summary_must_preserve_unresolved_and_failed_state(self):
        for case_index in (2, 3, 8):
            case = self.cases[case_index]
            outcome = _passing_outcome(case)
            outcome["summary"]["unresolved_questions"] = []
            outcome["summary"]["failed_attempts"] = []

            row = evaluate_case(case, outcome)

            self.assertFalse(row["summary_state_pass"], case["id"])
            self.assertFalse(row["case_pass"], case["id"])

    def test_summary_recomputes_all_metrics_instead_of_trusting_case_pass(self):
        rows = self._passing_rows()
        rows[0]["constraint_retention_pass"] = False
        rows[0]["case_pass"] = True

        summary = summarize_long_context(rows)

        self.assertFalse(summary["gate_pass"])
        self.assertLess(summary["metrics"]["constraint_retention_ratio"], 1.0)

    def test_summary_rejects_runtime_error_even_when_ratio_metrics_pass(self):
        rows = self._passing_rows()
        rows[0]["runtime_error"] = "RuntimeError: injected failure"
        rows[0]["case_pass"] = True

        summary = summarize_long_context(rows)

        self.assertEqual(9, summary["passed_case_count"])
        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["all_case_contracts"])

    def test_complete_rows_pass_all_gates(self):
        summary = summarize_long_context(self._passing_rows())

        self.assertTrue(summary["gate_pass"])
        self.assertEqual(10, summary["passed_case_count"])
        self.assertTrue(all(summary["gate_checks"].values()))


class LongContextRunnerTests(unittest.TestCase):
    def test_runner_writes_manifest_predictions_and_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_long_context_eval(
                DATASET_PATH,
                Path(temp_dir),
                long_context_eval.deterministic_compressor_factory,
                mode="deterministic",
            )
            run_dir = result["run_dir"]

            self.assertTrue((run_dir / "manifest.json").is_file())
            self.assertTrue((run_dir / "predictions.json").is_file())
            self.assertTrue((run_dir / "summary.json").is_file())
            self.assertTrue(result["summary"]["gate_pass"])
            self.assertEqual(10, result["manifest"]["evaluation_scope"]["executed_case_count"])
            self.assertEqual(64, len(result["manifest"]["dataset_fingerprint"]))

    def test_formal_subset_is_never_allowed_to_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_long_context_eval(
                DATASET_PATH,
                Path(temp_dir),
                _passing_outcome,
                mode="formal",
                case_ids=[EXPECTED_CASE_IDS[0]],
            )

        self.assertFalse(result["summary"]["gate_pass"])
        self.assertFalse(result["summary"]["gate_checks"]["evaluation_complete"])

    def test_git_identity_uses_repo_root_for_every_command(self):
        completed = mock.Mock(stdout="revision\n")
        with mock.patch(
            "eval.eval_long_context.subprocess.run",
            side_effect=(completed, mock.Mock(stdout="")),
        ) as run:
            long_context_eval._git_identity()

        self.assertEqual(2, run.call_count)
        for call in run.call_args_list:
            self.assertEqual(ROOT, call.kwargs["cwd"])
        self.assertIn(
            ":(exclude)results/**",
            run.call_args_list[1].args[0],
        )

    def test_git_identity_is_sampled_before_run_directory_and_factory(self):
        events: list[str] = []

        def factory(case: dict[str, Any]) -> dict[str, Any]:
            events.append("factory")
            return _passing_outcome(case)

        def git_identity() -> tuple[str, bool]:
            events.append("git")
            return "revision", False

        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch(
                "eval.eval_long_context._git_identity", side_effect=git_identity
            ):
                run_long_context_eval(DATASET_PATH, Path(temp_dir), factory)

        self.assertEqual("git", events[0])

    def test_formal_cli_accepts_importable_full_set_factory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            argv = [
                "eval_long_context.py",
                "--mode",
                "formal",
                "--factory",
                "test.test_long_context_eval:_passing_outcome",
                "--dataset",
                str(DATASET_PATH),
                "--out-dir",
                temp_dir,
            ]
            with mock.patch("sys.argv", argv), redirect_stdout(io.StringIO()):
                result = main()

        self.assertTrue(result["summary"]["gate_pass"])
        self.assertEqual(10, result["summary"]["passed_case_count"])

    def test_formal_mode_rejects_deterministic_factory_identity(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_long_context_eval(
                DATASET_PATH,
                Path(temp_dir),
                long_context_eval.deterministic_compressor_factory,
                mode="formal",
            )

        self.assertFalse(result["summary"]["gate_pass"])
        self.assertFalse(result["summary"]["gate_checks"]["dataset_contract"])


if __name__ == "__main__":
    unittest.main()
