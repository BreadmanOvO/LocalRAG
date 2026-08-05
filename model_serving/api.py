from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
import hashlib
from itertools import chain
import json
import logging
import re
import secrets
import time
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response, StreamingResponse
from prometheus_client.exposition import CONTENT_TYPE_LATEST

from .backend import (
    BackendConnectionError,
    BackendError,
    BackendGenerationError,
    BackendIdentity,
    BackendIdentityError,
    BackendMessage,
    BackendOutOfMemoryError,
    BackendRequestError,
    BackendTimeoutError,
    GenerationBackend,
    GenerationChunk,
    GenerationHandle,
    GenerationRequest,
    manifest_fingerprint,
)
from .metrics import ServingMetrics
from .profiles import ModelServingProfile
from .queue import GenerationQueue, QueueFullError, QueueTimeoutError
from .schemas import ChatCompletionRequest


logger = logging.getLogger(__name__)
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_UNSET = object()


def _sse(payload: Mapping[str, object] | str) -> str:
    if isinstance(payload, str):
        return f"data: {payload}\n\n"
    return "data: " + json.dumps(
        dict(payload), ensure_ascii=False, separators=(",", ":")
    ) + "\n\n"


def _stream_openai_events(
    *,
    handle: GenerationHandle,
    request_id: str,
    model: str,
    iterator: Iterator[GenerationChunk] | None = None,
    first_chunk: GenerationChunk | object = _UNSET,
    on_chunk: Callable[[GenerationChunk], None] | None = None,
    on_error: Callable[[BackendError], None] | None = None,
    on_cancel: Callable[[], None] | None = None,
) -> Iterator[str]:
    stream_id = f"chatcmpl-{request_id}"
    terminated = False
    chunks = iterator if iterator is not None else iter(handle)
    try:
        yield _sse(
            {
                "id": stream_id,
                "object": "chat.completion.chunk",
                "model": model,
                "choices": [
                    {"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}
                ],
            }
        )
        pending = [] if first_chunk is _UNSET else [first_chunk]
        try:
            for chunk in chain(pending, chunks):
                if not isinstance(chunk, GenerationChunk):
                    raise BackendGenerationError("invalid generation chunk", started=True)
                if on_chunk is not None:
                    on_chunk(chunk)
                payload: dict[str, Any] = {
                    "id": stream_id,
                    "object": "chat.completion.chunk",
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": chunk.text} if chunk.text else {},
                            "finish_reason": chunk.finish_reason,
                        }
                    ],
                }
                if chunk.finish_reason is not None:
                    payload["usage"] = {
                        "prompt_tokens": chunk.input_tokens,
                        "completion_tokens": chunk.output_tokens,
                        "total_tokens": chunk.input_tokens + chunk.output_tokens,
                    }
                yield _sse(payload)
        except BackendError as exc:
            if on_error is not None:
                on_error(exc)
            error_code = (
                "backend_out_of_memory"
                if isinstance(exc, BackendOutOfMemoryError)
                else "backend_generation_error"
            )
            yield _sse(
                {
                    "error": {
                        "type": "generation_error",
                        "code": error_code,
                    }
                }
            )
        terminated = True
        yield _sse("[DONE]")
    finally:
        if not terminated:
            handle.cancel()
            if on_cancel is not None:
                on_cancel()


def _error_response(status_code: int, code: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": code.replace("_", " "),
                "type": "local_model_error",
                "code": code,
            }
        },
        headers={"X-Request-ID": request_id},
    )


def _backend_error_response(
    error: Exception,
    *,
    request_id: str,
    metrics: ServingMetrics,
    profile: ModelServingProfile,
    purpose: str,
) -> JSONResponse:
    if isinstance(error, BackendRequestError):
        return _error_response(400, "backend_request_error", request_id)
    if isinstance(error, BackendOutOfMemoryError):
        metrics.record_oom(profile, purpose)
        return _error_response(503, "backend_out_of_memory", request_id)
    if isinstance(error, BackendTimeoutError):
        return _error_response(504, "backend_timeout", request_id)
    if isinstance(error, (BackendConnectionError, BackendIdentityError)):
        return _error_response(503, "backend_unavailable", request_id)
    if isinstance(error, BackendGenerationError):
        return _error_response(503, "backend_generation_error", request_id)
    return _error_response(500, "backend_internal_error", request_id)


def _request_id(value: str | None) -> str:
    if value is None:
        return uuid4().hex
    if not _REQUEST_ID_PATTERN.fullmatch(value):
        raise ValueError("invalid request ID")
    return value


def _expected_identity(
    profile: ModelServingProfile,
    expected_manifest: Mapping[str, object],
) -> BackendIdentity:
    return BackendIdentity(
        model_id=profile.model_id,
        backend=profile.backend,
        quantization=profile.quantization,
        manifest_sha256=manifest_fingerprint(expected_manifest),
    )


