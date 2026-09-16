"""Execution acceptance: persistence, ownership, recovery and room lifecycle."""
from collections import Counter
from dataclasses import replace
from threading import Event
from unittest.mock import patch
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, update

from agent_platform.api import create_app
from agent_platform.integrations.multi_agent_config import CloudAgentSpec
from agent_platform.runtime.durable_team import DurableTeamStore, RoomLeaseBusy
from agent_platform.runtime.multi_agent import CloudTeamRuntime
from agent_platform.runtime.team_scheduler import ModelCircuitBreaker, CircuitOpenError
from agent_platform.runtime.team_scheduler import transient_error


def runtime(invoker=None):
    agents = {key: CloudAgentSpec(key, key, key, "test", "http://localhost:9/v1", "test-model", "TEST_KEY", "not-a-real-key")
        for key in ("chief_eunuch", "grand_secretary", "minister_works", "academician")}
    return CloudTeamRuntime(agents, invoker=invoker or (lambda spec, messages: f"成果 {spec.agent_id}"))


def wait_terminal(client, room_id):
    for _ in range(150):
        items = client.get(f"/rooms/{room_id}/events", params={"limit": 1000}).json()["items"]
        if any(e["event_type"] in {"run_completed", "run_failed"} for e in items):
            return items
        time.sleep(.02)
    raise AssertionError("run did not terminate")


@pytest.mark.parametrize("mode", ["direct", "hierarchical", "swarm", "adversarial", "graph", "heterogeneous"])
def test_modes_repeat_with_persistent_events(tmp_path, mode):
    url = f"sqlite:///{tmp_path / 'workspace.db'}"
    with TestClient(create_app(database_url=url, team_runtime=runtime())) as client:
        room_id = client.post("/rooms", json={"space_id": "space-test"}).json()["room_id"]
        for _ in range(3):
            result = client.post(f"/rooms/{room_id}/multi-agent/execute", json={"goal": "完成工作", "architecture": mode, "persona_theme": "emperor"})
            assert result.status_code == 200, result.text
            assert result.json()["status"] == "completed"
        before = client.get(f"/rooms/{room_id}/events", params={"limit": 1000}).json()
        assert sum(e["event_type"] == "run_completed" for e in before["items"]) == 3
    with TestClient(create_app(database_url=url, team_runtime=runtime())) as client:
        assert client.get(f"/rooms/{room_id}/events", params={"limit": 1000}).json() == before
        assert client.get(f"/rooms/{room_id}/messages").json()["items"]


def test_room_close_reopen_delete_survive_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'rooms.db'}"
    with TestClient(create_app(database_url=url)) as client:
        room_id = client.post("/rooms", json={"space_id": "space-test"}).json()["room_id"]
        client.post(f"/rooms/{room_id}/messages", json={"content": "保留历史"})
        assert client.post(f"/rooms/{room_id}/archive").json()["status"] == "archived"
        assert client.get(f"/rooms/{room_id}/messages").json()["items"][0]["content"] == "保留历史"
        assert client.post(f"/rooms/{room_id}/messages", json={"content": "不准追加"}).status_code == 409
    with TestClient(create_app(database_url=url)) as client:
        assert client.post(f"/rooms/{room_id}/reopen").json()["status"] == "active"
        assert client.delete(f"/rooms/{room_id}").json()["status"] == "deleted"
        assert client.get(f"/rooms/{room_id}").status_code == 404
        assert client.get(f"/rooms/{room_id}/events").status_code == 404
        assert client.get("/rooms").json()["items"] == []


def test_recover_after_restart_skips_completed_model_calls(tmp_path):
    url = f"sqlite:///{tmp_path / 'resume.db'}"
    calls = Counter()
    def invoke(spec, messages):
        calls[spec.agent_id] += 1
        if spec.agent_id == "minister_works":
            raise ValueError("permanent failure")
        return "完成 " + spec.agent_id
    with TestClient(create_app(database_url=url, team_runtime=runtime(invoke))) as client:
        reply = client.post("/assistant/messages", json={"space_id": "space-test", "content": "分工", "architecture": "hierarchical", "persona_theme": "emperor"})
        room_id = reply.json()["room"]["room_id"]
        events = wait_terminal(client, room_id)
        assert any(e["event_type"] == "run_failed" for e in events)
    second_calls = Counter()
    with TestClient(create_app(database_url=url, team_runtime=runtime(lambda s, m: second_calls.update([s.agent_id]) or "恢复成果"))) as client:
        assert client.post(f"/rooms/{room_id}/start").json()["status"] == "queued"
        client.app.state.team_worker.close()
        events = client.get(f"/rooms/{room_id}/events", params={"limit": 1000}).json()["items"]
        assert events[-1]["event_type"] == "run_completed"
        assert second_calls == {"minister_works": 1, "chief_eunuch": 1}
        assert sum(e["event_type"] == "step_reused" for e in events) == 2


