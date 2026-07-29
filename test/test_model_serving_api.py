from __future__ import annotations

from threading import Event, Thread
import time
import unittest

from fastapi.testclient import TestClient

from model_serving.api import _stream_openai_events, create_app
from model_serving.backend import (
    BackendGenerationError,
    BackendIdentity,
    BackendReadiness,
    GenerationChunk,
    manifest_fingerprint,
)
from model_serving.metrics import ServingMetrics
from model_serving.profiles import ModelServingProfile
from model_serving.queue import GenerationQueue, QueueFullError


MANIFEST = {
    "contract_version": "localrag-model-manifest-v1",
    "kind": "model-input",
    "files": [{"path": "fixture.bin", "size": 1, "sha256": "a" * 64}],
    "metadata": {},
}


def _profile() -> ModelServingProfile:
    return ModelServingProfile(
        name="e6_1_adapter_bf16",
        model_id="localrag-qwen3-4b-e6.1",
        backend="transformers",
        base_model_path="models/Qwen3-4B",
        adapter_path=(
            "saves/Qwen3-4B-Thinking/lora/localrag_sft_e6_1_qlora_webui"
        ),
        artifact_path=None,
        dtype="bfloat16",
        quantization="none",
        context_limit=40960,
        max_new_tokens=1024,
        enable_thinking=False,
        manifest_path="model_deployment/manifests/e6_1_input_manifest.json",
    )


class FakeGenerationHandle:
    def __init__(self, chunks=(), *, error=None):
        self.chunks = list(chunks)
        self.error = error
        self.cancelled = False

    def __iter__(self):
        yield from self.chunks
        if self.error is not None:
            raise self.error

    def cancel(self):
        self.cancelled = True


class BlockingGenerationHandle(FakeGenerationHandle):
    def __init__(self, release: Event):
        super().__init__()
        self.release = release

    def __iter__(self):
        self.release.wait(timeout=3)
        yield GenerationChunk("released", 4, 1, "stop")


class FakeGenerationBackend:
    def __init__(self):
        self._identity = BackendIdentity(
            model_id="localrag-qwen3-4b-e6.1",
            backend="transformers",
            quantization="none",
            manifest_sha256=manifest_fingerprint(MANIFEST),
        )
        self.ready = False
        self.oom_latched = False
        self.readiness_calls = 0
        self.requests = []
        self.handles = []
        self.start_error = None

    @property
    def identity(self):
        return self._identity

    def warmup(self):
        self.ready = True

    def readiness(self):
        self.readiness_calls += 1
        return BackendReadiness(
            ready=self.ready and not self.oom_latched,
            warmed_up=self.ready,
            oom_latched=self.oom_latched,
            detail="ready" if self.ready else "not_warmed_up",
        )

    def start(self, request):
        self.requests.append(request)
        if self.start_error is not None:
            raise self.start_error
        if self.handles:
            return self.handles.pop(0)
        return FakeGenerationHandle(
            [GenerationChunk("fake answer", 7, 2, "stop")]
        )


def _request(*, stream=False, **overrides):
    payload = {
        "model": "localrag-qwen3-4b-e6.1",
        "messages": [{"role": "user", "content": "测试"}],
        "temperature": 0,
        "max_tokens": 16,
        "stream": stream,
        "purpose": "rag_generation",
        "metadata": {"session_id": "session-1"},
    }
    payload.update(overrides)
    return payload


