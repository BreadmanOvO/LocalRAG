"""Shared, safe failure contract for Agent tools."""
from __future__ import annotations

import logging
import re

from langchain_core.tools import ToolException

ERROR_CODE_PATTERN = re.compile(r"^\[error_code=([a-z0-9_]+)\]\s*")


class ToolFailure(ToolException):
    def __init__(self, error_code: str, safe_message: str) -> None:
        self.error_code = error_code
        super().__init__(safe_message)


def classify_tool_error(exc: Exception, *, default_code: str) -> str:
    if isinstance(exc, TimeoutError):
        return "tool_timeout"
    if isinstance(exc, ConnectionError):
        return "tool_unavailable"
    if isinstance(exc, PermissionError):
        return "tool_forbidden"
    if isinstance(exc, (TypeError, ValueError)):
        return "tool_invalid_input"
    return default_code


def build_tool_failure(
    operation: str,
    exc: Exception,
    *,
    default_code: str,
    logger: logging.Logger,
) -> ToolFailure:
    logger.exception("Tool failed during %s", operation)
    error_code = classify_tool_error(exc, default_code=default_code)
    return ToolFailure(error_code, f"{operation}失败，请检查输入或稍后重试。")


def render_tool_error(exc: ToolException) -> str:
    if isinstance(exc, ToolFailure):
        return f"[error_code={exc.error_code}] {exc}"
    return "[error_code=tool_execution_failed] 工具执行失败，请稍后重试。"


def render_tool_validation_error(_exc: Exception) -> str:
    return "[error_code=tool_invalid_input] 工具参数无效，请检查输入后重试。"


def extract_tool_error_code(content: object) -> str:
    if not isinstance(content, str):
        return ""
    match = ERROR_CODE_PATTERN.match(content.strip())
    return match.group(1) if match else ""
