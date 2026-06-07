import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config.model_paths import QWEN3_4B_LOCAL, QWEN3_8B_LOCAL


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "results" / "local_qwen_smoke"
DEFAULT_PROMPT = "请用一句话说明自动驾驶感知模块的作用。"


def _now_run_id() -> str:
    return f"qwen3-smoke-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def _memory_snapshot(torch_module: Any) -> dict[str, Any]:
    if not torch_module.cuda.is_available():
        return {
            "cuda_available": False,
            "gpu_name": None,
            "memory_free_bytes": None,
            "memory_total_bytes": None,
            "memory_allocated_bytes": None,
            "memory_reserved_bytes": None,
            "max_memory_allocated_bytes": None,
        }
    free_bytes, total_bytes = torch_module.cuda.mem_get_info()
    return {
        "cuda_available": True,
        "gpu_name": torch_module.cuda.get_device_name(0),
        "memory_free_bytes": int(free_bytes),
        "memory_total_bytes": int(total_bytes),
        "memory_allocated_bytes": int(torch_module.cuda.memory_allocated()),
        "memory_reserved_bytes": int(torch_module.cuda.memory_reserved()),
        "max_memory_allocated_bytes": int(torch_module.cuda.max_memory_allocated()),
    }


def _format_bytes(value: int | None) -> str:
    if value is None:
        return "unknown"
    return f"{value / (1024 ** 3):.2f} GiB"


def _resolve_torch_dtype(torch_module: Any, dtype_name: str):
    if dtype_name == "auto":
        return "auto"
    if dtype_name == "float16":
        return torch_module.float16
    if dtype_name == "bfloat16":
        return torch_module.bfloat16
    if dtype_name == "float32":
        return torch_module.float32
    raise ValueError(f"unsupported torch dtype: {dtype_name}")


def _select_device(torch_module: Any, requested_device: str) -> str:
    if requested_device != "auto":
        return requested_device
    return "cuda" if torch_module.cuda.is_available() else "cpu"


def _build_inputs(tokenizer: Any, prompt: str, device: str) -> dict[str, Any]:
    messages = [{"role": "user", "content": prompt}]
    if hasattr(tokenizer, "apply_chat_template"):
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    else:
        text = prompt
    inputs = tokenizer(text, return_tensors="pt")
    if device == "cuda":
        inputs = {key: value.to(device) for key, value in inputs.items()}
    return inputs


def _decode_new_tokens(tokenizer: Any, outputs: Any, input_length: int) -> str:
    generated_ids = outputs[0][input_length:]
    return tokenizer.decode(generated_ids, skip_special_tokens=True).strip()


def run_smoke(
    *,
    model_path: Path,
    prompt: str,
    out_dir: Path,
    device: str = "auto",
    torch_dtype: str = "float16",
    max_new_tokens: int = 64,
) -> dict[str, Any]:
    run_id = _now_run_id()
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    result: dict[str, Any] = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "model_path": str(model_path),
        "prompt": prompt,
        "device_requested": device,
        "torch_dtype_requested": torch_dtype,
        "max_new_tokens": max_new_tokens,
        "success": False,
        "tokenizer_loaded": False,
        "model_loaded": False,
        "generated_text": "",
        "error": None,
        "traceback": None,
        "memory_before": None,
        "memory_after_load": None,
        "memory_after_generate": None,
    }

    try:
        if not model_path.exists():
            raise FileNotFoundError(f"model path does not exist: {model_path}")

        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        selected_device = _select_device(torch, device)
        result["device"] = selected_device
        result["torch_version"] = str(torch.__version__)
        result["transformers_version"] = _get_transformers_version()
        result["memory_before"] = _memory_snapshot(torch)
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()

        tokenizer = AutoTokenizer.from_pretrained(
            str(model_path),
            trust_remote_code=True,
            local_files_only=True,
        )
        result["tokenizer_loaded"] = True

        dtype = _resolve_torch_dtype(torch, torch_dtype)
        model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            torch_dtype=dtype,
            trust_remote_code=True,
            local_files_only=True,
        )
        if selected_device == "cuda":
            model = model.to(selected_device)
        model.eval()
        result["model_loaded"] = True
        result["memory_after_load"] = _memory_snapshot(torch)

        inputs = _build_inputs(tokenizer, prompt, selected_device)
        input_length = inputs["input_ids"].shape[-1]
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        result["generated_text"] = _decode_new_tokens(tokenizer, outputs, input_length)
        result["memory_after_generate"] = _memory_snapshot(torch)
        result["success"] = bool(result["generated_text"])
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()

    write_result_files(run_dir, result)
    return result


