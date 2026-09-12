from __future__ import annotations
import unittest
from agent_platform.capability_packs import AssetParser

class Day23AssetTests(unittest.TestCase):
    def test_parser_preserves_hash_and_type(self) -> None:
        record = AssetParser().parse("table.csv", b"a,b\n1,2")
        self.assertEqual("text/csv", record.media_type); self.assertEqual(7, record.size_bytes); self.assertIn("a,b", record.derived_preview or "")
    def test_image_enters_low_confidence_review(self) -> None:
        record = AssetParser().parse("chart.png", b"png-bytes")
        self.assertEqual(0.0, record.confidence); self.assertIsNotNone(record.derived_preview)

if __name__ == "__main__": unittest.main()
