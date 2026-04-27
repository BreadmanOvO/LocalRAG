# TODO

## Next work before and during v1.2

1. **Expand the Gold Set into a stronger version gate**
   - Goal: move from the current tiny sample to a more stable 30-50 question gate.
   - Focus: perception, planning/control, safety, and system architecture coverage.

2. **Run the baseline evaluation for real and keep the artifacts**
   - Script: `eval_ragas.py`
   - Desired output: reusable real `predictions` / `metrics` artifacts for the current baseline.

3. **Start hybrid retrieval experiment design**
   - Goal: define the first dense + sparse/BM25 comparison against the current chunking baseline.
   - Constraint: keep retrieval inspection and comparison artifacts reusable.

4. **Deepen retrieval inspection and error analysis**
   - Goal: make it easier to explain why a gold evidence source was retrieved, outranked, or missing.
   - Focus: scored candidates, locator boundaries, and per-sample evidence analysis.

## Local runtime reminder

Keep a local-only `config/runtime_models.json` with a unified shape:

```json
{
  "provider": "modelscope",
  "api_key": "...",
  "base_url": "https://api-inference.modelscope.cn/v1",
  "chat_model_name": "Qwen/Qwen2.5-72B-Instruct",
  "embedding_model_name": "Qwen/Qwen3-Embedding-8B"
}
```

Do not commit this file.