class ModelServingApiTests(unittest.TestCase):
    def setUp(self):
        self.backend = FakeGenerationBackend()
        self.metrics = ServingMetrics()
        self.app = create_app(
            backend=self.backend,
            profile=_profile(),
            expected_manifest=MANIFEST,
            api_token="local-test",
            metrics=self.metrics,
        )
        self.client = TestClient(self.app)
        self.headers = {
            "Authorization": "Bearer local-test",
            "X-Request-ID": "req-1",
        }

    def test_health_does_not_access_backend(self):
        response = self.client.get("/health")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json())
        self.assertEqual(0, self.backend.readiness_calls)

    def test_ready_requires_warmup_manifest_and_backend_identity(self):
        response = self.client.get("/ready", headers=self.headers)
        self.assertEqual(503, response.status_code)

        self.backend.warmup()
        response = self.client.get("/ready", headers=self.headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual("ready", response.json()["status"])

        self.backend.oom_latched = True
        response = self.client.get("/ready", headers=self.headers)
        self.assertEqual(503, response.status_code)
        self.backend.oom_latched = False

        self.backend._identity = BackendIdentity(
            model_id="wrong",
            backend="transformers",
            quantization="none",
            manifest_sha256=manifest_fingerprint(MANIFEST),
        )
        response = self.client.get("/ready", headers=self.headers)
        self.assertEqual(503, response.status_code)

    def test_models_exposes_only_current_identity(self):
        response = self.client.get("/v1/models", headers=self.headers)

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()["data"]))
        self.assertEqual(_profile().model_id, response.json()["data"][0]["id"])

    def test_auth_and_request_validation_fail_closed_with_4xx(self):
        self.backend.warmup()
        self.assertEqual(
            401,
            self.client.post("/v1/chat/completions", json=_request()).status_code,
        )
        invalid_payloads = (
            _request(purpose="unknown"),
            _request(messages=[{"role": "tool", "content": "bad"}]),
            _request(max_tokens=2048),
            _request(model="other"),
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    "/v1/chat/completions", headers=self.headers, json=payload
                )
                self.assertEqual(400, response.status_code)

    def test_non_streaming_response_has_usage_and_request_id(self):
        self.backend.warmup()

        response = self.client.post(
            "/v1/chat/completions",
            headers=self.headers,
            json=_request(stream=False),
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("req-1", response.headers["X-Request-ID"])
        payload = response.json()
        self.assertEqual("fake answer", payload["choices"][0]["message"]["content"])
        self.assertEqual("stop", payload["choices"][0]["finish_reason"])
        self.assertEqual(
            {"prompt_tokens": 7, "completion_tokens": 2, "total_tokens": 9},
            payload["usage"],
        )
        request = self.backend.requests[0]
        self.assertEqual("rag_generation", request.purpose)
        self.assertEqual("测试", request.messages[0].content)

    def test_stream_uses_openai_sse_and_post_token_failure_is_contained(self):
        self.backend.warmup()
        self.backend.handles.append(
            FakeGenerationHandle(
                [GenerationChunk("first", 5, 1)],
                error=BackendGenerationError("stream broke", started=True),
            )
        )

        response = self.client.post(
            "/v1/chat/completions",
            headers=self.headers,
            json=_request(stream=True),
        )

        self.assertEqual(200, response.status_code)
        events = [line for line in response.text.splitlines() if line.startswith("data:")]
        self.assertIn('"role":"assistant"', events[0])
        self.assertTrue(any('"content":"first"' in event for event in events))
        self.assertTrue(any('"type":"generation_error"' in event for event in events))
        self.assertEqual("data: [DONE]", events[-1])

        normal = self.client.post(
            "/v1/chat/completions", headers=self.headers, json=_request()
        )
        self.assertEqual(200, normal.status_code)

    def test_failure_before_first_token_returns_error_response(self):
        self.backend.warmup()
        self.backend.handles.append(
            FakeGenerationHandle(
                error=BackendGenerationError("failed before token", started=False)
            )
        )

        response = self.client.post(
            "/v1/chat/completions",
            headers=self.headers,
            json=_request(stream=True),
        )

        self.assertEqual(503, response.status_code)
        self.assertEqual("backend_generation_error", response.json()["error"]["code"])

    def test_closing_stream_generator_cancels_handle(self):
        handle = FakeGenerationHandle([GenerationChunk("first", 1, 1)])
        events = _stream_openai_events(
            handle=handle,
            request_id="req-cancel",
            model=_profile().model_id,
        )

        next(events)
        events.close()

        self.assertTrue(handle.cancelled)

    def test_metrics_expose_fixed_names_without_high_cardinality_ids(self):
        self.backend.warmup()
        self.client.post(
            "/v1/chat/completions",
            headers=self.headers,
            json=_request(),
        )

        response = self.client.get("/metrics")
        body = response.text

        for metric_name in (
            "localrag_model_requests_total",
            "localrag_model_queue_depth",
            "localrag_model_active_generations",
            "localrag_model_ttft_seconds",
            "localrag_model_request_duration_seconds",
            "localrag_model_input_tokens_total",
            "localrag_model_output_tokens_total",
            "localrag_model_oom_total",
            "localrag_model_cancel_total",
            "localrag_model_gpu_allocated_memory_bytes",
            "localrag_model_gpu_reserved_memory_bytes",
            "localrag_model_gpu_peak_memory_bytes",
        ):
            self.assertIn(metric_name, body)
        self.assertNotIn("req-1", body)
        self.assertNotIn("session-1", body)

    def test_request_log_hashes_content_without_logging_prompt_text(self):
        self.backend.warmup()
        prompt = "private-prompt-must-not-be-logged"

        with self.assertLogs("model_serving.api", level="INFO") as captured:
            response = self.client.post(
                "/v1/chat/completions",
                headers=self.headers,
                json=_request(messages=[{"role": "user", "content": prompt}]),
            )

        self.assertEqual(200, response.status_code)
        logs = "\n".join(captured.output)
        self.assertNotIn(prompt, logs)
        self.assertIn("sha256=", logs)

    def test_api_queue_allows_one_waiter_and_rejects_the_next_request(self):
        backend = FakeGenerationBackend()
        backend.warmup()
        release = Event()
        backend.handles.extend(
            [
                BlockingGenerationHandle(release),
                FakeGenerationHandle([GenerationChunk("second", 4, 1, "stop")]),
            ]
        )
        app = create_app(
            backend=backend,
            profile=_profile(),
            expected_manifest=MANIFEST,
            api_token="local-test",
            active_limit=1,
            waiting_limit=1,
            queue_timeout_seconds=2,
        )
        client = TestClient(app)
        responses = []

        def submit(request_id):
            responses.append(
                client.post(
                    "/v1/chat/completions",
                    headers={**self.headers, "X-Request-ID": request_id},
                    json=_request(),
                )
            )

        first = Thread(target=submit, args=("queue-1",))
        second = Thread(target=submit, args=("queue-2",))
        first.start()
        deadline = time.monotonic() + 1
        while app.state.generation_queue.snapshot().active != 1:
            if time.monotonic() >= deadline:
                self.fail("first request did not acquire active slot")
            time.sleep(0.01)
        second.start()
        deadline = time.monotonic() + 1
        while app.state.generation_queue.snapshot().waiting != 1:
            if time.monotonic() >= deadline:
                self.fail("second request did not enter the waiting queue")
            time.sleep(0.01)

        rejected = client.post(
            "/v1/chat/completions",
            headers={**self.headers, "X-Request-ID": "queue-3"},
            json=_request(),
        )
        release.set()
        first.join(timeout=3)
        second.join(timeout=3)

        self.assertEqual(429, rejected.status_code)
        self.assertEqual(
            [200, 200], sorted(response.status_code for response in responses)
        )


class GenerationQueueTests(unittest.TestCase):
    def test_waiting_limit_is_bounded_and_waiter_acquires_after_release(self):
        queue = GenerationQueue(active_limit=1, waiting_limit=1)
        first = queue.acquire(timeout_seconds=1)
        first.__enter__()
        acquired = Event()

        def wait_for_slot():
            with queue.acquire(timeout_seconds=2):
                acquired.set()

        thread = Thread(target=wait_for_slot)
        thread.start()
        deadline = time.monotonic() + 1
        while queue.snapshot().waiting != 1 and time.monotonic() < deadline:
            time.sleep(0.01)

        with self.assertRaises(QueueFullError):
            queue.acquire(timeout_seconds=1).__enter__()
        first.__exit__(None, None, None)
        thread.join(timeout=2)

        self.assertTrue(acquired.is_set())
        self.assertEqual((0, 0), (queue.snapshot().active, queue.snapshot().waiting))


if __name__ == "__main__":
    unittest.main()
