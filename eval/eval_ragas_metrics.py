"""Evaluate RAG predictions using Ragas standard metrics.

Metrics: faithfulness, answer_relevancy, context_precision, context_recall.

Usage:
    python eval/eval_ragas_metrics.py \
        --predictions results/ragas_eval/predictions.json \
        --out-dir results/ragas_eval
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.runtime_keys import load_runtime_config


def load_predictions(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "predictions" in data:
        return data["predictions"]
    if isinstance(data, list):
        return data
    raise ValueError(f"Unexpected predictions format: {type(data)}")


def build_ragas_samples(predictions: list[dict[str, Any]]) -> list:
    from ragas import SingleTurnSample

    samples = []
    for pred in predictions:
        answer = pred.get("answer", "").strip()
        if not answer:
            continue

        # Build contexts list from retrieved_rows (preferred) or retrieved_context (fallback)
        rows = pred.get("retrieved_rows", [])
        if rows:
            contexts = [row["content"] for row in rows if row.get("content")]
        elif pred.get("retrieved_context"):
            contexts = [c for c in pred["retrieved_context"].split("\n") if c.strip()]
        else:
            contexts = []

        ground_truth = pred.get("reference_answer", "")

        samples.append(SingleTurnSample(
            user_input=pred["question"],
            response=answer,
            retrieved_contexts=contexts,
            reference=ground_truth,
        ))

    return samples


def init_evaluator_llm(config):
    from langchain_openai import ChatOpenAI
    from ragas.llms import LangchainLLMWrapper

    llm = ChatOpenAI(
        model=config.chat_model_name,
        api_key=config.api_key,
        base_url=config.base_url,
        temperature=0,
        extra_body={"enable_thinking": False},
        max_retries=10,
    )
    return LangchainLLMWrapper(llm)


def init_evaluator_embeddings():
    from langchain_core.embeddings import Embeddings
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("BAAI/bge-m3", local_files_only=True)

    class LocalBgeEmbeddings(Embeddings):
        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            embeddings = model.encode(texts, normalize_embeddings=True)
            return [e.tolist() for e in embeddings]

        def embed_query(self, text: str) -> list[float]:
            embedding = model.encode([text], normalize_embeddings=True)
            return embedding[0].tolist()

    return LangchainEmbeddingsWrapper(LocalBgeEmbeddings())


def run_ragas_evaluation(predictions_path: Path, out_dir: Path, eval_model: str | None = None, run_metrics: list[str] | None = None) -> dict[str, Any]:
    from ragas import EvaluationDataset, evaluate
    from ragas.metrics import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
    from ragas.run_config import RunConfig

    config = load_runtime_config()
    if eval_model:
        config = type(config)(**{**config.__dict__, "chat_model_name": eval_model})
    predictions = load_predictions(predictions_path)

    print(f"Loaded {len(predictions)} predictions from {predictions_path}")

    samples = build_ragas_samples(predictions)
    print(f"Built {len(samples)} Ragas samples (skipped {len(predictions) - len(samples)} empty answers)")

    if not samples:
        print("No valid samples. Exiting.")
        return {}

    out_dir.mkdir(parents=True, exist_ok=True)
    run_config = RunConfig(max_workers=3, max_retries=10, max_wait=120, timeout=180)

    evaluator_llm = init_evaluator_llm(config)
    evaluator_embeddings = init_evaluator_embeddings()

    # Run each metric separately and save incrementally
    all_metric_defs = [
        ("faithfulness", Faithfulness(llm=evaluator_llm)),
        ("answer_relevancy", AnswerRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)),
        ("context_precision", ContextPrecision(llm=evaluator_llm)),
        ("context_recall", ContextRecall(llm=evaluator_llm)),
    ]
    if run_metrics:
        metric_defs = [(n, m) for n, m in all_metric_defs if n in run_metrics]
    else:
        metric_defs = all_metric_defs

    # Load existing scores if resuming
    all_scores = {}
    existing_scores_path = out_dir / "ragas_scores.json"
    if existing_scores_path.exists():
        existing = json.loads(existing_scores_path.read_text(encoding="utf-8"))
        for metric_name in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
            vals = [s.get(metric_name) for s in existing if metric_name in s and s[metric_name] is not None]
            if vals and not all(isinstance(v, float) and v != v for v in vals):  # not all NaN
                all_scores[metric_name] = vals
        print(f"Loaded existing scores for: {list(all_scores.keys())}")

    for metric_name, metric in metric_defs:
        print(f"\n--- Running {metric_name} ({metric_defs.index((metric_name, metric))+1}/{len(metric_defs)}) ---")
        dataset = EvaluationDataset(samples=samples)
        try:
            result = evaluate(dataset=dataset, metrics=[metric], run_config=run_config)
            scores_df = result.to_pandas()
            metric_scores = scores_df[metric_name].tolist()
            all_scores[metric_name] = metric_scores
            mean_score = round(float(scores_df[metric_name].mean()), 4)
            print(f"  {metric_name}: {mean_score} (saved)")

            # Save partial results after each metric
            partial_summary = {k: round(float(sum(v)/len(v)), 4) for k, v in all_scores.items()}
            partial_summary["sample_count"] = len(samples)
            (out_dir / "ragas_summary.json").write_text(
                json.dumps(partial_summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as e:
            print(f"  {metric_name} FAILED: {e}")
            all_scores[metric_name] = [float("nan")] * len(samples)

    # Build final per-sample scores
    per_sample = []
    for i, pred in enumerate(predictions[:len(samples)]):
        row = {"id": pred.get("id", f"sample-{i}")}
        for metric_name in all_scores:
            row[metric_name] = all_scores[metric_name][i] if i < len(all_scores[metric_name]) else float("nan")
        per_sample.append(row)

    summary = {k: round(float(sum(v)/len(v)), 4) for k, v in all_scores.items() if not all(float("nan") == x for x in v)}
    summary["sample_count"] = len(samples)

    # Write final outputs
    (out_dir / "ragas_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "ragas_scores.json").write_text(
        json.dumps(per_sample, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "manifest.json").write_text(
        json.dumps({
            "pipeline": "ragas_eval",
            "contract_version": "v1.1",
            "run_id": f"ragas-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "predictions_path": str(predictions_path),
            "metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"],
            "provider": config.provider,
            "chat_model_name": config.chat_model_name,
            "eval_model": eval_model or config.chat_model_name,
        }, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG predictions with Ragas metrics")
    parser.add_argument("--predictions", required=True, type=Path, help="Path to predictions.json")
    parser.add_argument("--out-dir", default=Path("results/ragas_eval"), type=Path)
    parser.add_argument("--eval-model", default=None, help="Override model for Ragas evaluator LLM")
    parser.add_argument("--metrics", default=None, nargs="+", help="Run only specific metrics (e.g. context_precision context_recall)")
    args = parser.parse_args()

    summary = run_ragas_evaluation(args.predictions, args.out_dir, eval_model=args.eval_model, run_metrics=args.metrics)

    if summary:
        print(f"\n{'='*50}")
        print("Ragas Evaluation Results:")
        print(f"  faithfulness:       {summary['faithfulness']:.4f}")
        print(f"  answer_relevancy:   {summary['answer_relevancy']:.4f}")
        print(f"  context_precision:  {summary['context_precision']:.4f}")
        print(f"  context_recall:     {summary['context_recall']:.4f}")
        print(f"  sample_count:       {summary['sample_count']}")
        print(f"{'='*50}")


if __name__ == "__main__":
    main()
