#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from typing import Any


NESTED_REPO_NAME = "RAG_md"


def discover_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


REPO_ROOT = discover_repo_root()

REWRITE_EXACT = {
    Path("TODO.md"),
    Path("docs/references.md"),
    Path("docs/resume_notes.md"),
    Path("docs/roadmap.md"),
    Path("docs/source_intake_plan.md"),
}
EXCLUDED_EXACT = {
    Path("README.md"),
    Path("docs/evaluation.md"),
    Path("docs/repo_guide.md"),
}
REWRITE_PREFIXES = (Path("docs/superpowers"),)
EXCLUDED_PREFIXES = (Path("results"),)


def _normalize(path: Path) -> Path:
    normalized_parts: list[str] = []
    for part in path.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if normalized_parts and normalized_parts[-1] != "..":
                normalized_parts.pop()
            else:
                normalized_parts.append(part)
            continue
        normalized_parts.append(part)
    return Path(*normalized_parts)


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def should_rewrite(relative_path: Path) -> bool:
    relative_path = _normalize(relative_path)
    if relative_path in EXCLUDED_EXACT:
        return False
    if any(relative_path == prefix or _is_relative_to(relative_path, prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    if relative_path in REWRITE_EXACT:
        return True
    return any(relative_path == prefix or _is_relative_to(relative_path, prefix) for prefix in REWRITE_PREFIXES)


def rewrite_target_path(target_path: Path, repo_root: Path = REPO_ROOT) -> Path:
    target_path = Path(target_path)
    repo_root = Path(repo_root)
    nested_repo = repo_root / NESTED_REPO_NAME

    try:
        relative_path = _normalize(target_path.relative_to(repo_root))
    except ValueError:
        return target_path

    if _is_relative_to(relative_path, Path(NESTED_REPO_NAME)):
        return repo_root / relative_path
    if not should_rewrite(relative_path):
        return repo_root / relative_path
    if not nested_repo.is_dir():
        raise FileNotFoundError(f"Expected nested docs repo at {nested_repo}")
    return nested_repo / relative_path


def build_updated_input(tool_input: dict[str, Any], repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    key = "file_path"
    if key not in tool_input:
        return tool_input

    updated_input = dict(tool_input)
    updated_input[key] = str(rewrite_target_path(Path(tool_input[key]), repo_root=repo_root))
    return updated_input


def main() -> int:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input", {})

    try:
        updated_input = build_updated_input(tool_input)
    except FileNotFoundError as exc:
        response = {
            "continue": False,
            "stopReason": str(exc),
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": str(exc),
            },
        }
    else:
        response = {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "updatedInput": updated_input,
            },
        }

    json.dump(response, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
