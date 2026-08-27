from __future__ import annotations

from collections.abc import Callable
import logging
from typing import TYPE_CHECKING

from langchain_core.tools import tool

from agent.memory import SessionRetrievalMemory, TaskMemoryPolicy, TaskMemoryStore
from agent.observability import build_source_observation
from agent.tools.failures import (
    build_tool_failure,
    render_tool_error,
    render_tool_validation_error,
)
from utils.session import validate_session_id, validate_task_id

if TYPE_CHECKING:
    from core.rag import RagService

logger = logging.getLogger(__name__)


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

    @tool(
        "rag_search",
        response_format="content_and_artifact",
        return_direct=True,
    )
    def rag_search(query: str) -> tuple[str, dict]:
        """从自动驾驶知识库检索相关内容并生成有引用的回答。"""
        nonlocal service
        try:
            if service is None:
                if rag_service_factory is not None:
                    service = rag_service_factory()
                else:
                    from core.rag import RagService

                    service = RagService()

            result = service.answer_with_retrieval(query, session_id=bound_session_id)
        except Exception as exc:
            raise build_tool_failure(
                "知识库检索",
                exc,
                default_code="rag_search_failed",
                logger=logger,
            ) from exc

        raw_documents = result.get("retrieved_rows", [])
        documents = (
            [document for document in raw_documents if isinstance(document, dict)]
            if isinstance(raw_documents, list)
            else []
        )
        memory_errors = []
        try:
            retrieval_memory.remember(
                bound_session_id,
                query,
                documents,
            )
        except Exception:
            logger.warning("Session retrieval memory write failed", exc_info=True)
            memory_errors.append("session_memory_write_failed")

        try:
            if (
                bound_task_id is not None
                and task_memory_store is not None
                and (task_memory_policy is None or task_memory_policy.enabled)
            ):
                source_ids = []
                for document in documents:
                    source_id = str(document.get("source_id", "")).strip()
                    if source_id and source_id not in source_ids:
                        source_ids.append(source_id)
                task_memory_store.record_retrieval(bound_task_id, query, source_ids)
        except Exception:
            logger.warning("Task memory retrieval record failed", exc_info=True)
            memory_errors.append("task_memory_write_failed")

        artifact = {
            "source_observations": [
                build_source_observation(document, evidence_status="retrieved")
                for document in documents
            ],
            "trace": {
                "retrieval_strategy": result.get("retrieval_strategy", "unknown"),
                "retrieval_fallback_reason": result.get("retrieval_fallback_reason"),
                "retrieval_errors": list(result.get("retrieval_errors") or []),
                "retrieval_final_count": result.get("retrieval_final_count"),
                "retrieval_candidate_count": result.get("retrieval_candidate_count"),
                "generation_context_count": result.get("generation_context_count"),
                "memory_errors": memory_errors,
                "generation_route": result.get("generation_route"),
            },
        }
        return result.get("answer", "抱歉，未能找到相关内容。"), artifact

    rag_search.handle_tool_error = render_tool_error
    rag_search.handle_validation_error = render_tool_validation_error

    return rag_search