def _safe_log_request(request_id: str, payload: ChatCompletionRequest) -> None:
    message_bytes = "\n".join(message.content for message in payload.messages).encode(
        "utf-8"
    )
    metadata_ids = tuple(
        value
        for value in (
            payload.metadata.session_id,
            payload.metadata.task_id,
            payload.metadata.run_id,
        )
        if value is not None
    )
    logger.info(
        "model request id=%s purpose=%s metadata_ids=%s messages=%d chars=%d sha256=%s",
        request_id,
        payload.purpose,
        metadata_ids,
        len(payload.messages),
        len(message_bytes),
        hashlib.sha256(message_bytes).hexdigest(),
    )


def create_app(
    *,
    backend: GenerationBackend,
    profile: ModelServingProfile,
    expected_manifest: Mapping[str, object],
    api_token: str | None = None,
    active_limit: int = 1,
    waiting_limit: int = 4,
    queue_timeout_seconds: float = 30.0,
    metrics: ServingMetrics | None = None,
) -> FastAPI:
    if not isinstance(profile, ModelServingProfile):
        raise TypeError("profile must be a ModelServingProfile")
    if not isinstance(expected_manifest, Mapping):
        raise TypeError("expected_manifest must be a mapping")
    if api_token is not None and (not isinstance(api_token, str) or not api_token):
        raise ValueError("api_token must be non-empty when configured")
    serving_metrics = metrics or ServingMetrics()
    expected_identity = _expected_identity(profile, expected_manifest)
    generation_queue = GenerationQueue(
        active_limit=active_limit,
        waiting_limit=waiting_limit,
        on_change=lambda snapshot: serving_metrics.set_queue(
            profile, active=snapshot.active, waiting=snapshot.waiting
        ),
    )
    serving_metrics.set_queue(profile, active=0, waiting=0)
    app = FastAPI(title="LocalRAG Model Service")
    app.state.generation_queue = generation_queue
    app.state.serving_metrics = serving_metrics

    @app.exception_handler(RequestValidationError)
    def validation_error_handler(request: Request, exc: RequestValidationError):
        return _error_response(400, "invalid_request", request.headers.get("X-Request-ID", ""))

    def authorize(authorization: str | None) -> JSONResponse | None:
        if api_token is None:
            return None
        expected = f"Bearer {api_token}"
        if authorization is None or not secrets.compare_digest(authorization, expected):
            return _error_response(401, "unauthorized", "")
        return None

    def ready_error(request_id: str) -> JSONResponse | None:
        try:
            identity = backend.identity
            readiness = backend.readiness()
        except Exception:
            return _error_response(503, "backend_unavailable", request_id)
        if identity != expected_identity:
            return _error_response(503, "backend_identity_mismatch", request_id)
        if not readiness.ready or not readiness.warmed_up or readiness.oom_latched:
            return _error_response(503, "backend_not_ready", request_id)
        return None

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready(
        authorization: str | None = Header(default=None, alias="Authorization"),
        request_id_header: str | None = Header(default=None, alias="X-Request-ID"),
    ):
        unauthorized = authorize(authorization)
        if unauthorized is not None:
            return unauthorized
        try:
            request_id = _request_id(request_id_header)
        except ValueError:
            return _error_response(400, "invalid_request_id", "")
        unavailable = ready_error(request_id)
        if unavailable is not None:
            return unavailable
        return JSONResponse(
            {"status": "ready", "model": profile.model_id},
            headers={"X-Request-ID": request_id},
        )

    @app.get("/v1/models")
    def models(
        authorization: str | None = Header(default=None, alias="Authorization"),
    ):
        unauthorized = authorize(authorization)
        if unauthorized is not None:
            return unauthorized
        return {
            "object": "list",
            "data": [
                {"id": profile.model_id, "object": "model", "owned_by": "localrag"}
            ],
        }

    @app.get("/metrics")
    def prometheus_metrics() -> Response:
        return Response(
            serving_metrics.render(),
            media_type=CONTENT_TYPE_LATEST,
        )

    @app.post("/v1/chat/completions")
    def chat_completions(
        payload: ChatCompletionRequest,
        authorization: str | None = Header(default=None, alias="Authorization"),
        request_id_header: str | None = Header(default=None, alias="X-Request-ID"),
    ):
        unauthorized = authorize(authorization)
        if unauthorized is not None:
            return unauthorized
        try:
            request_id = _request_id(request_id_header)
        except ValueError:
            return _error_response(400, "invalid_request_id", "")
        if payload.model != profile.model_id or payload.max_tokens > profile.max_new_tokens:
            return _error_response(400, "invalid_request", request_id)
        unavailable = ready_error(request_id)
        if unavailable is not None:
            return unavailable
        _safe_log_request(request_id, payload)
        generation_request = GenerationRequest(
            request_id=request_id,
            model=payload.model,
            messages=tuple(
                BackendMessage(message.role, message.content)
                for message in payload.messages
            ),
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            purpose=payload.purpose,
        )
        started_at = time.monotonic()

        try:
            lease = generation_queue.acquire(queue_timeout_seconds)
            lease.__enter__()
        except (QueueFullError, QueueTimeoutError):
            serving_metrics.record_request(
                profile,
                purpose=payload.purpose,
                status="queue_rejected",
                duration_seconds=time.monotonic() - started_at,
                ttft_seconds=None,
                input_tokens=0,
                output_tokens=0,
            )
            return _error_response(429, "queue_unavailable", request_id)
        queue_wait_seconds = time.monotonic() - started_at
        try:
            handle = backend.start(generation_request)
        except Exception as exc:
            lease.__exit__(type(exc), exc, exc.__traceback__)
            serving_metrics.record_request(
                profile,
                purpose=payload.purpose,
                status="start_error",
                duration_seconds=time.monotonic() - started_at,
                ttft_seconds=None,
                input_tokens=0,
                output_tokens=0,
            )
            return _backend_error_response(
                exc,
                request_id=request_id,
                metrics=serving_metrics,
                profile=profile,
                purpose=payload.purpose,
            )

        if not payload.stream:
            text_parts: list[str] = []
            input_tokens = 0
            output_tokens = 0
            finish_reason = "stop"
            ttft: float | None = None
            status = "success"
            try:
                for chunk in handle:
                    if ttft is None:
                        ttft = time.monotonic() - started_at
                    text_parts.append(chunk.text)
                    input_tokens = max(input_tokens, chunk.input_tokens)
                    output_tokens = max(output_tokens, chunk.output_tokens)
                    if chunk.finish_reason is not None:
                        finish_reason = chunk.finish_reason
            except Exception as exc:
                status = "generation_error"
                handle.cancel()
                return _backend_error_response(
                    exc,
                    request_id=request_id,
                    metrics=serving_metrics,
                    profile=profile,
                    purpose=payload.purpose,
                )
            finally:
                lease.__exit__(None, None, None)
                serving_metrics.record_request(
                    profile,
                    purpose=payload.purpose,
                    status=status,
                    duration_seconds=time.monotonic() - started_at,
                    ttft_seconds=ttft,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )
            return JSONResponse(
                {
                    "id": f"chatcmpl-{request_id}",
                    "object": "chat.completion",
                    "model": profile.model_id,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "".join(text_parts),
                            },
                            "finish_reason": finish_reason,
                        }
                    ],
                    "usage": {
                        "prompt_tokens": input_tokens,
                        "completion_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens,
                    },
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Queue-Wait-Seconds": f"{queue_wait_seconds:.6f}",
                    "X-TTFT-Seconds": f"{(ttft or 0.0):.6f}",
                    "X-Backend": profile.backend,
                    "X-Quantization": profile.quantization,
                },
            )

        iterator = iter(handle)
        try:
            first_chunk = next(iterator)
        except StopIteration:
            first_chunk = GenerationChunk("", 0, 0, "stop")
        except Exception as exc:
            handle.cancel()
            lease.__exit__(type(exc), exc, exc.__traceback__)
            serving_metrics.record_request(
                profile,
                purpose=payload.purpose,
                status="generation_error",
                duration_seconds=time.monotonic() - started_at,
                ttft_seconds=None,
                input_tokens=0,
                output_tokens=0,
            )
            return _backend_error_response(
                exc,
                request_id=request_id,
                metrics=serving_metrics,
                profile=profile,
                purpose=payload.purpose,
            )

        stream_state: dict[str, Any] = {
            "status": "success",
            "ttft": None,
            "input_tokens": 0,
            "output_tokens": 0,
        }

        def observe_chunk(chunk: GenerationChunk) -> None:
            if stream_state["ttft"] is None:
                stream_state["ttft"] = time.monotonic() - started_at
            stream_state["input_tokens"] = max(
                stream_state["input_tokens"], chunk.input_tokens
            )
            stream_state["output_tokens"] = max(
                stream_state["output_tokens"], chunk.output_tokens
            )

        def stream_error(error: BackendError) -> None:
            stream_state["status"] = "generation_error"
            if isinstance(error, BackendOutOfMemoryError):
                serving_metrics.record_oom(profile, payload.purpose)

        def stream_cancel() -> None:
            stream_state["status"] = "cancelled"
            serving_metrics.record_cancel(profile, payload.purpose)

        def body() -> Iterator[str]:
            try:
                yield from _stream_openai_events(
                    handle=handle,
                    request_id=request_id,
                    model=profile.model_id,
                    iterator=iterator,
                    first_chunk=first_chunk,
                    on_chunk=observe_chunk,
                    on_error=stream_error,
                    on_cancel=stream_cancel,
                )
            finally:
                lease.__exit__(None, None, None)
                serving_metrics.record_request(
                    profile,
                    purpose=payload.purpose,
                    status=stream_state["status"],
                    duration_seconds=time.monotonic() - started_at,
                    ttft_seconds=stream_state["ttft"],
                    input_tokens=stream_state["input_tokens"],
                    output_tokens=stream_state["output_tokens"],
                )

        return StreamingResponse(
            body(),
            media_type="text/event-stream",
            headers={
                "X-Request-ID": request_id,
                "X-Queue-Wait-Seconds": f"{queue_wait_seconds:.6f}",
                "X-Backend": profile.backend,
                "X-Quantization": profile.quantization,
            },
        )

    return app
