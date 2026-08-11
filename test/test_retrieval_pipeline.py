import unittest
from types import SimpleNamespace
from unittest import mock

from langchain_core.documents import Document

from core import rag
from core.bm25_retriever import BM25Retriever, _tokenize
from core.retrieval_pipeline import (
    RankedDocument,
    RetrievalPipeline,
    RetrievalResult,
    reciprocal_rank_fusion,
)


def _doc(source_id: str, content: str | None = None) -> Document:
    return Document(
        page_content=content or f"content for {source_id}",
        metadata={
            "source_id": source_id,
            "locator": f"page={source_id}",
            "chunk_order": 1,
            "chunk_strategy": "test",
        },
    )


class FakeVectorStore:
    def __init__(self, dense_results=None, error: Exception | None = None):
        self.dense_results = list(dense_results or [])
        self.error = error
        self.calls: list[tuple[str, int]] = []

    def similarity_search_with_relevance_scores(self, query, k):
        self.calls.append((query, k))
        if self.error is not None:
            raise self.error
        return self.dense_results[:k]


class FakeCollection:
    def __init__(self, documents):
        self.documents = list(documents)

    def get(self, *, include, limit, offset):
        batch = self.documents[offset : offset + limit]
        return {
            "ids": [f"doc-{offset + index}" for index, _item in enumerate(batch)],
            "documents": [item.page_content for item in batch],
            "metadatas": [item.metadata for item in batch],
        }


class FakeBM25VectorStore:
    def __init__(self, documents):
        self._collection = FakeCollection(documents)


class FakeSparseRetriever:
    def __init__(self, results=None, error: Exception | None = None):
        self.results = list(results or [])
        self.error = error
        self.calls: list[tuple[str, int]] = []

    def retrieve_scored(self, query, *, k):
        self.calls.append((query, k))
        if self.error is not None:
            raise self.error
        return self.results[:k]


class FakeReranker:
    def __init__(self, order=None, error: Exception | None = None):
        self.order = list(order or [])
        self.error = error
        self.calls: list[tuple[str, list[tuple[Document, float]], int]] = []

    def rerank(self, query, docs, top_k):
        self.calls.append((query, list(docs), top_k))
        if self.error is not None:
            raise self.error
        by_source = {doc.metadata["source_id"]: doc for doc, _score in docs}
        return [
            (by_source[source_id], float(len(self.order) - index))
            for index, source_id in enumerate(self.order[:top_k])
        ]


class ReciprocalRankFusionTests(unittest.TestCase):
    def test_fuses_independent_rank_lists_and_preserves_component_ranks(self):
        doc_a = _doc("a")
        doc_b = _doc("b")
        doc_c = _doc("c")

        fused = reciprocal_rank_fusion(
            [(doc_a, 0.99), (doc_b, 0.80)],
            [(doc_b, 12.0), (doc_c, 8.0)],
            rrf_k=60,
            top_k=3,
        )

        self.assertEqual(["b", "a", "c"], [item.document.metadata["source_id"] for item in fused])
        self.assertEqual(2, fused[0].dense_rank)
        self.assertEqual(1, fused[0].bm25_rank)
        self.assertEqual(1, fused[0].rrf_rank)
        self.assertAlmostEqual(1 / 62 + 1 / 61, fused[0].score)

    def test_deduplicates_repeated_documents_within_one_branch(self):
        doc_a = _doc("a")

        fused = reciprocal_rank_fusion(
            [(doc_a, 0.9), (doc_a, 0.8)],
            [],
            top_k=5,
        )

        self.assertEqual(1, len(fused))
        self.assertEqual(1, fused[0].dense_rank)


class BM25RetrieverTests(unittest.TestCase):
    def test_tokenizer_supports_mixed_english_and_chinese_queries(self):
        tokens = _tokenize("CRN 摄像头与毫米波雷达")

        self.assertIn("crn", tokens)
        self.assertIn("摄像", tokens)
        self.assertIn("毫米", tokens)
        self.assertIn("雷达", tokens)

    def test_zero_match_query_returns_no_candidates(self):
        retriever = BM25Retriever(
            FakeBM25VectorStore(
                [
                    _doc("a", "planning module input"),
                    _doc("b", "control module output"),
                ]
            )
        )

        result = retriever.retrieve_scored("completely-absent-token", k=2)

        self.assertEqual([], result)

    def test_retrieves_chinese_phrase_without_whitespace_segmentation(self):
        retriever = BM25Retriever(
            FakeBM25VectorStore(
                [
                    _doc("camera-radar", "摄像头与毫米波雷达融合机制"),
                    _doc("lidar", "激光雷达点云目标检测"),
                    _doc("planning", "规划控制与车辆轨迹预测"),
                ]
            )
        )

        results = retriever.retrieve_scored("摄像头如何与毫米波雷达融合？", k=2)

        self.assertTrue(results)
        self.assertEqual("camera-radar", results[0][0].metadata["source_id"])


