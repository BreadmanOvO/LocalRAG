import json
import tempfile
import unittest
from pathlib import Path

from eval import eval_finetune_behavior
from eval import eval_finetune_compare
from scripts import prepare_sft_dataset
from scripts import prepare_sft_e2_draft
from scripts import prepare_sft_e2_dataset
from scripts import prepare_sft_e3_draft
from scripts import prepare_sft_e3_dataset
from scripts import prepare_sft_e4_draft
from scripts import prepare_sft_e4_dataset
from scripts import audit_sft_dataset
from scripts import check_finetune_env
from scripts import run_local_qwen3_e0
from scripts import smoke_local_qwen3
from scripts import smoke_local_rag_qwen3
from data.evaluation.shared.eval_schema import validate_dataset


def _sample(sample_id: str = "train-001") -> dict:
    return {
        "id": sample_id,
        "question": "CRN 融合了哪些传感器？",
        "reference_answer": "CRN 融合了摄像头和雷达。",
        "evidence": [
            {
                "quote": "CRN is a camera-radar fusion framework.",
                "source_id": "paper-030",
                "locator": "page=1",
            }
        ],
        "metadata": {
            "difficulty": "easy",
            "topic": "sensor_fusion",
            "doc_type": "paper",
        },
    }


class PrepareSftDatasetTests(unittest.TestCase):
    def test_build_sft_record_uses_chat_messages_with_evidence_and_citation(self):
        record = prepare_sft_dataset.build_sft_record(_sample(), "system prompt")

        self.assertEqual("train-001", record["id"])
        self.assertEqual(["system", "user", "assistant"], [m["role"] for m in record["messages"]])
        self.assertIn("CRN 融合了哪些传感器", record["messages"][1]["content"])
        self.assertIn("source_id=paper-030", record["messages"][1]["content"])
        self.assertIn("CRN 融合了摄像头和雷达。", record["messages"][2]["content"])
        self.assertIn("paper-030 page=1", record["messages"][2]["content"])

    def test_build_llamafactory_record_uses_instruction_input_output_shape(self):
        record = prepare_sft_dataset.build_llamafactory_record(
            _sample(),
            instruction="instruction",
            dataset_version="v1.3-e1",
            data_type="normal_grounded_qa",
        )

        self.assertEqual("instruction", record["instruction"])
        self.assertIn("CRN 融合了哪些传感器", record["input"])
        self.assertIn("source_id=paper-030", record["input"])
        self.assertIn("CRN 融合了摄像头和雷达。", record["output"])
        self.assertEqual("train-001", record["metadata"]["source_sample_id"])
        self.assertEqual("v1.3-e1", record["metadata"]["dataset_version"])
        self.assertEqual("normal_grounded_qa", record["metadata"]["data_type"])

    def test_prepare_sft_dataset_writes_train_and_validation_jsonl(self):
        samples = [_sample("train-001"), _sample("train-002"), _sample("train-003")]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            input_path = temp_dir / "train_set.json"
            train_output = temp_dir / "sft_train.jsonl"
            validation_output = temp_dir / "sft_validation.jsonl"
            input_path.write_text(json.dumps(samples, ensure_ascii=False), encoding="utf-8")

            summary = prepare_sft_dataset.prepare_sft_dataset(
                input_path=input_path,
                train_output_path=train_output,
                validation_output_path=validation_output,
                validation_count=1,
            )

            train_rows = [
                json.loads(line) for line in train_output.read_text(encoding="utf-8").splitlines()
            ]
            validation_rows = [
                json.loads(line)
                for line in validation_output.read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual(3, summary["source_count"])
        self.assertEqual(2, summary["train_count"])
        self.assertEqual(1, summary["validation_count"])
        self.assertEqual(["train-001", "train-002"], [row["id"] for row in train_rows])
        self.assertEqual(["train-003"], [row["id"] for row in validation_rows])

    def test_prepare_sft_dataset_writes_llamafactory_jsonl(self):
        samples = [_sample("train-001"), _sample("train-002"), _sample("train-003")]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            input_path = temp_dir / "train_set.json"
            train_output = temp_dir / "localrag_sft_e1.jsonl"
            validation_output = temp_dir / "localrag_sft_e1_validation.jsonl"
            input_path.write_text(json.dumps(samples, ensure_ascii=False), encoding="utf-8")

            summary = prepare_sft_dataset.prepare_sft_dataset(
                input_path=input_path,
                train_output_path=train_output,
                validation_output_path=validation_output,
                validation_count=1,
                output_format="llamafactory",
                dataset_version="v1.3-e1",
            )

            train_rows = [
                json.loads(line) for line in train_output.read_text(encoding="utf-8").splitlines()
            ]
            validation_rows = [
                json.loads(line)
                for line in validation_output.read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual("llamafactory", summary["format"])
        self.assertEqual(2, summary["train_count"])
        self.assertEqual(1, summary["validation_count"])
        self.assertEqual("train-001", train_rows[0]["metadata"]["source_sample_id"])
        self.assertEqual("train-003", validation_rows[0]["metadata"]["source_sample_id"])
        self.assertIn("instruction", train_rows[0])
        self.assertIn("input", train_rows[0])
        self.assertIn("output", train_rows[0])

    def test_default_llamafactory_instruction_requires_citations(self):
        record = prepare_sft_dataset.build_llamafactory_record(_sample())

        self.assertIn("引用", record["instruction"])
        self.assertIn("source_id", record["instruction"])
        self.assertIn("locator", record["instruction"])

    def test_split_records_rejects_validation_count_equal_to_dataset_size(self):
        with self.assertRaisesRegex(ValueError, "smaller than record count"):
            prepare_sft_dataset.split_records([_sample()], 1)


class PrepareSftE2DraftTests(unittest.TestCase):
    def test_build_refusal_row_marks_missing_evidence_and_keeps_citation(self):
        row = prepare_sft_e2_draft.build_refusal_row(
            row_id="e2-draft-001",
            source_record=_sample("train-001"),
            unsupported_question="资料是否说明 CRN 已在量产车型上部署并给出了部署成本？",
            unsupported_focus="CRN 的量产部署情况和部署成本",
            review_focus="refusal_insufficient_context",
        )

        self.assertEqual("e2-draft-001", row["metadata"]["source_sample_id"])
        self.assertEqual("refusal_insufficient_context", row["metadata"]["data_type"])
        self.assertEqual(["train-001"], row["metadata"]["source_record_ids"])
        self.assertIn("无法根据资料确定", row["output"])
        self.assertIn("paper-030 page=1", row["output"])

    def test_build_distractor_row_cites_only_target_record(self):
        target = _sample("train-target")
        distractor = _sample("train-distractor")
        distractor["evidence"][0]["source_id"] = "paper-999"
        distractor["evidence"][0]["locator"] = "page=9"

        row = prepare_sft_e2_draft.build_distractor_row(
            row_id="e2-draft-002",
            target_record=target,
            distractor_record=distractor,
            question="CRN 融合了哪些传感器？",
            answer="CRN 融合了摄像头和雷达。",
            review_focus="distractor_context",
        )

        self.assertEqual("distractor_context", row["metadata"]["data_type"])
        self.assertIn("source_id=paper-030", row["input"])
        self.assertIn("source_id=paper-999", row["input"])
        self.assertIn("paper-030 page=1", row["output"])
        self.assertNotIn("paper-999 page=9", row["output"])

    def test_e2_draft_alks_refusal_uses_constraint_language(self):
        required_ids = {
            "train-001",
            "train-003",
            "train-007",
            "train-038",
            "train-045",
            "train-085",
            "train-099",
            "train-110",
            "train-136",
            "train-144",
            "train-149",
            "train-164",
            "train-178",
        }
        records = [_sample(sample_id) for sample_id in sorted(required_ids)]
        for record in records:
            if record["id"] == "train-099":
                record["question"] = "根据UN R157，ALKS系统可以在哪些道路条件下被激活？"
                record["reference_answer"] = "在禁止行人和自行车、且设计有物理隔离分隔对向交通的道路上。"
                record["evidence"] = [
                    {
                        "quote": "ALKS can be activated under certain conditions on roads where pedestrians and cyclists are prohibited and which, by design, are equipped with a physical separation that divides the traffic moving in opposite directions…",
                        "source_id": "standard-009",
                        "locator": "page=3",
                    }
                ]
                record["metadata"] = {
                    "difficulty": "medium",
                    "topic": "planning_control",
                    "doc_type": "standard",
                }

        rows = prepare_sft_e2_draft.build_e2_rows(records)
        row = next(row for row in rows if row["metadata"]["source_sample_id"] == "e2-draft-refusal-004")

        self.assertEqual("e2-draft-refusal-004", row["metadata"]["source_sample_id"])
        self.assertIn("不能根据资料得出", row["output"])
        self.assertIn("行人和自行车被禁止", row["output"])
        self.assertIn("物理隔离", row["output"])


class PrepareSftE2DatasetTests(unittest.TestCase):
    def test_build_e2_dataset_merges_e1_train_with_hardcase_slice(self):
        e1_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-001"),
            dataset_version="v1.3-e1",
            data_type="normal_grounded_qa",
        )
        hardcase_row = prepare_sft_e2_draft.build_refusal_row(
            row_id="e2-draft-001",
            source_record=_sample("train-002"),
            unsupported_question="资料是否说明 CRN 已量产？",
            unsupported_focus="CRN 量产情况",
            review_focus="refusal_insufficient_context",
        )

        merged = prepare_sft_e2_dataset.build_e2_train_rows(
            e1_rows=[e1_row],
            hardcase_rows=[hardcase_row],
            dataset_version="v1.3-e2",
        )

        self.assertEqual(2, len(merged))
        self.assertEqual("v1.3-e2", merged[0]["metadata"]["dataset_version"])
        self.assertEqual("normal_grounded_qa", merged[0]["metadata"]["data_type"])
        self.assertEqual("e2_hardcase_refusal_insufficient_context", merged[1]["metadata"]["data_type"])
        self.assertEqual("v1.3-e2", merged[1]["metadata"]["dataset_version"])
        self.assertEqual("e2-draft-001", merged[1]["metadata"]["source_sample_id"])

    def test_build_e2_validation_rows_copies_validation_with_e2_version(self):
        validation_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-003"),
            dataset_version="v1.3-e1",
            data_type="normal_grounded_qa",
        )

        rows = prepare_sft_e2_dataset.build_e2_validation_rows(
            validation_rows=[validation_row],
            dataset_version="v1.3-e2",
        )

        self.assertEqual(1, len(rows))
        self.assertEqual("train-003", rows[0]["metadata"]["source_sample_id"])
        self.assertEqual("v1.3-e2", rows[0]["metadata"]["dataset_version"])
        self.assertEqual("normal_grounded_qa_validation", rows[0]["metadata"]["data_type"])


