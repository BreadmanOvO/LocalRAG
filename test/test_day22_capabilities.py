from __future__ import annotations
import unittest
from agent_platform.integrations import Capability, CapabilityRegistry

class Day22CapabilityTests(unittest.TestCase):
    def test_registry_tracks_modality_provider_and_cost(self) -> None:
        registry = CapabilityRegistry(); registry.register(Capability("vision-ocr", "vision", "vlm-local", 3))
        item = registry.require("vision-ocr")
        self.assertEqual("vision", item.modality); self.assertEqual(3, item.cost_units)
    def test_missing_capability_is_explicit(self) -> None:
        with self.assertRaisesRegex(ValueError, "capability unavailable"): CapabilityRegistry().require("code")

if __name__ == "__main__": unittest.main()
