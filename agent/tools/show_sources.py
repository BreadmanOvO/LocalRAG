from langchain_core.tools import tool
from agent.tools.rag_search import get_last_retrieval_result


@tool
def show_sources() -> str:
    """展示最近一次检索命中的知识来源。

    Returns:
        格式化的来源列表，包含 source_id、locator 和内容摘要
    """
    result = get_last_retrieval_result()
    documents = result.get("documents", [])

    if not documents:
        return "暂无检索记录，请先提问。"

    lines = ["以下是最近一次检索的来源："]
    for i, doc in enumerate(documents, start=1):
        source_id = doc.get("source_id", "未知来源")
        locator = doc.get("locator", "")
        content = doc.get("content", "")
        # 截取内容摘要（前100字符）
        summary = content[:100] + "..." if len(content) > 100 else content

        lines.append(f"\n【来源 {i}】")
        lines.append(f"source_id: {source_id}")
        if locator:
            lines.append(f"locator: {locator}")
        lines.append(f"摘要: {summary}")

    return "\n".join(lines)
