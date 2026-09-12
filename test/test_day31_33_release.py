from __future__ import annotations
import unittest
from agent_platform.runtime.release_gate import Readiness

class Day31To33ReleaseTests(unittest.TestCase):
    def test_no_go_lists_blockers(self) -> None:
        readiness = Readiness(True, True, False, False, 1)
        self.assertEqual("no-go", readiness.decision())
        self.assertEqual(("deployment", "backup_restore", "critical_failures"), readiness.blockers())
    def test_go_requires_all_gates(self) -> None:
        self.assertEqual("go", Readiness(True, True, True, True).decision())

if __name__ == "__main__": unittest.main()
