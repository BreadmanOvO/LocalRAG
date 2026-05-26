# LocalRAG 项目面试复盘文档

## 1. 项目一句话介绍

LocalRAG 是一个面向自动驾驶感知算法场景的垂直领域 RAG 系统。项目不只是完成了一个基于向量库的问答 Demo，而是围绕知识源治理、文档清洗、分块策略、混合检索、重排、Agent 工具调用和多层评测体系，构建了一条可复现、可度量、可迭代的 RAG 工程闭环。

面试中可以这样概括：

> 我做的是自动驾驶感知算法方向的垂直 RAG。核心目标不是简单接入 LangChain 和向量库，而是从数据治理开始，把 source registry、chunk provenance、dense + BM25 hybrid retrieval、cross-encoder reranker、RAGAS 和 LLM Judge 都纳入评测闭环。项目最大的特点是评估先行，每一轮优化都能用 Hit@k、MRR、RAGAS 和 Judge 结果解释收益。

## 2. 项目已完成内容

### 2.1 应用能力

- Streamlit 问答入口：`app_qa.py`
- Streamlit 文档上传入口：`app_file_uploader.py`
- ReAct Agent：`agent/react_agent.py`
- Agent 三工具：
  - `rag_search`：检索知识库并生成回答
  - `show_sources`：展示最近一次检索来源
  - `clarify_question`：问题模糊时生成澄清追问
- 对话历史管理：`core/chat_history.py`
- 运行时模型配置：`config/runtime_keys.py`
- 多 provider 适配：`bailian`、`modelscope`、`sensenova`、`local_embedding`、`local_sentence_transformer`

### 2.2 知识库能力

- 使用 ChromaDB 作为本地向量库
- 支持文档上传、MD5 去重、chunk 入库
- 支持 `source_id`、`doc_type`、`locator`、`chunk_strategy`、`chunk_order` 等 provenance metadata
- 当前 registry 口径覆盖 100 份 raw PDF：
  - Apollo 官方文档：10 篇
  - 标准规范：9 篇
  - 论文/报告：81 篇
- 当前评测数据：
  - eval set：100 题
  - train set：203 题

需要注意：`RAG_md` 的 archive 中保留了 41 篇文档阶段的 v1.2 历史结果，而主仓库 README/docs 和 `RAG_md` 主文档已更新到 100 篇文档后的最新口径。面试时应区分“历史快照”“当前评测口径”和“来源池全集”。

### 2.3 分块策略

项目实现了三种分块策略：

1. baseline chunking
   - 使用 `RecursiveCharacterTextSplitter`
   - 默认 `chunk_size=500`，`chunk_overlap=50`

2. doc_type_aware chunking
   - 按文档类型设置不同 chunk 参数
   - `official_doc`：500/50
   - `standard`：900/100
   - `paper`、`report`：700/80
   - 识别不同文档的结构边界：Apollo/标准文档的 `[p.N]` 或 `- [p.N]` 页码标记，论文/报告的 `### Page N` 标题
   - 保留页码和章节路径，生成 `locator`
   - 需要诚实说明：早期实现更偏“参数分档”，只有官方文档较充分利用标题/页码结构；这确实不够理想。当前实现已补强为结构感知，但需要重建 store 后重新评测，不能把旧指标直接当作新实现收益。

3. semantic chunking
   - 先按句子切分
   - 用 BGE-M3 编码句子
   - 计算相邻句子余弦相似度
   - 相似度低于阈值 0.5 时断开
   - 超长 chunk 再做二次拆分

### 2.4 检索与重排能力

- Dense retrieval：BGE-M3 embedding + ChromaDB
- Sparse retrieval：BM25Okapi
- Hybrid retrieval：
  - dense 和 sparse 各自召回 top-k
  - 对分数归一化
  - 使用 `final_score = alpha * dense_score + (1-alpha) * sparse_score`
  - 实验中常用 `alpha=0.5`
- Reranker：
  - 推荐方案：BAAI/bge-reranker-base cross-encoder
  - fallback：LLM reranker
  - 典型流程：hybrid top-20 -> cross-encoder rerank -> final top-5

### 2.5 评测体系

项目采用多层评测：

- baseline eval：生成回答、记录检索上下文、计算基础指标
- chunking eval：比较 baseline、doc_type_aware、semantic
- retrieval-only eval：只评估检索，不经过 LLM
- hybrid eval：比较 dense-only、sparse-only、hybrid
- reranker eval：比较 hybrid-only 和 hybrid + reranker
- RAGAS eval：评估 faithfulness、answer_relevancy、context_precision、context_recall
- LLM Judge：pairwise 比较 baseline 和 candidate
- formal judge run：编排端到端验收流程

