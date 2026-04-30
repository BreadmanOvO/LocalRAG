import ast
import json
import re
import shlex
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from eval import eval_chunking
from eval import eval_judge_formal_run as judge_formal_run
from eval import eval_llm_judge as judge_runner
from eval import eval_ragas as ragas_runner

formal_runner = judge_formal_run
from eval.eval_llm_judge import summarize_judgements
from eval.eval_ragas import (
    build_prediction_record,
    build_session_id,
    require_runtime_config,
    run_baseline,
    summarize_predictions,
    write_json,
)


class JudgeFormalRunTests(unittest.TestCase):
    def test_build_judge_formal_run_returns_paths_for_all_bundles(self):
        paths = judge_formal_run.build_judge_formal_run(
            dataset_path=Path('data/evaluation/gold/gold_set.json'),
            baseline_run_dir=Path('results/baseline_eval/gold_set-20260429-120000'),
            chunking_run_dir=Path('results/chunking_eval/gold_set-20260429-120100'),
            judge_run_dir=Path('results/judge_eval/predictions-vs-predictions-20260429-120200'),
        )

        self.assertEqual(paths['dataset_path'], Path('data/evaluation/gold/gold_set.json'))
        self.assertEqual(
            paths['baseline_predictions_path'],
            Path('results/baseline_eval/gold_set-20260429-120000/predictions.json'),
        )
        self.assertEqual(
            paths['candidate_predictions_path'],
            Path('results/chunking_eval/gold_set-20260429-120100/doc_type_aware/predictions.json'),
        )
        self.assertEqual(
            paths['report_path'],
            Path('results/judge_eval/predictions-vs-predictions-20260429-120200/test_report.md'),
        )

    def test_run_formal_judge_pipeline_calls_existing_runners(self):
        root = Path('/tmp/formal-run')
        dataset_path = root / 'gold_set.json'
        baseline_out_dir = root / 'baseline_eval'
        chunking_out_dir = root / 'chunking_eval'
        judge_out_dir = root / 'judge_eval'
        baseline_existing_run_dir = baseline_out_dir / 'baseline-old'
        baseline_run_dir = baseline_out_dir / 'baseline-run'
        chunking_existing_run_dir = chunking_out_dir / 'chunking-old'
        chunking_run_dir = chunking_out_dir / 'chunking-run'
        judge_existing_run_dir = judge_out_dir / 'judge-old'
        judge_run_dir = judge_out_dir / 'judge-run'

        baseline_summary = {'sample_count': 2}
        chunking_summary = {'sample_count': 2}
        judge_summary = {'sample_count': 2}

        with (
            mock.patch.object(formal_runner, 'list_run_dirs') as list_run_dirs,
            mock.patch.object(formal_runner.ragas_runner, 'run_baseline_to_dir', return_value=baseline_summary) as baseline_run,
            mock.patch.object(formal_runner.eval_chunking, 'main', return_value=chunking_summary) as chunking_main,
            mock.patch.object(formal_runner.judge_runner, 'run_pairwise_judge_to_dir', return_value=judge_summary) as judge_run,
            mock.patch.object(formal_runner, 'write_test_report') as write_report,
            mock.patch.object(formal_runner, 'verify_formal_run_artifacts', return_value=[]),
            mock.patch.object(Path, 'exists', return_value=True),
        ):
            list_run_dirs.side_effect = [
                [baseline_existing_run_dir],
                [baseline_existing_run_dir, baseline_run_dir],
                [chunking_existing_run_dir],
                [chunking_existing_run_dir, chunking_run_dir],
                [judge_existing_run_dir],
                [judge_existing_run_dir, judge_run_dir],
            ]
            result = formal_runner.run_formal_judge_pipeline(
                dataset_path=dataset_path,
                baseline_out_dir=baseline_out_dir,
                chunking_out_dir=chunking_out_dir,
                judge_out_dir=judge_out_dir,
            )

        baseline_run.assert_called_once_with(dataset_path, baseline_out_dir)
        chunking_main.assert_called_once_with()
        judge_run.assert_called_once()
        write_report.assert_called_once()
        self.assertEqual(result['baseline_summary'], baseline_summary)
        self.assertEqual(result['chunking_summary'], chunking_summary)
        self.assertEqual(result['judge_summary'], judge_summary)
        self.assertEqual(result['verification_failures'], [])
        self.assertEqual(result['run']['judge_run_dir'], judge_run_dir)

    def test_list_run_dirs_ignores_non_run_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            stores_dir = parent / 'stores'
            stores_dir.mkdir()
            (stores_dir / 'nested').mkdir()
            run_dir = parent / 'gold_set-20260430-161506'
            run_dir.mkdir()
            (run_dir / 'manifest.json').write_text('{}', encoding='utf-8')

            self.assertEqual([run_dir], formal_runner.list_run_dirs(parent))

    def test_discover_new_run_dir_returns_only_new_directory(self):
        parent = Path('/tmp/run-parent')
        previous_run_dirs = [parent / 'older-run']

        with mock.patch.object(
            formal_runner,
            'list_run_dirs',
            return_value=[parent / 'older-run', parent / 'fresh-run'],
        ):
            result = formal_runner.discover_new_run_dir(parent, previous_run_dirs)

        self.assertEqual(parent / 'fresh-run', result)

    def test_discover_new_run_dir_raises_when_new_directory_count_is_not_one(self):
        parent = Path('/tmp/run-parent')

        with mock.patch.object(formal_runner, 'list_run_dirs', return_value=[parent / 'older-run']):
            with self.assertRaisesRegex(ValueError, r'Expected exactly one new run directory'):
                formal_runner.discover_new_run_dir(parent, [parent / 'older-run'])

    def test_eval_judge_formal_run_main_returns_pipeline_summary(self):
        expected_summary = {
            'baseline_summary': {'sample_count': 30},
            'chunking_summary': {'sample_count': 30},
            'judge_summary': {'sample_count': 30, 'candidate_win_count': 12},
            'verification_failures': [],
            'run': {'judge_run_dir': Path('/tmp/judge-run')},
        }

        with (
            mock.patch.object(formal_runner, 'run_formal_judge_pipeline', return_value=expected_summary) as run_pipeline,
            mock.patch.object(
                sys,
                'argv',
                [
                    'eval_judge_formal_run.py',
                    '--dataset',
                    'custom-data.json',
                    '--baseline-out-dir',
                    'baseline-results',
                    '--chunking-out-dir',
                    'chunking-results',
                    '--judge-out-dir',
                    'judge-results',
                ],
            ),
        ):
            result = formal_runner.main()

        run_pipeline.assert_called_once_with(
            dataset_path=Path('custom-data.json'),
            baseline_out_dir=Path('baseline-results'),
            chunking_out_dir=Path('chunking-results'),
            judge_out_dir=Path('judge-results'),
        )
        self.assertEqual(expected_summary['judge_summary'], result['judge_summary'])

    def test_verify_formal_run_artifacts_checks_required_files_and_sample_count(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            run = judge_formal_run.build_judge_formal_run(
                dataset_path=temp_dir / 'gold_set.json',
                baseline_run_dir=temp_dir / 'baseline_eval' / 'baseline-run',
                chunking_run_dir=temp_dir / 'chunking_eval' / 'chunking-run',
                judge_run_dir=temp_dir / 'judge_eval' / 'judge-run',
            )

            missing_failures = judge_formal_run.verify_formal_run_artifacts(run)
            self.assertEqual(
                missing_failures,
                [
                    f"missing baseline predictions: {run['baseline_predictions_path']}",
                    f"missing baseline metrics: {run['baseline_metrics_path']}",
                    f"missing baseline manifest: {run['baseline_manifest_path']}",
                    f"missing candidate predictions: {run['candidate_predictions_path']}",
                    f"missing candidate metrics: {run['candidate_metrics_path']}",
                    f"missing chunking manifest: {run['chunking_manifest_path']}",
                    f"missing chunking comparison summary: {run['chunking_summary_path']}",
                    f"missing judge judgements: {run['judge_judgements_path']}",
                    f"missing judge summary: {run['judge_summary_path']}",
                    f"missing judge manifest: {run['judge_manifest_path']}",
                ],
            )

            for key in (
                'baseline_predictions_path',
                'baseline_metrics_path',
                'baseline_manifest_path',
                'candidate_predictions_path',
                'candidate_metrics_path',
                'chunking_manifest_path',
                'chunking_summary_path',
                'judge_judgements_path',
            ):
                run[key].parent.mkdir(parents=True, exist_ok=True)
                run[key].write_text('{}', encoding='utf-8')

            run['judge_summary_path'].write_text(json.dumps({'sample_count': 29}), encoding='utf-8')
            run['judge_manifest_path'].write_text(
                json.dumps(
                    {
                        'judge_prompt_version': 'stale-version',
                        'baseline_predictions_path': str(temp_dir / 'wrong-baseline.json'),
                        'candidate_predictions_path': str(temp_dir / 'wrong-candidate.json'),
                    }
                ),
                encoding='utf-8',
            )

            failures = judge_formal_run.verify_formal_run_artifacts(run)
            self.assertEqual(
                failures,
                [
                    'judge summary sample_count must be 30',
                    'judge manifest must include the current judge_prompt_version',
                    'judge manifest baseline_predictions_path must point to the fresh baseline run',
                    'judge manifest candidate_predictions_path must point to the fresh candidate run',
                ],
            )

            run['judge_summary_path'].write_text(json.dumps({'sample_count': 30}), encoding='utf-8')
            run['judge_manifest_path'].write_text(
                json.dumps(
                    {
                        'judge_prompt_version': judge_runner.JUDGE_PROMPT_VERSION,
                        'baseline_predictions_path': str(run['baseline_predictions_path']),
                        'candidate_predictions_path': str(run['candidate_predictions_path']),
                    }
                ),
                encoding='utf-8',
            )

            self.assertEqual([], judge_formal_run.verify_formal_run_artifacts(run))

    def test_write_test_report_outputs_shell_safe_replay_commands_and_verification_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run = formal_runner.build_judge_formal_run(
                dataset_path=Path('data/evaluation/gold set.json'),
                baseline_run_dir=root / 'baseline eval' / 'gold_set-20260429-120000',
                chunking_run_dir=root / 'chunking eval' / 'gold_set-20260429-120100',
                judge_run_dir=root / 'judge eval' / 'predictions-vs-predictions-20260429-120200',
            )

            report_path = formal_runner.write_test_report(
                run=run,
                baseline_summary={'sample_count': 30, 'answered_ratio': 1.0},
                chunking_summary={
                    'run_id': 'gold_set-20260429-120100',
                    'baseline': {'evidence_source_hit_ratio': 0.4},
                    'doc_type_aware': {'evidence_source_hit_ratio': 0.6},
                },
                judge_summary={'sample_count': 30, 'candidate_win_count': 12, 'baseline_win_count': 8, 'tie_count': 10},
                verification_failures=['judge summary sample_count must be 30', 'missing judge manifest: /tmp/fake/manifest.json'],
            )

            report_text = run['report_path'].read_text(encoding='utf-8')
            commands = re.findall(r"- `([^`]+)`", report_text)

        self.assertEqual(run['report_path'], report_path)
        self.assertIn('# Judge formal run test report', report_text)
        self.assertIn('candidate_win_count', report_text)
        self.assertEqual(3, len(commands))
        self.assertIn(str(run['dataset_path'].resolve()), report_text)
        self.assertIn(str(run['baseline_run_dir'].parent.resolve()), report_text)
        self.assertIn(str(run['chunking_run_dir'].parent.resolve()), report_text)
        self.assertIn(str(run['judge_run_dir'].parent.resolve()), report_text)
        self.assertIn(str(run['candidate_predictions_path'].resolve()), report_text)
        self.assertIn(run['baseline_run_dir'].name, report_text)
        self.assertIn(run['chunking_run_dir'].name, report_text)
        self.assertIn(run['judge_run_dir'].name, report_text)

        expected_python_fragments = [
            [
                'from pathlib import Path',
                'import eval.eval_ragas as module',
                f"module.build_run_id = lambda *_: {run['baseline_run_dir'].name!r}",
                f"Path({str(run['dataset_path'].resolve())!r})",
                f"Path({str(run['baseline_run_dir'].parent.resolve())!r})",
                'module.run_baseline_to_dir',
            ],
            [
                'from eval import eval_chunking as module',
                f"module.build_run_id = lambda *_: {run['chunking_run_dir'].name!r}",
                f"sys.argv = {repr(['eval_chunking.py', '--dataset', str(run['dataset_path'].resolve()), '--out-dir', str(run['chunking_run_dir'].parent.resolve())])}",
                'module.main()',
            ],
            [
                'from pathlib import Path',
                'import eval.eval_llm_judge as module',
                f"module.build_run_id = lambda *_: {run['judge_run_dir'].name!r}",
                f"Path({str(run['baseline_predictions_path'].resolve())!r})",
                f"Path({str(run['candidate_predictions_path'].resolve())!r})",
                f"Path({str(run['judge_run_dir'].parent.resolve())!r})",
                'module.run_pairwise_judge_to_dir',
            ],
        ]

        expected_interpreter = str(Path(sys.executable))
        for command, expected_fragments in zip(commands, expected_python_fragments, strict=True):
            subprocess.run(
                ['bash', '-n', '-c', command],
                check=True,
                capture_output=True,
                text=True,
            )
            parts = shlex.split(command)
            self.assertEqual(['cd', str(formal_runner.REPO_ROOT), '&&', expected_interpreter, '-c'], parts[:5])
            self.assertEqual(6, len(parts))
            python_snippet = parts[5]
            ast.parse(python_snippet)
            for fragment in expected_fragments:
                self.assertIn(fragment, python_snippet)

        self.assertIn('Result: **FAIL**', report_text)
        self.assertIn('- Failures:', report_text)
        self.assertIn('  - judge summary sample_count must be 30', report_text)
        self.assertIn('  - missing judge manifest: /tmp/fake/manifest.json', report_text)


class EvalRunnerTests(unittest.TestCase):
    def test_build_prediction_record_includes_required_fields(self):
        record = build_prediction_record(
            {
                "id": "sample-1",
                "question": "What is LocalRAG?",
                "reference_answer": "A local retrieval augmented generation project.",
                "evidence": [{"quote": "LocalRAG", "source_id": "doc-1", "locator": "p1"}],
                "metadata": {"source": "gold"},
            },
            {
                "answer": "A local retrieval augmented generation project.",
                "retrieved_context": "ctx-1",
                "retrieved_rows": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
                "retrieval_debug_candidates": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
            },
        )

        self.assertEqual(record["id"], "sample-1")
        self.assertEqual(record["answer"], "A local retrieval augmented generation project.")
        self.assertEqual(record["retrieved_context"], "ctx-1")
        self.assertEqual(record["retrieved_rows"][0]["source_id"], "doc-1")
        self.assertEqual(record["evidence"][0]["locator"], "p1")
        self.assertEqual(
            record["reference_answer"],
            "A local retrieval augmented generation project.",
        )

    def test_build_session_id_isolated_per_sample(self):
        self.assertEqual(build_session_id({"id": "sample-1"}), "eval-session-sample-1")
        self.assertEqual(build_session_id({"id": 42}), "eval-session-42")

    def test_summarize_predictions_counts_answered_context_and_evidence_hits(self):
        summary = summarize_predictions(
            [
                {
                    "id": 1,
                    "answer": "Answer 1",
                    "retrieved_context": "C1",
                    "retrieved_rows": [{"source_id": "doc-1", "locator": "p1"}],
                    "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}],
                },
                {
                    "id": 2,
                    "answer": "",
                    "retrieved_context": "",
                    "retrieved_rows": [{"source_id": "doc-x", "locator": "p9"}],
                    "evidence": [{"quote": "q2", "source_id": "doc-2", "locator": "p2"}],
                },
                {
                    "id": 3,
                    "answer": "   ",
                    "retrieved_context": "C2",
                    "retrieved_rows": [{"source_id": "doc-3", "locator": "p3   sec=1"}],
                    "evidence": [{"quote": "q3", "source_id": "doc-9", "locator": "p3 sec=1"}],
                },
            ]
        )

        self.assertEqual(summary["sample_count"], 3)
        self.assertEqual(summary["answered_count"], 1)
        self.assertEqual(summary["answered_ratio"], 0.333)
        self.assertEqual(summary["context_hit_count"], 2)
        self.assertEqual(summary["context_hit_ratio"], 0.667)
        self.assertEqual(summary["evidence_source_hit_count"], 1)
        self.assertEqual(summary["evidence_source_hit_ratio"], 0.333)
        self.assertEqual(summary["evidence_locator_hit_count"], 2)
        self.assertEqual(summary["evidence_locator_hit_ratio"], 0.667)

    def test_summarize_predictions_adds_objective_metrics(self):
        summary = summarize_predictions(
            [
                {
                    "id": "sample-1",
                    "reference_answer": "Apollo planning module",
                    "answer": "Apollo planning module",
                    "retrieved_context": "ctx-1",
                    "retrieved_rows": [{"source_id": "doc-1", "locator": "p1"}, {"source_id": "doc-2", "locator": "p2"}],
                    "retrieval_debug_candidates": [{"source_id": "doc-1"}, {"source_id": "doc-2"}],
                    "evidence": [{"quote": "Apollo planning module", "source_id": "doc-1", "locator": "p1"}],
                },
                {
                    "id": "sample-2",
                    "reference_answer": "Perception safety report",
                    "answer": " perception   safety report ",
                    "retrieved_context": "",
                    "retrieved_rows": [],
                    "retrieval_debug_candidates": [],
                    "evidence": [{"quote": "Perception safety report", "source_id": "doc-2", "locator": "p2"}],
                },
            ]
        )

        self.assertEqual(1, summary["exact_match_count"])
        self.assertEqual(0.5, summary["exact_match_ratio"])
        self.assertEqual(2, summary["normalized_exact_match_count"])
        self.assertEqual(1.0, summary["normalized_exact_match_ratio"])
        self.assertEqual(2, summary["retrieved_row_count"])
        self.assertEqual(1.0, summary["avg_retrieved_row_count"])
        self.assertEqual(2, summary["retrieval_debug_candidate_count"])
        self.assertEqual(1.0, summary["avg_retrieval_debug_candidate_count"])
        self.assertEqual(2, summary["reference_substring_hit_count"])
        self.assertEqual(1.0, summary["reference_substring_hit_ratio"])

    def test_summarize_judgements_counts_winners_and_ties(self):
        summary = summarize_judgements(
            [
                {"id": "sample-1", "winner": "candidate", "reason": "c1"},
                {"id": "sample-2", "winner": "baseline", "reason": "b1"},
                {"id": "sample-3", "winner": "tie", "reason": "t1"},
                {"id": "sample-4", "winner": "candidate", "reason": "c2"},
            ]
        )

        self.assertEqual(summary["sample_count"], 4)
        self.assertEqual(summary["candidate_win_count"], 2)
        self.assertEqual(summary["baseline_win_count"], 1)
        self.assertEqual(summary["tie_count"], 1)

    def test_run_pairwise_judge_aligns_by_id_and_uses_llm_verdicts(self):
        baseline_predictions = [
            {
                "id": "sample-1",
                "question": "Q1",
                "reference_answer": "R1",
                "answer": "baseline-1",
                "retrieved_rows": [{"source_id": "doc-x", "locator": "p9"}],
                "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}],
                "metadata": {"topic": "rag"},
            },
            {
                "id": "sample-2",
                "question": "Q2",
                "reference_answer": "R2",
                "answer": "baseline-2",
                "retrieved_rows": [{"source_id": "doc-2", "locator": "p2"}],
                "evidence": [{"quote": "q2", "source_id": "doc-2", "locator": "p2"}],
                "metadata": {"topic": "eval"},
            },
        ]
        candidate_predictions = [
            {
                "id": "sample-2",
                "question": "Q2",
                "reference_answer": "R2",
                "answer": "candidate-2",
                "retrieved_rows": [{"source_id": "doc-x", "locator": "p9"}],
                "evidence": [{"quote": "q2", "source_id": "doc-2", "locator": "p2"}],
                "metadata": {"topic": "eval"},
            },
            {
                "id": "sample-1",
                "question": "Q1",
                "reference_answer": "R1",
                "answer": "candidate-1",
                "retrieved_rows": [{"source_id": "doc-1", "locator": "p1"}],
                "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}],
                "metadata": {"topic": "rag"},
            },
        ]

        fake_runtime_config = types.SimpleNamespace(
            api_key="test-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            chat_model_name="qwen3-max",
            embedding_model_name="text-embedding-v4",
        )
        fake_chat_model = mock.Mock()
        fake_chat_model.invoke.side_effect = [
            '{"winner":"candidate","reason":"candidate answer uses better evidence"}',
            '{"winner":"baseline","reason":"baseline answer is more accurate"}',
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            output_path = temp_dir / "judgements.json"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with (
                mock.patch.object(judge_runner, "load_runtime_config", return_value=fake_runtime_config),
                mock.patch.object(judge_runner, "build_chat_model", return_value=fake_chat_model) as mock_chat,
            ):
                summary = judge_runner.run_pairwise_judge(baseline_path, candidate_path, output_path)

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(2, summary["sample_count"])
            self.assertEqual(1, payload["summary"]["candidate_win_count"])
            self.assertEqual(1, payload["summary"]["baseline_win_count"])
            self.assertEqual("sample-1", payload["rows"][0]["id"])
            self.assertEqual("baseline-1", payload["rows"][0]["baseline_answer"])
            self.assertEqual("candidate-1", payload["rows"][0]["candidate_answer"])
            self.assertEqual("candidate", payload["rows"][0]["winner"])
            self.assertEqual("candidate answer uses better evidence", payload["rows"][0]["reason"])
            self.assertEqual("baseline", payload["rows"][1]["winner"])
            mock_chat.assert_called_once_with(fake_runtime_config, temperature=0)
            self.assertEqual(2, fake_chat_model.invoke.call_count)

    def test_run_pairwise_judge_builds_model_with_deterministic_settings(self):
        baseline_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "b1", "retrieved_rows": [], "evidence": []}]
        candidate_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "c1", "retrieved_rows": [], "evidence": []}]
        fake_runtime_config = types.SimpleNamespace(
            provider="modelscope",
            api_key="test-key",
            base_url="https://api-inference.modelscope.cn/v1",
            chat_model_name="Qwen/Qwen2.5-72B-Instruct",
            embedding_model_name="Qwen/Qwen3-Embedding-8B",
        )
        fake_chat_model = mock.Mock()
        fake_chat_model.invoke.return_value = '{"winner":"candidate","reason":"candidate is more accurate"}'

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            output_path = temp_dir / "judgements.json"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with (
                mock.patch.object(judge_runner, "load_runtime_config", return_value=fake_runtime_config),
                mock.patch.object(judge_runner, "build_chat_model", return_value=fake_chat_model) as mock_chat,
            ):
                judge_runner.run_pairwise_judge(baseline_path, candidate_path, output_path)

            mock_chat.assert_called_once_with(fake_runtime_config, temperature=0)

    def test_run_pairwise_judge_accepts_wrapped_json_response(self):
        baseline_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "b1", "retrieved_rows": [], "evidence": []}]
        candidate_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "c1", "retrieved_rows": [], "evidence": []}]
        fake_runtime_config = types.SimpleNamespace(
            provider="modelscope",
            api_key="test-key",
            base_url="https://api-inference.modelscope.cn/v1",
            chat_model_name="Qwen/Qwen2.5-72B-Instruct",
            embedding_model_name="Qwen/Qwen3-Embedding-8B",
        )
        fake_chat_model = mock.Mock()
        fake_chat_model.invoke.return_value = "裁判结果如下\n{\"winner\":\"candidate\",\"reason\":\"candidate is more faithful to the reference answer\"}\n谢谢"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            output_path = temp_dir / "judgements.json"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with (
                mock.patch.object(judge_runner, "load_runtime_config", return_value=fake_runtime_config),
                mock.patch.object(judge_runner, "build_chat_model", return_value=fake_chat_model),
            ):
                judge_runner.run_pairwise_judge(baseline_path, candidate_path, output_path)

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual("candidate", payload["rows"][0]["winner"])
            self.assertEqual(
                "candidate is more faithful to the reference answer",
                payload["rows"][0]["reason"],
            )

    def test_run_pairwise_judge_rejects_mismatched_ids(self):
        baseline_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "b1"}]
        candidate_predictions = [{"id": "sample-2", "question": "Q2", "reference_answer": "R2", "answer": "c2"}]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            output_path = temp_dir / "judgements.json"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "same sample ids"):
                judge_runner.run_pairwise_judge(baseline_path, candidate_path, output_path)

    def test_run_pairwise_judge_to_dir_writes_manifest_bundle(self):
        baseline_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "", "retrieved_rows": [], "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}]}]
        candidate_predictions = [{"id": "sample-1", "question": "Q1", "reference_answer": "R1", "answer": "c1", "retrieved_rows": [{"source_id": "doc-1", "locator": "p1"}], "evidence": [{"quote": "q1", "source_id": "doc-1", "locator": "p1"}]}]
        fake_runtime_config = types.SimpleNamespace(
            provider="modelscope",
            api_key="test-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            chat_model_name="qwen3-max",
            embedding_model_name="text-embedding-v4",
        )
        fake_chat_model = mock.Mock()
        fake_chat_model.invoke.return_value = '{"winner":"candidate","reason":"candidate is better"}'

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            out_dir = temp_dir / "judge_eval"
            baseline_path.write_text(json.dumps(baseline_predictions), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate_predictions), encoding="utf-8")

            with (
                mock.patch.object(judge_runner, "load_runtime_config", return_value=fake_runtime_config),
                mock.patch.object(judge_runner, "build_chat_model", return_value=fake_chat_model),
            ):
                summary = judge_runner.run_pairwise_judge_to_dir(baseline_path, candidate_path, out_dir)

            run_dirs = list(out_dir.iterdir())
            self.assertEqual(1, len(run_dirs))
            run_dir = run_dirs[0]
            self.assertEqual(1, summary["sample_count"])
            self.assertTrue((run_dir / "judgements.json").exists())
            self.assertTrue((run_dir / "summary.json").exists())
            self.assertTrue((run_dir / "manifest.json").exists())
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("v1.1", manifest["contract_version"])
            self.assertEqual("judge_eval", manifest["pipeline"])
            self.assertEqual("modelscope", manifest["provider"])
            self.assertEqual("qwen3-max", manifest["chat_model_name"])
            self.assertEqual("v1.1-pairwise-judge", manifest["judge_prompt_version"])

    def test_run_baseline_uses_distinct_session_ids_per_sample(self):
        samples = [
            {
                "id": "sample-1",
                "question": "What is LocalRAG?",
                "reference_answer": "A local RAG project.",
                "evidence": [
                    {"quote": "LocalRAG", "source_id": "doc-1", "locator": "p1"}
                ],
                "metadata": {"difficulty": "easy", "topic": "rag", "doc_type": "guide"},
            },
            {
                "id": "sample-2",
                "question": "What does it test?",
                "reference_answer": "Baseline evaluation.",
                "evidence": [
                    {"quote": "baseline", "source_id": "doc-2", "locator": "p2"}
                ],
                "metadata": {"difficulty": "easy", "topic": "evaluation", "doc_type": "guide"},
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            dataset_path = temp_dir / "dataset.json"
            predictions_path = temp_dir / "predictions.json"
            metrics_path = temp_dir / "metrics.json"
            dataset_path.write_text(json.dumps(samples), encoding="utf-8")

            fake_rag_module = types.SimpleNamespace()
            fake_rag_service = mock.Mock()
            fake_rag_service.answer_with_retrieval.side_effect = [
                {
                    "answer": "answer-1",
                    "retrieved_context": "ctx-1",
                    "retrieved_rows": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
                    "retrieval_debug_candidates": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
                },
                {
                    "answer": "answer-2",
                    "retrieved_context": "ctx-2",
                    "retrieved_rows": [{"source_id": "doc-2", "locator": "p2", "content": "ctx-2"}],
                    "retrieval_debug_candidates": [{"source_id": "doc-2", "locator": "p2", "content": "ctx-2"}],
                },
            ]
            fake_rag_module.RagService = mock.Mock(return_value=fake_rag_service)

            with (
                mock.patch.dict(sys.modules, {"core.rag": fake_rag_module}),
                mock.patch("eval.eval_ragas.load_runtime_config", return_value=None),
            ):
                summary = run_baseline(dataset_path, predictions_path, metrics_path)

            self.assertEqual(summary["sample_count"], 2)
            self.assertEqual(summary["evidence_source_hit_count"], 2)
            self.assertEqual(summary["evidence_locator_hit_count"], 2)
            self.assertEqual(fake_rag_module.RagService.call_count, 1)
            fake_rag_service.answer_with_retrieval.assert_has_calls(
                [
                    mock.call("What is LocalRAG?", session_id="eval-session-sample-1"),
                    mock.call("What does it test?", session_id="eval-session-sample-2"),
                ]
            )
            self.assertEqual(
                [call.kwargs["session_id"] for call in fake_rag_service.answer_with_retrieval.call_args_list],
                ["eval-session-sample-1", "eval-session-sample-2"],
            )
            predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
            self.assertEqual("ctx-1", predictions[0]["retrieved_context"])
            self.assertEqual("doc-1", predictions[0]["retrieved_rows"][0]["source_id"])
            self.assertEqual("p2", predictions[1]["evidence"][0]["locator"])
            self.assertTrue(predictions_path.exists())
            self.assertTrue(metrics_path.exists())

    def test_run_baseline_to_dir_writes_manifest_bundle(self):
        samples = [
            {
                "id": "sample-1",
                "question": "What is LocalRAG?",
                "reference_answer": "A local RAG project.",
                "evidence": [
                    {"quote": "LocalRAG", "source_id": "doc-1", "locator": "p1"}
                ],
                "metadata": {"difficulty": "easy", "topic": "rag", "doc_type": "guide"},
            }
        ]
        fake_runtime_config = types.SimpleNamespace(
            provider="modelscope",
            api_key="test-key",
            base_url="https://api-inference.modelscope.cn/v1",
            chat_model_name="Qwen/Qwen2.5-72B-Instruct",
            embedding_model_name="Qwen/Qwen3-Embedding-8B",
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            dataset_path = temp_dir / "gold_set.json"
            out_dir = temp_dir / "results"
            dataset_path.write_text(json.dumps(samples), encoding="utf-8")

            fake_rag_module = types.SimpleNamespace()
            fake_rag_service = mock.Mock()
            fake_rag_service.answer_with_retrieval.return_value = {
                "answer": "answer-1",
                "retrieved_context": "ctx-1",
                "retrieved_rows": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
                "retrieval_debug_candidates": [{"source_id": "doc-1", "locator": "p1", "content": "ctx-1"}],
            }
            fake_rag_module.RagService = mock.Mock(return_value=fake_rag_service)

            with (
                mock.patch.dict(sys.modules, {"core.rag": fake_rag_module}),
                mock.patch("eval.eval_ragas.load_runtime_config", return_value=fake_runtime_config),
            ):
                summary = ragas_runner.run_baseline_to_dir(dataset_path, out_dir)

            run_dirs = list(out_dir.iterdir())
            self.assertEqual(1, len(run_dirs))
            run_dir = run_dirs[0]
            self.assertEqual(1, summary["sample_count"])
            self.assertTrue((run_dir / "predictions.json").exists())
            self.assertTrue((run_dir / "metrics.json").exists())
            self.assertTrue((run_dir / "manifest.json").exists())
            metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(1, metrics["evidence_source_hit_count"])
            self.assertEqual(1, metrics["evidence_locator_hit_count"])
            manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("v1.1", manifest["contract_version"])
            self.assertEqual("baseline_eval", manifest["pipeline"])
            self.assertEqual(str(dataset_path), manifest["dataset_path"])
            self.assertEqual("modelscope", manifest["provider"])
            self.assertEqual("Qwen/Qwen2.5-72B-Instruct", manifest["chat_model_name"])
            self.assertEqual("Qwen/Qwen3-Embedding-8B", manifest["embedding_model_name"])

    def test_require_runtime_config_calls_runtime_config_loader(self):
        with mock.patch("eval.eval_ragas.load_runtime_config", return_value=None) as loader:
            require_runtime_config()

        loader.assert_called_once_with()

    def test_require_chunking_runtime_credentials_calls_runtime_config_loader(self):
        with mock.patch("eval.eval_chunking.load_runtime_config", return_value=None) as loader:
            eval_chunking.require_runtime_config()

        loader.assert_called_once_with()

    def test_require_runtime_config_surfaces_loader_runtime_error(self):
        with mock.patch(
            "eval.eval_ragas.load_runtime_config",
            side_effect=RuntimeError("Missing runtime credentials"),
        ):
            with self.assertRaisesRegex(RuntimeError, "Missing runtime credentials"):
                require_runtime_config()

    def test_require_chunking_runtime_credentials_surfaces_loader_runtime_error(self):
        with mock.patch(
            "eval.eval_chunking.load_runtime_config",
            side_effect=RuntimeError("Missing runtime credentials"),
        ):
            with self.assertRaisesRegex(RuntimeError, "Missing runtime credentials"):
                eval_chunking.require_runtime_config()

    def test_eval_scripts_support_direct_python_execution_import_path(self):
        eval_dir = Path(__file__).resolve().parents[1] / "eval"
        for file_name in ("eval_ragas.py", "eval_llm_judge.py", "eval_chunking.py"):
            content = (eval_dir / file_name).read_text(encoding="utf-8")
            self.assertIn("if __package__ in {None, \"\"}", content)
            self.assertIn("sys.path.insert(0, str(Path(__file__).resolve().parents[1]))", content)

    def test_write_json_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "nested" / "results" / "baseline.json"

            write_json(path, {"status": "ok"})

            self.assertTrue(path.exists())
            self.assertTrue(path.parent.exists())
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
