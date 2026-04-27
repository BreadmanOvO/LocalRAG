# 版本规划与技术路线

## 项目定位
- 自动驾驶感知算法垂直领域专家系统
- 目标时间：6 周分版本迭代
- 核心原则：评估先行、数据驱动、渐进优化
- 优化重点：简历含金量 + 工程落地能力
- 面试亮点：将自动驾驶领域背景与大模型技术深度结合，打造垂直行业解决方案

## 版本路线图

| 版本 | 时间 | 核心目标 | 关键产出 | 评估对比 | 亮点 |
|------|------|----------|----------|----------|------|
| **v1.0 Baseline** | 第1周 | 建立双评估框架与基准数据集 | Gold Set + Synthetic Set + 双评估基线 | - | 先建立可复用评估闭环 |
| **v1.1 数据层** | 第2周 | 文档清洗、source registry、结构化切分与 metadata 增强 | 文档解析结果 + baseline chunking + doc-type-aware chunking + metadata 规范 + 评测 artifact contract | vs v1.0 | 为检索优化建立稳定、可追溯输入 |
| **v1.2 检索层** | 第3周 | 分阶段升级检索链路：hybrid retrieval + retrieval inspection + reranker | 混合检索、检索检查能力、重排、检索消融实验结果 | vs v1.1 | 聚焦最可能产生核心收益的主链路 |
| **v1.3 模型层** | 第4-5周 | 仅在检索趋于稳定后再评估 QLoRA | 指令微调实验（条件满足时） | vs v1.2 | 用门槛控制训练投入 |

> 当前状态：v1.1 已落地 `source_registry`、baseline/doc-type-aware chunking、provenance metadata、真实 chunking 对比实验，以及 baseline/judge/chunking 三条结果目录合同。当前收尾重点已收敛为：补齐更完整的 baseline 客观指标、真实 LLM judge 逻辑，以及继续扩充评测数据集；在这些收口前，不进入 v1.2 检索层实现。
| **v1.4 工程增强** | 第6周 | UI、部署、性能优化与可选底层实验 | Chainlit / 部署整理 / 性能测试 / 可选 parent-child chunking | vs v1.3 | 把增强项放在主线之后 |

### v1.0 Baseline
- 建立人工小规模 Gold Set（30-50 题）
- 建立 Synthetic Set 作为扩展评估集
- 建立 Ragas + LLM-as-a-Judge 双评估框架
- 记录 baseline 指标与 retrieval/evidence 命中统计
- 产出 `data/evaluation/synthetic/synthetic_dataset.json`、`eval/eval_ragas.py`、`eval/eval_llm_judge.py`、`results/baseline_eval/<run_id>/`

### v1.1 数据层
- 已完成 `source_registry` 驱动的知识源入库路径与真实 chunking 对比实验骨架
- 已完成统一 baseline chunking 与按文档类型选择 chunk 策略的能力
- 已完成 chunk provenance metadata 规范，核心字段包括 `source_id`、`doc_type`、`chunk_order`、`chunk_strategy` 与可选 locator 信息
- 已完成真实 chunking 对比实验与结果产物落盘，当前已验证 `similarity_top_k = 5` 下 baseline 与 `doc_type_aware` 的 source-level 命中都达到 1.0
- 当前收尾项：更完整的 baseline 客观指标、真实 LLM judge 逻辑、评测数据集继续扩容，以及状态文档同步
- 多模态 OCR 作为增强项，仅在文本检索稳定后再深入

### v1.2 检索层
- 先切换嵌入模型到 BGE-M3、本地向量库到 Qdrant
- 明确知识库级 embedding 配置，避免同一知识库混用不同 embedding space
- 按消融顺序推进：
  1. baseline metadata/chunking
  2. doc-type-aware chunking
  3. hybrid retrieval
  4. retrieval inspection 增强
  5. reranker
  6. 可选 HyDE
  7. 可选 hierarchical index
- hybrid retrieval 以 dense + sparse/BM25 融合为主，先支持可调融合权重与召回阈值
- 增加 retrieval inspection 能力，用于查看 query、召回 chunk、chunk 分数、来源文档与切分策略
- 每一步都在同一套 Gold Set + Synthetic Set 上验证收益
- 重点验证检索层相对微调层的收益

### v1.3 模型层
- 仅在 retrieval + reranker 收益趋稳后再进入 QLoRA
- 前提是 error analysis 显示主要问题来自生成表达而非证据召回
- 基于 Qwen2-7B / Qwen3-8B 做条件式微调实验
- DPO 不纳入主线，作为后续可选加分实验

