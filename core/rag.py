from core.vector_stores import VectorStoreService
from core.channel_context import enrich_apollo_channel_context
from config import settings as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from core.chat_history import get_history
from config.runtime_keys import load_runtime_config
from config.provider_factory import build_chat_model, build_embedding_model
from uuid import uuid4

DEFAULT_RAG_SYSTEM_PROMPT = (
    "你是 LocalRAG 的证据约束回答助手。只能使用参考资料中的信息回答问题；"
    "如果参考资料不足以支持答案，请明确说明无法根据资料确定。"
    "回答必须简洁、直接，并且答案末尾必须包含“引用：”小节，"
    "逐条列出使用到的 source_id 和 locator。参考资料：\n{context}"
)


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


def _document_key(doc: Document) -> tuple[str, str, str, str]:
    return (
        str(doc.metadata.get("source_id", "")),
        str(doc.metadata.get("locator", "")),
        str(doc.metadata.get("chunk_strategy", "")),
        doc.page_content,
    )


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
    scored_rows_by_key: dict[tuple[str, str, str, str], dict] = {}
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
    def __init__(self, *, chat_model=None, embedding_model=None) -> None:
        runtime_config = load_runtime_config()
        self.vector_service = VectorStoreService(
            embedding=(
                embedding_model
                if embedding_model is not None
                else build_embedding_model(runtime_config)
            ),
        )

        system_prompt = getattr(runtime_config, "rag_system_prompt", None) or DEFAULT_RAG_SYSTEM_PROMPT
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history", optional=True),
                ("user", "请回答用户提问：{question}")
            ]
        )
        
        self.chat_model = (
            chat_model if chat_model is not None else build_chat_model(runtime_config)
        )

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
        retriever = self.vector_service.get_retriever()
        return retriever.invoke(question)

    def retrieve_scored_documents(self, question: str) -> list[tuple[Document, float]]:
        debug_top_k = max(config.similarity_top_k, config.retrieval_debug_top_k)
        return self.vector_service.get_scored_documents(question, k=debug_top_k)

    def answer_from_documents(self, question: str, documents: list[Document], session_id: str = "eval-session") -> str:
        effective_session_id = self._get_effective_session_id(session_id)
        return self.chain.invoke(
            {
                "question": question,
                "context": _format_documents(documents),
            },
            config={"configurable": {"session_id": effective_session_id}},
        )

    def answer_once(self, question: str, session_id: str = "eval-session") -> str:
        documents = self.retrieve_documents(question)
        return self.answer_from_documents(question, documents, session_id=session_id)

    def answer_with_retrieval(self, question: str, session_id: str = "eval-session") -> dict:
        documents = self.retrieve_documents(question)
        scored_documents = self.retrieve_scored_documents(question)
        generation_documents = _extend_documents_with_same_source_candidates(documents, scored_documents)
        scored_rows = _normalize_scored_rows(scored_documents)
        generation_rows = _rows_for_documents(generation_documents, scored_documents)
        return {
            "answer": self.answer_from_documents(question, generation_documents, session_id=session_id),
            "retrieved_context": _format_retrieved_context(generation_documents),
            "retrieved_rows": generation_rows,
            "retrieval_debug_candidates": scored_rows,
        }
