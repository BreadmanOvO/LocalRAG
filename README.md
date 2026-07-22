# 自动驾驶感知算法 LocalRAG

面向自动驾驶感知算法场景的研究型 Agent，支持会话与任务记忆、来源研究工具、可观察运行轨迹以及独立 Agent Gate。

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
streamlit run app_qa.py
```

默认读取 `config/active_corpus.json`，加载 v1.4.1 已通过 Gate 的 100-source / 7339-chunk Chroma store。大型 Chroma 二进制不进入 Git；新环境需要先生成该 store，或通过环境变量选择其他本地 store：

```powershell
$env:LOCALRAG_PERSIST_DIRECTORY = "path\to\chroma_store"
streamlit run app_qa.py
```

UI 会同时检查 active corpus profile 指纹、最近一次完整 Agent Gate 的 corpus 指纹和代码版本。任一身份不一致时不会显示 Gate 通过。

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
│   ├── react_agent.py         # Session-aware Agent 入口
│   ├── observability.py       # 工具轨迹、来源、记忆与 gate 可观察性
│   ├── memory/                # Agent 会话检索记忆与持久化任务记忆
│   └── tools/                 # RAG、来源研究与任务记忆工具
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
│   ├── evaluation/            # 清洗后的评测/训练数据集
│   └── sources/               # 知识源文档（100 篇：10 Apollo + 81 论文/报告 + 9 标准）
├── results/                   # 评测结果
└── scripts/                   # 工具脚本
```

## 评测

### 运行评测

```bash
# Baseline 评测（使用 chunking_eval 生成的当前 store）
python eval/eval_ragas.py \
  --dataset data/evaluation/gold/eval_set.json \
  --store-dir results/chunking_eval/stores/<run_id>/baseline \
  --predictions-out results/ragas_eval/eval_set-current/predictions.json \
  --metrics-out results/ragas_eval/eval_set-current/metrics.json

# 分块策略对比（baseline / doc_type_aware / semantic）
python eval/eval_chunking.py \
  --dataset data/evaluation/gold/eval_set.json

# 纯检索评测（以 semantic store 为例）
python eval/eval_retrieval_only.py \
  --dataset data/evaluation/gold/eval_set.json \
  --store-dir results/chunking_eval/stores/<run_id>/semantic

# Hybrid Retrieval 对比
python eval/eval_hybrid.py \
  --dataset data/evaluation/gold/eval_set.json \
  --store-dir results/chunking_eval/stores/<run_id>/semantic \
  --alpha 0.5

# Reranker 效果评估
python eval/eval_reranker.py \
  --dataset data/evaluation/gold/eval_set.json \
  --store-dir results/chunking_eval/stores/<run_id>/semantic \
  --alpha 0.5

# Formal Judge 流水线汇总
python eval/eval_judge_formal_run.py \
  --dataset data/evaluation/gold/eval_set.json

# Agent 正式 Gate（默认使用 active corpus）
python eval/eval_agent.py
```

### 微调数据与行为评测

```bash
# 将 203 条训练样本导出为 Qwen/TRL 常用 chat JSONL
python scripts/prepare_sft_dataset.py \
  --input data/evaluation/train/train_set.json \
  --train-output data/finetuning/sft_train.jsonl \
  --validation-output data/finetuning/sft_validation.jsonl \
  --validation-count 20

# 对 baseline / 微调后 predictions 做离线行为对比
python eval/eval_finetune_behavior.py \
  --baseline-predictions results/baseline_eval/<run_id>/predictions.json \
  --predictions results/finetuned_eval/<run_id>/predictions.json
```

### 最新评测结果（100 题，bge-m3，100 篇文档，sensenova-6.7-flash-lite）

| 分块策略 | Reranker | Hit@5 | MRR | Hit@1 | Hit@3 |
|---------|:--------:|:-----:|:---:|:-----:|:-----:|
| baseline | No | 0.920 | 0.874 | 0.840 | 0.910 |
| baseline | Yes | 0.930 | 0.889 | 0.860 | 0.920 |
| doc_type_aware | No | 0.930 | 0.870 | 0.830 | 0.920 |
| **doc_type_aware** | **Yes** | **0.940** | 0.892 | 0.850 | **0.940** |
| semantic | No | 0.930 | 0.798 | 0.710 | 0.870 |
| **semantic** | **Yes** | **0.940** | **0.893** | **0.860** | 0.930 |

最优 Hit@5：doc_type_aware + reranker 与 semantic + reranker 均为 94%；semantic + reranker 的 MRR 最高（0.893）。

Baseline 端到端评测使用当前 baseline store（`results/chunking_eval/stores/eval_set-20260522-071034/baseline`）重跑后，`answered_ratio=1.00`、`context_hit_ratio=1.00`、`evidence_source_hit_ratio=0.97`。

## 文档

- [评估框架与指标](RAG_md/docs/evaluation.md) — 评测体系、指标口径、结果目录合同
- [仓库使用说明](RAG_md/docs/repo_guide.md) — 详细模块说明与使用方式
- [E4 数据草案复核](RAG_md/docs/reports/e4-draft-review.md) — E4 multi-metric partial-context 草案与复核标准
- [E5 pairwise contrast 数据报告](RAG_md/docs/reports/e5-pairwise-contrast-review.md) — E5 完整上下文 / 部分上下文对照样本与设计原则
- [v1.4 Agent 可靠性复核](RAG_md/docs/reports/v1.4-agent-reliability-review.md) — M1-M5 Gate、失败状态与运行身份收口

## 版本

| 版本 | 核心目标 | 状态 |
|------|---------|------|
| v1.0 | 评估基线（Gold Set + baseline runner + judge 骨架） | 已完成 |
| v1.1 | 数据层（文档采集、chunk、metadata、formal judge） | 已完成 |
| v1.2 | 检索层（hybrid retrieval + reranker + semantic chunking） | 已完成 |
| v1.3 | 数据扩充与评测重建 + Qwen3-4B 微调 E1-E9 闭环 | 已完成 |
| v1.4.1 | Agent + Memory 研究助手 | 已完成（M1-M5 与发布可靠性收口） |
