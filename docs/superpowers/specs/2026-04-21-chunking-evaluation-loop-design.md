# LocalRAG chunking evaluation loop design

## Goal

Add a dedicated experiment flow that rebuilds two knowledge bases from the same cleaned sources, runs the same evaluation dataset against both chunking strategies, compares the outputs by retrieval evidence and sample metadata, and saves both machine-readable artifacts and a human-readable report.

This iteration is meant to answer one concrete question: does `doc_type_aware` chunking produce measurable gains over `baseline` chunking on the current LocalRAG evaluation datasets?

## Scope

### In scope

1. Add a dedicated chunking evaluation experiment entrypoint.
2. Rebuild one knowledge base with `baseline` chunking and one with `doc_type_aware` chunking.
3. Ingest source documents using the source registry and cleaned markdown, preserving true `source_id`, `doc_type`, and locator metadata.
4. Run one evaluation dataset against both rebuilt knowledge bases.
5. Save organized prediction, metric, comparison, error-case, and report artifacts.
6. Add repository usage guidance that distinguishes engineering entrypoints from experiment scripts and result directories.
7. Run at least one real comparison and save the resulting artifacts in the repository.

### Out of scope

- hybrid retrieval
- reranking
- replacing the existing judge scaffold with a real pairwise judge
- UI changes
- broad repository restructuring unrelated to evaluation navigation

## Design summary

The chunking experiment should be implemented as a separate evaluation pipeline, not as an extension of the current upload-based app flow.

The key reason is that the current upload path in `knowledge_base.py` marks uploads as `doc_type="untyped"`, which forces baseline chunking and cannot produce a meaningful comparison with `doc_type_aware`. A valid chunking experiment must ingest registry-backed cleaned documents using their actual `doc_type` values.

The experiment should produce two isolated stores:

1. one built with `baseline`
2. one built with `doc_type_aware`

The evaluation runner should then execute the same dataset against both stores, capture both answer output and retrieval metadata, compute comparison summaries, and write all artifacts into a single run directory.

## File and component design

### Experiment entrypoint

#### `eval_chunking.py`

This file should be the only top-level experiment entrypoint for the chunking comparison.

Its responsibilities are:

- load source registry records
- resolve cleaned markdown paths for ingestion
- build two isolated knowledge base directories
- run one dataset against each knowledge base
- save predictions and summaries
- compute cross-strategy comparison outputs
- write a markdown report

This file should orchestrate the experiment, not contain all lower-level logic inline.

### Knowledge base ingestion support

#### `knowledge_base.py`

This file should gain one ingestion path for registry-backed documents.

The current `upload_by_str(...)` path is appropriate for ad hoc UI uploads, but it is not appropriate for chunking experiments because it hardcodes:

- `source_id = "upload::<filename>"`
- `doc_type = "untyped"`

The new experiment-facing ingestion path should accept explicit `source_metadata` so the experiment can ingest cleaned registry documents with their true:

- `source`
- `source_id`
- `doc_type`
- `create_time`
- `operator`

This keeps the existing upload behavior intact while making evaluation ingestion trustworthy.

### Retrieval inspection support

#### `rag.py`

The current baseline runner only stores generated answers and an empty `retrieved_context` placeholder.

For chunking comparison, the runner needs a lightweight evaluation-facing method that returns:

- generated answer
- retrieved documents or normalized retrieval rows
- retrieval metadata needed for comparison

At minimum, each retrieved row should expose:

- `source_id`
- `doc_type`
- `locator`
- `chunk_strategy`
- retrieved text or a short content field

This should be implemented as an additive evaluation helper rather than a broad refactor of the main chat chain.

### Existing baseline runner boundary

#### `eval_ragas.py`

This file should remain the baseline evaluation runner. It should not absorb the new chunking experiment.

If a small amount of reusable helper logic can be shared with the new experiment, that is fine, but `eval_chunking.py` should remain the dedicated experiment boundary.

### Repository usage guidance

#### `README.md`

The README should gain a stable navigation section that distinguishes:

- main engineering/runtime entrypoints
- experiment/evaluation entrypoints
- datasets and registries
- result directories
- where new experiment artifacts belong

#### `docs/repo_guide.md`

Add one focused navigation document that explains which files are for running the product, which files are for running experiments, and where experiment outputs are stored.

This document should be maintained as new experiment scripts are added so the repository remains understandable.

## Data flow

