"""Immutable local object-store adapter for the D38 asset intake path."""

from __future__ import annotations

import base64
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .assets import AssetParser, AssetRecord


@dataclass(frozen=True)
class AssetIngestResult:
    record: AssetRecord
    object_path: str
    chunks: tuple[str, ...]
    published: bool = False
    evaluation_requested: bool = False


class LocalObjectStore:
    """Content-addressed object store used until S3/MinIO is configured."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or os.environ.get("LOCALRAG_OBJECT_STORE", "results/object_store")).resolve()
        # Create the backing directory on first write; importing the API must
        # not create runtime artifacts in a source checkout.
        self.parser = AssetParser()

    def ingest(self, filename: str, content: bytes, *, evaluate: bool = False, space_id: str | None = None) -> AssetIngestResult:
        record = self.parser.parse(filename, content)
        directory = self.root / record.content_hash
        self.root.mkdir(parents=True, exist_ok=True)
        directory.mkdir(parents=True, exist_ok=True)
        object_file = directory / "original.bin"
        if object_file.exists() and object_file.read_bytes() != content:
            raise ValueError("content hash collision")
        if not object_file.exists():
            fd, temporary = tempfile.mkstemp(prefix="asset-", dir=directory)
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(content)
                os.replace(temporary, object_file)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        chunks = self._chunks(record, content)
        (directory / "manifest.json").write_text(json.dumps({"record": record.__dict__, "chunks": chunks, "evaluation_requested": evaluate, "space_id": space_id}, ensure_ascii=False, indent=2), encoding="utf-8")
        return AssetIngestResult(record, str(object_file), chunks, False, evaluate)

    def read(self, content_hash: str) -> bytes:
        path = self.root / content_hash / "original.bin"
        if not path.exists():
            raise FileNotFoundError(content_hash)
        return path.read_bytes()

    def read_asset(self, asset_id: str) -> bytes:
        prefix = asset_id.removeprefix("asset-")
        matches = tuple(self.root.glob(f"{prefix}*/original.bin"))
        if len(matches) != 1:
            raise FileNotFoundError(asset_id)
        return matches[0].read_bytes()

    def read_asset_space(self, asset_id: str) -> str | None:
        """Read the persisted space owner without exposing manifest internals."""
        prefix = asset_id.removeprefix("asset-")
        manifests = tuple(self.root.glob(f"{prefix}*/manifest.json"))
        if len(manifests) != 1:
            raise FileNotFoundError(asset_id)
        payload = json.loads(manifests[0].read_text(encoding="utf-8"))
        value = payload.get("space_id")
        return str(value) if value else None

    @staticmethod
    def _chunks(record: AssetRecord, content: bytes) -> tuple[str, ...]:
        if record.media_type.startswith("text/") or record.media_type == "application/json":
            text = content.decode("utf-8", errors="replace")
            return tuple(text[index:index + 800] for index in range(0, len(text), 800)) or ("",)
        return (record.derived_preview or "binary asset pending modality parser",)
