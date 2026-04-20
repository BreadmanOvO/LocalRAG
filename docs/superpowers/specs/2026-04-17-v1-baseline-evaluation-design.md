# LocalRAG v1.0 baseline evaluation design

## Goal

Establish the minimum executable v1.0 evaluation baseline for LocalRAG on top of the existing simple RAG prototype. The purpose of this iteration is not to improve retrieval quality yet, but to create a runnable evaluation loop that later versions can reuse to prove gains.

## Current stage assessment

The repository is currently in a mixed state:

- The roadmap and README define the project as being in `v1.0 Baseline`.
- The codebase already contains a runnable prototype with Streamlit UI, file upload, Chroma, DashScope embeddings, and Tongyi generation.
- This means the project is not purely in planning anymore. It is best described as: **an existing naive RAG prototype with the v1.0 evaluation baseline still missing**.

Because of that, the next development step should be to complete the evaluation baseline before starting the `v1.1` data-layer work or the `v1.2` retrieval-layer work.

## Scope

This design covers only the minimum executable v1.0 baseline.

### In scope

1. Create a small but valid Gold Set dataset file.
2. Create a small but valid Synthetic Set dataset file.
3. Add a shared schema validation module for evaluation records.
4. Add a minimal `eval_ragas.py` runner for loading a dataset, invoking the current baseline system, and writing output artifacts.
5. Add a minimal `eval_llm_judge.py` scaffold that produces comparison-shaped output.
6. Produce initial baseline result artifacts under `results/`.
7. Add tests that protect the file contracts and result structure.

### Explicitly out of scope for this iteration

These are deferred, not cancelled:

- `source_registry`, improved chunking, and metadata enrichment in `v1.1`
- `BGE-M3`, `Qdrant`, hybrid retrieval, retrieval inspection, and reranking in `v1.2`
- `QLoRA` in `v1.3`, only after retrieval gains stabilize
- `Chainlit`, deployment cleanup, and performance optimization in `v1.4`
- Full real Ragas metric integration in this iteration
- A real LLM-as-a-Judge implementation in this iteration

## Design summary

The v1.0 baseline should create a stable evaluation loop with four layers:

1. **Dataset layer** — stores evaluation samples in JSON files.
2. **Validation layer** — enforces a single shared record schema.
3. **Execution layer** — runs the current baseline system against a dataset and saves predictions and summary metrics.
4. **Comparison layer** — produces a minimal judge-format output so later versions can swap in a real judge without changing the artifact contract.

The main design decision is to optimize for **runnable structure first**, not metric sophistication. The first version only needs to prove that the repository can load evaluation data, run the baseline system, and persist reusable result files.

## File design

### Dataset files

#### `data/evaluation/gold/gold_set.json`

This file stores the manually curated Gold Set.

Its role is to provide the small, most trusted benchmark set. Each record should include:

- `id`
- `question`
- `reference_answer`
- `evidence`
- `metadata`

The first iteration only needs a minimum executable set, not the final 30–50 target. The file must still follow the final intended structure so that it can scale without redesign.

#### `data/evaluation/synthetic/synthetic_dataset.json`

This file stores the initial Synthetic Set.

Its role is to extend coverage beyond the Gold Set and provide the first regression-friendly batch dataset. The first version can stay small, but it should use the same schema as the Gold Set so all evaluation tooling stays consistent.

### Shared validation file

#### `data/evaluation/shared/eval_schema.py`

This module defines the shared record contract for evaluation datasets.

Its responsibilities are:

- validate one record
- validate a dataset collection
- reject missing fields
- reject empty required strings or empty evidence
- reject duplicate sample IDs

This file exists to prevent schema drift between datasets, runners, and future tooling.

### Evaluation runner

#### `eval_ragas.py`

Despite the name, the first version is a minimal baseline evaluation runner rather than a full Ragas implementation.

Its responsibilities are:

- load a dataset JSON file
- validate it through `eval_schema.py`
- invoke the current baseline RAG system for each question
- build normalized prediction records
- summarize simple execution metrics
- write `baseline_predictions.json`
- write `baseline_metrics.json`

The first version should focus on execution stability and artifact generation. Real Ragas metrics can be added later behind the same script boundary.

### Judge scaffold

