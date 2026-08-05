from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
import inspect
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
from uuid import uuid4

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_gateway import (  # noqa: E402
    CircuitBreaker,
    GatewayBadRequestError,
    GatewayCancelledError,
    GatewayChunk,
    GatewayConnectionError,
    GatewayIdentityError,
    GatewayOOMError,
    GatewayQueueFullError,
    GatewayRequestContext,
    GatewayResponse,
    GatewayServerError,
    GatewayStreamInterruptedError,
    GatewayTimeoutError,
    LocalModelGateway,
    ModelPurpose,
)


CONTRACT_VERSION = "v1.6-service-reliability-gate-v1"
MODEL_ID = "localrag-qwen3-4b-e6.1"
REQUIRED_CASE_IDS = (
    "local-success-nonstream",
    "local-success-stream",
    "connection-retry-fallback",
    "timeout-before-token-fallback",
    "queue-full-fallback",
    "server-error-fallback",
    "oom-fallback-not-ready",
    "bad-request-no-fallback",
    "identity-mismatch-no-fallback",
    "cancel-no-fallback",
    "stream-error-after-token-no-fallback",
    "circuit-open-half-open-recovery",
)

RELIABILITY_CASES = tuple(
    {"id": case_id}
    for case_id in REQUIRED_CASE_IDS
)
_FALLBACK_CASES = {
    "connection-retry-fallback": ("connection", 2, 3, "complete"),
    "timeout-before-token-fallback": ("timeout", 1, 1, "stream"),
    "queue-full-fallback": ("queuefull", 1, 2, "complete"),
    "server-error-fallback": ("server", 1, 2, "complete"),
    "oom-fallback-not-ready": ("oom", 1, 2, "complete"),
}
_NO_FALLBACK_ERRORS = {
    "bad-request-no-fallback": "badrequest",
    "identity-mismatch-no-fallback": "identity",
    "cancel-no-fallback": "cancelled",
}
_SENSITIVE_KEYS = {
    "answer",
    "api_key",
    "api_token",
    "authorization",
    "content",
    "messages",
    "prompt",
    "secret",
}


@dataclass
class _Fixture:
    gateway: LocalModelGateway
    events: list[dict[str, object]]
    fallback: Callable[[], GatewayResponse]
    fallback_stream: Callable[[], Any]
    clock: list[float]
    ready: list[bool]


class _ScenarioStream:
    def __init__(self, values: Sequence[object]) -> None:
        self._values = list(values)
        self.closed = False

    def __iter__(self) -> _ScenarioStream:
        return self

    def __next__(self) -> GatewayChunk:
        if self.closed:
            raise StopIteration
        if not self._values:
            self.closed = True
            raise StopIteration
        value = self._values.pop(0)
        if isinstance(value, BaseException):
            self.closed = True
            raise value
        return value

    def close(self) -> None:
        self.closed = True


class _ScenarioPrimary:
    model = MODEL_ID

    def __init__(
        self,
        *,
        complete_values: Sequence[object] = (),
        stream_value: object | None = None,
        events: list[dict[str, object]],
        ready: list[bool],
    ) -> None:
        self._complete_values = list(complete_values)
        self._stream_value = stream_value
        self._events = events
        self._ready = ready
        self.complete_calls = 0
        self.stream_calls = 0

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def ready(self) -> dict[str, str]:
        return {"status": "ready" if self._ready[0] else "not_ready"}

    def complete(self, messages, *, context, **kwargs):
        del messages, kwargs
        self.complete_calls += 1
        self._events.append(
            {"event": "primary_call", "operation": "complete", "attempt": self.complete_calls}
        )
        if not self._complete_values:
            raise RuntimeError("fixture exhausted")
        value = self._complete_values.pop(0)
        if isinstance(value, GatewayOOMError):
            self._ready[0] = False
        if isinstance(value, BaseException):
            raise value
        if not isinstance(value, GatewayResponse):
            raise TypeError("fixture response is invalid")
        return value

    def stream(self, messages, *, context):
        del messages, context
        self.stream_calls += 1
        self._events.append(
            {"event": "primary_call", "operation": "stream", "attempt": self.stream_calls}
        )
        if isinstance(self._stream_value, BaseException):
            raise self._stream_value
        if not isinstance(self._stream_value, _ScenarioStream):
            raise TypeError("fixture stream is invalid")
        return self._stream_value


