# 自动驾驶问答 Agent 升级实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有朴素 RAG 问答系统升级为标准版 Agent 架构，支持 3 个核心工具调用，保留评测链路。

**Architecture:** 在现有 RAG 能力之上新增 Agent 层，采用 LangChain ReAct 模式编排工具。评测脚本迁移至 `eval/` 目录，主入口改为调用 Agent。

**Tech Stack:** LangChain Agent (create_react_agent), Streamlit, ChromaDB, DashScope, qwen3-max

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `agent/__init__.py` | 新建 | 包初始化 |
| `agent/react_agent.py` | 新建 | ReAct Agent 核心实现 |
| `agent/tools/__init__.py` | 新建 | 工具包初始化 |
| `agent/tools/rag_search.py` | 新建 | 检索问答工具 |
| `agent/tools/show_sources.py` | 新建 | 来源展示工具 |
| `agent/tools/clarify.py` | 新建 | 澄清追问工具 |
| `eval/__init__.py` | 新建 | 评测包初始化 |
| `eval/eval_ragas.py` | 迁移 | 从根目录迁入 |
| `eval/eval_chunking.py` | 迁移 | 从根目录迁入 |
| `eval/eval_llm_judge.py` | 迁移 | 从根目录迁入 |
| `config/agent.yml` | 修改 | 添加 Agent 系统提示词 |
| `prompts/agent_system.txt` | 新建 | Agent 系统提示词 |
| `app_qa.py` | 修改 | 改为调用 Agent |
| `rag/__init__.py` | 新建 | 确保 rag 包可导入 |

---

## Task 1: 创建 Agent 目录结构与包初始化

**Files:**
- Create: `agent/__init__.py`
- Create: `agent/tools/__init__.py`

- [ ] **Step 1: 创建 agent 目录和 __init__.py**

```python
# agent/__init__.py
from agent.react_agent import ReactAgent

__all__ = ["ReactAgent"]
```

- [ ] **Step 2: 创建 agent/tools/__init__.py**

```python
# agent/tools/__init__.py
from agent.tools.rag_search import rag_search
from agent.tools.show_sources import show_sources
from agent.tools.clarify import clarify_question

__all__ = ["rag_search", "show_sources", "clarify_question"]
```

- [ ] **Step 3: 验证目录结构**

Run: `ls -la agent/ agent/tools/`
Expected: 两个目录均存在且包含 __init__.py

- [ ] **Step 4: Commit**

```bash
git add agent/__init__.py agent/tools/__init__.py
git commit -m "feat: create agent directory structure"
```

---

## Task 2: 创建 rag 包初始化文件

**Files:**
- Create: `rag/__init__.py`

- [ ] **Step 1: 创建 rag/__init__.py**

```python
# rag/__init__.py
from rag.vector_stores import VectorStoreService

__all__ = ["VectorStoreService"]
```

- [ ] **Step 2: 验证导入正常**

Run: `python -c "from rag import VectorStoreService; print('OK')"`
Expected: 输出 "OK"

- [ ] **Step 3: Commit**

```bash
git add rag/__init__.py
git commit -m "feat: add rag package init"
```

---

## Task 3: 实现 rag_search 工具

**Files:**
- Create: `agent/tools/rag_search.py`

- [ ] **Step 1: 实现 rag_search 工具**

```python
# agent/tools/rag_search.py
from langchain_core.tools import tool
from rag import RagService

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
```

- [ ] **Step 2: 验证工具可导入**

Run: `python -c "from agent.tools.rag_search import rag_search; print(rag_search.name)"`
Expected: 输出 "rag_search"

- [ ] **Step 3: Commit**

```bash
git add agent/tools/rag_search.py
git commit -m "feat: implement rag_search tool"
```

---

## Task 4: 实现 show_sources 工具

**Files:**
- Create: `agent/tools/show_sources.py`

- [ ] **Step 1: 实现 show_sources 工具**

```python
# agent/tools/show_sources.py
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
```

- [ ] **Step 2: 验证工具可导入**

Run: `python -c "from agent.tools.show_sources import show_sources; print(show_sources.name)"`
Expected: 输出 "show_sources"

- [ ] **Step 3: Commit**

```bash
git add agent/tools/show_sources.py
git commit -m "feat: implement show_sources tool"
```

---

## Task 5: 实现 clarify_question 工具

**Files:**
- Create: `agent/tools/clarify.py`

- [ ] **Step 1: 实现 clarify_question 工具**