每次实验都落盘：

- `predictions.json`
- `metrics.json`
- `manifest.json`

这样可以保留数据集、模型、provider、store、run_id 等复现实验信息。

### 2.6 当前口径与历史口径对照

面试时最容易被追问的是“你到底以哪个版本作为项目最终成果”。建议统一按下面口径说明：

| 口径 | 文档规模 | 评测规模 | 主要用途 | 面试说法 |
| --- | ---: | ---: | --- | --- |
| v1.2 历史快照 | 41 篇 | 30 题 | 验证 hybrid/reranker 思路 | 小规模阶段 reranker 最高 source_hit 0.967，说明路线有效 |
| v1.3 最新口径 | 100 篇 | 100 题 | 当前主成果 | 最新最优 Hit@5 约 0.94，MRR 约 0.893 |
| train set | 100 篇来源池 | 203 题 | 后续训练/调参候选 | 用于 hard negatives、reranker 微调或 QLoRA 数据准备 |

如果面试官问“为什么以前 0.98、现在 0.94”，不要解释成退步，而要说明：文档池从 41 扩到 100 后，负样本更多、相似来源更多、问题覆盖更广，所以指标更接近真实难度。小规模高分证明方法有效，大规模结果证明系统更稳健。

## 3. 技术架构

### 3.1 数据入库链路

```text
raw PDF / Markdown
  -> processing/source_cleaning.py
  -> 去页眉页脚 / OCR fallback / evidence-ready excerpts
  -> source_registry.json
  -> KnowledgeBaseService.ingest_document()
  -> chunking strategy
  -> embedding
  -> ChromaDB
```

### 3.2 在线问答链路

```text
用户问题
  -> Streamlit app_qa.py
  -> ReactAgent
  -> rag_search 工具
  -> RagService.answer_with_retrieval()
  -> retriever 召回 top-k 文档
  -> prompt 注入 context/source_id/locator
  -> LLM 生成回答
  -> show_sources 可展示来源
```

### 3.3 检索实验链路

```text
query
  -> BGE-M3 dense retrieval
  -> BM25 sparse retrieval
  -> score normalization
  -> alpha fusion
  -> optional cross-encoder reranker
  -> top-5 contexts
  -> Hit@k / MRR / RAGAS / Judge
```

### 3.4 核心模块职责

| 模块 | 职责 | 面试中可强调的点 |
| --- | --- | --- |
| `core/knowledge_base.py` | 文档入库、embedding、Chroma 写入 | 把 chunk、metadata、source_id 统一管理 |
| `core/chunking.py` | baseline/doc_type_aware/semantic 分块 | 分块不是纯文本切割，而是保留页码、章节、locator |
| `core/retriever.py` | dense 检索与召回封装 | 与上层生成解耦，方便替换检索策略 |
| `core/rag_service.py` | 检索增强生成主流程 | 负责把上下文、来源、prompt 和 LLM 串起来 |
| `agent/react_agent.py` | ReAct 工具调用 | 让问答、来源展示、澄清追问成为可组合工具 |
| `scripts/eval_*.py` | 评测 runner | 统一生成 predictions/metrics/manifest |
| `processing/source_cleaning.py` | PDF 清洗和证据片段准备 | 解决页眉页脚、OCR、标准文档噪声等数据问题 |

架构答题可以用一句话收束：数据层保证“文档可信且可追溯”，检索层保证“相关证据能被找出来”，生成层保证“回答受上下文约束”，评测层保证“每轮优化有证据”。

## 4. 版本迭代规划与成果

### 4.1 v1.0：评估基线

目标：先建立可复现的评测框架，而不是直接堆优化技巧。

完成内容：

- 创建 Gold Set 和 Synthetic Set
- 实现数据 schema 校验
- 建立 baseline runner
- 建立 LLM Judge 骨架
- 定义 `manifest/predictions/metrics` artifact contract
- 使用 local-hash embedding 作为占位

结果：

- answered_ratio = 1.0
- context_hit_ratio = 0
- evidence_source_hit_ratio = 0

解释：

v1.0 检索指标为 0 并不是失败，因为当时使用的是 MD5 hash 伪嵌入。这个版本的价值是把评测框架和实验合同搭起来，让后续优化有可比较的基线。

### 4.2 v1.1：数据层升级

目标：把知识源、文档清洗、chunk 规则和评测契约固定下来。

完成内容：

- source registry
- PDF 清洗与 Markdown 重建
- baseline chunking
- doc_type_aware chunking
- provenance metadata
- formal judge pipeline
- ReAct Agent 三工具架构

代表结果：

