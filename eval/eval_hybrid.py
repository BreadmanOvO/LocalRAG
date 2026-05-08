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
from config.provider_factory import build_embedding_model
from core.hybrid_retriever import HybridRetriever
from core.rag import RagService, _format_documents, _normalize_scored_rows
from eval.eval_chunking import (
    _build_prediction_record,
    _empty_summary,
    build_comparison_artifacts,
    load_dataset,
    render_chunking_report,
    summarize_chunking_predictions,
    write_chunking_run_artifacts,
)
from eval.eval_ragas import build_session_id, write_json

STRATEGY_DENSE = "dense_only"
STRATEGY_SPARSE = "sparse_only"
STRATEGY_HYBRID = "hybrid"


def _build_hybrid_retriever(store_path: Path, alpha: float, final_top_k: int) -> HybridRetriever:
    import sqlite3
    if tuple(map(int, sqlite3.sqlite_version.split("."))) < (3, 35, 0):
        import pysqlite3
        sys.modules["sqlite3"] = pysqlite3

    from langchain_chroma import Chroma

    runtime_config = load_runtime_config()
    embedder = build_embedding_model(runtime_config)
    chroma = Chroma(
        collection_name=config.collection_name,
        embedding_function=embedder,
        persist_directory=str(store_path),
    )
    return HybridRetriever(chroma, alpha=alpha, final_top_k=final_top_k)


def run_hybrid_evaluation(
    dataset: list[dict[str, Any]],
    store_path: Path,
    alpha: float,
    strategy: str,
) -> list[dict[str, Any]]:
    retriever = _build_hybrid_retriever(store_path, alpha=alpha, final_top_k=config.similarity_top_k)
    runtime_config = load_runtime_config()
    from config.provider_factory import build_chat_model
    chat_model = build_chat_model(runtime_config)
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "以我提供的已知参考资料为主，简洁和专业的回答用户问题。参考资料：{context}。"),
            ("user", "请回答用户提问：{question}")
        ]
    )
    chain = prompt_template | chat_model | (lambda x: x.content if hasattr(x, "content") else str(x))

    predictions = []
    for sample in dataset:
        question = str(sample["question"])

        if strategy == STRATEGY_DENSE:
            scored = retriever._dense_search(question, k=config.retrieval_debug_top_k)
            from core.hybrid_retriever import HybridRetriever as HR
            scored = HR._normalize_scores(scored)
            docs = [doc for doc, _ in scored[:config.similarity_top_k]]
        elif strategy == STRATEGY_SPARSE:
            scored = retriever._sparse_search(question, k=config.retrieval_debug_top_k)
            from core.hybrid_retriever import HybridRetriever as HR
            scored = HR._normalize_scores(scored)
            docs = [doc for doc, _ in scored[:config.similarity_top_k]]
        else:
            scored_all = retriever.retrieve_all_scores(question)
            scored = scored_all["merged"]
            docs = [doc for doc, _ in scored]

        context_str = _format_documents(docs)
        answer = chain.invoke({"question": question, "context": context_str})

        scored_rows = [
            {"source_id": d.metadata.get("source_id", ""), "doc_type": d.metadata.get("doc_type", ""),
             "locator": d.metadata.get("locator", ""), "chunk_strategy": d.metadata.get("chunk_strategy", ""),
             "content": d.page_content, "score": s, "rank": i}
            for i, (d, s) in enumerate(scored, start=1)
        ]

        predictions.append({
            "id": sample["id"],
            "question": sample["question"],
            "reference_answer": sample["reference_answer"],
            "answer": answer,
            "retrieved_context": "\n".join(d.page_content for d in docs),
            "retrieved_rows": scored_rows[:len(docs)],
            "retrieval_debug_candidates": scored_rows,
            "evidence": sample.get("evidence", []),
            "metadata": sample.get("metadata", {}),
        })

    return predictions


def build_run_id(dataset_path: Path) -> str:
    return f"{dataset_path.stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Run hybrid retrieval comparison")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--store-dir", required=True, type=Path, help="Chunking eval store directory (baseline)")
    parser.add_argument("--out-dir", default=Path("results/hybrid_eval"), type=Path)
    parser.add_argument("--alpha", type=float, default=0.7, help="Dense weight (1-alpha = sparse weight)")
    args = parser.parse_args()

    load_runtime_config()
    dataset = load_dataset(args.dataset)
    run_id = build_run_id(args.dataset)

    dense_predictions = run_hybrid_evaluation(dataset, args.store_dir, alpha=1.0, strategy=STRATEGY_DENSE)
    sparse_predictions = run_hybrid_evaluation(dataset, args.store_dir, alpha=0.0, strategy=STRATEGY_SPARSE)
    hybrid_predictions = run_hybrid_evaluation(dataset, args.store_dir, alpha=args.alpha, strategy=STRATEGY_HYBRID)

    dense_metrics = summarize_chunking_predictions(dense_predictions)
    sparse_metrics = summarize_chunking_predictions(sparse_predictions)
    hybrid_metrics = summarize_chunking_predictions(hybrid_predictions)

    run_dir = args.out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "dense_only" / "predictions.json", dense_predictions)
    write_json(run_dir / "dense_only" / "metrics.json", dense_metrics)
    write_json(run_dir / "sparse_only" / "predictions.json", sparse_predictions)
    write_json(run_dir / "sparse_only" / "metrics.json", sparse_metrics)
    write_json(run_dir / "hybrid" / "predictions.json", hybrid_predictions)
    write_json(run_dir / "hybrid" / "metrics.json", hybrid_metrics)

    summary = {
        "run_id": run_id,
        "alpha": args.alpha,
        "dense_only": dense_metrics,
        "sparse_only": sparse_metrics,
        "hybrid": hybrid_metrics,
    }
    write_json(run_dir / "comparison" / "summary.json", summary)

    write_json(run_dir / "manifest.json", {
        "contract_version": "v1.1",
        "pipeline": "hybrid_eval",
        "run_id": run_id,
        "alpha": args.alpha,
        "store_dir": str(args.store_dir),
    })

    report_lines = [
        f"# Hybrid retrieval evaluation: {run_id}",
        "",
        "## Run metadata",
        f"- Dataset: {args.dataset}",
        f"- Store: {args.store_dir}",
        f"- Alpha (dense weight): {args.alpha}",
        "",
        "## Overall summary",
        f"- dense_only source_hit_ratio: {dense_metrics['evidence_source_hit_ratio']}",
        f"- sparse_only source_hit_ratio: {sparse_metrics['evidence_source_hit_ratio']}",
        f"- hybrid source_hit_ratio: {hybrid_metrics['evidence_source_hit_ratio']}",
        f"- dense_only locator_hit_ratio: {dense_metrics['evidence_locator_hit_ratio']}",
        f"- sparse_only locator_hit_ratio: {sparse_metrics['evidence_locator_hit_ratio']}",
        f"- hybrid locator_hit_ratio: {hybrid_metrics['evidence_locator_hit_ratio']}",
    ]
    (run_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    main()
