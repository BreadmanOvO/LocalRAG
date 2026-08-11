# 自动驾驶感知算法 LocalRAG

面向自动驾驶感知算法场景的研究型 Agent，支持会话与任务记忆、来源研究工具、可观察运行轨迹、独立 Agent Gate，以及本地模型服务和长会话压缩。

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

本地模型服务使用独立的示例配置和部署 profile：

```powershell
Copy-Item config/runtime_v1_6_local_service.example.json config/runtime_v1_6_local_service.json
Copy-Item config/model_serving_profiles.example.json config/model_serving_profiles.json
```

服务端和应用端依赖已合并到唯一的 `requirements.txt`；不再维护单独的 serving requirements 文件。

### 3. 启动问答服务

```bash
streamlit run app_qa.py
```

默认读取 `config/active_corpus.json`，加载 v1.4.2 已通过 Gate 的 100-source / 7339-chunk Chroma store。active corpus v2 profile 同时固定来源数、片段数和 corpus/registry 指纹。大型 Chroma 二进制不进入 Git；新环境需要先生成该 store，或通过环境变量选择其他本地 store。v1.6 的本地模型 gateway、会话压缩和模型路由状态会在配置可用时接入同一 Agent UI：

```powershell
$env:LOCALRAG_PERSIST_DIRECTORY = "path\to\chroma_store"
streamlit run app_qa.py
```

UI 会同时检查 active corpus profile、最近一次完整 Agent Gate 的 corpus/代码身份，以及最近三轮正式评测的连续稳定性 Gate。任一身份不一致、artifact 损坏或出现递归上限错误时不会显示 Gate 通过。

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
│   ├── context/               # 上下文预算、摘要压缩、持久化与恢复
│   ├── memory/                # Agent 会话检索记忆与持久化任务记忆
│   ├── research/              # 研究 run、恢复控制、证据绑定与 UI 适配
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
│   └── release_gate.py        # 最近三轮正式 Agent Gate 稳定性检查
├── model_gateway/              # 本地模型 gateway、熔断、fallback 与适配器
├── model_serving/              # Transformers / llama.cpp 服务端与队列指标
├── model_deployment/           # 模型合并、量化、manifest 与启动脚本
├── data/
│   ├── evaluation/            # 清洗后的评测/训练数据集
│   └── sources/               # 知识源文档（100 篇：10 Apollo + 81 论文/报告 + 9 标准）
├── results/                   # 评测结果
├── scripts/                   # 工具脚本
├── release_note.md            # v1.1–v1.7 累计发布记录
└── requirements.txt           # 应用与本地模型服务的统一依赖入口
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

# 最近三轮正式 Agent Gate 的发布稳定性检查
python eval/release_gate.py

# 本地模型服务质量与可靠性评测
python eval/eval_model_quality.py
python eval/eval_service_reliability.py

# 长会话压缩评测
python eval/eval_long_context.py
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

Reranker 的收益主要体现在排序质量：semantic 的 MRR 从 0.798 提升到 0.893，Hit@1 从 0.71 提升到 0.86。v1.7 默认链路固定为 Dense + BM25 → RRF → Cross-Encoder → Top5；加权融合 `HybridRetriever` 作为历史对照保留，失败时降级到 Dense + reranker、Dense-only。

v1.7 最终默认链路在同一 100 题活动语料上完成 retrieval-only 回归：Hit@1=0.85、Hit@3=0.97、Hit@5=0.97、MRR=0.9067，100/100 进入 `rrf_rerank` 且无 fallback；该结果不调用线上生成模型。

Baseline 端到端评测使用当前 baseline store（`results/chunking_eval/stores/eval_set-20260522-071034/baseline`）重跑后，`answered_ratio=1.00`、`context_hit_ratio=1.00`、`evidence_source_hit_ratio=0.97`。

v1.6 本地模型服务与长会话验证：模型服务质量 gate、性能 benchmark、Task 8 UI 端到端验证和 Task 9 双轮压缩探针均通过；Task 9 的摘要 revision 从 `1` 正确递增到 `2`。

## 文档与发布记录

- [累计发布记录](release_note.md) — v1.1–v1.7 的功能、验证结果、门禁结论和已知限制
- [仓库使用说明](https://github.com/BreadmanOvO/RAG_md/blob/v1.7/docs/repo_guide.md) — 工程入口、评测脚本与结果目录合同
- [v1.7 Agentic RAG 与生产化开发计划](https://github.com/BreadmanOvO/RAG_md/blob/v1.7/docs/v1.7-agent-production-plan.md) — 面向 Agent/RAG/工程化面试能力的架构复审、里程碑与发布门槛
- [v1.7 架构掌握与面试复盘](https://github.com/BreadmanOvO/RAG_md/blob/v1.7/docs/v1.7-architecture-interview-guide.md) — 六层架构、线上/本地路径、工具失败、模型评测与深挖题
- [v1.7 Agentic RAG 收口报告](https://github.com/BreadmanOvO/RAG_md/blob/v1.7/docs/reports/v1.7-agentic-rag-closure.md) — 默认 RRF 主链路、工具失败合同、provider smoke、真实 Agent trace 与 100 题回归
- 评测结果与 manifest：`results/`（原始截图、运行数据库等本地文件不提交）
- 配置示例：`config/*.example.json`

## 版本

| 版本 | 核心目标 | 状态 |
|------|---------|------|
| v1.0 | 评估基线（Gold Set + baseline runner + judge 骨架） | 已完成 |
| v1.1 | 数据层（文档采集、chunk、metadata、formal judge） | 已完成 |
| v1.2 | 检索层（hybrid retrieval + reranker + semantic chunking） | 已完成 |
| v1.3 | 数据扩充与评测重建 + Qwen3-4B 微调 E1-E9 闭环 | 已完成 |
| v1.4.2 | Agent + Memory 研究助手 | 已完成（M1-M5、稳定性补强与代码精简收口） |
| v1.5 | 可控研究 Agent | 已完成（A1-A5 评测发布） |
| v1.6 | 本地模型部署与会话压缩 | 已完成（Task 8/9 验证通过） |
| v1.7 | Agentic RAG 收口：Dense + BM25 → RRF → Cross-Encoder、工具失败合同与架构证据 | 已完成 |

## 仓库维护约定

- 所有运行依赖统一写入根目录 `requirements.txt`，应用与本地模型服务共用同一安装入口。
- 历史 TODO 和临时发布文档不作为版本能力入口；版本状态以 `release_note.md`、代码和 `results/` 中的 manifest 为准。
