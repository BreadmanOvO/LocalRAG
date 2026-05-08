# 自动驾驶感知算法 LocalRAG

面向自动驾驶感知算法场景的垂直领域 RAG 系统，支持多种检索策略、分块策略与评测流水线。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置运行时

复制示例配置并填写真实值：

```bash
cp config/runtime_models.example.json config/runtime_models.json
```

```json
{
  "provider": "modelscope",
  "api_key": "your-api-key",
  "base_url": "https://api-inference.modelscope.cn/v1",
  "chat_model_name": "Qwen/Qwen2.5-72B-Instruct",
  "embedding_model_name": "Qwen/Qwen3-Embedding-8B"
}
```

### 3. 启动问答服务

```bash
python app_qa.py
```

### 4. 上传文档入库

```bash
python app_file_uploader.py
```

## 项目结构

```
LocalRAG/
├── app_qa.py                  # 问答入口（Streamlit）
├── app_file_uploader.py       # 文件上传入库入口
├── agent/
│   └── react_agent.py         # ReAct Agent（3 工具：rag_search / show_sources / clarify_question）
├── core/
│   ├── rag.py                 # RAG 服务核心
│   ├── knowledge_base.py      # 知识库入库与 chunk 写入
│   ├── chunking.py            # 分块策略（baseline / doc_type_aware / semantic）
│   ├── hybrid_retriever.py    # Hybrid Retrieval（dense + BM25 sparse）
│   └── reranker.py            # Cross-Encoder Reranker
├── config/
│   ├── runtime_models.json    # 运行时配置（不提交）
│   ├── runtime_keys.py        # 配置加载器
│   └── settings.py            # 全局设置
├── eval/                      # 评测脚本
├── data/
│   ├── evaluation/            # 评测数据集（gold / synthetic）
│   └── sources/               # 知识源文档（41 篇）
├── results/                   # 评测结果
└── scripts/                   # 工具脚本
```

## 评测

### 运行评测

```bash
# Baseline 评测
python eval/eval_ragas.py

# 分块策略对比（baseline / doc_type_aware / semantic）
python eval/eval_chunking.py

# 纯检索评测（dense / sparse / hybrid）
python eval/eval_retrieval_only.py

# Hybrid Retrieval 对比
python eval/eval_hybrid.py

# Reranker 效果评估
python eval/eval_reranker.py

# Pairwise LLM Judge
python eval/eval_llm_judge.py
```

### 最新评测结果（100 题，bge-m3，41 篇文档）

| 分块策略 | Reranker | Hit@5 | MRR | Hit@1 | Hit@3 |
|---------|:--------:|:-----:|:---:|:-----:|:-----:|
| baseline | No | 0.960 | 0.865 | 0.790 | 0.940 |
| baseline | Yes | 0.960 | 0.899 | 0.850 | 0.950 |
| doc_type_aware | No | 0.940 | 0.870 | 0.830 | 0.900 |
| doc_type_aware | Yes | 0.960 | 0.904 | 0.860 | 0.950 |
| **semantic** | No | **0.970** | 0.864 | 0.800 | 0.920 |
| **semantic** | Yes | **0.980** | 0.897 | 0.840 | 0.950 |

最优配置：semantic chunking + reranker = 98% Hit@5，0.897 MRR。

## 文档

- [评估框架与指标](docs/evaluation.md) — 评测体系、指标口径、结果目录合同
- [仓库使用说明](docs/repo_guide.md) — 详细模块说明与使用方式

## 版本

| 版本 | 核心目标 | 状态 |
|------|---------|------|
| v1.0 | 评估基线（Gold Set + baseline runner + judge 骨架） | 已完成 |
| v1.1 | 数据层（文档采集、chunk、metadata、formal judge） | 已完成 |
| v1.2 | 检索层（hybrid retrieval + reranker + semantic chunking） | 已完成 |
