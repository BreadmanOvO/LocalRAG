# 仓库使用说明

## 工程/运行文件
- `app_qa.py`：Streamlit 问答入口
- `app_file_uploader.py`：知识库上传入口
- `agent/react_agent.py`：Agent 入口
- `core/rag.py`：baseline RAG 主服务
- `core/knowledge_base.py`：知识库写入与 chunk 入库
- `core/chunking.py`：chunk 切分、locator 与 provenance metadata
- `core/vector_stores.py`：向量检索封装
- `config/settings.py`：静态运行参数
- `config/runtime_keys.py`：运行时私有配置加载器

## 实验/评测脚本
- `eval/eval_ragas.py`：baseline 评测入口
- `eval/eval_llm_judge.py`：规则式 pairwise judge 入口
- `eval/eval_chunking.py`：chunking 对比实验入口
- `test/`：单元测试与实验验证脚本
- `data/evaluation/`：评测数据与 source registry

## 结果目录
- `results/baseline_eval/<run_id>/`
  - `predictions.json`
  - `metrics.json`
  - `manifest.json`
- `results/judge_eval/<baseline_run_id>-vs-<candidate_run_id>/`
  - `judgements.json`
  - `summary.json`
  - `manifest.json`
- `results/chunking_eval/<run_id>/`
  - `baseline/`
  - `doc_type_aware/`
  - `comparison/`
  - `report.md`
  - `manifest.json`
- `results/chunking_eval/stores/`：实验运行时生成的本地向量库缓存，不提交到仓库

## 使用约定
- 日常运行主系统时，优先看工程/运行文件。
- 做对比实验时，优先看实验/评测脚本与 `results/` 下的对应 bundle。
- 新增实验脚本或结果目录时，同步更新本文件和 `README.md`。
