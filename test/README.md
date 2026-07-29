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
