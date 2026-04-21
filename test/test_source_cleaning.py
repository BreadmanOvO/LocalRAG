import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from source_catalog import SourceDocument
from source_cleaning import (
    assemble_ocr_page_text,
    assemble_ocr_page_text_from_items,
    build_registry_entry,
    extract_candidate_snippets,
    is_low_signal_text,
    normalize_candidate_text,
    render_clean_markdown,
    write_source_registry,
)


class SourceRenderingTests(unittest.TestCase):
    def setUp(self):
        self.doc = SourceDocument(
            source_id="sample-001",
            title="Sample Source",
            doc_type="official_doc",
            category="apollo",
            language="en",
            raw_relpath="data/sources/raw/apollo/sample.pdf",
            clean_relpath="data/sources/apollo/sample.md",
            origin_url="https://example.com/sample",
            version="Sample v1",
            topic_tags=("perception", "sensor_fusion"),
            summary_hint="Sample summary that should appear in the markdown output.",
        )
        self.page_texts = [
            "Overview paragraph with enough content to become a key point and a structured note. " * 2,
            "Detailed paragraph describing module responsibilities and data flow in enough detail for evidence extraction. " * 2,
            "Constraint paragraph describing operational behavior and interface expectations in enough detail for evidence extraction. " * 2,
        ]

    def test_render_clean_markdown_contains_required_sections(self):
        markdown = render_clean_markdown(self.doc, self.page_texts)
        self.assertIn("# Sample Source", markdown)
        self.assertIn("## Summary", markdown)
        self.assertIn("## Key points", markdown)
        self.assertIn("## Structured notes", markdown)
        self.assertIn("## Evidence-ready excerpts", markdown)
        self.assertIn("## Cleaning notes", markdown)
        self.assertIn("[p.1]", markdown)

    def test_build_registry_entry_points_to_clean_markdown(self):
        entry = build_registry_entry(self.doc)
        self.assertEqual("sample-001", entry["source_id"])
        self.assertEqual("data/sources/apollo/sample.md", entry["path_or_url"])
        self.assertEqual("data/sources/raw/apollo/sample.pdf", entry["raw_path"])
        self.assertEqual("official_doc", entry["doc_type"])
        self.assertEqual(["perception", "sensor_fusion"], entry["topic_tags"])

    def test_write_source_registry_creates_parent_directory(self):
        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "data" / "evaluation" / "shared" / "source_registry.json"
            write_source_registry(output_path, [build_registry_entry(self.doc)])
            data = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("sample-001", data[0]["source_id"])

    def test_normalize_candidate_text_strips_apollo_nav_noise(self):
        raw = (
            "Apollo开放平台文档 Q搜索 发版说明 Apollo预测能力介绍 安装说明 快速上手 更新时间：2022-05-05 "
            "上机使用教程 概览 本文为开发者介绍Apollo预测模块的基本知识，包括预测模块在自动驾驶系统中的主要作用。 "
            "文档意见反馈 如果您在使用文档的过程中，遇到任何问题，请反馈相关问题。"
        )
        cleaned = normalize_candidate_text(raw)
        self.assertNotIn("Apollo开放平台文档", cleaned)
        self.assertNotIn("Q搜索", cleaned)
        self.assertNotIn("文档意见反馈", cleaned)
        self.assertIn("本文为开发者介绍Apollo预测模块的基本知识", cleaned)

    def test_normalize_candidate_text_strips_msf_figure_label_noise(self):
        raw = (
            "MSF定位模块原理 这里重点介绍（Multi-SensorFusion）定位模块实现原理，系统框图如下图所示： "
            "ing with VCV position/velcity/attitu (AA) axueyen-oo pue "
            "MSF定位系统以多种传感器数据和离线制作的高精度Lidar定位地图为输入。"
        )
        cleaned = normalize_candidate_text(raw)
        self.assertIn("MSF定位系统以多种传感器数据", cleaned)
        self.assertNotIn("ing with VCV", cleaned)
        self.assertNotIn("position/velcity/attitu", cleaned)

    def test_is_low_signal_text_flags_qr_contact_noise(self):
        noisy = (
            "Director Sr.Engineering Manager Apollo Platform FollowUs Scan the QR code "
            "(WeChat: Apollodev) to add us to contacts."
        )
        self.assertTrue(is_low_signal_text(noisy))

    def test_assemble_ocr_page_text_keeps_multicolumn_lines_separate(self):
        lines = [
            "Through this course, you will be able to identify key parts of self-driving cars and get to know Apollo architecture.",
            "You will be able to utilize Apollo HD Map, localization, perception, prediction, planning and control, and start the learning path of building a self-driving car.",
            "Self-driving Overview",
            "HDMap",
            "Localization",
            "Perception",
            "Identify key parts of self-driving cars,",
            "Get to know how high-definition maps",
            "Learn how the vehicle localizes itself",
            "Identify different perception tasks such",
        ]
        text = assemble_ocr_page_text(lines)
        snippets = extract_candidate_snippets(text)
        self.assertTrue(any("Through this course" in snippet for snippet in snippets))
        self.assertTrue(any("You will be able to utilize Apollo HD Map" in snippet for snippet in snippets))
        self.assertFalse(any("Self-driving Overview HDMap Localization Perception" in snippet for snippet in snippets))

    def test_assemble_ocr_page_text_keeps_short_lowercase_continuation_line(self):
        lines = [
            "Localization",
            "Learn how the vehicle localizes itself",
            "with single-digit-centimeter-level",
            "accuracy.",
        ]
        text = assemble_ocr_page_text(lines)
        self.assertIn("with single-digit-centimeter-level accuracy.", text)

    def test_assemble_ocr_page_text_drops_interleaved_nav_lines(self):
        lines = [
            "本文档介绍Apollo定位模块以及ApolloMSF（Multi-SensorFusion）的原理。",
            "Apollo定位模块",
            "上机实践Apollo视觉感知能力",
            "高精度、高鲁棒性的定位系统是自动驾驶系统不可或缺的基础模块。Apollo定位模块针对不同的应用需求提供了三",
            "上机实践Apollo激光雷达感知能",
            "力",
            "种不同实现方式的定位模块。",
        ]
        text = assemble_ocr_page_text(lines)
        self.assertIn("本文档介绍Apollo定位模块以及ApolloMSF", text)
        self.assertIn("种不同实现方式的定位模块。", text)
        self.assertNotIn("上机实践Apollo视觉感知能力", text)

    def test_assemble_ocr_page_text_from_items_uses_columns_to_drop_nav(self):
        items = [
            ([[291, 228], [729, 228], [729, 247], [291, 247]], "本文档介绍Apollo定位模块以及ApolloMSF（Multi-SensorFusion）的原理。"),
            ([[84, 263], [257, 263], [257, 280], [84, 280]], "实时通信框架CyberRT的使用>"),
            ([[291, 266], [440, 266], [440, 293], [291, 293]], "Apollo定位模块"),
            ([[86, 294], [249, 294], [249, 311], [86, 311]], "上机实践Apollo视觉感知能力"),
            ([[291, 311], [927, 311], [927, 330], [291, 330]], "高精度、高鲁棒性的定位系统是自动驾驶系统不可或缺的基础模块。Apollo定位模块针对不同的应用需求提供了三"),
            ([[86, 327], [263, 327], [263, 344], [86, 344]], "上机实践Apollo激光雷达感知能"),
            ([[86, 342], [100, 342], [100, 355], [86, 355]], "力"),
            ([[291, 336], [451, 336], [451, 352], [291, 352]], "种不同实现方式的定位模块。"),
        ]
        text = assemble_ocr_page_text_from_items(items)
        self.assertIn("本文档介绍Apollo定位模块以及ApolloMSF", text)
        self.assertIn("种不同实现方式的定位模块。", text)
        self.assertNotIn("上机实践Apollo视觉感知能力", text)
        self.assertNotIn("实时通信框架CyberRT的使用", text)

    def test_assemble_ocr_page_text_from_items_drops_msf_side_nav_lines(self):
        items = [
            ([[290, 451], [577, 451], [577, 471], [290, 471]], "MSF（Multi-SensorFusion）定位模块"),
            ([[102, 466], [253, 466], [253, 483], [102, 483]], "使用MSFLocalizer的多传感"),
            ([[102, 481], [194, 481], [194, 497], [102, 497]], "器融合定位实践"),
            ([[290, 490], [920, 490], [920, 510], [290, 510]], "结合GPS+IMU+Lidar实现的多传感器融合全局定位导航系统，利用多传感器优缺点的互补，实现高精度、高鲁棒性的定位能力。"),
            ([[102, 520], [253, 520], [253, 537], [102, 537]], "基于MSFVisualizer的Apollo"),
            ([[102, 538], [194, 538], [194, 555], [102, 555]], "定位可视化实践"),
            ([[290, 522], [920, 522], [920, 542], [290, 542]], "对于GPS失效或者Lidar地图环境变更场景具备一定的冗余处理能力。"),
        ]
        text = assemble_ocr_page_text_from_items(items)
        self.assertIn("MSF（Multi-SensorFusion）定位模块", text)
        self.assertIn("对于GPS失效或者Lidar地图环境变更场景具备一定的冗余处理能力。", text)
        self.assertNotIn("使用MSFLocalizer", text)
        self.assertNotIn("MSFVisualizer", text)

    def test_assemble_ocr_page_text_from_items_drops_chart_label_cluster(self):
        items = [
            ([[290, 451], [577, 451], [577, 471], [290, 471]], "MSF（Multi-SensorFusion）定位模块"),
            ([[290, 490], [920, 490], [920, 510], [290, 510]], "结合GPS+IMU+Lidar实现的多传感器融合全局定位导航系统，利用多传感器优缺点的互补，实现高精度、高鲁棒性的定位能力。"),
            ([[290, 560], [700, 560], [700, 580], [290, 580]], "Specific force and rotation rate"),
            ([[750, 560], [1010, 560], [1010, 580], [750, 580]], "Predicted prior PVA with VCV"),
            ([[290, 610], [600, 610], [600, 630], [290, 630]], "de (PVA) with varli"),
            ([[290, 660], [960, 660], [960, 680], [290, 680]], "MSF定位系统以多种传感器数据和离线制作的高精度Lidar定位地图为输入，其中GNSSLocalization模块以车端"),
        ]
        text = assemble_ocr_page_text_from_items(items)
        self.assertIn("MSF定位系统以多种传感器数据", text)
        self.assertNotIn("Specific force and rotation rate", text)
        self.assertNotIn("Predicted prior PVA with VCV", text)
        self.assertNotIn("de (PVA) with varli", text)

    def test_is_low_signal_text_flags_detail_reference_noise(self):
        noisy = "详情参见 Robust and Precise Vehicle Localization Based on Multi-Sensor Fusion in Diverse City Scenes"
        self.assertTrue(is_low_signal_text(noisy))


if __name__ == "__main__":
    unittest.main()