def test_transient_retry_is_local_to_failed_step():
    calls = Counter()
    def invoke(spec, messages):
        calls[spec.agent_id] += 1
        if spec.agent_id == "grand_secretary" and calls[spec.agent_id] == 1:
            raise TimeoutError("temporary")
        return "ok"
    result = runtime(invoke).execute("工作", architecture="hierarchical", persona_theme="emperor")
    assert result.status == "completed"
    assert calls == {"chief_eunuch": 2, "grand_secretary": 2, "minister_works": 1}


def test_partial_swarm_failure_blocks_summary_and_keeps_success():
    turns, events = [], []
    def invoke(spec, messages):
        if spec.agent_id == "grand_secretary":
            raise ValueError("bad input")
        return "good output"
    with pytest.raises(ValueError):
        runtime(invoke).execute("工作", architecture="swarm", persona_theme="emperor", on_turn=turns.append, on_activity=lambda t, p: events.append((t, p)))
    assert [t.agent_id for t in turns] == ["chief_eunuch", "minister_works"]
    assert all(not t.is_final for t in turns)
    assert any(t == "step_blocked" and p["agent_id"] == "chief_eunuch" for t, p in events)


def test_circuit_cooldown_allows_only_one_probe():
    now = [0]
    breaker = ModelCircuitBreaker(threshold=2, cooldown=10, clock=lambda: now[0])
    key = ("test",)
    breaker.failure(key, False)
    breaker.failure(key, False)
    with pytest.raises(CircuitOpenError):
        breaker.acquire(key)
    now[0] = 11
    assert breaker.acquire(key)
    with pytest.raises(CircuitOpenError):
        breaker.acquire(key)
    breaker.success(key, True)
    assert not breaker.acquire(key)


def test_durable_claim_fences_stale_owner(tmp_path):
    url = f"sqlite:///{tmp_path / 'leases.db'}"
    first, second = DurableTeamStore(create_engine(url)), DurableTeamStore(create_engine(url))
    token = first.claim("room-test")
    with pytest.raises(RoomLeaseBusy):
        second.claim("room-test")
    with first.engine.begin() as conn:
        conn.execute(update(first.rooms).values(expires_at=0))
    next_token = second.claim("room-test")
    with pytest.raises(RoomLeaseBusy):
        first.heartbeat("room-test", token)
    first.release("room-test", token)
    second.heartbeat("room-test", next_token)


def test_persistent_binding_has_no_key_and_rejects_changed_model():
    original = runtime()
    snapshot = original.freeze_model_bindings(architecture="direct", persona_theme="emperor")
    saved = snapshot.persistent()
    assert "not-a-real-key" not in str(saved)
    changed = runtime()
    changed._profiles = {}
    changed.agents["chief_eunuch"] = replace(changed.agents["chief_eunuch"], model="changed")
    with pytest.raises(RuntimeError):
        changed.restore_bindings(saved)


def test_quota_exhaustion_does_not_retry():
    exc = RuntimeError("quota")
    exc.status_code = 429
    exc.body = {"code": "insufficient_quota"}
    assert not transient_error(exc)


def test_binding_write_failure_does_not_leave_active_room(tmp_path):
    with TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'failure.db'}", team_runtime=runtime())) as client:
        rid = client.post("/rooms", json={"space_id": "space-test"}).json()["room_id"]
        with patch.object(DurableTeamStore, "save_bindings", side_effect=RuntimeError("database failed")):
            with pytest.raises(RuntimeError):
                client.post(f"/rooms/{rid}/multi-agent/execute", json={"goal": "测试", "architecture": "direct", "persona_theme": "emperor"})
        lease_store = DurableTeamStore(client.app.state.runtime_store.engine)
        assert not lease_store.active(rid)
        assert not lease_store.bindings(rid)
        assert not any(e["event_type"] == "run_started" for e in client.get(f"/rooms/{rid}/events").json()["items"])
        response = client.post(f"/rooms/{rid}/multi-agent/execute", json={"goal": "测试", "architecture": "direct", "persona_theme": "emperor"})
        assert response.status_code == 200, response.text


