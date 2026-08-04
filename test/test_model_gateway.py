from __future__ import annotations

import unittest

from model_gateway import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    GatewayBadRequestError,
    GatewayChunk,
    GatewayConnectionError,
    GatewayFallbackError,
    GatewayIdentityError,
    GatewayQueueFullError,
    GatewayRequestContext,
    GatewayResponse,
    GatewayStreamInterruptedError,
    GatewayUsage,
    LocalModelGateway,
    ModelPurpose,
)


def _context() -> GatewayRequestContext:
    return GatewayRequestContext("req-001", ModelPurpose.RAG_GENERATION)


def _response(model: str = "local-model", text: str = "local") -> GatewayResponse:
    return GatewayResponse(
        text=text,
        model=model,
        usage=GatewayUsage(2, 1, 3),
        request_id="req-001",
        backend="llama.cpp",
        quantization="Q4_K_M",
    )


class FakePrimary:
    model = "local-model"

    def __init__(self, *, complete_values=(), stream_value=None):
        self.complete_values = list(complete_values)
        self.stream_value = stream_value
        self.complete_calls = 0
        self.stream_calls = 0

    def complete(self, messages, *, context):
        del messages, context
        self.complete_calls += 1
        value = self.complete_values.pop(0)
        if isinstance(value, BaseException):
            raise value
        return value

    def stream(self, messages, *, context):
        del messages, context
        self.stream_calls += 1
        if isinstance(self.stream_value, BaseException):
            raise self.stream_value
        return self.stream_value


class CircuitBreakerTests(unittest.TestCase):
    def test_threshold_open_half_open_probe_and_recovery(self):
        now = [0.0]
        transitions = []
        breaker = CircuitBreaker(
            failure_threshold=3,
            reset_seconds=10,
            clock=lambda: now[0],
            transition_sink=lambda previous, current: transitions.append((previous, current)),
        )
        for _ in range(3):
            permit = breaker.before_request()
            breaker.record_failure(
                permit,
                GatewayQueueFullError("queue", request_id="req"),
            )
        self.assertEqual(CircuitState.OPEN, breaker.snapshot().state)
        with self.assertRaises(CircuitOpenError):
            breaker.before_request()
        now[0] = 10
        probe = breaker.before_request()
        with self.assertRaises(CircuitOpenError):
            breaker.before_request()
        breaker.record_success(probe)
        self.assertEqual(CircuitState.CLOSED, breaker.snapshot().state)
        self.assertEqual(
            [(CircuitState.CLOSED, CircuitState.OPEN),
             (CircuitState.OPEN, CircuitState.HALF_OPEN),
             (CircuitState.HALF_OPEN, CircuitState.CLOSED)],
            transitions,
        )

    def test_non_degradable_error_does_not_count(self):
        breaker = CircuitBreaker(failure_threshold=1)
        permit = breaker.before_request()
        breaker.record_failure(
            permit,
            GatewayBadRequestError("bad", request_id="req"),
        )
        self.assertEqual(CircuitState.CLOSED, breaker.snapshot().state)
        self.assertEqual(0, breaker.snapshot().failure_count)


