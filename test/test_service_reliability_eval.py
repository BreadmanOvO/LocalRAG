from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from eval.eval_service_reliability import (
    CONTRACT_VERSION,
    RELIABILITY_CASES,
    REQUIRED_CASE_IDS,
    _deterministic_gateway_factory,
    run_reliability_case,
    run_reliability_eval,
    summarize_reliability,
)


def _rows() -> list[dict[str, object]]:
    return [
        run_reliability_case(case, _deterministic_gateway_factory)
        for case in RELIABILITY_CASES
    ]


def _case(rows: list[dict[str, object]], case_id: str) -> dict[str, object]:
    return next(row for row in rows if row["case_id"] == case_id)


def _event(row: dict[str, object], event_name: str, index: int = -1) -> dict[str, object]:
    events = row["events"]
    assert isinstance(events, list)
    matching = [event for event in events if event.get("event") == event_name]
    return matching[index]


class ServiceReliabilityEvalTests(unittest.TestCase):
    def test_script_supports_direct_python_execution(self):
        script = Path(__file__).resolve().parents[1] / "eval" / "eval_service_reliability.py"

        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("--mode", result.stdout)

    def test_fixed_case_ids_are_complete_and_ordered(self):
        self.assertEqual(12, len(REQUIRED_CASE_IDS))
        self.assertEqual(
            REQUIRED_CASE_IDS,
            tuple(case["id"] for case in RELIABILITY_CASES),
        )

    def test_deterministic_rows_pass_all_recomputed_contracts(self):
        rows = _rows()

        summary = summarize_reliability(rows)

        self.assertTrue(summary["gate_pass"])
        self.assertEqual(CONTRACT_VERSION, summary["contract_version"])
        self.assertEqual(12, summary["case_count"])
        self.assertEqual(12, summary["passed_case_count"])
        self.assertTrue(all(summary["gate_checks"].values()))
        serialized = json.dumps(rows, ensure_ascii=False).lower()
        self.assertNotIn("private prompt", serialized)
        self.assertNotIn("private answer", serialized)
        self.assertNotIn("api_token", serialized)
        self.assertNotIn("authorization", serialized)

    def test_missing_or_subset_cases_fail_coverage(self):
        rows = _rows()

        missing = summarize_reliability(rows[:-1])
        subset = summarize_reliability(rows[2:5])

        self.assertFalse(missing["gate_pass"])
        self.assertFalse(missing["gate_checks"]["case_coverage"])
        self.assertFalse(subset["gate_pass"])
        self.assertFalse(subset["gate_checks"]["case_coverage"])

    def test_wrong_retry_count_fails(self):
        rows = copy.deepcopy(_rows())
        result = _event(_case(rows, "connection-retry-fallback"), "result")
        result["attempt_count"] = 2

        summary = summarize_reliability(rows)

        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["retry_contract"])

    def test_wrong_actual_model_fails(self):
        rows = copy.deepcopy(_rows())
        result = _event(_case(rows, "queue-full-fallback"), "result")
        result["actual_model"] = "unexpected-model"

        summary = summarize_reliability(rows)

        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["case_outcomes"])

    def test_wrong_route_metadata_fails_even_when_result_is_unchanged(self):
        rows = copy.deepcopy(_rows())
        route = _event(_case(rows, "queue-full-fallback"), "route")
        route["actual_model"] = "unexpected-model"

        summary = summarize_reliability(rows)

        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["case_outcomes"])

    def test_fallback_after_first_token_fails(self):
        rows = copy.deepcopy(_rows())
        row = _case(rows, "stream-error-after-token-no-fallback")
        events = row["events"]
        assert isinstance(events, list)
        events.append({"event": "fallback_call", "operation": "stream"})

        summary = summarize_reliability(rows)

        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["fallback_contract"])

    def test_timeout_before_first_token_streams_only_cloud_chunks(self):
        rows = _rows()
        row = _case(rows, "timeout-before-token-fallback")
        result = _event(row, "result")
        events = row["events"]
        assert isinstance(events, list)
        chunks = [event for event in events if event.get("event") == "stream_chunk"]

        self.assertEqual("stream", result["operation"])
        self.assertTrue(result["fallback_used"])
        self.assertEqual("timeout", result["fallback_reason"])
        self.assertEqual({"cloud-model"}, {chunk["model"] for chunk in chunks})

    def test_oom_still_ready_fails(self):
        rows = copy.deepcopy(_rows())
        readiness = _event(_case(rows, "oom-fallback-not-ready"), "readiness")
        readiness["ready"] = True

        summary = summarize_reliability(rows)

        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["readiness_contract"])

    def test_wrong_breaker_state_fails(self):
        rows = copy.deepcopy(_rows())
        row = _case(rows, "circuit-open-half-open-recovery")
        snapshots = [
            event
            for event in row["events"]
            if event.get("event") == "circuit_snapshot"
        ]
        snapshots[1]["state"] = "closed"

        summary = summarize_reliability(rows)

        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["circuit_contract"])

    def test_prompt_or_token_leak_fails(self):
        rows = copy.deepcopy(_rows())
        row = _case(rows, "local-success-nonstream")
        events = row["events"]
        assert isinstance(events, list)
        events.append({"event": "trace", "prompt": "private prompt"})

        prompt_summary = summarize_reliability(rows)
        events[-1] = {"event": "trace", "api_token": "secret"}
        token_summary = summarize_reliability(rows)

        self.assertFalse(prompt_summary["gate_pass"])
        self.assertFalse(prompt_summary["gate_checks"]["log_redaction"])
        self.assertFalse(token_summary["gate_pass"])
        self.assertFalse(token_summary["gate_checks"]["log_redaction"])

    def test_missing_fallback_reason_fails(self):
        rows = copy.deepcopy(_rows())
        result = _event(_case(rows, "server-error-fallback"), "result")
        result["fallback_reason"] = ""

        summary = summarize_reliability(rows)

        self.assertFalse(summary["gate_pass"])
        self.assertFalse(summary["gate_checks"]["fallback_contract"])

    def test_case_self_report_cannot_override_raw_events(self):
        rows = copy.deepcopy(_rows())
        result = _event(_case(rows, "local-success-nonstream"), "result")
        result["actual_model"] = "wrong"
        _case(rows, "local-success-nonstream")["case_pass"] = True
        _case(rows, "local-success-nonstream")["gate_pass"] = True

        summary = summarize_reliability(rows)

        self.assertFalse(summary["gate_pass"])
        first = summary["case_results"][0]
        self.assertFalse(first["case_pass"])

    def test_unhandled_factory_exception_is_recorded_without_message(self):
        def broken_factory(case):
            del case
            raise RuntimeError("private prompt and private answer")

        row = run_reliability_case(RELIABILITY_CASES[0], broken_factory)
        summary = summarize_reliability([row, *_rows()[1:]])

        self.assertFalse(summary["gate_pass"])
        serialized = json.dumps(row, ensure_ascii=False)
        self.assertIn("unhandled_exception", serialized)
        self.assertNotIn("private prompt", serialized)
        self.assertNotIn("private answer", serialized)

    def test_run_writes_deterministic_artifacts_and_formal_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            deterministic = run_reliability_eval(
                Path(temp_dir) / "deterministic",
                "deterministic",
            )
            formal = run_reliability_eval(Path(temp_dir) / "formal", "formal")
            run_dir = deterministic["run_dir"]
            assert isinstance(run_dir, Path)

            self.assertTrue((run_dir / "manifest.json").exists())
            self.assertTrue((run_dir / "events.json").exists())
            self.assertTrue((run_dir / "summary.json").exists())
            self.assertTrue(deterministic["summary"]["gate_pass"])
            self.assertFalse(formal["summary"]["gate_pass"])
            self.assertFalse(formal["summary"]["gate_checks"]["mode_contract"])

    def test_public_inputs_are_strict(self):
        with self.assertRaises(TypeError):
            run_reliability_case([], _deterministic_gateway_factory)
        with self.assertRaises(ValueError):
            run_reliability_case({"id": "unknown"}, _deterministic_gateway_factory)
        with self.assertRaises(TypeError):
            summarize_reliability({})
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                run_reliability_eval(Path(temp_dir), "unknown")


if __name__ == "__main__":
    unittest.main()
