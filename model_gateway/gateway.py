from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass

from .circuit_breaker import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitPermit,
    CircuitSnapshot,
)
from .client import OpenAICompatibleClient
from .metrics import GatewayMetrics
from .models import (
    GatewayChunk,
    GatewayError,
    GatewayRequestContext,
    GatewayResponse,
    GatewayResponseValidationError,
    GatewayUsage,
)


FallbackResponse = Callable[[], GatewayResponse]
FallbackStream = Callable[[], Iterator[GatewayChunk]]


@dataclass(frozen=True)
class RoutedResponse:
    text: str
    model: str
    usage: GatewayUsage
    request_id: str
    backend: str
    quantization: str
    primary_model: str
    actual_model: str
    fallback_used: bool
    fallback_reason: str
    attempt_count: int
    queue_seconds: float | None = None
    ttft_seconds: float | None = None
    latency_seconds: float | None = None


@dataclass(frozen=True)
class GatewaySnapshot:
    circuit: CircuitSnapshot
    primary_model: str
    available: bool = True
    health: str = "unknown"
    ready: str = "unknown"
    last_route: Mapping[str, object] | None = None


class GatewayFallbackError(GatewayError):
    fallback_allowed = False

    def __init__(
        self,
        *,
        primary_error: GatewayError,
        fallback_error: Exception,
        request_id: str,
    ) -> None:
        super().__init__(
            "local model and fallback both failed",
            request_id=request_id,
            started=primary_error.started,
        )
        self.primary_error = primary_error
        self.fallback_error = fallback_error


