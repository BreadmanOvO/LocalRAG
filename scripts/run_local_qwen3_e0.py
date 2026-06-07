import argparse
import json
import os
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config import settings as config
from config.runtime_keys import RUNTIME_CONFIG_ENV_VAR, load_runtime_config
from eval.eval_ragas import (
    build_prediction_record,
    build_runtime_manifest_fields,
    build_session_id,
    load_dataset,
    summarize_predictions,
    write_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "runtime_local_qwen3_4b.example.json"
DEFAULT_DATASET_PATH = REPO_ROOT / "data" / "evaluation" / "gold" / "generation_eval_set.json"
DEFAULT_STORE_DIR = REPO_ROOT / "results" / "chunking_eval" / "stores" / "eval_set-20260522-071034" / "semantic"
DEFAULT_OUT_DIR = REPO_ROOT / "results" / "qwen3_base_eval"


def _now_run_id(dataset_path: Path, run_label: str = "qwen3-4b-base") -> str:
    return f"{dataset_path.stem}-{run_label}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def _memory_snapshot() -> dict[str, Any]:
    try:
        import torch

        if not torch.cuda.is_available():
            return {"cuda_available": False}
        free_bytes, total_bytes = torch.cuda.mem_get_info()
        return {
            "cuda_available": True,
            "gpu_name": torch.cuda.get_device_name(0),
            "memory_free_bytes": int(free_bytes),
            "memory_total_bytes": int(total_bytes),
            "memory_allocated_bytes": int(torch.cuda.memory_allocated()),
            "memory_reserved_bytes": int(torch.cuda.memory_reserved()),
            "max_memory_allocated_bytes": int(torch.cuda.max_memory_allocated()),
        }
    except Exception as exc:
        return {"cuda_available": False, "error": str(exc)}


def select_records(records: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    if limit is None or limit <= 0:
        return records
    return records[:limit]


@contextmanager
def local_runtime_context(
    *,
    runtime_config_path: Path,
    store_dir: Path,
    top_k: int,
    debug_top_k: int,
):
    if not runtime_config_path.exists():
        raise FileNotFoundError(f"runtime config does not exist: {runtime_config_path}")
    if not store_dir.exists():
        raise FileNotFoundError(f"store directory does not exist: {store_dir}")

    original_runtime_config = os.environ.get(RUNTIME_CONFIG_ENV_VAR)
    original_persist_directory = config.persist_directory
    original_top_k = config.similarity_top_k
    original_debug_top_k = config.retrieval_debug_top_k
    try:
        os.environ[RUNTIME_CONFIG_ENV_VAR] = str(runtime_config_path)
        config.persist_directory = str(store_dir)
        config.similarity_top_k = top_k
        config.retrieval_debug_top_k = debug_top_k
        yield
    finally:
        if original_runtime_config is None:
            os.environ.pop(RUNTIME_CONFIG_ENV_VAR, None)
        else:
            os.environ[RUNTIME_CONFIG_ENV_VAR] = original_runtime_config
        config.persist_directory = original_persist_directory
        config.similarity_top_k = original_top_k
        config.retrieval_debug_top_k = original_debug_top_k


def build_manifest(
    *,
    run_id: str,
    dataset_path: Path,
    runtime_config_path: Path,
    store_dir: Path,
    out_dir: Path,
    top_k: int,
    debug_top_k: int,
    limit: int | None,
    runtime_config: Any,
    summary: dict[str, Any],
    memory_after: dict[str, Any],
    run_label: str = "qwen3-4b-base",
) -> dict[str, Any]:
    return {
        "contract_version": "v1.1",
        "pipeline": "qwen3_base_e0",
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runner_script": "scripts/run_local_qwen3_e0.py",
        "dataset_path": str(dataset_path),
        "runtime_config_path": str(runtime_config_path),
        "store_dir": str(store_dir),
        "out_dir": str(out_dir),
        "similarity_top_k": top_k,
        "retrieval_debug_top_k": debug_top_k,
        "limit": limit,
        "run_label": run_label,
        "summary": summary,
        "memory_after": memory_after,
        **build_runtime_manifest_fields(runtime_config),
    }


def run_e0_baseline(
    *,
    runtime_config_path: Path,
    dataset_path: Path,
    store_dir: Path,
    out_dir: Path,
    top_k: int,
    debug_top_k: int,
    limit: int | None = None,
    sleep_seconds: float = 0.0,
    run_label: str = "qwen3-4b-base",
) -> dict[str, Any]:
    run_id = _now_run_id(dataset_path, run_label=run_label)
    run_dir = out_dir / run_id

    with local_runtime_context(
        runtime_config_path=runtime_config_path,
        store_dir=store_dir,
        top_k=top_k,
        debug_top_k=debug_top_k,
    ):
        runtime_config = load_runtime_config()
        dataset = select_records(load_dataset(dataset_path), limit)

        from core.rag import RagService

        rag_service = RagService()
        predictions = []
        for index, sample in enumerate(dataset, start=1):
            try:
                result = rag_service.answer_with_retrieval(
                    str(sample["question"]),
                    session_id=build_session_id(sample),
                )
                prediction = build_prediction_record(sample, result)
                prediction["error"] = None
                predictions.append(prediction)
                print(f"  [{index}/{len(dataset)}] OK: {sample['id']}", flush=True)
            except Exception as exc:
                prediction = build_prediction_record(
                    sample,
                    {
                        "answer": "",
                        "retrieved_context": "",
                        "retrieved_rows": [],
                        "retrieval_debug_candidates": [],
                    },
                )
                prediction["error"] = f"{type(exc).__name__}: {exc}"
                predictions.append(prediction)
                print(f"  [{index}/{len(dataset)}] FAILED: {sample['id']} {exc}", flush=True)
            if sleep_seconds:
                time.sleep(sleep_seconds)

        summary = summarize_predictions(predictions)
        memory_after = _memory_snapshot()

    write_json(run_dir / "predictions.json", predictions)
    write_json(run_dir / "metrics.json", summary)
    write_json(
        run_dir / "manifest.json",
        build_manifest(
            run_id=run_id,
            dataset_path=dataset_path,
            runtime_config_path=runtime_config_path,
            store_dir=store_dir,
            out_dir=out_dir,
            top_k=top_k,
            debug_top_k=debug_top_k,
            limit=limit,
            runtime_config=runtime_config,
            summary=summary,
            memory_after=memory_after,
            run_label=run_label,
        ),
    )

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "summary": summary,
        "artifacts": {
            "predictions": str(run_dir / "predictions.json"),
            "metrics": str(run_dir / "metrics.json"),
            "manifest": str(run_dir / "manifest.json"),
        },
    }


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Run Qwen3-4B base E0 generation evaluation.")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, type=Path)
    parser.add_argument("--dataset", default=DEFAULT_DATASET_PATH, type=Path)
    parser.add_argument("--store-dir", default=DEFAULT_STORE_DIR, type=Path)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, type=Path)
    parser.add_argument("--top-k", default=2, type=int)
    parser.add_argument("--debug-top-k", default=4, type=int)
    parser.add_argument("--limit", default=0, type=int)
    parser.add_argument("--sleep-seconds", default=0.0, type=float)
    parser.add_argument("--run-label", default="qwen3-4b-base")
    args = parser.parse_args()

    output = run_e0_baseline(
        runtime_config_path=args.config,
        dataset_path=args.dataset,
        store_dir=args.store_dir,
        out_dir=args.out_dir,
        top_k=args.top_k,
        debug_top_k=args.debug_top_k,
        limit=args.limit,
        sleep_seconds=args.sleep_seconds,
        run_label=args.run_label,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
