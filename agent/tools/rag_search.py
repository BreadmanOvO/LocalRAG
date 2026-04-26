from langchain_core.tools import tool
from core.rag import RagService

# 全局缓存最近一次检索结果
_last_retrieval_result: dict = {
    "documents": [],
    "query": "",
}


@tool
def rag_search(query: str) -> str:
    """从自动驾驶知识库检索相关内容并生成回答。

    Args:
        query: 用户的问题或检索关键词

    Returns:
        基于知识库内容生成的回答
    """
    global _last_retrieval_result

    rag_service = RagService()
    result = rag_service.answer_with_retrieval(query, session_id="agent-session")

    # 缓存检索结果供 show_sources 使用
    _last_retrieval_result = {
        "documents": result.get("retrieved_rows", []),
        "query": query,
    }

    return result.get("answer", "抱歉，未能找到相关内容。")


def get_last_retrieval_result() -> dict:
    """获取最近一次检索结果，供其他工具使用。"""
    return _last_retrieval_result
