from __future__ import annotations
import unittest
from agent_platform.runtime.integration import IntegrationCheck, IntegrationGate

class Day28IntegrationTests(unittest.TestCase):
    def test_publish_does_not_require_evaluation(self) -> None:
        check = IntegrationGate().publish_without_evaluation("gen-1")
        self.assertFalse(check.evaluation_requested)
    def test_incomplete_composition_is_rejected(self) -> None:
        with self.assertRaises(ValueError): IntegrationGate().validate(IntegrationCheck("", "gen", "direct"))

if __name__ == "__main__": unittest.main()
