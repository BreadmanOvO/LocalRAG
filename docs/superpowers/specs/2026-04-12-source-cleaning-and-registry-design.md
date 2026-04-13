# 原始 PDF 清洗与来源登记设计

## 1. 背景
当前仓库中已经存在两套与知识源相关的内容：

1. `data/sources/raw/**/*` 中保存的原始 PDF。
2. `data/sources/{apollo,standards,papers}/*.md` 中保存的早期整理稿或摘要稿。

现状问题是：
- 原始 PDF 的权威性和完整性更高，但尚未统一转化为后续评估可直接使用的 clean md。
- 现有部分 md 质量不一致，尤其标准类文档存在明显网页脚本、导航噪音和非正文内容混入的问题。
- 仓库中尚未落地正式的 `source_registry.json`，导致后续 Gold Set、Synthetic Set 和证据追溯缺少统一来源标识。

为了保证 `v1.0 Baseline` 阶段的数据基础稳定，本次设计明确：以 raw PDF 作为唯一可信原始来源，重建 clean md，再基于 clean md 建立统一来源登记。

## 2. 目标
本次设计的目标是：
1. 明确 raw PDF 到 clean md 的统一处理规则。
2. 统一 clean md 的文档结构、字段和质量要求。
3. 规定旧 md 与新 clean md 的关系，避免继续在脏底稿上修补。
4. 定义 `source_registry.json` 的字段结构与登记时机。
5. 为后续 Gold Set / Synthetic Set 的证据抽取提供稳定、可追溯的来源基础。

## 3. 非目标
1. 不在本次设计中实现检索、chunking、向量库或评估脚本。
2. 不在本次设计中直接编写 Gold Set 或 Synthetic Set 样本。
3. 不要求本次设计产出逐字全文转录版本。
4. 不在本次设计中删除现有旧 md 文件。
5. 不把尚未通过质量检查的 clean md 提前写入 `source_registry.json`。

## 4. 当前输入范围
本次处理范围覆盖 `data/sources/raw/**/*` 下的全部 PDF。

### 4.1 Apollo
- `data/sources/raw/apollo/apollo-devcenter-learning-path.pdf`
- `data/sources/raw/apollo/Apollo-Cyber-RT-framework.pdf`
- `data/sources/raw/apollo/apollo-channel-data-format.pdf`
- `data/sources/raw/apollo/Apollo-Open-Platform-overview.pdf`
- `data/sources/raw/apollo/apollo-perception-fusion-overview.pdf`
- `data/sources/raw/apollo/apollo-vision-perception-overview.pdf`
- `data/sources/raw/apollo/apollo-vision-prediction-overview.pdf`
- `data/sources/raw/apollo/apollo-vision-plan-overview.pdf`
- `data/sources/raw/apollo/apollo-vision-control-overview.pdf`
- `data/sources/raw/apollo/apollo-vision-location-overview.pdf`

### 4.2 Standards
- `data/sources/raw/standards/NHTSA ADS overview.pdf`
- `data/sources/raw/standards/Automated Driving Systems 2.0 A Vision for Safety.pdf`
- `data/sources/raw/standards/Preparing for the Future of Transportation Automated Vehicles 3.0.pdf`
- `data/sources/raw/standards/Ensuring American Leadership in Automated Vehicle Technologies AV 4.0.pdf`
- `data/sources/raw/standards/Automated Driving System Safety Overview of NHTSA Activities.pdf`
- `data/sources/raw/standards/Overview of Select NHTSA Activities – Automated Driving Systems.pdf`
- `data/sources/raw/standards/UN Regulation No. 155 - Cyber security and cyber security management system.pdf`
- `data/sources/raw/standards/UN Regulation No. 156 - Software update and software update management system.pdf`
- `data/sources/raw/standards/UN Regulation No. 157 - Automated Lane Keeping Systems (ALKS).pdf`

### 4.3 Papers
- `data/sources/raw/papers/BEVFormer.pdf`
- `data/sources/raw/papers/BEVFusion.pdf`
- `data/sources/raw/papers/Occupancy Flow Fields for Motion Forecasting in Autonomous Driving.pdf`
- `data/sources/raw/papers/Scalability in Perception for Autonomous Driving Waymo Open Dataset.pdf`
- `data/sources/raw/papers/VAD Vectorized Scene Representation for Efficient Autonomous Driving.pdf`
- `data/sources/raw/papers/FusionAD Multi-modality Fusion for Prediction and Planning Tasks of Autonomous.pdf`
- `data/sources/raw/papers/GenAD Generative End-to-End Autonomous Driving.pdf`

