from __future__ import annotations

import json
import os
import tempfile
import unittest
from unittest.mock import Mock, patch
from langchain_core.messages import AIMessage
from pathlib import Path

from fastapi.testclient import TestClient

from agent_platform.api import create_app
from agent_platform.integrations.multi_agent_config import CloudAgentClient, CloudAgentSpec, load_cloud_agents
from agent_platform.runtime.multi_agent import CloudTeamRuntime


def _spec(agent_id: str, responsibility: str) -> CloudAgentSpec:
    return CloudAgentSpec(agent_id, agent_id, responsibility, "sensenova", "https://token.sensenova.cn/v1", "sensenova-6.7-flash-lite", "KEY", "secret")


class CloudConfigTests(unittest.TestCase):
    def test_reasoning_only_is_not_a_final_answer(self) -> None:
        with patch("agent_platform.integrations.multi_agent_config.ChatOpenAI") as model:
            model.return_value.invoke.return_value = AIMessage(content="", additional_kwargs={"reasoning_content": "private draft"})
            with self.assertRaisesRegex(RuntimeError, "empty response"):
                CloudAgentClient(_spec("assistant", "助理")).invoke([])
        self.assertNotIn("secret", repr(_spec("assistant", "助理")))

    def test_loader_keeps_credentials_out_of_json_and_allows_disabled_agent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "multi.json"
            path.write_text(json.dumps({"contract_version": "agent-platform-cloud-v1", "agents": {"researcher": {"display_name": "研究员", "responsibility": "研究", "provider": "modelscope", "base_url": "https://api-inference.modelscope.cn/v1", "model": "Qwen/Qwen3-8B", "api_key_env": "MODELSCOPE_API_KEY", "enabled": False}}}), encoding="utf-8")
            agents = load_cloud_agents(path, environ={})
            self.assertFalse(agents["researcher"].enabled)
            self.assertEqual("", agents["researcher"].api_key)


class CloudTeamRuntimeTests(unittest.TestCase):
    def test_unimplemented_architecture_and_missing_independent_agents_fail_before_call(self) -> None:
        invoke = Mock(return_value="ok")
        runtime = CloudTeamRuntime({"chairperson": _spec("chairperson", "汇总"), "reviewer": _spec("reviewer", "审查")}, invoker=invoke)
        for architecture in ("graph", "heterogeneous", "adversarial"):
            with self.assertRaises(ValueError):
                runtime.execute("task", architecture=architecture)
        invoke.assert_not_called()

    def test_partial_turns_survive_failure_and_followup_reads_history(self) -> None:
        calls = []
        def invoke(spec, messages):
            calls.append(str(messages[-1].content))
            if len(calls) == 2:
                raise RuntimeError("provider failed with private key")
            return "已完成计划"
        runtime = CloudTeamRuntime({"chairperson": _spec("chairperson", "汇总"), "reviewer": _spec("reviewer", "审查")}, invoker=invoke)
        client = TestClient(create_app(team_runtime=runtime))
        room_id = client.post("/rooms", json={"space_id": "space-demo"}).json()["room_id"]
        client.post(f"/rooms/{room_id}/messages", json={"content": "前置约束只讨论摄像头"})
        response = client.post(f"/rooms/{room_id}/multi-agent/execute", json={"goal": "继续介绍"})
        self.assertEqual(502, response.status_code)
        self.assertNotIn("private key", response.text)
        self.assertIn("前置约束只讨论摄像头", calls[0])
        messages = client.get(f"/rooms/{room_id}/messages").json()["items"]
        self.assertIn("已完成计划", messages[-1]["content"])
        events = client.get(f"/rooms/{room_id}/events").json()["items"]
        self.assertEqual("run_failed", events[-1]["event_type"])
        response = client.post(f"/rooms/{room_id}/multi-agent/execute", json={"goal": "补充", "architecture": "direct"})
        self.assertEqual(200, response.status_code)

    def test_swarm_shares_prior_outputs_with_reducer(self) -> None:
        calls: list[tuple[str, str]] = []

        def invoke(spec, messages):
            prompt = str(messages[-1].content)
            calls.append((spec.agent_id, prompt))
            return f"{spec.agent_id} result"

        runtime = CloudTeamRuntime({"chairperson": _spec("chairperson", "汇总"), "researcher": _spec("researcher", "研究"), "reviewer": _spec("reviewer", "审查")}, invoker=invoke)
        result = runtime.execute("比较两份资料", architecture="swarm", max_agents=3)
        self.assertEqual("completed", result.status)
        self.assertEqual(["researcher", "reviewer", "chairperson"], [turn.agent_id for turn in result.turns])
        self.assertIn("researcher result", calls[-1][1])
        self.assertIn("reviewer result", calls[-1][1])

    def test_api_persists_team_messages_and_events(self) -> None:
        def invoke(spec, messages):
            return f"answer from {spec.agent_id}"

        runtime = CloudTeamRuntime({"chairperson": _spec("chairperson", "汇总"), "researcher": _spec("researcher", "研究"), "reviewer": _spec("reviewer", "审查")}, invoker=invoke)
        client = TestClient(create_app(team_runtime=runtime))
        room = client.post("/rooms", json={"space_id": "space-demo", "title": "team"}).json()
        response = client.post(f"/rooms/{room['room_id']}/multi-agent/execute", json={"goal": "解释 BEVFormer", "architecture": "hierarchical", "max_agents": 3})
        self.assertEqual(200, response.status_code, response.text)
        payload = response.json()
        self.assertEqual("completed", payload["status"])
        self.assertEqual(3, len(payload["turns"]))
        events = client.get(f"/rooms/{room['room_id']}/events").json()["items"]
        self.assertEqual("run_started", events[1]["event_type"])
        self.assertEqual("run_completed", events[-1]["event_type"])


if __name__ == "__main__":
    unittest.main()