#### `eval_llm_judge.py`

This file provides the minimum comparison-layer scaffold.

Its responsibilities are:

- load prediction output
- generate comparison rows with a stable result shape
- summarize win/loss/tie counts
- write `baseline_judge.json`

The first version can use self-comparison or another simplified method. The important part is to establish the output contract for later pairwise evaluation.

### Output artifacts

#### `results/baseline_predictions.json`

This stores per-sample baseline outputs.

Its role is to preserve the raw prediction-level record that later debugging and error analysis can inspect. It should include at least:

- sample ID
- question
- reference answer
- generated answer
- retrieved context placeholder or context text
- metadata

#### `results/baseline_metrics.json`

This stores the baseline summary metrics.

Its role is to provide the smallest reusable baseline summary for version-to-version comparison. In the first version, simple counts and ratios are enough.

#### `results/baseline_judge.json`

This stores the comparison result summary and rows.

Its role is to preserve the judge-shaped artifact contract for future pairwise evaluations.

### Tests

#### `test/test_eval_schema.py`

This test file protects the dataset contract.

It should verify:

- a valid record passes
- duplicate IDs fail
- the dataset files exist
- the dataset files load and validate

#### `test/test_eval_runners.py`

This test file protects the runner and judge contract.

It should verify:

- prediction summary fields are correct
- JSON writing creates parent directories
- prediction records contain required keys
- judge summaries contain the expected structure

## Execution flow

The minimum executable flow is:

1. Prepare the Gold Set and Synthetic Set files.
2. Validate dataset structure before execution.
3. Run the current baseline system on each sample.
4. Save per-sample predictions.
5. Compute simple summary metrics.
6. Save a minimal judge-format result.
7. Use tests to lock the file and output contracts.

In short:

`dataset json -> schema validate -> baseline predict -> predictions -> metrics -> judge`

## Component boundaries

### Dataset layer

The dataset files only store evaluation samples. They do not contain runtime logic.

### Validation layer

`eval_schema.py` is the only shared source of truth for record structure. Runners depend on it, instead of re-implementing parsing rules.

### Execution layer

`eval_ragas.py` is responsible for dataset loading, baseline invocation, prediction shaping, and summary generation. It does not handle judging.

### Comparison layer

`eval_llm_judge.py` is responsible for comparison-shaped output only. It is intentionally decoupled from prediction generation so the judge implementation can change later without rewriting the runner.

### Existing RAG integration

The current Streamlit-driven baseline should not be refactored for this iteration. Instead, the design should add one minimal offline-friendly entrypoint on top of the existing `RagService`, so evaluation scripts can ask one question at a time without routing through the UI.

## Error handling strategy

The first version should keep error handling narrow and explicit.

### Validation errors

Missing fields, empty required values, invalid evidence, and duplicate IDs should fail fast in `eval_schema.py`.

### File writing

The runner should ensure parent directories exist before writing JSON output.

### Baseline runtime errors

If the current baseline system throws during evaluation, the error should surface directly in the first version. This iteration is trying to reveal breakpoints, not hide them behind fallback logic.

## Testing strategy

The tests should verify infrastructure contracts, not model quality.

### What to test

- schema validation behavior
- dataset file presence and loadability
- runner summary behavior
- result file writing
- prediction record structure
- judge summary structure

### What not to test in this iteration

- answer quality
- retrieval quality
- real faithfulness metrics
- real pairwise judge quality

## Completion criteria

This v1.0 baseline is considered complete when:

1. `test/test_eval_schema.py` passes.
2. `test/test_eval_runners.py` passes.
3. `eval_ragas.py` runs and writes `results/baseline_predictions.json` and `results/baseline_metrics.json`.
4. `eval_llm_judge.py` runs and writes `results/baseline_judge.json`.
5. The repository now has a reusable baseline evaluation loop that later versions can improve without changing the overall artifact structure.

## Why this is the right next step

This design matches the roadmap’s stated sequencing: evaluation first, then data, then retrieval, then model tuning.

It also respects the actual state of the repository: there is already a naive runnable system, so the highest-value next step is not another prototype feature. The right step is to add measurement around the existing baseline so future changes in `v1.1` and `v1.2` can be defended with evidence instead of anecdotes.