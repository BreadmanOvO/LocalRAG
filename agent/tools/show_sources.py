import logging

from langchain_core.tools import tool

from agent.memory import SessionRetrievalMemory
from agent.tools.failures import (
    build_tool_failure,
    render_tool_error,
    render_tool_validation_error,
)
from utils.session import validate_session_id

logger = logging.getLogger(__name__)


def build_show_sources_tool(session_id: str, retrieval_memory: SessionRetrievalMemory):
    """Build a source display tool bound to one agent session."""
    bound_session_id = validate_session_id(session_id)

    @tool("show_sources")
    def show_sources() -> str:
        """展示当前会话最近一次检索命中的知识来源。"""
        try:
            snapshot = retrieval_memory.recall(bound_session_id)
            if snapshot is None or not snapshot.documents:
                return "当前会话暂无检索记录，请先提问。"

            lines = [f"最近检索问题：{snapshot.query}", "以下是当前会话命中的来源："]
            for index, document in enumerate(snapshot.documents, start=1):
                source_id = document.get("source_id", "未知来源")
                locator = document.get("locator", "") or "unknown"
                chunk_order = document.get("chunk_order")
                chunk_strategy = document.get("chunk_strategy", "") or "unknown"
                content = str(document.get("content", ""))
                summary = content[:100] + "..." if len(content) > 100 else content

                lines.extend(
                    [
                        f"\n【来源 {index}】",
                        f"source_id: {source_id}",
                        f"locator: {locator}",
                        f"chunk_order: {chunk_order}",
                        f"chunk_strategy: {chunk_strategy}",
                        f"摘要: {summary}",
                    ]
                )

            return "\n".join(lines)
        except Exception as exc:
            raise build_tool_failure(
                "来源读取",
                exc,
                default_code="source_memory_read_failed",
                logger=logger,
            ) from exc

    show_sources.handle_tool_error = render_tool_error
    show_sources.handle_validation_error = render_tool_validation_error

    return show_sources
