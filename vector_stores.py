from langchain_chroma import Chroma
import config_data as config

class VectorStoreService(object):
    def __init__(self, embedding) -> None:
        """
        :param embedding: 嵌入模型
        """
        self.embedding = embedding
        self.vector_store = Chroma(
            collection_name=config.collection_name, # 索引表名
            embedding_function=self.embedding, # 嵌入模型
            persist_directory=config.persist_directory, # 索引数据库文件
        )

    def get_retriever(self):
        """
        返回向量检索器，方便加入chain
        """
        result = self.vector_store.as_retriever(search_kwargs={"k": config.similarity_top_k})
        return result