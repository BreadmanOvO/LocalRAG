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

## v1.2

**收口提交**：`bc10d14`（2026-05-21，`v1.1..v1.2`）

### 检索与数据能力

- 将嵌入模型收口到本地 `BAAI/bge-m3`，加入 dense + BM25 sparse 的 Hybrid Retrieval（最优融合权重 α=0.5）。
- 增加 `BAAI/bge-reranker-base` Cross-Encoder reranker，并加入 semantic chunking（基于句子嵌入相似度检测断点）。
- 评测语料从 26 篇扩充到 41 篇，评测集从 30 题扩充到 100 题；补齐 MRR、Hit@1、Hit@3、Hit@5 排名指标。
- 增加模型路径配置与下载脚本，统一本地模型目录；补充标准化评测、污染数据清理与 source registry 对齐。

### 验证结果（2026-05-08，100 题，bge-m3 本地，41 篇文档）

| 分块策略 | Reranker | Hit@5 | MRR | Hit@1 | Hit@3 | 命中数 |
| --- | :---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 否 | 0.960 | 0.865 | 0.790 | 0.940 | 96 |
| baseline | 是 | 0.960 | 0.899 | 0.850 | 0.950 | 96 |
| doc_type_aware | 否 | 0.940 | 0.870 | 0.830 | 0.900 | 94 |
| doc_type_aware | 是 | 0.960 | **0.904** | **0.860** | 0.950 | 96 |
| semantic | 否 | **0.970** | 0.864 | 0.800 | 0.920 | **97** |
| semantic | 是 | **0.980** | 0.897 | 0.840 | 0.950 | **98** |

### 结论

`semantic + reranker` 在该评测口径下取得最佳 Hit@5（98/100）和 0.897 MRR；reranker 对排名指标的收益已可观测，v1.2 检索层完成收口。

## v1.3

**收口提交**：`1995dd2`（2026-07-08，`v1.2..v1.3`）

### 检索与评测数据扩充

- 在 v1.2 检索层基础上将语料扩充到 100 篇（10 篇 Apollo、81 篇论文/报告、9 项标准），重建 100 题 eval 集和 203 题 train 集。
- 固定本地 `BAAI/bge-m3`、`sensenova-6.7-flash-lite`、Hybrid Retrieval、`BAAI/bge-reranker-base` 和 semantic chunking 的评测组合。
- 清理污染数据、补齐 source registry 与评测 manifest，并完成 retrieval、hybrid、reranker、judge formal 等可复现实验链路。

### 检索验证结果

在 100 题、100 篇文档口径下：

| 分块策略 | Reranker | Hit@5 | MRR | Hit@1 | Hit@3 | 命中数 |
| --- | :---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 否 | 0.920 | 0.874 | 0.840 | 0.910 | 92 |
| baseline | 是 | 0.930 | 0.889 | 0.860 | 0.920 | 93 |
| doc_type_aware | 否 | 0.930 | 0.870 | 0.830 | 0.920 | 93 |
| doc_type_aware | 是 | **0.940** | 0.892 | 0.850 | **0.940** | **94** |
| semantic | 否 | 0.930 | 0.798 | 0.710 | 0.870 | 93 |
| semantic | 是 | **0.940** | **0.893** | **0.860** | 0.930 | **94** |

端到端结果为 `answered_ratio=1.00`、`context_hit_ratio=1.00`、`evidence_source_hit_ratio=0.97`；hybrid 生成评测的 dense-only source hit 为 0.97，reranker 评测为 0.94；100 条 judge 中 candidate 胜 94、baseline 胜 4、平局 2。

### E1–E9 微调与退出门禁

- E4 完成 SFT/QLoRA 数据与训练链，但 top-k2 硬化门禁因 `gen-eval-004` 的无依据数值/方向推断未通过。
- E5 引入完整上下文/部分上下文 pairwise contrast，修复核心臆测样本；E6/E6.1 针对 Apollo channel 表格 hard case 加固，但单纯追加 SFT 仍未关闭 `gen-eval-007` 合同风险。
- E7 将检索上下文结构化，E8 增加训练退出门禁并停止盲目追加 SFT；E9 修复同源 chunk 补充、partial-context refusal 判定和 locator 数字误报。
- E9 结果：`training_exit_pass=true`、`product_goal_pass=true`、`decision=training_goal_met`；`evidence_source_hit_ratio=1.0`，unsupported claim、answer contract、citation support、required/forbidden term 和 over-refusal 风险均为 `0.0`。

### 版本结论

v1.3 完成检索数据扩充与 E1–E9 微调退出闭环；后续改进转入引用筛选、locator 精度和检索邻接工程，不再以追加 SFT 作为默认手段。
