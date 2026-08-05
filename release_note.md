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

## v1.4

**收口提交**：`2988e27`（2026-07-22，`v1.3..v1.4`）

### Agent 与研究能力

- 增加 Agent 会话隔离、短期会话记忆和持久化任务记忆，避免跨会话串扰并支持任务状态复用。
- 增加研究型证据工具、来源检索与 finding 结构，统一研究任务的证据绑定、运行轨迹和可观察状态。
- 增加 active corpus/profile 配置，固定来源数、片段数、代码身份与评测参数；UI 展示运行身份、Gate 状态和失败原因。
- 建立 Agent 正式评测与发布稳定性门禁，收紧工具预算、递归保护、终止状态和评测产物合同；完成代码精简与 v1.4.2 发布收口。

### 验证结果

- P0 稳定性加固 Gate、P1 代码精简 Gate 和 v1.4.2 release Gate 均通过。
- 每个 Gate 选取 3 轮正式运行，所有轮次 `case_pass_ratio=1.0`、产物有效、评测完整、代码 revision clean、身份一致且无图递归；v1.4.2 的三轮运行均无基础设施错误。

### 版本结论

v1.4 将 Agent 从“能运行”推进到具备记忆、研究证据、运行可观察性和可重复发布门禁的研究助手形态。

## v1.5

**收口提交**：`eea34da`（2026-07-25，`v1.4..v1.5`）

### 可控研究 Agent

- 增加执行预算、循环终止守卫和跨轮状态隔离，明确单轮/跨轮运行的终止与资源边界。
- 建立 `agent/research/` 研究运行域：状态模型、schema、持久化 store、校验、运行时编排、控制器和 UI presentation。
- 支持研究任务的认领、暂停/恢复、取消与断点续跑；在问答 UI 中展示运行状态、控制入口和证据关系。
- 增加 A4/A5 控制探针与发布评测契约，覆盖可恢复执行、finding-evidence 绑定、终止分类、禁止工具调用和控制状态一致性。

### 验证结果

`results/agent_eval/v1.5-a5-release-gate.json` 使用 `agent-stability-gate-v2.1` 契约，连续 3 轮正式运行、每轮 15 个 case，结果如下：

- 每轮 `case_pass_ratio=1.0`，评测产物有效、评测完整、revision clean、身份一致。
- `duplicate_tool_violation_count=0`、`unclassified_termination_count=0`、`no_forbidden_tool_violations=true`。
- `verified_finding_evidence_binding_ratio=1.0`、`checkpoint_resume_pass_ratio=1.0`，控制探针覆盖完整。

### 版本结论

v1.5 将研究 Agent 收口为可控、可恢复、可验证的运行单元；研究任务状态与证据链可以在 Gate 中稳定复现。

## v1.6

**收口提交**：`884c097`（2026-08-05，`v1.5..v1.6`）

### 发布结论

v1.6 完成本地模型服务与长会话运行能力建设：本地模型可以被 Agent 稳定调用，长会话不会无限膨胀。本版本不重新启动 SFT；v1.3 的 E9 退出门禁已确认微调目标闭环，后续质量问题进入检索、证据和运行时工程治理。

### 已交付能力

- 固定 Qwen3-4B + E6.1 LoRA 的模型身份、输入 manifest 和 SHA-256 校验。
- 完成 adapter BF16、merged BF16、GGUF F16、GGUF `Q4_K_M` 四类部署 profile。
- 支持 Windows 原生 Transformers 与 llama.cpp 部署链路。
- 增加本地模型 HTTP 服务、OpenAI-compatible API、请求队列和服务指标。
- 增加 gateway 重试、fallback、熔断和 half-open 恢复机制，并将本地模型路由状态暴露到 UI。
- 增加会话摘要、上下文预算、持久化摘要版本和恢复后的继续压缩；保留完整会话与工具消息边界，避免压缩破坏研究证据链。

### 验证结果

正式部署 manifest：`model_deployment/manifests/v1_6_model_serving_release.json`

- 模型服务质量 gate、服务性能 benchmark gate 和 Task 8 端到端验证均通过。
- 健康检查、就绪检查和模型列表接口均返回 `200`；鉴权 `401`、缺少 purpose、错误模型、超出 token 限制等 `400` 场景已覆盖。
- 非流式生成和 SSE 流式生成均通过。
- Task 9 长上下文探针：首轮压缩和恢复后的第二轮压缩均通过，摘要 revision 从 `1` 递增到 `2`，`probe_pass=true`，transcript 与 covered message identity 无重复或越界，第二轮压缩后模型视图低于目标预算。
- Task 8 已验证桌面 `1440x900` 与移动端 `390x844`：无水平溢出、会话压缩和模型路由面板可见，展开面板不会遮挡消息输入框。

### 已知限制

- Task 8 未配置云端凭据，真实云 fallback 尚未完成外部 provider 验证。
- 本机活动 Chroma `rag` collection 当前不可用，研究 Agent 的真实 RAG 执行链路需在 v1.7 恢复后再验收。
- vLLM 保留为后续 WSL2 扩展，不作为 v1.6 发布阻塞项。
- 原始截图、日志、预测全文和 SQLite 运行数据库不进入 Git；发布记录只保留去敏摘要和 manifest。

### 下一版本入口

v1.7 优先恢复活动语料库，并验收“提问 → 检索 → 研究步骤 → 证据 → finding → 会话压缩 → 会话恢复”完整链路；随后补统一部署启动、停止、状态检查和真实云 fallback 验证。

## v1.7

**维护提交**：`main` 当前分支（2026-08-05）

### 发布结构维护

- 删除历史 `TODO.md`，避免已经完成或过期的计划继续作为当前版本入口。
- 将应用依赖与本地模型服务依赖合并到根目录唯一的 `requirements.txt`，并检查依赖项无重复。
- 更新 README，使项目结构、本地模型服务、长会话评测、依赖入口和版本状态与当前代码一致。
- 本节仅记录仓库维护变更，不宣称新增模型或 Agent 行为；功能能力继续以 v1.6 验证结果为准。
