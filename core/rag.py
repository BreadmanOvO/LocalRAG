from core.vector_stores import VectorStoreService
from core.channel_context import enrich_apollo_channel_context
from config import settings as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from core.chat_history import get_history
from config.runtime_keys import load_runtime_config
from config.provider_factory import (
    build_agent_chat_model,
    build_embedding_model,
    build_rag_chat_model,
)
from core.retrieval_pipeline import (
    DocumentKey,
    RankedDocument,
    RetrievalPipeline,
    RetrievalResult,
    document_key,
)
from uuid import uuid4

DEFAULT_RAG_SYSTEM_PROMPT = (
    "你是 LocalRAG 的证据约束回答助手。只能使用参考资料中的信息回答问题；"
    "如果参考资料不足以支持答案，请明确说明无法根据资料确定。"
    "回答必须简洁、直接，并且答案末尾必须包含“引用：”小节，"
    "逐条列出使用到的 source_id 和 locator。参考资料：\n{context}"
)

NO_EVIDENCE_ANSWER = "抱歉，未检索到足够的参考资料，无法根据知识库回答。"


def _normalize_retrieved_row(doc: Document, score: float | None = None, rank: int | None = None) -> dict:
    row = {
        "source_id": doc.metadata.get("source_id", ""),
        "doc_type": doc.metadata.get("doc_type", ""),
        "locator": doc.metadata.get("locator", ""),
        "chunk_order": doc.metadata.get("chunk_order"),
        "chunk_strategy": doc.metadata.get("chunk_strategy", ""),
        "content": doc.page_content,
    }
    if score is not None:
        row["score"] = score
    if rank is not None:
        row["rank"] = rank
    return row


def _normalize_scored_rows(scored_documents: list[tuple[Document, float]]) -> list[dict]:
    return [
        _normalize_retrieved_row(doc, score=score, rank=index)
        for index, (doc, score) in enumerate(scored_documents, start=1)
    ]


def _document_key(doc: Document) -> DocumentKey:
    return document_key(doc)


def _normalize_ranked_document(item: RankedDocument) -> dict:
    row = _normalize_retrieved_row(item.document, score=item.score, rank=item.rank)
    row["retrieval_stage"] = item.stage
    for field_name in ("dense_rank", "bm25_rank", "rrf_rank", "rerank_rank"):
        value = getattr(item, field_name)
        if value is not None:
            row[field_name] = value
    return row


def _rows_for_ranked_documents(
    documents: list[Document],
    ranked_documents: list[RankedDocument],
) -> list[dict]:
    ranked_by_key: dict[DocumentKey, dict] = {}
    for item in ranked_documents:
        ranked_by_key.setdefault(_document_key(item.document), _normalize_ranked_document(item))

    rows = []
    for index, document in enumerate(documents, start=1):
        row = ranked_by_key.get(_document_key(document))
        if row is None:
            row = _normalize_retrieved_row(document, rank=index)
        rows.append(dict(row))
    return rows


def _extend_documents_with_same_source_candidates(
    documents: list[Document],
    scored_documents: list[tuple[Document, float]],
) -> list[Document]:
    per_source_limit = int(getattr(config, "same_source_context_extension_per_source", 0) or 0)
    if not documents or not scored_documents or per_source_limit <= 0:
        return list(documents)

    target_sources = {
        str(doc.metadata.get("source_id", ""))
        for doc in documents
        if doc.metadata.get("source_id")
    }
    if not target_sources:
        return list(documents)

    expanded = list(documents)
    seen_keys = {_document_key(doc) for doc in documents}
    supplemental_counts: dict[str, int] = {}

    for doc, _score in scored_documents:
        source_id = str(doc.metadata.get("source_id", ""))
        if source_id not in target_sources:
            continue
        key = _document_key(doc)
        if key in seen_keys:
            continue
        if supplemental_counts.get(source_id, 0) >= per_source_limit:
            continue

        expanded.append(doc)
        seen_keys.add(key)
        supplemental_counts[source_id] = supplemental_counts.get(source_id, 0) + 1

    return expanded


def _rows_for_documents(
    documents: list[Document],
    scored_documents: list[tuple[Document, float]],
) -> list[dict]:
    scored_rows_by_key: dict[DocumentKey, dict] = {}
    for index, (doc, score) in enumerate(scored_documents, start=1):
        scored_rows_by_key.setdefault(
            _document_key(doc),
            _normalize_retrieved_row(doc, score=score, rank=index),
        )

    rows = []
    for index, doc in enumerate(documents, start=1):
        row = scored_rows_by_key.get(_document_key(doc))
        if row is None:
            row = _normalize_retrieved_row(doc, rank=index)
        rows.append(dict(row))
    return rows


def _format_documents(documents: list[Document]) -> str:
    if not documents:
        return "无相关参考资料"
    formatted_blocks = []
    for index, doc in enumerate(documents, start=1):
        source_id = doc.metadata.get("source_id", "") or "unknown"
        locator = doc.metadata.get("locator", "") or "unknown"
        content = enrich_apollo_channel_context(doc.page_content, doc.metadata)
        formatted_blocks.append(
            f"[{index}] source_id={source_id} locator={locator}\n"
            f"content:\n{content}"
        )
    return "\n\n".join(formatted_blocks)


def _format_retrieved_context(documents: list[Document]) -> str:
    return "\n".join(
        enrich_apollo_channel_context(doc.page_content, doc.metadata)
        for doc in documents
    )


