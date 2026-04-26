# 自动驾驶问答 Agent 升级设计

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有朴素 RAG 问答系统升级为标准版 Agent 架构，支持工具调用，保留评测链路。

**Architecture:** 在现有 RAG 能力之上新增 Agent 层，采用 ReAct 模式编排 3 个核心工具。评测脚本迁移至独立目录，主入口改为调用 Agent。

**Tech Stack:** LangChain Agent, Streamlit, ChromaDB, DashScope

---

## 1. 目录结构

```
LocalRAG/
├── agent/
│   ├── __init__.py
│   ├── react_agent.py        # ReAct Agent 入口
│   └── tools/
│       ├── __init__.py
│       ├── rag_search.py     # 检索问答工具
│       ├── show_sources.py   # 来源展示工具
│       └── clarify.py        # 澄清追问工具
├── rag/                      # 现有 RAG 模块（如 vector_stores.py），不迁移、不重构
│   ├── __init__.py           # 可能需新增
│   ├── vector_stores.py
│   └── ...
├── eval/                     # 评测专用（原 eval_*.py 迁入）
│   ├── __init__.py
│   ├── eval_ragas.py
│   ├── eval_chunking.py
│   └── eval_llm_judge.py
├── app_qa.py                 # Streamlit 入口，改为调用 Agent
├── rag.py                    # 保留，供 eval 直接调用
├── config/
├── prompts/
├── model/
├── utils/
├── data/
└── ...
```

## 2. Agent 核心设计

**Agent 类型**：ReAct Agent（Reasoning + Acting）

**系统提示词要点**：
- 你是自动驾驶领域的问答助手
- 先判断问题是否清晰，不清晰则调用 `clarify_question` 追问
- 清晰的问题调用 `rag_search` 检索并回答
- 回答时自动附带来源引用

**执行流程**：
1. 用户提问 -> Agent 分析意图
2. 若问题模糊 -> 调用 `clarify_question` -> 返回追问
3. 若问题清晰 -> 调用 `rag_search` -> 返回答案
4. 用户需要来源 -> 调用 `show_sources` -> 返回来源列表

## 3. 工具详细设计

### 3.1 rag_search

```python
@tool
def rag_search(query: str) -> str:
    """从自动驾驶知识库检索相关内容并生成回答"""
```

**实现要点**：
- 复用现有 `RagService.answer_once()` 或 `answer_with_retrieval()`
- 内部缓存检索结果，供 `show_sources` 使用
- 返回纯文本答案

### 3.2 show_sources

```python
@tool
def show_sources() -> str:
    """展示最近一次检索命中的知识来源"""
```

**实现要点**：
- 读取 `rag_search` 缓存的检索结果
- 格式化输出：`source_id + locator + 内容摘要`
- 若无缓存，返回"暂无检索记录"

### 3.3 clarify_question

```python
@tool
def clarify_question(reason: str) -> str:
    """当用户问题模糊时，生成澄清追问"""
```

**实现要点**：
- 由 LLM 根据模糊原因生成追问
- 返回追问文本，等待用户补充

## 4. 评测目录迁移方案

**迁移内容**：
- `eval_ragas.py` -> `eval/eval_ragas.py`
- `eval_chunking.py` -> `eval/eval_chunking.py`
- `eval_llm_judge.py` -> `eval/eval_llm_judge.py`

**改动点**：
1. 文件迁移后，内部 `import` 路径保持不变（`rag.py` 在根目录）
2. 新增 `eval/__init__.py`（空文件）
3. 运行方式：`python eval/eval_ragas.py`

**不改动**：
- `rag.py` 保持在根目录，评测和 Agent 都可以直接调用
- 结果目录 `results/` 保持原位置

## 5. Streamlit 入口改造

**改动点**：
- `app_qa.py` 从调用 `RagService` 改为调用 `ReactAgent`
- 保持现有 UI 交互逻辑（聊天记录、流式输出）

**改造前**：
```python
from rag import RagService
st.session_state["rag"] = RagService()
response_stream = st.session_state["rag"].chain.stream(...)
```

**改造后**：
```python
from agent.react_agent import ReactAgent
st.session_state["agent"] = ReactAgent()
response_stream = st.session_state["agent"].execute_stream(prompt)
```

## 6. 保护资产

- `rag.py`（RagService）保持在根目录，不做任何修改
- `rag/` 目录下的现有模块（如 `vector_stores.py`）不迁移、不重构
- Agent 工具通过 `from rag import RagService` 复用现有能力
- 评测脚本只迁移目录，不改核心逻辑
- `results/` 目录不变
- 现有 `key.json` 配置方式不变

## 7. 后续扩展点

- `agent/tools/` 可加术语解释、文档对比、主题总结
- `eval/` 可加更多评测脚本
- Agent 可升级为多轮对话规划模式

## 8. 成功标准

- Agent 能正确调用 3 个工具
- 评测脚本迁移后可正常运行
- Streamlit 入口能正常问答
- 不破坏现有评测结果
