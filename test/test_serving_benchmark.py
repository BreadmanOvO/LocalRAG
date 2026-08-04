from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import httpx

from eval.benchmark_serving import (
    BenchmarkCase,
    CONCURRENCY_LEVELS,
    MEASURED_ROUNDS,
    OUTPUT_TOKENS,
    PROMPT_TARGETS,
    ServingBenchmarkError,
    _atomic_write_text,
    _completed_cells,
    _deterministic_samples,
    _jsonl_write,
    _load_jsonl,
    _validate_request_timeout_seconds,
    _validate_resume_identity,
    build_prompt,
    compare_profiles,
    deterministic_fixture,
    run_benchmark_cell,
    summarize_profile,
)


class _WhitespaceTokenizer:
    @staticmethod
    def encode(text, add_special_tokens=False):
        del add_special_tokens
        return list(range(len(text.split())))

    @staticmethod
    def decode(token_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False):
        del skip_special_tokens, clean_up_tokenization_spaces
        return " ".join(f"t{value}" for value in token_ids)


class ServingBenchmarkTests(unittest.TestCase):
    def test_prompt_builder_stays_within_two_percent(self):
        tokenizer = _WhitespaceTokenizer()
        for target in PROMPT_TARGETS:
            with self.subTest(target=target):
                prompt = build_prompt(tokenizer, target)
                actual = len(tokenizer.encode(prompt))
                self.assertLessEqual(abs(actual - target) / target, 0.02)

    def test_cell_runs_two_warmups_and_five_measured_batches(self):
        def handler(request):
            payload = json.loads(request.content)
            self.assertTrue(payload["stream"])
            self.assertEqual(OUTPUT_TOKENS, payload["max_tokens"])
            events = [
                {
                    "choices": [
                        {
                            "delta": {"content": "基准"},
                            "finish_reason": None,
                        }
                    ]
                },
                {
                    "choices": [{"delta": {}, "finish_reason": "length"}],
                    "usage": {
                        "prompt_tokens": 512,
                        "completion_tokens": OUTPUT_TOKENS,
                        "total_tokens": 512 + OUTPUT_TOKENS,
                    },
                },
            ]
            body = "".join(
                f"data: {json.dumps(event)}\n\n" for event in events
            ) + "data: [DONE]\n\n"
            return httpx.Response(
                200,
                text=body,
                headers={
                    "content-type": "text/event-stream",
                    "X-Queue-Wait-Seconds": "0.001",
                },
            )

        client = httpx.Client(
            base_url="http://127.0.0.1:8001/v1/",
            transport=httpx.MockTransport(handler),
        )
        self.addCleanup(client.close)
        def memory():
            return {
                "gpu_used_bytes": 10,
                "gpu_total_bytes": 100,
                "gpu_name": "test",
                "driver_version": "test",
            }
        rows = run_benchmark_cell(
            client,
            BenchmarkCase(
                profile="e6_1_adapter_bf16",
                prompt="benchmark prompt",
                prompt_target_tokens=512,
                prompt_tokens=512,
                concurrency=2,
                git_revision="a" * 40,
                memory_reader=memory,
            ),
        )

        self.assertEqual(14, len(rows))
        self.assertEqual(4, sum(row["phase"] == "warmup" for row in rows))
        self.assertEqual(10, sum(row["phase"] == "measurement" for row in rows))
        self.assertTrue(all(row["completion_tokens"] == OUTPUT_TOKENS for row in rows))
        self.assertTrue(all(row["queue_seconds"] == 0.001 for row in rows))

    def test_summary_recomputes_matrix_and_fails_closed(self):
        samples = _deterministic_samples(
            "e6_1_adapter_bf16", peak=10 * 1024**3, throughput=30.0
        )
        summary = summarize_profile(samples)
        self.assertTrue(summary["gate_pass"])
        self.assertEqual(
            MEASURED_ROUNDS * sum(CONCURRENCY_LEVELS) * len(PROMPT_TARGETS),
            summary["measurement_sample_count"],
        )
        self.assertEqual(9, len(summary["cells"]))
        first = next(row for row in samples if row["phase"] == "measurement")
        first["http_status"] = 500
        failed = summarize_profile(samples)
        self.assertFalse(failed["gate_pass"])
        self.assertIn("cell_512_c1", failed["failures"])

    def test_checkpoint_detects_only_complete_cells_and_round_trips_atomically(self):
        samples = _deterministic_samples(
            "e6_1_adapter_bf16", peak=10 * 1024**3, throughput=30.0
        )
        self.assertEqual(9, len(_completed_cells(samples)))
        samples.pop()
        self.assertNotIn((8192, 4), _completed_cells(samples))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "samples.jsonl"
            _jsonl_write(path, samples)
            self.assertEqual(samples, _load_jsonl(path))
            self.assertEqual([], list(path.parent.glob("*.tmp")))

    def test_checkpoint_rejects_semantically_corrupt_or_duplicate_cells(self):
        base = _deterministic_samples(
            "e6_1_adapter_bf16", peak=10 * 1024**3, throughput=30.0
        )
        corruptions = {
            "profile": "e6_1_q4_k_m",
            "model_id": "other",
            "git_revision": "b" * 40,
            "git_dirty": True,
            "output_token_limit": 1,
            "http_status": 500,
            "error_code": "failed",
            "completion_tokens": 0,
            "tokens_per_second": 0.0,
            "gpu_peak_used_bytes": None,
        }
        for field, value in corruptions.items():
            with self.subTest(field=field):
                samples = [dict(row) for row in base]
                samples[0][field] = value
                completed = _completed_cells(
                    samples,
                    profile="e6_1_adapter_bf16",
                    git_revision="a" * 40,
                    git_dirty=False,
                )
                self.assertNotIn((512, 1), completed)
        samples = [dict(row) for row in base]
        first = next(
            row
            for row in samples
            if row["prompt_target_tokens"] == 512 and row["concurrency"] == 1
        )
        first["request_id"] = next(
            row["request_id"]
            for row in samples
            if row["prompt_target_tokens"] == 512
            and row["concurrency"] == 1
            and row is not first
        )
        self.assertNotIn((512, 1), _completed_cells(samples))

        numeric_corruptions = (
            ("queue_seconds", -1.0),
            ("queue_seconds", float("nan")),
            ("ttft_seconds", float("inf")),
            ("latency_seconds", True),
            ("tokens_per_second", float("nan")),
        )
        for field, value in numeric_corruptions:
            with self.subTest(field=field, value=value):
                samples = [dict(row) for row in base]
                samples[0][field] = value
                self.assertNotIn((512, 1), _completed_cells(samples))

    def test_atomic_write_failure_preserves_previous_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "samples.jsonl"
            path.write_text("original\n", encoding="utf-8")
            with mock.patch.object(Path, "replace", side_effect=OSError("replace failed")):
                with self.assertRaises(OSError):
                    _atomic_write_text(path, "replacement\n")
            self.assertEqual("original\n", path.read_text(encoding="utf-8"))
            self.assertEqual([], list(path.parent.glob("*.tmp")))

    def test_resume_identity_binds_output_root(self):
        manifest = {"profile": "e6_1_adapter_bf16", "output_root": "results/one"}
        _validate_resume_identity(manifest, dict(manifest))
        with self.assertRaisesRegex(ServingBenchmarkError, "identity does not match"):
            _validate_resume_identity(
                manifest,
                {"profile": "e6_1_adapter_bf16", "output_root": "results/two"},
            )

    def test_request_timeout_must_be_positive_and_finite(self):
        self.assertEqual(1200.0, _validate_request_timeout_seconds(1200))
        for value in (0, -1, float("nan"), float("inf"), True):
            with self.subTest(value=value):
                with self.assertRaises(ServingBenchmarkError):
                    _validate_request_timeout_seconds(value)

    def test_summary_rejects_prompt_error_missing_cell_and_warmup_substitution(self):
        samples = _deterministic_samples(
            "e6_1_adapter_bf16", peak=10 * 1024**3, throughput=30.0
        )
        samples = [
            row
            for row in samples
            if not (
                row["phase"] == "measurement"
                and row["prompt_target_tokens"] == 8192
                and row["concurrency"] == 4
            )
        ]
        samples[0]["prompt_tokens"] = 1
        summary = summarize_profile(samples)
        self.assertFalse(summary["gate_pass"])
        self.assertIn("cell_8192_c4", summary["failures"])

    def test_profile_comparison_enforces_vram_and_single_concurrency_speed(self):
        bf16 = summarize_profile(
            _deterministic_samples(
                "e6_1_adapter_bf16", peak=10 * 1024**3, throughput=30.0
            )
        )
        q4 = summarize_profile(
            _deterministic_samples(
                "e6_1_q4_k_m", peak=8 * 1024**3, throughput=20.0
            )
        )
        failed = compare_profiles(bf16, q4)
        self.assertFalse(failed["gate_pass"])
        self.assertIn("q4_vram_reduction", failed["failures"])
        self.assertIn("q4_throughput_512", failed["failures"])

        fixture = deterministic_fixture()
        self.assertTrue(fixture["gate_pass"])
        self.assertEqual(18, sum(len(value["cells"]) for value in fixture["profiles"].values()))

    def test_invalid_case_fails_before_requests(self):
        client = httpx.Client(base_url="http://127.0.0.1:8001/v1/")
        self.addCleanup(client.close)
        with self.assertRaises(ServingBenchmarkError):
            run_benchmark_cell(
                client,
                BenchmarkCase(
                    profile="e6_1_adapter_bf16",
                    prompt="bad",
                    prompt_target_tokens=512,
                    prompt_tokens=400,
                    concurrency=1,
                ),
            )


if __name__ == "__main__":
    unittest.main()
