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

### 2.1 judge_formal_run
入口：`eval/eval_judge_formal_run.py`

当前用于 formal judge 结果整理：
- 读取既有 `judge_eval` run bundle
- 汇总关键判断结果与结论
- 输出面向验收的 `test_report.md`

结果目录合同补充：
- `results/judge_eval/<baseline_run_id>-vs-<candidate_run_id>/test_report.md`

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

### 4. retrieval_eval
入口：`eval/eval_retrieval_only.py`

纯检索评测，不经过 LLM 生成：
- 支持 dense / sparse / hybrid 检索模式
- 输出 Hit@k、MRR 等排名指标
- 适合快速迭代检索参数

结果目录合同：
- `results/retrieval_eval/<run_id>/predictions.json`
- `results/retrieval_eval/<run_id>/metrics.json`
- `results/retrieval_eval/<run_id>/manifest.json`

### 5. hybrid_eval
入口：`eval/eval_hybrid.py`

Hybrid Retrieval 对比实验：
- dense / sparse / hybrid 三种检索模式对比
- 融合权重 α 参数调优
- 输出各模式的 metrics 对比

结果目录合同：
- `results/hybrid_eval/<run_id>/predictions.json`
- `results/hybrid_eval/<run_id>/metrics.json`
- `results/hybrid_eval/<run_id>/manifest.json`

### 6. reranker_eval
入口：`eval/eval_reranker.py`

Reranker 效果评估：
- 有/无 reranker 的检索结果对比
- Hit@k、MRR 等排名指标对比

结果目录合同：
- `results/reranker_eval/<run_id>/predictions.json`
- `results/reranker_eval/<run_id>/metrics.json`
- `results/reranker_eval/<run_id>/manifest.json`

### 7. sparse_compare
入口：`eval/eval_sparse_compare.py`

Sparse Retrieval 对比实验：
- BM25 等稀疏检索方法的效果评估

结果目录合同：
- `results/sparse_compare/<run_id>/predictions.json`
- `results/sparse_compare/<run_id>/metrics.json`
- `results/sparse_compare/<run_id>/manifest.json`

### 8. inspection
入口：`eval/eval_inspection.py`

手动检索检查：
- 小规模 gold item 的召回结果检查
- 用于调试和验证检索行为

结果目录合同：
- `results/inspection/<run_id>/`

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

## v1.1 收口状态
v1.1 已完成收口，详见 `RAG_md/docs/reports/v1.1-closure-report.md`。

核心结论：
- 评测基础设施已就绪（30 题 Gold gate + chunking_eval + judge_eval + formal pipeline）
- doc_type_aware chunking 在当前 30 题上未显著优于 baseline chunking（source_hit_ratio 均为 0.4）
- 下一步进入 v1.2 检索层：BGE-M3 + Qdrant → hybrid retrieval → inspection → reranker

## v1.2 检索层（已完成）

### 已完成
- 嵌入模型切换：LocalHash → Qwen3-Embedding-0.6B → **BAAI/bge-m3（本地 sentence-transformers）**
- Hybrid Retrieval：dense + BM25 sparse，最优 α=0.5
- Cross-Encoder Reranker：`BAAI/bge-reranker-base`
- 文档扩充：26 篇 → 41 篇（新增 Apollo 模块 5 篇 + 论文 5 篇 + 标准 5 篇）
- 评测集扩充：30 题 → 100 题
- **语义分块（Semantic Chunking）**：基于句子嵌入相似度的断点检测
- **排名指标**：MRR、Hit@1、Hit@3

### 最新评测结果（2026-05-08，100 题，bge-m3 本地，41 篇文档，含排名指标）
| 分块策略 | Reranker | Hit@5 | MRR | Hit@1 | Hit@3 | 命中数 |
|---------|:--------:|:-----:|:---:|:-----:|:-----:|:------:|
| baseline | No | 0.960 | 0.865 | 0.790 | 0.940 | 96 |
| baseline | Yes | 0.960 | 0.899 | 0.850 | 0.950 | 96 |
| doc_type_aware | No | 0.940 | 0.870 | 0.830 | 0.900 | 94 |
| doc_type_aware | Yes | 0.960 | **0.904** | **0.860** | 0.950 | 96 |
| **semantic** | No | **0.970** | 0.864 | 0.800 | 0.920 | **97** |
| **semantic** | Yes | **0.980** | 0.897 | 0.840 | 0.950 | **98** |

**关键发现**：
1. Reranker 的真实价值在排名指标下可见：Hit@1 +6.0%，MRR +3.9%（baseline 配置）
2. 语义分块最优：Hit@5 97%→98%（+reranker），解决 2 道其他策略未命中题目
3. 最优配置：semantic + reranker = 98% Hit@5，0.897 MRR
详见 `RAG_md/docs/reports/v1.2-chunking-comparison-report.md`。

## 使用建议
- 看当前真实实验能力时，优先参考 `eval/eval_chunking.py` 与 `results/chunking_eval/`
- 看 baseline / judge 合同时，优先参考 `eval/eval_ragas.py`、`eval/eval_llm_judge.py` 与对应测试
- 新增评测脚本或结果目录时，同步更新本文件与 `docs/repo_guide.md`
