# Judge formal run test report

- Generated at: 2026-05-01T19:14:16
- Dataset: `/root/workspace/LocalRAG/data/evaluation/gold/gold_set.json`
- Baseline run: `/root/workspace/LocalRAG/results/baseline_eval/gold_set-20260501-190804`
- Candidate run: `/root/workspace/LocalRAG/results/chunking_eval/gold_set-20260501-190943`
- Judge run: `/root/workspace/LocalRAG/results/judge_eval/predictions-vs-predictions-20260501-191339`

## Commands
- `cd /root/workspace/LocalRAG && /opt/aiext/bin/python -c 'from pathlib import Path; import eval.eval_ragas as module; module.build_run_id = lambda *_: '"'"'gold_set-20260501-190804'"'"'; module.run_baseline_to_dir(Path('"'"'/root/workspace/LocalRAG/data/evaluation/gold/gold_set.json'"'"'), Path('"'"'/root/workspace/LocalRAG/results/baseline_eval'"'"'))'`
- `cd /root/workspace/LocalRAG && /opt/aiext/bin/python -c 'import sys; from eval import eval_chunking as module; module.build_run_id = lambda *_: '"'"'gold_set-20260501-190943'"'"'; sys.argv = ['"'"'eval_chunking.py'"'"', '"'"'--dataset'"'"', '"'"'/root/workspace/LocalRAG/data/evaluation/gold/gold_set.json'"'"', '"'"'--out-dir'"'"', '"'"'/root/workspace/LocalRAG/results/chunking_eval'"'"']; module.main()'`
- `cd /root/workspace/LocalRAG && /opt/aiext/bin/python -c 'from pathlib import Path; import eval.eval_llm_judge as module; module.build_run_id = lambda *_: '"'"'predictions-vs-predictions-20260501-191339'"'"'; module.run_pairwise_judge_to_dir(Path('"'"'/root/workspace/LocalRAG/results/baseline_eval/gold_set-20260501-190804/predictions.json'"'"'), Path('"'"'/root/workspace/LocalRAG/results/chunking_eval/gold_set-20260501-190943/doc_type_aware/predictions.json'"'"'), Path('"'"'/root/workspace/LocalRAG/results/judge_eval'"'"'))'`

## Summaries
- baseline_summary: `{"answered_count": 30, "answered_ratio": 1.0, "avg_retrieval_debug_candidate_count": 0.0, "avg_retrieved_row_count": 0.0, "context_hit_count": 0, "context_hit_ratio": 0.0, "evidence_locator_hit_count": 0, "evidence_locator_hit_ratio": 0.0, "evidence_source_hit_count": 0, "evidence_source_hit_ratio": 0.0, "exact_match_count": 0, "exact_match_ratio": 0.0, "normalized_exact_match_count": 0, "normalized_exact_match_ratio": 0.0, "reference_substring_hit_count": 0, "reference_substring_hit_ratio": 0.0, "retrieval_debug_candidate_count": 0, "retrieved_row_count": 0, "sample_count": 30}`
- chunking_summary: `{"baseline": {"answered_count": 30, "answered_ratio": 1.0, "evidence_locator_hit_count": 0, "evidence_locator_hit_ratio": 0.0, "evidence_source_hit_count": 12, "evidence_source_hit_ratio": 0.4, "retrieved_row_count": 150, "sample_count": 30}, "doc_type_aware": {"answered_count": 30, "answered_ratio": 1.0, "evidence_locator_hit_count": 0, "evidence_locator_hit_ratio": 0.0, "evidence_source_hit_count": 12, "evidence_source_hit_ratio": 0.4, "retrieved_row_count": 150, "sample_count": 30}, "run_id": "gold_set-20260501-190943"}`
- judge_summary: `{"baseline_win_count": 27, "candidate_win_count": 3, "sample_count": 30, "tie_count": 0}`

## Verification
- Result: **PASS**
- Failures: none
