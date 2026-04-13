# 评估数据设计（v1.0 Baseline 第一步）

## 1. 背景
当前项目在 `README.md`、`docs/evaluation.md`、`docs/roadmap.md` 中已经明确：`v1.0 Baseline` 的首要任务是先建立可复用的评估基线，再推进数据层与检索层升级。

在这个阶段，最先需要落地的不是评估脚本实现，也不是批量造数，而是统一定义评估数据的结构、边界和质量规则。只有先把评估数据设计清楚，后续的人工 Gold Set 编写、Synthetic Set 批量生成、Ragas 评估和 LLM-as-a-Judge 对比，才能共享同一套输入契约，避免返工。

## 2. 目标
本次设计只覆盖评估数据层，不涉及评估脚本实现、RAG 系统实现或批量样本生产。

设计目标：
1. 定义 `Gold Set` 与 `Synthetic Set` 的目录结构。
2. 定义两类数据集的 schema 和字段语义。
3. 明确主题、难度、题型、来源追溯等公共规范。
4. 明确 Gold 与 Synthetic 的质量门槛差异。
5. 为后续 `eval_ragas.py`、`eval_llm_judge.py` 和 `results/*.json` 提供稳定接口约定。

## 3. 非目标
1. 不在本设计中实现 `eval_ragas.py` 或 `eval_llm_judge.py`。
2. 不在本设计中批量编写正式 Gold/Synthetic 样本。
3. 不在本设计中决定具体的检索实现、嵌入模型或评估提示词。
4. 不把评估运行结果回写到基准数据集文件中。

## 4. 数据目录结构
建议在仓库中单独建立评估数据目录，避免把评估样本散落到 `docs/` 或脚本目录中。

```text
data/
  evaluation/
    gold/
      gold_set.jsonl
      gold_set_schema.md
      manifest.json
    synthetic/
      synthetic_dataset.jsonl
      synthetic_generation_spec.md
      manifest.json
    shared/
      taxonomy.md
      source_registry.json
```

### 4.1 目录职责
- `data/evaluation/gold/gold_set.jsonl`
  - 人工高质量标注集。
  - 初期规模 30–50 条。
  - 作为版本闸门主基准。
- `data/evaluation/gold/gold_set_schema.md`
  - 记录 Gold Set 字段说明与标注规范。
- `data/evaluation/gold/manifest.json`
  - 记录数据集版本、样本数、语言、审核过滤条件等元信息。
- `data/evaluation/synthetic/synthetic_dataset.jsonl`
  - 扩展覆盖集。
  - 首期目标 200+ 条，后续逐步扩容。
- `data/evaluation/synthetic/synthetic_generation_spec.md`
  - 记录 Synthetic 生成原则与抽检要求。
- `data/evaluation/synthetic/manifest.json`
  - 记录 Synthetic 数据集版本和统计信息。
- `data/evaluation/shared/taxonomy.md`
  - 统一定义主题、难度、题型等枚举口径。
- `data/evaluation/shared/source_registry.json`
  - 统一登记来源文档的 `source_id`、标题、类型、版本和路径/链接。

### 4.2 文件格式选择
评估样本主文件采用 `jsonl`，而不是单个大 JSON 数组。原因：
1. 便于逐条追加和抽样检查。
2. 便于后续脚本做流式读取。
3. Git diff 更清晰，更适合长期迭代维护。
4. 后续若要拆分批次，也更容易按行处理。

规则文档使用 Markdown，来源登记使用 JSON。

## 5. Gold Set 设计
Gold Set 的定位是人工精标主基准集，用于版本闸门、关键回归验证和核心结论支撑。它必须可核验、可追溯、可重复使用。

### 5.1 单条样本结构
文件：`data/evaluation/gold/gold_set.jsonl`

