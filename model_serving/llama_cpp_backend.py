from __future__ import annotations

from collections.abc import Iterator, Mapping
import json
from pathlib import Path
from threading import Event, Lock
from urllib.parse import urlparse

import httpx

from model_deployment.manifest import validate_manifest

from .backend import (
    BackendConnectionError,
    BackendGenerationError,
    BackendIdentity,
    BackendIdentityError,
    BackendMessage,
    BackendOutOfMemoryError,
    BackendReadiness,
    BackendRequestError,
    BackendTimeoutError,
    GenerationChunk,
    GenerationHandle,
    GenerationRequest,
    manifest_fingerprint,
)
from .profiles import ModelServingProfile


def _map_status(response: httpx.Response, *, started: bool) -> Exception:
    body = response.text.lower()
    if response.status_code == 400:
        return BackendRequestError("llama.cpp rejected the request")
    if response.status_code == 429:
        return BackendTimeoutError("llama.cpp queue is unavailable")
    if "out of memory" in body or "cuda error" in body:
        return BackendOutOfMemoryError("llama.cpp CUDA out of memory")
    if response.status_code >= 500:
        return BackendGenerationError("llama.cpp generation failed", started=started)
    return BackendConnectionError("llama.cpp returned an unexpected status")


class _LlamaCppGenerationHandle(GenerationHandle):
    def __init__(
        self,
        *,
        client: httpx.Client,
        payload: Mapping[str, object],
    ) -> None:
        self._client = client
        self._payload = dict(payload)
        self._cancel_event = Event()
        self._iteration_lock = Lock()
        self._iterated = False
        self._response: httpx.Response | None = None

    def cancel(self) -> None:
        self._cancel_event.set()
        response = self._response
        if response is not None:
            response.close()

    def __iter__(self) -> Iterator[GenerationChunk]:
        with self._iteration_lock:
            if self._iterated:
                raise RuntimeError("generation handle can only be iterated once")
            self._iterated = True
        yielded = False
        input_tokens = 0
        output_tokens = 0
        finish_reason: str | None = None
        try:
            with self._client.stream(
                "POST",
                "chat/completions",
                json=self._payload,
            ) as response:
                self._response = response
                if response.status_code != 200:
                    response.read()
                    raise _map_status(response, started=False)
                for line in response.iter_lines():
                    if self._cancel_event.is_set():
                        finish_reason = "cancelled"
                        break
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if not data or data == "[DONE]":
                        continue
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        raise BackendGenerationError(
                            "llama.cpp returned invalid SSE JSON",
                            started=yielded,
                        ) from None
                    if not isinstance(event, Mapping):
                        raise BackendGenerationError(
                            "llama.cpp returned an invalid event",
                            started=yielded,
                        )
                    error = event.get("error")
                    if error is not None:
                        error_text = json.dumps(error, ensure_ascii=False).lower()
                        if "out of memory" in error_text or "cuda" in error_text:
                            raise BackendOutOfMemoryError("llama.cpp CUDA out of memory")
                        raise BackendGenerationError(
                            "llama.cpp stream failed",
                            started=yielded,
                        )
                    usage = event.get("usage")
                    if isinstance(usage, Mapping):
                        prompt_value = usage.get("prompt_tokens")
                        completion_value = usage.get("completion_tokens")
                        if type(prompt_value) is int:
                            input_tokens = max(input_tokens, prompt_value)
                        if type(completion_value) is int:
                            output_tokens = max(output_tokens, completion_value)
                    choices = event.get("choices")
                    if not isinstance(choices, list) or not choices:
                        continue
                    choice = choices[0]
                    if not isinstance(choice, Mapping):
                        continue
                    delta = choice.get("delta")
                    text = delta.get("content") if isinstance(delta, Mapping) else None
                    if isinstance(text, str) and text:
                        yielded = True
                        yield GenerationChunk(text=text)
                    reason = choice.get("finish_reason")
                    if isinstance(reason, str):
                        finish_reason = reason
        except (BackendRequestError, BackendTimeoutError, BackendOutOfMemoryError):
            raise
        except BackendGenerationError:
            raise
        except httpx.TimeoutException:
            raise BackendTimeoutError("llama.cpp request timed out") from None
        except httpx.HTTPError:
            raise BackendConnectionError("llama.cpp connection failed") from None
        finally:
            self._response = None
        if self._cancel_event.is_set():
            finish_reason = "cancelled"
        if finish_reason is None:
            finish_reason = "stop"
        yield GenerationChunk(
            text="",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            finish_reason=finish_reason,
        )


