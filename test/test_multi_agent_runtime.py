from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from agent_platform.api import create_app
from agent_platform.integrations.multi_agent_config import CloudAgentSpec, load_cloud_agents
from agent_platform.runtime.multi_agent import CloudTeamRuntime


def _spec(agent_id: str, responsibility: str) -> CloudAgentSpec:
    return CloudAgentSpec(agent_id, agent_id, responsibility, "sensenova", "https://token.sensenova.cn/v1", "sensenova-6.7-flash-lite", "KEY", "secret")


class CloudConfigTests(unittest.TestCase):
    def test_loader_keeps_credentials_out_of_json_and_allows_disabled_agent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "multi.json"
            path.write_text(json.dumps({"contract_version": "agent-platform-cloud-v1", "agents": {"researcher": {"display_name": "研究员", "responsibility": "研究", "provider": "modelscope", "base_url": "https://api-inference.modelscope.cn/v1", "model": "Qwen/Qwen3-8B", "api_key_env": "MODELSCOPE_API_KEY", "enabled": False}}}), encoding="utf-8")
            agents = load_cloud_agents(path, environ={})
            self.assertFalse(agents["researcher"].enabled)
            self.assertEqual("", agents["researcher"].api_key)


class CloudTeamRuntimeTests(unittest.TestCase):
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