class RetrievalPipelineTests(unittest.TestCase):
    def _pipeline(self, *, dense, sparse, reranker):
        pipeline = RetrievalPipeline(
            FakeVectorStore(dense),
            candidate_top_k=4,
            final_top_k=2,
            reranker_factory=lambda: reranker,
            sparse_retriever_factory=lambda _vector_store: sparse,
        )
        return pipeline

    def test_default_path_uses_rrf_then_reranker(self):
        doc_a = _doc("a")
        doc_b = _doc("b")
        doc_c = _doc("c")
        sparse = FakeSparseRetriever([(doc_b, 1.0), (doc_c, 0.8)])
        reranker = FakeReranker(["c", "b"])
        pipeline = self._pipeline(
            dense=[(doc_a, 0.9), (doc_b, 0.8)],
            sparse=sparse,
            reranker=reranker,
        )

        result = pipeline.retrieve("question")

        self.assertEqual("rrf_rerank", result.strategy)
        self.assertIsNone(result.fallback_reason)
        self.assertEqual(["c", "b"], [doc.metadata["source_id"] for doc in result.documents])
        self.assertEqual("rerank", result.final[0].stage)
        self.assertEqual(2, result.final[0].bm25_rank)
        self.assertEqual(1, result.final[0].rerank_rank)
        self.assertEqual([("question", 4)], pipeline.vector_store.calls)
        self.assertEqual([("question", 4)], sparse.calls)

    def test_bm25_failure_falls_back_to_dense_plus_reranker(self):
        doc_a = _doc("a")
        doc_b = _doc("b")
        sparse = FakeSparseRetriever(error=RuntimeError("bm25 unavailable"))
        reranker = FakeReranker(["b", "a"])
        pipeline = self._pipeline(
            dense=[(doc_a, 0.9), (doc_b, 0.8)],
            sparse=sparse,
            reranker=reranker,
        )

        result = pipeline.retrieve("question")

        self.assertEqual("dense_rerank", result.strategy)
        self.assertEqual("bm25_or_rrf_failed", result.fallback_reason)
        self.assertEqual(["b", "a"], [doc.metadata["source_id"] for doc in result.documents])

    def test_reranker_failure_falls_back_to_dense_only(self):
        doc_a = _doc("a")
        doc_b = _doc("b")
        sparse = FakeSparseRetriever([(doc_b, 1.0)])
        reranker = FakeReranker(error=RuntimeError("reranker unavailable"))
        pipeline = self._pipeline(
            dense=[(doc_a, 0.9), (doc_b, 0.8)],
            sparse=sparse,
            reranker=reranker,
        )

        result = pipeline.retrieve("question")

        self.assertEqual("dense_only", result.strategy)
        self.assertEqual("reranker_failed", result.fallback_reason)
        self.assertEqual(["a", "b"], [doc.metadata["source_id"] for doc in result.documents])

    def test_dense_failure_stops_without_calling_other_stages(self):
        reranker_factory = mock.Mock()
        sparse = FakeSparseRetriever([(_doc("b"), 1.0)])
        pipeline = RetrievalPipeline(
            FakeVectorStore(error=RuntimeError("dense unavailable")),
            reranker_factory=reranker_factory,
            sparse_retriever_factory=lambda _vector_store: sparse,
        )

        result = pipeline.retrieve("question")

        self.assertEqual("no_candidate", result.strategy)
        self.assertEqual("dense_failed", result.fallback_reason)
        self.assertEqual([], result.documents)
        self.assertEqual([], sparse.calls)
        reranker_factory.assert_not_called()


class RagServiceRetrievalIntegrationTests(unittest.TestCase):
    def test_no_candidate_early_stops_without_calling_generation_model(self):
        retrieval_result = RetrievalResult(
            final=(),
            candidates=(),
            strategy="no_candidate",
            fallback_reason="dense_failed",
            errors=("dense_failed",),
        )
        service = object.__new__(rag.RagService)
        service.retrieval_pipeline = SimpleNamespace(
            retrieve=mock.Mock(return_value=retrieval_result)
        )
        service.answer_from_documents = mock.Mock()
        service.last_generation_route = None

        result = rag.RagService.answer_with_retrieval(
            service,
            "question",
            session_id="session-1",
        )

        service.answer_from_documents.assert_not_called()
        self.assertEqual(rag.NO_EVIDENCE_ANSWER, result["answer"])
        self.assertEqual("no_candidate", result["retrieval_strategy"])
        self.assertEqual(0, result["generation_context_count"])
        self.assertEqual("none", result["generation_route"]["backend"])
        self.assertEqual(
            "no_candidate",
            result["generation_route"]["termination_reason"],
        )

    def test_answer_bundle_uses_one_pipeline_result_and_exposes_stage_metadata(self):
        document = _doc("a")
        final = RankedDocument(
            document=document,
            score=2.5,
            rank=1,
            stage="rerank",
            dense_rank=2,
            bm25_rank=1,
            rrf_rank=1,
            rerank_rank=1,
        )
        retrieval_result = RetrievalResult(
            final=(final,),
            candidates=(final,),
            strategy="rrf_rerank",
        )
        service = object.__new__(rag.RagService)
        service.retrieval_pipeline = SimpleNamespace(retrieve=mock.Mock(return_value=retrieval_result))
        service.answer_from_documents = mock.Mock(return_value="answer")
        service.last_generation_route = {"actual_model": "local"}

        result = rag.RagService.answer_with_retrieval(service, "question", session_id="session-1")

        service.retrieval_pipeline.retrieve.assert_called_once_with("question")
        self.assertEqual("rrf_rerank", result["retrieval_strategy"])
        self.assertEqual(1, result["retrieved_rows"][0]["bm25_rank"])
        self.assertEqual(1, result["retrieved_rows"][0]["rerank_rank"])
        self.assertEqual(1, result["retrieval_final_count"])
        self.assertEqual(1, result["retrieval_candidate_count"])
        self.assertEqual(1, result["generation_context_count"])
        self.assertEqual({"actual_model": "local"}, result["generation_route"])


if __name__ == "__main__":
    unittest.main()
