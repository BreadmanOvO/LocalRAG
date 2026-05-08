"""Sparse-only (BM25) comparison across chunking stores.

Controls: same dataset, same top-k.
Variable: chunking strategy (baseline vs doc_type_aware).

No embedding API needed - BM25 works on raw text only.
"""
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if tuple(map(int, sqlite3.sqlite_version.split("."))) < (3, 35, 0):
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3

from langchain_chroma import Chroma
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from config import settings as config
from eval.eval_ragas import load_dataset, write_json
from eval.eval_chunking import summarize_chunking_predictions


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def build_bm25_from_store(store_path: Path):
    chroma = Chroma(
        collection_name=config.collection_name,
        embedding_function=None,
        persist_directory=str(store_path),
    )
    collection = chroma._collection
    result = collection.get(include=["documents", "metadatas"])
    docs = [
        Document(page_content=text, metadata=meta or {})
        for text, meta in zip(result["documents"], result["metadatas"])
    ]
    tokenized = [_tokenize(doc.page_content) for doc in docs]
    bm25 = BM25Okapi(tokenized)
    return bm25, docs


def sparse_search(bm25, docs, query: str, top_k: int) -> list[dict]:
    scores = bm25.get_scores(_tokenize(query))
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    max_score = max(scores[i] for i in top_indices) if top_indices else 1.0
    results = []
    for rank, idx in enumerate(top_indices, 1):
        doc = docs[idx]
        results.append({
            "rank": rank,
            "score": round(float(scores[idx] / max_score) if max_score > 0 else 0.0, 4),
            "source_id": doc.metadata.get("source_id", ""),
            "doc_type": doc.metadata.get("doc_type", ""),
            "locator": doc.metadata.get("locator", ""),
            "chunk_strategy": doc.metadata.get("chunk_strategy", ""),
            "content": doc.page_content,
        })
    return results


def run_sparse_eval(dataset, store_path: Path, top_k: int = 5):
    bm25, docs = build_bm25_from_store(store_path)
    predictions = []
    for sample in dataset:
        results = sparse_search(bm25, docs, sample["question"], top_k)
        predictions.append({
            "id": sample["id"],
            "question": sample["question"],
            "reference_answer": sample.get("reference_answer", ""),
            "answer": "",
            "retrieved_context": "\n".join(r["content"] for r in results),
            "retrieved_rows": results,
            "evidence": sample.get("evidence", []),
            "metadata": sample.get("metadata", {}),
        })
    return predictions


def main():
    dataset_path = Path("data/evaluation/gold/gold_set.json")
    stores_dir = Path("results/chunking_eval/stores/gold_set-20260505-104419")

    dataset = load_dataset(dataset_path)
    top_k = config.similarity_top_k

    results = {}
    for strategy in ["baseline", "doc_type_aware"]:
        store_path = stores_dir / strategy
        if not store_path.exists():
            print(f"Store not found: {store_path}")
            continue
        print(f"Running sparse eval on {strategy} store...")
        predictions = run_sparse_eval(dataset, store_path, top_k=top_k)
        metrics = summarize_chunking_predictions(predictions)
        results[strategy] = metrics
        print(f"  {strategy}: source_hit={metrics['evidence_source_hit_ratio']}, "
              f"locator_hit={metrics['evidence_locator_hit_ratio']}")

    comparison = {
        "experiment": "sparse_only_chunking_comparison",
        "description": "BM25 sparse on different chunking stores",
        "top_k": top_k,
        "results": results,
    }

    out_dir = Path("results/sparse_compare") / f"compare-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "comparison.json", comparison)
    print(f"\nResults written to {out_dir}")
    print(json.dumps(comparison, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
