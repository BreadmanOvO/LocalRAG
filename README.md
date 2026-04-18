# 自动驾驶感知算法 RAG 项目

## 项目简介
这是一个面向自动驾驶感知算法场景的垂直领域 RAG 项目，目标是围绕评估体系、数据工程、检索优化、模型对齐与推理性能，逐步构建具备工程落地价值的专家系统。

## 当前定位
- 项目状态：规划阶段
- 当前目标版本：v1.0 Baseline
- 当前最高优先级：先建立评估基线，再推进数据与检索升级
- 仓库内容：当前以规划与设计文档为主

## 当前状态总览

| 模块 | 当前状态 | 说明 | 下一步 |
| --- | --- | --- | --- |
| 数据源 | 已规划 | 已明确 Apollo、论文、技术文章等候选来源 | 整理首批核心文档并服务于 Gold Set / Synthetic Set 构建 |
| 切分 | 计划中 | 当前优先关注结构化切分与 metadata 稳定性 | 先落实可评估的 chunking 方案 |
| 检索 | 计划中 | v1.2 主线先做 chunking / metadata、hybrid retrieval、reranker 消融 | HyDE 与层级索引按评估结果决定是否引入 |
| 评估 | 优先准备中 | 已明确 Gold Set + Synthetic Set + 双评估框架 | 先完成基准集与 baseline 指标文件 |
| 模型 | 计划中 | QLoRA 仅在检索收益趋稳且 error analysis 支持时进入 | DPO 作为后续可选加分项 |
| 部署 | 计划中 | 当前无运行入口与部署脚本 | 后续在 v1.4 再推进 |
| 文档 | 进行中 | 已完成首页与分主题文档拆分 | 持续同步路线图与评估口径 |

## 当前阶段与下一步
- 当前阶段：v1.0 Baseline 规划中
- baseline 状态：Gold Set / Synthetic Set / `eval_ragas.py` / `eval_llm_judge.py` 已完成首版骨架与测试覆盖；当前环境下 baseline 运行前还需要提供有效的 `OPENAI_API_KEY`，后续继续扩样本并补充真实 Ragas 指标。
- 本周重点：先建立 Gold Set + Synthetic Set 双数据集，并完成 Ragas + LLM-as-a-Judge baseline 跑通
- 下一步任务：
  1. 创建人工 Gold Set（30-50 题）
  2. 生成 `synthetic_dataset.json`（首期 200+ 三元组）
  3. 实现 `eval_ragas.py`
  4. 实现 `eval_llm_judge.py`
  5. 产出 `results/baseline_metrics.json`
- 准入原则：只有在 v1.2 检索收益稳定、且 error analysis 证明瓶颈主要在生成层后，才进入 QLoRA
- 优先级提醒：整体规划很多，但实际开发阶段要优先保证 v1.2 检索收益

## 开发路线图

| 版本 | 核心目标 | 关键产出 | 状态 |
| --- | --- | --- | --- |
| v1.0 | 建立评估基线 | Gold Set + Synthetic Set + 双评估框架 | 规划中 |
| v1.1 | 升级数据层 | 文档采集、解析、切分、metadata | 计划中 |
| v1.2 | 升级检索层 | hybrid retrieval + reranker + 检索消融 | 计划中 |
| v1.3 | 升级模型层 | 条件式 QLoRA 实验 | 计划中 |
| v1.4 | 优化性能与部署 | Chainlit / 部署整理 / 性能测试 | 计划中 |

## 文档导航
- [详细版本规划](docs/roadmap.md)
- [评估框架与指标](docs/evaluation.md)
- [简历表达与面试亮点](docs/resume_notes.md)
- [参考资料与学习路径](docs/references.md)
- [首页重构设计](docs/superpowers/specs/2026-04-09-readme-homepage-redesign-design.md)
- [首页重构实施计划](docs/superpowers/plans/2026-04-10-readme-homepage-refactor.md)

## 成功标准
- 检索效果：目标提升 Top-k 召回与排序质量
- 回答质量：目标提升 faithfulness 与评审胜率
- 系统性能：目标控制端到端延迟与 TTFT
- 领域覆盖：覆盖感知、规划、安全等核心主题

## 仓库说明
当前仓库以规划文档为主；后续代码、脚本和评估结果会随版本推进逐步补齐。README 会继续从“规划首页”演进为“项目首页”。

## 环境依赖
- 主运行依赖见 `requirements.txt`
- 文档清洗专项依赖见 `requirements-source-cleaning.txt`
- 运行 `eval_ragas.py` 前需要先设置 `OPENAI_API_KEY`
- 默认生成模型为 `gpt-5.4`，当前 embedding 仍使用 DashScope 配置
