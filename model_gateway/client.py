from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Iterator, Mapping, Sequence
import time
from typing import Any
from uuid import uuid4

import httpx

from .models import (
    GatewayBadRequestError,
    GatewayChunk,
    GatewayConnectionError,
    GatewayError,
    GatewayIdentityError,
    GatewayOOMError,
    GatewayQueueFullError,
    GatewayRequestContext,
    GatewayResponse,
    GatewayResponseValidationError,
    GatewayServerError,
    GatewayStreamInterruptedError,
    GatewayTimeoutError,
    GatewayUsage,
)


def _noop_trace(_: Mapping[str, object]) -> None:
    return None


def _usage(value: object) -> GatewayUsage:
    if not isinstance(value, Mapping):
        raise GatewayResponseValidationError("gateway usage is invalid")
    try:
        prompt_tokens = value["prompt_tokens"]
        completion_tokens = value["completion_tokens"]
        total_tokens = value["total_tokens"]
    except KeyError as exc:
        raise GatewayResponseValidationError("gateway usage is incomplete") from exc
    if any(type(item) is not int or item < 0 for item in (prompt_tokens, completion_tokens, total_tokens)):
        raise GatewayResponseValidationError("gateway usage is invalid")
    return GatewayUsage(prompt_tokens, completion_tokens, total_tokens)


def _header_float(headers: httpx.Headers, name: str) -> float | None:
    value = headers.get(name)
    if value is None:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) and parsed >= 0 else None


