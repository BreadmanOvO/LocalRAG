# test 脚本目录

本目录用于存放 LocalRAG 的测试与评估脚本。

## 1) chunk 参数测试

脚本：`chunk_benchmark.py`

用途：快速比较不同 `chunk_size/chunk_overlap` 的切分结果统计，辅助选择候选参数。

示例：

```bash
python test/chunk_benchmark.py --input data/your_doc.txt
```

自定义参数组：

```bash
python test/chunk_benchmark.py --input data/your_doc.txt --pairs "500:80,800:120,1000:150"
```

输出 JSON 报告：

```bash
python test/chunk_benchmark.py --input data/your_doc.txt --out test/chunk_report.json
```

## 2) v1.6 本地模型服务合同

以下测试不加载真实 4B 权重：

```powershell
python -m unittest test.test_model_serving_profiles test.test_model_manifest -v
python -m unittest test.test_model_serving_api -v
python -m unittest test.test_transformers_backend -v
```

- `test_model_serving_profiles.py`：固定 BF16/Q4 profile 和路径边界。
- `test_model_manifest.py`：验证模型输入 SHA-256 与 E6.1 LoRA 身份。
- `test_model_serving_api.py`：验证 OpenAI-compatible API、队列、SSE 和指标。
- `test_transformers_backend.py`：使用 mock 验证 BF16/PEFT 加载、生成、取消和 OOM latch。

## 3) v1.6 模型质量与服务性能

以下测试默认不加载真实权重；真实模型结果保存在 `results/model_quality/` 和
`results/model_benchmark/`，由 release manifest 记录路径与 SHA-256：

```powershell
python -m unittest test.test_model_quality_eval test.test_serving_benchmark -v
python eval/eval_model_quality.py --mode deterministic
python eval/benchmark_serving.py --mode deterministic
```

- `test_model_quality_eval.py`：验证四 profile、三段质量隔离和固定 10-case Gate。
- `test_serving_benchmark.py`：验证 9-cell 矩阵、队列指标、原子 checkpoint、断点恢复和失败关闭。
- 正式部署结果见 `model_deployment/manifests/v1_6_model_serving_release.json`。

## 4) v1.6 本地服务端到端验证

`results/v1_6_e2e/task8_e2e_summary.json` 记录 Q4 llama.cpp、LocalRAG gateway 和
前端页面的去敏验证结果，包括健康检查、鉴权、SSE、模型路由和会话压缩面板。
该报告不包含 prompt、answer、API token、权重或截图；未配置云凭据时，真实云降级不在
本地端到端范围内。

## 5) 文档上传入库工作流

以下测试覆盖文本规范化、预览、显式发布、重复发布和可选评测回调：

```powershell
python -m unittest test.test_ingestion_workflow -v
```

测试使用内存 Chroma 替身，不会修改当前知识库。