def test_cancel_is_durable_before_model_returns(tmp_path):
    started, release = Event(), Event()
    def invoke(spec, messages):
        started.set()
        assert release.wait(10)
        return "late output"
    with TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'cancel.db'}", team_runtime=runtime(invoke))) as client:
        try:
            response = client.post("/assistant/messages", json={"space_id": "space-test", "content": "测试", "persona_theme": "emperor", "architecture": "direct"})
            rid = response.json()["room"]["room_id"]
            assert started.wait(5)
            run_id = next(e["run_id"] for e in client.get(f"/rooms/{rid}/events").json()["items"] if e["event_type"] == "run_started")
            state = client.get(f"/runs/{run_id}").json()
            reply = client.post("/commands/operation-cancel-test", json={"action": "cancel", "run_id": run_id, "expected_row_version": state["row_version"], "expected_control_epoch": state["control_epoch"]})
            assert reply.status_code == 200, reply.text
            assert client.app.state.runtime_store.get_run(run_id)["status"] == "cancelled"
            assert client.get(f"/rooms/{rid}/events").json()["items"][-1]["event_type"] == "run_cancelled"
            task_id = client.app.state.runtime_store.get_run(run_id)["task_id"]
            assert client.get(f"/tasks/{task_id}").json()["status"] == "cancelled"
            with TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'cancel.db'}")) as restarted:
                assert restarted.get(f"/runs/{run_id}").json()["status"] == "cancelled"
                assert restarted.get(f"/tasks/{task_id}").json()["active_run_id"] is None
                execution = restarted.get(f"/rooms/{rid}/execution").json()
                assert execution["status"] == "cancelled"
                assert not execution["can_resume"]
                replay = restarted.post("/commands/operation-cancel-test", json={"action": "cancel", "run_id": run_id, "expected_row_version": state["row_version"], "expected_control_epoch": state["control_epoch"]})
                assert replay.json() == reply.json()
                assert sum(e["event_type"] == "run_cancelled" for e in restarted.get(f"/rooms/{rid}/events").json()["items"]) == 1
        finally:
            release.set()
    with TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'cancel.db'}")) as restarted:
        assert restarted.get(f"/tasks/{task_id}").json()["status"] == "cancelled"
        assert not any(e["event_type"] == "step_completed" for e in restarted.get(f"/rooms/{rid}/events").json()["items"])


def test_cancel_command_after_api_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'command.db'}"
    with TestClient(create_app(database_url=url)) as client:
        rid = client.post("/rooms", json={"space_id": "space-test"}).json()["room_id"]
        tid = client.post("/tasks", json={"room_id": rid, "title": "取消测试"}).json()["task_id"]
        run = client.post("/runs", json={"task_id": tid, "status": "running"}).json()
    with TestClient(create_app(database_url=url)) as restarted:
        reply = restarted.post("/commands/operation-after-restart", json={"action": "cancel", "run_id": run["run_id"], "expected_row_version": run["row_version"], "expected_control_epoch": run["control_epoch"]})
        assert reply.status_code == 200, reply.text
        assert restarted.get(f"/tasks/{tid}").json()["status"] == "cancelled"


def test_changed_plan_cannot_reuse_checkpoint(tmp_path):
    def fail(spec, messages):
        raise ValueError("failed step")
    with TestClient(create_app(database_url=f"sqlite:///{tmp_path / 'plan.db'}", team_runtime=runtime(fail))) as client:
        rid = client.post("/assistant/messages", json={"space_id": "space-test", "content": "工作", "persona_theme": "emperor"}).json()["room"]["room_id"]
        wait_terminal(client, rid)
        with patch("agent_platform.api.app.inspect.getsource", return_value="changed plan"):
            reply = client.post(f"/rooms/{rid}/start")
        assert reply.json()["status"] == "blocked"
        items = client.get(f"/rooms/{rid}/events").json()["items"]
        assert items[-1]["event_type"] == "task_start_failed"
        assert "执行计划" in items[-1]["payload"]["error"]
