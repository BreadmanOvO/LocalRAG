from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_REL_PATH = "data/evaluation/shared/source_registry.json"


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    title: str
    doc_type: str
    category: str
    language: str
    raw_relpath: str
    clean_relpath: str
    origin_url: str
    version: str
    topic_tags: tuple[str, ...]
    summary_hint: str

    @property
    def raw_path(self) -> Path:
        return ROOT / self.raw_relpath

    @property
    def clean_path(self) -> Path:
        return ROOT / self.clean_relpath


def _summary_hint(entry: dict[str, object]) -> str:
    notes = str(entry.get("notes") or "").strip()
    if notes:
        return notes
    title = str(entry["title"])
    doc_type = str(entry["doc_type"])
    return f"{doc_type.replace('_', ' ').title()} source document: {title}."


@lru_cache(maxsize=1)
def _load_source_documents() -> tuple[SourceDocument, ...]:
    registry_path = ROOT / REGISTRY_REL_PATH
    entries = json.loads(registry_path.read_text(encoding="utf-8"))
    documents = []
    for entry in entries:
        documents.append(
            SourceDocument(
                source_id=str(entry["source_id"]),
                title=str(entry["title"]),
                doc_type=str(entry["doc_type"]),
                category=str(entry["category"]),
                language=str(entry["language"]),
                raw_relpath=str(entry["raw_path"]),
                clean_relpath=str(entry["path_or_url"]),
                origin_url=str(entry.get("origin_url") or "unknown"),
                version=str(entry.get("version") or "unknown"),
                topic_tags=tuple(str(tag) for tag in entry.get("topic_tags", ())),
                summary_hint=_summary_hint(entry),
            )
        )
    return tuple(documents)


SOURCE_DOCUMENTS: tuple[SourceDocument, ...] = _load_source_documents()


def all_documents() -> tuple[SourceDocument, ...]:
    return SOURCE_DOCUMENTS


def documents_for_category(category: str) -> tuple[SourceDocument, ...]:
    return tuple(doc for doc in SOURCE_DOCUMENTS if doc.category == category)