class LlamaCppGenerationBackend:
    def __init__(
        self,
        *,
        profile: ModelServingProfile,
        repo_root: Path,
        expected_manifest: Mapping[str, object],
        base_url: str,
        client: httpx.Client | None = None,
    ) -> None:
        if (
            profile.backend != "llama_cpp"
            or profile.quantization != "Q4_K_M"
            or profile.artifact_path is None
            or profile.base_model_path is not None
            or profile.adapter_path is not None
        ):
            raise BackendIdentityError("profile is not the E6.1 Q4 identity")
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
            "127.0.0.1",
            "localhost",
        }:
            raise BackendIdentityError("llama.cpp base URL must be loopback-only")
        if parsed.path.rstrip("/") != "/v1" or parsed.query or parsed.fragment:
            raise BackendIdentityError("llama.cpp base URL must end with /v1")
        validate_manifest(repo_root, expected_manifest)
        metadata = expected_manifest.get("metadata")
        identity = metadata.get("model_identity") if isinstance(metadata, Mapping) else None
        if (
            not isinstance(identity, Mapping)
            or identity.get("model_id") != profile.model_id
            or identity.get("architecture") != "Qwen3ForCausalLM"
            or identity.get("context_limit") != profile.context_limit
            or identity.get("quantization") != "Q4_K_M"
            or identity.get("artifact_path") != profile.artifact_path
        ):
            raise BackendIdentityError("Q4 manifest identity does not match profile")
        self.profile = profile
        self._client = client or httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            timeout=httpx.Timeout(120.0, connect=10.0),
        )
        self._identity = BackendIdentity(
            model_id=profile.model_id,
            backend="llama_cpp",
            quantization="Q4_K_M",
            manifest_sha256=manifest_fingerprint(expected_manifest),
        )
        self._ready = False
        self._detail = "not_warmed_up"

    @property
    def identity(self) -> BackendIdentity:
        return self._identity

    def readiness(self) -> BackendReadiness:
        return BackendReadiness(
            ready=self._ready,
            warmed_up=self._ready,
            oom_latched=False,
            detail=self._detail,
        )

    def _validate_request(self, request: GenerationRequest) -> None:
        if not isinstance(request, GenerationRequest):
            raise BackendRequestError("request must be a GenerationRequest")
        if request.model != self.profile.model_id:
            raise BackendRequestError("request model does not match backend")
        if (
            type(request.max_tokens) is not int
            or request.max_tokens <= 0
            or request.max_tokens > self.profile.max_new_tokens
        ):
            raise BackendRequestError("max_tokens exceeds profile")
        if not isinstance(request.temperature, (int, float)) or not (
            0 <= request.temperature <= 2
        ):
            raise BackendRequestError("temperature is invalid")
        if request.purpose not in {"rag_generation", "conversation_summary"}:
            raise BackendRequestError("request purpose is invalid")
        if not request.messages or any(
            message.role not in {"system", "user", "assistant"}
            or not isinstance(message.content, str)
            or not message.content
            for message in request.messages
        ):
            raise BackendRequestError("messages are invalid")

    def start(self, request: GenerationRequest) -> GenerationHandle:
        self._validate_request(request)
        return _LlamaCppGenerationHandle(
            client=self._client,
            payload={
                "model": request.model,
                "messages": [
                    {"role": message.role, "content": message.content}
                    for message in request.messages
                ],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "stream": True,
                "stream_options": {"include_usage": True},
            },
        )

    def warmup(self) -> None:
        try:
            response = self._client.get("models")
        except httpx.TimeoutException:
            raise BackendTimeoutError("llama.cpp model identity timed out") from None
        except httpx.HTTPError:
            raise BackendConnectionError("llama.cpp model identity failed") from None
        if response.status_code != 200:
            raise _map_status(response, started=False)
        try:
            payload = response.json()
        except ValueError:
            raise BackendIdentityError("llama.cpp model list is invalid") from None
        rows = payload.get("data") if isinstance(payload, Mapping) else None
        model_ids = {
            row.get("id")
            for row in rows
            if isinstance(row, Mapping) and isinstance(row.get("id"), str)
        } if isinstance(rows, list) else set()
        if self.profile.model_id not in model_ids:
            raise BackendIdentityError("llama.cpp model ID does not match profile")
        for _ in self.start(
            GenerationRequest(
                request_id="warmup",
                model=self.profile.model_id,
                messages=(BackendMessage(role="user", content="ready"),),
                temperature=0.0,
                max_tokens=1,
                purpose="conversation_summary",
            )
        ):
            pass
        self._ready = True
        self._detail = "ready"
