from __future__ import annotations

import unittest

from agent_platform.capability_packs import OcrVlmService


class MultimodalTests(unittest.TestCase):
    def test_text_is_builtin_and_image_without_provider_is_explicit(self) -> None:
        service = OcrVlmService()
        self.assertEqual("completed", service.extract(b"hello", media_type="text/plain").status)
        image = service.extract(b"png", media_type="image/png")
        self.assertEqual("capability_not_ready", image.status)
        self.assertEqual("", image.text)

    def test_vlm_result_keeps_low_confidence_boundary(self) -> None:
        service = OcrVlmService(vlm=lambda content, instruction: "table result")
        result = service.extract(b"png", media_type="image/png", instruction="read table")
        self.assertEqual("completed", result.status)
        self.assertEqual(0.75, result.confidence)


if __name__ == "__main__":
    unittest.main()
