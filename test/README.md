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