class PrepareSftE3DraftTests(unittest.TestCase):
    def test_build_partial_context_row_answers_supported_part_and_refuses_missing_metric(self):
        source = _sample("train-001")
        source["evidence"][0]["quote"] = (
            "using 4096 size queries reduce the latency of MFA by 76.4%."
        )

        row = prepare_sft_e3_draft.build_partial_context_row(
            row_id="e3-draft-partial-001",
            source_record=source,
            question="4096 个 Top-K 查询会让 MFA 延迟和 AP 指标发生什么变化？",
            answer=(
                "资料只说明 4096 个查询会让 MFA 延迟降低 76.4%；"
                "没有给出 AP 指标变化，不能根据资料确定 AP 是提升还是下降。"
            ),
            review_focus="partial_context_numeric_no_guess",
        )

        self.assertEqual("e3-draft-partial-001", row["metadata"]["source_sample_id"])
        self.assertEqual("partial_context_insufficient_metric", row["metadata"]["data_type"])
        self.assertEqual(["train-001"], row["metadata"]["source_record_ids"])
        self.assertIn("不能根据资料确定", row["output"])
        self.assertIn("paper-030 page=1", row["output"])

    def test_build_strict_distractor_row_cites_only_target_record(self):
        target = _sample("train-target")
        distractor = _sample("train-distractor")
        distractor["evidence"][0]["source_id"] = "apollo-doc-007"
        distractor["evidence"][0]["locator"] = "page=9"

        row = prepare_sft_e3_draft.build_strict_distractor_row(
            row_id="e3-draft-distractor-001",
            target_record=target,
            distractor_record=distractor,
            question="CRN 融合了哪些传感器？",
            answer="CRN 融合了摄像头和雷达。",
            review_focus="strict_target_only_citation",
        )

        self.assertEqual("strict_distractor_target_only_citation", row["metadata"]["data_type"])
        self.assertIn("source_id=paper-030", row["input"])
        self.assertIn("source_id=apollo-doc-007", row["input"])
        self.assertIn("paper-030 page=1", row["output"])
        self.assertNotIn("apollo-doc-007 page=9", row["output"])

    def test_build_e3_rows_creates_two_balanced_hardcase_groups(self):
        required_ids = set()
        for spec in prepare_sft_e3_draft.PARTIAL_CONTEXT_SPECS:
            required_ids.add(spec["source_id"])
        for spec in prepare_sft_e3_draft.STRICT_DISTRACTOR_SPECS:
            required_ids.add(spec["target_id"])
            required_ids.add(spec["distractor_id"])
        records = [_sample(sample_id) for sample_id in sorted(required_ids)]

        rows = prepare_sft_e3_draft.build_e3_rows(records)
        data_types = [row["metadata"]["data_type"] for row in rows]

        self.assertEqual(16, len(rows))
        self.assertEqual(8, data_types.count("partial_context_insufficient_metric"))
        self.assertEqual(8, data_types.count("strict_distractor_target_only_citation"))