```python
# agent/tools/clarify.py
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from runtime_keys import load_bailian_runtime_config


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
```

- [ ] **Step 2: 验证工具可导入**

Run: `python -c "from agent.tools.clarify import clarify_question; print(clarify_question.name)"`
Expected: 输出 "clarify_question"

- [ ] **Step 3: Commit**

```bash
git add agent/tools/clarify.py
git commit -m "feat: implement clarify_question tool"
```

---

## Task 6: 创建 Agent 系统提示词

**Files:**
- Create: `prompts/agent_system.txt`
- Modify: `config/agent.yml`

- [ ] **Step 1: 创建系统提示词文件**

```text
你是自动驾驶领域的专业问答助手，具备自主的 ReAct 思考与工具调用能力，严格遵循「思考→行动→观察→再思考」的流程回答用户问题。

### 核心思考准则
1. 先判断用户的核心需求，分析「当前已有的信息是否足够直接回答」
2. 若问题模糊或缺少关键信息，调用 clarify_question 生成追问
3. 若问题清晰，调用 rag_search 检索知识库并生成回答
4. 用户需要了解来源时，调用 show_sources 展示检索命中的来源

### 可使用工具
1. rag_search：从自动驾驶知识库检索相关内容并生成回答
2. show_sources：展示最近一次检索命中的知识来源
3. clarify_question：当用户问题模糊时，生成澄清追问

### 输出规则
1. 每次调用工具前，必须输出真实的自然语言思考过程
2. 思考过程完成后，直接触发工具调用
3. 仅当获取的信息足够完整时，才生成最终自然语言回答
4. 回答需贴合自动驾驶领域，给出具体、专业的解释
```

- [ ] **Step 2: 更新 config/agent.yml**

```yaml
# config/agent.yml
system_prompt_path: prompts/agent_system.txt
max_iterations: 5
```

- [ ] **Step 3: Commit**

```bash
git add prompts/agent_system.txt config/agent.yml
git commit -m "feat: add agent system prompt"
```

---

## Task 7: 实现 ReAct Agent 核心

**Files:**
- Create: `agent/react_agent.py`

- [ ] **Step 1: 实现 ReactAgent 类**

```python
# agent/react_agent.py
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from runtime_keys import load_bailian_runtime_config
from utils.path_tools import get_abs_path

from agent.tools import rag_search, show_sources, clarify_question


def load_agent_system_prompt() -> str:
    """加载 Agent 系统提示词"""
    prompt_path = get_abs_path("prompts/agent_system.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


class ReactAgent:
    def __init__(self):
        runtime_config = load_bailian_runtime_config()

        self.chat_model = ChatOpenAI(
            model=runtime_config.chat_model_name,
            api_key=runtime_config.dashscope_api_key,
            base_url=runtime_config.dashscope_base_url,
            temperature=0.7,
        )

        self.tools = [rag_search, show_sources, clarify_question]

        # 构建 ReAct 提示词模板
        system_prompt = load_agent_system_prompt()
        self.prompt = PromptTemplate.from_template(
            system_prompt + "\n\n{tools}\n\nUse the following format:\n\n"
            "Question: the input question you must answer\n"
            "Thought: you should always think about what to do\n"
            "Action: the action to take, should be one of [{tool_names}]\n"
            "Action Input: the input to the action\n"
            "Observation: the result of the action\n"
            "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
            "Thought: I now know the final answer\n"
            "Final Answer: the final answer to the original input question\n\n"
            "Begin!\n\nQuestion: {input}\nThought: {agent_scratchpad}"
        )

        # 创建 Agent
        self.agent = create_react_agent(
            llm=self.chat_model,
            tools=self.tools,
            prompt=self.prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
        )

    def execute(self, query: str) -> str:
        """执行单次问答"""
        result = self.agent_executor.invoke({"input": query})
        return result.get("output", "抱歉，处理过程中出现错误。")

    def execute_stream(self, query: str):
        """流式执行问答，逐步返回结果"""
        # 先尝试流式输出
        try:
            for chunk in self.agent_executor.stream({"input": query}):
                # 返回中间步骤或最终结果
                if "output" in chunk:
                    yield chunk["output"]
                elif "actions" in chunk:
                    for action in chunk["actions"]:
                        yield f"[思考] {action.log}\n"
                elif "steps" in chunk:
                    for step in chunk["steps"]:
                        yield f"[观察] {step.observation}\n"
        except Exception:
            # 流式失败时回退到同步执行
            yield self.execute(query)
```