def _response(model: str, request_id: str, *, text: str = "fixture") -> GatewayResponse:
    from model_gateway import GatewayUsage

    return GatewayResponse(
        text=text,
        model=model,
        usage=GatewayUsage(12 if model == MODEL_ID else 8, 4, 16 if model == MODEL_ID else 12),
        request_id=request_id,
        backend="llama.cpp" if model == MODEL_ID else "cloud",
        quantization="Q4_K_M" if model == MODEL_ID else "none",
        ttft_seconds=0.2,
        latency_seconds=0.8,
    )


def _context(request_id: str = "reliability-request") -> GatewayRequestContext:
    return GatewayRequestContext(request_id, ModelPurpose.RAG_GENERATION)


def _fixture(case_id: str) -> _Fixture:
    events: list[dict[str, object]] = []
    ready = [True]
    clock = [0.0]
    request_id = f"reliability-{case_id}"
    local = _response(MODEL_ID, request_id)
    cloud = _response("cloud-model", request_id, text="fallback")

    complete_values: list[object] = []
    stream_value: object | None = None
    if case_id == "local-success-nonstream":
        complete_values = [local]
    elif case_id == "local-success-stream":
        stream_value = _ScenarioStream(
            [GatewayChunk("fixture", request_id, MODEL_ID, "stop")]
        )
    elif case_id == "connection-retry-fallback":
        complete_values = [
            GatewayConnectionError("connection", request_id=request_id),
            GatewayConnectionError("connection", request_id=request_id),
        ]
    elif case_id == "timeout-before-token-fallback":
        stream_value = GatewayTimeoutError("timeout", request_id=request_id)
    elif case_id == "queue-full-fallback":
        complete_values = [GatewayQueueFullError("queue", request_id=request_id)]
    elif case_id == "server-error-fallback":
        complete_values = [GatewayServerError("server", request_id=request_id)]
    elif case_id == "oom-fallback-not-ready":
        complete_values = [GatewayOOMError("oom", request_id=request_id)]
    elif case_id == "bad-request-no-fallback":
        complete_values = [GatewayBadRequestError("bad", request_id=request_id)]
    elif case_id == "identity-mismatch-no-fallback":
        complete_values = [GatewayIdentityError("identity", request_id=request_id)]
    elif case_id == "cancel-no-fallback":
        complete_values = [GatewayCancelledError("cancelled", request_id=request_id)]
    elif case_id == "stream-error-after-token-no-fallback":
        stream_value = _ScenarioStream(
            [
                GatewayChunk("fixture", request_id, MODEL_ID),
                GatewayStreamInterruptedError(
                    "stream interrupted",
                    request_id=request_id,
                    started=True,
                ),
            ]
        )
    elif case_id == "circuit-open-half-open-recovery":
        complete_values = [
            GatewayQueueFullError("queue", request_id=request_id),
            local,
        ]
    else:
        raise ValueError(f"unknown reliability case: {case_id}")

    primary = _ScenarioPrimary(
        complete_values=complete_values,
        stream_value=stream_value,
        events=events,
        ready=ready,
    )

    def fallback() -> GatewayResponse:
        events.append({"event": "fallback_call", "operation": "complete"})
        return cloud

    def fallback_stream() -> _ScenarioStream:
        events.append({"event": "fallback_call", "operation": "stream"})
        return _ScenarioStream([GatewayChunk("fallback", request_id, "cloud-model", "stop")])

    if case_id == "circuit-open-half-open-recovery":
        breaker = CircuitBreaker(
            failure_threshold=1,
            reset_seconds=30,
            clock=lambda: clock[0],
            transition_sink=lambda previous, current: events.append(
                {
                    "event": "circuit_transition",
                    "from_state": previous.value,
                    "to_state": current.value,
                }
            ),
        )
    else:
        breaker = CircuitBreaker(
            transition_sink=lambda previous, current: events.append(
                {
                    "event": "circuit_transition",
                    "from_state": previous.value,
                    "to_state": current.value,
                }
            )
        )
    return _Fixture(
        gateway=LocalModelGateway(primary, breaker=breaker),
        events=events,
        fallback=fallback,
        fallback_stream=fallback_stream,
        clock=clock,
        ready=ready,
    )


