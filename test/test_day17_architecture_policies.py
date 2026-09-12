from __future__ import annotations
import unittest
from agent_platform.architectures import GraphPolicy, HierarchicalPolicy, validate_dependencies

class Day17ArchitecturePolicyTests(unittest.TestCase):
    def test_hierarchical_plan_has_parent_dependencies(self) -> None:
        plan = HierarchicalPolicy().plan("研究问题")
        validate_dependencies(plan)
        self.assertEqual("hierarchical", plan.architecture)
        self.assertEqual(("root",), plan.nodes[1].depends_on)

    def test_graph_plan_is_checkpointable_dag(self) -> None:
        plan = GraphPolicy().plan("计算指标")
        validate_dependencies(plan)
        self.assertEqual("graph", plan.architecture)
        self.assertEqual(("compute",), plan.nodes[-1].depends_on)

    def test_invalid_dependency_is_rejected(self) -> None:
        from agent_platform.architectures import PolicyNode, PolicyPlan
        with self.assertRaises(ValueError): validate_dependencies(PolicyPlan("graph", (PolicyNode("a", "x", ("missing",)),)))

if __name__ == "__main__": unittest.main()