- [ ] **Step 2: 验证 Agent 可实例化**

Run: `python -c "from agent import ReactAgent; print('OK')"`
Expected: 输出 "OK"

- [ ] **Step 3: Commit**

```bash
git add agent/react_agent.py
git commit -m "feat: implement ReactAgent core"
```

---

## Task 8: 创建评测目录并迁移脚本

**Files:**
- Create: `eval/__init__.py`
- Move: `eval_ragas.py` -> `eval/eval_ragas.py`
- Move: `eval_chunking.py` -> `eval/eval_chunking.py`
- Move: `eval_llm_judge.py` -> `eval/eval_llm_judge.py`

- [ ] **Step 1: 创建 eval 目录**

Run: `mkdir -p eval`
Expected: eval 目录创建成功

- [ ] **Step 2: 创建 eval/__init__.py**

```python
# eval/__init__.py
# 评测脚本包
```

- [ ] **Step 3: 迁移评测脚本**

Run:
```bash
git mv eval_ragas.py eval/eval_ragas.py
git mv eval_chunking.py eval/eval_chunking.py
git mv eval_llm_judge.py eval/eval_llm_judge.py
```
Expected: 三个文件迁移到 eval/ 目录

- [ ] **Step 4: 更新 eval_chunking.py 内部导入**

由于 `eval_chunking.py` 导入了 `from eval_ragas import ...`，需要更新为相对导入：

```python
# 在 eval/eval_chunking.py 中
# 原来
from eval_ragas import build_session_id, load_dataset, write_json
# 改为
from eval.eval_ragas import build_session_id, load_dataset, write_json
```

- [ ] **Step 5: 更新 eval_llm_judge.py 内部导入**

```python
# 在 eval/eval_llm_judge.py 中
# 原来
from eval_ragas import write_json
# 改为
from eval.eval_ragas import write_json
```

- [ ] **Step 6: 验证评测脚本可导入**

Run: `python -c "from eval.eval_ragas import run_baseline; print('OK')"`
Expected: 输出 "OK"

- [ ] **Step 7: Commit**

```bash
git add eval/
git commit -m "refactor: move evaluation scripts to eval/ directory"
```

---

## Task 9: 更新 Streamlit 入口

**Files:**
- Modify: `app_qa.py`

- [ ] **Step 1: 修改 app_qa.py 调用 Agent**

```python
# app_qa.py
import streamlit as st
import uuid
from agent import ReactAgent

st.title("自动驾驶问答助手")
st.divider()

if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "你好，我是自动驾驶领域的问答助手，有什么可以帮助你？"}]

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    ai_res_list = []
    with st.spinner("思考中..."):
        response_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator):
            for chunk in generator:
                ai_res_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(response_stream))
        st.session_state["message"].append({"role": "assistant", "content": "".join(ai_res_list)})
```

- [ ] **Step 2: Commit**

```bash
git add app_qa.py
git commit -m "feat: update Streamlit entry to use ReactAgent"
```

---

## Task 10: 集成测试与验证

**Files:**
- 无新建文件，仅验证

- [ ] **Step 1: 验证 Agent 目录结构完整**

Run: `ls -la agent/ agent/tools/ eval/`
Expected: 所有目录和文件存在

- [ ] **Step 2: 验证所有导入正常**

Run:
```bash
python -c "from agent import ReactAgent; print('Agent OK')"
python -c "from agent.tools import rag_search, show_sources, clarify_question; print('Tools OK')"
python -c "from eval.eval_ragas import run_baseline; print('Eval OK')"
```
Expected: 全部输出 "OK"

- [ ] **Step 3: 启动 Streamlit 验证**

Run: `streamlit run app_qa.py`
Expected: 浏览器打开，能正常对话

- [ ] **Step 4: 验证评测脚本运行**

Run:
```bash
python eval/eval_ragas.py --dataset data/evaluation/gold_set/gold_set.json --predictions-out results/test/predictions.json --metrics-out results/test/metrics.json
```
Expected: 脚本正常执行（如有数据集）

- [ ] **Step 5: 最终 Commit**

```bash
git add -A
git commit -m "feat: complete agent upgrade with tools and eval migration"
```

---

## 成功标准

- [ ] Agent 能正确调用 3 个工具（rag_search, show_sources, clarify_question）
- [ ] 评测脚本迁移后可正常运行
- [ ] Streamlit 入口能正常问答
- [ ] 不破坏现有评测结果
- [ ] 目录结构清晰：agent/, rag/, eval/ 各司其职
