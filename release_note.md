# LocalRAG Release Notes

## v1.1

**收口提交**：`265aee6`（2026-04-29，`v1.0..v1.1`）

### 版本目标与交付

- 将单体 RAG 升级为可编排的 React Agent，并提供 `rag_search`、`show_sources`、`clarify_question` 三个工具；问答入口切换为 Agent 驱动。
- 重构工程目录与运行时配置，抽象模型供应商，统一 `core/` 下的 RAG、知识库、切分和向量库组件。
- 建立带来源与定位信息的文档切分/入库链路，补齐 Apollo、论文和自动驾驶安全标准语料及 source registry。
- 建立 baseline、chunking comparison、LLM judge 与 formal pipeline 评测基础设施，并固定评测 schema、结果目录合同和测试覆盖。
- 清理历史迁移文档与不应跟踪的实验产物，完成 v1.1.1 版本收口。

### 验证与结论

- v1.1 评测基础设施已就绪：30 题 Gold gate、chunking_eval、judge_eval 与 formal pipeline 均可运行。
- 在当时的 30 题口径下，`doc_type_aware` chunking 的 `source_hit_ratio` 与 baseline 均为 `0.4`，未证明有显著收益；后续工作转入 v1.2 检索层。

### 版本边界

本节只记录 `v1.0` 到 `v1.1` 新增的能力；后续分支在本节基础上追加各自版本报告。
