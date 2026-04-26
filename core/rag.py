# from langchain_core.prompts.base import format_document
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from core.vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatOpenAI
from config import settings as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from core.chat_history import get_history
from config.runtime_keys import load_bailian_runtime_config
from uuid import uuid4


def _normalize_retrieved_row(doc: Document, score: float | None = None, rank: int | None = None) -> dict:
    row = {
        "source_id": doc.metadata.get("source_id", ""),
        "doc_type": doc.metadata.get("doc_type", ""),
        "locator": doc.metadata.get("locator", ""),
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


def _format_documents(documents: list[Document]) -> str:
    if not documents:
        return "无相关参考资料"
    formatted_str = ""
    for doc in documents:
        source_id = doc.metadata.get("source_id", "")
        locator = doc.metadata.get("locator", "")
        formatted_str += f"资料内容：{doc.page_content}。资料来源：source_id={source_id}, locator={locator}\n"
    return formatted_str


class RagService(object):
    def __init__(self) -> None:
        runtime_config = load_bailian_runtime_config()
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(
                model=runtime_config.embedding_model_name,
                dashscope_api_key=runtime_config.dashscope_api_key,
            ),
        )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的已知参考资料为主，"
                 "简洁和专业的回答用户问题。参考资料：{context}。"),
                ("system", "并且我提供用户的对话历史记录："),
                MessagesPlaceholder("chat_history"),
                ("user", "请回答用户提问：{question}")
            ]
        )
        
        self.chat_model = ChatOpenAI(
            model=runtime_config.chat_model_name,
            api_key=runtime_config.dashscope_api_key,
            base_url=runtime_config.dashscope_base_url,
        )

        self.chain = self.__get_chain()

    def __get_chain(self):
        '''获取最终的执行链'''
        retriever = self.vector_service.get_retriever()

        def format_for_retriever(value: dict) -> str:
            return value["question"]

        def format_for_prompt_template(value: dict) -> dict:
            new_dict = {}
            new_dict["question"] = value["question"]["question"]
            new_dict["chat_history"] = value["question"]["chat_history"]
            new_dict["context"] = value["context"]
            return new_dict

        chain = (
            {
                "question": RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever) | retriever | RunnableLambda(_format_documents)
            } | RunnableLambda(format_for_prompt_template) | self.prompt_template | self.chat_model | StrOutputParser()
        )

        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="question",
            history_messages_key="chat_history"
        )

        return chain_with_history

    def _get_effective_session_id(self, session_id: str) -> str:
        if session_id == "eval-session":
            return f"eval-session-{uuid4().hex}"
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
        scored_rows = _normalize_scored_rows(scored_documents)
        generation_rows = scored_rows[:len(documents)]
        return {
            "answer": self.answer_from_documents(question, documents, session_id=session_id),
            "retrieved_context": "\n".join(doc.page_content for doc in documents),
            "retrieved_rows": generation_rows,
            "retrieval_debug_candidates": scored_rows,
        }