def _deterministic_gateway_factory(case: Mapping[str, object]) -> _Fixture:
    return _fixture(str(case.get("id", "")))


_deterministic_gateway_factory.evaluation_mode = "deterministic"


def _factory_result(factory: Callable[..., object], case: Mapping[str, object]) -> _Fixture:
    try:
        parameters = inspect.signature(factory).parameters.values()
    except (TypeError, ValueError):
        return factory(case)  # type: ignore[return-value]
    accepts_case = any(
        parameter.kind
        in {parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD, parameter.VAR_POSITIONAL}
        for parameter in parameters
    )
    result = factory(case) if accepts_case else factory()
    if isinstance(result, _Fixture):
        return result
    if isinstance(result, Mapping) and isinstance(result.get("gateway"), LocalModelGateway):
        return _Fixture(
            gateway=result["gateway"],
            events=result.get("events", []),
            fallback=result.get("fallback", lambda: _response("cloud-model", "external")),
            fallback_stream=result.get(
                "fallback_stream",
                lambda: iter([GatewayChunk("fallback", "external", "cloud-model", "stop")]),
            ),
            clock=[0.0],
            ready=[True],
        )
    if isinstance(result, LocalModelGateway):
        return _Fixture(
            gateway=result,
            events=[],
            fallback=lambda: _response("cloud-model", "external"),
            fallback_stream=lambda: iter(
                [GatewayChunk("fallback", "external", "cloud-model", "stop")]
            ),
            clock=[0.0],
            ready=[True],
        )
    raise TypeError("gateway_factory must return a LocalModelGateway or fixture")


def _record_route(events: list[dict[str, object]], gateway: LocalModelGateway) -> None:
    route = gateway.snapshot().last_route
    if isinstance(route, Mapping):
        events.append({"event": "route", **dict(route)})


def _record_result(
    events: list[dict[str, object]],
    result: object,
    *,
    operation: str,
) -> None:
    events.append(
        {
            "event": "result",
            "operation": operation,
            "status": "success",
            "actual_model": getattr(result, "actual_model", ""),
            "fallback_used": getattr(result, "fallback_used", False),
            "fallback_reason": getattr(result, "fallback_reason", ""),
            "attempt_count": getattr(result, "attempt_count", None),
            "stream_started": getattr(result, "started", False),
        }
    )


def _record_error(
    events: list[dict[str, object]],
    error: Exception,
    *,
    operation: str,
    stream_started: bool = False,
) -> None:
    error_code = (
        error.__class__.__name__.removeprefix("Gateway").removesuffix("Error").lower()
    )
    events.append(
        {
            "event": "error",
            "operation": operation,
            "error_code": error_code,
            "started": bool(getattr(error, "started", False)),
            "stream_started": stream_started,
        }
    )


def _run_stream(fixture: _Fixture, case_id: str) -> None:
    request_id = f"reliability-{case_id}"
    try:
        routed = fixture.gateway.stream(
            [{"role": "user", "content": "private prompt"}],
            context=_context(request_id),
            fallback=fixture.fallback_stream,
        )
        started = False
        chunks = 0
        try:
            for chunk in routed:
                chunks += 1
                started = started or bool(chunk.text)
                fixture.events.append(
                    {
                        "event": "stream_chunk",
                        "has_text": bool(chunk.text),
                        "model": chunk.model,
                        "started": started,
                    }
                )
        except Exception as exc:
            _record_error(
                fixture.events,
                exc,
                operation="stream",
                stream_started=started,
            )
        else:
            fixture.events.append(
                {
                    "event": "result",
                    "operation": "stream",
                    "status": "success",
                    "actual_model": routed.actual_model,
                    "fallback_used": routed.fallback_used,
                    "fallback_reason": routed.fallback_reason,
                    "attempt_count": routed.attempt_count,
                    "stream_started": started,
                    "chunk_count": chunks,
                }
            )
        finally:
            routed.close()
    except Exception as exc:
        _record_error(fixture.events, exc, operation="stream")


