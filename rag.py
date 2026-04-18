# from langchain_core.prompts.base import format_document
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from chat_history_store import get_history
from uuid import uuid4

class RagService(object):
    def __init__(self) -> None:
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name),
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
        
        self.chat_model = ChatOpenAI(model=config.chat_model_name)

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

        def format_document(doc: list[Document]): 
            if not doc:
                return "无相关参考资料"
            formatted_str = ""
            for doc in doc:
                formatted_str += f"资料内容：{doc.page_content}。资料来源：{doc.metadata}\n"
            return formatted_str
        
        chain = (
            {
                "question": RunnablePassthrough(),
                "context": RunnableLambda(format_for_retriever) | retriever | format_document
            } | RunnableLambda(format_for_prompt_template) | self.prompt_template | self.chat_model | StrOutputParser()
        )

        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="question",
            history_messages_key="chat_history"
        )

        return chain_with_history

    def answer_once(self, question: str, session_id: str = "eval-session") -> str:
        effective_session_id = session_id
        if session_id == "eval-session":
            effective_session_id = f"eval-session-{uuid4().hex}"

        return self.chain.invoke(
            {"question": question},
            config={"configurable": {"session_id": effective_session_id}},
        )
