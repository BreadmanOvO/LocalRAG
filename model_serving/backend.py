from __future__ import annotations

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
import hashlib
import json
from typing import Any, Protocol


@dataclass(frozen=True)
class BackendMessage:
    role: str
    content: str = ""
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: tuple[Mapping[str, Any], ...] = ()


@dataclass(frozen=True)
class GenerationRequest:
    request_id: str
    model: str
    messages: tuple[BackendMessage, ...]
    temperature: float
    max_tokens: int
    purpose: str
    tools: tuple[Mapping[str, Any], ...] = ()
    tool_choice: str | Mapping[str, Any] | None = None


@dataclass(frozen=True)
class GenerationChunk:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str | None = None


@dataclass(frozen=True)
class BackendIdentity:
    model_id: str
    backend: str
    quantization: str
    manifest_sha256: str


@dataclass(frozen=True)
class BackendReadiness:
    ready: bool
    warmed_up: bool
    oom_latched: bool
    detail: str = ""


class GenerationHandle(Protocol):
    def __iter__(self) -> Iterator[GenerationChunk]: ...

    def cancel(self) -> None: ...


class GenerationBackend(Protocol):
    @property
    def identity(self) -> BackendIdentity: ...

    def warmup(self) -> None: ...

    def readiness(self) -> BackendReadiness: ...

    def start(self, request: GenerationRequest) -> GenerationHandle: ...


class BackendError(RuntimeError):
    pass


class BackendConnectionError(BackendError):
    pass


class BackendTimeoutError(BackendError):
    pass


class BackendOutOfMemoryError(BackendError):
    pass


class BackendIdentityError(BackendError):
    pass


class BackendRequestError(BackendError):
    pass


class BackendGenerationError(BackendError):
    def __init__(self, message: str, *, started: bool) -> None:
        super().__init__(message)
        self.started = bool(started)


def manifest_fingerprint(payload: Mapping[str, object]) -> str:
    if not isinstance(payload, Mapping):
        raise TypeError("manifest payload must be a mapping")
    encoded = json.dumps(
        dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
