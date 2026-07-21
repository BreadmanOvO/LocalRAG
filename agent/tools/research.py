from __future__ import annotations

from langchain_core.tools import tool

from agent.memory import SessionRetrievalMemory
from core.source_evidence import SourceEvidenceService
from utils.session import validate_session_id


def _source_header(source: dict) -> list[str]:
    return [
        f"source_id: {source.get('source_id', 'unknown')}",
        f"title: {source.get('title', 'unknown')}",
        f"doc_type: {source.get('doc_type', 'unknown')}",
        f"language: {source.get('language', 'unknown')}",
        f"version: {source.get('version', 'unknown')}",
        f"origin_url: {source.get('origin_url', 'unknown')}",
    ]


def _chunk_lines(chunk: dict, index: int) -> list[str]:
    return [
        f"片段 {index}：chunk_order={chunk.get('chunk_order')} "
        f"locator={chunk.get('locator', 'unknown')} "
        f"strategy={chunk.get('chunk_strategy', 'unknown')}",
        str(chunk.get("content") or ""),
    ]


def build_inspect_source_tool(evidence_service: SourceEvidenceService):
    @tool("inspect_source")
    def inspect_source(source_id: str, max_chunks: int = 3) -> str:
        """按 source_id 查看来源元数据、chunk 数量和首批可用片段。"""
        try:
            result = evidence_service.inspect_source(source_id, max_chunks=max_chunks)
        except Exception as exc:
            return f"来源检查失败：{exc}"
        if not result["found"]:
            return f"未找到来源：{result['source_id']}"

        lines = _source_header(result["source"])
        lines.append(f"chunk_count: {result['chunk_count']}")
        for index, chunk in enumerate(result["chunks"], start=1):
            lines.extend(["", *_chunk_lines(chunk, index)])
        return "\n".join(lines)

    return inspect_source


def build_expand_context_tool(evidence_service: SourceEvidenceService):
    @tool("expand_context")
    def expand_context(
        source_id: str,
        chunk_order: int,
        before: int = 1,
        after: int = 1,
        chunk_strategy: str = "",
    ) -> str:
        """围绕指定 source chunk 扩展相邻上下文；chunk_order 来自检索来源。"""
        try:
            result = evidence_service.expand_context(
                source_id,
                chunk_order,
                before=before,
                after=after,
                chunk_strategy=chunk_strategy,
            )
        except Exception as exc:
            return f"上下文扩展失败：{exc}"
        if not result["found"]:
            return (
                f"未找到 {result['source_id']} 的 chunk_order={result['chunk_order']}。"
                f"可用序号：{result['available_chunk_orders']}"
            )

        lines = [
            f"source_id: {result['source_id']}",
            f"target_chunk_order: {result['target_chunk_order']}",
        ]
        for index, chunk in enumerate(result["chunks"], start=1):
            lines.extend(["", *_chunk_lines(chunk, index)])
        return "\n".join(lines)

    return expand_context


def build_compare_sources_tool(evidence_service: SourceEvidenceService):
    @tool("compare_sources")
    def compare_sources(
        source_ids: list[str],
        focus: str = "",
        max_chunks_per_source: int = 2,
    ) -> str:
        """按统一 focus 提取 2-5 个来源的元数据和高相关片段，供对比分析。"""
        try:
            result = evidence_service.compare_sources(
                source_ids,
                focus=focus,
                max_chunks_per_source=max_chunks_per_source,
            )
        except Exception as exc:
            return f"来源对比失败：{exc}"

        lines = [f"对比焦点：{result['focus'] or '未指定'}"]
        for source_index, item in enumerate(result["sources"], start=1):
            lines.extend(["", f"【来源 {source_index}】", *_source_header(item["source"])])
            lines.append(f"chunk_count: {item['chunk_count']}")
            if not item["found"]:
                lines.append("该来源未在 registry 或知识库中找到。")
                continue
            for chunk_index, chunk in enumerate(item["chunks"], start=1):
                coverage = chunk.get("term_coverage")
                if coverage is not None:
                    lines.append(f"term_coverage: {coverage}")
                lines.extend(_chunk_lines(chunk, chunk_index))
        return "\n".join(lines)

    return compare_sources


def build_evidence_check_tool(
    session_id: str,
    retrieval_memory: SessionRetrievalMemory,
    evidence_service: SourceEvidenceService,
):
    bound_session_id = validate_session_id(session_id)

    @tool("evidence_check")
    def evidence_check(
        claim: str,
        source_ids: list[str] | None = None,
        max_candidates: int = 3,
    ) -> str:
        """在当前会话最近一次检索片段中检查某项结论是否存在候选证据。"""
        snapshot = retrieval_memory.recall(bound_session_id)
        documents = snapshot.documents if snapshot is not None else ()
        try:
            result = evidence_service.check_evidence(
                claim,
                documents,
                source_ids=source_ids,
                max_candidates=max_candidates,
            )
        except Exception as exc:
            return f"证据检查失败：{exc}"

        status_text = {
            "no_retrieval": "当前会话没有可检查的检索片段，请先检索。",
            "insufficient_overlap": "当前检索片段未找到关键词重合的候选证据。",
            "weak_candidate": "找到弱相关候选片段，需要进一步扩展上下文核对。",
            "candidate_found": "找到候选证据片段，需要根据原文判断是否支持结论。",
        }[result["status"]]
        lines = [
            f"待检查结论：{result['claim']}",
            f"检查状态：{result['status']}",
            status_text,
            f"已检查片段数：{result['searched_document_count']}",
        ]
        for index, candidate in enumerate(result["candidates"], start=1):
            lines.extend(
                [
                    "",
                    f"【候选证据 {index}】",
                    f"source_id: {candidate['source_id']}",
                    f"chunk_order: {candidate['chunk_order']}",
                    f"locator: {candidate['locator']}",
                    f"term_coverage: {candidate['term_coverage']}",
                    candidate["content"],
                ]
            )
        return "\n".join(lines)

    return evidence_check
