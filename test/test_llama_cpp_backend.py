from __future__ import annotations

from contextlib import ExitStack
import json
from pathlib import Path
import unittest
from unittest import mock

import httpx

from model_serving.backend import (
    BackendGenerationError,
    BackendIdentityError,
    BackendMessage,
    BackendOutOfMemoryError,
    BackendRequestError,
    BackendTimeoutError,
    GenerationRequest,
)
from model_serving.llama_cpp_backend import LlamaCppGenerationBackend
from model_serving.profiles import ModelServingProfile


MANIFEST = {
    "contract_version": "localrag-model-manifest-v1",
    "kind": "model-gguf-q4-k-m",
    "files": [
        {
            "path": "artifacts/models/qwen3-4b-e6.1-q4_k_m.gguf",
            "size": 1,
            "sha256": "a" * 64,
        }
    ],
    "metadata": {
        "model_identity": {
            "model_id": "localrag-qwen3-4b-e6.1",
            "architecture": "Qwen3ForCausalLM",
            "context_limit": 40960,
            "dtype": "float16",
            "quantization": "Q4_K_M",
            "artifact_path": "artifacts/models/qwen3-4b-e6.1-q4_k_m.gguf",
        }
    },
}


def _profile() -> ModelServingProfile:
    return ModelServingProfile(
        name="e6_1_q4_k_m",
        model_id="localrag-qwen3-4b-e6.1",
        backend="llama_cpp",
        base_model_path=None,
        adapter_path=None,
        artifact_path="artifacts/models/qwen3-4b-e6.1-q4_k_m.gguf",
        dtype="float16",
        quantization="Q4_K_M",
        context_limit=40960,
        max_new_tokens=1024,
        enable_thinking=False,
        manifest_path="model_deployment/manifests/e6_1_q4_k_m_manifest.json",
    )


def _request(**overrides) -> GenerationRequest:
    values = {
        "request_id": "req-1",
        "model": "localrag-qwen3-4b-e6.1",
        "messages": (BackendMessage("user", "测试"),),
        "temperature": 0.0,
        "max_tokens": 16,
        "purpose": "rag_generation",
    }
    values.update(overrides)
    return GenerationRequest(**values)


def _sse(*events) -> bytes:
    rows = [
        "data: " + json.dumps(event, ensure_ascii=False)
        for event in events
    ]
    rows.append("data: [DONE]")
    return ("\n\n".join(rows) + "\n\n").encode()


class LlamaCppBackendTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(
            mock.patch("model_serving.llama_cpp_backend.validate_manifest")
        )
        self.requests = []

    def _client(self, handler):
        return httpx.Client(
            base_url="http://127.0.0.1:18002/v1/",
            transport=httpx.MockTransport(handler),
        )

    def _backend(self, handler, **overrides):
        values = {
            "profile": _profile(),
            "repo_root": Path("."),
            "expected_manifest": MANIFEST,
            "base_url": "http://127.0.0.1:18002/v1",
            "client": self._client(handler),
        }
        values.update(overrides)
        return LlamaCppGenerationBackend(**values)

    def test_warmup_identity_and_stream_mapping(self):
        def handler(request):
            self.requests.append(request)
            if request.url.path.endswith("/models"):
                return httpx.Response(
                    200,
                    json={
                        "object": "list",
                        "data": [{"id": "localrag-qwen3-4b-e6.1"}],
                    },
                )
            payload = json.loads(request.content)
            self.assertNotIn("purpose", payload)
            self.assertNotIn("metadata", payload)
            return httpx.Response(
                200,
                content=_sse(
                    {
                        "choices": [
                            {"delta": {"content": "答案"}, "finish_reason": None}
                        ]
                    },
                    {
                        "choices": [{"delta": {}, "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": 7, "completion_tokens": 2},
                    },
                ),
            )

        backend = self._backend(handler)
        backend.warmup()
        chunks = list(backend.start(_request()))

        self.assertTrue(backend.readiness().ready)
        self.assertEqual("答案", chunks[0].text)
        self.assertEqual("stop", chunks[-1].finish_reason)
        self.assertEqual((7, 2), (chunks[-1].input_tokens, chunks[-1].output_tokens))

    def test_identity_mismatch_fails_warmup(self):
        def handler(request):
            return httpx.Response(200, json={"data": [{"id": "other"}]})

        with self.assertRaises(BackendIdentityError):
            self._backend(handler).warmup()

    def test_stream_error_after_first_token_preserves_started_state(self):
        def handler(request):
            return httpx.Response(
                200,
                content=(
                    'data: {"choices":[{"delta":{"content":"first"}}]}\n\n'
                    "data: not-json\n\n"
                ).encode(),
            )

        iterator = iter(self._backend(handler).start(_request()))
        self.assertEqual("first", next(iterator).text)
        with self.assertRaises(BackendGenerationError) as caught:
            next(iterator)
        self.assertTrue(caught.exception.started)

    def test_status_errors_are_mapped(self):
        cases = (
            (400, "bad request", BackendRequestError),
            (429, "busy", BackendTimeoutError),
            (500, "CUDA out of memory", BackendOutOfMemoryError),
        )
        for status, body, error_type in cases:
            with self.subTest(status=status):
                backend = self._backend(
                    lambda request, status=status, body=body: httpx.Response(
                        status, text=body
                    )
                )
                with self.assertRaises(error_type):
                    list(backend.start(_request()))

    def test_cancelled_handle_reports_cancelled(self):
        backend = self._backend(
            lambda request: httpx.Response(
                200,
                content=_sse(
                    {"choices": [{"delta": {"content": "ignored"}}]}
                ),
            )
        )
        handle = backend.start(_request())
        handle.cancel()

        chunks = list(handle)

        self.assertEqual("cancelled", chunks[-1].finish_reason)

    def test_request_and_base_url_validation_fail_closed(self):
        backend = self._backend(lambda request: httpx.Response(200))
        with self.assertRaises(BackendRequestError):
            backend.start(_request(model="other"))
        with self.assertRaises(BackendIdentityError):
            self._backend(
                lambda request: httpx.Response(200),
                base_url="http://example.com/v1",
            )

    def test_manifest_identity_must_match_q4_profile(self):
        manifest = json.loads(json.dumps(MANIFEST))
        manifest["metadata"]["model_identity"]["quantization"] = "none"

        with self.assertRaises(BackendIdentityError):
            self._backend(lambda request: httpx.Response(200), expected_manifest=manifest)


if __name__ == "__main__":
    unittest.main()