class PrepareSftE3DatasetTests(unittest.TestCase):
    def test_build_e3_dataset_merges_e2_train_with_e3_hardcase_slice(self):
        e2_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-001"),
            dataset_version="v1.3-e2",
            data_type="normal_grounded_qa",
        )
        hardcase_row = prepare_sft_e3_draft.build_partial_context_row(
            row_id="e3-draft-partial-001",
            source_record=_sample("train-002"),
            question="资料是否说明 CRN 已量产？",
            answer="资料没有说明 CRN 是否已量产，无法根据资料确定。",
            review_focus="partial_context_numeric_no_guess",
        )

        merged = prepare_sft_e3_dataset.build_e3_train_rows(
            e2_rows=[e2_row],
            hardcase_rows=[hardcase_row],
            dataset_version="v1.3-e3",
        )

        self.assertEqual(2, len(merged))
        self.assertEqual("v1.3-e3", merged[0]["metadata"]["dataset_version"])
        self.assertEqual("normal_grounded_qa", merged[0]["metadata"]["data_type"])
        self.assertEqual(
            "e3_hardcase_partial_context_insufficient_metric",
            merged[1]["metadata"]["data_type"],
        )
        self.assertEqual("e3_hardcase_slice", merged[1]["metadata"]["e3_source"])

    def test_build_e3_validation_rows_copies_validation_with_e3_version(self):
        validation_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-003"),
            dataset_version="v1.3-e2",
            data_type="normal_grounded_qa_validation",
        )

        rows = prepare_sft_e3_dataset.build_e3_validation_rows(
            validation_rows=[validation_row],
            dataset_version="v1.3-e3",
        )

        self.assertEqual(1, len(rows))
        self.assertEqual("train-003", rows[0]["metadata"]["source_sample_id"])
        self.assertEqual("v1.3-e3", rows[0]["metadata"]["dataset_version"])
        self.assertEqual("normal_grounded_qa_validation", rows[0]["metadata"]["data_type"])


class PrepareSftE4DraftTests(unittest.TestCase):
    def test_build_multi_metric_partial_context_row_refuses_missing_metric_direction(self):
        source = _sample("train-001")
        source["evidence"][0]["quote"] = "using 4096 size queries reduce the latency of MFA by 76.4%."

        row = prepare_sft_e4_draft.build_multi_metric_partial_context_row(
            row_id="e4-draft-multi-metric-001",
            source_record=source,
            question="4096 个 Top-K 查询会让 MFA 延迟、AP 和 ATE 分别发生什么变化？",
            supported_claim="资料只说明 4096 个查询会让 MFA 延迟降低 76.4%。",
            missing_metrics=["AP", "ATE"],
            review_focus="multi_metric_partial_context_no_direction_guess",
        )

        self.assertEqual("e4-draft-multi-metric-001", row["metadata"]["source_sample_id"])
        self.assertEqual("multi_metric_partial_context_refusal", row["metadata"]["data_type"])
        self.assertEqual(["AP", "ATE"], row["metadata"]["missing_metrics"])
        self.assertEqual("partial_refuse", row["metadata"]["expected_behavior"])
        self.assertIn("延迟降低 76.4%", row["output"])
        self.assertIn("不能根据资料确定 AP 或 ATE 是提升还是下降", row["output"])
        self.assertNotIn("1.3%", row["output"])
        self.assertIn("paper-030 page=1", row["output"])

    def test_build_e4_rows_creates_focused_multi_metric_slice(self):
        required_ids = {spec["source_id"] for spec in prepare_sft_e4_draft.MULTI_METRIC_PARTIAL_CONTEXT_SPECS}
        records = [_sample(sample_id) for sample_id in sorted(required_ids)]

        rows = prepare_sft_e4_draft.build_e4_rows(records)
        data_types = [row["metadata"]["data_type"] for row in rows]

        self.assertEqual(8, len(rows))
        self.assertEqual(8, data_types.count("multi_metric_partial_context_refusal"))
        self.assertTrue(all(row["metadata"].get("missing_metrics") for row in rows))


