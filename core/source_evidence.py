from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from config import settings as config
from utils.path_tools import get_abs_path


DEFAULT_REGISTRY_PATH = "data/evaluation/shared/source_registry.json"
_UNSET = object()
_ENGLISH_STOP_WORDS = {
    "about",
    "and",
    "are",
    "for",
    "from",
    "has",
    "how",
    "into",
    "that",
    "the",
    "this",
    "uses",
    "was",
    "what",
    "when",
    "where",
    "which",
    "with",
}


def _clean_text(value: str, field_name: str, *, max_length: int = 4000) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if len(normalized) > max_length:
        raise ValueError(f"{field_name} must not exceed {max_length} characters")
    return normalized


def _bounded_int(value: int, field_name: str, *, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{field_name} must be between {minimum} and {maximum}")
    return value


def _chunk_order(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _terms(text: str) -> set[str]:
    normalized = text.lower()
    terms = {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9._+-]*", normalized)
        if len(token) >= 2 and token not in _ENGLISH_STOP_WORDS
    }
    for sequence in re.findall(r"[\u4e00-\u9fff]+", normalized):
        if len(sequence) == 1:
            terms.add(sequence)
        else:
            terms.update(sequence[index : index + 2] for index in range(len(sequence) - 1))
    return terms


def _term_coverage(query: str, content: str) -> float:
    query_terms = _terms(query)
    if not query_terms:
        return 0.0
    return len(query_terms & _terms(content)) / len(query_terms)


def _snippet(content: str, *, limit: int = 1600) -> str:
    normalized = content.strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit].rstrip() + "..."


@dataclass(frozen=True)
class SourceChunk:
    record_id: str
    source_id: str
    content: str
    metadata: dict[str, Any]

    @property
    def chunk_order(self) -> int | None:
        return _chunk_order(self.metadata.get("chunk_order"))

    @property
    def locator(self) -> str:
        return str(self.metadata.get("locator") or "unknown")

    @property
    def chunk_strategy(self) -> str:
        return str(self.metadata.get("chunk_strategy") or "unknown")

    def to_dict(self, *, score: float | None = None) -> dict[str, Any]:
        result = {
            "source_id": self.source_id,
            "chunk_order": self.chunk_order,
            "locator": self.locator,
            "chunk_strategy": self.chunk_strategy,
            "content": _snippet(self.content),
        }
        if score is not None:
            result["term_coverage"] = round(score, 3)
        return result


