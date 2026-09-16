"""Check the local workspace API using an isolated DB and no model provider."""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
LOCAL_HTTP = build_opener(ProxyHandler({}))


def _runtime_python() -> Path:
    candidates: list[Path] = []
    candidates.append(Path(sys.executable))
    configured = os.environ.get("LOCALRAG_PYTHON")
    if configured:
        candidates.append(Path(configured))
    candidates.extend((ROOT / ".venv" / "Scripts" / "python.exe", ROOT / ".venv" / "bin" / "python"))
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        candidates.append(Path(conda_prefix) / "python.exe")
    conda_exe = os.environ.get("CONDA_EXE")
    if conda_exe:
        candidates.append(Path(conda_exe).resolve().parent.parent / "python.exe")
    for command in ("python", "python3"):
        resolved = shutil.which(command)
        if resolved:
            candidates.append(Path(resolved))
    seen: set[str] = set()
    for candidate in candidates:
        resolved = str(candidate.resolve()) if candidate.exists() else str(candidate)
        if resolved in seen or not Path(resolved).exists():
            continue
        seen.add(resolved)
        probe = subprocess.run([resolved, "-c", "import fastapi"], capture_output=True, check=False)
        if probe.returncode == 0:
            return Path(resolved)
    raise RuntimeError("FastAPI is unavailable; activate the project .venv/Conda environment or set LOCALRAG_PYTHON")


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _request(base: str, path: str, *, method: str = "GET", payload: dict | None = None, headers: dict[str, str] | None = None, timeout: float = 5) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(base + path, data=body, method=method, headers={"Content-Type": "application/json", **(headers or {})})
    with LOCAL_HTTP.open(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _wait_ready(process, base: str, *, timeout: float = 90) -> None:
    deadline = time.monotonic() + timeout
    last_error = "no response"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"agent platform exited before readiness (exit={process.returncode})")
        try:
            health = _request(base, "/health", timeout=min(1, max(.01, deadline - time.monotonic())))
            if health.get("status") == "ok":
                return
            last_error = "health status is not ok"
        except (URLError, OSError, ValueError) as exc:
            last_error = type(exc).__name__
        time.sleep(min(.2, max(0, deadline - time.monotonic())))
    raise RuntimeError(f"agent platform did not become ready within {timeout:g}s ({last_error})")


def main() -> int:
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    runtime_python = _runtime_python()
    temporary = tempfile.TemporaryDirectory(prefix="localrag-smoke-")
    environment = os.environ.copy()
    database_path = (Path(temporary.name) / "smoke.db").as_posix()
    environment["LOCALRAG_DATABASE_URL"] = f"sqlite:///{database_path}"
    environment["LOCALRAG_MULTI_AGENT_CONFIG"] = str(Path(temporary.name) / "no-models.json")
    environment["LOCALRAG_AUTH_REQUIRED"] = "0"
    startup_log = tempfile.TemporaryFile(mode="w+b")
    process = subprocess.Popen(
        [str(runtime_python), "-m", "uvicorn", "agent_platform.api.app:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=startup_log,
    )
    try:
        _wait_ready(process, base)

        headers = {"Idempotency-Key": "smoke-assistant-1"}
        first = _request(base, "/assistant/messages", method="POST", headers=headers, payload={"space_id": "space-demo", "content": "演示 v1.8 工作台"})
        replay = _request(base, "/assistant/messages", method="POST", headers=headers, payload={"space_id": "space-demo", "content": "演示 v1.8 工作台"})
        room_id = first["room"]["room_id"]
        plan = _request(base, "/plans/compile", method="POST", payload={"task_id": "task-smoke", "goal": "比较资料", "requires_decomposition": True, "architecture": "hierarchical", "max_agents": 2, "required_capabilities": ["rag"]})
        roles = _request(base, "/roles")
        messages = _request(base, f"/rooms/{room_id}/messages")
        events = _request(base, f"/rooms/{room_id}/events")
        assert first["created"] is True
        assert replay["created"] is False
        assert first["message"]["message_id"] == replay["message"]["message_id"]
        assert plan["mode"] == "delegate"
        assert len(roles["items"]) >= 3
        assert len(messages["items"]) == 1
        message_events = [item for item in events["items"] if item["event_type"] == "message_saved"]
        assert len(message_events) == 1
        print(f"smoke pass: room={room_id}, messages={len(messages['items'])}, events={len(events['items'])}, message_saved={len(message_events)}, roles={len(roles['items'])}, plan={plan['mode']}")
        return 0
    except Exception:
        startup_log.seek(0)
        print(startup_log.read().decode("utf-8", errors="replace")[-6000:], file=sys.stderr)
        raise
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        temporary.cleanup()
        startup_log.close()


if __name__ == "__main__":
    raise SystemExit(main())
