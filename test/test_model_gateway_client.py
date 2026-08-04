from __future__ import annotations

import json
import unittest

import httpx

from model_gateway import (
    GatewayBadRequestError,
    GatewayChunk,
    GatewayIdentityError,
    GatewayOOMError,
    GatewayQueueFullError,
    GatewayRequestContext,
    GatewayResponseValidationError,
    GatewayStreamInterruptedError,
    GatewayTimeoutError,
    GatewayUsage,
    ModelPurpose,
    OpenAICompatibleClient,
)


def _context() -> GatewayRequestContext:
    return GatewayRequestContext(
        request_id="req-001",
        purpose=ModelPurpose.RAG_GENERATION,
        session_id="session-001",
        task_id="task-001",
        run_id="run-001",
    )


def _success_body() -> dict[str, object]:
    return {
        "id": "chatcmpl-req-001",
        "object": "chat.completion",
        "model": "localrag-qwen3-4b-e6.1",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "有证据的答案"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 12, "completion_tokens": 6, "total_tokens": 18},
    }


class ModelGatewayClientTests(unittest.TestCase):
    def _client(self, handler, trace=None):
        transport = httpx.MockTransport(handler)
        http_client = httpx.Client(transport=transport)
        self.addCleanup(http_client.close)
        client = OpenAICompatibleClient(
            "http://127.0.0.1:8002/v1",
            model="localrag-qwen3-4b-e6.1",
            api_token="secret",
            http_client=http_client,
            trace_sink=trace,
        )
        self.addCleanup(client.close)
        return client

    def test_complete_sends_contract_metadata_and_redacted_trace(self):
        traces = []

        def handler(request):
            payload = json.loads(request.content)
            self.assertEqual("Bearer secret", request.headers["Authorization"])
            self.assertEqual("req-001", request.headers["X-Request-ID"])
            self.assertEqual("rag_generation", payload["purpose"])
            self.assertEqual(
                {"session_id": "session-001", "task_id": "task-001", "run_id": "run-001"},
                payload["metadata"],
            )
            self.assertNotIn("原始提示", json.dumps(traces, ensure_ascii=False))
            return httpx.Response(
                200,
                json=_success_body(),
                headers={
                    "X-Request-ID": "req-001",
                    "X-Queue-Wait-Seconds": "0.25",
                    "X-Backend": "llama.cpp",
                    "X-Quantization": "Q4_K_M",
                },
            )

        client = self._client(handler, traces.append)
        result = client.complete(
            [{"role": "user", "content": "原始提示"}],
            context=_context(),
            max_tokens=64,
        )
        self.assertEqual("有证据的答案", result.text)
        self.assertEqual(GatewayUsage(12, 6, 18), result.usage)
        self.assertEqual("llama.cpp", result.backend)
        self.assertEqual("Q4_K_M", result.quantization)
        self.assertEqual(0.25, result.queue_seconds)
        self.assertTrue(traces)
        self.assertEqual("success", traces[-1]["status"])
        self.assertNotIn("原始提示", json.dumps(traces, ensure_ascii=False))
        self.assertIn("prompt_sha256", traces[-1])

    def test_http_statuses_map_to_structured_errors(self):
        statuses = {
            400: GatewayBadRequestError,
            401: GatewayIdentityError,
            429: GatewayQueueFullError,
        }
        for status, error_type in statuses.items():
            with self.subTest(status=status):
                client = self._client(
                    lambda request, status=status: httpx.Response(
                        status,
                        json={"error": {"code": "queue_unavailable"}},
                    )
                )
                with self.assertRaises(error_type):
                    client.complete(
                        [{"role": "user", "content": "question"}],
                        context=_context(),
                    )

        special_statuses = (
            (503, "backend_out_of_memory", GatewayOOMError),
            (504, "backend_timeout", GatewayTimeoutError),
        )
        for status, code, error_type in special_statuses:
            with self.subTest(status=status, code=code):
                client = self._client(
                    lambda request, status=status, code=code: httpx.Response(
                        status,
                        json={"error": {"code": code}},
                    )
                )
                with self.assertRaises(error_type):
                    client.complete(
                        [{"role": "user", "content": "question"}],
                        context=_context(),
                    )

    def test_identity_and_response_validation_fail_closed(self):
        for body in (
            {**_success_body(), "model": "other"},
            {**_success_body(), "choices": []},
            {**_success_body(), "usage": {"prompt_tokens": 1}},
        ):
            with self.subTest(body=body):
                client = self._client(lambda request, body=body: httpx.Response(200, json=body))
                expected = GatewayIdentityError if body.get("model") == "other" else GatewayResponseValidationError
                with self.assertRaises(expected):
                    client.complete(
                        [{"role": "user", "content": "question"}],
                        context=_context(),
                    )

    def test_timeout_maps_without_leaking_exception_text(self):
        def handler(request):
            raise httpx.ReadTimeout("private prompt text", request=request)

        client = self._client(handler)
        with self.assertRaises(GatewayTimeoutError) as raised:
            client.complete(
                [{"role": "user", "content": "question"}],
                context=_context(),
            )
        self.assertNotIn("private prompt text", str(raised.exception))

    def test_stream_parses_sse_and_closes_response(self):
        events = [
            {"model": "localrag-qwen3-4b-e6.1", "choices": [{"delta": {"content": "有"}, "finish_reason": None}]},
            {"model": "localrag-qwen3-4b-e6.1", "choices": [{"delta": {"content": "证据"}, "finish_reason": None}]},
            {"model": "localrag-qwen3-4b-e6.1", "choices": [{"delta": {}, "finish_reason": "stop"}], "usage": {"prompt_tokens": 2, "completion_tokens": 2, "total_tokens": 4}},
        ]
        body = "".join(f"data: {json.dumps(event)}\n\n" for event in events) + "data: [DONE]\n\n"
        client = self._client(
            lambda request: httpx.Response(
                200,
                text=body,
                headers={"content-type": "text/event-stream"},
            )
        )
        stream = client.stream(
            [{"role": "user", "content": "question"}],
            context=_context(),
        )
        chunks = list(stream)
        self.assertEqual(["有", "证据", ""], [chunk.text for chunk in chunks])
        self.assertTrue(stream.started)
        self.assertTrue(stream.closed)
        self.assertEqual(GatewayUsage(2, 2, 4), chunks[-1].usage)

    def test_stream_identity_or_invalid_json_fails_and_can_close(self):
        bodies = (
            "data: {\"model\": \"other\", \"choices\": [{\"delta\": {\"content\": \"x\"}}]}\n\n",
            "data: not-json\n\n",
        )
        for body in bodies:
            with self.subTest(body=body):
                client = self._client(lambda request, body=body: httpx.Response(200, text=body))
                stream = client.stream(
                    [{"role": "user", "content": "question"}],
                    context=_context(),
                )
                expected = GatewayIdentityError if "other" in body else GatewayResponseValidationError
                with self.assertRaises(expected):
                    next(stream)
                stream.close()

    def test_stream_interrupt_after_start_is_not_silently_completed(self):
        def handler(request):
            def content():
                yield b'data: {"model":"localrag-qwen3-4b-e6.1","choices":[{"delta":{"content":"x"},"finish_reason":null}]}\n\n'
                raise httpx.ReadError("private stream detail", request=request)

            return httpx.Response(200, content=content())

        client = self._client(handler)
        stream = client.stream(
            [{"role": "user", "content": "question"}],
            context=_context(),
        )
        self.assertIsInstance(next(stream), GatewayChunk)
        with self.assertRaises(GatewayStreamInterruptedError) as raised:
            next(stream)
        self.assertTrue(raised.exception.started)

    def test_health_and_ready_use_authentication(self):
        paths = []

        def handler(request):
            paths.append((request.url.path, request.headers.get("Authorization")))
            return httpx.Response(200, json={"status": "ok"})

        client = self._client(handler)
        self.assertEqual({"status": "ok"}, client.health())
        self.assertEqual({"status": "ok"}, client.ready())
        self.assertEqual(
            [
                ("/health", "Bearer secret"),
                ("/ready", "Bearer secret"),
            ],
            paths,
        )

    def test_constructor_and_request_validation(self):
        with self.assertRaises(ValueError):
            OpenAICompatibleClient(
                "http://127.0.0.1:8002/v1",
                model="localrag-qwen3-4b-e6.1",
                api_token="secret",
                connect_timeout_seconds=0,
            )
        client = self._client(lambda request: httpx.Response(200, json=_success_body()))
        with self.assertRaises(ValueError):
            client.complete([], context=_context())
        with self.assertRaises(ValueError):
            client.complete(
                [{"role": "tool", "content": "bad"}],
                context=_context(),
            )


if __name__ == "__main__":
    unittest.main()
