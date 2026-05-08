# Chunking evaluation report: gold_set-20260505-104419

## Run metadata
- Dataset: data/evaluation/gold/gold_set.json
- Baseline store: results/chunking_eval/stores/gold_set-20260505-104419/baseline
- Doc-type-aware store: results/chunking_eval/stores/gold_set-20260505-104419/doc_type_aware

## Overall summary
- baseline answered ratio: 1.0
- doc_type_aware answered ratio: 1.0
- baseline evidence source hit ratio: 0.233
- doc_type_aware evidence source hit ratio: 0.367
- baseline evidence locator hit ratio: 0.0
- doc_type_aware evidence locator hit ratio: 0.0

## Comparison by doc_type
- official_doc: baseline=0.3 doc_type_aware=0.55
- paper: baseline=0.0 doc_type_aware=0.0
- report: baseline=1.0 doc_type_aware=0.0
- standard: baseline=0.0 doc_type_aware=0.0

## Metric notes
- evidence source hit: whether any retrieved row matched the gold evidence source_id
- evidence locator hit: whether any retrieved row matched the gold evidence locator after normalization

## Error cases
- gold-006: baseline_source_hit=True, doc_type_aware_source_hit=False
- gold-011: baseline_source_hit=False, doc_type_aware_source_hit=True
- gold-012: baseline_source_hit=False, doc_type_aware_source_hit=True
- gold-014: baseline_source_hit=False, doc_type_aware_source_hit=True
- gold-015: baseline_source_hit=False, doc_type_aware_source_hit=True
- gold-017: baseline_source_hit=False, doc_type_aware_source_hit=True
