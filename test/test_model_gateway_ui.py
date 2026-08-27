from __future__ import annotations

from dataclasses import fields
from pathlib import Path
import unittest

from agent.research.presentation import ModelGatewayView, build_model_gateway_view
from model_gateway import (
    CircuitSnapshot,
    CircuitState,
    GatewayConnectionError,
    GatewayRequestContext,
    GatewayResponse,
    GatewayServerError,
    GatewaySnapshot,
    GatewayUsage,
    LocalModelGateway,
    ModelPurpose,
)


ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "localrag-qwen3-4b-e6.1"


def _circuit(state: CircuitState = CircuitState.CLOSED) -> CircuitSnapshot:
    return CircuitSnapshot(
        state=state,
        failure_count=0,
        probe_in_flight=False,
        opened_at=None,
    )


def _snapshot(**overrides) -> GatewaySnapshot:
    values = {
        "circuit": _circuit(),
        "primary_model": MODEL_ID,
        "available": True,
        "health": "ok",
        "ready": "ready",
        "last_route": None,
    }
    values.update(overrides)
    return GatewaySnapshot(**values)


class ProbePrimary:
    model = MODEL_ID

    def __init__(self, *, health=None, ready=None, response=None):
        self.health_result = {"status": "ok"} if health is None else health
        self.ready_result = {"status": "ready"} if ready is None else ready
        self.response = response

    @staticmethod
    def _resolve(value):
        if isinstance(value, BaseException):
            raise value
        return value

    def health(self):
        return self._resolve(self.health_result)

    def ready(self):
        return self._resolve(self.ready_result)

    def complete(self, messages, *, context, **kwargs):
        del messages, context, kwargs
        return self.response


class ModelGatewayViewTests(unittest.TestCase):
    def test_no_request_has_fixed_safe_empty_fields(self):
        view = build_model_gateway_view(_snapshot(), None)

        self.assertEqual(set(ModelGatewayView.__required_keys__), set(view))
        self.assertEqual(
            {
                "available": True,
                "health": "ok",
                "ready": "ready",
                "configuration_status": "not_configured",
                "profile": "",
                "backend": "",
                "quantization": "",
                "circuit_state": "closed",
                "primary_model": MODEL_ID,
                "actual_model": "",
                "fallback_reason": "",
                "request_id": "",
                "ttft_seconds": None,
                "latency_seconds": None,
                "input_tokens": None,
                "output_tokens": None,
            },
            view,
        )

    def test_route_maps_profile_fallback_timing_and_usage(self):
        route = {
            "request_id": "req-001",
            "primary_model": MODEL_ID,
            "actual_model": "cloud-chat",
            "backend": "llama.cpp",
            "quantization": "Q4_K_M",
            "fallback_reason": "queuefull",
            "ttft_seconds": 0.25,
            "latency_seconds": 1.5,
            "input_tokens": 120,
            "output_tokens": 30,
        }

        view = build_model_gateway_view(_snapshot(last_route=route), route)

        self.assertEqual("e6_1_q4_k_m", view["profile"])
        self.assertEqual("cloud-chat", view["actual_model"])
        self.assertEqual("queuefull", view["fallback_reason"])
        self.assertEqual(0.25, view["ttft_seconds"])
        self.assertEqual(1.5, view["latency_seconds"])
        self.assertEqual(120, view["input_tokens"])
        self.assertEqual(30, view["output_tokens"])

    def test_non_scalar_route_values_never_render_object_repr(self):
        private = object()
        route = {field: private for field in (
            "profile",
            "backend",
            "quantization",
            "primary_model",
            "actual_model",
            "fallback_reason",
            "request_id",
            "ttft_seconds",
            "latency_seconds",
            "input_tokens",
            "output_tokens",
        )}

        view = build_model_gateway_view(_snapshot(), route)

        self.assertNotIn("object at", repr(view))
        self.assertEqual(MODEL_ID, view["primary_model"])
        self.assertEqual("", view["actual_model"])
        self.assertIsNone(view["latency_seconds"])
        self.assertIsNone(view["input_tokens"])

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(TypeError):
            build_model_gateway_view(object(), None)
        with self.assertRaises(TypeError):
            build_model_gateway_view(None, object())

    def test_app_route_panel_is_read_only_and_omits_content_fields(self):
        source = (ROOT / "app_qa.py").read_text(encoding="utf-8")
        start = source.index("def _render_model_gateway(")
        end = source.index("\ndef ", start + 1)
        render_source = source[start:end]

        self.assertIn('st.expander("模型路由"', render_source)
        self.assertNotIn(".button(", render_source)
        self.assertNotIn("api_token", render_source)
        self.assertNotIn("prompt", render_source)
        self.assertNotIn("answer", render_source)
        self.assertIn("disabled_by_route", render_source)
        self.assertIn("Planner 和摘要分别记录自己的路由", render_source)
        self.assertIn('f"model_route_{role}"', source)
        self.assertIn("for role in MODEL_ROLES", source)
        self.assertIn('list(MODEL_ROUTE_MODES)', source)
        self.assertIn('model_routes=selected_model_routes', source)
        self.assertIn('update_model_routes(selected_model_routes)', source)


