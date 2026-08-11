from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from core.bm25_retriever import BM25_BATCH_SIZE as BM25_BATCH_SIZE
from core.bm25_retriever import BM25Retriever


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

        self._bm25_retriever = BM25Retriever(vector_store)

    @property
    def _bm25_docs(self) -> list[Document]:
        """Compatibility view for historical evaluation tests."""
        return self._bm25_retriever.documents

    @property
    def _bm25_ids(self) -> list[str]:
        """Compatibility view for historical inspection scripts."""
        return self._bm25_retriever.ids

    def _dense_search(self, query: str, k: int) -> list[tuple[Document, float]]:
        return self.vector_store.similarity_search_with_relevance_scores(query, k=k)

    def _sparse_search(self, query: str, k: int) -> list[tuple[Document, float]]:
        return self._bm25_retriever.retrieve_scored(query, k=k)

    def retrieve_dense_scored(self, query: str, *, k: int | None = None) -> list[tuple[Document, float]]:
        """Return the unfused dense ranking for shared retrieval pipelines."""
        return self._dense_search(query, k=k or self.dense_top_k)

    def retrieve_sparse_scored(self, query: str, *, k: int | None = None) -> list[tuple[Document, float]]:
        """Return the unfused BM25 ranking for RRF or evaluation."""
        return self._sparse_search(query, k=k or self.sparse_top_k)

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
