"""Explicit OCR/VLM capability boundary for asset-derived evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class ModalityResult:
    text: str
    confidence: float
    provider: str
    status: str
    evidence_locator: str = ""


class OcrVlmService:
    """Use injected OCR/VLM providers; never silently treat an image as text."""

    def __init__(self, *, ocr: Callable[[bytes], str] | None = None, vlm: Callable[[bytes, str], str] | None = None) -> None:
        self._ocr = ocr
        self._vlm = vlm

    def extract(self, content: bytes, *, media_type: str, instruction: str = "") -> ModalityResult:
        if media_type.startswith("text/") or media_type == "application/json":
            return ModalityResult(content.decode("utf-8", errors="replace"), 1.0, "builtin-text", "completed")
        if media_type.startswith("image/"):
            if self._vlm is not None:
                return ModalityResult(self._vlm(content, instruction), 0.75, "injected-vlm", "completed")
            if self._ocr is not None:
                return ModalityResult(self._ocr(content), 0.45, "injected-ocr", "completed")
            return ModalityResult("", 0.0, "none", "capability_not_ready", "image")
        return ModalityResult("", 0.0, "none", "unsupported_media", media_type)