### v1.4 工程增强
- 将 UI 从 Streamlit 升级到 Chainlit
- 视情况补充 Docker 容器化
- 推进 llama.cpp 编译、量化与 TTFT 实验
- 如前序收益已趋稳，可选评估 parent-child chunking
- 工程增强不应阻塞评估与检索主线

## 技术决策

### 评估先行
- 第一周建立量化评估框架（Ragas + LLM-as-a-Judge）。
- 每个版本都跑同一套测试集，输出独立指标文件。
- 通过 pairwise 对战验证新版本相对上版本的实际收益。
- 评估优先使用人工 Gold Set，Synthetic Set 用于扩展覆盖与压力测试。

### 数据输入稳定优先
- 检索优化之前，先固定来源登记、清洗规则和 chunk 生成规则。
- `source_registry` 作为统一入口，保证每份知识源可追溯、可复查、可重复入库。
- 数据层优先解决“来源是否稳定、chunk 是否可靠、metadata 是否完整”，而不是过早堆叠复杂检索技巧。

### 文档类型感知 chunking
- 不再假设所有文档适用同一种 chunking 策略。
- chunking 策略至少按三类来源区分：官方文档、标准规范、论文/技术报告。
- 统一 baseline chunking 作为对照组，doc-type-aware chunking 作为 v1.2 首批消融项。
- chunk 元数据需显式记录 `chunk_strategy`，便于后续评测与误差分析。

### 检索可观察性优先
- 检索优化不能只看最终回答质量，还要能观察中间召回结果。
- 在 v1.2 阶段补齐 retrieval inspection 能力，用于展示 query、召回 chunk、融合分数、rerank 分数与来源信息。
- 每个 chunk 都应保留可追溯字段，至少包括 `source_id`、`doc_type`、页码/章节、`chunk_order`、`chunk_strategy`。
- 检索调优优先依赖可观察证据，而不是只凭主观回答印象做判断。

### 嵌入模型：BGE-M3 本地化
- v1.2 起统一切换到 BGE-M3。
- 兼顾 dense、sparse 与 colbert 多模式检索能力。
- 减少云端依赖，便于后续多路检索扩展。

### 多语言与多模态处理
- 推荐先使用 BGE-M3 的中英文混合检索能力。
- 第一阶段优先保证正文提取、结构化切分和元数据稳定。
- 文档解析时可抽取正文、图像 OCR、表格结构化数据，但只有在图表类问题评估中证明有收益时，才继续深化多模态链路。
- 通过页码、章节与相邻文本建立图表关联，提高检索可解释性。

### 向量数据库：Qdrant
- v1.2 直接切换到 Qdrant。
- 原因是其对本地部署和混合检索路线更友好。
- Qdrant 本地部署轻量，适合单机开发环境。

### LangChain 渐进式简化
- v1.0-v1.2 保留 LangChain 以保证迭代效率。
- 优先固定 ingestion、retrieval、rerank、generation 的最小可运行链路。
- v1.3 以后逐步将查询改写、检索、重排、生成拆成独立模块。
- v1.4 再决定是否进一步收缩 LangChain 依赖。

### UI 路线
- v1.0 维持现有 Streamlit 思路。
- v1.1-v1.3 优先补足检索检查视图，而不是先追求前端重构。
- v1.4 若系统稳定，再评估 Chainlit 或 Vue + FastAPI 前后端分离方案。

### Docker 容器化
- 作为 v1.4 或之后的可选项。
- 统一 GPU 运行时、依赖安装、挂载策略与启动入口。
- 目标是提升环境复现与部署一致性。

## 项目架构概览

```text
用户界面
  ├─ Web API / CLI
  ├─ Streamlit（当前思路）
  └─ Chainlit（后续升级）
        ↓
应用层
  ├─ 对话管理
  ├─ 查询预处理 / HyDE
  └─ 错误处理与日志
        ↓
核心服务层
  ├─ 文档解析与 doc-type-aware chunking
  ├─ 混合检索（BM25 + BGE-M3 + 融合排序）
  ├─ 检索检查 / inspection
  ├─ Rerank 精排
  └─ 模型生成（Qwen2-7B / Qwen3-8B）
        ↓
数据存储层
  ├─ Qdrant
  ├─ 本地文档存储
  ├─ source registry
  └─ 会话存储
        ↓
评估监控层
  ├─ Ragas 自动评估
  ├─ LLM-as-a-Judge 主观评估
  ├─ 检索消融实验记录
  └─ 指标可视化与日志分析
```

