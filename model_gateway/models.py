from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ModelPurpose(StrEnum):
    RAG_GENERATION = "rag_generation"
    CONVERSATION_SUMMARY = "conversation_summary"


@dataclass(frozen=True)
class GatewayRequestContext:
    request_id: str
    purpose: ModelPurpose
    session_id: str = ""
    task_id: str = ""
    run_id: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id must not be blank")
        if not isinstance(self.purpose, ModelPurpose):
            raise TypeError("purpose must be a ModelPurpose")
        for field_name in ("session_id", "task_id", "run_id"):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")


@dataclass(frozen=True)
class GatewayUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def __post_init__(self) -> None:
        for field_name in ("prompt_tokens", "completion_tokens", "total_tokens"):
            value = getattr(self, field_name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{field_name} must be a non-negative int")


@dataclass(frozen=True)
class GatewayResponse:
    text: str
    model: str
    usage: GatewayUsage
    request_id: str
    backend: str
    quantization: str
    queue_seconds: float | None = None
    ttft_seconds: float | None = None
    latency_seconds: float | None = None


@dataclass(frozen=True)
class GatewayChunk:
    text: str
    request_id: str
    model: str
    finish_reason: str | None = None
    usage: GatewayUsage | None = None


class GatewayError(RuntimeError):
    retryable = False
    fallback_allowed = False
    started = False

    def __init__(
        self,
        message: str,
        *,
        request_id: str = "",
        status_code: int | None = None,
        started: bool = False,
    ) -> None:
        super().__init__(message)
        self.request_id = request_id
        self.status_code = status_code
        self.started = started


class GatewayConnectionError(GatewayError):
    retryable = True
    fallback_allowed = True


class GatewayTimeoutError(GatewayError):
    retryable = False
    fallback_allowed = True


class GatewayQueueFullError(GatewayError):
    retryable = False
    fallback_allowed = True


class GatewayServerError(GatewayError):
    retryable = False
    fallback_allowed = True


class GatewayOOMError(GatewayError):
    retryable = False
    fallback_allowed = True


class GatewayBadRequestError(GatewayError):
    retryable = False
    fallback_allowed = False


class GatewayIdentityError(GatewayError):
    retryable = False
    fallback_allowed = False


class GatewayResponseValidationError(GatewayError):
    retryable = False
    fallback_allowed = True


class GatewayCancelledError(GatewayError):
    retryable = False
    fallback_allowed = False


class GatewayStreamInterruptedError(GatewayError):
    retryable = False
    fallback_allowed = True
