"""Reranker evaluation: hybrid retrieval + reranker vs hybrid only.

Controls: same embedding, same chunking store, same top-k.
Variable: with/without reranker (cross-encoder or LLM-based).
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
from config.provider_factory import build_chat_model, build_embedding_model
from core.hybrid_retriever import HybridRetriever
from core.reranker import CrossEncoderReranker, LLMReranker
from core.rag import _format_documents
from eval.eval_chunking import summarize_chunking_predictions
from eval.eval_hybrid import _build_hybrid_retriever
from eval.eval_ragas import load_dataset, write_json


def run_eval_with_reranker(
    dataset: list[dict[str, Any]],
    store_path: Path,
    alpha: float,
    reranker: CrossEncoderReranker | LLMReranker,
    *,
    retrieve_top_k: int = 20,
    final_top_k: int = 5,
) -> list[dict[str, Any]]:
    retriever = _build_hybrid_retriever(store_path, alpha=alpha, final_top_k=retrieve_top_k)
    runtime_config = load_runtime_config()
    chat_model = build_chat_model(runtime_config)

    from langchain_core.prompts import ChatPromptTemplate
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "以我提供的已知参考资料为主，简洁和专业的回答用户问题。参考资料：{context}。"),
        ("user", "请回答用户提问：{question}")
    ])
    chain = prompt_template | chat_model | (lambda x: x.content if hasattr(x, "content") else str(x))

    predictions = []
    for sample in dataset:
        question = str(sample["question"])

        # Step 1: hybrid retrieval (top-20 candidates)
        scored_all = retriever.retrieve_all_scores(question)
        candidates = scored_all["merged"]  # top-20 merged results

        # Step 2: rerank
        reranked = reranker.rerank(question, candidates, top_k=final_top_k)
        docs = [doc for doc, _ in reranked]

        # Step 3: generate answer
        context_str = _format_documents(docs)
        answer = chain.invoke({"question": question, "context": context_str})

        scored_rows = [
            {"source_id": d.metadata.get("source_id", ""), "doc_type": d.metadata.get("doc_type", ""),
             "locator": d.metadata.get("locator", ""), "chunk_strategy": d.metadata.get("chunk_strategy", ""),
             "content": d.page_content, "score": s, "rank": i}
            for i, (d, s) in enumerate(reranked, start=1)
        ]

        predictions.append({
            "id": sample["id"],
            "question": sample["question"],
            "reference_answer": sample["reference_answer"],
            "answer": answer,
            "retrieved_context": "\n".join(d.page_content for d in docs),
            "retrieved_rows": scored_rows,
            "evidence": sample.get("evidence", []),
            "metadata": sample.get("metadata", {}),
        })

    return predictions


def run_eval_without_reranker(
    dataset: list[dict[str, Any]],
    store_path: Path,
    alpha: float,
    *,
    final_top_k: int = 5,
) -> list[dict[str, Any]]:
    retriever = _build_hybrid_retriever(store_path, alpha=alpha, final_top_k=final_top_k)
    runtime_config = load_runtime_config()
    chat_model = build_chat_model(runtime_config)

    from langchain_core.prompts import ChatPromptTemplate
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "以我提供的已知参考资料为主，简洁和专业的回答用户问题。参考资料：{context}。"),
        ("user", "请回答用户提问：{question}")
    ])
    chain = prompt_template | chat_model | (lambda x: x.content if hasattr(x, "content") else str(x))

    predictions = []
    for sample in dataset:
        question = str(sample["question"])
        scored_all = retriever.retrieve_all_scores(question)
        merged = scored_all["merged"]
        docs = [doc for doc, _ in merged]

        context_str = _format_documents(docs)
        answer = chain.invoke({"question": question, "context": context_str})

        scored_rows = [
            {"source_id": d.metadata.get("source_id", ""), "doc_type": d.metadata.get("doc_type", ""),
             "locator": d.metadata.get("locator", ""), "chunk_strategy": d.metadata.get("chunk_strategy", ""),
             "content": d.page_content, "score": s, "rank": i}
            for i, (d, s) in enumerate(merged, start=1)
        ]

        predictions.append({
            "id": sample["id"],
            "question": sample["question"],
            "reference_answer": sample["reference_answer"],
            "answer": answer,
            "retrieved_context": "\n".join(d.page_content for d in docs),
            "retrieved_rows": scored_rows,
            "evidence": sample.get("evidence", []),
            "metadata": sample.get("metadata", {}),
        })

    return predictions


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate hybrid + reranker vs hybrid only")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--store-dir", required=True, type=Path)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--retrieve-top-k", type=int, default=20, help="Candidates from hybrid retrieval")
    parser.add_argument("--final-top-k", type=int, default=config.similarity_top_k)
    parser.add_argument("--out-dir", default=Path("results/reranker_eval"), type=Path)
    parser.add_argument(
        "--reranker", choices=["cross-encoder", "llm"], default="cross-encoder",
        help="Reranker type: cross-encoder (local, fast) or llm (API-based, slow)",
    )
    parser.add_argument(
        "--reranker-model", default="BAAI/bge-reranker-base",
        help="Cross-encoder model name (only used with --reranker cross-encoder)",
    )
    args = parser.parse_args()

    load_runtime_config()
    dataset = load_dataset(args.dataset)

    if args.reranker == "cross-encoder":
        reranker = CrossEncoderReranker(model_name=args.reranker_model)
    else:
        chat_model = build_chat_model(load_runtime_config())
        reranker = LLMReranker(chat_model)

    print("Running hybrid-only baseline...")
    baseline_preds = run_eval_without_reranker(
        dataset, args.store_dir, alpha=args.alpha, final_top_k=args.final_top_k,
    )

    print("Running hybrid + reranker...")
    reranker_preds = run_eval_with_reranker(
        dataset, args.store_dir, alpha=args.alpha, reranker=reranker,
        retrieve_top_k=args.retrieve_top_k, final_top_k=args.final_top_k,
    )

    baseline_metrics = summarize_chunking_predictions(baseline_preds)
    reranker_metrics = summarize_chunking_predictions(reranker_preds)

    run_id = f"gold_set-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    run_dir = args.out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    write_json(run_dir / "hybrid_only" / "predictions.json", baseline_preds)
    write_json(run_dir / "hybrid_only" / "metrics.json", baseline_metrics)
    write_json(run_dir / "hybrid_reranker" / "predictions.json", reranker_preds)
    write_json(run_dir / "hybrid_reranker" / "metrics.json", reranker_metrics)

    summary = {
        "run_id": run_id,
        "reranker_type": args.reranker,
        "reranker_model": args.reranker_model if args.reranker == "cross-encoder" else "llm",
        "alpha": args.alpha,
        "retrieve_top_k": args.retrieve_top_k,
        "final_top_k": args.final_top_k,
        "hybrid_only": baseline_metrics,
        "hybrid_reranker": reranker_metrics,
    }
    write_json(run_dir / "comparison" / "summary.json", summary)
    write_json(run_dir / "manifest.json", {
        "contract_version": "v1.1",
        "pipeline": "reranker_eval",
        "run_id": run_id,
        "reranker_type": args.reranker,
        "reranker_model": args.reranker_model if args.reranker == "cross-encoder" else "llm",
        "alpha": args.alpha,
        "store_dir": str(args.store_dir),
        "retrieve_top_k": args.retrieve_top_k,
        "final_top_k": args.final_top_k,
    })

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
