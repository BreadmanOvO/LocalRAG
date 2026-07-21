import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from eval import eval_agent


class FakeCollection:
    def __init__(self, source_ids):
        self.metadatas = [{"source_id": source_id} for source_id in source_ids]
        self.calls = []

    def count(self):
        return len(self.metadatas)

    def get(self, *, include, limit, offset):
        self.calls.append({"include": include, "limit": limit, "offset": offset})
        return {
            "metadatas": self.metadatas[offset : offset + limit],
        }


class FakeAgent:
    def __init__(self, responses):
        self.responses = responses
        self.prompts = []

    def execute_stream(self, prompt):
        self.prompts.append(prompt)
        return iter(self.responses[prompt])


def write_registry(path: Path, source_ids):
    path.write_text(
        json.dumps([{"source_id": source_id} for source_id in source_ids]),
        encoding="utf-8",
    )


def write_dataset(path: Path, cases):
    path.write_text(
        json.dumps({"dataset_version": "test-v1", "cases": cases}),
        encoding="utf-8",
    )


def build_turn(prompt, required_tools, **overrides):
    turn = {
        "prompt": prompt,
        "required_tools": required_tools,
        "forbidden_tools": [],
        "expected_source_ids": [],
        "expected_answer_terms_any": [],
        "expected_answer_terms_all": [],
        "min_answer_chars": 1,
    }
    turn.update(overrides)
    return turn


class AgentEvalSchemaTests(unittest.TestCase):
    def test_repo_agent_eval_dataset_is_valid(self):
        dataset = eval_agent.load_agent_eval_dataset(eval_agent.DEFAULT_DATASET_PATH)

        self.assertEqual("agent-eval-v1", dataset["dataset_version"])
        self.assertEqual(8, len(dataset["cases"]))
        self.assertTrue(any(len(case["turns"]) > 1 for case in dataset["cases"]))

    def test_dataset_rejects_unknown_and_conflicting_tools(self):
        payload = {
            "dataset_version": "test",
            "cases": [
                {
                    "id": "case-1",
                    "category": "test",
                    "turns": [
                        build_turn(
                            "prompt",
                            ["unknown_tool"],
                            forbidden_tools=["unknown_tool"],
                        )
                    ],
                }
            ],
        }

        with self.assertRaisesRegex(ValueError, "unknown tools"):
            eval_agent.validate_agent_eval_dataset(payload)


class AgentEvalScoringTests(unittest.TestCase):
    def test_parse_agent_stream_separates_tools_from_answer(self):
        chunks = [
            "[工具] rag_search\n",
            "[工具结果] rag_search 已完成\n",
            "[工具] evidence_check\n",
            "最终",
            "回答",
        ]

        tools, answer, raw = eval_agent.parse_agent_stream(chunks)

        self.assertEqual(["rag_search", "evidence_check"], tools)
        self.assertEqual("最终回答", answer)
        self.assertEqual(chunks, raw)

    def test_evaluate_turn_checks_order_forbidden_tools_and_answer_contract(self):
        turn = build_turn(
            "prompt",
            ["rag_search", "evidence_check"],
            forbidden_tools=["clarify_question"],
            expected_source_ids=["paper-001"],
            expected_answer_terms_any=["候选证据"],
            expected_answer_terms_all=["paper-001", "证据"],
            min_answer_chars=10,
        )

        passed = eval_agent.evaluate_turn(
            turn,
            ["rag_search", "evidence_check"],
            "paper-001 找到候选证据片段。",
        )
        failed = eval_agent.evaluate_turn(
            turn,
            ["evidence_check", "rag_search", "clarify_question"],
            "内容不足",
        )

        self.assertTrue(passed["turn_pass"])
        self.assertFalse(failed["tool_order_pass"])
        self.assertFalse(failed["forbidden_tools_pass"])
        self.assertFalse(failed["answer_contract_pass"])

    def test_summary_gate_requires_corpus_and_behavior_thresholds(self):
        rows = [
            {
                "case_pass": True,
                "turns": [
                    {
                        "evaluation": {
                            "tool_contract_pass": True,
                            "answer_contract_pass": True,
                            "forbidden_tools_pass": True,
                        }
                    }
                ],
            }
        ]

        passed = eval_agent.summarize_agent_eval(
            rows,
            corpus_manifest={"coverage_ratio": 1.0},
        )
        failed = eval_agent.summarize_agent_eval(
            rows,
            corpus_manifest={"coverage_ratio": 0.5},
        )

        self.assertTrue(passed["gate_pass"])
        self.assertFalse(failed["gate_pass"])
        self.assertFalse(failed["gate_checks"]["corpus_coverage"])