- baseline source_hit：0.233
- doc_type_aware source_hit：0.367
- official_doc 类从 0.300 提升到 0.550

面试解释：

doc_type_aware 在总分上提升有限，但按文档类型拆开看，官方文档类提升明显。标准和论文类效果差，主要是样本量小、结构复杂、证据位置分散。更重要的是，早期 doc_type_aware 主要是不同 `chunk_size/overlap` 的参数分档，这不是充分的“文档类型感知”。真正合理的做法应该利用文档结构：官方文档和标准看页码/章节，论文看 page heading、abstract、section，报告看标题层级。当前实现已补强为结构边界感知，但需要重新建库和评测来验证收益。

### 4.3 v1.2：检索层升级

目标：在同一评测集上逐步优化检索链路，每次只改一个关键变量。

完成内容：

- LocalHash -> Qwen3 Embedding -> 本地 BGE-M3
- BM25 sparse retrieval
- dense + sparse hybrid retrieval
- retrieval inspection
- BAAI/bge-reranker-base cross-encoder reranker
- semantic chunking
- 新增 Hit@1、Hit@3、Hit@5、MRR

30 题代表结果：

| 配置 | source_hit |
| --- | ---: |
| dense-only | 0.233 |
| sparse-only | 0.667 |
| hybrid, alpha=0.5 | 0.733 |
| hybrid + reranker, baseline store | 0.933 |
| hybrid + reranker, doc_type_aware store | 0.967 |

关键结论：

- 自动驾驶领域有大量精确术语，BM25 对术语匹配非常有效
- dense 和 sparse 互补，hybrid 比单路检索更稳
- reranker 的核心价值是精排，不一定显著提高 source_hit，但会改善排序质量

### 4.4 v1.3 / 最新口径：数据扩充与评测增强

完成内容：

- 文档扩充到 100 篇 raw PDF
- eval set 重建为 100 题
- train set 扩充到 203 题
- 统一使用本地 BGE-M3 embedding
- 生成/judge 使用 SenseNova
- 引入更完整的 RAGAS 标准评测

最新 100 文档口径代表结果：

| 配置 | Hit@5 | MRR | Hit@1 | Hit@3 |
| --- | ---: | ---: | ---: | ---: |
| baseline + reranker | 0.930 | 0.889 | 0.860 | 0.920 |
| doc_type_aware + reranker | 0.940 | 0.892 | 0.850 | 0.940 |
| semantic + reranker | 0.940 | 0.893 | 0.860 | 0.930 |

端到端 chunking source_hit：

- baseline：0.97
- doc_type_aware：0.95
- semantic：0.97

RAGAS 对比：

| 配置 | faithfulness | answer_relevancy | context_precision | context_recall |
| --- | ---: | ---: | ---: | ---: |
| dense-only | 0.2419 | 0.7105 | 0.0558 | 0.0372 |
| hybrid-only | 0.9361 | 0.9083 | 0.6955 | 0.8267 |
| hybrid + reranker | 0.9318 | 0.9264 | 0.8474 | 0.9366 |

LLM Judge：

- candidate win：94
- baseline win：4
- tie：2

### 4.5 指标口径解读

不同指标回答的是不同问题，面试中不要把它们混在一起：

| 指标 | 回答的问题 | 适合判断什么 |
| --- | --- | --- |
| Hit@1 | 第 1 个结果是不是正确 source | 首位排序质量 |
| Hit@3 / Hit@5 | top-k 里有没有正确 source | 召回是否足够 |
| MRR | 正确 source 排得靠不靠前 | reranker 和排序策略收益 |
| source_hit | 是否找到了正确来源文档 | 粗粒度检索能力 |
| locator_hit | 是否找到了正确页码/章节/片段 | 细粒度证据定位能力 |
| faithfulness | 回答是否被上下文支持 | 幻觉控制 |
| context_precision | 相关上下文是否排在前面 | top-k 噪声控制 |
| context_recall | 标准答案需要的信息是否被覆盖 | 上下文覆盖率 |

因此，项目里有几类常见现象都可以解释清楚：

- Hit@5 高但 MRR 一般：说明正确文档能进 top-5，但排序还不够靠前，适合上 reranker。
- source_hit 高但 locator_hit 低：说明找到了文档，但 chunk 粒度、页码解析或章节路径还需要优化。
- faithfulness 高但 answer_relevancy 一般：说明回答基本不胡编，但可能没有完全答到问题重点。
- context_precision 低而 context_recall 高：说明相关信息被找到了，但 top-k 里混入噪声，需要重排或过滤。
- dense-only RAGAS 很低而 hybrid/reranker 很高：说明该领域精确术语和结构化来源对检索质量影响很大。

