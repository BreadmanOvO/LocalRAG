from __future__ import annotations

import json
import unittest

import httpx

from eval.benchmark_serving import (
    BenchmarkCase,
    CONCURRENCY_LEVELS,
    MEASURED_ROUNDS,
    OUTPUT_TOKENS,
    PROMPT_TARGETS,
    ServingBenchmarkError,
    _deterministic_samples,
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
