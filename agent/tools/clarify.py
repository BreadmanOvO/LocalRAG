from langchain_core.tools import tool
from langchain_community.chat_models import ChatOpenAI
from config.runtime_keys import load_bailian_runtime_config


@tool
def clarify_question(reason: str) -> str:
    """当用户问题模糊或信息不足时，生成澄清追问。

    Args:
        reason: 判断问题模糊的原因说明

    Returns:
        生成的澄清追问文本
    """
    runtime_config = load_bailian_runtime_config()

    chat_model = ChatOpenAI(
        model=runtime_config.chat_model_name,
        api_key=runtime_config.dashscope_api_key,
        base_url=runtime_config.dashscope_base_url,
    )

    prompt = f"""你是一个自动驾驶领域的专业问答助手。
用户的问题不够清晰，原因如下：{reason}

请生成一个简洁、礼貌的追问，帮助用户补充必要信息。
追问应该：
1. 直接指向模糊的关键点
2. 提供可能的选项帮助用户回答
3. 保持专业和友好的语气

直接输出追问内容，不要包含其他说明。"""

    response = chat_model.invoke(prompt)
    return response.content.strip()
