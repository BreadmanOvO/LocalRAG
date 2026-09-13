"""Export the deterministic v1.8 OpenAPI schema for the frontend client."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "frontend" / "openapi.json"
sys.path.insert(0, str(ROOT))


def _runtime_python() -> Path:
    candidates: list[Path] = []
    candidates.append(Path(sys.executable))
    configured = os.environ.get("LOCALRAG_PYTHON")
    if configured:
        candidates.append(Path(configured))
    candidates.append(ROOT / ".venv" / "Scripts" / "python.exe")
    candidates.append(ROOT / ".venv" / "bin" / "python")
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


if __name__ == "__main__":
    try:
        runtime_python = _runtime_python()
    except RuntimeError as exc:
        if TARGET.exists():
            print(f"warning: {exc}; keeping existing {TARGET.relative_to(ROOT)}")
            raise SystemExit(0)
        raise
    if runtime_python.resolve() != Path(sys.executable).resolve():
        os.execv(str(runtime_python), [str(runtime_python), *sys.argv])

from agent_platform.api import create_app


def main() -> None:
    schema = create_app().openapi()
    TARGET.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
