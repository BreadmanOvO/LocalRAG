import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.model_paths import BGE_M3_LOCAL, QWEN3_4B_LOCAL, QWEN3_8B_LOCAL


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "results" / "finetune_env"


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _module_version(module_name: str) -> str | None:
    if not _module_available(module_name):
        return None
    try:
        module = __import__(module_name)
    except Exception:
        return "import_error"
    return str(getattr(module, "__version__", "unknown"))


def _torch_info() -> dict[str, Any]:
    info: dict[str, Any] = {
        "available": _module_available("torch"),
        "version": None,
        "cuda_available": False,
        "cuda_version": None,
        "gpu_name": None,
        "gpu_memory_total_bytes": None,
        "gpu_memory_free_bytes": None,
        "error": None,
    }
    if not info["available"]:
        return info

    try:
        import torch

        info["version"] = str(torch.__version__)
        info["cuda_available"] = bool(torch.cuda.is_available())
        info["cuda_version"] = torch.version.cuda
        if info["cuda_available"]:
            info["gpu_name"] = torch.cuda.get_device_name(0)
            free_bytes, total_bytes = torch.cuda.mem_get_info()
            info["gpu_memory_free_bytes"] = int(free_bytes)
            info["gpu_memory_total_bytes"] = int(total_bytes)
    except Exception as exc:
        info["error"] = str(exc)
    return info


def _command_candidates(command: str) -> list[str]:
    candidates: list[str] = []
    path_match = shutil.which(command)
    if path_match:
        candidates.append(path_match)

    executable_dir = Path(sys.executable).resolve().parent
    scripts_dir = executable_dir / "Scripts"
    for base_dir in (executable_dir, scripts_dir):
        candidates.append(str(base_dir / command))
        if platform.system() == "Windows":
            candidates.append(str(base_dir / f"{command}.exe"))

    seen: set[str] = set()
    unique_candidates: list[str] = []
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            unique_candidates.append(candidate)
    return unique_candidates