class LocalModelGatewayTests(unittest.TestCase):
    def test_connection_retries_once_then_returns_local_response(self):
        primary = FakePrimary(
            complete_values=[
                GatewayConnectionError("offline", request_id="req-001"),
                _response(),
            ]
        )
        gateway = LocalModelGateway(primary)
        result = gateway.complete(
            [{"role": "user", "content": "question"}],
            context=_context(),
            fallback=lambda: _response(model="cloud", text="fallback"),
        )
        self.assertEqual("local", result.text)
        self.assertEqual(2, result.attempt_count)
        self.assertFalse(result.fallback_used)
        self.assertEqual(2, primary.complete_calls)

    def test_queue_error_falls_back_once_without_partial_text(self):
        primary = FakePrimary(
            complete_values=[GatewayQueueFullError("queue", request_id="req-001")]
        )
        gateway = LocalModelGateway(primary)
        result = gateway.complete(
            [{"role": "user", "content": "question"}],
            context=_context(),
            fallback=lambda: _response(model="cloud", text="cloud answer"),
        )
        self.assertTrue(result.fallback_used)
        self.assertEqual("queuefull", result.fallback_reason)
        self.assertEqual("cloud answer", result.text)
        self.assertEqual(2, result.attempt_count)

    def test_identity_error_does_not_fallback(self):
        primary = FakePrimary(
            complete_values=[GatewayIdentityError("identity", request_id="req-001")]
        )
        gateway = LocalModelGateway(primary)
        fallback_called = False

        def fallback():
            nonlocal fallback_called
            fallback_called = True
            return _response(model="cloud")

        with self.assertRaises(GatewayIdentityError):
            gateway.complete(
                [{"role": "user", "content": "question"}],
                context=_context(),
                fallback=fallback,
            )
        self.assertFalse(fallback_called)

    def test_response_validator_failure_falls_back_and_circuit_counts(self):
        primary = FakePrimary(complete_values=[_response(text="invalid")])
        gateway = LocalModelGateway(primary)
        result = gateway.complete(
            [{"role": "user", "content": "question"}],
            context=_context(),
            fallback=lambda: _response(model="cloud", text="valid"),
            response_validator=lambda text: text == "valid",
        )
        self.assertTrue(result.fallback_used)
        self.assertEqual("responsevalidation", result.fallback_reason)
        self.assertEqual(1, gateway.breaker.snapshot().failure_count)

    def test_open_circuit_skips_primary(self):
        primary = FakePrimary(
            complete_values=[
                GatewayQueueFullError("queue", request_id="req-001"),
                GatewayQueueFullError("queue", request_id="req-001"),
                GatewayQueueFullError("queue", request_id="req-001"),
            ]
        )
        gateway = LocalModelGateway(primary)
        for _ in range(3):
            gateway.complete(
                [{"role": "user", "content": "question"}],
                context=_context(),
                fallback=lambda: _response(model="cloud"),
            )
        result = gateway.complete(
            [{"role": "user", "content": "question"}],
            context=_context(),
            fallback=lambda: _response(model="cloud", text="open fallback"),
        )
        self.assertEqual("open fallback", result.text)
        self.assertEqual(3, primary.complete_calls)
        self.assertEqual("circuit_open", result.fallback_reason)

    def test_fallback_failure_keeps_both_errors_without_content(self):
        primary_error = GatewayQueueFullError("private primary", request_id="req-001")
        gateway = LocalModelGateway(FakePrimary(complete_values=[primary_error]))
        with self.assertRaises(GatewayFallbackError) as raised:
            gateway.complete(
                [{"role": "user", "content": "private prompt"}],
                context=_context(),
                fallback=lambda: (_ for _ in ()).throw(RuntimeError("private answer")),
            )
        self.assertIs(primary_error, raised.exception.primary_error)
        self.assertIsInstance(raised.exception.fallback_error, RuntimeError)
        self.assertNotIn("private", str(raised.exception))

    def test_stream_before_first_token_falls_back(self):
        primary = FakePrimary(
            stream_value=GatewayQueueFullError("queue", request_id="req-001")
        )
        gateway = LocalModelGateway(primary)
        def fallback():
            return iter([GatewayChunk("cloud", "req-001", "cloud", "stop")])
        routed = gateway.stream(
            [{"role": "user", "content": "question"}],
            context=_context(),
            fallback=fallback,
        )
        self.assertEqual("cloud", next(routed).text)
        with self.assertRaises(StopIteration):
            next(routed)
        self.assertTrue(routed.fallback_used)

    def test_stream_after_first_token_never_falls_back(self):
        class Interrupted:
            def __iter__(self):
                return self

            def __next__(self):
                if not hasattr(self, "sent"):
                    self.sent = True
                    return GatewayChunk("partial", "req-001", "local")
                raise GatewayStreamInterruptedError(
                    "interrupted",
                    request_id="req-001",
                    started=True,
                )

            def close(self):
                return None

        primary = FakePrimary(stream_value=Interrupted())
        gateway = LocalModelGateway(primary)
        fallback_called = False

        def fallback():
            nonlocal fallback_called
            fallback_called = True
            return iter([GatewayChunk("cloud", "req-001", "cloud")])

        routed = gateway.stream(
            [{"role": "user", "content": "question"}],
            context=_context(),
            fallback=fallback,
        )
        self.assertEqual("partial", next(routed).text)
        with self.assertRaises(GatewayStreamInterruptedError):
            next(routed)
        self.assertFalse(fallback_called)

    def test_metrics_have_fixed_labels_and_no_request_ids(self):
        gateway = LocalModelGateway(FakePrimary(complete_values=[_response()]))
        gateway.complete(
            [{"role": "user", "content": "question"}],
            context=_context(),
            fallback=lambda: _response(model="cloud"),
        )
        rendered = gateway.metrics.render_prometheus().decode("utf-8")
        self.assertIn("localrag_gateway_requests_total", rendered)
        self.assertIn("localrag_gateway_circuit_transitions_total", rendered)
        self.assertNotIn("req-001", rendered)
        self.assertNotIn("session-001", rendered)


if __name__ == "__main__":
    unittest.main()
