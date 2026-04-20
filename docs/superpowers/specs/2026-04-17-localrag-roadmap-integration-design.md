# LocalRAG roadmap integration design

## Goal

Integrate the most transferable ideas from RAGFlow into the existing LocalRAG iteration plan without replacing the repo’s current direction. Preserve the current core strategy — evaluation first, then data, then retrieval, then model tuning — while making the roadmap more executable and retrieval-focused.

## Design summary

The roadmap should keep its current version structure (`v1.0` through `v1.4`) and absorb a focused subset of RAGFlow-inspired capabilities:

1. **Document-type-aware chunking** enters at `v1.1` as a data-layer capability.
2. **Chunk provenance metadata** becomes a required invariant of the ingestion pipeline.
3. **Hybrid retrieval** remains the centerpiece of `v1.2`.
4. **Retrieval inspection / debugging** becomes a first-class `v1.2` deliverable instead of an implicit debugging task.
5. **Knowledge-base-level embedding consistency** is added as a retrieval-layer rule.
6. **Parent-child chunking** is deferred to `v1.4` as an optional enhancement, not part of the main line.

This integration intentionally does **not** import RAGFlow’s full platform scope. It borrows the parts with the best payoff for a local-first, evaluation-driven repo: retrieval ergonomics, source traceability, and document-structure-aware ingestion.

## What changes in the roadmap

### Version structure

The roadmap keeps the same macro sequence:
- `v1.0 Baseline` — evaluation framework and benchmark datasets
- `v1.1 Data layer` — cleaned sources, registry, chunking, metadata
- `v1.2 Retrieval layer` — embedding upgrade, vector store upgrade, hybrid retrieval, retrieval inspection, reranking
- `v1.3 Model layer` — conditional QLoRA only after retrieval stabilizes
- `v1.4 Engineering enhancements` — UI, deployment, performance, optional advanced chunking

The main change is that `v1.1` and `v1.2` become more explicit about the retrieval-oriented infrastructure they are preparing.

### v1.1 data layer integration

`v1.1` should no longer describe chunking as one generic step. It should explicitly separate:

- a **baseline chunking** strategy used as a control
- a **document-type-aware chunking** strategy used as an experimental upgrade

The initial document-type-aware policy should be:

- **Apollo official docs** → split on chapter, section, and module-description boundaries
- **Standards / regulations** → split on clause, definition, and list boundaries
- **Papers / technical reports** → split on abstract, method, experiment, conclusion, and other structural boundaries

This capability depends on the source-cleaning and registry work already outlined elsewhere in the repo. In practice, the insertion point is directly after cleaned-source generation and source registration: cleaned source files and stable source metadata provide the basis for choosing chunk policies by source type.

### v1.2 retrieval layer integration

`v1.2` should become the first explicit retrieval-ablation phase.

The ablation order should be written into the roadmap as:
1. baseline metadata/chunking
2. document-type-aware chunking
3. hybrid retrieval
4. retrieval inspection / debugging
5. reranker
6. optional HyDE
7. optional hierarchical index

The purpose of this order is to avoid changing too many variables at once. The roadmap should state that each retrieval change is measured on the same Gold Set and Synthetic Set.

## Required invariants

### Chunk provenance

Every chunk produced after `v1.1` should preserve enough source metadata to support error analysis and citation-ready retrieval debugging. The minimum recommended fields are:

- `source_id`
- `doc_type`
- page number and/or section locator
- `chunk_order`
- `chunk_strategy`

This is important both for evaluation and for later UI/inspection work. It is one of the most valuable ideas to borrow from RAGFlow because it improves trust and debugging without requiring platform-scale complexity.

### Knowledge-base embedding consistency

The roadmap should add a retrieval rule that a single knowledge base should not silently mix multiple embedding spaces. The practical outcome is that embedding configuration is fixed at the knowledge-base level, so retrieval comparisons remain meaningful and ingestion stays reproducible.

This belongs in `v1.2`, because that is the stage where the roadmap already plans to switch embeddings and vector stores.

## Retrieval inspection design

A new `v1.2` deliverable should be added: **retrieval inspection / debugging**.

Its purpose is to expose retrieval internals during experimentation. The inspection view or CLI output should show at least:

- original query
- retrieved chunks
- source document identity
- chunk strategy used to produce each chunk
- fusion score and, when available, rerank score

This is not just a debugging convenience. It is part of the evaluation workflow. The roadmap should treat inspection as a tool for understanding why a retrieval change helped or failed, instead of relying only on final-answer quality.

## Deferred capability

### Parent-child chunking

Parent-child chunking is worth considering, but it should remain outside the main line until the simpler retrieval gains have been measured.

The design decision is:
- do **not** place parent-child chunking in `v1.1`
- do **not** require it for `v1.2` success
- place it in `v1.4` as an optional enhancement if earlier retrieval gains have stabilized

This keeps ingestion complexity under control while still preserving a path to a stronger retrieval design later.

## Recommended roadmap wording changes

The roadmap rewrite should reflect these decisions:

- `v1.1` explicitly includes `source_registry`, baseline chunking, and document-type-aware chunking.
- `v1.2` explicitly includes hybrid retrieval, retrieval inspection, reranking, and knowledge-base-level embedding consistency.
- the technical decisions section gains dedicated subsections for:
  - stable data inputs
  - document-type-aware chunking
  - retrieval observability
- the architecture section adds:
  - document parsing and document-type-aware chunking
  - retrieval inspection / debugging
  - source registry in the storage/data layer
- the weekly task list adds retrieval inspection and provenance metadata as concrete deliverables.

## Out of scope

This design intentionally does not add:

- RAGFlow-style multi-tenant platform abstractions
- workflow canvases or pipeline graph orchestration
- OCR-heavy multimodal ingestion as a main-line requirement
- advanced knowledge graph retrieval
- enterprise UI breadth

These are excluded because they would dilute the repo’s strongest direction: proving retrieval quality with disciplined evaluation.

## Why this is the right integration

This design preserves the strongest existing decisions in LocalRAG:
- evaluation first
- source quality before retrieval sophistication
- retrieval before model fine-tuning
- strict control over optional complexity

At the same time, it imports the most useful practical lessons from RAGFlow:
- chunking should reflect document structure
- retrieval systems need observability, not just end-task scores
- provenance is a core product/debugging feature
- hybrid retrieval is a main-line capability, not a side experiment

The result is a roadmap that is still small enough to execute, but much stronger as an engineering story and as a retrieval-focused project.
