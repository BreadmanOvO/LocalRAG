from __future__ import annotations
import unittest
from agent_platform.runtime.evaluation import EvaluationResult

class Day30EvaluationTests(unittest.TestCase):
    def test_completion_rate_and_long_session_counts(self) -> None:
        result = EvaluationResult(60, 57, 10, 5); result.validate()
        self.assertAlmostEqual(0.95, result.completion_rate)
    def test_invalid_pass_count_rejected(self) -> None:
        with self.assertRaises(ValueError): EvaluationResult(10, 11, 0, 0).validate()

if __name__ == "__main__": unittest.main()
