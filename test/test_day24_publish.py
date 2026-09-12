from __future__ import annotations
import unittest
from agent_platform.capability_packs.publishing import GenerationManifest, PublishService

class Day24PublishTests(unittest.TestCase):
    def test_publish_switches_complete_generation_atomically(self) -> None:
        service = PublishService(); service.stage(GenerationManifest("gen-1", ("hash-1",), "vec-1", "bm25-1")); service.publish("space-demo", "gen-1")
        self.assertEqual("gen-1", service.current("space-demo").generation_id)
    def test_incomplete_generation_cannot_publish(self) -> None:
        with self.assertRaises(ValueError): PublishService().stage(GenerationManifest("gen-x", (), "vec", "bm25", complete=False))

if __name__ == "__main__": unittest.main()
