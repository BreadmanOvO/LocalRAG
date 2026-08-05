from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from langchain_core.tools import tool

from agent.memory import SessionRetrievalMemory, TaskMemoryPolicy, TaskMemoryStore
from utils.session import validate_session_id, validate_task_id

if TYPE_CHECKING:
    from core.rag import RagService


def build_rag_search_tool(
    session_id: str,
    retrieval_memory: SessionRetrievalMemory,
    rag_service: RagService | None = None,
    *,
    rag_service_factory: Callable[[], RagService] | None = None,
    task_id: str | None = None,
    task_memory_store: TaskMemoryStore | None = None,
    task_memory_policy: TaskMemoryPolicy | None = None,
):
    """Build a RAG search tool bound to one agent session."""
    bound_session_id = validate_session_id(session_id)
    bound_task_id = validate_task_id(task_id) if task_id is not None else None
    if rag_service is not None and rag_service_factory is not None:
        raise ValueError("rag_service and rag_service_factory are mutually exclusive")
    if rag_service_factory is not None and not callable(rag_service_factory):
        raise TypeError("rag_service_factory must be callable")
    service = rag_service

    @tool("rag_search")
    def rag_search(query: str) -> str:
        """从自动驾驶知识库检索相关内容并生成有引用的回答。"""
        nonlocal service
        if service is None:
            if rag_service_factory is not None:
                service = rag_service_factory()
            else:
                from core.rag import RagService

                service = RagService()

        result = service.answer_with_retrieval(query, session_id=bound_session_id)
        documents = result.get("retrieved_rows", [])
        retrieval_memory.remember(
            bound_session_id,
            query,
            documents if isinstance(documents, list) else [],
        )
        if (
            bound_task_id is not None
            and task_memory_store is not None
            and (task_memory_policy is None or task_memory_policy.enabled)
        ):
            source_ids = []
            for document in documents if isinstance(documents, list) else []:
                source_id = str(document.get("source_id", "")).strip()
                if source_id and source_id not in source_ids:
                    source_ids.append(source_id)
            task_memory_store.record_retrieval(bound_task_id, query, source_ids)
        return result.get("answer", "抱歉，未能找到相关内容。")

    return rag_search