The end-to-end experiment flow should be:

1. Load `data/evaluation/shared/source_registry.json`.
2. For each source, load the corresponding cleaned markdown file.
3. Build knowledge base A with `chunking_strategy="baseline"`.
4. Build knowledge base B with `chunking_strategy="doc_type_aware"`.
5. Run the same evaluation dataset against both knowledge bases.
6. Capture answer output and retrieval metadata for every sample.
7. Compare the two runs using the dataset evidence and sample metadata.
8. Save structured outputs and one markdown report.

In short:

`source registry + cleaned markdown -> two isolated stores -> same dataset -> two prediction sets -> comparison summaries -> saved report`

## Result layout

Each run should write to a unique directory:

`results/chunking_eval/<run_id>/`

The run directory should contain:

### Per-strategy outputs

- `baseline/predictions.json`
- `baseline/metrics.json`
- `doc_type_aware/predictions.json`
- `doc_type_aware/metrics.json`

### Comparison outputs

- `comparison/summary.json`
- `comparison/by_doc_type.json`
- `comparison/by_source_id.json`
- `comparison/error_cases.json`

### Human-readable output

- `report.md`

The `run_id` should include enough context to avoid accidental overwrite, such as dataset name plus timestamp.

## Comparison rules

The comparison layer should focus on evidence retrieval and answer availability first.

### Per-sample prediction record

Each prediction row should include at least:

- sample ID
- question
- reference answer
- generated answer
- sample metadata
- normalized retrieved rows

### Retrieved row structure

Each retrieved row should include at least:

- `source_id`
- `doc_type`
- `locator`
- `chunk_strategy`
- content text or excerpt

### Summary metrics

Per-strategy metrics should include at least:

- sample count
- answered count
- answered ratio
- retrieved row count or context-hit-style summary
- evidence source hit count
- evidence source hit ratio
- evidence locator hit count
- evidence locator hit ratio

### Grouped comparison outputs

The comparison should aggregate differences by:

- `doc_type`
- `source_id`

This makes the experiment useful for chunking ablations, not just for one overall number.

### Error case output

`comparison/error_cases.json` should collect samples that are most useful for manual review, including:

- answer missing in one or both strategies
- evidence `source_id` not retrieved
- evidence `locator` not retrieved
- large retrieval difference between strategies

## Testing strategy

The tests should protect experiment contracts and comparison behavior.

### New or expanded tests

The implementation should cover:

- result directory generation
- prediction row shaping for chunking evaluation
- evidence hit detection by `source_id`
- evidence hit detection by `locator`
- grouped summaries by `doc_type`
- grouped summaries by `source_id`
- error-case selection
- markdown report generation inputs

### Integration-style coverage

At least one integration-oriented test should mock the two strategy runs and verify that the comparison outputs and report are written to the expected paths.

### Real execution verification

In addition to tests, the implementation should run at least one real evaluation comparison and save the resulting artifacts in the repository.

## Report design

`report.md` should be readable without opening the JSON files.

It should include:

1. run metadata
2. which dataset was used
3. where the two stores were built
4. overall summary comparison
5. comparison by `doc_type`
6. notable source-level differences
7. highlighted error cases
8. a short conclusion about whether `doc_type_aware` appears better, worse, or mixed on the current data

The report is for human review and should summarize the saved JSON outputs rather than inventing separate metrics.

## Repository navigation guidance

This iteration should explicitly improve repository usability.

The README and `docs/repo_guide.md` should define a simple separation such as:

- **Engineering/runtime files**: app/UI entrypoints, core RAG services, chunking/knowledge-base modules, config
- **Experiment/evaluation files**: `eval_ragas.py`, `eval_llm_judge.py`, `eval_chunking.py`, evaluation datasets, comparison outputs
- **Generated artifacts**: `results/...`

The goal is not to create a large documentation system. The goal is to make it obvious where to run the system, where to run experiments, and where experiment outputs are stored.

## Why this design is the right next step

The repository has already completed the first pass of provenance metadata and doc-type-aware chunking. The next high-value step is to measure whether those changes help.

This design matches the roadmap’s requirement that chunking and metadata improvements be evaluated before moving deeper into retrieval upgrades like hybrid retrieval or reranking. It also respects the architecture that now exists in the codebase: chunking behavior is configurable, provenance metadata is available, and the missing piece is a trustworthy comparison loop built on real source metadata rather than ad hoc uploads.
