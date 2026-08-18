# LocalRAG 发布记录

记录各版本已合并的功能、验证结果和已知限制。指标保留对应的评测口径。

## v1.1

2026-04-29 · `265aee6` · `v1.0..v1.1`

### 变更

- 将单体 RAG 升级为可编排的 React Agent，并提供 `rag_search`、`show_sources`、`clarify_question` 三个工具；问答入口切换为 Agent 驱动。
- 重构工程目录与运行时配置，抽象模型供应商，统一 `core/` 下的 RAG、知识库、切分和向量库组件。
- 建立带来源与定位信息的文档切分/入库链路，补齐 Apollo、论文和自动驾驶安全标准语料及 source registry。
- 建立 baseline、chunking comparison、LLM judge 与 formal pipeline 评测基础设施，并固定评测 schema、结果目录合同和测试覆盖。
- 清理历史迁移文档与不应跟踪的实验产物，形成 v1.1.1 发布内容。

### 验证

- v1.1 评测基础设施已就绪：30 题 Gold gate、chunking_eval、judge_eval 与 formal pipeline 均可运行。
- 在当时的 30 题口径下，`doc_type_aware` chunking 的 `source_hit_ratio` 与 baseline 均为 `0.4`，未证明有显著收益；后续工作转入 v1.2 检索层。

## v1.2

2026-05-21 · `bc10d14` · `v1.1..v1.2`

### 变更

- 固定嵌入模型为本地 `BAAI/bge-m3`，加入 dense + BM25 sparse 的 Hybrid Retrieval（最优融合权重 α=0.5）。
- 增加 `BAAI/bge-reranker-base` Cross-Encoder reranker，并加入 semantic chunking（基于句子嵌入相似度检测断点）。
- 评测语料从 26 篇扩充到 41 篇，评测集从 30 题扩充到 100 题；补齐 MRR、Hit@1、Hit@3、Hit@5 排名指标。
- 增加模型路径配置与下载脚本，统一本地模型目录；补充标准化评测、污染数据清理与 source registry 对齐。

### 验证（2026-05-08，100 题，bge-m3 本地，41 篇文档）

| 分块策略 | Reranker | Hit@5 | MRR | Hit@1 | Hit@3 | 命中数 |
| --- | :---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 否 | 0.960 | 0.865 | 0.790 | 0.940 | 96 |
| baseline | 是 | 0.960 | 0.899 | 0.850 | 0.950 | 96 |
| doc_type_aware | 否 | 0.940 | 0.870 | 0.830 | 0.900 | 94 |
| doc_type_aware | 是 | 0.960 | **0.904** | **0.860** | 0.950 | 96 |
| semantic | 否 | **0.970** | 0.864 | 0.800 | 0.920 | **97** |
| semantic | 是 | **0.980** | 0.897 | 0.840 | 0.950 | **98** |

### 结果

`semantic + reranker` 在该评测口径下取得最佳 Hit@5（98/100）和 0.897 MRR。Reranker 对排名指标有提升，v1.2 的检索实现确定为该组合。

## v1.3

2026-07-08 · `1995dd2` · `v1.2..v1.3`

### 变更

- 在 v1.2 检索层基础上将语料扩充到 100 篇（10 篇 Apollo、81 篇论文/报告、9 项标准），重建 100 题 eval 集和 203 题 train 集。
- 固定本地 `BAAI/bge-m3`、`sensenova-6.7-flash-lite`、Hybrid Retrieval、`BAAI/bge-reranker-base` 和 semantic chunking 的评测组合。
- 清理污染数据、补齐 source registry 与评测 manifest，并完成 retrieval、hybrid、reranker、judge formal 等可复现实验链路。

### 检索验证

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

### E1–E9 微调与退出检查

- E4 完成 SFT/QLoRA 数据与训练链，但 top-k2 硬化检查因 `gen-eval-004` 的无依据数值/方向推断未通过。
- E5 引入完整上下文/部分上下文 pairwise contrast，修复核心臆测样本；E6/E6.1 针对 Apollo channel 表格 hard case 加固，但单纯追加 SFT 仍未关闭 `gen-eval-007` 合同风险。
- E7 将检索上下文结构化，E8 增加训练退出检查并停止追加 SFT；E9 修复同源 chunk 补充、partial-context refusal 判定和 locator 数字误报。
- E9 结果：`training_exit_pass=true`、`product_goal_pass=true`、`decision=training_goal_met`；`evidence_source_hit_ratio=1.0`，unsupported claim、answer contract、citation support、required/forbidden term 和 over-refusal 风险均为 `0.0`。

### 结果

v1.3 完成检索数据扩充与 E1–E9 微调退出检查；后续改进转入引用筛选、locator 精度和检索邻接工程，不再以追加 SFT 作为默认手段。

## v1.4

2026-07-22 · `2988e27` · `v1.3..v1.4`

### 变更

- 增加 Agent 会话隔离、短期会话记忆和持久化任务记忆，避免跨会话串扰并支持任务状态复用。
- 增加研究型证据工具、来源检索与 finding 结构，统一研究任务的证据绑定、运行轨迹和可观察状态。
- 增加 active corpus/profile 配置，固定来源数、片段数、代码身份与评测参数；UI 展示运行身份、Gate 状态和失败原因。
- 建立 Agent 正式评测与发布稳定性门禁，收紧工具预算、递归保护、终止状态和评测产物合同；完成代码精简并发布 v1.4.2。