## 5. 项目亮点

### 5.1 评估先行

项目第一步不是上复杂检索，而是先建立 Gold Set、schema、baseline runner 和指标体系。这样每次优化都能回答“是否真的变好”。

### 5.2 数据治理完整

每个知识源都有 registry，chunk 带 `source_id/doc_type/locator/chunk_strategy/chunk_order`。这让回答可以追溯，也让错误分析能落到具体来源和具体切分策略。

### 5.3 检索优化有消融实验

不是直接宣称 hybrid 或 reranker 更好，而是分别对 dense-only、sparse-only、hybrid、hybrid + reranker 做对照。

### 5.4 指标选择有方法论

当 Hit@5 接近天花板时，只看 source_hit 看不出 reranker 的价值。项目引入 Hit@1、Hit@3、MRR 后，才能看到 reranker 对排序质量的贡献。

### 5.5 RAGAS + LLM Judge 双轨评测

自建指标适合快速迭代，RAGAS 适合解释上下文质量和回答忠实度，LLM Judge 适合做版本间 pairwise 验收。三者互补。

## 6. 踩坑经验

### 6.1 LocalHash 指标不可代表真实检索

早期 local-hash embedding 只是占位，可能出现虚高或完全无语义的结果。真正检索效果必须切换到语义 embedding 后重新评估。

### 6.2 ModelScope API 限流

使用 Qwen3 Embedding API 时遇到 429 限流。这里要特别注意控制变量：不能在同一次评测 run 中前半段用 API embedding/模型、后半段切到本地 BGE-M3 或其他模型继续跑，否则生成结果和检索结果会混用不同模型，指标没有参考意义。正确处理是当前 run 内只做退避重试；如果限流无法恢复，就中止或记录失败样本。后续切换到本地 BGE-M3 必须作为新的独立实验：重新建库、重新评测，并在 manifest 中记录新的 provider、chat_model_name、embedding_model_name。

### 6.3 换 embedding 必须重建 store

embedding 维度和语义空间变化后，旧向量库不能复用。否则评测结果没有意义。

### 6.4 默认 Chroma store 容易误用

评测脚本必须显式传入 `--store-dir`，避免跑到默认 `./chroma_db`，导致实验不可复现。

### 6.5 Hit@5 天花板会掩盖优化收益

100 题上 Hit@5 已经较高，reranker 的价值更多体现在 Hit@1、MRR、context_precision 和 context_recall。

### 6.6 RAGAS 对标准/表格类文档不稳定

标准文档、表格、bullet-heavy 上下文容易引发超时或 NaN，需要分批评测、增量保存和人工解释异常。

### 6.7 locator 命中仍是技术债

当前 source 级召回较强，但 locator 级命中仍未完全打通。说明系统能找到正确文档，但对“页码/章节/证据片段”的细粒度对齐仍需优化。

### 6.8 doc_type_aware 早期设计偏浅

早期 doc_type_aware 主要做了不同文档类型的 `chunk_size/overlap` 参数分档，这只能算弱版本的文档类型感知。它解释了为什么 official_doc 有收益，但 standard/paper 不稳定。后续已补强为结构感知：标准文档识别 `[p.N]` / `- [p.N]` 页码标记，论文识别 `### Page N` 页面标题，并继续生成 page/section locator。这个改动更符合“按文档结构切分”的初衷。

## 7. 失败模式与项目反思

### 7.1 主要瓶颈在检索侧

误差分析显示，失败样本更多来自：

- 概述性文档被具体模块文档挤出 top-5
- 正确 source 被召回，但关键 chunk 没排进 top-5
- 标准文档正文解析不完整
- chunk 粒度不适合精确参数类问题

### 7.2 生成侧问题相对较少

RAGAS faithfulness 均值已接近 0.93，说明多数回答能被上下文支持。生成侧主要问题是 LLM 偶尔会补充上下文没有的额外 claim。

### 7.3 为什么不优先做 QLoRA

如果主要错误来自检索不到正确上下文，微调生成模型无法根治。QLoRA 可以作为展示模型训练能力的加分项，但不是当前收益最高的主线。更优先的方向是修复数据清洗、locator、chunk 粒度和 reranker/hybrid 策略。

### 7.4 失败样本归因

可以把失败样本按“责任层”拆开讲，这样比简单说“模型不准”更专业：