def _run_complete(fixture: _Fixture, case_id: str) -> None:
    request_id = f"reliability-{case_id}"
    try:
        result = fixture.gateway.complete(
            [{"role": "user", "content": "private prompt"}],
            context=_context(request_id),
            fallback=fixture.fallback,
        )
    except Exception as exc:
        _record_error(fixture.events, exc, operation="complete")
    else:
        _record_result(fixture.events, result, operation="complete")


def _run_circuit(fixture: _Fixture, case_id: str) -> None:
    request_id = f"reliability-{case_id}"
    for phase in ("initial_failure", "circuit_open", "recovery"):
        if phase == "circuit_open":
            fixture.clock[0] = 0.0
        elif phase == "recovery":
            fixture.clock[0] = 30.0
        try:
            result = fixture.gateway.complete(
                [{"role": "user", "content": "private prompt"}],
                context=_context(f"{request_id}-{phase}"),
                fallback=fixture.fallback,
            )
        except Exception as exc:
            _record_error(fixture.events, exc, operation="complete")
        else:
            _record_result(fixture.events, result, operation="complete")
        snapshot = fixture.gateway.snapshot()
        fixture.events.append(
            {
                "event": "circuit_snapshot",
                "phase": phase,
                "state": snapshot.circuit.state.value,
            }
        )


def run_reliability_case(
    case: Mapping[str, object],
    gateway_factory: Callable[..., object],
) -> dict[str, object]:
    if not isinstance(case, Mapping):
        raise TypeError("case must be a mapping")
    case_id = case.get("id")
    if not isinstance(case_id, str):
        raise TypeError("case id must be a string")
    if case_id not in REQUIRED_CASE_IDS:
        raise ValueError("unknown reliability case")
    if not callable(gateway_factory):
        raise TypeError("gateway_factory must be callable")
    try:
        fixture = _factory_result(gateway_factory, case)
        if case_id == "circuit-open-half-open-recovery":
            _run_circuit(fixture, case_id)
        elif case_id in {
            "local-success-stream",
            "timeout-before-token-fallback",
            "stream-error-after-token-no-fallback",
        }:
            _run_stream(fixture, case_id)
        else:
            _run_complete(fixture, case_id)
        _record_route(fixture.events, fixture.gateway)
        if case_id == "oom-fallback-not-ready":
            fixture.events.append(
                {"event": "readiness", "ready": fixture.ready[0]}
            )
    except Exception as exc:
        if "fixture" in locals():
            events = fixture.events
        else:
            events = []
        _record_error(events, exc, operation="runner")
        events.append({"event": "unhandled_exception", "error_type": type(exc).__name__})
    return {"case_id": case_id, "events": events if "events" in locals() else fixture.events}


