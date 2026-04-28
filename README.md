# 自动驾驶感知算法 LocalRAG

## 项目简介
这是一个面向自动驾驶感知算法场景的垂直领域 RAG 项目，v1.1 已完成数据、评测与文档收口，当前进入 v1.2 检索层实验规划阶段。

## 当前定位
- 项目状态：v1.1 已收口，v1.2 规划中
- 当前最高优先级：在稳定评测合同基础上推进检索层实验设计
- v1.2 状态：尚未进入实现阶段，当前仅保留检索层实验规划

## 当前已落地能力
- Agent 问答入口：`app_qa.py` + `agent/react_agent.py`
- 文件上传与入库入口：`app_file_uploader.py`
- 核心 RAG 服务：`core/rag.py`
- 知识库入库与 chunk 写入：`core/knowledge_base.py`
- chunking 与 locator / provenance metadata：`core/chunking.py`
- baseline 评测 runner：`eval/eval_ragas.py`
- pairwise LLM judge：`eval/eval_llm_judge.py`
- chunking 对比实验：`eval/eval_chunking.py`

## 当前评测状态
### 1. baseline_eval
`eval/eval_ragas.py` 已升级为 retrieval-aware baseline runner：
- 调用 `RagService.answer_with_retrieval()`
- 预测结果包含：`answer`、`retrieved_context`、`retrieved_rows`、`retrieval_debug_candidates`、`evidence`、`metadata`
- 当前 metrics 已包含 answered/context 命中、retrieved row / retrieval candidate 统计，以及 exact match / normalized exact match / reference substring / evidence source/locator 命中统计
- 支持按 run bundle 输出结果目录

结果目录约定：
- `results/baseline_eval/<run_id>/predictions.json`
- `results/baseline_eval/<run_id>/metrics.json`
- `results/baseline_eval/<run_id>/manifest.json`

### 2. judge_eval
`eval/eval_llm_judge.py` 当前是 pairwise LLM judge：
- 输入 baseline / candidate 两份 predictions
- 校验 sample id 集合一致
- 使用 temperature=0 的真实 judge model 做 pairwise 判分
- 通过严格 JSON contract 解析 `winner` 与 `reason`
- 输出 `judgements.json`、`summary.json`、`manifest.json`

结果目录约定：
- `results/judge_eval/<baseline_run_id>-vs-<candidate_run_id>/judgements.json`
- `results/judge_eval/<baseline_run_id>-vs-<candidate_run_id>/summary.json`
- `results/judge_eval/<baseline_run_id>-vs-<candidate_run_id>/manifest.json`

### 3. chunking_eval
`eval/eval_chunking.py` 是当前最完整的评测链路：
- 支持 baseline 与 `doc_type_aware` 两套切分策略对比
- 统计 `answered_ratio`、`evidence_source_hit_ratio`、`evidence_locator_hit_ratio`
- 输出 comparison bundle 与 `report.md`

结果目录约定：
- `results/chunking_eval/<run_id>/baseline/`
- `results/chunking_eval/<run_id>/doc_type_aware/`
- `results/chunking_eval/<run_id>/comparison/`
- `results/chunking_eval/<run_id>/report.md`
- `results/chunking_eval/<run_id>/manifest.json`

## 数据集状态
当前仓库已包含可通过 schema 校验的评测数据集：
- `data/evaluation/gold/gold_set.json`
- `data/evaluation/synthetic/synthetic_dataset.json`
- `data/evaluation/shared/source_registry.json`
- `data/evaluation/shared/eval_schema.py`

样本结构统一要求：
- 顶层字段：`id`、`question`、`reference_answer`、`evidence`、`metadata`
- `evidence` 字段：`quote`、`source_id`、`locator`
- `metadata` 字段：`difficulty`、`topic`、`doc_type`

## 当前限制与后续方向
- `eval/eval_ragas.py` 仍是 baseline runner，而不是完整 Ragas pipeline
- `judge_eval` 已是可复现的真实 LLM judge，但仍依赖本地 provider / model 配置
- Gold Set 已扩到 30 题并作为当前版本闸门；Synthetic Set 保持为辅助覆盖集
- v1.2 的 hybrid retrieval、reranker、HyDE、hierarchical index 仍处于规划状态

## 运行说明
### 环境依赖
- 主运行依赖见 `requirements.txt`
- 文档清洗专项依赖见 `requirements-source-cleaning.txt`

### 运行时配置
运行时配置统一从 `config/runtime_models.json` 加载；如本地仍保留旧 `config/key.json`，当前实现会仅作为兼容输入读取，但公开入口以 `config/runtime_models.json` 为准。

推荐字段：
- `provider`
- `api_key`
- `base_url`
- `chat_model_name`
- `embedding_model_name`

示例：
```json
{
  "provider": "modelscope",
  "api_key": "your-api-key",
  "base_url": "https://api-inference.modelscope.cn/v1",
  "chat_model_name": "Qwen/Qwen2.5-72B-Instruct",
  "embedding_model_name": "Qwen/Qwen3-Embedding-8B"
}
```

仓库提供了可提交的示例文件 `config/runtime_models.example.json`；本地使用时请复制为 `config/runtime_models.json` 后再填写真实值。

该文件仅用于本地运行，不应提交到仓库。

## 文档导航
- 评估框架与指标：`docs/evaluation.md`
- 仓库使用说明：`docs/repo_guide.md`
- 其余规划与资料文档由仓库外层文档映射维护

## 下一步迭代
1. 进入 v1.2 检索层消融实验，实现 hybrid retrieval、reranker、HyDE、hierarchical index
2. 在现有 artifact contract 上继续做 retrieval-side ablation
3. 如有需要，再补充更完整的 Ragas 风格指标