| 失败类型 | 典型表现 | 主要责任层 | 优化方向 |
| --- | --- | --- | --- |
| A. 正确文档没进 top-k | 概述性文档被具体模块文档挤掉 | 检索召回 | RRF、query expansion、领域同义词、召回 top-k 扩大 |
| B. 正确 source 进了但 chunk 不对 | 文档命中但关键证据没出现 | 分块/排序 | parent-child chunk、locator-aware rerank、结构化 chunk |
| C. LLM 使用参数化知识 | 上下文不足时补充常识 | 生成约束 | stricter prompt、引用约束、无法回答策略 |
| D. 过度推断或幻觉 | 回答包含上下文没有的 claim | 生成/评测 | faithfulness gate、Judge 回归、答案后处理 |
| E. 评测边界问题 | RAGAS 超时、NaN、标准答案过窄 | 评测数据 | 分批评测、异常样本标注、人工复核 |

当前经验是：主要瓶颈不在“LLM 不会写答案”，而在“证据是否准确进入上下文、是否排在靠前位置”。这也是为什么项目优先做 hybrid、reranker、chunking 和数据清洗，而不是直接上 QLoRA。

## 8. 面试题库与答题要点

### 8.1 基础提问

**Q1：这个项目解决什么问题？**

A：解决自动驾驶感知算法资料分散、专业术语多、人工查找成本高的问题。通过垂直领域 RAG，把 Apollo 文档、标准规范和论文报告纳入知识库，让用户能基于可追溯来源进行问答。

**Q2：项目和普通 RAG Demo 有什么区别？**

A：普通 Demo 通常只做上传、向量化和问答。我这个项目重点做了数据治理、source registry、chunk provenance、hybrid retrieval、cross-encoder reranker 和多层评测，能证明每次优化是否有效。

**Q3：系统完整链路是什么？**

A：文档先清洗并登记到 registry，然后按策略 chunk，生成 embedding 写入 Chroma。用户问题进来后，Agent 调用 RAG 工具，系统检索相关 chunk，把上下文和来源注入 prompt，再由 LLM 生成答案，并支持展示来源。

**Q4：为什么选择自动驾驶感知算法？**

A：这个领域专业术语密集，文档来源权威且结构复杂，包括 Apollo 官方文档、法规标准和论文，很适合展示垂直 RAG 的数据治理、术语检索和可追溯问答能力。

### 8.2 深度技术追问

**Q5：BM25 为什么在你的项目里表现很好？**

A：自动驾驶领域有大量精确术语和模块名，例如 Apollo、Cyber RT、BEV、occupancy、planning module。BM25 对关键词和术语精确匹配非常敏感，而 dense embedding 更擅长语义相似。实验中 sparse-only 在 30 题上达到 0.667，高于 dense-only 的 0.233，说明术语匹配非常重要。

**Q6：Hybrid Retrieval 怎么做？**

A：先分别做 dense retrieval 和 BM25 sparse retrieval，各取 top-k。然后把两路分数归一化，按 `alpha * dense_score + (1-alpha) * sparse_score` 融合排序。实验中 `alpha=0.5` 是较稳定的平衡点。

**Q7：Cross-Encoder Reranker 和 Embedding 检索有什么区别？**

A：Embedding 检索是 bi-encoder，query 和 document 独立编码后算相似度，速度快，适合召回。Cross-encoder 把 query 和 chunk 拼在一起输入模型，能捕捉 token 级交互，精度更高但更慢。因此我用 bi-encoder/hybrid 召回 top-20，再用 cross-encoder 精排到 top-5。

**Q8：Reranker 的收益为什么不能只看 Hit@5？**

A：Hit@5 只看前 5 个里有没有正确 source，如果基线已经很高，它无法体现排序改善。Reranker 的价值是把正确 chunk 排得更靠前，所以要看 Hit@1、MRR，以及 RAGAS 的 context_precision/context_recall。

**Q9：semantic chunking 怎么实现？**

A：先按中英文句末标点切句，用 BGE-M3 编码每个句子，计算相邻句子的余弦相似度。如果相似度低于 0.5，就认为语义发生跳转，在这里断开。最后对超过 1000 字符的 chunk 做二次拆分。

**Q10：RAGAS 四个指标怎么解释？**

A：faithfulness 看回答是否被上下文支持；answer_relevancy 看回答是否切题；context_precision 看 top-k 上下文中相关内容排序是否靠前；context_recall 看参考答案需要的信息是否被上下文覆盖。

### 8.3 项目反思类问题

**Q11：v1.0 检索指标为 0，为什么还有价值？**

A：v1.0 的目标不是效果，而是建立评测基线和 artifact contract。没有这个基线，后续 hybrid、reranker、chunking 的收益都无法客观比较。

**Q12：doc_type_aware 为什么没有一直优于 baseline？**

