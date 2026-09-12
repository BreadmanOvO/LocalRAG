"""Generation manifests and atomic publish pointers for D24."""
from __future__ import annotations
from dataclasses import dataclass
from threading import RLock

@dataclass(frozen=True)
class GenerationManifest:
    generation_id: str
    asset_hashes: tuple[str, ...]
    vector_index_version: str
    lexical_index_version: str
    complete: bool = True

class PublishService:
    def __init__(self) -> None: self._lock = RLock(); self._generations: dict[str, GenerationManifest] = {}; self._pointers: dict[str, str] = {}
    def stage(self, manifest: GenerationManifest) -> GenerationManifest:
        if not manifest.complete: raise ValueError("incomplete generation cannot publish")
        with self._lock: self._generations[manifest.generation_id] = manifest
        return manifest
    def publish(self, space_id: str, generation_id: str) -> GenerationManifest:
        with self._lock:
            manifest = self._generations.get(generation_id)
            if manifest is None or not manifest.complete: raise ValueError("generation is not ready")
            self._pointers[space_id] = generation_id
            return manifest
    def current(self, space_id: str) -> GenerationManifest:
        with self._lock:
            return self._generations[self._pointers[space_id]]