class RagService(object):
    def __init__(
        self,
        *,
        chat_model=None,
        embedding_model=None,
        gateway=None,
        runtime_config=None,
        retrieval_pipeline=None,
    ) -> None:
        runtime_config = runtime_config or load_runtime_config()
        self.runtime_config = runtime_config
        self.gateway = gateway
        self.last_generation_route: dict[str, object] | None = None
        self.vector_service = VectorStoreService(
            embedding=(
                embedding_model
                if embedding_model is not None
                else build_embedding_model(runtime_config)
            ),
        )
        self.retrieval_pipeline = retrieval_pipeline or RetrievalPipeline(
            self.vector_service.vector_store,
            candidate_top_k=config.retrieval_candidate_top_k,
            final_top_k=config.similarity_top_k,
            rrf_k=config.retrieval_rrf_k,
        )

        system_prompt = getattr(runtime_config, "rag_system_prompt", None) or DEFAULT_RAG_SYSTEM_PROMPT
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history", optional=True),
                ("user", "请回答用户提问：{question}")
            ]
        )
        
        if chat_model is not None:
            self.chat_model = chat_model
        elif gateway is not None or getattr(runtime_config, "local_model_gateway", None) is not None:
            self.chat_model = build_rag_chat_model(runtime_config, gateway=gateway)
        else:
            self.chat_model = build_agent_chat_model(runtime_config)

        self.chain = self.__get_chain()

    def __get_chain(self):
        '''获取最终的执行链'''
        chain = self.prompt_template | self.chat_model | StrOutputParser()

        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="question",
            history_messages_key="chat_history"
        )

        return chain_with_history

    def _get_effective_session_id(self, session_id: str) -> str:
        if session_id.startswith("eval-session"):
            return f"{session_id}-{uuid4().hex}"
        return session_id

    def retrieve_documents(self, question: str) -> list[Document]:
        return self.retrieve_result(question).documents

    def retrieve_scored_documents(self, question: str) -> list[tuple[Document, float]]:
        return self.retrieve_result(question).scored_documents

    def retrieve_result(self, question: str) -> RetrievalResult:
        return self.retrieval_pipeline.retrieve(question)

    def refresh_sparse_index(self) -> None:
        """Refresh the BM25 snapshot after a document is published."""
        self.retrieval_pipeline.refresh_sparse_index()

    def answer_from_documents(self, question: str, documents: list[Document], session_id: str = "eval-session") -> str:
        effective_session_id = self._get_effective_session_id(session_id)
        answer = self.chain.invoke(
            {
                "question": question,
                "context": _format_documents(documents),
            },
            config={"configurable": {"session_id": effective_session_id}},
        )
        self.last_generation_route = getattr(
            getattr(self, "chat_model", None),
            "last_route",
            None,
        )
        runtime_config = getattr(self, "runtime_config", None)
        if self.last_generation_route is None and runtime_config is not None:
            self.last_generation_route = {
                "primary_model": runtime_config.chat_model_name,
                "actual_model": runtime_config.chat_model_name,
                "provider": runtime_config.provider,
                "backend": "cloud",
                "fallback_used": False,
                "fallback_reason": None,
            }
        return answer

    def answer_once(self, question: str, session_id: str = "eval-session") -> str:
        documents = self.retrieve_documents(question)
        return self.answer_from_documents(question, documents, session_id=session_id)

    def answer_with_retrieval(self, question: str, session_id: str = "eval-session") -> dict:
        retrieval_result = None
        retrieve_result = getattr(self, "retrieve_result", None)
        if callable(retrieve_result) and getattr(self, "retrieval_pipeline", None) is not None:
            retrieval_result = retrieve_result(question)

        if retrieval_result is None:
            documents = self.retrieve_documents(question)
            scored_documents = self.retrieve_scored_documents(question)
            ranked_documents = []
            retrieval_strategy = "legacy"
            retrieval_fallback_reason = None
            retrieval_errors = []
            retrieval_final_count = len(documents)
            retrieval_candidate_count = len(scored_documents)
        else:
            documents = retrieval_result.documents
            scored_documents = retrieval_result.scored_documents
            ranked_documents = list(retrieval_result.final) + list(retrieval_result.candidates)
            retrieval_strategy = retrieval_result.strategy
            retrieval_fallback_reason = retrieval_result.fallback_reason
            retrieval_errors = list(retrieval_result.errors)
            retrieval_final_count = len(retrieval_result.final)
            retrieval_candidate_count = len(retrieval_result.candidates)

        generation_documents = _extend_documents_with_same_source_candidates(documents, scored_documents)
        if ranked_documents and retrieval_result is not None:
            scored_rows = [
                _normalize_ranked_document(item)
                for item in retrieval_result.candidates
            ]
            generation_rows = _rows_for_ranked_documents(generation_documents, ranked_documents)
        else:
            scored_rows = _normalize_scored_rows(scored_documents)
            generation_rows = _rows_for_documents(generation_documents, scored_documents)
        if retrieval_result is not None and not generation_documents:
            self.last_generation_route = {
                "backend": "none",
                "actual_model": None,
                "fallback_used": False,
                "fallback_reason": retrieval_fallback_reason,
                "termination_reason": "no_candidate",
            }
            answer = NO_EVIDENCE_ANSWER
        else:
            answer = self.answer_from_documents(
                question,
                generation_documents,
                session_id=session_id,
            )

        return {
            "answer": answer,
            "retrieved_context": _format_retrieved_context(generation_documents),
            "retrieved_rows": generation_rows,
            "retrieval_debug_candidates": scored_rows,
            "retrieval_strategy": retrieval_strategy,
            "retrieval_fallback_reason": retrieval_fallback_reason,
            "retrieval_errors": retrieval_errors,
            "retrieval_final_count": retrieval_final_count,
            "retrieval_candidate_count": retrieval_candidate_count,
            "generation_context_count": len(generation_rows),
            "generation_route": getattr(self, "last_generation_route", None),
        }
