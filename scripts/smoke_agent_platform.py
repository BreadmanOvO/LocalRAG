"""Run a local end-to-end smoke check for the v1.8 demo contract.

This deliberately exercises the API and does not call a model provider. The
legacy Streamlit app remains the real RAG execution path until the Runtime
worker integration is completed.
"""
from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


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


def _request(base: str, path: str, *, method: str = "GET", payload: dict | None = None, headers: dict[str, str] | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(base + path, data=body, method=method, headers={"Content-Type": "application/json", **(headers or {})})
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    runtime_python = _runtime_python()
    process = subprocess.Popen(
        [str(runtime_python), "-m", "uvicorn", "agent_platform.api.app:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            try:
                if _request(base, "/health")["status"] == "ok":
                    break
            except (URLError, OSError):
                time.sleep(0.2)
        else:
            raise RuntimeError("agent platform did not become ready")

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
        assert len(events["items"]) == 1
        assert events["items"][0]["event_type"] == "message_saved"
        print(f"smoke pass: room={room_id}, messages={len(messages['items'])}, events={len(events['items'])}, roles={len(roles['items'])}, plan={plan['mode']}")
        return 0
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
