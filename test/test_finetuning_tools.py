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
from scripts import prepare_sft_e5_dataset
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
        distractor["evidence"][0]["source_id"] = "paper-999"
        distractor["evidence"][0]["locator"] = "page=9"

        row = prepare_sft_e3_draft.build_strict_distractor_row(
            row_id="e3-draft-distractor-001",
            target_record=target,
            distractor_record=distractor,
            question="CRN 融合了哪些传感器？",
            answer="CRN 融合了摄像头和雷达。",
            review_focus="strict_distractor_context",
        )

        self.assertEqual("strict_distractor_target_only_citation", row["metadata"]["data_type"])
        self.assertIn("source_id=paper-030", row["input"])
        self.assertIn("source_id=paper-999", row["input"])
        self.assertIn("paper-030 page=1", row["output"])
        self.assertNotIn("paper-999 page=9", row["output"])


class PrepareSftE3DatasetTests(unittest.TestCase):
    def test_build_e3_train_rows_merges_e2_and_hardcase_rows(self):
        e2_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-001"),
            dataset_version="v1.3-e2",
            data_type="normal_grounded_qa",
        )
        hardcase_row = prepare_sft_e3_draft.build_partial_context_row(
            row_id="e3-draft-partial-001",
            source_record=_sample("train-002"),
            question="资料是否说明 CRN 已量产？",
            answer="资料未说明 CRN 已量产，不能根据资料确定量产情况。",
            review_focus="partial_context_insufficient_metric",
        )

        merged = prepare_sft_e3_dataset.build_e3_train_rows(
            e2_rows=[e2_row],
            hardcase_rows=[hardcase_row],
            dataset_version="v1.3-e3",
        )

        self.assertEqual(2, len(merged))
        self.assertEqual("v1.3-e3", merged[0]["metadata"]["dataset_version"])
        self.assertEqual("normal_grounded_qa", merged[0]["metadata"]["data_type"])
        self.assertEqual("e3_hardcase_partial_context_insufficient_metric", merged[1]["metadata"]["data_type"])


class PrepareSftE4DraftTests(unittest.TestCase):
    def test_build_multi_metric_partial_context_row_refuses_missing_metrics(self):
        source = _sample("train-001")
        row = prepare_sft_e4_draft.build_multi_metric_partial_context_row(
            row_id="e4-draft-001",
            source_record=source,
            question="使用 4096 个 Top-K 查询时，MFA 延迟、AP 和 ATE 分别发生什么变化？",
            supported_claim="资料只说明 4096 个查询会让 MFA 延迟降低 76.4%。",
            missing_metrics=["AP", "ATE"],
            review_focus="multi_metric_partial_context_no_direction_guess",
            quote="using 4096 size queries reduce the latency of MFA by 76.4%.",
        )

        self.assertEqual("e4-draft-001", row["metadata"]["source_sample_id"])
        self.assertEqual("multi_metric_partial_context_refusal", row["metadata"]["data_type"])
        self.assertEqual(["train-001"], row["metadata"]["source_record_ids"])
        self.assertIn("不能根据资料确定 AP 或 ATE 是提升还是下降", row["output"])
        self.assertIn("paper-030 page=1", row["output"])


class PrepareSftE4DatasetTests(unittest.TestCase):
    def test_build_e4_dataset_merges_e3_train_with_hardcase_slice(self):
        e3_row = prepare_sft_dataset.build_llamafactory_record(
            _sample("train-001"),
            dataset_version="v1.3-e3",
            data_type="normal_grounded_qa",
        )
        hardcase_row = prepare_sft_e4_draft.build_multi_metric_partial_context_row(
            row_id="e4-draft-001",
            source_record=_sample("train-002"),
            question="资料是否说明 CRN 已量产？",
            supported_claim="资料只说明 CRN 融合了摄像头和雷达。",
            missing_metrics=["量产情况"],
            review_focus="multi_metric_partial_context_no_missing_value_guess",
        )

        merged = prepare_sft_e4_dataset.build_e4_train_rows(
            e3_rows=[e3_row],
            hardcase_rows=[hardcase_row],
            dataset_version="v1.3-e4",
        )

        self.assertEqual(2, len(merged))
        self.assertEqual("v1.3-e4", merged[0]["metadata"]["dataset_version"])
        self.assertEqual("normal_grounded_qa", merged[0]["metadata"]["data_type"])
        self.assertEqual("e4_hardcase_multi_metric_partial_context_refusal", merged[1]["metadata"]["data_type"])
        self.assertEqual("v1.3-e4", merged[1]["metadata"]["dataset_version"])


class PrepareSftE5DatasetTests(unittest.TestCase):
    def test_build_pairwise_contrast_row_creates_complete_and_partial_outputs(self):
        source = _sample("train-001")
        source["metadata"]["source_sample_id"] = "e5-source-001"
        source["metadata"]["target_source_id"] = "paper-030"
        row = prepare_sft_e5_dataset.build_pairwise_contrast_row(
            row_id="e5-pairwise-001",
            source_record=source,
            question="使用 4096 个 Top-K 查询时，MFA 延迟、AP 和 ATE 分别发生什么变化？",
            complete_supported_claim="资料说明 4096 个查询会让 MFA 延迟降低 76.4%，从 21.01ms 降到 4.96ms。",
            partial_supported_claim="资料只说明 4096 个查询会让 MFA 延迟降低 76.4%。",
            missing_metrics=["AP", "ATE"],
            review_focus="pairwise_complete_vs_partial_no_direction_guess",
            quote="using 4096 size queries reduce the latency of MFA by 76.4% (21.01ms to 4.96ms) on 256 × 256 size BEV grid.",
        )

        self.assertEqual("e5-pairwise-001-complete", row["metadata"]["source_sample_id"])
        self.assertEqual("pairwise_complete_context", row["metadata"]["data_type"])
        self.assertEqual("complete_answer", row["metadata"]["expected_behavior"])
        self.assertEqual("partial_refuse", row["contrast_output"]["metadata"]["expected_behavior"])
        self.assertIn("不能根据资料确定 AP 或 ATE 是提升还是下降", row["contrast_output"]["output"])
        self.assertIn("paper-030 page=1", row["output"])