## 5. 核心设计决定
### 5.1 raw PDF 是唯一真源
`data/sources/raw/**/*` 下的 PDF 作为唯一可信原始来源。所有 clean md 均以 raw PDF 为基础重建，而不是在旧 md 上继续修补。

### 5.2 clean md 采用混合型结构
每份 clean md 同时满足两类需求：
- **快速阅读**：通过摘要、关键点和结构化笔记快速理解内容。
- **证据抽取**：通过带页码的摘录支持 Gold Set 和 Synthetic Set 的证据追溯。

### 5.3 旧 md 暂不删除，但不再作为权威底稿
现有 `data/sources/*.md` 暂时保留，便于对照和回溯，但后续一律以新 clean md 为准。`source_registry.json` 只登记新的 clean md。

### 5.4 范围一次性确定，执行分批推进
虽然本次覆盖全部 raw PDF，但具体执行顺序按三批推进：
1. Apollo
2. Standards
3. Papers

这样既保证统一模板和统一范围，也便于中途抽检和局部修正。

## 6. clean md 输出目录
新的 clean md 继续放在现有目录结构下：

- `data/sources/apollo/*.md`
- `data/sources/standards/*.md`
- `data/sources/papers/*.md`

命名要求：
- 与 raw 文件主题保持一致。
- 优先使用小写连字符命名。
- 若需要与旧文件共存，优先直接覆盖同主题旧 md；若无法安全判定对应关系，可先以新文件名写入，再在来源登记阶段统一切换。

## 7. clean md 模板
每份 clean md 统一采用以下结构：

```md
# <文档标题>

- Source type: official_doc | standard | paper | report
- Category: apollo | standards | papers
- Original file: data/sources/raw/...
- Original URL: ...
- Language: zh | en
- Version: ...
- Pages: ...
- Topic tags: [tag1, tag2, ...]

## Summary
2-5 句摘要，说明文档用途、核心主题和适用范围。

## Key points
- 3-8 条关键结论
- 优先保留定义、模块职责、流程、约束、结论

## Structured notes
### 1. ...
### 2. ...
### 3. ...

## Evidence-ready excerpts
- [p.3] ...
- [p.7] ...
- [p.12] ...

## Cleaning notes
- 是否文本层提取
- 是否可能存在 OCR 噪音
- 图表/公式是否未完整转写
- 是否需要人工复核
```

### 7.1 字段规则
- `Original file`：必须填写对应 raw PDF 路径。
- `Original URL`：若已知则填写原始来源链接；未知时可写 `unknown`，后续补齐。
- `Pages`：优先填写 PDF 总页数。
- `Topic tags`：控制在 2–5 个，便于后续筛选与覆盖分析。
- `Evidence-ready excerpts`：必须带页码，至少包含一组可直接引用的摘录。

### 7.2 内容规则
- 不追求全文逐字转录。
- 不保留导航、脚本、页眉页脚、重复版权说明等噪音。
- Apollo 文档优先保留模块职责、输入输出、数据流、系统关系。
- Standards 文档优先保留定义、适用范围、要求、边界条件。
- Papers 文档优先保留任务定义、方法核心、贡献点、实验结论。

## 8. 文档处理流程
每份 raw PDF 统一按以下流程处理：

1. 读取 raw PDF。
2. 提取正文内容。
3. 清理明显噪音。
4. 整理为 clean md。
5. 补齐元信息头。
6. 提炼摘要、关键点和结构化笔记。
7. 摘录带页码证据片段。
8. 进行人工快速复核。
9. 写入正式目录。

### 8.1 提取要求
优先保留：
- 标题
- 分节标题
- 正文段落
- 表格中的关键信息
- 与结论直接相关的图表文字

优先删除：
- 网页脚本
- 导航栏文本
- 页眉页脚重复内容
- 与正文无关的版权、登录、UI 组件文本

