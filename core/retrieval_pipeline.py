"""Shared retrieval pipeline for online RAG and offline evaluation.

The default path keeps dense and BM25 rankings independent, fuses them with
reciprocal rank fusion (RRF), and applies a local Cross-Encoder reranker.
Weighted score fusion remains available through ``HybridRetriever`` as a
historical comparison, but is intentionally not chained into RRF.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import logging
from threading import Lock
from typing import Any

from langchain_core.documents import Document

from core.bm25_retriever import BM25Retriever

logger = logging.getLogger(__name__)

DocumentKey = tuple[str, str, str, str, str]


def document_key(document: Document) -> DocumentKey:
    """Return a stable identity for deduplication across retrieval branches."""
    metadata = document.metadata
    return (
        str(metadata.get("source_id", "")),
        str(metadata.get("locator", "")),
        str(metadata.get("chunk_order", "")),
        str(metadata.get("chunk_strategy", "")),
        document.page_content,
    )


@dataclass(frozen=True)
class RankedDocument:
    document: Document
    score: float
    rank: int
    stage: str
    dense_rank: int | None = None
    bm25_rank: int | None = None
    rrf_rank: int | None = None
    rerank_rank: int | None = None


@dataclass(frozen=True)
class RetrievalResult:
    final: tuple[RankedDocument, ...]
    candidates: tuple[RankedDocument, ...]
    strategy: str
    fallback_reason: str | None = None
    errors: tuple[str, ...] = ()

    @property
    def documents(self) -> list[Document]:
        return [item.document for item in self.final]

    @property
    def scored_documents(self) -> list[tuple[Document, float]]:
        return [(item.document, item.score) for item in self.candidates]


def _ranked_dense(
    documents: Sequence[tuple[Document, float]],
    *,
    limit: int | None = None,
) -> list[RankedDocument]:
    ranked = [
        RankedDocument(
            document=document,
            score=float(score),
            rank=rank,
            stage="dense",
            dense_rank=rank,
        )
        for rank, (document, score) in enumerate(documents, start=1)
    ]
    return ranked if limit is None else ranked[:limit]


def reciprocal_rank_fusion(
    dense_results: Sequence[tuple[Document, float]],
    bm25_results: Sequence[tuple[Document, float]],
    *,
    rrf_k: int = 60,
    top_k: int = 20,
) -> list[RankedDocument]:
    """Fuse independent dense and BM25 rank lists without mixing raw scores."""
    if rrf_k < 0:
        raise ValueError("rrf_k must be non-negative")
    if top_k <= 0:
        raise ValueError("top_k must be positive")

    merged: dict[DocumentKey, dict[str, Any]] = {}
    for stage, results in (("dense", dense_results), ("bm25", bm25_results)):
        seen: set[DocumentKey] = set()
        for rank, (document, _score) in enumerate(results, start=1):
            key = document_key(document)
            if key in seen:
                continue
            seen.add(key)
            entry = merged.setdefault(
                key,
                {
                    "document": document,
                    "score": 0.0,
                    "dense_rank": None,
                    "bm25_rank": None,
                },
            )
            entry["score"] += 1.0 / (rrf_k + rank)
            entry[f"{stage}_rank"] = rank

    ordered = sorted(
        merged.items(),
        key=lambda item: (
            -float(item[1]["score"]),
            min(
                rank
                for rank in (item[1]["dense_rank"], item[1]["bm25_rank"])
                if rank is not None
            ),
            item[0],
        ),
    )
    return [
        RankedDocument(
            document=entry["document"],
            score=float(entry["score"]),
            rank=rank,
            stage="rrf",
            dense_rank=entry["dense_rank"],
            bm25_rank=entry["bm25_rank"],
            rrf_rank=rank,
        )
        for rank, (_key, entry) in enumerate(ordered[:top_k], start=1)
    ]


class RetrievalPipeline:
    """Dense + BM25 -> RRF -> Cross-Encoder with deterministic fallbacks."""

    def __init__(
        self,
        vector_store: Any,
        *,
        candidate_top_k: int = 20,
        final_top_k: int = 5,
        rrf_k: int = 60,
        reranker_factory: Callable[[], Any] | None = None,
        sparse_retriever_factory: Callable[[Any], Any] | None = None,
    ) -> None:
        if candidate_top_k <= 0 or final_top_k <= 0:
            raise ValueError("candidate_top_k and final_top_k must be positive")
        if candidate_top_k < final_top_k:
            raise ValueError("candidate_top_k must be >= final_top_k")
        self.vector_store = vector_store
        self.candidate_top_k = candidate_top_k
        self.final_top_k = final_top_k
        self.rrf_k = rrf_k
        self._reranker_factory = reranker_factory or self._default_reranker_factory
        self._sparse_retriever_factory = sparse_retriever_factory or BM25Retriever
        self._reranker: Any | None = None
        self._sparse_retriever: Any | None = None
        self._reranker_lock = Lock()
        self._sparse_lock = Lock()

    @staticmethod
    def _default_reranker_factory() -> Any:
        from core.reranker import CrossEncoderReranker

        return CrossEncoderReranker()

    def _get_reranker(self) -> Any:
        if self._reranker is None:
            with self._reranker_lock:
                if self._reranker is None:
                    self._reranker = self._reranker_factory()
        return self._reranker

    def _get_sparse_retriever(self) -> Any:
        if self._sparse_retriever is None:
            with self._sparse_lock:
                if self._sparse_retriever is None:
                    self._sparse_retriever = self._sparse_retriever_factory(self.vector_store)
        return self._sparse_retriever

    def refresh_sparse_index(self) -> None:
        """Refresh the BM25 snapshot after corpus ingestion or replacement."""
        replacement = self._sparse_retriever_factory(self.vector_store)
        with self._sparse_lock:
            self._sparse_retriever = replacement

    def _dense_search(self, query: str) -> list[tuple[Document, float]]:
        return list(
            self.vector_store.similarity_search_with_relevance_scores(
                query,
                k=self.candidate_top_k,
            )
        )

    def _bm25_search(self, query: str) -> list[tuple[Document, float]]:
        return self._get_sparse_retriever().retrieve_scored(query, k=self.candidate_top_k)

    def _rerank(
        self,
        query: str,
        candidates: Sequence[RankedDocument],
    ) -> list[RankedDocument]:
        reranked = self._get_reranker().rerank(
            query,
            [(item.document, item.score) for item in candidates],
            top_k=self.final_top_k,
        )
        if not reranked:
            raise RuntimeError("reranker returned no documents")

        source_by_key = {document_key(item.document): item for item in candidates}
        output: list[RankedDocument] = []
        seen: set[DocumentKey] = set()
        for rank, (document, score) in enumerate(reranked, start=1):
            key = document_key(document)
            if key in seen:
                continue
            seen.add(key)
            source = source_by_key.get(key)
            output.append(
                RankedDocument(
                    document=document,
                    score=float(score),
                    rank=rank,
                    stage="rerank",
                    dense_rank=source.dense_rank if source else None,
                    bm25_rank=source.bm25_rank if source else None,
                    rrf_rank=source.rrf_rank if source else None,
                    rerank_rank=rank,
                )
            )
        if not output:
            raise RuntimeError("reranker returned only duplicate documents")
        return output

    @staticmethod
    def _reason(errors: list[str]) -> str | None:
        return ",".join(errors) if errors else None

    def retrieve(self, query: str) -> RetrievalResult:
        errors: list[str] = []
        try:
            dense_results = self._dense_search(query)
        except Exception:
            logger.warning("Dense retrieval failed; stopping without evidence", exc_info=True)
            return RetrievalResult(
                final=(),
                candidates=(),
                strategy="no_candidate",
                fallback_reason="dense_failed",
                errors=("dense_failed",),
            )

        dense_ranked = _ranked_dense(dense_results)
        if not dense_ranked:
            return RetrievalResult(
                final=(),
                candidates=(),
                strategy="no_candidate",
                fallback_reason="dense_empty",
                errors=("dense_empty",),
            )

        fused: list[RankedDocument] = []
        try:
            bm25_results = self._bm25_search(query)
            if not bm25_results:
                errors.append("bm25_empty")
            else:
                fused = reciprocal_rank_fusion(
                    dense_results,
                    bm25_results,
                    rrf_k=self.rrf_k,
                    top_k=self.candidate_top_k,
                )
                if not fused:
                    errors.append("rrf_empty")
        except Exception:
            logger.warning("BM25 or RRF failed; degrading to dense candidates", exc_info=True)
            errors.append("bm25_or_rrf_failed")

        if fused:
            try:
                reranked = self._rerank(query, fused)
                return RetrievalResult(
                    final=tuple(reranked),
                    candidates=tuple(fused),
                    strategy="rrf_rerank",
                )
            except Exception:
                logger.warning("Reranker failed after RRF; degrading to dense-only", exc_info=True)
                errors.append("reranker_failed")
                return RetrievalResult(
                    final=tuple(dense_ranked[: self.final_top_k]),
                    candidates=tuple(dense_ranked),
                    strategy="dense_only",
                    fallback_reason=self._reason(errors),
                    errors=tuple(errors),
                )

        try:
            reranked = self._rerank(query, dense_ranked)
            return RetrievalResult(
                final=tuple(reranked),
                candidates=tuple(dense_ranked),
                strategy="dense_rerank",
                fallback_reason=self._reason(errors),
                errors=tuple(errors),
            )
        except Exception:
            logger.warning("Reranker failed on dense candidates; degrading to dense-only", exc_info=True)
            errors.append("reranker_failed")
            return RetrievalResult(
                final=tuple(dense_ranked[: self.final_top_k]),
                candidates=tuple(dense_ranked),
                strategy="dense_only",
                fallback_reason=self._reason(errors),
                errors=tuple(errors),
            )
