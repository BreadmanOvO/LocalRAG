# TODO

## Pending runs blocked by API keys

1. **Run the baseline evaluation for real and save artifacts**
   - Script: `eval_ragas.py`
   - Blocker: missing `OPENAI_API_KEY`
   - Desired output: real `predictions` / `metrics` artifacts for the current baseline instead of test-only validation.

2. **Run the chunking comparison for real and save artifacts**
   - Script: `eval_chunking.py`
   - Blockers: missing `OPENAI_API_KEY` and `DASHSCOPE_API_KEY`
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

In this Claude Code session, export the keys first:

```bash
! export OPENAI_API_KEY=...
! export DASHSCOPE_API_KEY=...
```

Then run the blocked scripts.