class GatewayStream(Iterator[GatewayChunk]):
    def __init__(
        self,
        response: httpx.Response,
        *,
        request_id: str,
        model: str,
        backend: str,
        quantization: str,
        trace: Callable[[Mapping[str, object]], None],
        trace_context: Mapping[str, object],
    ) -> None:
        self._response = response
        self.request_id = request_id
        self.model = model
        self.backend = backend
        self.quantization = quantization
        self._trace_sink = trace
        self._trace_context = dict(trace_context)
        self._lines = response.iter_lines()
        self.started = False
        self.closed = False
        self.queue_seconds = _header_float(response.headers, "X-Queue-Wait-Seconds")

    def __iter__(self) -> GatewayStream:
        return self

    def __next__(self) -> GatewayChunk:
        if self.closed:
            raise StopIteration
        try:
            for line in self._lines:
                if not line or not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    self.close()
                    raise StopIteration
                try:
                    value = json.loads(payload)
                except json.JSONDecodeError as exc:
                    self.close()
                    raise GatewayResponseValidationError(
                        "gateway stream JSON is invalid",
                        request_id=self.request_id,
                        started=self.started,
                    ) from exc
                chunk = self._parse_chunk(value)
                if chunk is not None:
                    return chunk
            self.close()
            raise StopIteration
        except GatewayError:
            raise
        except (httpx.ReadError, httpx.RemoteProtocolError) as exc:
            self.close()
            raise GatewayStreamInterruptedError(
                "gateway stream was interrupted",
                request_id=self.request_id,
                started=self.started,
            ) from exc

    def _parse_chunk(self, value: object) -> GatewayChunk | None:
        if not isinstance(value, Mapping):
            raise GatewayResponseValidationError(
                "gateway stream event is invalid",
                request_id=self.request_id,
                started=self.started,
            )
        model = value.get("model")
        if model is not None and model != self.model:
            self.close()
            raise GatewayIdentityError(
                "gateway model identity does not match",
                request_id=self.request_id,
                started=self.started,
            )
        choices = value.get("choices")
        if not isinstance(choices, list) or not choices:
            raise GatewayResponseValidationError(
                "gateway stream choices are invalid",
                request_id=self.request_id,
                started=self.started,
            )
        choice = choices[0]
        if not isinstance(choice, Mapping):
            raise GatewayResponseValidationError("gateway stream choice is invalid")
        delta = choice.get("delta", {})
        if not isinstance(delta, Mapping):
            raise GatewayResponseValidationError("gateway stream delta is invalid")
        text = delta.get("content", "")
        finish_reason = choice.get("finish_reason")
        if not isinstance(text, str) or finish_reason is not None and not isinstance(finish_reason, str):
            raise GatewayResponseValidationError("gateway stream content is invalid")
        usage = None
        if "usage" in value:
            usage = _usage(value["usage"])
        if not text and finish_reason is None and usage is None:
            return None
        if text:
            self.started = True
        return GatewayChunk(
            text=text,
            request_id=self.request_id,
            model=self.model,
            finish_reason=finish_reason,
            usage=usage,
        )

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        self._response.close()
        self._trace_sink(
            {
                **self._trace_context,
                "event": "model_gateway_stream_closed",
                "request_id": self.request_id,
                "started": self.started,
            }
        )

    def __enter__(self) -> GatewayStream:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class OpenAICompatibleClient:
    def __init__(
        self,
        base_url: str,
        *,
        model: str,
        api_token: str,
        connect_timeout_seconds: float = 2.0,
        read_timeout_seconds: float = 120.0,
        http_client: httpx.Client | None = None,
        trace_sink: Callable[[Mapping[str, object]], None] | None = None,
    ) -> None:
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url must not be blank")
        if not isinstance(model, str) or not model.strip():
            raise ValueError("model must not be blank")
        if not isinstance(api_token, str) or not api_token.strip():
            raise ValueError("api_token must not be blank")
        for name, value in (
            ("connect_timeout_seconds", connect_timeout_seconds),
            ("read_timeout_seconds", read_timeout_seconds),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError(f"{name} must be positive and finite")
        self.base_url = base_url.rstrip("/")
        self._root_url = (
            self.base_url[:-3]
            if self.base_url.endswith("/v1")
            else self.base_url
        ).rstrip("/")
        self.model = model.strip()
        self._trace_sink = trace_sink or _noop_trace
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            timeout=httpx.Timeout(
                read_timeout_seconds,
                connect=connect_timeout_seconds,
            )
        )
        self._headers = {
            "Authorization": f"Bearer {api_token.strip()}",
            "Accept": "application/json",
        }

    def complete(
        self,
        messages: Sequence[Mapping[str, str]],
        *,
        context: GatewayRequestContext,
        temperature: float = 0.0,
        max_tokens: int = 256,
    ) -> GatewayResponse:
        started_at = time.monotonic()
        payload = self._payload(messages, context, temperature, max_tokens, stream=False)
        prompt_hash, prompt_length = self._prompt_fingerprint(payload["messages"])
        trace_context = self._trace_context(context, prompt_hash, prompt_length)
        try:
            response = self._client.post(
                f"{self.base_url}/chat/completions",
                headers={**self._headers, "X-Request-ID": context.request_id},
                json=payload,
            )
        except httpx.TimeoutException as exc:
            self._trace_error(trace_context, "timeout")
            raise GatewayTimeoutError("local model request timed out", request_id=context.request_id) from exc
        except httpx.RequestError as exc:
            self._trace_error(trace_context, "connection")
            raise GatewayConnectionError("local model connection failed", request_id=context.request_id) from exc
        try:
            if response.status_code != 200:
                self._raise_http_error(response, context.request_id)
            try:
                value = response.json()
            except ValueError as exc:
                raise GatewayResponseValidationError(
                    "gateway response JSON is invalid",
                    request_id=context.request_id,
                ) from exc
            result = self._parse_response(
                value,
                response.headers,
                request_id=context.request_id,
                started_at=started_at,
            )
            self._trace_sink(
                {
                    **trace_context,
                    "event": "model_gateway_request",
                    "status": "success",
                    "usage": {
                        "prompt_tokens": result.usage.prompt_tokens,
                        "completion_tokens": result.usage.completion_tokens,
                        "total_tokens": result.usage.total_tokens,
                    },
                    "latency_seconds": result.latency_seconds,
                }
            )
            return result
        except GatewayError as exc:
            self._trace_error(trace_context, _error_code(exc), error=exc)
            raise
        finally:
            response.close()

    def stream(
        self,
        messages: Sequence[Mapping[str, str]],
        *,
        context: GatewayRequestContext,
        temperature: float = 0.0,
        max_tokens: int = 256,
    ) -> GatewayStream:
        payload = self._payload(messages, context, temperature, max_tokens, stream=True)
        prompt_hash, prompt_length = self._prompt_fingerprint(payload["messages"])
        trace_context = self._trace_context(context, prompt_hash, prompt_length)
        request = self._client.build_request(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={**self._headers, "X-Request-ID": context.request_id},
            json=payload,
        )
        try:
            response = self._client.send(request, stream=True)
        except httpx.TimeoutException as exc:
            self._trace_error(trace_context, "timeout")
            raise GatewayTimeoutError("local model stream timed out", request_id=context.request_id) from exc
        except httpx.RequestError as exc:
            self._trace_error(trace_context, "connection")
            raise GatewayConnectionError("local model stream connection failed", request_id=context.request_id) from exc
        try:
            if response.status_code != 200:
                self._raise_http_error(response, context.request_id)
            return GatewayStream(
                response,
                request_id=context.request_id,
                model=self.model,
                backend=response.headers.get("X-Backend", "unknown"),
                quantization=response.headers.get("X-Quantization", "unknown"),
                trace=self._trace_sink,
                trace_context=trace_context,
            )
        except GatewayError as exc:
            response.close()
            self._trace_error(trace_context, _error_code(exc), error=exc)
            raise

    def health(self) -> dict[str, Any]:
        return self._get_json("/health")

    def ready(self) -> dict[str, Any]:
        return self._get_json("/ready")

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _payload(
        self,
        messages: Sequence[Mapping[str, str]],
        context: GatewayRequestContext,
        temperature: float,
        max_tokens: int,
        *,
        stream: bool,
    ) -> dict[str, Any]:
        if not isinstance(messages, Sequence) or isinstance(messages, (str, bytes)) or not messages:
            raise ValueError("messages must be a non-empty sequence")
        normalized_messages = []
        for message in messages:
            if not isinstance(message, Mapping):
                raise ValueError("message must be an object")
            role = message.get("role")
            content = message.get("content")
            if role not in {"system", "user", "assistant"} or not isinstance(content, str) or not content:
                raise ValueError("message role or content is invalid")
            normalized_messages.append({"role": role, "content": content})
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)) or not math.isfinite(temperature) or not 0 <= temperature <= 2:
            raise ValueError("temperature is invalid")
        if type(max_tokens) is not int or max_tokens <= 0:
            raise ValueError("max_tokens is invalid")
        metadata = {
            key: value
            for key, value in {
                "session_id": context.session_id,
                "task_id": context.task_id,
                "run_id": context.run_id,
            }.items()
            if value
        }
        return {
            "model": self.model,
            "messages": normalized_messages,
            "temperature": float(temperature),
            "max_tokens": max_tokens,
            "stream": stream,
            "purpose": context.purpose.value,
            "metadata": metadata,
        }

    @staticmethod
    def _prompt_fingerprint(messages: Sequence[Mapping[str, str]]) -> tuple[str, int]:
        serialized = json.dumps(list(messages), ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest(), len(serialized)

    @staticmethod
    def _trace_context(
        context: GatewayRequestContext,
        prompt_hash: str,
        prompt_length: int,
    ) -> dict[str, object]:
        return {
            "request_id": context.request_id,
            "purpose": context.purpose.value,
            "session_id": context.session_id,
            "task_id": context.task_id,
            "run_id": context.run_id,
            "prompt_sha256": prompt_hash,
            "prompt_length": prompt_length,
        }

    def _parse_response(
        self,
        value: object,
        headers: httpx.Headers,
        *,
        request_id: str,
        started_at: float,
    ) -> GatewayResponse:
        if not isinstance(value, Mapping):
            raise GatewayResponseValidationError("gateway response is invalid", request_id=request_id)
        if value.get("model") != self.model:
            raise GatewayIdentityError("gateway model identity does not match", request_id=request_id)
        choices = value.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], Mapping):
            raise GatewayResponseValidationError("gateway choices are invalid", request_id=request_id)
        message = choices[0].get("message")
        if not isinstance(message, Mapping) or not isinstance(message.get("content"), str):
            raise GatewayResponseValidationError("gateway message is invalid", request_id=request_id)
        response_request_id = headers.get("X-Request-ID", request_id)
        if not response_request_id:
            raise GatewayResponseValidationError("gateway request ID is invalid", request_id=request_id)
        return GatewayResponse(
            text=message["content"],
            model=self.model,
            usage=_usage(value.get("usage")),
            request_id=response_request_id,
            backend=headers.get("X-Backend", "unknown"),
            quantization=headers.get("X-Quantization", "unknown"),
            queue_seconds=_header_float(headers, "X-Queue-Wait-Seconds"),
            ttft_seconds=_header_float(headers, "X-TTFT-Seconds"),
            latency_seconds=max(0.0, time.monotonic() - started_at),
        )

    def _get_json(self, path: str) -> dict[str, Any]:
        request_id = uuid4().hex
        try:
            response = self._client.get(
                f"{self._root_url}{path}",
                headers={**self._headers, "X-Request-ID": request_id},
            )
        except httpx.TimeoutException as exc:
            raise GatewayTimeoutError("local model request timed out", request_id=request_id) from exc
        except httpx.RequestError as exc:
            raise GatewayConnectionError("local model connection failed", request_id=request_id) from exc
        try:
            if response.status_code != 200:
                self._raise_http_error(response, request_id)
            value = response.json()
            if not isinstance(value, dict):
                raise GatewayResponseValidationError("gateway status response is invalid", request_id=request_id)
            return value
        except ValueError as exc:
            raise GatewayResponseValidationError("gateway status response is invalid", request_id=request_id) from exc
        finally:
            response.close()

    def _raise_http_error(self, response: httpx.Response, request_id: str) -> None:
        error_code = ""
        try:
            value = response.json()
            if isinstance(value, Mapping) and isinstance(value.get("error"), Mapping):
                error_code = str(value["error"].get("code", ""))
        except ValueError:
            pass
        if response.status_code == 400:
            raise GatewayBadRequestError(
                "local model rejected the request",
                request_id=request_id,
                status_code=response.status_code,
            )
        if response.status_code == 401:
            raise GatewayIdentityError(
                "local model authorization failed",
                request_id=request_id,
                status_code=response.status_code,
            )
        if response.status_code == 429:
            raise GatewayQueueFullError(
                "local model queue is unavailable",
                request_id=request_id,
                status_code=response.status_code,
            )
        if error_code in {"oom", "backend_out_of_memory"}:
            raise GatewayOOMError(
                "local model ran out of memory",
                request_id=request_id,
                status_code=response.status_code,
            )
        if response.status_code == 504:
            raise GatewayTimeoutError(
                "local model request timed out",
                request_id=request_id,
                status_code=response.status_code,
            )
        if response.status_code >= 500:
            raise GatewayServerError(
                "local model server failed",
                request_id=request_id,
                status_code=response.status_code,
            )
        raise GatewayResponseValidationError(
            "local model response status is invalid",
            request_id=request_id,
            status_code=response.status_code,
        )

    def _trace_error(
        self,
        context: Mapping[str, object],
        error_code: str,
        *,
        error: GatewayError | None = None,
    ) -> None:
        self._trace_sink(
            {
                **context,
                "event": "model_gateway_request",
                "status": "error",
                "error_code": error_code,
                "started": error.started if error is not None else False,
            }
        )


def _error_code(error: GatewayError) -> str:
    return error.__class__.__name__.removeprefix("Gateway").removesuffix("Error").lower()
