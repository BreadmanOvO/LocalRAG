# TODO

## Pending runs blocked by API keys

1. **Run the baseline evaluation for real and save artifacts**
   - Script: `eval_ragas.py`
   - Blocker: missing repository-root `key.json` runtime config
   - Desired output: real `predictions` / `metrics` artifacts for the current baseline instead of test-only validation.

2. **Run the chunking comparison for real and save artifacts**
   - Script: `eval_chunking.py`
   - Blockers: missing repository-root `key.json` runtime config
   - Desired output: `results/chunking_eval/<run_id>/` containing:
     - `baseline/predictions.json`
     - `baseline/metrics.json`
     - `doc_type_aware/predictions.json`
     - `doc_type_aware/metrics.json`
     - `comparison/summary.json`
     - `comparison/by_doc_type.json`
     - `comparison/by_source_id.json`
     - `comparison/error_cases.json`
     - `report.md`

## How to unblock

Create a local-only root `key.json` with this exact shape:

```json
{
  "dashscope_api_key": "...",
  "dashscope_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "chat_model_name": "qwen3-max",
  "embedding_model_name": "text-embedding-v4"
}
```

Do not commit this file.

Then run the blocked scripts.
