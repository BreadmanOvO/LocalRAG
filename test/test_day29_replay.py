from __future__ import annotations
import unittest
from agent_platform.runtime.replay import FaultCase, ReplayHarness

class Day29ReplayTests(unittest.TestCase):
    def test_fault_case_is_replayable(self) -> None:
        harness = ReplayHarness((FaultCase("tool-timeout", "tool", "run_failed"),))
        self.assertEqual("run_failed", harness.replay("tool-timeout").expected_state)
    def test_empty_matrix_rejected(self) -> None:
        with self.assertRaises(ValueError): ReplayHarness(()).validate()

if __name__ == "__main__": unittest.main()