def _contains_sensitive_data(value: object) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if any(token in str(key).lower() for token in _SENSITIVE_KEYS):
                return True
            if _contains_sensitive_data(item):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_contains_sensitive_data(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return any(token in lowered for token in ("private prompt", "private answer", "bearer "))
    return False


def _case_checks(case_id: str, events: Sequence[object]) -> dict[str, bool]:
    clean_events = [event for event in events if isinstance(event, Mapping)]
    result_events = [event for event in clean_events if event.get("event") == "result"]
    error_events = [event for event in clean_events if event.get("event") == "error"]
    route_events = [event for event in clean_events if event.get("event") == "route"]
    route = route_events[-1] if route_events else {}
    primary_calls = sum(event.get("event") == "primary_call" for event in clean_events)
    fallback_calls = sum(event.get("event") == "fallback_call" for event in clean_events)
    sensitive = _contains_sensitive_data(events)
    unhandled = any(event.get("event") == "unhandled_exception" for event in clean_events)

    checks = {
        "result_contract": False,
        "retry_contract": False,
        "fallback_contract": False,
        "circuit_contract": True,
        "stream_boundary_contract": True,
        "readiness_contract": True,
        "log_redaction": not sensitive,
        "no_unhandled_exception": not unhandled,
    }
    if case_id == "local-success-nonstream":
        result = result_events[-1] if result_events else {}
        checks["result_contract"] = (
            result.get("status") == "success"
            and result.get("actual_model") == MODEL_ID
            and result.get("fallback_used") is False
            and route.get("actual_model") == MODEL_ID
            and route.get("fallback_used") is False
        )
        checks["retry_contract"] = primary_calls == 1 and result.get("attempt_count") == 1
        checks["fallback_contract"] = fallback_calls == 0
    elif case_id == "local-success-stream":
        result = result_events[-1] if result_events else {}
        checks["result_contract"] = (
            result.get("status") == "success"
            and result.get("actual_model") == MODEL_ID
            and result.get("fallback_used") is False
        )
        checks["retry_contract"] = primary_calls == 1 and result.get("attempt_count") == 1
        checks["fallback_contract"] = fallback_calls == 0
        checks["stream_boundary_contract"] = (
            result.get("stream_started") is True
            and result.get("fallback_used") is False
        )
    elif case_id in _FALLBACK_CASES:
        reason, expected_primary, expected_attempts, operation = _FALLBACK_CASES[case_id]
        result = result_events[-1] if result_events else {}
        route_contract = operation == "stream" or (
            route.get("actual_model") == "cloud-model"
            and route.get("fallback_reason") == reason
        )
        checks["result_contract"] = (
            result.get("status") == "success"
            and result.get("operation") == operation
            and result.get("actual_model") == "cloud-model"
            and result.get("fallback_used") is True
            and result.get("fallback_reason") == reason
            and route_contract
        )
        checks["retry_contract"] = (
            primary_calls == expected_primary
            and result.get("attempt_count") == expected_attempts
        )
        checks["fallback_contract"] = (
            fallback_calls == 1
            and bool(result.get("fallback_reason"))
        )
        if case_id == "oom-fallback-not-ready":
            readiness = [event for event in clean_events if event.get("event") == "readiness"]
            checks["readiness_contract"] = bool(readiness) and readiness[-1].get("ready") is False
        if case_id == "timeout-before-token-fallback":
            chunks = [event for event in clean_events if event.get("event") == "stream_chunk"]
            checks["stream_boundary_contract"] = (
                bool(chunks)
                and all(chunk.get("model") == "cloud-model" for chunk in chunks)
                and result.get("stream_started") is True
            )
    elif case_id in _NO_FALLBACK_ERRORS:
        error = error_events[-1] if error_events else {}
        checks["result_contract"] = (
            error.get("error_code") == _NO_FALLBACK_ERRORS[case_id]
            and error.get("started") is False
            and route.get("status") == "error"
            and route.get("fallback_used") is False
        )
        checks["retry_contract"] = primary_calls == 1
        checks["fallback_contract"] = fallback_calls == 0 and not result_events
    elif case_id == "stream-error-after-token-no-fallback":
        error = error_events[-1] if error_events else {}
        chunks = [event for event in clean_events if event.get("event") == "stream_chunk"]
        checks["result_contract"] = (
            error.get("error_code") == "streaminterrupted"
            and error.get("started") is True
        )
        checks["retry_contract"] = primary_calls == 1
        checks["fallback_contract"] = fallback_calls == 0
        checks["stream_boundary_contract"] = (
            bool(chunks)
            and chunks[0].get("started") is True
            and error.get("stream_started") is True
            and not result_events
        )
    elif case_id == "circuit-open-half-open-recovery":
        outcomes = result_events
        states = [
            event.get("state")
            for event in clean_events
            if event.get("event") == "circuit_snapshot"
        ]
        checks["result_contract"] = (
            len(outcomes) == 3
            and outcomes[0].get("actual_model") == "cloud-model"
            and outcomes[0].get("fallback_reason") == "queuefull"
            and outcomes[1].get("fallback_reason") == "circuit_open"
            and outcomes[2].get("actual_model") == MODEL_ID
            and outcomes[2].get("fallback_used") is False
            and route.get("actual_model") == MODEL_ID
            and route.get("fallback_used") is False
        )
        checks["retry_contract"] = primary_calls == 2 and fallback_calls == 2
        checks["fallback_contract"] = (
            outcomes[0].get("fallback_used") is True
            and outcomes[1].get("fallback_used") is True
            and bool(outcomes[0].get("fallback_reason"))
            and bool(outcomes[1].get("fallback_reason"))
        )
        checks["circuit_contract"] = states == ["open", "open", "closed"] and any(
            event.get("event") == "circuit_transition"
            and event.get("to_state") == "half_open"
            for event in clean_events
        )
    return checks


def summarize_reliability(
    rows: Sequence[object],
    *,
    contract_errors: Sequence[str] = (),
) -> dict[str, object]:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise TypeError("rows must be a sequence")
    expected = list(REQUIRED_CASE_IDS)
    row_ids = [
        row.get("case_id")
        for row in rows
        if isinstance(row, Mapping)
    ]
    coverage = row_ids == expected
    case_results = []
    for row in rows:
        if not isinstance(row, Mapping):
            case_results.append({"case_id": "", "case_pass": False, "checks": {}})
            continue
        case_id = str(row.get("case_id") or "")
        events = row.get("events", [])
        checks = _case_checks(case_id, events if isinstance(events, Sequence) else [])
        case_results.append(
            {
                "case_id": case_id,
                "case_pass": all(checks.values()),
                "checks": checks,
            }
        )

    check_names = (
        "retry_contract",
        "fallback_contract",
        "circuit_contract",
        "stream_boundary_contract",
        "readiness_contract",
        "log_redaction",
        "no_unhandled_exception",
    )
    gate_checks = {
        "case_coverage": coverage,
        "case_outcomes": bool(case_results) and all(
            result["case_pass"] for result in case_results
        )
        and coverage,
        **{
            name: bool(case_results)
            and all(result["checks"].get(name) is True for result in case_results)
            and coverage
            for name in check_names
        },
        "mode_contract": not contract_errors,
    }
    return {
        "contract_version": CONTRACT_VERSION,
        "expected_case_count": len(expected),
        "case_count": len(rows),
        "passed_case_count": sum(
            result["case_pass"] for result in case_results
        ),
        "case_results": case_results,
        "gate_checks": gate_checks,
        "contract_errors": list(contract_errors),
        "gate_pass": all(gate_checks.values()),
    }


def _git_identity() -> tuple[str, bool]:
    try:
        revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown", True
    return revision, dirty


def run_reliability_eval(out_dir: Path, mode: str) -> dict[str, object]:
    if mode not in {"deterministic", "formal"}:
        raise ValueError("mode must be deterministic or formal")
    contract_errors = []
    if mode == "formal":
        contract_errors.append("formal mode requires a live serving fixture")
    rows = [
        run_reliability_case(case, _deterministic_gateway_factory)
        for case in RELIABILITY_CASES
    ]
    summary = summarize_reliability(rows, contract_errors=contract_errors)
    run_id = f"service-reliability-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"
    run_dir = Path(out_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    revision, dirty = _git_identity()
    manifest = {
        "contract_version": CONTRACT_VERSION,
        "pipeline": "service_reliability_eval",
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "git_revision": revision,
        "git_dirty": dirty,
        "expected_case_ids": list(REQUIRED_CASE_IDS),
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "events.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return {
        "run_dir": run_dir,
        "manifest": manifest,
        "events": rows,
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LocalRAG service reliability gate.")
    parser.add_argument("--mode", choices=("deterministic", "formal"), default="deterministic")
    parser.add_argument("--out-dir", type=Path, default=Path("results/service_reliability"))
    args = parser.parse_args()
    result = run_reliability_eval(args.out_dir, args.mode)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