class PrepareSftE4DatasetTests(unittest.TestCase):
    def test_build_e4_dataset_merges_e3_train_with_e4_hardcase_slice(self):
        e3_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-001"),
            dataset_version="v1.3-e3",
            data_type="normal_grounded_qa",
        )
        hardcase_row = prepare_sft_e4_draft.build_multi_metric_partial_context_row(
            row_id="e4-draft-multi-metric-001",
            source_record=_sample("train-002"),
            question="资料是否说明 CRN 的延迟和 AP 都改善？",
            supported_claim="资料没有说明 CRN 的延迟或 AP 是否改善。",
            missing_metrics=["latency", "AP"],
            review_focus="multi_metric_partial_context_no_direction_guess",
        )

        merged = prepare_sft_e4_dataset.build_e4_train_rows(
            e3_rows=[e3_row],
            hardcase_rows=[hardcase_row],
            dataset_version="v1.3-e4",
        )

        self.assertEqual(2, len(merged))
        self.assertEqual("v1.3-e4", merged[0]["metadata"]["dataset_version"])
        self.assertEqual("normal_grounded_qa", merged[0]["metadata"]["data_type"])
        self.assertEqual(
            "e4_hardcase_multi_metric_partial_context_refusal",
            merged[1]["metadata"]["data_type"],
        )
        self.assertEqual("e4_hardcase_slice", merged[1]["metadata"]["e4_source"])

    def test_build_e4_validation_rows_copies_validation_with_e4_version(self):
        validation_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-003"),
            dataset_version="v1.3-e3",
            data_type="normal_grounded_qa_validation",
        )

        rows = prepare_sft_e4_dataset.build_e4_validation_rows(
            validation_rows=[validation_row],
            dataset_version="v1.3-e4",
        )

        self.assertEqual(1, len(rows))
        self.assertEqual("train-003", rows[0]["metadata"]["source_sample_id"])
        self.assertEqual("v1.3-e4", rows[0]["metadata"]["dataset_version"])
        self.assertEqual("normal_grounded_qa_validation", rows[0]["metadata"]["data_type"])


class AuditSftDatasetTests(unittest.TestCase):
    def test_validate_llamafactory_row_accepts_complete_record(self):
        row = prepare_sft_dataset.build_llamafactory_record(_sample())

        issues = audit_sft_dataset.validate_llamafactory_row(row)

        self.assertEqual([], issues)

    def test_validate_llamafactory_row_flags_missing_citation(self):
        row = prepare_sft_dataset.build_llamafactory_record(_sample())
        row["output"] = "CRN 融合了摄像头和雷达。"

        issues = audit_sft_dataset.validate_llamafactory_row(row)

        self.assertIn("output is missing citation section", issues)

    def test_audit_sft_dataset_reports_split_and_eval_overlap(self):
        train_row = prepare_sft_dataset.build_llamafactory_record(_sample("train-001"))
        validation_row = prepare_sft_dataset.build_llamafactory_record(_sample("train-001"))
        eval_record = _sample("train-001")
        generation_record = _sample("gen-eval-001")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            train_path = temp_dir / "train.jsonl"
            validation_path = temp_dir / "validation.jsonl"
            eval_path = temp_dir / "eval.json"
            generation_path = temp_dir / "generation.json"
            train_path.write_text(json.dumps(train_row, ensure_ascii=False) + "\n", encoding="utf-8")
            validation_path.write_text(json.dumps(validation_row, ensure_ascii=False) + "\n", encoding="utf-8")
            eval_path.write_text(json.dumps([eval_record], ensure_ascii=False), encoding="utf-8")
            generation_path.write_text(json.dumps([generation_record], ensure_ascii=False), encoding="utf-8")

            summary = audit_sft_dataset.audit_sft_dataset(
                train_path=train_path,
                validation_path=validation_path,
                eval_set_path=eval_path,
                generation_eval_set_path=generation_path,
            )

        self.assertEqual(["train-001"], summary["split_overlap_source_sample_ids"])
        self.assertEqual(["train-001"], summary["eval_set_overlap_source_sample_ids"])
        self.assertEqual([], summary["generation_eval_set_overlap_source_sample_ids"])

    def test_write_audit_accepts_run_name_for_e2_outputs(self):
        train_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-001"),
            dataset_version="v1.3-e2",
        )
        validation_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-002"),
            dataset_version="v1.3-e2",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            summary = {
                "created_at": "2026-06-13T00:00:00",
                "train_path": "train.jsonl",
                "validation_path": "validation.jsonl",
                "eval_set_path": "eval.json",
                "generation_eval_set_path": "generation.json",
                "train": audit_sft_dataset.summarize_rows([train_row]),
                "validation": audit_sft_dataset.summarize_rows([validation_row]),
                "split_overlap_source_sample_ids": [],
                "eval_set_overlap_source_sample_ids": [],
                "generation_eval_set_overlap_source_sample_ids": [],
            }

            artifacts = audit_sft_dataset.write_audit(summary, temp_dir, run_name="sft-e2-audit")
            report = Path(artifacts["report"]).read_text(encoding="utf-8")

        self.assertIn("sft-e2-audit-", artifacts["run_dir"])
        self.assertIn("# LocalRAG SFT Dataset Audit", report)