def _get_transformers_version() -> str:
    try:
        import transformers

        return str(transformers.__version__)
    except Exception:
        return "unknown"


def build_markdown_result(result: dict[str, Any]) -> str:
    memory_after_load = result.get("memory_after_load") or {}
    memory_after_generate = result.get("memory_after_generate") or {}
    return "\n".join(
        [
            "# Local Qwen3 Smoke Result",
            "",
            f"- Run id: `{result['run_id']}`",
            f"- Created at: `{result['created_at']}`",
            f"- Success: `{result['success']}`",
            f"- Model path: `{result['model_path']}`",
            f"- Device: `{result.get('device', result['device_requested'])}`",
            f"- Torch dtype requested: `{result['torch_dtype_requested']}`",
            f"- Max new tokens: `{result['max_new_tokens']}`",
            f"- Tokenizer loaded: `{result['tokenizer_loaded']}`",
            f"- Model loaded: `{result['model_loaded']}`",
            "",
            "## GPU Memory",
            "",
            f"- After load allocated: `{_format_bytes(memory_after_load.get('memory_allocated_bytes'))}`",
            f"- After load reserved: `{_format_bytes(memory_after_load.get('memory_reserved_bytes'))}`",
            f"- After generate max allocated: `{_format_bytes(memory_after_generate.get('max_memory_allocated_bytes'))}`",
            "",
            "## Prompt",
            "",
            result["prompt"],
            "",
            "## Generated Text",
            "",
            result.get("generated_text") or "(empty)",
            "",
            "## Error",
            "",
            result.get("error") or "none",
            "",
        ]
    )


def write_result_files(run_dir: Path, result: dict[str, Any]) -> dict[str, str]:
    json_path = run_dir / "result.json"
    markdown_path = run_dir / "result.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(build_markdown_result(result), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(markdown_path)}


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Smoke test local Qwen3-8B generation.")
    parser.add_argument("--model-path", default=Path(QWEN3_4B_LOCAL), type=Path)
    parser.add_argument(
        "--model-size",
        default="4b",
        choices=["4b", "8b"],
        help="Convenience selector used only when --model-path is not supplied.",
    )
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, type=Path)
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    parser.add_argument(
        "--torch-dtype",
        default="float16",
        choices=["auto", "float16", "bfloat16", "float32"],
        help="Use float16 by default to keep the 8B smoke test within GPU memory.",
    )
    parser.add_argument("--max-new-tokens", default=64, type=int)
    args = parser.parse_args()
    if args.model_path == Path(QWEN3_4B_LOCAL) and args.model_size == "8b":
        args.model_path = Path(QWEN3_8B_LOCAL)

    result = run_smoke(
        model_path=args.model_path,
        prompt=args.prompt,
        out_dir=args.out_dir,
        device=args.device,
        torch_dtype=args.torch_dtype,
        max_new_tokens=args.max_new_tokens,
    )
    print(
        json.dumps(
            {
                "success": result["success"],
                "run_id": result["run_id"],
                "tokenizer_loaded": result["tokenizer_loaded"],
                "model_loaded": result["model_loaded"],
                "generated_text": result["generated_text"],
                "error": result["error"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return result


if __name__ == "__main__":
    main()
