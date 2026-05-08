import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings as config
from config.runtime_keys import load_runtime_config
from config.provider_factory import build_embedding_model
from core.hybrid_retriever import HybridRetriever
from eval.eval_hybrid import _build_hybrid_retriever
from eval.eval_chunking import load_dataset


def inspect_query(
    retriever: HybridRetriever,
    query: str,
    *,
    top_k: int = 5,
) -> dict[str, Any]:
    all_scores = retriever.retrieve_all_scores(query)

    def _format_results(results: list, label: str) -> list[dict]:
        return [
            {
                "rank": i + 1,
                "score": round(score, 4),
                "source_id": doc.metadata.get("source_id", ""),
                "doc_type": doc.metadata.get("doc_type", ""),
                "chunk_strategy": doc.metadata.get("chunk_strategy", ""),
                "locator": doc.metadata.get("locator", ""),
                "content_preview": doc.page_content[:200],
            }
            for i, (doc, score) in enumerate(results[:top_k])
        ]

    return {
        "query": query,
        "dense_results": _format_results(all_scores["dense"], "dense"),
        "sparse_results": _format_results(all_scores["sparse"], "sparse"),
        "merged_results": _format_results(all_scores["merged"], "merged"),
    }


def render_inspection_markdown(inspection: dict[str, Any]) -> str:
    lines = [
        f"# Retrieval Inspection",
        "",
        f"**Query**: {inspection['query']}",
        "",
        "## Merged (Hybrid) Results",
        "",
    ]

    for r in inspection["merged_results"]:
        lines.append(f"### [{r['rank']}] score={r['score']}")
        lines.append(f"- source: `{r['source_id']}` | doc_type: `{r['doc_type']}` | strategy: `{r['chunk_strategy']}`")
        lines.append(f"- content: {r['content_preview']}...")
        lines.append("")

    lines.extend([
        "## Dense-only Results",
        "",
    ])
    for r in inspection["dense_results"][:3]:
        lines.append(f"- [{r['rank']}] score={r['score']} source=`{r['source_id']}` {r['content_preview'][:80]}...")

    lines.extend(["", "## Sparse-only Results", ""])
    for r in inspection["sparse_results"][:3]:
        lines.append(f"- [{r['rank']}] score={r['score']} source=`{r['source_id']}` {r['content_preview'][:80]}...")

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run retrieval inspection")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--store-dir", required=True, type=Path)
    parser.add_argument("--out-dir", default=Path("results/inspection"), type=Path)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--sample-ids", nargs="*", help="Specific sample IDs to inspect")
    args = parser.parse_args()

    load_runtime_config()
    dataset = load_dataset(args.dataset)
    retriever = _build_hybrid_retriever(args.store_dir, alpha=args.alpha, final_top_k=config.similarity_top_k)

    if args.sample_ids:
        samples = [s for s in dataset if s["id"] in args.sample_ids]
    else:
        samples = dataset[:5]

    from datetime import datetime
    run_id = f"inspection-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    out_dir = args.out_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    inspections = []
    for sample in samples:
        inspection = inspect_query(retriever, sample["question"])
        inspection["sample_id"] = sample["id"]
        inspection["reference_answer"] = sample.get("reference_answer", "")
        inspection["evidence"] = sample.get("evidence", [])
        inspections.append(inspection)

        md = render_inspection_markdown(inspection)
        (out_dir / f"{sample['id']}.md").write_text(md, encoding="utf-8")

    import json
    (out_dir / "inspections.json").write_text(
        json.dumps(inspections, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Inspection results written to {out_dir}")
    print(f"Inspected {len(inspections)} samples")


if __name__ == "__main__":
    main()