class AgentEvalRunnerTests(unittest.TestCase):
    def test_build_corpus_manifest_reads_metadata_in_batches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "registry.json"
            write_registry(registry_path, ["source-1", "source-2", "source-3"])
            collection = FakeCollection(["source-1", "source-2", "extra-source"])

            with mock.patch.object(eval_agent, "CHROMA_BATCH_SIZE", 2):
                manifest = eval_agent.build_corpus_manifest(
                    registry_path=registry_path,
                    persist_directory=root / "chroma",
                    collection_name="rag",
                    collection=collection,
                )

        self.assertEqual(3, manifest["registry_source_count"])
        self.assertEqual(2, manifest["covered_source_count"])
        self.assertEqual(0.667, manifest["coverage_ratio"])
        self.assertEqual(["source-3"], manifest["missing_source_ids"])
        self.assertEqual(["extra-source"], manifest["extra_source_ids"])
        self.assertEqual([0, 2], [call["offset"] for call in collection.calls])

    def test_run_agent_eval_reuses_agent_across_turns_and_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "registry.json"
            dataset_path = root / "dataset.json"
            out_dir = root / "results"
            write_registry(registry_path, ["paper-001"])
            first_prompt = "inspect"
            second_prompt = "expand"
            write_dataset(
                dataset_path,
                [
                    {
                        "id": "case-1",
                        "category": "followup",
                        "turns": [
                            build_turn(
                                first_prompt,
                                ["inspect_source"],
                                expected_source_ids=["paper-001"],
                            ),
                            build_turn(
                                second_prompt,
                                ["expand_context"],
                                expected_source_ids=["paper-001"],
                            ),
                        ],
                    }
                ],
            )
            fake_agent = FakeAgent(
                {
                    first_prompt: ["[工具] inspect_source\n", "paper-001 inspected"],
                    second_prompt: ["[工具] expand_context\n", "paper-001 expanded"],
                }
            )
            agent_factory = mock.Mock(return_value=fake_agent)

            result = eval_agent.run_agent_eval(
                dataset_path=dataset_path,
                registry_path=registry_path,
                persist_directory=root / "chroma",
                out_dir=out_dir,
                run_id="agent-eval-test",
                agent_factory=agent_factory,
                collection=FakeCollection(["paper-001"]),
            )

            self.assertTrue((result["run_dir"] / "manifest.json").exists())
            self.assertTrue((result["run_dir"] / "predictions.json").exists())
            self.assertTrue((result["run_dir"] / "summary.json").exists())

        agent_factory.assert_called_once()
        self.assertEqual([first_prompt, second_prompt], fake_agent.prompts)
        self.assertTrue(result["summary"]["gate_pass"])
        self.assertTrue(result["predictions"][0]["case_pass"])

    def test_stale_corpus_skips_agent_execution_and_fails_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "registry.json"
            dataset_path = root / "dataset.json"
            write_registry(registry_path, ["paper-001", "paper-002"])
            write_dataset(
                dataset_path,
                [
                    {
                        "id": "case-1",
                        "category": "inspect",
                        "turns": [build_turn("inspect", ["inspect_source"])],
                    }
                ],
            )
            agent_factory = mock.Mock()

            result = eval_agent.run_agent_eval(
                dataset_path=dataset_path,
                registry_path=registry_path,
                persist_directory=root / "chroma",
                out_dir=root / "results",
                run_id="agent-eval-stale",
                agent_factory=agent_factory,
                collection=FakeCollection(["paper-001"]),
            )

        agent_factory.assert_not_called()
        self.assertTrue(result["summary"]["skipped"])
        self.assertFalse(result["summary"]["gate_pass"])
        self.assertFalse(result["summary"]["gate_checks"]["evaluation_executed"])

    def test_agent_initialization_error_is_persisted_as_failed_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "registry.json"
            dataset_path = root / "dataset.json"
            write_registry(registry_path, ["paper-001"])
            write_dataset(
                dataset_path,
                [
                    {
                        "id": "case-1",
                        "category": "inspect",
                        "turns": [build_turn("inspect", ["inspect_source"])],
                    }
                ],
            )

            result = eval_agent.run_agent_eval(
                dataset_path=dataset_path,
                registry_path=registry_path,
                persist_directory=root / "chroma",
                out_dir=root / "results",
                run_id="agent-eval-init-error",
                agent_factory=mock.Mock(side_effect=RuntimeError("model unavailable")),
                collection=FakeCollection(["paper-001"]),
            )

        turn = result["predictions"][0]["turns"][0]
        self.assertEqual("RuntimeError: model unavailable", turn["error"])
        self.assertFalse(result["predictions"][0]["case_pass"])
        self.assertFalse(result["summary"]["gate_pass"])

    def test_run_agent_eval_rejects_non_positive_max_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "registry.json"
            dataset_path = root / "dataset.json"
            write_registry(registry_path, ["paper-001"])
            write_dataset(
                dataset_path,
                [
                    {
                        "id": "case-1",
                        "category": "inspect",
                        "turns": [build_turn("inspect", ["inspect_source"])],
                    }
                ],
            )

            with self.assertRaisesRegex(ValueError, "max_cases"):
                eval_agent.run_agent_eval(
                    dataset_path=dataset_path,
                    registry_path=registry_path,
                    persist_directory=root / "chroma",
                    out_dir=root / "results",
                    max_cases=0,
                    agent_factory=mock.Mock(),
                    collection=FakeCollection(["paper-001"]),
                )

    def test_run_agent_eval_rejects_unknown_case_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry_path = root / "registry.json"
            dataset_path = root / "dataset.json"
            write_registry(registry_path, ["paper-001"])
            write_dataset(
                dataset_path,
                [
                    {
                        "id": "case-1",
                        "category": "inspect",
                        "turns": [build_turn("inspect", ["inspect_source"])],
                    }
                ],
            )

            with self.assertRaisesRegex(ValueError, "unknown case ids"):
                eval_agent.run_agent_eval(
                    dataset_path=dataset_path,
                    registry_path=registry_path,
                    persist_directory=root / "chroma",
                    out_dir=root / "results",
                    case_ids=["missing-case"],
                    agent_factory=mock.Mock(),
                    collection=FakeCollection(["paper-001"]),
                )


if __name__ == "__main__":
    unittest.main()
