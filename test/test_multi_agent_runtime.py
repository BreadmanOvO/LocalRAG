from __future__ import annotations

import json
import tempfile
import unittest
import time
import threading
from unittest.mock import Mock, patch
from langchain_core.messages import AIMessage
from pathlib import Path

from fastapi.testclient import TestClient

from agent_platform.api import create_app
from agent_platform.integrations.multi_agent_config import CloudAgentClient, CloudAgentSpec, CloudModelProfile, load_cloud_agents, load_cloud_team_config
from agent_platform.runtime.multi_agent import CloudTeamRuntime, ModelRoutingError


def _spec(agent_id: str, responsibility: str) -> CloudAgentSpec:
    return CloudAgentSpec(agent_id, agent_id, responsibility, "sensenova", "https://token.sensenova.cn/v1", "sensenova-6.7-flash-lite", "KEY", "secret")


def _profile(
    profile_id: str,
    model: str,
    *,
    tier: str = "strong",
    capabilities: tuple[str, ...] = ("reasoning",),
    modalities: tuple[str, ...] = ("text",),
    scenarios: tuple[str, ...] = ("research",),
    max_concurrency: int = 4,
) -> CloudModelProfile:
    return CloudModelProfile(
        profile_id=profile_id,
        display_name=profile_id,
        provider="sensenova",
        base_url="https://token.sensenova.cn/v1",
        model=model,
        api_key_env="KEY",
        api_key="secret",
        tier=tier,
        capabilities=capabilities,
        modalities=modalities,
        scenarios=scenarios,
        max_concurrency=max_concurrency,
    )


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

    def test_loader_accepts_inline_key_and_model_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "multi.json"
            path.write_text(json.dumps({
                "contract_version": "agent-platform-cloud-v1",
                "model_profiles": {"strong-text": {"provider": "sensenova", "base_url": "https://token.sensenova.cn/v1", "model": "strong", "api_key_env": "UNSET", "api_key": "inline-secret", "capabilities": ["reasoning"], "modalities": ["text"], "max_concurrency": 4}},
                "agents": {"chairperson": {"display_name": "总助理", "responsibility": "汇总", "model_profile": "strong-text", "tier": "lead", "system_prompt": "brief"}},
            }), encoding="utf-8")
            agents = load_cloud_agents(path, environ={})
            self.assertEqual("inline-secret", agents["chairperson"].api_key)
            self.assertEqual("strong-text", agents["chairperson"].model_profile)
            self.assertEqual("lead", agents["chairperson"].tier)

    def test_loader_keeps_automatic_agent_unresolved_until_runtime_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "multi.json"
            path.write_text(json.dumps({
                "contract_version": "agent-platform-cloud-v1",
                "model_profiles": {
                    "vision": {
                        "provider": "sensenova", "base_url": "https://token.sensenova.cn/v1",
                        "model": "vision-model", "api_key": "inline-secret", "tier": "strong",
                        "capabilities": ["reasoning", "vision"], "modalities": ["text", "image"],
                        "scenarios": ["research", "image-understanding"], "max_concurrency": 8,
                    },
                },
                "agents": {
                    "chairperson": {
                        "display_name": "总助理", "responsibility": "汇总", "model_binding_mode": "auto",
                        "auto_tier": "strong", "auto_modalities": ["image"],
                        "auto_capabilities": ["reasoning"], "auto_scenarios": ["research"],
                    },
                },
            }), encoding="utf-8")
            loaded = load_cloud_team_config(path, environ={})
            self.assertEqual("auto", loaded.agents["chairperson"].model_binding_mode)
            self.assertEqual("", loaded.agents["chairperson"].model)
            runtime = CloudTeamRuntime(loaded.agents, profiles=loaded.profiles, invoker=lambda spec, messages: spec.model)
            result = runtime.execute("理解图片", architecture="direct")
            self.assertEqual("vision-model", result.turns[0].model)
            self.assertEqual("vision", result.turns[0].model_profile)

    def test_fixed_profile_snapshot_preserves_agent_level_connection_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "multi.json"
            path.write_text(json.dumps({
                "contract_version": "agent-platform-cloud-v1",
                "model_profiles": {
                    "shared": {
                        "provider": "sensenova", "base_url": "https://token.sensenova.cn/v1",
                        "model": "shared-model", "api_key": "profile-key",
                    },
                },
                "agents": {
                    "chairperson": {
                        "display_name": "总助理", "responsibility": "汇总", "model_profile": "shared",
                        "model": "agent-model", "api_key": "agent-key",
                    },
                },
            }), encoding="utf-8")
            loaded = load_cloud_team_config(path, environ={})
            seen: list[tuple[str, str]] = []
            runtime = CloudTeamRuntime(
                loaded.agents,
                profiles=loaded.profiles,
                invoker=lambda spec, messages: (seen.append((spec.model, spec.api_key)) or "ok"),
            )
            runtime.execute("固定模型", architecture="direct")
            self.assertEqual([("agent-model", "agent-key")], seen)


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
        response = client.post(f"/rooms/{room_id}/multi-agent/execute", json={"goal": "继续介绍", "architecture": "hierarchical"})
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

    def test_swarm_runs_independent_agents_concurrently_with_isolated_prompts(self) -> None:
        barrier = threading.Barrier(2)
        prompts: dict[str, str] = {}

        def invoke(spec, messages):
            prompts[spec.agent_id] = str(messages[-1].content)
            if spec.agent_id in {"researcher", "reviewer"}:
                barrier.wait(timeout=2)
            return f"{spec.agent_id} result"

        runtime = CloudTeamRuntime({"chairperson": _spec("chairperson", "汇总"), "researcher": _spec("researcher", "研究"), "reviewer": _spec("reviewer", "审查")}, invoker=invoke)
        result = runtime.execute("并发独立探索", architecture="swarm", max_agents=3)
        self.assertEqual(["researcher", "reviewer", "chairperson"], [turn.agent_id for turn in result.turns])
        self.assertNotEqual(prompts["researcher"], prompts["reviewer"])

    def test_model_settings_rebind_only_future_runtime_calls(self) -> None:
        runtime = CloudTeamRuntime({"chairperson": _spec("chairperson", "汇总"), "reviewer": _spec("reviewer", "审查")}, invoker=lambda spec, messages: "ok")
        client = TestClient(create_app(team_runtime=runtime))
        settings = client.get("/settings/models")
        self.assertEqual(200, settings.status_code)
        updated = client.put("/settings/models/chairperson", json={"source_agent_id": "reviewer", "tier": "strong"})
        self.assertEqual(200, updated.status_code, updated.text)
        chair = next(item for item in updated.json()["agents"] if item["agent_id"] == "chairperson")
        self.assertEqual("strong", chair["tier"])
        self.assertEqual("sensenova-6.7-flash-lite", chair["model"])

    def test_running_execution_keeps_model_snapshot_after_rebind(self) -> None:
        chair = _spec("chairperson", "汇总")
        researcher = CloudAgentSpec("researcher", "研究", "研究", "sensenova", "https://token.sensenova.cn/v1", "research-model", "KEY", "secret")
        reviewer = CloudAgentSpec("reviewer", "审查", "审查", "sensenova", "https://token.sensenova.cn/v1", "review-model", "KEY", "secret")
        runtime = CloudTeamRuntime({"chairperson": chair, "researcher": researcher, "reviewer": reviewer})
        calls = []

        def invoke(spec, messages):
            calls.append((spec.agent_id, spec.model))
            if len(calls) == 1:
                runtime.update_model_binding("researcher", source_agent_id="reviewer")
            return spec.model

        runtime._invoker = invoke
        result = runtime.execute("snapshot", architecture="hierarchical", max_agents=3)
        self.assertEqual(["chairperson", "researcher", "reviewer"], [item[0] for item in calls])
        self.assertEqual("research-model", calls[1][1])
        self.assertEqual("research-model", result.turns[1].content)

    def test_auto_routing_selects_closest_tier_then_higher_concurrency(self) -> None:
        auto = CloudAgentSpec(
            "chairperson", "总助理", "汇总", "", "", "", "", "",
            model_binding_mode="auto",
            auto_tier="strong",
            auto_capabilities=("reasoning",),
            auto_modalities=("image",),
            auto_scenarios=("research",),
        )
        profiles = {
            "standard": _profile("standard", "standard-model", tier="standard", capabilities=("reasoning", "vision"), modalities=("text", "image"), scenarios=("research", "image-understanding"), max_concurrency=16),
            "strong-slow": _profile("strong-slow", "strong-slow-model", capabilities=("reasoning", "vision"), modalities=("text", "image"), scenarios=("research", "image-understanding"), max_concurrency=2),
            "strong-fast": _profile("strong-fast", "strong-fast-model", capabilities=("reasoning", "vision"), modalities=("text", "image"), scenarios=("research", "image-understanding"), max_concurrency=8),
            "premium": _profile("premium", "premium-model", tier="premium", capabilities=("reasoning", "vision"), modalities=("text", "image"), scenarios=("research", "image-understanding"), max_concurrency=32),
        }
        runtime = CloudTeamRuntime({"chairperson": auto}, profiles=profiles, invoker=lambda spec, messages: spec.model)
        result = runtime.execute("分析图像", architecture="direct")
        turn = result.turns[0]
        self.assertEqual("strong-fast-model", turn.model)
        self.assertEqual("strong-fast", turn.model_profile)
        self.assertEqual("auto", turn.selection_mode)
        self.assertIn("最终合并条件", turn.selection_reason)
        self.assertIn("capabilities=reasoning,vision", turn.selection_reason)
        self.assertIn("modalities=image", turn.selection_reason)
        self.assertIn("候选排序：1.strong-fast", turn.selection_reason)
        self.assertIn("并发=8", turn.selection_reason)

    def test_auto_routing_fails_before_provider_call_when_no_profile_matches(self) -> None:
        auto = CloudAgentSpec(
            "chairperson", "总助理", "汇总", "", "", "", "", "",
            model_binding_mode="auto", auto_modalities=("image",), auto_scenarios=("vision-review",),
        )
        invoke = Mock(return_value="unexpected")
        runtime = CloudTeamRuntime({"chairperson": auto}, profiles={"text": _profile("text", "text-model")}, invoker=invoke)
        with self.assertRaisesRegex(ModelRoutingError, "没有符合自动路由条件"):
            runtime.execute("检查图片", architecture="direct")
        invoke.assert_not_called()

    def test_auto_routing_merges_role_and_task_requirements(self) -> None:
        auto = CloudAgentSpec(
            "chairperson", "总助理", "汇总", "", "", "", "", "",
            model_binding_mode="auto",
            auto_capabilities=("reasoning",),
            auto_modalities=("text",),
            auto_scenarios=("research",),
        )
        all_formats = _profile(
            "all-formats",
            "all-formats-model",
            capabilities=("reasoning", "review", "vision", "table", "document"),
            modalities=("text", "image", "table", "pdf"),
            scenarios=("research", "image-understanding", "table-analysis", "document-reading"),
        )
        runtime = CloudTeamRuntime({"chairperson": auto}, profiles={"all-formats": all_formats}, invoker=lambda spec, messages: spec.model)
        snapshot = runtime.freeze_model_bindings(
            architecture="direct",
            max_agents=1,
            goal="审查图片里的表格和 PDF 文档",
            required_capabilities=("review",),
        )
        binding = snapshot.bindings[0]
        self.assertEqual("all-formats", binding.model_profile)
        self.assertIn("capabilities=reasoning,review,vision,table,document", binding.selection_reason)
        self.assertIn("modalities=text,image,table,pdf", binding.selection_reason)
        self.assertIn("scenarios=research,image-understanding,table-analysis,document-reading", binding.selection_reason)

    def test_api_returns_explainable_auto_routing_failure_before_creating_a_run(self) -> None:
        auto = CloudAgentSpec(
            "chairperson", "总助理", "汇总", "", "", "", "", "",
            model_binding_mode="auto", auto_modalities=("image",),
        )
        runtime = CloudTeamRuntime({"chairperson": auto}, profiles={"text": _profile("text", "text-model")}, invoker=Mock(return_value="unexpected"))
        client = TestClient(create_app(team_runtime=runtime))
        room_id = client.post("/rooms", json={"space_id": "space-demo"}).json()["room_id"]
        response = client.post(f"/rooms/{room_id}/multi-agent/execute", json={"goal": "识别图片", "architecture": "direct"})
        self.assertEqual(422, response.status_code, response.text)
        self.assertEqual("model_routing_failed", response.json()["code"])
        self.assertEqual("chairperson", response.json()["details"]["agent_id"])
        self.assertEqual([], client.get(f"/rooms/{room_id}/messages").json()["items"])

    def test_api_merges_task_router_capability_into_auto_routing_reason(self) -> None:
        agents = {
            agent_id: CloudAgentSpec(
                agent_id, agent_id, responsibility, "", "", "", "", "",
                model_binding_mode="auto",
            )
            for agent_id, responsibility in (("chairperson", "汇总"), ("researcher", "研究"), ("reviewer", "审查"))
        }
        runtime = CloudTeamRuntime(
            agents,
            profiles={"review": _profile("review", "review-model", capabilities=("review",))},
            invoker=lambda spec, messages: "ok",
        )
        client = TestClient(create_app(team_runtime=runtime))
        room_id = client.post("/rooms", json={"space_id": "space-demo"}).json()["room_id"]
        response = client.post(f"/rooms/{room_id}/multi-agent/execute", json={"goal": "请审查方案并指出风险", "architecture": "auto", "max_agents": 3})
        self.assertEqual(200, response.status_code, response.text)
        self.assertEqual("adversarial", response.json()["architecture"])
        self.assertIn("capabilities=review", response.json()["turns"][0]["selection_reason"])

    def test_auto_run_snapshot_is_immune_to_profile_change_after_first_turn(self) -> None:
        auto_agents = {
            agent_id: CloudAgentSpec(agent_id, agent_id, responsibility, "", "", "", "", "", model_binding_mode="auto", auto_tier="strong")
            for agent_id, responsibility in (("chairperson", "汇总"), ("researcher", "研究"), ("reviewer", "审查"))
        }
        selected = _profile("selected", "selected-model", max_concurrency=8)
        replacement = _profile("replacement", "replacement-model", tier="premium", max_concurrency=1)
        runtime = CloudTeamRuntime(auto_agents, profiles={"selected": selected, "replacement": replacement})
        calls: list[str] = []

        def invoke(spec, messages):
            calls.append(spec.model)
            if len(calls) == 1:
                with runtime._configuration_lock:
                    runtime._profiles["selected"] = _profile("selected", "changed-model", max_concurrency=8)
            return spec.model

        runtime._invoker = invoke
        result = runtime.execute("冻结自动路由", architecture="hierarchical", max_agents=3)
        self.assertEqual(["selected-model", "selected-model", "selected-model"], calls)
        self.assertEqual(["selected-model"] * 3, [turn.model for turn in result.turns])

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
        self.assertEqual("sensenova-6.7-flash-lite", payload["turns"][0]["model"])
        self.assertEqual("fixed", payload["turns"][0]["selection_mode"])
        events = client.get(f"/rooms/{room['room_id']}/events").json()["items"]
        self.assertEqual("run_started", events[1]["event_type"])
        self.assertEqual("sensenova-6.7-flash-lite", events[1]["payload"]["model_snapshot"][0]["model"])
        completed_steps = [event for event in events if event["event_type"] == "step_completed"]
        self.assertEqual("sensenova-6.7-flash-lite", completed_steps[0]["payload"]["model"])
        self.assertNotIn("secret", str(events))
        self.assertEqual("run_completed", events[-1]["event_type"])

    def test_background_execution_returns_run_id_and_persists_completion(self) -> None:
        runtime = CloudTeamRuntime({"chairperson": _spec("chairperson", "汇总")}, invoker=lambda spec, messages: "done")
        with TestClient(create_app(team_runtime=runtime)) as client:
            room = client.post("/rooms", json={"space_id": "space-demo", "title": "async"}).json()
            response = client.post(f"/rooms/{room['room_id']}/multi-agent/execute", json={"goal": "异步处理", "architecture": "direct", "background": True})
            self.assertEqual(200, response.status_code, response.text)
            self.assertEqual("queued", response.json()["status"])
            run_id = response.json()["run_id"]
            for _ in range(40):
                if client.get(f"/runs/{run_id}").json()["status"] == "completed":
                    break
                time.sleep(0.02)
            self.assertEqual("completed", client.get(f"/runs/{run_id}").json()["status"])


if __name__ == "__main__":
    unittest.main()