class FinetuneBehaviorEvalTests(unittest.TestCase):
    def test_evaluate_row_marks_unsupported_claim_and_over_refusal(self):
        unsupported = {
            "id": "eval-001",
            "answer": "CRN 融合摄像头和雷达。",
            "retrieved_rows": [{"source_id": "paper-999", "locator": "page=9"}],
            "evidence": [{"source_id": "paper-030", "locator": "page=1"}],
        }
        over_refusal = {
            "id": "eval-002",
            "answer": "无法从给定证据确认。",
            "retrieved_rows": [{"source_id": "paper-030", "locator": "page=1"}],
            "evidence": [{"source_id": "paper-030", "locator": "page=1"}],
        }

        unsupported_row = eval_finetune_behavior.evaluate_row(unsupported)
        over_refusal_row = eval_finetune_behavior.evaluate_row(over_refusal)

        self.assertTrue(unsupported_row["unsupported_claim_risk"])
        self.assertFalse(unsupported_row["over_refusal_risk"])
        self.assertFalse(over_refusal_row["unsupported_claim_risk"])
        self.assertTrue(over_refusal_row["over_refusal_risk"])

    def test_summarize_and_compare_behavior_ratios(self):
        baseline = eval_finetune_behavior.summarize_rows(
            [
                {
                    "answered": True,
                    "refusal": False,
                    "evidence_source_hit": False,
                    "evidence_locator_hit": False,
                    "answer_cites_evidence": False,
                    "unsupported_claim_risk": True,
                    "over_refusal_risk": False,
                    "correct_refusal": False,
                }
            ]
        )
        candidate = eval_finetune_behavior.summarize_rows(
            [
                {
                    "answered": True,
                    "refusal": False,
                    "evidence_source_hit": True,
                    "evidence_locator_hit": True,
                    "answer_cites_evidence": True,
                    "unsupported_claim_risk": False,
                    "over_refusal_risk": False,
                    "correct_refusal": False,
                }
            ]
        )

        comparison = eval_finetune_behavior.compare_summaries(baseline, candidate)

        self.assertEqual(1.0, candidate["answer_cites_evidence_ratio"])
        self.assertEqual(-1.0, comparison["unsupported_claim_risk_ratio_delta"])
        self.assertEqual(1.0, comparison["evidence_source_hit_ratio_delta"])

    def test_evaluate_predictions_rejects_mismatched_baseline_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            baseline_path.write_text(json.dumps([{"id": "eval-001"}]), encoding="utf-8")
            candidate_path.write_text(json.dumps([{"id": "eval-002"}]), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "same sample ids"):
                eval_finetune_behavior.evaluate_predictions(
                    predictions_path=candidate_path,
                    baseline_predictions_path=baseline_path,
                    out_dir=temp_dir / "out",
                )

    def test_expected_refusal_is_not_marked_as_over_refusal(self):
        row = {
            "id": "gen-eval-005",
            "answer": "资料并未提及相关数据，因此无法从现有资料中得出结论。",
            "retrieved_rows": [{"source_id": "apollo-doc-006", "locator": "page=1"}],
            "evidence": [{"source_id": "apollo-doc-006", "locator": "page=1"}],
            "metadata": {"expected_behavior": "refuse"},
        }

        evaluated = eval_finetune_behavior.evaluate_row(row)

        self.assertTrue(evaluated["correct_refusal"])
        self.assertFalse(evaluated["over_refusal_risk"])

    def test_is_refusal_recognizes_natural_chinese_missing_evidence_phrases(self):
        refusal_answers = [
            "没有提到 CRN 在量产车型上的部署或成本。",
            "资料没有说明该模块在雨夜施工区域的误检率。",
            "现有材料未给出具体数值。",
        ]

        for answer in refusal_answers:
            with self.subTest(answer=answer):
                self.assertTrue(eval_finetune_behavior.is_refusal(answer))


