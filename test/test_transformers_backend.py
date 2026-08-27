from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path
from threading import Event
import sys
import time
import unittest
from unittest import mock

import torch

from model_deployment.manifest import ManifestMismatchError
from model_serving.backend import (
    BackendOutOfMemoryError,
    BackendRequestError,
    GenerationRequest,
)
from model_serving.profiles import ModelServingProfile


IDENTITY = {
    "model_id": "localrag-qwen3-4b-e6.1",
    "architecture": "Qwen3ForCausalLM",
    "context_limit": 40960,
    "base_model_path": "models/Qwen3-4B",
    "adapter_path": (
        "saves/Qwen3-4B-Thinking/lora/localrag_sft_e6_1_qlora_webui"
    ),
    "adapter": {
        "type": "LORA",
        "r": 8,
        "alpha": 16,
        "dropout": 0,
        "target_modules": [
            "down_proj",
            "gate_proj",
            "k_proj",
            "o_proj",
            "q_proj",
            "up_proj",
            "v_proj",
        ],
    },
}
MANIFEST = {
    "contract_version": "localrag-model-manifest-v1",
    "kind": "model-input",
    "files": [{"path": "fixture.bin", "size": 1, "sha256": "a" * 64}],
    "metadata": {"model_identity": IDENTITY},
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


def _request(*, temperature=0.0, max_tokens=16):
    from model_serving.backend import BackendMessage

    return GenerationRequest(
        request_id="req-1",
        model="localrag-qwen3-4b-e6.1",
        messages=(BackendMessage("user", "测试"),),
        temperature=temperature,
        max_tokens=max_tokens,
        purpose="rag_generation",
    )


class FakeTensor:
    def __init__(self, token_count):
        self.shape = (1, token_count)
        self.to_calls = []

    def to(self, device):
        self.to_calls.append(device)
        return self


class FakeSequences:
    def __init__(self, token_count):
        self.shape = (1, token_count)


class FakeStreamer:
    def __init__(self, items, *args, **kwargs):
        self.items = list(items)
        self.args = args
        self.kwargs = kwargs
        self.finalized = False

    def __iter__(self):
        yield from self.items

    def on_finalized_text(self, text, stream_end=False):
        self.finalized = bool(stream_end)


class TransformersBackendTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.events = []
        self.token_count = 32
        self.stream_items = ["片段一", "片段二"]
        self.tokenizer = mock.MagicMock()
        self.tokenizer.apply_chat_template.return_value = "rendered prompt"
        self.tokenizer.side_effect = lambda *args, **kwargs: {
            "input_ids": FakeTensor(self.token_count),
            "attention_mask": FakeTensor(self.token_count),
        }
        self.base_model = mock.MagicMock(name="base_model")
        self.model = mock.MagicMock(name="peft_model")
        self.model.generate.side_effect = lambda **kwargs: FakeSequences(
            self.token_count + 2
        )

        self.validate_manifest = self.stack.enter_context(
            mock.patch(
                "model_serving.transformers_backend.validate_manifest",
                side_effect=lambda *args: self.events.append("manifest"),
            )
        )
        self.auto_tokenizer = self.stack.enter_context(
            mock.patch("model_serving.transformers_backend.AutoTokenizer")
        )
        self.auto_tokenizer.from_pretrained.side_effect = (
            lambda *args, **kwargs: self.events.append("tokenizer") or self.tokenizer
        )
        self.auto_model = self.stack.enter_context(
            mock.patch("model_serving.transformers_backend.AutoModelForCausalLM")
        )
        self.auto_model.from_pretrained.side_effect = (
            lambda *args, **kwargs: self.events.append("base") or self.base_model
        )
        self.peft_model = self.stack.enter_context(
            mock.patch("model_serving.transformers_backend.PeftModel")
        )
        self.peft_model.from_pretrained.side_effect = (
            lambda *args, **kwargs: self.events.append("adapter") or self.model
        )
        self.streamer = self.stack.enter_context(
            mock.patch(
                "model_serving.transformers_backend.TextIteratorStreamer",
                side_effect=lambda *args, **kwargs: FakeStreamer(
                    self.stream_items, *args, **kwargs
                ),
            )
        )

    def _backend(self):
        from model_serving.transformers_backend import TransformersGenerationBackend

        return TransformersGenerationBackend(
            profile=_profile(),
            repo_root=Path("."),
            expected_manifest=MANIFEST,
            device="cuda",
        )

    def test_load_order_and_manifest_bound_bf16_adapter_identity(self):
        backend = self._backend()

        self.assertEqual(
            ["manifest", "tokenizer", "base", "adapter"],
            self.events,
        )
        self.auto_tokenizer.from_pretrained.assert_called_once_with(
            Path(_profile().base_model_path).resolve(),
            local_files_only=True,
            trust_remote_code=False,
        )
        self.auto_model.from_pretrained.assert_called_once_with(
            Path(_profile().base_model_path).resolve(),
            dtype=torch.bfloat16,
            local_files_only=True,
            trust_remote_code=False,
            low_cpu_mem_usage=True,
        )
        self.peft_model.from_pretrained.assert_called_once_with(
            self.base_model,
            Path(_profile().adapter_path).resolve(),
            local_files_only=True,
            is_trainable=False,
        )
        self.model.eval.assert_called_once_with()
        self.model.to.assert_called_once_with("cuda")
        self.assertFalse(hasattr(self.model, "merge_and_unload") and self.model.merge_and_unload.called)
        self.assertEqual("none", backend.identity.quantization)
        self.assertFalse(backend.readiness().ready)

    def test_manifest_failure_stops_before_model_loading(self):
        self.validate_manifest.side_effect = ManifestMismatchError("changed")

        with self.assertRaises(ManifestMismatchError):
            self._backend()

        self.auto_tokenizer.from_pretrained.assert_not_called()
        self.auto_model.from_pretrained.assert_not_called()

    def test_prompt_disables_thinking_and_context_limit_fails_closed(self):
        backend = self._backend()

        backend.start(_request(max_tokens=16))

        self.tokenizer.apply_chat_template.assert_called_with(
            [{"role": "user", "content": "测试"}],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        self.token_count = 40945
        with self.assertRaises(BackendRequestError):
            backend.start(_request(max_tokens=16))

    def test_greedy_streaming_generation_and_cancel_criteria(self):
        backend = self._backend()
        handle = backend.start(_request(temperature=0.0))

        chunks = list(handle)

        self.assertEqual(["片段一", "片段二", ""], [chunk.text for chunk in chunks])
        self.assertEqual("stop", chunks[-1].finish_reason)
        self.assertEqual((32, 2), (chunks[-1].input_tokens, chunks[-1].output_tokens))
        generate_kwargs = self.model.generate.call_args.kwargs
        self.assertFalse(generate_kwargs["do_sample"])
        self.assertIsNone(generate_kwargs["temperature"])
        self.assertIsNone(generate_kwargs["top_p"])
        self.assertIsNone(generate_kwargs["top_k"])
        self.assertEqual(16, generate_kwargs["max_new_tokens"])
        self.assertTrue(self.streamer.call_args.kwargs["skip_prompt"])
        self.assertTrue(self.streamer.call_args.kwargs["skip_special_tokens"])

        second = backend.start(_request())
        self.assertIsNot(handle._cancel_event, second._cancel_event)
        second.cancel()
        list(second)
        stopping = self.model.generate.call_args.kwargs["stopping_criteria"][0]
        self.assertTrue(stopping(None, None))

    def test_sampling_request_sets_temperature(self):
        backend = self._backend()

        list(backend.start(_request(temperature=0.7)))

        kwargs = self.model.generate.call_args.kwargs
        self.assertTrue(kwargs["do_sample"])
        self.assertEqual(0.7, kwargs["temperature"])

    def test_generation_reaching_token_limit_reports_length(self):
        backend = self._backend()
        self.model.generate.side_effect = lambda **kwargs: FakeSequences(
            self.token_count + 16
        )

        chunks = list(backend.start(_request(max_tokens=16)))

        self.assertEqual("length", chunks[-1].finish_reason)
        self.assertEqual(16, chunks[-1].output_tokens)

    def test_closing_handle_stops_and_joins_generation_thread(self):
        backend = self._backend()
        generation_started = Event()

        def blocking_generate(**kwargs):
            generation_started.set()
            stopping = kwargs["stopping_criteria"][0]
            deadline = time.monotonic() + 2
            while not stopping(None, None):
                if time.monotonic() >= deadline:
                    raise AssertionError("cancel stopping criteria was not activated")
                time.sleep(0.01)
            return FakeSequences(self.token_count + 1)

        self.model.generate.side_effect = blocking_generate
        iterator = iter(backend.start(_request()))

        self.assertEqual("片段一", next(iterator).text)
        self.assertTrue(generation_started.wait(timeout=1))
        iterator.close()

        self.assertTrue(self.model.generate.called)

    def test_cuda_oom_clears_cache_and_latches_not_ready(self):
        backend = self._backend()
        self.stream_items = []
        self.model.generate.side_effect = torch.cuda.OutOfMemoryError("oom")

        with mock.patch("model_serving.transformers_backend.torch.cuda.empty_cache") as empty:
            with self.assertRaises(BackendOutOfMemoryError):
                list(backend.start(_request()))

        empty.assert_called_once_with()
        readiness = backend.readiness()
        self.assertFalse(readiness.ready)
        self.assertTrue(readiness.oom_latched)
        with self.assertRaises(BackendOutOfMemoryError):
            backend.start(_request())

    def test_warmup_consumes_generation_and_marks_ready(self):
        backend = self._backend()

        backend.warmup()

        readiness = backend.readiness()
        self.assertTrue(readiness.ready)
        self.assertTrue(readiness.warmed_up)


class ModelServingCliTests(unittest.TestCase):
    def test_cli_rejects_multiple_workers_before_loading_model(self):
        from model_serving import main as serving_main

        argv = ["main.py", "--workers", "2"]
        with mock.patch.object(sys, "argv", argv):
            with self.assertRaisesRegex(ValueError, "workers"):
                serving_main.main()

    def test_launch_script_binds_loopback_and_single_active_generation(self):
        script = (
            Path(__file__).resolve().parents[1]
            / "model_deployment"
            / "launch_transformers.ps1"
        ).read_text(encoding="utf-8")

        self.assertIn("--host 127.0.0.1", script)
        self.assertIn("--active-limit 1", script)
        self.assertIn("--waiting-limit 4", script)
        self.assertNotIn("0.0.0.0", script)
        self.assertIn("$LASTEXITCODE", script)


if __name__ == "__main__":
    unittest.main()
