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

Keep a local-only root `key.json` with this exact shape:

```json
{
  "dashscope_api_key": "...",
  "dashscope_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "chat_model_name": "qwen3-max",
  "embedding_model_name": "text-embedding-v4"
}
```

Do not commit this file.