```json
{
  "id": "gold-0001",
  "question": "什么是 BEV 感知，它相对前视视角感知的主要优势是什么？",
  "reference_answer": "BEV 感知是将多传感器信息映射到鸟瞰视角统一建模的方法，主要优势是空间尺度更一致，更适合做多目标关系建模、占用理解与规划协同。",
  "evidence": [
    {
      "source_id": "apollo-doc-001",
      "locator": "chapter=3/section=3.2",
      "quote": "..."
    }
  ],
  "topic": "perception",
  "difficulty": "medium",
  "question_type": "principle_explanation",
  "keywords": ["BEV", "多传感器融合", "空间表示"],
  "language": "zh",
  "review_status": "approved"
}
```

### 5.2 必填字段
- `id`
  - 稳定样本 ID，如 `gold-0001`。
- `question`
  - 待评估问题。
- `reference_answer`
  - 标准答案，要求可直接作为评估参考。
- `evidence`
  - 非空数组，至少包含 1 条证据。
- `topic`
  - 主题分类。
- `difficulty`
  - 难度等级。
- `question_type`
  - 题型分类。
- `keywords`
  - 便于筛选与误差分析的关键词。
- `language`
  - 当前首版固定为 `zh`。
- `review_status`
  - 人工审核状态。

### 5.3 `evidence` 结构
每条证据建议采用：
- `source_id`
- `locator`
- `quote`

其中：
- `source_id` 用于关联 `source_registry.json`
- `locator` 用于描述原文定位，例如 `page=5/paragraph=2` 或 `chapter=3/section=3.2`
- `quote` 用于保存支撑答案关键结论的摘录

### 5.4 关键设计决定
Gold Set **不把 `chunk_id` 设为必填字段**。

原因：
1. `v1.1-v1.2` 阶段会持续调整 chunking 与 metadata 策略，`chunk_id` 很容易失效。
2. Gold Set 应绑定原始知识证据位置，而不是绑定某一版切分产物。
3. 这样可以让同一份 Gold Set 被不同切分策略和不同检索版本重复使用。

因此，证据追溯统一采用：
- `source_id` + `locator` + `quote`

而不是：
- `source_id` + `chunk_id`

### 5.5 不属于 Gold Set 的字段
以下字段属于评估运行结果，**不应写回基准集**：
- `retrieved_contexts`
- `model_answer`
- `judge_score`
- `pairwise_result`

Gold Set 是静态基准输入，不应混入动态运行产物。

## 6. Synthetic Set 设计
Synthetic Set 的定位是扩展覆盖、压力测试和长尾观察。它不能替代 Gold Set 做版本闸门，但应尽量复用 Gold Set 主字段，以便共享读取和分析逻辑。

### 6.1 单条样本结构
文件：`data/evaluation/synthetic/synthetic_dataset.jsonl`

```json
{
  "id": "syn-0001",
  "question": "在自动驾驶感知系统中，为什么相机与激光雷达融合可以提升目标检测稳定性？",
  "reference_answer": "相机提供纹理和语义信息，激光雷达提供更稳定的几何和距离信息，二者融合可以在远距、遮挡和光照变化场景下提高检测鲁棒性。",
  "evidence": [
    {
      "source_id": "paper-003",
      "locator": "page=5/paragraph=2",
      "quote": "..."
    }
  ],
  "topic": "sensor_fusion",
  "difficulty": "medium",
  "question_type": "why_analysis",
  "keywords": ["camera", "lidar", "fusion"],
  "language": "zh",
  "generation_meta": {
    "method": "llm_generated",
    "source_basis": ["paper-003"],
    "validation_status": "pending"
  }
}
```

### 6.2 与 Gold Set 的关系
Synthetic Set 与 Gold Set 尽量保持同构。二者共享以下主字段：
- `id`
- `question`
- `reference_answer`
- `evidence`
- `topic`
- `difficulty`
- `question_type`
- `keywords`
- `language`

Synthetic Set 仅额外增加：
- `generation_meta`

这样做的好处：
1. `eval_ragas.py` 可以复用同一套读取逻辑。
2. 后续抽样升级时，部分 Synthetic 样本可以自然转为 Gold 样本。
3. Error analysis 不需要区分两套完全不同的数据格式。

