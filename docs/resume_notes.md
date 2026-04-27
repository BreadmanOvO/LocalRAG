# 简历表达与面试亮点

## 使用方式
本文件整理项目完成后可用于简历与面试表达的内容，不作为当前实现状态说明。

## 项目名称建议
- 基于全链路优化的自动驾驶感知算法专家系统
- 自动驾驶感知算法垂直领域 RAG 系统
- 面向自动驾驶感知场景的专家级问答与检索系统

## 项目描述建议
针对自动驾驶感知算法中专业术语密集、跨模态文档检索难度大、通用模型领域幻觉严重的问题，从零构建垂直领域 RAG 系统，并围绕数据工程、检索优化、模型对齐与推理性能做全链路优化。

## 核心贡献表达

### 1. 已落地的工程化评估体系
- 建立了自动驾驶领域评测数据合同，统一样本的 `evidence`、`metadata` 与 `locator` 字段要求。
- 搭建了 baseline runner、规则式 pairwise judge 与 chunking 对比实验三条评测链路，并统一了结果目录 contract。
- 通过 source-level / locator-level 指标与 error case 汇总，为后续检索实验提供可复用的量化闭环。

### 2. 已落地的数据与检索前置能力
- 建立 `source_registry` 驱动的知识源管理方式，统一 Apollo 文档、标准规范、论文/报告的来源登记。
- 实现 baseline chunking 与 doc-type-aware chunking，并把 `source_id`、`doc_type`、`chunk_strategy`、`locator` 等 provenance metadata 写入 chunk。
- 为后续 retrieval inspection、混合检索与 reranker 消融打下可追溯输入基础。

### 3. 仍应保留“计划”口径的方向
- Ragas 客观指标的完整接入仍在收尾，不应写成已经完成。
- 真实 LLM-as-a-Judge 判分逻辑仍未接入，不应写成已有稳定胜率结论。
- hybrid retrieval、HyDE、BGE-M3、Rerank、QLoRA、DPO、llama.cpp 性能优化都属于后续路线，不应提前写成既成事实。

## 面试亮点准备
1. 为什么检索层收益往往大于微调层收益？
2. HyDE 解决了什么问题，适合什么场景？
3. BGE-M3 的 dense / sparse / colbert 多模式能力如何用于混合检索？
4. DPO 与 RLHF 的差异是什么？
5. TTFT 受哪些因素影响，如何从工程层优化？
6. 如何把自动驾驶领域知识与通用大模型能力结合，减少幻觉？

## 表达规则
- 未完成的数据、指标和效果必须保留“目标”“计划”或“预期”口径。
- 只有真实落地后的结果，才能改写成既成事实。
- 简历表达应优先突出“解决了什么问题”，而不是简单罗列“用了什么技术”。
- 面试时要把评估闭环、检索收益、性能优化与领域理解串成完整故事线。
