import argparse
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config import settings as config


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "runtime_local_qwen3_4b.example.json"
DEFAULT_STORE_DIR = REPO_ROOT / "results" / "chunking_eval" / "stores" / "eval_set-20260522-071034" / "semantic"
DEFAULT_OUT_DIR = REPO_ROOT / "results" / "local_rag_qwen_smoke"
DEFAULT_QUESTION = "自动驾驶感知模块的作用是什么？"


def _now_run_id() -> str:
    return f"local-rag-qwen3-smoke-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


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


def _format_bytes(value: int | None) -> str:
    if value is None:
        return "unknown"
    return f"{value / (1024 ** 3):.2f} GiB"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_markdown_result(result: dict[str, Any]) -> str:
    memory = result.get("memory_after") or {}
    retrieved_rows = result.get("retrieved_rows", [])
    sources = ", ".join(
        row.get("source_id", "") for row in retrieved_rows if row.get("source_id")
    )
    return "\n".join(
        [
            "# Local RAG Qwen3 Smoke Result",
            "",
            f"- Run id: `{result['run_id']}`",
            f"- Created at: `{result['created_at']}`",
            f"- Success: `{result['success']}`",
            f"- Runtime config: `{result['runtime_config_path']}`",
            f"- Store dir: `{result['store_dir']}`",
            f"- Question: `{result['question']}`",
            f"- Retrieved rows: `{len(retrieved_rows)}`",
            f"- Retrieved sources: `{sources or 'none'}`",
            f"- CUDA memory allocated after run: `{_format_bytes(memory.get('memory_allocated_bytes'))}`",
            f"- CUDA memory reserved after run: `{_format_bytes(memory.get('memory_reserved_bytes'))}`",
            f"- CUDA max memory allocated: `{_format_bytes(memory.get('max_memory_allocated_bytes'))}`",
            "",
            "## Answer",
            "",
            result.get("answer") or "(empty)",
            "",
            "## Error",
            "",
            result.get("error") or "none",
            "",
        ]
    )


def write_result_files(run_dir: Path, result: dict[str, Any]) -> dict[str, str]:
    json_path = run_dir / "prediction.json"
    markdown_path = run_dir / "result.md"
    manifest_path = run_dir / "manifest.json"
    _write_json(json_path, result)
    markdown_path.write_text(build_markdown_result(result), encoding="utf-8")
    _write_json(
        manifest_path,
        {
            "pipeline": "local_rag_qwen_smoke",
            "contract_version": "v1.1",
            "run_id": result["run_id"],
            "created_at": result["created_at"],
            "runtime_config_path": result["runtime_config_path"],
            "store_dir": result["store_dir"],
            "question": result["question"],
        },
    )
    return {
        "prediction": str(json_path),
        "markdown": str(markdown_path),
        "manifest": str(manifest_path),
    }


def run_smoke(
    *,
    runtime_config_path: Path,
    store_dir: Path,
    question: str,
    out_dir: Path,
    top_k: int,
    debug_top_k: int,
) -> dict[str, Any]:
    run_id = _now_run_id()
    run_dir = out_dir / run_id
    result: dict[str, Any] = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runtime_config_path": str(runtime_config_path),
        "store_dir": str(store_dir),
        "question": question,
        "success": False,
        "answer": "",
        "retrieved_context": "",
        "retrieved_rows": [],
        "retrieval_debug_candidates": [],
        "memory_after": None,
        "error": None,
        "traceback": None,
    }

    original_runtime_config = os.environ.get("LOCALRAG_RUNTIME_CONFIG")
    original_persist_directory = config.persist_directory
    original_top_k = config.similarity_top_k
    original_debug_top_k = config.retrieval_debug_top_k
    try:
        if not runtime_config_path.exists():
            raise FileNotFoundError(f"runtime config does not exist: {runtime_config_path}")
        if not store_dir.exists():
            raise FileNotFoundError(f"store directory does not exist: {store_dir}")

        os.environ["LOCALRAG_RUNTIME_CONFIG"] = str(runtime_config_path)
        config.persist_directory = str(store_dir)
        config.similarity_top_k = top_k
        config.retrieval_debug_top_k = debug_top_k

        from core.rag import RagService

        rag_service = RagService()
        answer_payload = rag_service.answer_with_retrieval(question, session_id="local-rag-qwen3-smoke")
        result.update(answer_payload)
        result["memory_after"] = _memory_snapshot()
        result["success"] = bool(result.get("answer", "").strip()) and bool(result.get("retrieved_rows"))
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
        result["memory_after"] = _memory_snapshot()
    finally:
        if original_runtime_config is None:
            os.environ.pop("LOCALRAG_RUNTIME_CONFIG", None)
        else:
            os.environ["LOCALRAG_RUNTIME_CONFIG"] = original_runtime_config
        config.persist_directory = original_persist_directory
        config.similarity_top_k = original_top_k
        config.retrieval_debug_top_k = original_debug_top_k

    result["artifacts"] = write_result_files(run_dir, result)
    return result


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Smoke test LocalRAG retrieval with local Qwen3 generation.")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, type=Path)
    parser.add_argument("--store-dir", default=DEFAULT_STORE_DIR, type=Path)
    parser.add_argument("--question", default=DEFAULT_QUESTION)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, type=Path)
    parser.add_argument("--top-k", default=2, type=int)
    parser.add_argument("--debug-top-k", default=4, type=int)
    args = parser.parse_args()

    result = run_smoke(
        runtime_config_path=args.config,
        store_dir=args.store_dir,
        question=args.question,
        out_dir=args.out_dir,
        top_k=args.top_k,
        debug_top_k=args.debug_top_k,
    )
    print(
        json.dumps(
            {
                "success": result["success"],
                "run_id": result["run_id"],
                "answer": result["answer"],
                "retrieved_count": len(result.get("retrieved_rows", [])),
                "error": result["error"],
                "artifacts": result.get("artifacts", {}),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    main()