class ModelGatewayProbeTests(unittest.TestCase):
    def test_probe_reports_ready_service_without_changing_circuit(self):
        gateway = LocalModelGateway(ProbePrimary())

        snapshot = gateway.probe_snapshot()

        self.assertTrue(snapshot.available)
        self.assertEqual("ok", snapshot.health)
        self.assertEqual("ready", snapshot.ready)
        self.assertEqual(CircuitState.CLOSED, snapshot.circuit.state)

    def test_probe_distinguishes_not_ready_from_unavailable(self):
        not_ready = LocalModelGateway(
            ProbePrimary(
                ready=GatewayServerError("not ready", request_id="private"),
            )
        ).probe_snapshot()
        unavailable = LocalModelGateway(
            ProbePrimary(
                health=GatewayConnectionError("offline", request_id="private"),
            )
        ).probe_snapshot()

        self.assertTrue(not_ready.available)
        self.assertEqual("not_ready", not_ready.ready)
        self.assertFalse(unavailable.available)
        self.assertEqual("unavailable", unavailable.health)
        self.assertEqual("unknown", unavailable.ready)
        self.assertNotIn("private", repr(not_ready))
        self.assertNotIn("private", repr(unavailable))

    def test_completed_route_snapshot_contains_only_operational_metadata(self):
        response = GatewayResponse(
            text="private answer",
            model=MODEL_ID,
            usage=GatewayUsage(12, 4, 16),
            request_id="req-001",
            backend="transformers",
            quantization="none",
            ttft_seconds=0.2,
            latency_seconds=0.8,
        )
        gateway = LocalModelGateway(ProbePrimary(response=response))
        gateway.complete(
            [{"role": "user", "content": "private prompt"}],
            context=GatewayRequestContext(
                "req-001",
                ModelPurpose.RAG_GENERATION,
            ),
            fallback=lambda: response,
        )

        route = dict(gateway.snapshot().last_route or {})

        self.assertEqual("e6_1_adapter_bf16", route["profile"])
        self.assertEqual(MODEL_ID, route["primary_model"])
        self.assertEqual(0.2, route["ttft_seconds"])
        self.assertEqual(0.8, route["latency_seconds"])
        self.assertEqual(12, route["input_tokens"])
        self.assertEqual(4, route["output_tokens"])
        self.assertNotIn("private prompt", repr(route))
        self.assertNotIn("private answer", repr(route))
        self.assertNotIn("api_token", route)

    def test_gateway_snapshot_contract_remains_explicit(self):
        self.assertEqual(
            [
                "circuit",
                "primary_model",
                "available",
                "health",
                "ready",
                "last_route",
            ],
            [field.name for field in fields(GatewaySnapshot)],
        )


if __name__ == "__main__":
    unittest.main()