A：有两个原因。第一，不同文档类型结构差异很大，official_doc 的标题和页码更规整，所以收益明显；标准和论文更依赖解析质量、证据位置和 chunk 粒度。第二，早期 doc_type_aware 的实现确实偏浅，主要是不同 `chunk_size/overlap`，不是真正充分利用文档结构。这个反思之后，我把它补强成结构感知策略：标准识别 `[p.N]` / `- [p.N]`，论文识别 `### Page N`，并生成 locator。后续要重建 store 后再评测新收益。

**Q13：当前最大不足是什么？**

A：source 级召回已经不错，但 locator 级证据对齐还不够好；部分标准文档清洗有噪声；概述性文档容易被具体模块文档挤出 top-5；评测脚本还可以进一步做成一键回归门禁。

### 8.4 方案对比类问题

**Q14：Chroma 和 Qdrant 怎么选？**

A：Chroma 适合本地快速实验，部署简单，当前项目已经满足评测需要。Qdrant 更适合后续生产化、过滤查询、混合检索和服务化部署。项目曾规划 Qdrant，但实际因环境和优先级仍使用 Chroma。

**Q15：RAG 优化和微调怎么取舍？**

A：先看错误归因。如果错误主要是检索不到正确上下文，优先优化检索、chunk、reranker 和数据清洗。如果上下文正确但回答不忠实，再考虑 prompt、解码约束或 QLoRA。

**Q16：HyDE 和 reranker 有什么区别？**

A：HyDE 是查询改写/扩展思路，用 LLM 生成假设答案再检索，适合 query 和文档表述差异大。Reranker 是对已召回候选重排，适合提高 top-k 排序质量。一个偏召回增强，一个偏精排增强。

**Q17：doc_type_aware 和 semantic chunking 怎么取舍？**

A：doc_type_aware 是结构先验驱动，适合文档格式稳定、页码和标题层级清晰的 Apollo/标准/论文场景；semantic chunking 是内容相似度驱动，适合语义边界不完全等同于格式边界的长文本。我的经验是两者不应该绝对替代，而应该作为不同策略做消融。当前最新 100 篇文档口径下，两者加 reranker 后 Hit@5 都是 0.94，semantic + reranker 的 MRR 略高。

### 8.5 应急问题

**Q18：如果线上回答幻觉怎么办？**

A：先检查检索上下文是否正确。如果上下文正确但回答发散，就收紧 prompt，要求只基于上下文回答，并输出引用；同时用 RAGAS faithfulness 和 Judge 做回归。如果上下文错误，则优先修检索。

**Q19：如果检索不到正确文档怎么办？**

A：按层排查：source 是否入库、embedding 是否重建、chunk 是否包含证据、BM25 是否能召回、dense 是否召回、hybrid alpha 是否合适、reranker 是否把正确 chunk 排下去了。

**Q20：如果 API 限流怎么办？**

A：项目里遇到过 ModelScope 429。严谨做法不是在同一次评测里临时换模型，而是先退避重试；如果仍失败，就让当前 run 失败或把该样本标记为空结果。要换成本地 BGE-M3 可以，但必须重新建库、重新跑完整评测，并把新旧结果作为两个独立 run 对比。这样才满足控制变量法。

**Q21：如果评测结果突然下降怎么办？**

A：先看 manifest 确认 dataset、store、embedding、provider、chat_model、reranker 是否一致；如果发现同一组结果里混用了模型，就不能拿来做结论。然后检查是否误用了默认 Chroma store；最后对比 predictions 里的 retrieved_rows 和 debug candidates，定位是召回问题还是生成问题。

**Q22：为什么 100 篇文档后 Hit@5 从历史高点下降到 0.94？**

A：这是规模扩大后的正常现象，不应该解释成方法失效。41 篇阶段候选空间小，相似 source 较少，问题也更集中；扩到 100 篇后，标准、论文、报告大量增加，概念相近的文档会互相竞争，top-k 召回难度更高。0.94 更接近真实检索难度，也更适合作为最终口径。

**Q23：为什么 hybrid 或 reranker 在端到端 source_hit 上有时不如 dense-only？**

A：端到端 source_hit 会受到生成模型、top-k 截断、chunk 内容完整度和评测答案匹配共同影响。hybrid/reranker 的主要收益可能体现在排序质量、context_precision、context_recall 或 MRR 上，而不一定每次都反映在 source_hit。遇到这种情况要拆开看 retrieval-only 指标和 RAGAS 指标，不能只用一个指标下结论。

**Q24：如何证明 reranker 有价值？**

