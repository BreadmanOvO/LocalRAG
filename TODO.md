# v1.2 检索层待办事项

> 环境要求：需要 GPU（用于本地 cross-encoder / embedding）
> 当前进度：Step 1-5 已完成，Step 6 开始需要 GPU 环境

---

## 已完成（仅供参考）

- Step 1: 嵌入模型切换（LocalHash → Qwen3-Embedding-0.6B via ModelScope API）
- Step 2-4: Hybrid Retrieval（dense + BM25 sparse，最优 α=0.5，source_hit=0.733）
- Step 5: Retrieval Inspection 工具
- 对比报告：`RAG_md/docs/reports/v1.2-retrieval-comparison-report.md`

---

## TODO-1: 集成本地 Cross-Encoder Reranker ✅

**优先级**：高（v1.2 核心任务）

**已完成**：
1. ✅ 新增 `CrossEncoderReranker` 类（`core/reranker.py`），使用 `sentence_transformers.CrossEncoder`
2. ✅ 保留 `LLMReranker` 作为 fallback
3. ✅ `eval/eval_reranker.py` 支持 `--reranker cross-encoder|llm` 参数切换
4. ✅ 默认模型：`BAAI/bge-reranker-base`（可通过 `--reranker-model` 自定义）

**运行命令**：
```bash
# Cross-encoder reranker（默认，推荐）
python eval/eval_reranker.py   --dataset data/evaluation/gold/gold_set.json   --store-dir results/chunking_eval/stores/gold_set-20260505-104419/baseline   --alpha 0.5

# LLM reranker（fallback）
python eval/eval_reranker.py   --dataset data/evaluation/gold/gold_set.json   --store-dir results/chunking_eval/stores/gold_set-20260505-104419/baseline   --alpha 0.5 --reranker llm
```

**对比**：
- hybrid retrieval（无 rerank）source_hit = 0.733
- hybrid retrieval + rerank → 看 source_hit 是否提升

**产出**：`results/reranker_eval/` 下的对比结果

---

## TODO-2: Hybrid + doc_type_aware 完整评测

**优先级**：中

**做什么**：
在 doc_type_aware store 上运行 hybrid eval（α=0.5），对比 baseline store 的结果。

之前因 ModelScope API 限流（429）未完成。在 GPU 环境下，embedding 可以本地跑，不受限。

**运行命令**：
```bash
# 需要先修改 config/runtime_models.json 中的 provider 为本地 embedding
# 或者如果有 ModelScope API 额度，直接跑：
python eval/eval_hybrid.py \
  --dataset data/evaluation/gold/gold_set.json \
  --store-dir results/chunking_eval/stores/gold_set-20260505-104419/doc_type_aware \
  --alpha 0.5
```

**对比**：
- baseline store + hybrid α=0.5 → 0.733（已有）
- doc_type_aware store + hybrid α=0.5 → 待测

**已有参考数据**（不含 hybrid）：
- baseline store + dense-only → 0.233
- doc_type_aware store + dense-only → 0.367
- baseline store + sparse-only → 0.667
- doc_type_aware store + sparse-only → 0.700

---

## TODO-3: Reranker + doc_type_aware 联合评测

**优先级**：中（TODO-1 和 TODO-2 完成后）

**做什么**：
在 doc_type_aware store 上运行 hybrid + reranker，看双重优化是否叠加。

**验证方式**：
```bash
python eval/eval_reranker.py \
  --dataset data/evaluation/gold/gold_set.json \
  --store-dir results/chunking_eval/stores/gold_set-20260505-104419/doc_type_aware \
  --alpha 0.5
```

---

## TODO-4（可选）: HyDE（假设性文档嵌入）

**优先级**：低（reranker 收益趋稳后再考虑）

**做什么**：
1. 用 LLM 为每个 query 生成假设性答案
2. 用假设性答案做 retrieval（而非原始 query）
3. 适合 query 和文档表述差异大的场景

**实现位置**：新建 `core/hyde_retriever.py`

**验证**：对比 hybrid vs hybrid + HyDE

---

## TODO-5（可选）: Hierarchical Index

**优先级**：低

**做什么**：
1. 建立 parent-child chunk 结构
2. 先检索 child chunk，再关联到 parent chunk 提供上下文

**验证**：对比 hybrid + rerank vs hybrid + rerank + hierarchical

---

## 环境切换注意事项

从当前机器迁移到 GPU 机器时：

1. **配置文件**：`config/runtime_models.json`
   - 如果 GPU 机器用本地 embedding，provider 改为 `local_embedding` 或 `local_sentence_transformer`
   - 如果继续用 ModelScope API，保持不变

2. **依赖安装**：
   ```bash
   pip install rank-bm25 sentence-transformers langchain-chroma pysqlite3-binary
   ```

3. **ChromaDB stores**：在 `results/chunking_eval/stores/gold_set-20260505-104419/` 下
   - `baseline/` — baseline chunking 的向量库
   - `doc_type_aware/` — doc_type_aware chunking 的向量库
   - 注意：如果切换 embedding 模型，需要重新 build stores

4. **数据集**：`data/evaluation/gold/gold_set.json`（30 题）

---

## 当前最优结果汇总

## 评测结果汇总（30 题 vs 100 题）

### 30 题评测集（Qwen3-Embedding-0.6B API）

| 配置 | source_hit |
|------|:---------:|
| v1.1 baseline（hash embedding） | 0.400（虚高） |
| Qwen3 + baseline + dense-only | 0.233 |
| Qwen3 + doc_type_aware + dense-only | 0.367 |
| Qwen3 + baseline + sparse-only | 0.667 |
| Qwen3 + baseline + hybrid α=0.5 | **0.733** |
| Qwen3 + doc_type_aware + sparse-only | 0.700 |
| Qwen3 + doc_type_aware + hybrid α=0.5 | 0.700 |
| Qwen3 + baseline + hybrid + cross-encoder reranker | 0.933 |
| Qwen3 + doc_type_aware + hybrid + cross-encoder reranker | **0.967** |

### 100 题评测集（BAAI/bge-m3 本地，41 篇文档，含排名指标）

| 分块策略 | Reranker | Hit@5 | MRR | Hit@1 | Hit@3 | 命中数 |
|---------|:--------:|:-----:|:---:|:-----:|:-----:|:------:|
| baseline | No | 0.960 | 0.865 | 0.790 | 0.940 | 96 |
| baseline | Yes | 0.960 | 0.899 | 0.850 | 0.950 | 96 |
| doc_type_aware | No | 0.940 | 0.870 | 0.830 | 0.900 | 94 |
| doc_type_aware | Yes | 0.960 | **0.904** | **0.860** | 0.950 | 96 |
| **semantic** | No | **0.970** | 0.864 | 0.800 | 0.920 | **97** |
| **semantic** | Yes | **0.980** | 0.897 | 0.840 | 0.950 | **98** |

**关键发现**：
1. **Reranker 的真实价值在排名指标下可见**：Hit@1 +6.0%，MRR +3.9%（baseline 配置）
2. **语义分块最优**：Hit@5 97%→98%（+reranker），解决 2 道其他策略未命中题目
3. **最优配置**：semantic + reranker = 98% Hit@5，0.897 MRR
4. **天花板效应**：Hit@5 已接近上限，MRR/Hit@1 才能看到优化差异
5. 详细报告：`RAG_md/docs/reports/v1.2-chunking-comparison-report.md`
