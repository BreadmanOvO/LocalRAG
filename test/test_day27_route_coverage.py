from __future__ import annotations
import unittest
from agent_platform.routing import RouteCase, RouteCoverage

class Day27RouteCoverageTests(unittest.TestCase):
    def test_matrix_records_direct_and_delegate_cases(self) -> None:
        matrix = RouteCoverage((RouteCase("explain", "direct", "direct", "completed"), RouteCase("compare", "hierarchical", "delegate", "completed"), RouteCase("review", "graph", "delegate", "blocked")))
        self.assertEqual({"cases": 3, "direct": 1, "delegate": 2}, matrix.summary())

if __name__ == "__main__": unittest.main()
