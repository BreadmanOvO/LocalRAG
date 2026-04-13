# 参考资料与学习路径

## 使用方式
集中存放项目规划阶段参考的技术文档、论文、数据源与面试学习材料。

## 核心技术文档

### 评估框架
- [Ragas 官方文档](https://docs.ragas.io/) — 客观评估框架
- [LMSYS Chatbot Arena](https://chat.lmsys.org/) — LLM-as-a-Judge 参考
- [MT-Bench 论文](https://arxiv.org/abs/2306.05685) — 多轮对话评估参考

### 检索优化
- [HyDE 论文](https://arxiv.org/abs/2212.10496) — Hypothetical Document Embeddings
- [BGE-M3 模型](https://huggingface.co/BAAI/bge-m3) — 多语言多模式检索
- [Qdrant Hybrid Search 文档](https://qdrant.tech/documentation/concepts/search/#hybrid-search) — 混合检索实现参考

### 模型微调
- [Unsloth](https://github.com/unslothai/unsloth) — QLoRA 训练工具
- [DPO 论文](https://arxiv.org/abs/2305.18290) — Direct Preference Optimization
- [Flash-Attention 2 论文](https://arxiv.org/abs/2307.08691) — 训练加速参考

### 部署优化
- [llama.cpp Build 指南](https://github.com/ggerganov/llama.cpp#build) — 编译与部署入口
- [vLLM PagedAttention 论文](https://arxiv.org/abs/2309.06180) — 显存管理思路
- [GGML](https://github.com/ggerganov/ggml) — 量化与推理基础

## 数据源（自动驾驶领域）

### 中文文档
- [Apollo 自动驾驶平台文档](https://apollo.auto/docs/) — 感知、规划、控制等核心资料
- [CSDN 自动驾驶专栏](https://blog.csdn.net/nav/ai) — 技术博客补充
- [知乎自动驾驶话题](https://www.zhihu.com/topic/19551132/hot) — 行业讨论与文章入口

### 英文论文
- [arXiv 自动驾驶感知检索](https://arxiv.org/search/?query=autonomous+driving+perception) — 感知相关论文检索
- [CVF Open Access](https://openaccess.thecvf.com/) — CVPR / ECCV / ICCV 论文入口
- [Waymo Open Dataset](https://waymo.com/open/) — 数据集与技术报告

### 标准规范
- ISO 26262 — 功能安全标准
- SOTIF（ISO 21448）— 预期功能安全
- NHTSA / SAE 标准 — 自动驾驶分级与规范参考

## 面试准备资料

### Transformer 与大模型基础
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — Transformer 原始论文
- [RoPE 详解（苏剑林）](https://kexue.fm/archives/8265) — 相对位置编码中文解释

### 工程与系统设计
- 召回率与精确率权衡
- 多路召回融合策略
- 查询改写技术对比
- 评估指标选择依据

### C++ / 推理优化方向
- 内存对齐原理
- 多线程同步策略
- KV Cache 管理优化
- 首字延迟（TTFT）影响因素
