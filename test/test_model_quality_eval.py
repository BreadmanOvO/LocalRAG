from __future__ import annotations

from contextlib import ExitStack
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import httpx

from eval.eval_model_quality import (
    MODEL_ID,
    PROFILE_NAMES,
    QualityProfile,
    compare_quality_stage,
    deterministic_fixture,
    run_quality_profile,
    summarize_model_quality,
)
from model_deployment.manifest import build_manifest, write_manifest


class ModelQualityEvalTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name).resolve()
        self.dataset = self.root / "data/evaluation/gold/generation_eval_set.json"
        self.dataset.parent.mkdir(parents=True)
        rows = []
        for index in range(10):
            rows.append(
                {
                    "id": f"case-{index:02d}",
                    "question": "资料说明了什么？",
                    "reference_answer": "资料说明系统使用证据回答。",
                    "evidence": [
                        {
                            "quote": "系统使用证据回答。",
                            "source_id": f"source-{index:02d}",
                            "locator": "page=1",
                        }
                    ],
                    "metadata": {"expected_behavior": "answer"},
                }
            )
        self.dataset.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
        artifact = self.root / "artifact.gguf"
        artifact.write_text("x", encoding="utf-8")
        manifest = build_manifest(
            self.root,
            [artifact.relative_to(self.root)],
            kind="model-input",
        )
        self.manifest = self.root / "model_deployment/manifests/model.json"
        write_manifest(self.manifest, manifest)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(
            mock.patch(
                "eval.eval_model_quality._git_state",
                return_value=("a" * 40, False),
            )
        )

    def _client(self):
        def handler(request):
            if request.url.path.endswith("/models"):
                return httpx.Response(200, json={"data": [{"id": MODEL_ID}]})
            payload = json.loads(request.content)
            self.assertEqual(0, payload["temperature"])
            self.assertEqual(256, payload["max_tokens"])
            source = payload["messages"][0]["content"].split("source_id=", 1)[1].split()[0]
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {
                                "content": f"系统使用证据回答。\n\n引用：\n- {source} page=1"
                            }
                        }
                    ]
                },
            )

        return httpx.Client(
            base_url="http://127.0.0.1:8001/v1/",
            transport=httpx.MockTransport(handler),
        )

    def test_endpoint_profile_runs_complete_ten_case_gate(self):
        output = run_quality_profile(
            QualityProfile(
                name="adapter_bf16",
                repo_root=self.root,
                manifest_path=self.manifest,
                endpoint="http://127.0.0.1:8001/v1",
                client=self._client(),
            ),
            self.dataset,
            self.root / "results",
        )

        self.assertTrue(output["summary"]["gate_pass"])
        self.assertEqual(10, output["summary"]["request_success_count"])
        self.assertEqual(1.0, output["summary"]["evidence_source_hit_ratio"])
        self.assertEqual(10, len(output["prediction_ids"]))

    def test_stage_comparison_fails_on_dirty_or_incomplete_run(self):
        fixture = self._runs()
        fixture["merged_bf16"]["manifest"]["git_dirty"] = True

        result = compare_quality_stage(
            fixture["adapter_bf16"],
            fixture["merged_bf16"],
            "adapter_to_merged",
        )

        self.assertFalse(result["gate_pass"])
        self.assertIn("git_dirty", result["failures"])

    def test_summary_requires_all_profiles_and_stops_at_first_stage(self):
        runs = self._runs()
        missing = dict(runs)
        missing.pop("gguf_q4_k_m")
        self.assertFalse(summarize_model_quality(missing)["gate_pass"])

        runs["gguf_f16"]["summary"]["gate_pass"] = False
        output = summarize_model_quality(runs)
        self.assertFalse(output["gate_pass"])
        self.assertEqual("merged_to_gguf_f16", output["first_failed_stage"])

    def test_deterministic_fixture_passes_all_three_stages(self):
        output = deterministic_fixture()
        self.assertTrue(output["gate_pass"])
        self.assertEqual(3, len(output["stages"]))

    @staticmethod
    def _runs():
        ids = [f"case-{index:02d}" for index in range(10)]
        runs = {}
        for name in PROFILE_NAMES:
            runs[name] = {
                "profile": name,
                "summary": {"gate_pass": True},
                "prediction_ids": ids,
                "manifest": {
                    "model_id": MODEL_ID,
                    "dataset_sha256": "b" * 64,
                    "generation": {
                        "temperature": 0,
                        "max_tokens": 256,
                        "enable_thinking": False,
                    },
                    "git_dirty": False,
                },
            }
        return runs


if __name__ == "__main__":
    unittest.main()
