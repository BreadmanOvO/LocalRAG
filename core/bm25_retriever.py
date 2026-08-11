"""BM25-only retrieval over the active Chroma collection."""
from __future__ import annotations

import heapq
import re
from typing import Any

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

BM25_BATCH_SIZE = 500
TOKEN_PATTERN = re.compile(r"[a-z0-9_]+|[\u3400-\u4dbf\u4e00-\u9fff]+")
CJK_PATTERN = re.compile(r"^[\u3400-\u4dbf\u4e00-\u9fff]+$")


def _tokenize(text: str) -> list[str]:
    tokens = []
    for segment in TOKEN_PATTERN.findall(text.lower()):
        if not CJK_PATTERN.fullmatch(segment):
            tokens.append(segment)
            continue
        if len(segment) == 1:
            tokens.append(segment)
            continue
        tokens.extend(segment[index : index + 2] for index in range(len(segment) - 1))
    return tokens


class BM25Retriever:
    """In-memory BM25 index with an explicit refresh lifecycle.

    The index is a snapshot of the Chroma collection at construction time.
    Call ``refresh()`` after corpus ingestion or replacement.
    """

    def __init__(self, vector_store: Any) -> None:
        self.vector_store = vector_store
        self._bm25: BM25Okapi | None = None
        self._documents: list[Document] = []
        self._ids: list[str] = []
        self.refresh()

    @property
    def documents(self) -> list[Document]:
        return self._documents

    @property
    def ids(self) -> list[str]:
        return self._ids

    def refresh(self) -> None:
        documents: list[Document] = []
        ids: list[str] = []
        collection = self.vector_store._collection
        offset = 0
        while True:
            result = collection.get(
                include=["documents", "metadatas"],
                limit=BM25_BATCH_SIZE,
                offset=offset,
            )
            batch_ids = result["ids"]
            if not batch_ids:
                break

            ids.extend(batch_ids)
            documents.extend(
                Document(page_content=text, metadata=metadata or {})
                for text, metadata in zip(result["documents"], result["metadatas"])
            )
            if len(batch_ids) < BM25_BATCH_SIZE:
                break
            offset += BM25_BATCH_SIZE

        self._ids = ids
        self._documents = documents
        self._bm25 = (
            BM25Okapi([_tokenize(document.page_content) for document in documents])
            if documents
            else None
        )

    def retrieve_scored(self, query: str, *, k: int) -> list[tuple[Document, float]]:
        if k <= 0:
            raise ValueError("k must be positive")
        if self._bm25 is None or not self._documents:
            return []

        scores = self._bm25.get_scores(_tokenize(query))
        top_indices = heapq.nlargest(
            min(k, len(scores)),
            range(len(scores)),
            key=scores.__getitem__,
        )
        max_score = max((float(scores[index]) for index in top_indices), default=0.0)
        if max_score <= 0:
            return []
        return [
            (
                self._documents[index],
                float(scores[index] / max_score) if max_score > 0 else 0.0,
            )
            for index in top_indices
        ]
