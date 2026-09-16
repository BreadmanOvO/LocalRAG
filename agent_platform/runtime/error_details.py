"""Safe, user-facing serialization for model/runtime failures.

The event log is durable and may be shown in the UI.  Keep this payload
actionable without leaking credentials, prompts, or a provider stack trace.
"""

from __future__ import annotations

import re
from typing import Any


_SECRET_RE = re.compile(r"(?i)(?:sk-[a-z0-9_-]{8,}|kira_[a-z0-9_-]{8,}|ms-[a-z0-9-]{8,})")


def _status_code(exc: BaseException) -> int | None:
    value = getattr(exc, "status_code", None)
    if value is None:
        response = getattr(exc, "response", None)
        value = getattr(response, "status_code", None)
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _safe_message(exc: BaseException) -> str:
    text = _SECRET_RE.sub("[已脱敏凭据]", str(exc or "").strip())
    text = re.sub(r"\s+", " ", text)
    return text[:360] or "运行时未返回具体错误信息"


def _classification(exc: BaseException, status_code: int | None) -> tuple[str, bool, str]:
    name = type(exc).__name__
    if name in {"RateLimitError"} or status_code == 429:
        return "model_rate_limited", True, "检查模型额度与并发限制，稍后重试或切换模型。"
    if name in {"AuthenticationError"} or status_code in {401, 403}:
        return "model_auth_failed", False, "检查 API Key、模型权限和供应商地址。"
    if status_code == 404:
        return "model_not_found", False, "检查模型名称与 API endpoint 是否匹配。"
    if name in {"APITimeoutError", "TimeoutError"} or status_code == 408:
        return "model_timeout", True, "模型响应超时，可稍后恢复任务或切换更快的模型。"
    if name in {"CircuitOpenError"}:
        return "model_circuit_open", True, "模型连续失败已触发熔断，等待冷却后再恢复任务。"
    if name in {"APIConnectionError", "ConnectionError"} or status_code in {502, 503, 504}:
        return "model_provider_unavailable", True, "模型供应商暂时不可用，检查服务状态后重试。"
    if name in {"ModelRoutingError"}:
        return "model_routing_failed", False, "检查模型设置，启用至少一个满足该 Agent 能力要求的模型。"
    if name in {"ControlConflictError", "RoomLeaseBusy"}:
        return "execution_control_conflict", True, "任务状态已变化，请刷新任务后恢复或重新执行。"
    if name in {"RuntimeError"} and "empty response" in str(exc).lower():
        return "empty_model_response", True, "模型返回空结果，可恢复任务或切换模型。"
    retryable = status_code in {500, 502, 503, 504}
    return "model_request_failed", retryable, "查看技术详情；必要时检查模型配置、额度和供应商状态。"


def serialize_exception(
    exc: BaseException,
    *,
    phase: str = "runtime",
    agent_id: str | None = None,
    agent_name: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    retry_count: int | None = None,
) -> dict[str, Any]:
    status_code = _status_code(exc)
    error_code, retryable, suggestion = _classification(exc, status_code)
    payload: dict[str, Any] = {
        "error_code": error_code,
        "error_type": type(exc).__name__,
        "error_message": _safe_message(exc),
        "phase": phase,
        "retryable": retryable,
        "suggestion": suggestion,
    }
    if status_code is not None:
        payload["status_code"] = status_code
    for key, value in (("agent_id", agent_id), ("agent_name", agent_name), ("provider", provider), ("model", model)):
        if value:
            payload[key] = value
    if retry_count is not None:
        payload["retry_count"] = retry_count
    return payload