A：要看三类证据。第一，看 MRR 和 Hit@1 是否提升，说明正确证据排得更靠前。第二，看 RAGAS 的 context_precision/context_recall 是否提升，说明上下文质量变好。第三，看 case study，比较 rerank 前后 top-5 的顺序变化。如果只是 Hit@5 不变，也可能是 reranker 把正确 chunk 从第 5 位提到第 1 位，这对生成质量很重要。

**Q25：如何排查 locator_hit 为 0 或偏低？**

A：先确认 gold set 是否有 locator 标注，再确认 chunk metadata 是否写入 page/section/locator。然后看清洗后的 Markdown 是否保留页码和标题；如果文档没有结构标记，就算 source 命中也无法判断细粒度位置。最后检查评测脚本是否按统一格式比较 locator，避免 `p.3`、`Page 3`、`pages 3-4` 这种格式不一致。

**Q26：如果重建向量库成本高怎么办？**

A：可以做增量化和缓存。文档层用 MD5 判断是否变化，chunk 层记录 `source_id/chunk_strategy/chunk_order`，embedding 层做向量缓存。只有清洗规则、chunk 策略、embedding 模型或 source 内容变化时才重建相关部分。评测时通过 manifest 固定 store-dir，避免不同版本混用。

**Q27：如果面试官问“这个项目怎么落到生产”？**

A：生产化要补三块。服务层把 Streamlit 原型拆成 API 服务和前端；数据层加入定时同步、增量入库、权限控制和版本化索引；质量层加入一键评测门禁、灰度发布、日志追踪和人工反馈闭环。向量库可以从 Chroma 迁移到 Qdrant，支持更稳定的服务化部署和 metadata filter。

**Q28：这个项目适合怎么写到简历上？**

A：可以写成“自动驾驶感知领域 LocalRAG 系统”，突出 100 篇垂直文档、100 题评测集、BGE-M3 + BM25 hybrid、cross-encoder reranker、RAGAS/Judge 评测闭环。量化结果写最新口径：Hit@5 约 0.94、MRR 约 0.893，RAGAS context_recall 从 dense-only 0.0372 提升到 hybrid + reranker 0.9366。注意不要只写 0.98，因为那是历史小规模口径。

## 9. 可直接背的项目话术

### 9.1 30 秒版

我做了一个自动驾驶感知算法领域的 LocalRAG 系统。它不只是简单问答，而是从数据治理、文档清洗、chunk provenance、hybrid retrieval、cross-encoder reranker 到 RAGAS/LLM Judge 评测都做了闭环。检索层从 dense-only 到 BM25 + dense hybrid，再到 reranker，30 题 source_hit 从 0.233 提升到最高 0.967；最新 100 文档口径下，semantic + reranker Hit@5 约 0.94，MRR 约 0.893。

### 9.2 1 分钟版

这个项目的主线是评估先行。v1.0 先建立 Gold Set、schema、baseline runner 和 Judge 骨架；v1.1 做 source registry、文档清洗、doc_type_aware chunking 和 provenance metadata；v1.2 做 BGE-M3、BM25、hybrid retrieval、cross-encoder reranker 和 semantic chunking；v1.3 扩到 100 篇文档、eval 100 题和 train 203 题。过程中我发现自动驾驶领域术语密集，BM25 对精确术语非常有效，dense 和 sparse 融合后比单路检索更稳。扩容后最新 Hit@5 是 0.94，MRR 最高 0.893；这也提醒我不能只拿小规模阶段的 98% 讲成果，必须明确评测口径。

### 9.3 2 分钟版

我的 LocalRAG 项目面向自动驾驶感知算法，知识源包括 Apollo 文档、标准规范和自动驾驶论文。项目最大的特点是工程闭环比较完整：数据层有 source registry 和 provenance metadata，检索层有 dense、BM25、hybrid 和 cross-encoder reranker，评测层有 retrieval-only、chunking eval、RAGAS 和 pairwise LLM Judge。

迭代上，我先在 v1.0 建评测基线，即使 local-hash embedding 指标为 0，也先把实验合同固定下来。v1.1 做数据层，source_hit 从 0.233 到 0.367，official_doc 类提升更明显。v1.2 做检索层，30 题上 dense-only 0.233，sparse-only 0.667，hybrid alpha=0.5 到 0.733，cross-encoder reranker 后最高到 0.967。扩展到 100 文档后，最新最优配置 Hit@5 约 0.94，MRR 约 0.893。RAGAS 上，dense-only 的 context_recall 只有 0.0372，hybrid + reranker 提升到 0.9366，说明检索链路优化对端到端质量影响很大。

我最大的收获是：RAG 优化不能只看最终答案，也不能只看 Hit@5。要把 source hit、locator、MRR、context_precision、context_recall 和 faithfulness 结合起来，才能判断瓶颈到底在数据、检索、重排还是生成。

