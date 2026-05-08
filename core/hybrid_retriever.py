from __future__ import annotations

import re
from typing import Any

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


class HybridRetriever:
    def __init__(
        self,
        vector_store: Any,
        *,
        alpha: float = 0.7,
        dense_top_k: int = 20,
        sparse_top_k: int = 20,
        final_top_k: int = 5,
    ) -> None:
        self.vector_store = vector_store
        self.alpha = alpha
        self.dense_top_k = dense_top_k
        self.sparse_top_k = sparse_top_k
        self.final_top_k = final_top_k

        self._bm25: BM25Okapi | None = None
        self._bm25_docs: list[Document] = []
        self._bm25_ids: list[str] = []
        self._build_bm25_index()

    def _build_bm25_index(self) -> None:
        collection = self.vector_store._collection
        result = collection.get(include=["documents", "metadatas"])
        if not result["ids"]:
            return

        self._bm25_ids = result["ids"]
        self._bm25_docs = [
            Document(page_content=text, metadata=meta or {})
            for text, meta in zip(result["documents"], result["metadatas"])
        ]
        tokenized = [_tokenize(doc.page_content) for doc in self._bm25_docs]
        self._bm25 = BM25Okapi(tokenized)

    def _dense_search(self, query: str, k: int) -> list[tuple[Document, float]]:
        return self.vector_store.similarity_search_with_relevance_scores(query, k=k)

    def _sparse_search(self, query: str, k: int) -> list[tuple[Document, float]]:
        if self._bm25 is None or not self._bm25_docs:
            return []
        scores = self._bm25.get_scores(_tokenize(query))
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        max_score = max(scores[i] for i in top_indices) if top_indices else 1.0
        return [
            (self._bm25_docs[i], float(scores[i] / max_score) if max_score > 0 else 0.0)
            for i in top_indices
        ]

    @staticmethod
    def _normalize_scores(results: list[tuple[Document, float]]) -> list[tuple[Document, float]]:
        if not results:
            return []
        max_score = max(score for _, score in results)
        if max_score <= 0:
            return [(doc, 0.0) for doc, _ in results]
        return [(doc, score / max_score) for doc, score in results]

    def _merge_results(
        self,
        dense_results: list[tuple[Document, float]],
        sparse_results: list[tuple[Document, float]],
    ) -> list[tuple[Document, float]]:
        doc_scores: dict[str, tuple[Document, float]] = {}

        for doc, score in dense_results:
            key = doc.page_content[:200]
            doc_scores[key] = (doc, self.alpha * score)

        for doc, score in sparse_results:
            key = doc.page_content[:200]
            if key in doc_scores:
                existing_doc, existing_score = doc_scores[key]
                doc_scores[key] = (existing_doc, existing_score + (1 - self.alpha) * score)
            else:
                doc_scores[key] = (doc, (1 - self.alpha) * score)

        merged = sorted(doc_scores.values(), key=lambda x: x[1], reverse=True)
        return merged[: self.final_top_k]

    def retrieve(self, query: str) -> list[Document]:
        scored = self.retrieve_scored(query)
        return [doc for doc, _ in scored]

    def retrieve_scored(self, query: str) -> list[tuple[Document, float]]:
        dense_raw = self._dense_search(query, k=self.dense_top_k)
        sparse_raw = self._sparse_search(query, k=self.sparse_top_k)

        dense_norm = self._normalize_scores(dense_raw)
        sparse_norm = self._normalize_scores(sparse_raw)

        return self._merge_results(dense_norm, sparse_norm)

    def retrieve_all_scores(self, query: str) -> dict[str, list[tuple[Document, float]]]:
        dense_raw = self._dense_search(query, k=self.dense_top_k)
        sparse_raw = self._sparse_search(query, k=self.sparse_top_k)
        dense_norm = self._normalize_scores(dense_raw)
        sparse_norm = self._normalize_scores(sparse_raw)
        merged = self._merge_results(dense_norm, sparse_norm)
        return {
            "dense": dense_norm,
            "sparse": sparse_norm,
            "merged": merged,
        }
