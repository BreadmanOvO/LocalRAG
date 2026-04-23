# 自动驾驶感知算法 RAG 项目

## 项目简介
这是一个面向自动驾驶感知算法场景的垂直领域 RAG 项目，目标是围绕评估体系、数据工程、检索优化、模型对齐与推理性能，逐步构建具备工程落地价值的专家系统。

## 当前定位
- 项目状态：v1.1 收尾中
- 当前目标版本：v1.2 检索层
- 当前最高优先级：完成 1.1 数据层收口，并开始检索消融实验
- 仓库内容：已包含可运行的评测脚本、chunking 对比链路与真实实验结果

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
- 当前阶段：v1.1 数据层基本完成，正在收口 provenance / locator 合同与状态文档。
- baseline 状态：`eval_ragas.py` / `eval_llm_judge.py` 已具备首版骨架；运行时配置统一从仓库根目录 `key.json` 加载。
- chunking 状态：`eval_chunking.py` 已完成真实对比实验，`results/chunking_eval/gold_set-20260423-115858/` 证明在 `similarity_top_k = 5` 下 baseline 与 `doc_type_aware` 的 evidence source hit 都达到 `1.0`。
- 当前重点：保持 source-level 命中稳定，厘清 locator 级评测边界，并为 v1.2 检索消融建立干净起点。
- 下一步任务：
  1. 扩充 Gold Set 覆盖范围到更稳定的版本闸门规模
  2. 补齐 baseline 真实评测结果与更完整的 Ragas 指标
  3. 启动 hybrid retrieval / reranker 的实验设计
  4. 继续增强 retrieval inspection 的误差分析能力
- 准入原则：只有在 v1.2 检索收益稳定、且 error analysis 证明瓶颈主要在生成层后，才进入 QLoRA
- 优先级提醒：先证明检索层收益，再决定是否进入模型层

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
- [仓库使用说明](docs/repo_guide.md)
- [首页重构设计](docs/superpowers/specs/2026-04-09-readme-homepage-redesign-design.md)
- [首页重构实施计划](docs/superpowers/plans/2026-04-10-readme-homepage-refactor.md)

## 工程/运行入口
- 运行入口、实验脚本、结果目录的详细分类统一维护在 [docs/repo_guide.md](docs/repo_guide.md)。
- 日常开发优先关注主服务、知识库、chunking 与配置相关文件。

## 实验/评测入口
- baseline 评测入口：`eval_ragas.py`
- chunking 对比入口：`eval_chunking.py`
- 详细说明与结果目录约定见 [docs/repo_guide.md](docs/repo_guide.md)

## 成功标准
- 检索效果：目标提升 Top-k 召回与排序质量
- 回答质量：目标提升 faithfulness 与评审胜率
- 系统性能：目标控制端到端延迟与 TTFT
- 领域覆盖：覆盖感知、规划、安全等核心主题

## 仓库说明
当前仓库已经包含主问答服务、知识入库、chunking 对比实验、真实实验结果与版本规划文档。README 的职责是同步当前工程状态，并为后续 v1.2 检索实验提供入口导航。

## 环境依赖
- 主运行依赖见 `requirements.txt`
- 文档清洗专项依赖见 `requirements-source-cleaning.txt`
- 运行评测脚本前需要在仓库根目录提供本地 `key.json`，字段包括 `dashscope_api_key`、`dashscope_base_url`、`chat_model_name`、`embedding_model_name`
- `key.json` 只用于本地运行，不应提交到仓库
- 默认生成模型为 `gpt-5.4`，当前 embedding 使用 DashScope 配置
