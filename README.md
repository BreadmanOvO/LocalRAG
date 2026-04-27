# 自动驾驶感知算法 LocalRAG

## 项目简介
这是一个面向自动驾驶感知算法场景的垂直领域 RAG 项目，当前主线是先补齐 v1.1 的数据、评测与文档合同，再进入 v1.2 检索层消融实验。

## 当前定位
- 项目状态：v1.1 收尾中
- 当前最高优先级：补齐评测数据集、稳定 artifact contract、修正文档口径
- v1.2 状态：尚未正式展开，仅保留检索层实验规划

## 当前已落地能力
- Agent 问答入口：`app_qa.py` + `agent/react_agent.py`
- 文件上传与入库入口：`app_file_uploader.py`
- 核心 RAG 服务：`core/rag.py`
- 知识库入库与 chunk 写入：`core/knowledge_base.py`
- chunking 与 locator / provenance metadata：`core/chunking.py`
- baseline 评测 runner：`eval/eval_ragas.py`
- pairwise judge scaffold：`eval/eval_llm_judge.py`
- chunking 对比实验：`eval/eval_chunking.py`

## 当前评测状态
### 1. baseline_eval
`eval/eval_ragas.py` 已升级为 retrieval-aware baseline runner：
- 调用 `RagService.answer_with_retrieval()`
- 预测结果包含：`answer`、`retrieved_context`、`retrieved_rows`、`retrieval_debug_candidates`、`evidence`、`metadata`
- 当前 metrics 已包含 answered/context 命中与 evidence source/locator 命中统计
- 支持按 run bundle 输出结果目录

结果目录约定：
- `results/baseline_eval/<run_id>/predictions.json`
- `results/baseline_eval/<run_id>/metrics.json`
- `results/baseline_eval/<run_id>/manifest.json`

### 2. judge_eval
`eval/eval_llm_judge.py` 目前是 pairwise scaffold：
- 输入 baseline / candidate 两份 predictions
- 校验 sample id 集合一致
- 基于 answer/evidence 命中情况做 deterministic pairwise 判分
- 输出 `judgements.json`、`summary.json`、`manifest.json`
- 当前仍未接入真实 LLM Judge，现阶段主要用于稳定 pairwise contract 与回归比较

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

## 当前仍未完成的部分
- `ragas` 真实指标尚未接入，`eval/eval_ragas.py` 目前仍是 baseline runner，而不是完整 Ragas pipeline
- `eval/eval_llm_judge.py` 尚未接入真实 LLM 判分逻辑
- Gold / Synthetic 数据集虽然已满足当前合同，但离最终版本闸门规模仍有差距
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
- [版本规划](docs/roadmap.md)
- [评估框架与指标](docs/evaluation.md)
- [仓库使用说明](docs/repo_guide.md)
- [简历表达与面试亮点](docs/resume_notes.md)
- [参考资料与学习路径](docs/references.md)

## 下一步迭代
1. 继续扩充 Gold Set 与 Synthetic Set，提高版本闸门强度
2. 为 baseline_eval 接入更完整的客观指标
3. 为 judge_eval 接入真实 pairwise LLM 判分流程
4. 在 v1.1 完整收口后，再启动 v1.2 检索层消融实验
