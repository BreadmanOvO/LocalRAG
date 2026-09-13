"""Multimodal asset intake metadata and immutable derived previews for D23."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

@dataclass(frozen=True)
class AssetRecord:
    asset_id: str
    media_type: str
    content_hash: str
    size_bytes: int
    source_name: str
    derived_preview: str | None = None
    confidence: float | None = None

class AssetParser:
    def parse(self, path: str, content: bytes) -> AssetRecord:
        suffix = Path(path).suffix.lower()
        media_type = {".txt": "text/plain", ".md": "text/markdown", ".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".csv": "text/csv", ".json": "application/json"}.get(suffix, "application/octet-stream")
        if not content: raise ValueError("asset content must not be empty")
        digest = sha256(content).hexdigest()
        preview = None; confidence = None
        if media_type == "text/csv": preview = content.decode("utf-8", errors="replace").splitlines()[0][:500]
        elif media_type == "application/json": preview = content.decode("utf-8", errors="replace")[:500]
        elif media_type.startswith("image/"): preview, confidence = "image preview pending OCR/VLM", 0.0
        return AssetRecord(f"asset-{digest[:16]}", media_type, digest, len(content), Path(path).name, preview, confidence)