class SourceEvidenceService:
    """Read source metadata and chunks without loading an embedding model."""

    def __init__(
        self,
        *,
        registry_path: str | Path | None = None,
        registry_entries: Iterable[dict[str, Any]] | None = None,
        collection: Any = _UNSET,
    ) -> None:
        self.registry_path = Path(
            registry_path or get_abs_path(DEFAULT_REGISTRY_PATH)
        ).resolve()
        self._registry_by_id = (
            self._index_registry(registry_entries) if registry_entries is not None else None
        )
        self._collection = collection
        self._client = None

    @staticmethod
    def _index_registry(entries: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        indexed = {}
        for entry in entries:
            source_id = str(entry.get("source_id") or "").strip()
            if source_id:
                indexed[source_id] = dict(entry)
        return indexed

    def _registry(self) -> dict[str, dict[str, Any]]:
        if self._registry_by_id is None:
            entries = json.loads(self.registry_path.read_text(encoding="utf-8"))
            if not isinstance(entries, list):
                raise ValueError("source registry must contain a list")
            self._registry_by_id = self._index_registry(entries)
        return self._registry_by_id

    def _get_collection(self):
        if self._collection is _UNSET:
            import chromadb

            self._client = chromadb.PersistentClient(
                path=get_abs_path(config.persist_directory),
            )
            self._collection = self._client.get_collection(config.collection_name)
        if self._collection is None:
            raise RuntimeError("knowledge collection is unavailable")
        return self._collection

    def get_chunks(self, source_id: str) -> list[SourceChunk]:
        source_id = _clean_text(source_id, "source_id", max_length=256)
        result = self._get_collection().get(
            where={"source_id": source_id},
            include=["documents", "metadatas"],
        )
        record_ids = result.get("ids") or []
        documents = result.get("documents") or []
        metadatas = result.get("metadatas") or []
        chunks = []
        for index, content in enumerate(documents):
            metadata = dict(metadatas[index] or {}) if index < len(metadatas) else {}
            record_id = str(record_ids[index]) if index < len(record_ids) else str(index)
            chunks.append(
                SourceChunk(
                    record_id=record_id,
                    source_id=str(metadata.get("source_id") or source_id),
                    content=str(content or ""),
                    metadata=metadata,
                )
            )
        return sorted(
            chunks,
            key=lambda chunk: (
                chunk.chunk_order is None,
                chunk.chunk_order if chunk.chunk_order is not None else 0,
                chunk.locator,
                chunk.record_id,
            ),
        )

    def inspect_source(self, source_id: str, *, max_chunks: int = 3) -> dict[str, Any]:
        source_id = _clean_text(source_id, "source_id", max_length=256)
        max_chunks = _bounded_int(max_chunks, "max_chunks", minimum=1, maximum=5)
        entry = self._registry().get(source_id)
        chunks = self.get_chunks(source_id)
        if entry is None and not chunks:
            return {"found": False, "source_id": source_id}

        metadata = dict(entry or (chunks[0].metadata if chunks else {}))
        metadata["source_id"] = source_id
        return {
            "found": True,
            "source": metadata,
            "chunk_count": len(chunks),
            "chunks": [chunk.to_dict() for chunk in chunks[:max_chunks]],
        }

    def expand_context(
        self,
        source_id: str,
        chunk_order: int,
        *,
        before: int = 1,
        after: int = 1,
        chunk_strategy: str = "",
    ) -> dict[str, Any]:
        source_id = _clean_text(source_id, "source_id", max_length=256)
        chunk_order = _bounded_int(chunk_order, "chunk_order", minimum=0, maximum=1_000_000)
        before = _bounded_int(before, "before", minimum=0, maximum=3)
        after = _bounded_int(after, "after", minimum=0, maximum=3)
        strategy = chunk_strategy.strip() if isinstance(chunk_strategy, str) else ""

        chunks = self.get_chunks(source_id)
        if strategy:
            chunks = [chunk for chunk in chunks if chunk.chunk_strategy == strategy]
        target_index = next(
            (index for index, chunk in enumerate(chunks) if chunk.chunk_order == chunk_order),
            None,
        )
        if target_index is None:
            return {
                "found": False,
                "source_id": source_id,
                "chunk_order": chunk_order,
                "available_chunk_orders": [
                    chunk.chunk_order for chunk in chunks if chunk.chunk_order is not None
                ][:20],
            }

        start = max(0, target_index - before)
        end = min(len(chunks), target_index + after + 1)
        return {
            "found": True,
            "source_id": source_id,
            "target_chunk_order": chunk_order,
            "chunks": [chunk.to_dict() for chunk in chunks[start:end]],
        }

    def compare_sources(
        self,
        source_ids: list[str],
        *,
        focus: str = "",
        max_chunks_per_source: int = 2,
    ) -> dict[str, Any]:
        if not isinstance(source_ids, list):
            raise TypeError("source_ids must be a list")
        unique_source_ids = []
        for source_id in source_ids:
            normalized = _clean_text(source_id, "source_id", max_length=256)
            if normalized not in unique_source_ids:
                unique_source_ids.append(normalized)
        if not 2 <= len(unique_source_ids) <= 5:
            raise ValueError("source_ids must contain between 2 and 5 unique values")
        max_chunks_per_source = _bounded_int(
            max_chunks_per_source,
            "max_chunks_per_source",
            minimum=1,
            maximum=3,
        )
        normalized_focus = focus.strip() if isinstance(focus, str) else ""

        sources = []
        for source_id in unique_source_ids:
            entry = self._registry().get(source_id)
            chunks = self.get_chunks(source_id)
            ranked = [(_term_coverage(normalized_focus, chunk.content), chunk) for chunk in chunks]
            if normalized_focus:
                ranked.sort(
                    key=lambda item: (
                        -item[0],
                        item[1].chunk_order is None,
                        item[1].chunk_order if item[1].chunk_order is not None else 0,
                    )
                )
            selected = ranked[:max_chunks_per_source]
            metadata = dict(entry or (chunks[0].metadata if chunks else {}))
            metadata["source_id"] = source_id
            sources.append(
                {
                    "found": bool(entry or chunks),
                    "source": metadata,
                    "chunk_count": len(chunks),
                    "chunks": [chunk.to_dict(score=score) for score, chunk in selected],
                }
            )
        return {"focus": normalized_focus, "sources": sources}

    def check_evidence(
        self,
        claim: str,
        documents: Iterable[dict[str, Any]],
        *,
        source_ids: list[str] | None = None,
        max_candidates: int = 3,
    ) -> dict[str, Any]:
        claim = _clean_text(claim, "claim")
        max_candidates = _bounded_int(
            max_candidates,
            "max_candidates",
            minimum=1,
            maximum=5,
        )
        allowed_sources = None
        if source_ids:
            allowed_sources = {
                _clean_text(source_id, "source_id", max_length=256)
                for source_id in source_ids
            }

        ranked = []
        for document in documents:
            if not isinstance(document, dict):
                continue
            source_id = str(document.get("source_id") or "").strip()
            if allowed_sources is not None and source_id not in allowed_sources:
                continue
            content = str(document.get("content") or "")
            ranked.append((_term_coverage(claim, content), dict(document)))
        ranked.sort(key=lambda item: item[0], reverse=True)

        positive = [item for item in ranked if item[0] > 0]
        if not ranked:
            status = "no_retrieval"
        elif not positive:
            status = "insufficient_overlap"
        elif positive[0][0] < 0.35:
            status = "weak_candidate"
        else:
            status = "candidate_found"

        candidates = []
        for score, document in positive[:max_candidates]:
            candidates.append(
                {
                    "source_id": document.get("source_id", ""),
                    "chunk_order": _chunk_order(document.get("chunk_order")),
                    "locator": document.get("locator") or "unknown",
                    "term_coverage": round(score, 3),
                    "content": _snippet(str(document.get("content") or "")),
                }
            )
        return {
            "claim": claim,
            "status": status,
            "searched_document_count": len(ranked),
            "candidates": candidates,
        }
