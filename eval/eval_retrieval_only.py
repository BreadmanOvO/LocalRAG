"""Evaluate retrieval quality only (no answer generation).

This script evaluates whether the evidence source documents are retrieved
in the top-k results, without requiring a chat model for answer generation.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings as config
from config.runtime_keys import load_runtime_config
from eval.eval_hybrid import _build_hybrid_retriever
from eval.eval_ragas import load_dataset, write_json
from core.reranker import CrossEncoderReranker


def evaluate_retrieval(
    dataset: list[dict[str, Any]],
    store_path: Path,
    alpha: float,
    *,
    final_top_k: int = 5,
    use_reranker: bool = False,
    reranker_model: str = "BAAI/bge-reranker-base",
) -> dict[str, Any]:
    """Evaluate retrieval quality by checking if evidence sources are in top-k."""
    retriever = _build_hybrid_retriever(store_path, alpha=alpha, final_top_k=20)

    reranker = None
    if use_reranker:
        reranker = CrossEncoderReranker(model_name=reranker_model)

    results = []
    reciprocal_ranks = []

    for sample in dataset:
        question = str(sample["question"])
        evidence_source_ids = {e["source_id"] for e in sample.get("evidence", [])}

        # Retrieve
        scored_all = retriever.retrieve_all_scores(question)
        merged = scored_all["merged"]

        # Optionally rerank
        if reranker:
            reranked = reranker.rerank(question, merged, top_k=final_top_k)
            retrieved_docs = [(doc, score) for doc, score in reranked]
        else:
            retrieved_docs = merged[:final_top_k]

        # Find best rank of any evidence source
        best_rank = None
        for i, (doc, score) in enumerate(retrieved_docs):
            sid = doc.metadata.get("source_id", "")
            if sid in evidence_source_ids and best_rank is None:
                best_rank = i + 1  # 1-based rank

        # Check if evidence sources are in retrieved docs
        retrieved_source_ids = {doc.metadata.get("source_id", "") for doc, _ in retrieved_docs}
        hit = bool(evidence_source_ids & retrieved_source_ids)

        # Reciprocal rank for MRR
        rr = 1.0 / best_rank if best_rank else 0.0
        reciprocal_ranks.append(rr)

        results.append({
            "id": sample["id"],
            "question": question,
            "evidence_source_ids": list(evidence_source_ids),
            "retrieved_source_ids": list(retrieved_source_ids),
            "hit": hit,
            "best_rank": best_rank,
        })

    # Calculate metrics
    total = len(results)
    hit_count = sum(1 for r in results if r["hit"])
    hit_at_1 = sum(1 for r in results if r["best_rank"] is not None and r["best_rank"] <= 1)
    hit_at_3 = sum(1 for r in results if r["best_rank"] is not None and r["best_rank"] <= 3)
    hit_at_5 = sum(1 for r in results if r["best_rank"] is not None and r["best_rank"] <= 5)
    mrr = sum(reciprocal_ranks) / total if total > 0 else 0.0

    return {
        "sample_count": total,
        "hit_count": hit_count,
        "hit_ratio": hit_count / total if total > 0 else 0,
        "mrr": mrr,
        "hit_at_1": hit_at_1 / total if total > 0 else 0,
        "hit_at_3": hit_at_3 / total if total > 0 else 0,
        "hit_at_5": hit_at_5 / total if total > 0 else 0,
        "details": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate retrieval quality only")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--store-dir", required=True, type=Path)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--final-top-k", type=int, default=5)
    parser.add_argument("--use-reranker", action="store_true", help="Use cross-encoder reranker")
    parser.add_argument("--reranker-model", default="BAAI/bge-reranker-base")
    parser.add_argument("--out-dir", default=Path("results/retrieval_eval"), type=Path)
    args = parser.parse_args()

    load_runtime_config()
    dataset = load_dataset(args.dataset)

    print(f"Evaluating retrieval on {len(dataset)} questions...")
    print(f"  Store: {args.store_dir}")
    print(f"  Alpha: {args.alpha}")
    print(f"  Top-k: {args.final_top_k}")
    print(f"  Reranker: {args.use_reranker}")

    results = evaluate_retrieval(
        dataset, args.store_dir, alpha=args.alpha,
        final_top_k=args.final_top_k,
        use_reranker=args.use_reranker,
        reranker_model=args.reranker_model,
    )

    # Save results
    run_id = f"gold_set_100-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    run_dir = args.out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "results.json", results)
    write_json(run_dir / "manifest.json", {
        "contract_version": "v1.1",
        "pipeline": "retrieval_eval",
        "run_id": run_id,
        "alpha": args.alpha,
        "final_top_k": args.final_top_k,
        "use_reranker": args.use_reranker,
        "reranker_model": args.reranker_model if args.use_reranker else None,
        "store_dir": str(args.store_dir),
    })

    # Print summary
    print(f"\n{'='*50}")
    print(f"Results:")
    print(f"  Total questions: {results['sample_count']}")
    print(f"  Hit count: {results['hit_count']}")
    print(f"  Hit ratio (hit@{args.final_top_k}): {results['hit_ratio']:.3f}")
    print(f"  MRR: {results['mrr']:.3f}")
    print(f"  Hit@1: {results['hit_at_1']:.3f}")
    print(f"  Hit@3: {results['hit_at_3']:.3f}")
    print(f"  Hit@5: {results['hit_at_5']:.3f}")
    print(f"{'='*50}")

    # Print per-question details
    print("\nDetailed results:")
    for r in results["details"]:
        rank_str = f"rank={r['best_rank']}" if r['best_rank'] else "rank=miss"
        status = "✓" if r["hit"] else "✗"
        print(f"  {status} {r['id']}: {r['question'][:50]}... [{rank_str}]")
        if not r["hit"]:
            print(f"    Evidence: {r['evidence_source_ids']}")
            print(f"    Retrieved: {r['retrieved_source_ids']}")


if __name__ == "__main__":
    main()