### 6.3 `generation_meta` 结构
建议字段：
- `method`
- `source_basis`
- `validation_status`

含义：
- `method`
  - 生成方式，首版可固定为 `llm_generated`。
- `source_basis`
  - 这条样本主要基于哪些来源生成。
- `validation_status`
  - 当前校验状态，建议取值：`pending | checked | rejected`。

### 6.4 关键设计决定
Synthetic Set 允许“先生成、后抽检”，但**不允许没有证据来源**。

也就是说：
1. 可以先批量生成问题和参考答案。
2. 但每条都必须保留来源依据，至少要有 `source_basis`。
3. 进入正式评估前，必须保留可追溯证据；如果证据追溯不上，样本不能进入正式评估集。

## 7. 公共分类与来源规范
公共枚举和来源规则统一放入 `data/evaluation/shared/` 中维护。

### 7.1 主题分类 `topic`
首版建议固定为以下小而稳的枚举：
- `perception`
- `sensor_fusion`
- `planning_control`
- `safety`
- `system_architecture`

这样可以覆盖当前 README 和评估文档中强调的核心主线，同时避免一开始分类过细。

### 7.2 难度分类 `difficulty`
固定为：
- `easy`
- `medium`
- `hard`

约束：
- Gold Set：三档都要覆盖，避免全部变成术语解释题。
- Synthetic Set：按 `30% / 50% / 20%` 控制，与 `docs/evaluation.md` 保持一致。

### 7.3 题型分类 `question_type`
首版建议限制为：
- `definition`
- `principle_explanation`
- `why_analysis`
- `process_description`
- `comparison`
- `scenario_reasoning`

先保证少而清晰，后续确有需要再扩展。

### 7.4 来源登记 `source_registry.json`
建议统一登记来源，避免每条样本里重复长文本元信息。

单条来源示例：

```json
{
  "source_id": "apollo-doc-001",
  "title": "Apollo 感知模块文档",
  "source_type": "doc",
  "language": "zh",
  "path_or_url": "...",
  "version": "2026-04-10"
}
```

后续样本中仅引用 `source_id`，从而实现统一追溯与扩展。

## 8. 质量规则
### 8.1 通用规则
无论 Gold 还是 Synthetic，都应满足：
1. 一条样本只问一个核心问题，禁止把多个问题绑在一起。
2. `reference_answer` 必须可核验，不能只是模糊概述。
3. `evidence` 必须能支撑答案关键结论，而不是仅与问题相关。
4. 问题和答案口径必须一致，例如问“为什么”时不能只给定义。
5. 首版语言统一为中文 `zh`。
6. `keywords` 需要服务于检索分析，不追求数量，但要覆盖核心术语。

### 8.2 Gold Set 额外要求
Gold Set 作为版本闸门主基准，要求更严：
1. 每条必须人工审核。
2. 每条至少 1 条高质量证据。
3. 综合题建议至少 2 条证据。
4. `reference_answer` 尽量短而完整，建议 2–5 句。
5. 不收录“看起来对但证据弱”的样本。
6. `review_status` 仅在 `approved` 时才能进入正式 baseline 统计。

建议 `review_status` 取值：
- `draft`
- `approved`

### 8.3 Synthetic Set 额外要求
Synthetic Set 更强调规模和覆盖，但必须有底线：
1. 100% 通过 schema 校验。
2. 100% 有来源依据。
3. 至少抽检 10%–20%。
4. 抽检不合格的主题批次应整体回炉。
5. `validation_status` 不为 `checked` 的样本，不进入正式 baseline 统计。

## 9. 与后续评估脚本的接口约定
本设计的关键目标之一，是让当前定义的数据结构可以直接被后续评估脚本消费，而无需重新改 schema。

### 9.1 数据集只存静态真值
数据集文件中只保留以下静态内容：
- 问题
- 标准答案
- 证据
- 主题/难度/题型
- 来源信息
- 审核状态

