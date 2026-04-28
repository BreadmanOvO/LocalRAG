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

当前 metrics 包含基础统计、客观答案指标与 evidence 命中统计：
- `sample_count`
- `answered_count`
- `answered_ratio`
- `context_hit_count`
- `context_hit_ratio`
- `retrieved_row_count`
- `avg_retrieved_row_count`
- `retrieval_debug_candidate_count`
- `avg_retrieval_debug_candidate_count`
- `exact_match_count`
- `exact_match_ratio`
- `normalized_exact_match_count`
- `normalized_exact_match_ratio`
- `reference_substring_hit_count`
- `reference_substring_hit_ratio`
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
- 调用真实 LLM 做 pairwise judgement，并固定 `temperature=0`
- 使用版本化 prompt rubric，比对 reference answer、retrieved_rows、evidence 与 answer
- 从模型返回文本中提取严格 JSON contract：`{"winner":"baseline|candidate|tie","reason":"..."}`
- 会落盘 `judgements.json`、`summary.json`、`manifest.json`

当前 summary 包含：
- `sample_count`
- `candidate_win_count`
- `baseline_win_count`
- `tie_count`

当前限制：
- 当前不是完整 Ragas pipeline，baseline_eval 仍以轻量客观指标为主
- Judge 已接入真实 LLM-as-a-Judge，但仍依赖本地 provider / model 配置
- pairwise 结论已可用于回归比较，但仍受具体模型能力与本地运行时配置影响

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
- Gold Set 至少 30 条
- Synthetic Set 至少 10 条
- Gold Set 自身需覆盖核心主题：`system_architecture`、`perception`、`planning_control`、`safety`、`sensor_fusion`
- Gold Set 自身必须至少包含一种 `report` 类型样本

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
当前适合用于：
- 进行 baseline / candidate 的 pairwise 回归比较
- 复用稳定的 judge artifact contract 与 `judge_prompt_version`
- 对候选版本做小规模真实 LLM 裁判验证

### chunking_eval
当前最适合用于：
- 比较不同 chunking 策略的 source hit / locator hit
- 做 retrieval inspection
- 观察不同 `doc_type` 的切分收益差异

## 与目标态的差距
以下能力仍是 v1.2 之前的延展方向：
- 如有需要，为 baseline_eval 接入更完整的 Ragas 风格指标
- 继续扩充 Gold / Synthetic 数据集，增强版本闸门强度
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
