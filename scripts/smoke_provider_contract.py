from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from langchain_core.tools import tool

from config.provider_factory import build_agent_chat_model
from config.runtime_keys import RuntimeProviderConfig, load_runtime_config


@tool
def provider_smoke_echo(text: str) -> str:
    """Return text for the provider tool-call contract smoke."""
    return text


def _failed(error: Exception) -> dict[str, Any]:
    return {"passed": False, "error_type": type(error).__name__}


def run_provider_smoke(
    runtime_config: RuntimeProviderConfig,
    *,
    model_factory: Callable[..., Any] = build_agent_chat_model,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "scope": "functional_smoke",
        "quality_evaluation": False,
        "status": "live",
        "provider": runtime_config.provider,
        "model": runtime_config.chat_model_name,
        "request": {"passed": False},
        "tool_call": {"passed": False},
        "stream": {"passed": False},
    }

    try:
        model = model_factory(runtime_config, temperature=0.0, timeout=30)
    except Exception as exc:
        report["request"] = _failed(exc)
        report["tool_call"] = _failed(exc)
        report["stream"] = _failed(exc)
        report["overall_passed"] = False
        return report

    try:
        response = model.invoke("Reply with exactly: PROVIDER_SMOKE_OK")
        content = getattr(response, "content", "")
        normalized_content = content.strip() if isinstance(content, str) else ""
        report["request"] = {
            "passed": normalized_content == "PROVIDER_SMOKE_OK",
            "response_type": type(response).__name__,
            "marker_matched": normalized_content == "PROVIDER_SMOKE_OK",
        }
    except Exception as exc:
        report["request"] = _failed(exc)

    try:
        bound_model = model.bind_tools(
            [provider_smoke_echo],
            tool_choice="provider_smoke_echo",
        )
        response = bound_model.invoke(
            "Call provider_smoke_echo with text PROVIDER_TOOL_OK."
        )
        calls = getattr(response, "tool_calls", []) or []
        tool_names = [
            str(call.get("name", "")) for call in calls if isinstance(call, dict)
        ]
        marker_matched = any(
            call.get("name") == "provider_smoke_echo"
            and isinstance(call.get("args"), dict)
            and call["args"].get("text") == "PROVIDER_TOOL_OK"
            for call in calls
            if isinstance(call, dict)
        )
        report["tool_call"] = {
            "passed": marker_matched,
            "tool_names": tool_names,
            "call_count": len(calls),
            "marker_matched": marker_matched,
        }
    except Exception as exc:
        report["tool_call"] = _failed(exc)

    try:
        chunks = list(model.stream("Reply with exactly: PROVIDER_STREAM_OK"))
        streamed_text = "".join(
            str(getattr(chunk, "content", "") or "") for chunk in chunks
        )
        marker_matched = streamed_text.strip() == "PROVIDER_STREAM_OK"
        report["stream"] = {
            "passed": bool(chunks) and marker_matched,
            "chunk_count": len(chunks),
            "marker_matched": marker_matched,
        }
    except Exception as exc:
        report["stream"] = _failed(exc)

    report["overall_passed"] = all(
        bool(report[section]["passed"])
        for section in ("request", "tool_call", "stream")
    )
    return report


def load_and_run_provider_smoke() -> dict[str, Any]:
    try:
        runtime_config = load_runtime_config()
    except Exception as exc:
        return {
            "scope": "functional_smoke",
            "quality_evaluation": False,
            "status": "contract_only",
            "overall_passed": None,
            "error_type": type(exc).__name__,
        }
    return run_provider_smoke(runtime_config)


def main() -> None:
    print(json.dumps(load_and_run_provider_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
