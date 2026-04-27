# 评估框架与指标口径

## 文档用途
本文件描述当前仓库中已经落地的评测链路、结果目录合同，以及仍处于目标态的评估能力。阅读时应区分“已经实现”和“后续计划”，不要把规划项当成当前能力。

## 当前已落地的评测链路

### 1. baseline_eval
入口：`eval/eval_ragas.py`

当前实现状态：
- 会先加载并校验数据集 schema
- 会校验运行时配置是否可用
- 通过 `RagService.answer_with_retrieval()` 生成 retrieval-aware prediction
- 会落盘 `predictions.json`、`metrics.json`、`manifest.json`

当前 prediction 记录包含：
- `id`
- `question`
- `reference_answer`
- `answer`
- `retrieved_context`
- `retrieved_rows`
- `retrieval_debug_candidates`
- `evidence`
- `metadata`

当前 metrics 包含基础统计与 evidence 命中统计：
- `sample_count`
- `answered_count`
- `answered_ratio`
- `context_hit_count`
- `context_hit_ratio`
- `evidence_source_hit_count`
- `evidence_source_hit_ratio`
- `evidence_locator_hit_count`
- `evidence_locator_hit_ratio`

结果目录合同：
- `results/baseline_eval/<run_id>/predictions.json`
- `results/baseline_eval/<run_id>/metrics.json`
- `results/baseline_eval/<run_id>/manifest.json`

### 2. judge_eval
入口：`eval/eval_llm_judge.py`

当前实现状态：
- 读取 baseline 与 candidate 两份 predictions
- 校验两侧 sample id 完全一致
- 基于 answer 是否非空、evidence source hit、evidence locator hit 做 deterministic pairwise 判分
- 会落盘 `judgements.json`、`summary.json`、`manifest.json`

当前 summary 包含：
- `sample_count`
- `candidate_win_count`
- `baseline_win_count`
- `tie_count`

当前限制：
- `winner` 已不再是全 tie 占位逻辑，但仍属于规则式 judge，而不是真实 LLM-as-a-Judge
- `reason` 当前记录的是规则式打分依据，不是自然语言评审结论
- 尚未接入真实 LLM-as-a-Judge 判分标准

结果目录合同：
- `results/judge_eval/<baseline_run_id>-vs-<candidate_run_id>/judgements.json`
- `results/judge_eval/<baseline_run_id>-vs-<candidate_run_id>/summary.json`
- `results/judge_eval/<baseline_run_id>-vs-<candidate_run_id>/manifest.json`

### 3. chunking_eval
入口：`eval/eval_chunking.py`

这是当前最完整的一条实验链路，支持：
- baseline chunking
- `doc_type_aware` chunking
- source-level evidence hit 统计
- locator-level evidence hit 统计
- 分 `doc_type` / `source_id` 聚合对比
- error cases 汇总
- `report.md` 汇报输出

结果目录合同：
- `results/chunking_eval/<run_id>/baseline/`
- `results/chunking_eval/<run_id>/doc_type_aware/`
- `results/chunking_eval/<run_id>/comparison/`
- `results/chunking_eval/<run_id>/report.md`
- `results/chunking_eval/<run_id>/manifest.json`

## 数据集合同
数据文件：
- `data/evaluation/gold/gold_set.json`
- `data/evaluation/synthetic/synthetic_dataset.json`
- `data/evaluation/shared/eval_schema.py`

每条样本必须包含：
- `id`
- `question`
- `reference_answer`
- `evidence`
- `metadata`

`evidence` 内每项必须包含：
- `quote`
- `source_id`
- `locator`

`metadata` 必须包含：
- `difficulty`
- `topic`
- `doc_type`

当前 schema 测试还约束：
- Gold Set 至少 8 条
- Synthetic Set 至少 14 条
- 合并后需覆盖核心主题：`system_architecture`、`perception`、`planning_control`、`safety`、`sensor_fusion`
- 合并后必须至少包含一种 `report` 类型样本

## 当前口径下的指标解释

### baseline_eval
当前只适合回答这类问题：
- 能否稳定产出回答
- 能否稳定产出检索上下文
- retrieval-aware prediction 格式是否稳定

它暂时不能回答这类问题：
- faithfulness 是否提升
- answer_relevancy 是否提升
- 版本之间是否存在显著主观质量差异

### judge_eval
当前只适合验证：
- pairwise 输入输出合同是否稳定
- 后续接入真实 Judge 时目录与数据结构是否可复用

它暂时不能作为真实版本胜负结论。

### chunking_eval
当前最适合用于：
- 比较不同 chunking 策略的 source hit / locator hit
- 做 retrieval inspection
- 观察不同 `doc_type` 的切分收益差异

## 与目标态的差距
以下能力仍是 v1.1 的收尾项或 v1.2 之前的准备项：
- 为 baseline_eval 接入更完整的客观指标
- 为 judge_eval 接入真实 LLM 判分逻辑
- 继续扩充 Gold / Synthetic 数据集
- 用统一 artifact contract 支撑后续 hybrid retrieval / reranker 消融实验

## 运行前提
运行评测脚本前需要本地提供 `config/runtime_models.json`，统一字段包括：
- `provider`
- `api_key`
- `base_url`
- `chat_model_name`
- `embedding_model_name`

当前实现会兼容旧 `config/key.json` 作为历史本地输入，但该兼容路径不是新的公开配置入口。
仓库内可参考 `config/runtime_models.example.json`，本地运行时复制为 `config/runtime_models.json` 并填写真实值。

## 使用建议
- 看当前真实实验能力时，优先参考 `eval/eval_chunking.py` 与 `results/chunking_eval/`
- 看 baseline / judge 合同时，优先参考 `eval/eval_ragas.py`、`eval/eval_llm_judge.py` 与对应测试
- 新增评测脚本或结果目录时，同步更新本文件与 `docs/repo_guide.md`
