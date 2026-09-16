from __future__ import annotations

import unittest

from agent_platform.routing import TaskRouter


class TaskRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.router = TaskRouter()

    def test_short_question_is_direct(self) -> None:
        decision = self.router.route("什么是 BEVFormer？")
        self.assertEqual("direct", decision.mode)
        self.assertEqual("direct", decision.architecture)

    def test_review_and_visual_tasks_choose_distinct_strategies(self) -> None:
        review = self.router.route("请审查这份方案并指出风险")
        visual = self.router.route("分析这张图片里的表格")
        self.assertEqual("adversarial", review.architecture)
        self.assertEqual("heterogeneous", visual.architecture)
        self.assertGreaterEqual(review.max_agents, 3)

    def test_explicit_architecture_wins(self) -> None:
        decision = self.router.route("简单回答", requested_architecture="swarm", max_agents=2)
        self.assertEqual("swarm", decision.architecture)
        self.assertEqual("delegate", decision.mode)

    def test_long_task_exposes_capability_signals_for_participant_selection(self) -> None:
        decision = self.router.route("研究论文并整理证据，最后写一份详细技术报告与实施建议供团队使用")
        self.assertEqual("hierarchical", decision.architecture)
        self.assertEqual(("research", "writing"), decision.required_capabilities)


if __name__ == "__main__":
    unittest.main()
