import tempfile
import unittest
from pathlib import Path

from agent.research import ResearchExecutionIdentity
from eval.agent_control_probes import run_control_probe
from eval.agent_eval_contract import CONTROL_PROBE_NAMES


class AgentControlProbeTests(unittest.TestCase):
    @staticmethod
    def _identity() -> ResearchExecutionIdentity:
        return ResearchExecutionIdentity(
            corpus_fingerprint="sha256:corpus",
            registry_fingerprint="sha256:registry",
            code_revision="revision-a",
        )

    def test_all_control_probes_execute_against_production_boundaries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            results = {
                probe: run_control_probe(probe, self._identity(), root / probe)
                for probe in CONTROL_PROBE_NAMES
            }

        self.assertTrue(all(result["case_pass"] for result in results.values()))
        self.assertEqual(
            "tool_call_limit_exceeded",
            results["tool_budget_termination"]["termination"]["observed_code"],
        )
        self.assertTrue(results["duplicate_call_block"]["duplicate"]["blocked"])
        self.assertFalse(results["duplicate_call_block"]["duplicate"]["violation"])
        self.assertEqual(
            "no_progress_limit",
            results["no_progress_termination"]["termination"]["observed_code"],
        )

    def test_evidence_and_recovery_probes_persist_expected_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            insufficient = run_control_probe(
                "insufficient_evidence_rejection",
                self._identity(),
                root / "insufficient",
            )
            bound = run_control_probe(
                "verified_evidence_binding",
                self._identity(),
                root / "bound",
            )
            resumed = run_control_probe(
                "pause_resume_checkpoint",
                self._identity(),
                root / "resume",
            )
            cancelled = run_control_probe(
                "cancel_run_control",
                self._identity(),
                root / "cancel",
            )

        self.assertTrue(insufficient["evidence_binding"]["invalid_binding_rejected"])
        self.assertEqual(1, bound["evidence_binding"]["verified_finding_count"])
        self.assertEqual(1, bound["evidence_binding"]["bound_verified_finding_count"])
        self.assertTrue(resumed["resume"]["checkpoint_resume_pass"])
        self.assertEqual("cancelled", cancelled["control"]["final_status"])


if __name__ == "__main__":
    unittest.main()
