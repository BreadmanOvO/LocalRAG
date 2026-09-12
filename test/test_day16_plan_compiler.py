from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from agent_platform.api import create_app
from agent_platform.routing import ArchitectureSpec, PlanCompiler, TaskProfile

class Day16PlanCompilerTests(unittest.TestCase):
    def test_auto_direct_and_delegate(self) -> None:
        compiler = PlanCompiler()
        direct = compiler.compile(TaskProfile("task-a", "解释问题"), ArchitectureSpec("direct"), mode="auto")
        self.assertEqual("direct", direct.mode)
        delegated = compiler.compile(TaskProfile("task-b", "比较资料", True, ("rag",)), ArchitectureSpec("hierarchical", 2), mode="auto", available_capabilities={"rag"})
        self.assertEqual("delegate", delegated.mode)
        self.assertEqual(("dispatch", "collect", "summarize"), delegated.steps)

    def test_missing_capability_and_direct_architecture_are_rejected(self) -> None:
        compiler = PlanCompiler()
        with self.assertRaises(ValueError):
            compiler.compile(TaskProfile("task-a", "x", True, ("vision",)), ArchitectureSpec("hierarchical", 2), mode="delegate", available_capabilities=set())
        with self.assertRaises(ValueError):
            compiler.compile(TaskProfile("task-a", "x"), ArchitectureSpec("graph", 2), mode="direct")

    def test_api_plan_contract(self) -> None:
        client = TestClient(create_app())
        response = client.post("/plans/compile", json={"task_id": "task-api", "goal": "对比两个方案", "requires_decomposition": True, "architecture": "hierarchical", "max_agents": 2, "required_capabilities": ["rag"]})
        self.assertEqual(200, response.status_code)
        self.assertEqual("delegate", response.json()["mode"])

if __name__ == "__main__": unittest.main()
