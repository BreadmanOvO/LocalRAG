import tempfile
import unittest
from pathlib import Path

from eval.day2_failure_probes import run_d02_probes


class Day2FailureProbeTests(unittest.TestCase):
    def test_historical_failure_matrix_is_reproducible_without_external_services(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_d02_probes(Path(temp_dir))

        self.assertEqual("D02", result["day"])
        self.assertTrue(result["all_pass"], result)
        self.assertEqual(
            {
                "model_request_failed",
                "research_run_active",
                "tool_call_limit_exceeded",
                "compression_followup",
                "empty_task_memory",
            },
            {probe["probe"] for probe in result["probes"]},
        )


if __name__ == "__main__":
    unittest.main()