def _run_command(command: str, *args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            [command, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None


def _command_info(command: str) -> dict[str, Any]:
    for candidate in _command_candidates(command):
        version_result = _run_command(candidate, "version")
        if version_result is None or version_result.returncode not in {0, 1, 2}:
            continue

        version_output = "\n".join(
            line.rstrip()
            for line in (version_result.stdout or version_result.stderr).splitlines()
            if line.strip()
        )

        return {
            "available": True,
            "path": candidate,
            "version_output": version_output,
        }

    return {
        "available": False,
        "path": None,
        "version_output": None,
    }


def collect_environment() -> dict[str, Any]:
    torch_info = _torch_info()
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "packages": {
            "torch": torch_info,
            "transformers": {
                "available": _module_available("transformers"),
                "version": _module_version("transformers"),
            },
            "peft": {
                "available": _module_available("peft"),
                "version": _module_version("peft"),
            },
            "trl": {
                "available": _module_available("trl"),
                "version": _module_version("trl"),
            },
            "accelerate": {
                "available": _module_available("accelerate"),
                "version": _module_version("accelerate"),
            },
            "bitsandbytes": {
                "available": _module_available("bitsandbytes"),
                "version": _module_version("bitsandbytes"),
            },
            "flash_attn": {
                "available": _module_available("flash_attn"),
                "version": _module_version("flash_attn"),
            },
        },
        "commands": {
            "llamafactory-cli": _command_info("llamafactory-cli"),
        },
        "local_paths": {
            "qwen3_8b": {
                "path": QWEN3_8B_LOCAL,
                "exists": Path(QWEN3_8B_LOCAL).exists(),
            },
            "qwen3_4b": {
                "path": QWEN3_4B_LOCAL,
                "exists": Path(QWEN3_4B_LOCAL).exists(),
            },
            "bge_m3": {
                "path": BGE_M3_LOCAL,
                "exists": Path(BGE_M3_LOCAL).exists(),
            },
        },
    }


def _format_bytes(value: int | None) -> str:
    if value is None:
        return "unknown"
    gib = value / (1024 ** 3)
    return f"{gib:.2f} GiB"


def build_markdown_report(report: dict[str, Any]) -> str:
    torch_info = report["packages"]["torch"]
    package_rows = []
    for name in ("transformers", "peft", "trl", "accelerate", "bitsandbytes", "flash_attn"):
        package = report["packages"][name]
        package_rows.append(
            f"| {name} | {package['available']} | {package['version'] or 'not installed'} |"
        )

    return "\n".join(
        [
            "# Fine-Tuning Environment Report",
            "",
            f"- Created at: `{report['created_at']}`",
            f"- OS: `{report['platform']['system']} {report['platform']['release']}`",
            f"- Python: `{report['python']['version']}`",
            f"- Python executable: `{report['python']['executable']}`",
            "",
            "## PyTorch / CUDA",
            "",
            f"- PyTorch available: `{torch_info['available']}`",
            f"- PyTorch version: `{torch_info['version'] or 'not installed'}`",
            f"- CUDA available: `{torch_info['cuda_available']}`",
            f"- CUDA version: `{torch_info['cuda_version'] or 'unknown'}`",
            f"- GPU name: `{torch_info['gpu_name'] or 'unknown'}`",
            f"- GPU memory free: `{_format_bytes(torch_info['gpu_memory_free_bytes'])}`",
            f"- GPU memory total: `{_format_bytes(torch_info['gpu_memory_total_bytes'])}`",
            f"- Torch error: `{torch_info['error'] or 'none'}`",
            "",
            "## Packages",
            "",
            "| Package | Available | Version |",
            "|---------|-----------|---------|",
            *package_rows,
            "",
            "## Commands",
            "",
            f"- LLaMA-Factory CLI available: `{report['commands']['llamafactory-cli']['available']}`",
            f"- LLaMA-Factory CLI path: `{report['commands']['llamafactory-cli'].get('path') or 'not found'}`",
            f"- LLaMA-Factory CLI version output: `{report['commands']['llamafactory-cli'].get('version_output') or 'unknown'}`",
            "",
            "## Local Model Paths",
            "",
            f"- Qwen3-8B: `{report['local_paths']['qwen3_8b']['path']}` exists=`{report['local_paths']['qwen3_8b']['exists']}`",
            f"- Qwen3-4B: `{report['local_paths']['qwen3_4b']['path']}` exists=`{report['local_paths']['qwen3_4b']['exists']}`",
            f"- BGE-M3: `{report['local_paths']['bge_m3']['path']}` exists=`{report['local_paths']['bge_m3']['exists']}`",
            "",
            "## Gate Interpretation",
            "",
            "- Continue to local Qwen3 inference only if CUDA is available and `models/Qwen3-8B` exists.",
            "- Continue to QLoRA smoke only if `bitsandbytes` is available and the Qwen3 base smoke passes.",
            "- If `bitsandbytes` is unavailable on Windows, use the LoRA fallback branch after base inference works.",
            "",
        ]
    )


def write_reports(report: dict[str, Any], out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "env_report.json"
    markdown_path = out_dir / "env_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(build_markdown_report(report), encoding="utf-8")
    return {
        "json": str(json_path),
        "markdown": str(markdown_path),
    }


def main() -> dict[str, Any]:
    report = collect_environment()
    paths = write_reports(report)
    summary = {
        "cuda_available": report["packages"]["torch"]["cuda_available"],
        "gpu_name": report["packages"]["torch"]["gpu_name"],
        "qwen3_8b_exists": report["local_paths"]["qwen3_8b"]["exists"],
        "qwen3_4b_exists": report["local_paths"]["qwen3_4b"]["exists"],
        "bge_m3_exists": report["local_paths"]["bge_m3"]["exists"],
        "bitsandbytes_available": report["packages"]["bitsandbytes"]["available"],
        "llamafactory_cli_available": report["commands"]["llamafactory-cli"]["available"],
        "reports": paths,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    main()
