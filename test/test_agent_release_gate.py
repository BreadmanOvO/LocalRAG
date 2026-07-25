import json
import tempfile
import unittest
from pathlib import Path

from eval.release_gate import evaluate_agent_stability_gate, load_formal_agent_runs


class AgentStabilityGateTests(unittest.TestCase):
    def _write_run(
        self,
        root: Path,
        run_id: str,
        created_at: str,
        *,
        revision: str = "revision-a",
        gate_pass: bool = True,
        complete: bool = True,
        dirty: bool = False,
        selection_complete: bool = True,
        error: str = "",
        retry_count: int = 0,
        contract_version: str = "agent-eval-v2",
        summary_overrides: dict | None = None,
    ) -> None:
        run_dir = root / run_id
        run_dir.mkdir()
        manifest = {
            "contract_version": contract_version,
            "run_id": run_id,
            "created_at": created_at,
            "dataset_path": "data/evaluation/agent/agent_eval_set.json",
            "dataset_version": "agent-eval-v1.2",
            "registry_path": "data/evaluation/shared/source_registry.json",
            "git_revision": revision,
            "git_dirty": dirty,
            "allow_stale_corpus": False,
            "runtime": {"provider": "test", "chat_model_name": "model"},
            "execution": {
                "mode": "formal",
                "agent_temperature": 0,
                "request_timeout_seconds": 60,
                "max_retries": 0,
                "recursion_limit": 12,
                "case_infrastructure_retries": 1,
            },
            "evaluation_scope": {
                "selection_complete": selection_complete,
                "evaluation_complete": complete,
                "expected_case_count": 15,
                "expected_turn_count": 9,
                "expected_probe_types": [
                    "cancel_run_control",
                    "duplicate_call_block",
                    "insufficient_evidence_rejection",
                    "no_progress_termination",
                    "pause_resume_checkpoint",
                    "tool_budget_termination",
                    "verified_evidence_binding",
                ],
                "probe_selection_complete": True,
            },
            "corpus": {
                "persist_directory": "store",
                "collection_name": "rag",
                "registry_source_count": 100,
                "chroma_source_count": 100,
                "chunk_count": 7339,
                "corpus_fingerprint": "sha256:corpus",
                "registry_fingerprint": "sha256:registry",
            },
        }
        summary = {
            "gate_pass": gate_pass,
            "case_count": 15,
            "expected_case_count": 15,
            "passed_case_count": 15 if gate_pass else 0,
            "case_pass_ratio": 1.0 if gate_pass else 0.0,
            "case_tool_contract_pass_count": 15 if gate_pass else 0,
            "case_answer_contract_pass_count": 15 if gate_pass else 0,
            "graph_recursion_error_count": 0,
            "duplicate_tool_violation_count": 0,
            "unclassified_termination_count": 0,
            "verified_finding_count": 1,
            "bound_verified_finding_count": 1,
            "verified_finding_evidence_binding_ratio": 1.0,
            "checkpoint_resume_case_count": 1,
            "checkpoint_resume_pass_count": 1,
            "checkpoint_resume_pass_ratio": 1.0,
            "forbidden_tool_violation_count": 0,
            "expected_probe_types": [
                "cancel_run_control",
                "duplicate_call_block",
                "insufficient_evidence_rejection",
                "no_progress_termination",
                "pause_resume_checkpoint",
                "tool_budget_termination",
                "verified_evidence_binding",
            ],
            "infrastructure_retry_count": retry_count,
            "gate_thresholds": {
                "min_corpus_coverage": 1.0,
                "min_case_pass_ratio": 1.0,
                "min_tool_contract_ratio": 1.0,
                "min_answer_contract_ratio": 1.0,
            },
            "gate_checks": {
                "evaluation_complete": complete,
                "control_probe_coverage": True,
                "graph_recursion_errors": True,
                "classified_termination": True,
                "duplicate_tool_violations": True,
                "verified_finding_evidence_binding": True,
                "checkpoint_resume": True,
                "forbidden_tool_violations": True,
            },
        }
        summary.update(summary_overrides or {})
        turn = {"error": error}
        predictions = [
            {
                "attempt_count": retry_count + 1,
                "infrastructure_retry_count": retry_count,
                "turns": [turn],
                "attempts": [{"attempt": 1, "turns": [turn]}],
            }
        ]
        for name, payload in (
            ("manifest.json", manifest),
            ("summary.json", summary),
            ("predictions.json", predictions),
        ):
            (run_dir / name).write_text(
                json.dumps(payload),
                encoding="utf-8",
            )

    def test_three_consecutive_matching_runs_pass(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-1", "2026-01-01T00:00:00")
            self._write_run(
                root,
                "agent-eval-diagnostic",
                "2026-01-01T00:30:00",
                selection_complete=False,
            )
            self._write_run(root, "agent-eval-2", "2026-01-01T01:00:00")
            self._write_run(root, "agent-eval-3", "2026-01-01T02:00:00")

            result = evaluate_agent_stability_gate(root)
            formal_run_count = len(load_formal_agent_runs(root))

        self.assertTrue(result["gate_pass"])
        self.assertEqual(
            ["agent-eval-1", "agent-eval-2", "agent-eval-3"],
            result["selected_run_ids"],
        )
        self.assertEqual(3, formal_run_count)

    def test_retry_count_is_loaded_from_predictions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(
                root,
                "agent-eval-1",
                "2026-01-01T00:00:00",
                retry_count=1,
            )

            runs = load_formal_agent_runs(root)

        self.assertEqual(1, runs[0]["infrastructure_retry_count"])

    def test_identity_change_fails_stability_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-1", "2026-01-01T00:00:00")
            self._write_run(root, "agent-eval-2", "2026-01-01T01:00:00")
            self._write_run(
                root,
                "agent-eval-3",
                "2026-01-01T02:00:00",
                revision="revision-b",
            )

            result = evaluate_agent_stability_gate(root)

        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["checks"]["identity_consistent"])

    def test_graph_recursion_fails_stability_gate_even_when_ratio_gate_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-1", "2026-01-01T00:00:00")
            self._write_run(root, "agent-eval-2", "2026-01-01T01:00:00")
            self._write_run(
                root,
                "agent-eval-3",
                "2026-01-01T02:00:00",
                error="graph_recursion_limit",
            )

            result = evaluate_agent_stability_gate(root)

        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["checks"]["no_graph_recursion"])

    def test_a5_metric_violation_fails_even_when_summary_gate_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-1", "2026-01-01T00:00:00")
            self._write_run(root, "agent-eval-2", "2026-01-01T01:00:00")
            self._write_run(
                root,
                "agent-eval-3",
                "2026-01-01T02:00:00",
                summary_overrides={"duplicate_tool_violation_count": 1},
            )

            result = evaluate_agent_stability_gate(root)

        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["checks"]["no_duplicate_tool_violations"])

    def test_old_eval_contract_cannot_satisfy_a5_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-1", "2026-01-01T00:00:00")
            self._write_run(root, "agent-eval-2", "2026-01-01T01:00:00")
            self._write_run(
                root,
                "agent-eval-3",
                "2026-01-01T02:00:00",
                contract_version="agent-eval-v1",
            )

            result = evaluate_agent_stability_gate(root)

        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["checks"]["all_a5_contracts"])

    def test_missing_a5_metric_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-1", "2026-01-01T00:00:00")
            self._write_run(root, "agent-eval-2", "2026-01-01T01:00:00")
            self._write_run(
                root,
                "agent-eval-3",
                "2026-01-01T02:00:00",
                summary_overrides={"duplicate_tool_violation_count": None},
            )

            result = evaluate_agent_stability_gate(root)

        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["checks"]["all_a5_contracts"])
        self.assertFalse(result["checks"]["no_duplicate_tool_violations"])

    def test_insufficient_run_count_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-1", "2026-01-01T00:00:00")

            result = evaluate_agent_stability_gate(root)

        self.assertFalse(result["gate_pass"])
        self.assertIn("required_run_count", result["failure_reasons"])

    def test_corrupted_latest_formal_run_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_run(root, "agent-eval-1", "2026-01-01T00:00:00")
            self._write_run(root, "agent-eval-2", "2026-01-01T01:00:00")
            self._write_run(root, "agent-eval-3", "2026-01-01T02:00:00")
            self._write_run(root, "agent-eval-4", "2026-01-01T03:00:00")
            (root / "agent-eval-4" / "summary.json").write_text(
                "not-json",
                encoding="utf-8",
            )

            result = evaluate_agent_stability_gate(root)

        self.assertFalse(result["gate_pass"])
        self.assertFalse(result["checks"]["all_artifacts_valid"])
        self.assertEqual("agent-eval-4", result["selected_run_ids"][-1])


if __name__ == "__main__":
    unittest.main()