## 10. 后续优化方向

### 10.1 P0：先补齐评测和证据链

这部分最应该优先做，因为它直接影响项目可信度：

- 基于当前结构感知版 doc_type_aware 重新建库，重新跑 chunking eval 和 retrieval-only eval。
- 修复 locator 级命中与证据对齐，统一 page/section/locator 格式。
- 清理标准文档中的噪声、网页残留、页眉页脚和表格解析问题。
- 对标准/表格类文档设计专用 chunking，例如按条款号、表号、章节号切分。
- 将 retrieval、RAGAS、Judge 做成一键回归门禁，避免只靠人工手动跑实验。
- 增强 manifest，强制记录 dataset、store-dir、embedding model、chunk_strategy、reranker model、provider。

面试表达：我会先修评测闭环和证据定位，因为 source_hit 已经较高，下一步更重要的是把“找到文档”提升到“找到可引用证据”。

### 10.2 P1：检索和排序继续增强

这部分是指标继续提升的主线：

- 用 RRF 替代简单 alpha 加权，降低 dense/sparse 分数尺度差异带来的不稳定。
- 做 query-adaptive alpha：术语密集问题提高 BM25 权重，概念解释问题提高 dense 权重。
- 构造 hard negatives 微调 reranker，让模型学会区分相似 Apollo 模块、相似标准条款和相似论文段落。
- 引入 parent-child hierarchical index：小 chunk 用于精确召回，大 chunk 用于给 LLM 完整上下文。
- 尝试 HyDE 或 query expansion，解决用户问题和文档表述差异较大的 case。
- 对 top-k 做多样性约束，避免多个 chunk 都来自同一 source，挤掉概述性文档。

面试表达：当 Hit@5 接近天花板后，重点不是盲目扩大 top-k，而是改善排序、覆盖和上下文质量。

### 10.3 P2：工程化与产品化

这部分用于把项目从实验系统推向可展示产品：

- 用 Chainlit 或 FastAPI + 前端替代单纯 Streamlit 原型，增强会话体验和来源展示。
- Docker 化部署，固定 Python、模型缓存、向量库路径和环境变量。
- 做 embedding 缓存和批量入库优化，减少重建 store 成本。
- 加入日志追踪：记录 query、召回 source、reranker 分数、最终回答、用户反馈。
- 对本地模型推理做性能测试，包括 embedding 吞吐、reranker 延迟和端到端响应时间。
- 引入权限控制和 source 版本管理，为企业知识库场景做准备。

面试表达：工程化不是换一个 UI，而是让数据、模型、索引、评测和部署都能被版本化管理。

### 10.4 P3：模型微调作为后续加分项

QLoRA 或 instruction tuning 可以做，但前提是错误归因显示生成侧确实是瓶颈：

- 用失败样本构造 instruction tuning 数据。
- 训练“只基于上下文回答”“引用来源”“无法回答时拒答”等能力。
- 用 pairwise Judge 数据构造偏好样本，尝试 DPO 或 reranker 数据蒸馏。
- 对比微调前后的 faithfulness、answer_relevancy 和人工 Judge 胜率。

面试表达：我不会一开始就微调，因为 RAG 系统的主要收益来自高质量证据链；只有当上下文正确但生成仍不稳定时，微调才是更合理的投入。

## 11. 面试中需要诚实说明的口径

1. `RAG_md` 中有 41 文档阶段 Hit@5 0.98 的旧结果；最新 100 文档口径下最优 Hit@5 约 0.94，MRR 约 0.893。
2. 当前仍使用 ChromaDB，Qdrant 是规划项，不要说已经完成迁移。
3. 早期 doc_type_aware 主要是参数分档，不够充分；当前已补强结构感知，但新收益需要重建 store 后重新评测。
4. locator 级命中仍是技术债，source 级召回强，但细粒度证据定位还要优化。
5. QLoRA 是后续可选项，不是当前主线成果。
6. 部分标准文档清洗仍有噪声，需要后续治理。

## 12. 总结

这个项目最适合在面试中突出三点：

1. 评估先行：先建立指标和 artifact contract，再做优化。
2. 工程闭环：数据治理、检索、重排、生成、评测、误差分析都有落地。
3. 方法论成熟：能用实验说明为什么做 hybrid、为什么加 reranker、为什么暂时不优先微调，以及下一步应该优化哪里。

最终一句话：

> LocalRAG 的核心价值不是把文档塞进向量库，而是用自动驾驶垂直领域数据，把 RAG 的数据、检索、重排和评测做成了一个可解释、可复现、可迭代的工程系统。
