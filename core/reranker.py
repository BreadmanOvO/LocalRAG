"""Reranker implementations for hybrid retrieval results.

Provides two reranker strategies:
- CrossEncoderReranker: local cross-encoder model (recommended, requires GPU)
- LLMReranker: LLM-based scoring (fallback, slower)
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from langchain_core.documents import Document

# Use HuggingFace mirror for users in China
if "HF_ENDPOINT" not in os.environ:
    os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


class CrossEncoderReranker:
    """Local cross-encoder reranker using sentence-transformers.

    Uses a cross-encoder model to score (query, document) pairs for relevance,
    then re-ranks by the cross-encoder score.

    Recommended models:
    - BAAI/bge-reranker-base (Chinese + English, good quality)
    - cross-encoder/ms-marco-MiniLM-L-6-v2 (English, fast)
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        *,
        max_length: int = 512,
        device: str | None = None,
    ) -> None:
        from sentence_transformers import CrossEncoder
        self.model = CrossEncoder(model_name, max_length=max_length, device=device)

    def rerank(
        self,
        query: str,
        docs: list[tuple[Document, float]],
        top_k: int = 5,
    ) -> list[tuple[Document, float]]:
        if not docs:
            return []

        # Build (query, passage) pairs for scoring
        pairs = [(query, doc.page_content) for doc, _ in docs]

        # Cross-encoder scores (higher = more relevant)
        scores = self.model.predict(pairs)

        # Combine with original docs and sort by cross-encoder score
        scored = [
            (doc, float(ce_score), original_score)
            for (doc, original_score), ce_score in zip(docs, scores)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [(doc, ce_score) for doc, ce_score, _ in scored[:top_k]]


# --- LLM-based reranker (legacy fallback) ---

RERANK_PROMPT = """你是一个文档相关性评分专家。给定一个问题和若干文档片段，请为每个片段的相关性打分。

评分标准：
- 3分：直接回答问题，包含关键信息
- 2分：部分相关，包含背景或上下文信息
- 1分：略有相关，但不直接回答问题
- 0分：完全不相关

问题：{question}

文档片段：
{chunks}

请以 JSON 数组格式输出每个片段的分数，例如：[3, 2, 1, 0]
只输出 JSON 数组，不要其他内容。"""


def _extract_scores(text: str, expected_count: int) -> list[int]:
    """Extract JSON array of scores from LLM response."""
    match = re.search(r"\[[\d\s,]+\]", text)
    if match:
        try:
            scores = json.loads(match.group())
            if len(scores) == expected_count:
                return [int(s) for s in scores]
        except (json.JSONDecodeError, ValueError):
            pass
    # Fallback: return equal scores
    return [1] * expected_count


class LLMReranker:
    def __init__(self, chat_model: Any, *, batch_size: int = 20) -> None:
        self.chat_model = chat_model
        self.batch_size = batch_size

    def rerank(
        self,
        query: str,
        docs: list[tuple[Document, float]],
        top_k: int = 5,
    ) -> list[tuple[Document, float]]:
        if not docs:
            return []

        # Format chunks for the prompt
        chunks_text = "\n".join(
            f"[{i+1}] {doc.page_content[:300]}"
            for i, (doc, _) in enumerate(docs[:self.batch_size])
        )

        prompt = RERANK_PROMPT.format(question=query, chunks=chunks_text)

        try:
            response = self.chat_model.invoke(prompt)
            response_text = response.content if hasattr(response, "content") else str(response)
            scores = _extract_scores(response_text, len(docs[:self.batch_size]))
        except Exception:
            # On failure, return original order
            return docs[:top_k]

        # Combine with original docs and re-rank
        scored = [
            (doc, float(llm_score), original_score)
            for (doc, original_score), llm_score in zip(docs[:self.batch_size], scores)
        ]
        # Sort by LLM score descending, then by original score descending
        scored.sort(key=lambda x: (x[1], x[2]), reverse=True)

        # Return with LLM score as the new score
        return [(doc, float(llm_score)) for doc, llm_score, _ in scored[:top_k]]
