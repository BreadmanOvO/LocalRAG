# 仓库使用说明

## 工程/运行文件
- `app.py` / `app_file_uploader.py`：应用入口与上传入口
- `rag.py`：主问答服务
- `knowledge_base.py`：知识库写入与 chunk 入库
- `chunking.py`：chunk 切分与 provenance metadata
- `config_data.py`：运行配置

## 实验/评测脚本
- `eval_ragas.py`：基础 baseline 评测入口
- `eval_llm_judge.py`：judge scaffold
- `eval_chunking.py`：chunking 对比实验入口
- `test/`：单元测试与实验验证脚本
- `data/evaluation/`：评测数据与 source registry

## 结果目录
- `results/`：所有生成结果
- `results/chunking_eval/<run_id>/`：chunking 对比实验结果
  - `baseline/`
  - `doc_type_aware/`
  - `comparison/`
  - `report.md`

## 使用约定
- 日常运行主系统时，优先看工程/运行文件。
- 做对比实验时，优先看实验/评测脚本。
- 新增实验脚本或结果目录时，同步更新本文件和 `README.md`。