### 验证

- P0 稳定性加固 Gate、P1 代码精简 Gate 和 v1.4.2 release Gate 均通过。
- 每个 Gate 选取 3 轮正式运行，所有轮次 `case_pass_ratio=1.0`、产物有效、评测完整、代码 revision clean、身份一致且无图递归；v1.4.2 的三轮运行均无基础设施错误。

### 结果

v1.4 增加了会话记忆、研究证据、运行状态和重复验证能力。

## v1.5

2026-07-25 · `eea34da` · `v1.4..v1.5`

### 变更

- 增加执行预算、循环终止守卫和跨轮状态隔离，明确单轮/跨轮运行的终止与资源边界。
- 建立 `agent/research/` 研究运行域：状态模型、schema、持久化 store、校验、运行时编排、控制器和 UI presentation。
- 支持研究任务的认领、暂停/恢复、取消与断点续跑；在问答 UI 中展示运行状态、控制入口和证据关系。
- 增加 A4/A5 控制探针与发布评测契约，覆盖可恢复执行、finding-evidence 绑定、终止分类、禁止工具调用和控制状态一致性。

### 验证

`results/agent_eval/v1.5-a5-release-gate.json` 使用 `agent-stability-gate-v2.1` 契约，连续 3 轮正式运行、每轮 15 个 case，结果如下：

- 每轮 `case_pass_ratio=1.0`，评测产物有效、评测完整、revision clean、身份一致。
- `duplicate_tool_violation_count=0`、`unclassified_termination_count=0`、`no_forbidden_tool_violations=true`。
- `verified_finding_evidence_binding_ratio=1.0`、`checkpoint_resume_pass_ratio=1.0`，控制探针覆盖完整。

### 结果

v1.5 将研究 Agent 运行单元化：任务可以暂停、恢复和续跑，状态与证据绑定可在 Gate 中复现。

## v1.6

2026-08-05 · `884c097` · `v1.5..v1.6`

### 变更概览

v1.6 增加本地模型服务与长会话支持：本地模型可以被 Agent 调用，长会话会按预算压缩。本版本不重新启动 SFT；v1.3 的 E9 退出检查已确认微调目标，后续质量问题转入检索、证据和运行时工程。

### 已交付能力

- 固定 Qwen3-4B + E6.1 LoRA 的模型身份、输入 manifest 和 SHA-256 校验。
- 完成 adapter BF16、merged BF16、GGUF F16、GGUF `Q4_K_M` 四类部署 profile。
- 支持 Windows 原生 Transformers 与 llama.cpp 部署链路。
- 增加本地模型 HTTP 服务、OpenAI-compatible API、请求队列和服务指标。
- 增加 gateway 重试、fallback、熔断和 half-open 恢复机制，并将本地模型路由状态暴露到 UI。
- 增加会话摘要、上下文预算、持久化摘要版本和恢复后的继续压缩；保留完整会话与工具消息边界，避免压缩破坏研究证据链。
- 长会话评测中的上下文 Token 中位数降低 73.5%。

### 验证

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

### 下一步

v1.7 优先恢复活动语料库，并验收“提问 → 检索 → 研究步骤 → 证据 → finding → 会话压缩 → 会话恢复”完整链路；随后补统一部署启动、停止、状态检查和真实云 fallback 验证。

## v1.7

2026-08-10

### 检索主链路

- 在线默认检索统一为 Dense Top20 + BM25 Top20 → RRF → Cross-Encoder → Top5；BM25/RRF 失败降级到 Dense + Reranker，Reranker 失败降级到 Dense-only。
- 拆出独立 `BM25Retriever` 和 `RetrievalPipeline`，保留历史加权 `HybridRetriever` 作为学习/消融资产，避免加权融合与 RRF 重复串联。
- 中文 BM25 使用英文 token + 中文字符 bigram，解决自然中文问句大量 `bm25_empty` 的问题。
- provenance/trace 支持 Dense、BM25、RRF、Rerank 四级排名、retrieval stage、降级原因、route 与 final/candidate/context count。

### Agent 工具与模型

- 工具统一安全错误码和 schema validation 输出；内部异常不进入 ToolMessage。
- `rag_search` 核心结果与 session/task memory 副作用隔离，记忆失败只记录 `memory_errors`，不丢弃已生成回答。
- 移除 SenseNova 不安全的 `verify=False`；local gateway 初始化状态区分未配置、配置禁用、已构造和不健康。
- 新增 provider 功能 smoke，真实 SenseNova 普通请求、强制 tool-call 和 stream 均通过；线上模型未执行质量评测。

### 验证

- 在 100 题、100-source/7339-chunk 活动语料上，默认 retrieval pipeline 的 Hit@1=0.85、Hit@3=0.97、Hit@5=0.97、MRR=0.9067；100/100 使用 `rrf_rerank`，无 fallback。
- 真实 Agent trace 跑通 planner → `rag_search` → 四级检索排名 → provider generation route → task memory write → final answer。
- 自动化测试通过；详细证据见 `RAG_md/docs/reports/v1.7-agentic-rag-closure.md`。

### 版本边界

v1.7 暂不包含第二套显式 Graph、异步 Tool Queue、三层 Memory、Redis/Kafka/ES 或多 Agent。是否增加这些组件取决于实际容量和并发需求。
