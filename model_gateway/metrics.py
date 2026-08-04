from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter
from prometheus_client.exposition import generate_latest


class GatewayMetrics:
    def __init__(self) -> None:
        self.registry = CollectorRegistry(auto_describe=True)
        self.requests = Counter(
            "localrag_gateway_requests_total",
            "Local model gateway requests.",
            (
                "purpose",
                "status",
                "fallback_reason",
                "actual_model",
                "backend",
                "quantization",
            ),
            registry=self.registry,
        )
        self.fallbacks = Counter(
            "localrag_gateway_fallback_total",
            "Local model gateway fallbacks.",
            ("purpose", "fallback_reason"),
            registry=self.registry,
        )
        self.circuit_transitions = Counter(
            "localrag_gateway_circuit_transitions_total",
            "Local model gateway circuit transitions.",
            ("from_state", "to_state"),
            registry=self.registry,
        )
        self.stream_interruptions = Counter(
            "localrag_gateway_stream_interruptions_total",
            "Local model gateway stream interruptions.",
            ("purpose",),
            registry=self.registry,
        )

    def record_request(
        self,
        *,
        purpose: str,
        status: str,
        fallback_reason: str = "",
        actual_model: str = "unknown",
        backend: str = "unknown",
        quantization: str = "unknown",
    ) -> None:
        self.requests.labels(
            purpose=purpose,
            status=status,
            fallback_reason=fallback_reason,
            actual_model=actual_model,
            backend=backend,
            quantization=quantization,
        ).inc()

    def record_fallback(self, *, purpose: str, reason: str) -> None:
        self.fallbacks.labels(purpose=purpose, fallback_reason=reason).inc()

    def record_circuit_transition(self, *, from_state: str, to_state: str) -> None:
        self.circuit_transitions.labels(
            from_state=from_state,
            to_state=to_state,
        ).inc()

    def record_stream_interruption(self, *, purpose: str) -> None:
        self.stream_interruptions.labels(purpose=purpose).inc()

    def render_prometheus(self) -> bytes:
        return generate_latest(self.registry)
