from __future__ import annotations

from langchain_core.tools import tool

from agent.memory import SessionRetrievalMemory
from core.rag import RagService
from utils.session import validate_session_id


def build_rag_search_tool(
    session_id: str,
    retrieval_memory: SessionRetrievalMemory,
    rag_service: RagService | None = None,
):
    """Build a RAG search tool bound to one agent session."""
    bound_session_id = validate_session_id(session_id)
    service = rag_service

    @tool("rag_search")
    def rag_search(query: str) -> str:
        """从自动驾驶知识库检索相关内容并生成有引用的回答。"""
        nonlocal service
        if service is None:
            service = RagService()

        result = service.answer_with_retrieval(query, session_id=bound_session_id)
        documents = result.get("retrieved_rows", [])
        retrieval_memory.remember(
            bound_session_id,
            query,
            documents if isinstance(documents, list) else [],
        )
        return result.get("answer", "抱歉，未能找到相关内容。")

    return rag_search