### 8.2 人工快速复核要求
每份 clean md 至少快速检查以下内容：
- 标题是否正确
- 分类是否正确
- 原始文件路径是否正确
- 是否存在明显脏文本
- 摘要是否与正文一致
- 是否有可直接引用的页码摘录

## 9. 质量闸门
只有满足以下条件的 clean md，才允许进入正式来源登记：
1. 标题正确。
2. `Original file` 正确。
3. `Source type` 与 `Category` 正确。
4. `Topic tags` 合理。
5. 无明显脏文本残留。
6. 至少有一组带页码的 `Evidence-ready excerpts`。
7. `Summary`、`Key points` 与正文无明显矛盾。

如果某份文档暂时不满足条件：
- 可以先保留 clean md。
- 必须在 `Cleaning notes` 中标记问题。
- 暂不写入 `source_registry.json`。

## 10. source_registry 设计
正式来源登记文件落在：
- `data/evaluation/shared/source_registry.json`

每条记录至少包含：
- `source_id`
- `title`
- `source_type`
- `category`
- `language`
- `path_or_url`
- `raw_path`
- `origin_url`
- `version`
- `topic_tags`
- `notes`

### 10.1 示例
```json
{
  "source_id": "apollo-doc-001",
  "title": "Apollo Perception Fusion Overview",
  "source_type": "official_doc",
  "category": "apollo",
  "language": "zh",
  "path_or_url": "data/sources/apollo/apollo-perception-fusion-overview.md",
  "raw_path": "data/sources/raw/apollo/apollo-perception-fusion-overview.pdf",
  "origin_url": "https://developer.apollo.auto/...",
  "version": "Apollo Doc CN 6.0",
  "topic_tags": ["perception", "sensor_fusion"],
  "notes": "cleaned from raw PDF with page-level excerpts"
}
```

### 10.2 登记规则
- 只登记通过质量闸门的 clean md。
- `path_or_url` 指向 clean md，而不是 raw PDF。
- `raw_path` 保留原始 PDF 路径，用于追溯。
- `origin_url` 允许后补，但建议尽快补齐。
- `source_id` 保持稳定，不因排序调整反复变动。

## 11. 错误与特殊情况处理
### 11.1 PDF 提取质量差
如果 PDF 提取质量较差：
- 允许先生成 clean md。
- 在 `Cleaning notes` 中标记“需人工复核”。
- 不立即写入 `source_registry.json`。

### 11.2 原始 URL 缺失
如果原始来源链接暂时无法确认：
- `Original URL` / `origin_url` 可先写 `unknown`。
- 后续补齐时只更新字段，不改变 `source_id`。

### 11.3 旧 md 与 raw 冲突
若旧 md 与 raw PDF 内容存在冲突：
- 一律以 raw PDF 为准。
- 旧 md 不再继续修补。

## 12. 执行顺序
### 第一批：Apollo
优先处理：
- perception fusion
- vision perception
- prediction
- planning
- control
- localization
- Cyber RT
- Open Platform
- channel data format
- devcenter learning path

### 第二批：Standards
优先处理：
- NHTSA ADS / AV 2.0 / AV 3.0 / AV 4.0
- NHTSA activities overview
- UNECE R155 / R156 / R157

### 第三批：Papers
统一处理：
- BEVFormer
- BEVFusion
- Occupancy Flow Fields
- Waymo report
- VAD
- FusionAD
- GenAD

## 13. 验证与验收标准
如果满足以下条件，则认为本阶段文档处理与来源登记设计达成目标：
1. 所有 raw PDF 都有对应的 clean md 处理计划。
2. 新 clean md 结构统一，且支持快速阅读与页码证据抽取。
3. 脏 md 不再作为来源登记基底。
4. `source_registry.json` 的字段和登记规则已明确。
5. 后续可以在不改动本设计的前提下，直接进入 clean md 产出和来源登记实施。

## 14. 后续实现边界
本设计批准后的后续实现应限定在以下范围：
1. 从 raw PDF 重建 clean md。
2. 抽检 clean md 质量。
3. 建立 `data/evaluation/shared/source_registry.json`。
4. 不在这一阶段同时引入检索、chunking、评估脚本或数据集样本编写。

## 15. 说明
根据当前仓库协作规则，本次仅写入设计文档，不自动创建 git commit。若后续需要提交该 spec，再由用户明确指示进行提交。
