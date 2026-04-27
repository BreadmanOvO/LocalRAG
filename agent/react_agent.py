from langchain.agents import create_agent
from config.runtime_keys import load_runtime_config
from config.provider_factory import build_chat_model
from utils.path_tools import get_abs_path

from agent.tools import rag_search, show_sources, clarify_question


def load_agent_system_prompt() -> str:
    """加载 Agent 系统提示词"""
    prompt_path = get_abs_path("prompts/agent_system.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


class ReactAgent:
    def __init__(self):
        runtime_config = load_runtime_config()

        self.chat_model = build_chat_model(runtime_config, temperature=0.7)

        self.tools = [rag_search, show_sources, clarify_question]

        # 加载系统提示词
        system_prompt = load_agent_system_prompt()

        # 使用现代 create_agent API 创建 Agent
        self.agent_graph = create_agent(
            model=self.chat_model,
            tools=self.tools,
            system_prompt=system_prompt,
        )

    def execute(self, query: str) -> str:
        """执行单次问答"""
        result = self.agent_graph.invoke({"messages": [("user", query)]})
        # 从结果中提取最终回复
        messages = result.get("messages", [])
        if messages:
            # 获取最后一条 AI 消息
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.type == "ai":
                    return msg.content
        return "抱歉，处理过程中出现错误。"

    def execute_stream(self, query: str):
        """流式执行问答，逐步返回结果"""
        try:
            for chunk in self.agent_graph.stream({"messages": [("user", query)]}):
                # 处理不同类型的更新
                for node_name, node_output in chunk.items():
                    if "messages" in node_output:
                        for msg in node_output["messages"]:
                            if hasattr(msg, "content") and msg.content:
                                # 根据消息类型添加标签
                                if msg.type == "ai":
                                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                                        yield f"[思考] {msg.content}\n"
                                    else:
                                        yield msg.content
                                elif msg.type == "tool":
                                    yield f"[观察] {msg.content}\n"
        except Exception:
            # 流式失败时回退到同步执行
            yield self.execute(query)