不写入：
- 某次检索召回内容
- 某次模型回答
- 某次 judge 打分
- 某个版本的胜负结果

原则：**数据集是基准输入，运行结果是版本输出。**

### 9.2 `eval_ragas.py` 输入约定
`eval_ragas.py` 应把 Gold/Synthetic 样本作为基准输入，然后在运行时补充当前系统的：
- `retrieved_contexts`
- `generated_answer`

也就是说：

基准样本 → 调用当前版本 RAG 系统 → 得到检索上下文与生成答案 → 对齐 `reference_answer` 做 Ragas 评估

这样可以保证：
1. 数据集不依赖某个具体检索实现。
2. 后续替换 embedding、reranker、prompt 时不需要改数据结构。
3. 同一份数据集可以稳定复用到多个版本对比中。

### 9.3 `eval_llm_judge.py` 输入约定
LLM-as-a-Judge 的本质是系统 A 与系统 B 的回答对比。

Judge 脚本应基于两层输入：
1. 基准样本（来自 Gold/Synthetic 数据集）
2. 候选系统输出（运行时生成）

运行时输入示例：

```json
{
  "sample_id": "gold-0001",
  "system_a_answer": "...",
  "system_b_answer": "...",
  "reference_answer": "...",
  "evidence": [ ... ]
}
```

Judge 脚本读取时：
- 以 `sample_id` 回连基准样本
- 比较系统 A 与系统 B 的回答
- 输出胜负、理由与维度评分

关键约束：**pairwise comparison 是运行产物，不回写样本库。**

### 9.4 结果文件元信息约定
后续 `results/*.json` 建议至少记录：

```json
{
  "dataset_name": "gold_set",
  "dataset_version": "v1",
  "sample_count": 40,
  "filter": {
    "review_status": "approved"
  },
  "metrics": {
    "faithfulness": 0.0,
    "answer_relevancy": 0.0
  }
}
```

这样可以确保未来查看结果时，知道：
1. 用的是哪份数据集。
2. 用的是哪一版数据集。
3. 使用了什么过滤条件。
4. 结果是否可以与历史版本直接对比。

### 9.5 数据集版本管理
建议数据集版本信息放在 `manifest.json` 中，而不是每条样本重复写入。

Gold 示例：

```json
{
  "dataset_name": "gold_set",
  "dataset_version": "v1",
  "sample_count": 40,
  "language": "zh",
  "filter_for_baseline": {
    "review_status": "approved"
  }
}
```

Synthetic 示例：

```json
{
  "dataset_name": "synthetic_dataset",
  "dataset_version": "v1",
  "sample_count": 200,
  "language": "zh",
  "filter_for_baseline": {
    "validation_status": "checked"
  }
}
```

这样可以让结果文件与数据集版本稳定关联，同时保持样本本身干净。

## 10. 设计结论
本次设计的核心原则是：
1. Gold 与 Synthetic 结构尽量一致，差异主要体现在质量门槛上。
2. 数据集绑定原始证据位置，而不绑定某一版 chunk 产物。
3. 数据集保持静态，评估结果保持动态，严格分层。
4. 分类体系先小后大，避免前期过度复杂化。
5. 通过 `manifest.json` 与 `source_registry.json` 保证版本可追溯与来源可追溯。

## 11. 验收标准
如果后续落地满足以下条件，则认为本设计达成目标：
1. 可以按本 spec 创建 `gold_set.jsonl` 与 `synthetic_dataset.jsonl`，且字段边界清晰。
2. 不同人根据本 spec 标注样本时，能保持一致的字段理解与质量判断。
3. `eval_ragas.py` 与 `eval_llm_judge.py` 后续可直接消费这套数据，而不需要重构 schema。
4. 数据集版本、来源追溯和正式统计过滤条件都可被明确记录。
5. `v1.0 Baseline` 能基于这套设计继续推进样本编写与评估脚本实现。