class RoutedStream(Iterator[GatewayChunk]):
    def __init__(
        self,
        active: Iterator[GatewayChunk],
        *,
        primary: Iterator[GatewayChunk] | None,
        permit: CircuitPermit | None,
        breaker: CircuitBreaker,
        fallback: FallbackStream | None,
        primary_model: str,
        request_id: str,
        context: GatewayRequestContext,
        metrics: GatewayMetrics,
        fallback_used: bool = False,
        fallback_reason: str = "",
        attempt_count: int = 1,
    ) -> None:
        self._active = active
        self._primary = primary
        self._permit = permit
        self._breaker = breaker
        self._fallback = fallback
        self._primary_model = primary_model
        self.request_id = request_id
        self.context = context
        self._metrics = metrics
        self.fallback_used = fallback_used
        self.fallback_reason = fallback_reason
        self.attempt_count = attempt_count
        self.started = False
        self.closed = False
        self.actual_model = primary_model if not fallback_used else "unknown"
        self._metric_recorded = False
        self._stream_error = False

    def __iter__(self) -> RoutedStream:
        return self

    def __next__(self) -> GatewayChunk:
        if self.closed:
            raise StopIteration
        try:
            chunk = next(self._active)
        except StopIteration:
            if not self.fallback_used and self._permit is not None:
                self._breaker.record_success(self._permit)
            self.close()
            raise
        except GatewayError as error:
            if self.fallback_used or self.started or not error.fallback_allowed:
                self._breaker.release(self._permit)
                self._stream_error = True
                self.close()
                if self.started:
                    self._metrics.record_stream_interruption(
                        purpose=self.context.purpose.value
                    )
                raise
            if self._permit is not None:
                self._breaker.record_failure(self._permit, error)
            self._switch_to_fallback(error)
            return next(self)
        if chunk.text:
            self.started = True
        self.actual_model = chunk.model
        return chunk

    def _switch_to_fallback(self, primary_error: GatewayError) -> None:
        if self._fallback is None:
            self.close()
            raise primary_error
        self._close_iterator(self._active)
        try:
            candidate = self._fallback()
            if not isinstance(candidate, Iterator):
                candidate = iter(candidate)
        except Exception as exc:
            self.close()
            raise GatewayFallbackError(
                primary_error=primary_error,
                fallback_error=exc,
                request_id=self.request_id,
            ) from exc
        self._active = candidate
        self._primary = None
        self.fallback_used = True
        self.fallback_reason = _error_code(primary_error)
        self.attempt_count += 1
        self.actual_model = "unknown"
        self._metrics.record_fallback(
            purpose=self.context.purpose.value,
            reason=self.fallback_reason,
        )

    @staticmethod
    def _close_iterator(iterator: object) -> None:
        close = getattr(iterator, "close", None)
        if callable(close):
            close()

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        self._close_iterator(self._active)
        self._breaker.release(self._permit)
        if not self._metric_recorded:
            self._metric_recorded = True
            status = "error" if self._stream_error else (
                "fallback" if self.fallback_used else "success"
            )
            self._metrics.record_request(
                purpose=self.context.purpose.value,
                status=status,
                fallback_reason=self.fallback_reason,
                actual_model=self.actual_model,
            )

    def __enter__(self) -> RoutedStream:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class LocalModelGateway:
    def __init__(
        self,
        primary: OpenAICompatibleClient,
        *,
        breaker: CircuitBreaker | None = None,
        metrics: GatewayMetrics | None = None,
    ) -> None:
        self.primary = primary
        self.metrics = metrics or GatewayMetrics()
        self.breaker = breaker or CircuitBreaker(
            transition_sink=lambda previous, current: self.metrics.record_circuit_transition(
                from_state=previous.value,
                to_state=current.value,
            )
        )
        self._last_route: Mapping[str, object] | None = None

    def complete(
        self,
        messages: Sequence[Mapping[str, str]],
        *,
        context: GatewayRequestContext,
        fallback: FallbackResponse,
        response_validator: Callable[[str], object] | None = None,
        temperature: float = 0.0,
        max_tokens: int = 256,
    ) -> RoutedResponse:
        permit: CircuitPermit | None = None
        try:
            permit = self.breaker.before_request()
        except CircuitOpenError:
            return self._fallback_response(
                messages,
                context=context,
                fallback=fallback,
                primary_error=GatewayError(
                    "local model circuit is open",
                    request_id=context.request_id,
                ),
                reason="circuit_open",
                attempt_count=0,
            )
        assert permit is not None

        attempts = 0
        while True:
            attempts += 1
            try:
                response = self.primary.complete(
                    messages,
                    context=context,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                _validate_response(response, response_validator)
                self.breaker.record_success(permit)
                return self._local_response(response, context, attempts)
            except GatewayError as error:
                if error.started or not error.fallback_allowed:
                    self.breaker.record_failure(permit, error)
                    self._record_route(context, "error", response=None)
                    raise
                if error.retryable and attempts == 1:
                    continue
                self.breaker.record_failure(permit, error)
                return self._fallback_response(
                    messages,
                    context=context,
                    fallback=fallback,
                    primary_error=error,
                    reason=_error_code(error),
                    attempt_count=attempts,
                )

    def stream(
        self,
        messages: Sequence[Mapping[str, str]],
        *,
        context: GatewayRequestContext,
        fallback: FallbackStream,
    ) -> RoutedStream:
        permit: CircuitPermit | None = None
        try:
            permit = self.breaker.before_request()
        except CircuitOpenError:
            candidate = self._open_fallback_stream(
                fallback,
                context=context,
                primary_error=GatewayError(
                    "local model circuit is open",
                    request_id=context.request_id,
                ),
            )
            self.metrics.record_fallback(
                purpose=context.purpose.value,
                reason="circuit_open",
            )
            return RoutedStream(
                candidate,
                primary=None,
                permit=None,
                breaker=self.breaker,
                fallback=None,
                primary_model=self.primary.model,
                request_id=context.request_id,
                context=context,
                metrics=self.metrics,
                fallback_used=True,
                fallback_reason="circuit_open",
                attempt_count=0,
            )
        assert permit is not None
        try:
            primary_stream = self.primary.stream(messages, context=context)
        except GatewayError as error:
            if error.started or not error.fallback_allowed:
                self.breaker.record_failure(permit, error)
                raise
            self.breaker.record_failure(permit, error)
            candidate = self._open_fallback_stream(
                fallback,
                context=context,
                primary_error=error,
            )
            self.metrics.record_fallback(
                purpose=context.purpose.value,
                reason=_error_code(error),
            )
            return RoutedStream(
                candidate,
                primary=None,
                permit=None,
                breaker=self.breaker,
                fallback=None,
                primary_model=self.primary.model,
                request_id=context.request_id,
                context=context,
                metrics=self.metrics,
                fallback_used=True,
                fallback_reason=_error_code(error),
                attempt_count=1,
            )
        return RoutedStream(
            primary_stream,
            primary=primary_stream,
            permit=permit,
            breaker=self.breaker,
            fallback=fallback,
            primary_model=self.primary.model,
            request_id=context.request_id,
            context=context,
            metrics=self.metrics,
        )

    def snapshot(self) -> GatewaySnapshot:
        return GatewaySnapshot(
            circuit=self.breaker.snapshot(),
            primary_model=self.primary.model,
            last_route=self._last_route,
        )

    def _local_response(
        self,
        response: GatewayResponse,
        context: GatewayRequestContext,
        attempts: int,
    ) -> RoutedResponse:
        route = RoutedResponse(
            text=response.text,
            model=response.model,
            usage=response.usage,
            request_id=response.request_id,
            backend=response.backend,
            quantization=response.quantization,
            primary_model=self.primary.model,
            actual_model=response.model,
            fallback_used=False,
            fallback_reason="",
            attempt_count=attempts,
            queue_seconds=response.queue_seconds,
            ttft_seconds=response.ttft_seconds,
            latency_seconds=response.latency_seconds,
        )
        self._record_route(context, "success", response=route)
        return route

    def _fallback_response(
        self,
        messages: Sequence[Mapping[str, str]],
        *,
        context: GatewayRequestContext,
        fallback: FallbackResponse,
        primary_error: GatewayError,
        reason: str,
        attempt_count: int,
    ) -> RoutedResponse:
        del messages
        try:
            response = fallback()
            if not isinstance(response, GatewayResponse):
                raise TypeError("fallback must return GatewayResponse")
        except Exception as exc:
            self._record_route(context, "error", response=None)
            raise GatewayFallbackError(
                primary_error=primary_error,
                fallback_error=exc,
                request_id=context.request_id,
            ) from exc
        route = RoutedResponse(
            text=response.text,
            model=response.model,
            usage=response.usage,
            request_id=response.request_id,
            backend=response.backend,
            quantization=response.quantization,
            primary_model=self.primary.model,
            actual_model=response.model,
            fallback_used=True,
            fallback_reason=reason,
            attempt_count=attempt_count + 1,
            queue_seconds=response.queue_seconds,
            ttft_seconds=response.ttft_seconds,
            latency_seconds=response.latency_seconds,
        )
        self.metrics.record_fallback(
            purpose=context.purpose.value,
            reason=reason,
        )
        self._record_route(context, "fallback", response=route)
        return route

    def _open_fallback_stream(
        self,
        fallback: FallbackStream,
        *,
        context: GatewayRequestContext,
        primary_error: GatewayError,
    ) -> Iterator[GatewayChunk]:
        try:
            candidate = fallback()
            return iter(candidate)
        except Exception as exc:
            raise GatewayFallbackError(
                primary_error=primary_error,
                fallback_error=exc,
                request_id=context.request_id,
            ) from exc

    def _record_route(
        self,
        context: GatewayRequestContext,
        status: str,
        *,
        response: RoutedResponse | None,
    ) -> None:
        self._last_route = {
            "request_id": context.request_id,
            "purpose": context.purpose.value,
            "status": status,
            "actual_model": response.actual_model if response else "unknown",
            "backend": response.backend if response else "unknown",
            "quantization": response.quantization if response else "unknown",
            "fallback_used": response.fallback_used if response else False,
            "fallback_reason": response.fallback_reason if response else "",
        }
        self.metrics.record_request(
            purpose=context.purpose.value,
            status=status,
            fallback_reason=response.fallback_reason if response else "",
            actual_model=response.actual_model if response else "unknown",
            backend=response.backend if response else "unknown",
            quantization=response.quantization if response else "unknown",
        )


def _validate_response(
    response: GatewayResponse,
    validator: Callable[[str], object] | None,
) -> None:
    if validator is None:
        return
    try:
        result = validator(response.text)
    except Exception as exc:
        raise GatewayResponseValidationError(
            "local model response validation failed",
            request_id=response.request_id,
        ) from exc
    if result is False:
        raise GatewayResponseValidationError(
            "local model response validation failed",
            request_id=response.request_id,
        )


def _error_code(error: GatewayError) -> str:
    return error.__class__.__name__.removeprefix("Gateway").removesuffix("Error").lower()
