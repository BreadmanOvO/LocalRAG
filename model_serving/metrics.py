from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from prometheus_client.exposition import generate_latest

from .profiles import ModelServingProfile


_IDENTITY_LABELS = ("profile", "backend", "quantization")
_REQUEST_LABELS = (*_IDENTITY_LABELS, "purpose", "status")


class ServingMetrics:
    def __init__(self) -> None:
        self.registry = CollectorRegistry(auto_describe=True)
        self.requests = Counter(
            "localrag_model_requests_total",
            "Completed local model requests.",
            _REQUEST_LABELS,
            registry=self.registry,
        )
        self.queue_depth = Gauge(
            "localrag_model_queue_depth",
            "Current queued model requests.",
            _IDENTITY_LABELS,
            registry=self.registry,
        )
        self.active_generations = Gauge(
            "localrag_model_active_generations",
            "Current active model generations.",
            _IDENTITY_LABELS,
            registry=self.registry,
        )
        self.ttft = Histogram(
            "localrag_model_ttft_seconds",
            "Time to first generated token.",
            _REQUEST_LABELS,
            registry=self.registry,
        )
        self.duration = Histogram(
            "localrag_model_request_duration_seconds",
            "Model request duration.",
            _REQUEST_LABELS,
            registry=self.registry,
        )
        self.input_tokens = Counter(
            "localrag_model_input_tokens_total",
            "Model input tokens.",
            _REQUEST_LABELS,
            registry=self.registry,
        )
        self.output_tokens = Counter(
            "localrag_model_output_tokens_total",
            "Model output tokens.",
            _REQUEST_LABELS,
            registry=self.registry,
        )
        self.oom = Counter(
            "localrag_model_oom_total",
            "CUDA out-of-memory failures.",
            (*_IDENTITY_LABELS, "purpose"),
            registry=self.registry,
        )
        self.cancel = Counter(
            "localrag_model_cancel_total",
            "Cancelled model generations.",
            (*_IDENTITY_LABELS, "purpose"),
            registry=self.registry,
        )
        self.gpu_allocated = Gauge(
            "localrag_model_gpu_allocated_memory_bytes",
            "CUDA allocated memory.",
            _IDENTITY_LABELS,
            registry=self.registry,
        )
        self.gpu_reserved = Gauge(
            "localrag_model_gpu_reserved_memory_bytes",
            "CUDA reserved memory.",
            _IDENTITY_LABELS,
            registry=self.registry,
        )
        self.gpu_peak = Gauge(
            "localrag_model_gpu_peak_memory_bytes",
            "CUDA peak allocated memory.",
            _IDENTITY_LABELS,
            registry=self.registry,
        )

    @staticmethod
    def _identity(profile: ModelServingProfile) -> dict[str, str]:
        return {
            "profile": profile.name,
            "backend": profile.backend,
            "quantization": profile.quantization,
        }

    def set_queue(self, profile: ModelServingProfile, *, active: int, waiting: int) -> None:
        labels = self._identity(profile)
        self.active_generations.labels(**labels).set(active)
        self.queue_depth.labels(**labels).set(waiting)

    def record_request(
        self,
        profile: ModelServingProfile,
        *,
        purpose: str,
        status: str,
        duration_seconds: float,
        ttft_seconds: float | None,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        labels = {
            **self._identity(profile),
            "purpose": purpose,
            "status": status,
        }
        self.requests.labels(**labels).inc()
        self.duration.labels(**labels).observe(max(0.0, duration_seconds))
        if ttft_seconds is not None:
            self.ttft.labels(**labels).observe(max(0.0, ttft_seconds))
        self.input_tokens.labels(**labels).inc(max(0, input_tokens))
        self.output_tokens.labels(**labels).inc(max(0, output_tokens))

    def record_oom(self, profile: ModelServingProfile, purpose: str) -> None:
        self.oom.labels(**self._identity(profile), purpose=purpose).inc()

    def record_cancel(self, profile: ModelServingProfile, purpose: str) -> None:
        self.cancel.labels(**self._identity(profile), purpose=purpose).inc()

    def set_gpu_memory(
        self,
        profile: ModelServingProfile,
        *,
        allocated: int,
        reserved: int,
        peak: int,
    ) -> None:
        labels = self._identity(profile)
        self.gpu_allocated.labels(**labels).set(max(0, allocated))
        self.gpu_reserved.labels(**labels).set(max(0, reserved))
        self.gpu_peak.labels(**labels).set(max(0, peak))

    def render(self) -> bytes:
        return generate_latest(self.registry)