class FinetuneCompareTests(unittest.TestCase):
    def test_build_side_by_side_rows_requires_matching_ids_and_records_answer_lengths(self):
        baseline = [
            {
                "id": "gen-eval-001",
                "question": "问题1",
                "answer": "base answer",
                "retrieved_rows": [{"source_id": "doc-1"}],
                "evidence": [{"source_id": "doc-1", "locator": "page=1"}],
            }
        ]
        candidate = [
            {
                "id": "gen-eval-001",
                "question": "问题1",
                "answer": "adapter answer with doc-1 citation",
                "retrieved_rows": [{"source_id": "doc-1"}],
                "evidence": [{"source_id": "doc-1", "locator": "page=1"}],
            }
        ]

        rows = eval_finetune_compare.build_side_by_side_rows(baseline, candidate)

        self.assertEqual(1, len(rows))
        self.assertEqual("gen-eval-001", rows[0]["id"])
        self.assertEqual(len("base answer"), rows[0]["baseline_answer_length"])
        self.assertEqual(len("adapter answer with doc-1 citation"), rows[0]["candidate_answer_length"])
        self.assertTrue(rows[0]["candidate_behavior"]["answer_cites_evidence"])

    def test_build_side_by_side_rows_rejects_mismatched_ids(self):
        with self.assertRaisesRegex(ValueError, "same sample ids"):
            eval_finetune_compare.build_side_by_side_rows(
                [{"id": "base-1", "answer": ""}],
                [{"id": "candidate-1", "answer": ""}],
            )

    def test_classify_verdict_marks_citation_improvement(self):
        verdict = eval_finetune_compare.classify_verdict(
            {
                "answer_cites_evidence_ratio_delta": 1.0,
                "unsupported_claim_risk_ratio_delta": 0.0,
                "over_refusal_risk_ratio_delta": 0.0,
                "refusal_ratio_delta": 0.0,
            }
        )

        self.assertEqual("adapter_improved", verdict)

    def test_analyze_answer_hardening_flags_unsupported_numeric_claims(self):
        row = {
            "id": "gen-eval-004",
            "answer": "延迟降低76%，检测指标提升1.3%。\n\n引用：\n- paper-030 unknown",
            "reference_answer": "MFA 延迟从 21.01ms 降到 4.96ms，降低 76.4%；AP 从 56.9% 降到 54.0%，ATE 从 0.325 升到 0.367，说明延迟显著降低但回归相关指标下降更明显。",
            "retrieved_context": "using 4096 size queries reduce the latency of MFA by 76.",
            "retrieved_rows": [
                {
                    "source_id": "paper-030",
                    "content": "using 4096 size queries reduce the latency of MFA by 76.",
                }
            ],
            "evidence": [
                {
                    "source_id": "paper-030",
                    "quote": "using 4096 size queries reduce the latency of MFA by 76.4% ... the performance drops on True Positive metrics.",
                }
            ],
        }

        hardening = eval_finetune_compare.analyze_answer_hardening(row)

        self.assertIn("1.3", hardening["unsupported_answer_numbers"])
        self.assertTrue(hardening["unsupported_numeric_claim_risk"])
        self.assertTrue(hardening["directional_contradiction_risk"])
        self.assertTrue(hardening["citation_support_risk"])

    def test_analyze_answer_hardening_flags_missing_reference_terms(self):
        row = {
            "id": "gen-eval-009",
            "answer": "主要解决 BEV 感知中的 domain adaptation 问题，并与 intrinsic parameters 解耦。\n\n引用：\n- paper-038 unknown",
            "reference_answer": "One challenge is domain adaptation; feature learning should be independent of the extrinsic and/or intrinsic matrix.",
            "retrieved_context": "independent of the extrinsic and/or intrinsic matrix",
            "retrieved_rows": [{"source_id": "paper-038", "content": "extrinsic and intrinsic matrix"}],
            "evidence": [
                {
                    "source_id": "paper-038",
                    "quote": "independent of the extrinsic and/or intrinsic matrix",
                }
            ],
        }

        hardening = eval_finetune_compare.analyze_answer_hardening(row)

        self.assertIn("extrinsic", hardening["missing_reference_terms"])
        self.assertTrue(hardening["reference_coverage_risk"])

    def test_classify_verdict_does_not_call_hardcase_regression_improved(self):
        verdict = eval_finetune_compare.classify_verdict(
            {
                "answer_cites_evidence_ratio_delta": 0.2,
                "unsupported_claim_risk_ratio_delta": 0.0,
                "over_refusal_risk_ratio_delta": 0.0,
                "refusal_ratio_delta": 0.0,
                "unsupported_numeric_claim_risk_ratio_delta": 0.1,
                "citation_support_risk_ratio_delta": 0.1,
            }
        )

        self.assertEqual("mixed_or_regressed", verdict)

    def test_write_compare_outputs_summary_manifest_and_side_by_side_report(self):
        baseline = [
            {
                "id": "gen-eval-001",
                "question": "问题1",
                "answer": "base answer",
                "reference_answer": "doc-1",
                "retrieved_rows": [{"source_id": "doc-1"}],
                "evidence": [{"source_id": "doc-1", "locator": "page=1"}],
                "metadata": {"generation_category": "normal_answerable"},
            }
        ]
        candidate = [
            {
                "id": "gen-eval-001",
                "question": "问题1",
                "answer": "adapter answer with doc-1 citation",
                "reference_answer": "doc-1",
                "retrieved_rows": [{"source_id": "doc-1"}],
                "evidence": [{"source_id": "doc-1", "locator": "page=1"}],
                "metadata": {"generation_category": "normal_answerable"},
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            baseline_path = temp_dir / "baseline.json"
            candidate_path = temp_dir / "candidate.json"
            baseline_path.write_text(json.dumps(baseline, ensure_ascii=False), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate, ensure_ascii=False), encoding="utf-8")

            result = eval_finetune_compare.compare_predictions(
                baseline_predictions_path=baseline_path,
                candidate_predictions_path=candidate_path,
                out_dir=temp_dir / "out",
                baseline_label="base",
                candidate_label="adapter",
            )

            run_dir = Path(result["run_dir"])
            summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
            report = (run_dir / "side_by_side_samples.md").read_text(encoding="utf-8")
            manifest_exists = (run_dir / "manifest.json").exists()

        self.assertEqual("adapter_improved", summary["verdict"])
        self.assertTrue(manifest_exists)
        self.assertIn("base", report)
        self.assertIn("adapter", report)
        self.assertIn("gen-eval-001", report)


class GenerationEvalSetTests(unittest.TestCase):
    def test_generation_eval_set_is_valid_and_balanced(self):
        path = Path("data/evaluation/gold/generation_eval_set.json")
        records = json.loads(path.read_text(encoding="utf-8"))

        validate_dataset(records)
        categories = {record["metadata"]["generation_category"] for record in records}

        self.assertEqual(10, len(records))
        self.assertEqual(
            {
                "normal_answerable",
                "hallucination_prone",
                "insufficient_context",
                "distractor_context",
                "hard_case_pattern_d",
            },
            categories,
        )
        self.assertTrue(
            all(record["metadata"]["expected_behavior"] in {"answer", "refuse"} for record in records)
        )

    def test_generation_eval_set_does_not_overlap_training_ids(self):
        generation_records = json.loads(
            Path("data/evaluation/gold/generation_eval_set.json").read_text(encoding="utf-8")
        )
        training_records = json.loads(
            Path("data/evaluation/train/train_set.json").read_text(encoding="utf-8")
        )

        generation_ids = {record["id"] for record in generation_records}
        training_ids = {record["id"] for record in training_records}

        self.assertFalse(generation_ids & training_ids)


class LlamaFactoryDatasetInfoTests(unittest.TestCase):
    def test_llamafactory_dataset_info_points_to_train_and_validation_files(self):
        info_path = Path("finetune/llamafactory_data/dataset_info.json")
        dataset_info = json.loads(info_path.read_text(encoding="utf-8"))

        expected_counts = {
            "localrag_sft_e1": 183,
            "localrag_sft_e1_validation": 20,
            "localrag_sft_e2": 195,
            "localrag_sft_e2_validation": 20,
            "localrag_sft_e3": 211,
            "localrag_sft_e3_validation": 20,
            "localrag_sft_e4": 219,
            "localrag_sft_e4_validation": 20,
        }
        expected_columns = {
            "prompt": "instruction",
            "query": "input",
            "response": "output",
        }

        self.assertEqual(set(expected_counts), set(dataset_info))
        for dataset_name, expected_count in expected_counts.items():
            entry = dataset_info[dataset_name]
            data_path = (info_path.parent / entry["file_name"]).resolve()

            self.assertTrue(data_path.exists())
            rows = [
                json.loads(line)
                for line in data_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

            self.assertEqual("alpaca", entry["formatting"])
            self.assertFalse(entry["ranking"])
            self.assertEqual(expected_columns, entry["columns"])
            self.assertEqual(expected_count, len(rows))
            self.assertTrue(all({"instruction", "input", "output"} <= set(row) for row in rows))


class CheckFinetuneEnvTests(unittest.TestCase):
    def test_build_markdown_report_includes_gate_fields(self):
        report = {
            "created_at": "2026-05-28T00:00:00",
            "platform": {"system": "Windows", "release": "11"},
            "python": {"version": "3.12.7", "executable": "python"},
            "packages": {
                "torch": {
                    "available": True,
                    "version": "2.6.0+cu124",
                    "cuda_available": True,
                    "cuda_version": "12.4",
                    "gpu_name": "RTX 4080 SUPER",
                    "gpu_memory_free_bytes": 8 * 1024 ** 3,
                    "gpu_memory_total_bytes": 16 * 1024 ** 3,
                    "error": None,
                },
                "transformers": {"available": True, "version": "4.0.0"},
                "peft": {"available": False, "version": None},
                "trl": {"available": False, "version": None},
                "accelerate": {"available": False, "version": None},
                "bitsandbytes": {"available": False, "version": None},
                "flash_attn": {"available": False, "version": None},
            },
            "commands": {"llamafactory-cli": {"available": False}},
            "local_paths": {
                "qwen3_8b": {"path": "models/Qwen3-8B", "exists": True},
                "qwen3_4b": {"path": "models/Qwen3-4B", "exists": True},
                "bge_m3": {"path": "models/bge-m3", "exists": True},
            },
        }

        markdown = check_finetune_env.build_markdown_report(report)

        self.assertIn("CUDA available: `True`", markdown)
        self.assertIn("RTX 4080 SUPER", markdown)
        self.assertIn("bitsandbytes", markdown)
        self.assertIn("LLaMA-Factory CLI available: `False`", markdown)
        self.assertIn("Qwen3-8B", markdown)
        self.assertIn("Qwen3-4B", markdown)

    def test_write_reports_persists_json_and_markdown(self):
        report = {
            "created_at": "2026-05-28T00:00:00",
            "platform": {"system": "Windows", "release": "11"},
            "python": {"version": "3.12.7", "executable": "python"},
            "packages": {
                "torch": {
                    "available": False,
                    "version": None,
                    "cuda_available": False,
                    "cuda_version": None,
                    "gpu_name": None,
                    "gpu_memory_free_bytes": None,
                    "gpu_memory_total_bytes": None,
                    "error": None,
                },
                "transformers": {"available": False, "version": None},
                "peft": {"available": False, "version": None},
                "trl": {"available": False, "version": None},
                "accelerate": {"available": False, "version": None},
                "bitsandbytes": {"available": False, "version": None},
                "flash_attn": {"available": False, "version": None},
            },
            "commands": {"llamafactory-cli": {"available": False}},
            "local_paths": {
                "qwen3_8b": {"path": "models/Qwen3-8B", "exists": False},
                "qwen3_4b": {"path": "models/Qwen3-4B", "exists": False},
                "bge_m3": {"path": "models/bge-m3", "exists": False},
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = check_finetune_env.write_reports(report, Path(temp_dir))

            json_path = Path(paths["json"])
            markdown_path = Path(paths["markdown"])

            self.assertTrue(json_path.exists())
            self.assertTrue(markdown_path.exists())
            self.assertEqual("Windows", json.loads(json_path.read_text(encoding="utf-8"))["platform"]["system"])


class SmokeLocalQwen3Tests(unittest.TestCase):
    def test_build_markdown_result_includes_success_and_error(self):
        result = {
            "run_id": "qwen3-smoke-test",
            "created_at": "2026-06-01T00:00:00",
            "success": True,
            "model_path": "models/Qwen3-8B",
            "device": "cuda",
            "device_requested": "auto",
            "torch_dtype_requested": "float16",
            "max_new_tokens": 64,
            "tokenizer_loaded": True,
            "model_loaded": True,
            "memory_after_load": {
                "memory_allocated_bytes": 4 * 1024 ** 3,
                "memory_reserved_bytes": 5 * 1024 ** 3,
            },
            "memory_after_generate": {
                "max_memory_allocated_bytes": 6 * 1024 ** 3,
            },
            "prompt": "问题",
            "generated_text": "回答",
            "error": None,
        }

        markdown = smoke_local_qwen3.build_markdown_result(result)

        self.assertIn("Success: `True`", markdown)
        self.assertIn("models/Qwen3-8B", markdown)
        self.assertIn("回答", markdown)
        self.assertIn("none", markdown)

    def test_write_result_files_persists_json_and_markdown(self):
        result = {
            "run_id": "qwen3-smoke-test",
            "created_at": "2026-06-01T00:00:00",
            "success": False,
            "model_path": "missing",
            "device_requested": "auto",
            "torch_dtype_requested": "float16",
            "max_new_tokens": 64,
            "tokenizer_loaded": False,
            "model_loaded": False,
            "memory_after_load": None,
            "memory_after_generate": None,
            "prompt": "问题",
            "generated_text": "",
            "error": "FileNotFoundError",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = smoke_local_qwen3.write_result_files(Path(temp_dir), result)

            self.assertTrue(Path(paths["json"]).exists())
            self.assertTrue(Path(paths["markdown"]).exists())
            payload = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
            self.assertFalse(payload["success"])


class SmokeLocalRagQwen3Tests(unittest.TestCase):
    def test_build_markdown_result_includes_retrieval_and_memory(self):
        result = {
            "run_id": "local-rag-qwen3-smoke-test",
            "created_at": "2026-06-02T00:00:00",
            "success": True,
            "runtime_config_path": "config/runtime_local_qwen3_4b.example.json",
            "store_dir": "results/chunking_eval/stores/run/semantic",
            "question": "问题",
            "answer": "回答",
            "retrieved_rows": [{"source_id": "paper-001"}, {"source_id": "standard-001"}],
            "memory_after": {
                "memory_allocated_bytes": 8 * 1024 ** 3,
                "memory_reserved_bytes": 9 * 1024 ** 3,
                "max_memory_allocated_bytes": 10 * 1024 ** 3,
            },
            "error": None,
        }

        markdown = smoke_local_rag_qwen3.build_markdown_result(result)

        self.assertIn("Success: `True`", markdown)
        self.assertIn("paper-001, standard-001", markdown)
        self.assertIn("回答", markdown)
        self.assertIn("10.00 GiB", markdown)

    def test_write_result_files_persists_prediction_manifest_and_markdown(self):
        result = {
            "run_id": "local-rag-qwen3-smoke-test",
            "created_at": "2026-06-02T00:00:00",
            "runtime_config_path": "config/runtime_local_qwen3_4b.example.json",
            "store_dir": "store",
            "question": "问题",
            "success": False,
            "answer": "",
            "retrieved_rows": [],
            "memory_after": None,
            "error": "error",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = smoke_local_rag_qwen3.write_result_files(Path(temp_dir), result)

            self.assertTrue(Path(paths["prediction"]).exists())
            self.assertTrue(Path(paths["manifest"]).exists())
            self.assertTrue(Path(paths["markdown"]).exists())


class RunLocalQwen3E0Tests(unittest.TestCase):
    def test_select_records_respects_positive_limit(self):
        records = [{"id": "a"}, {"id": "b"}, {"id": "c"}]

        selected = run_local_qwen3_e0.select_records(records, 2)

        self.assertEqual([{"id": "a"}, {"id": "b"}], selected)

    def test_now_run_id_accepts_run_label(self):
        run_id = run_local_qwen3_e0._now_run_id(
            Path("generation_eval_set.json"),
            run_label="qwen3-4b-smoke-adapter",
        )

        self.assertIn("generation_eval_set-qwen3-4b-smoke-adapter-", run_id)

    def test_build_manifest_records_generation_runtime_fields(self):
        runtime_config = type(
            "RuntimeConfig",
            (),
            {
                "provider": "local_transformers",
                "chat_model_name": "models/Qwen3-4B",
                "embedding_model_name": "models/bge-m3",
                "device": "auto",
                "torch_dtype": "float16",
                "max_new_tokens": 256,
            },
        )()

        manifest = run_local_qwen3_e0.build_manifest(
            run_id="run-1",
            dataset_path=Path("data/evaluation/gold/generation_eval_set.json"),
            runtime_config_path=Path("config/runtime_local_qwen3_4b.example.json"),
            store_dir=Path("store"),
            out_dir=Path("out"),
            top_k=2,
            debug_top_k=4,
            limit=3,
            runtime_config=runtime_config,
            summary={"sample_count": 3},
            memory_after={"cuda_available": True},
        )

        self.assertEqual("qwen3_base_e0", manifest["pipeline"])
        self.assertEqual("models/Qwen3-4B", manifest["chat_model_name"])
        self.assertEqual(256, manifest["max_new_tokens"])
        self.assertEqual(2, manifest["similarity_top_k"])
        self.assertEqual(3, manifest["limit"])


if __name__ == "__main__":
    unittest.main()