## 开发任务清单

### 第1周：建立评估框架
- [ ] 创建人工 Gold Set（30-50 题）
- [ ] 创建 `synthetic_dataset.json`（首期 200+ 三元组）
- [ ] 实现 `eval_ragas.py`
- [ ] 实现 `eval_llm_judge.py`
- [ ] 运行 baseline 评估并记录指标
- [ ] 创建评估报告模板

### 第2周：数据层升级
- [ ] 收集 Apollo 中文文档（20篇）
- [ ] 下载经典英文论文（5篇）
- [ ] 完成 `source_registry` 与来源元数据规范
- [ ] 实现 baseline chunking
- [ ] 实现文档类型感知 chunking 策略
- [ ] 为 chunk 增加 provenance metadata（`source_id`、`doc_type`、`page/section`、`chunk_order`、`chunk_strategy`）
- [ ] 视评估需求决定是否补充多模态解析
- [ ] 重新入库并跑评估对比

### 第3周：检索层升级
- [ ] 切换嵌入模型到 BGE-M3 本地
- [ ] 切换到 Qdrant
- [ ] 固定知识库级 embedding 配置
- [ ] 优化 metadata 与 chunking 策略
- [ ] 实现 BM25 / sparse retrieval
- [ ] 实现 hybrid retrieval 与融合参数配置
- [ ] 实现 retrieval inspection（查看召回 chunk、分数、来源、chunk_strategy）
- [ ] 集成 `reranker_service.py`
- [ ] 视评估结果决定是否引入 HyDE
- [ ] 视评估结果决定是否引入层级索引
- [ ] 跑评估对比并记录消融结果

### 第4-5周：模型层升级
- [ ] 基于 error analysis 判断是否进入微调
- [ ] 准备微调数据集
- [ ] 配置 QLoRA 训练环境
- [ ] 训练 Qwen2-7B-QLoRA / Qwen3-8B
- [ ] 集成微调模型到 RAG
- [ ] 跑评估对比

### 第5周后半：可选 DPO 对齐
- [ ] 仅在主线完成且时间充足时再启动
- [ ] 准备偏好对数据集（100-200 对）
- [ ] 配置 DPO 训练
- [ ] 训练模型
- [ ] 集成 DPO 模型到 RAG
- [ ] 跑评估对比

### 第6周：部署优化（可选）
- [ ] 模型量化（llama.cpp INT4）
- [ ] TTFT 优化（threading + KV Cache + 批处理）
- [ ] UI 升级
- [ ] 代码简化重构
- [ ] Docker 容器化
- [ ] 如前序收益稳定，评估 parent-child chunking
- [ ] 性能测试

## 风险与应对

| 风险 | 可能性 | 影响 | 应对策略 | 备注 |
|------|--------|------|----------|------|
| **BGE-M3 显存不足** | 中 | 高 | 使用 FP16 或切 CPU 模式，必要时降级模型 | 4080 需提前压测 |
| **QLoRA / DPO 训练失败** | 中 | 高 | 先小规模试训并监控 loss，保留替代训练方案 | DPO 为加分项 |
| **评估指标无提升** | 高 | 中 | 分模块定位瓶颈，优先保证检索层收益 | 检索收益通常大于微调 |
| **chunking 收益不稳定** | 中 | 中 | 保留 baseline chunking 作为对照，按文档类型逐类验证 | 避免一次改太多变量 |
| **检索链路过早复杂化** | 中 | 中 | 先完成 hybrid retrieval + inspection，再决定是否上 hierarchical index / HyDE | 先抓主收益项 |
| **时间不足（6周紧张）** | 高 | 高 | 先完成 v1.0 → v1.1 → v1.2 核心路径 | v1.2 是最高优先级 |
| **合成数据质量差** | 中 | 中 | 多轮生成、去重、人工抽检 | 生成数据必须审核 |
| **HyDE 效果不佳** | 中 | 低 | 准备 Query Expansion 等备选方案 | 原理理解同样重要 |
| **C++ 优化复杂度高** | 高 | 中 | 先完成基础功能，再逐步做性能优化 | 这是差异化优势 |

## 时间管理策略
- **核心原则**：检索层（v1.2）收益通常大于微调层（v1.3）。
- **必做路径**：先完成 v1.0 评估、v1.1 数据、v1.2 检索。
- **加分路径**：时间允许再做 DPO、性能优化、parent-child chunking 和容器化。
- **最简可行方案**：至少完成 v1.0 + v1.1 + v1.2，并将 v1.3 压缩为基础 QLoRA。
