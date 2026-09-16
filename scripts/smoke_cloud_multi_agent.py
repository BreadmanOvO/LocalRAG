"""Opt-in live smoke for configured cloud models and team architectures."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from agent_platform.api import create_app
from agent_platform.integrations.multi_agent_config import DEFAULT_CONFIG, load_cloud_team_config
from agent_platform.runtime.multi_agent import CloudTeamRuntime


def _summary(path: Path) -> dict[str, object]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    profiles = raw.get("model_profiles", {})
    agents = raw.get("agents", {})
    enabled_profiles = []
    for profile_id, item in profiles.items():
        if not item.get("enabled", True):
            continue
        env_name = str(item.get("api_key_env", "")).strip()
        enabled_profiles.append({
            "profile_id": profile_id,
            "model": str(item.get("model", "")),
            "key_present": bool(str(item.get("api_key", "")).strip() or (env_name and os.environ.get(env_name, "").strip())),
        })
    enabled_agents = [
        {"agent_id": agent_id, "binding_mode": str(item.get("model_binding_mode", "fixed"))}
        for agent_id, item in agents.items() if item.get("enabled", True)
    ]
    return {
        "config": str(path),
        "enabled_profiles": enabled_profiles,
        "enabled_agents": enabled_agents,
        "ready_for_adversarial": len(enabled_agents) >= 3,
    }


def run_live(path: Path) -> dict[str, object]:
    runtime = CloudTeamRuntime.from_config(path)
    client = TestClient(create_app(team_runtime=runtime))
    nonce = uuid4().hex[:10]
    reports = []
    for architecture, max_agents in (("direct", 1), ("hierarchical", 3), ("swarm", 3), ("adversarial", 3), ("graph", 3), ("heterogeneous", 3)):
        room = client.post("/rooms", json={"space_id": "space-cloud-smoke", "title": f"cloud-{architecture}"})
        room.raise_for_status()
        started = time.perf_counter()
        response = client.post(
            f"/rooms/{room.json()['room_id']}/multi-agent/execute",
            json={"goal": f"这是连通性测试 {nonce}。每个步骤只回复一句话，不要扩展任务。", "architecture": architecture, "max_agents": max_agents,
                "persona_theme": "emperor"},
        )
        report = {"architecture": architecture, "status_code": response.status_code, "latency_seconds": round(time.perf_counter() - started, 3)}
        if response.status_code == 200:
            body = response.json()
            report.update({"status": body["status"], "turn_count": len(body["turns"]), "models": sorted({turn["model"] for turn in body["turns"]})})
        else:
            body = response.json()
            report.update({"status": "failed", "error_code": body.get("code", "unknown")})
            history = client.get(f"/rooms/{room.json()['room_id']}/events", params={"limit": 1000}).json()["items"]
            report["step_errors"] = [e["payload"].get("error") for e in history if e["event_type"] == "step_failed"]
        reports.append(report)
        print(json.dumps(report, ensure_ascii=False), flush=True)
    client.app.state.team_worker.close()
    return {"nonce": nonce, "architectures": reports}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate LocalRAG cloud multi-agent configuration")
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("LOCALRAG_MULTI_AGENT_CONFIG", DEFAULT_CONFIG)))
    parser.add_argument("--live", action="store_true", help="send paid/external model requests")
    args = parser.parse_args()
    try:
        summary = _summary(args.config)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        missing = [item["profile_id"] for item in summary["enabled_profiles"] if not item["key_present"]]  # type: ignore[index]
        if missing:
            print(json.dumps({"status": "not_configured", "missing_profile_keys": missing}, ensure_ascii=False))
            return 2
        if not args.live:
            print(json.dumps({"status": "ready", "live_requests": False}, ensure_ascii=False))
            return 0
        result = run_live(args.config)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if all(item["status"] == "completed" for item in result["architectures"]) else 1  # type: ignore[index]
    except Exception as exc:
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
