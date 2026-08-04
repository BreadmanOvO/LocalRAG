from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
from threading import Barrier, Event, Thread
import time
from typing import Any, TypeGuard
from uuid import uuid4

import httpx

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from model_deployment.manifest import load_manifest, sha256_file, validate_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "localrag-qwen3-4b-e6.1"
PROFILES = ("e6_1_adapter_bf16", "e6_1_q4_k_m")
PROMPT_TARGETS = (512, 2048, 8192)
CONCURRENCY_LEVELS = (1, 2, 4)
OUTPUT_TOKENS = 256
WARMUP_ROUNDS = 2
MEASURED_ROUNDS = 5
REQUEST_TIMEOUT_SECONDS = 1200.0
PROFILE_MANIFESTS = {
    "e6_1_adapter_bf16": Path(
        "model_deployment/manifests/e6_1_input_manifest.json"
    ),
    "e6_1_q4_k_m": Path(
        "model_deployment/manifests/e6_1_q4_k_m_manifest.json"
    ),
}


class ServingBenchmarkError(RuntimeError):
    pass


@dataclass(frozen=True)
class BenchmarkCase:
    profile: str
    prompt: str
    prompt_target_tokens: int
    prompt_tokens: int
    concurrency: int
    model_id: str = MODEL_ID
    output_tokens: int = OUTPUT_TOKENS
    warmup_rounds: int = WARMUP_ROUNDS
    measured_rounds: int = MEASURED_ROUNDS
    git_revision: str = ""
    git_dirty: bool = False
    memory_reader: Callable[[], Mapping[str, Any]] | None = None


def _encode(tokenizer: object, text: str) -> list[int]:
    encode = getattr(tokenizer, "encode", None)
    if not callable(encode):
        raise ServingBenchmarkError("tokenizer must provide encode")
    values = encode(text, add_special_tokens=False)
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise ServingBenchmarkError("tokenizer returned invalid token IDs")
    return [int(value) for value in values]


def build_prompt(tokenizer: object, target_tokens: int) -> str:
    if type(target_tokens) is not int or target_tokens <= 0:
        raise ServingBenchmarkError("target token count must be positive")
    decode = getattr(tokenizer, "decode", None)
    if not callable(decode):
        raise ServingBenchmarkError("tokenizer must provide decode")
    instruction = (
        "请阅读以下性能基准文本，并持续输出“基准”直到达到系统输出上限，"
        "不要解释，也不要提前结束。\n\n"
    )
    unit = (
        "LocalRAG 本地模型服务使用固定上下文、固定并发和固定输出长度测量性能。"
        "该文本只用于构造稳定输入，不包含需要记忆的事实。\n"
    )
    text = instruction + unit
    while len(_encode(tokenizer, text)) < target_tokens:
        text += unit
    token_ids = _encode(tokenizer, text)[:target_tokens]
    prompt = str(
        decode(
            token_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
    )
    actual = len(_encode(tokenizer, prompt))
    if abs(actual - target_tokens) / target_tokens > 0.02:
        raise ServingBenchmarkError(
            f"prompt token error exceeds 2%: target={target_tokens}, actual={actual}"
        )
    return prompt


def _gpu_memory() -> Mapping[str, Any]:
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.used,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if result.returncode != 0:
        raise ServingBenchmarkError("nvidia-smi failed")
    row = next((line.strip() for line in result.stdout.splitlines() if line.strip()), "")
    fields = [field.strip() for field in row.split(",")]
    if len(fields) != 5:
        raise ServingBenchmarkError("nvidia-smi returned invalid GPU data")
    return {
        "gpu_index": int(fields[0]),
        "gpu_name": fields[1],
        "gpu_used_bytes": int(fields[2]) * 1024 * 1024,
        "gpu_total_bytes": int(fields[3]) * 1024 * 1024,
        "driver_version": fields[4],
    }


def _memory_samples(
    reader: Callable[[], Mapping[str, Any]],
    stop: Event,
    output: list[Mapping[str, Any]],
) -> None:
    while not stop.wait(0.05):
        try:
            output.append(dict(reader()))
        except Exception:
            continue


def _parse_sse_line(line: str) -> Mapping[str, Any] | None:
    if not line.startswith("data:"):
        return None
    value = line[5:].strip()
    if not value or value == "[DONE]":
        return None
    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        raise ServingBenchmarkError("service returned invalid SSE JSON") from None
    if not isinstance(payload, Mapping):
        raise ServingBenchmarkError("service returned invalid SSE event")
    return payload


def _request_sample(
    client: httpx.Client,
    case: BenchmarkCase,
    *,
    phase: str,
    round_index: int,
    worker_index: int,
    barrier: Barrier,
) -> dict[str, Any]:
    request_id = (
        f"benchmark-{case.profile}-{case.prompt_target_tokens}-"
        f"c{case.concurrency}-{phase}-{round_index}-{worker_index}-{uuid4().hex[:8]}"
    )
    sample: dict[str, Any] = {
        "profile": case.profile,
        "model_id": case.model_id,
        "git_revision": case.git_revision,
        "git_dirty": case.git_dirty,
        "phase": phase,
        "round": round_index,
        "worker": worker_index,
        "request_id": request_id,
        "prompt_target_tokens": case.prompt_target_tokens,
        "prompt_tokens": case.prompt_tokens,
        "output_token_limit": case.output_tokens,
        "concurrency": case.concurrency,
        "http_status": 0,
        "error_code": None,
        "oom": False,
        "queue_seconds": None,
        "ttft_seconds": None,
        "latency_seconds": None,
        "completion_tokens": 0,
        "tokens_per_second": 0.0,
    }
    try:
        barrier.wait(timeout=30)
        started = time.perf_counter()
        first_content_at: float | None = None
        completion_tokens = 0
        with client.stream(
            "POST",
            "chat/completions",
            headers={"X-Request-ID": request_id},
            json={
                "model": case.model_id,
                "messages": [{"role": "user", "content": case.prompt}],
                "temperature": 0,
                "max_tokens": case.output_tokens,
                "stream": True,
                "purpose": "rag_generation",
                "metadata": {
                    "run_id": f"benchmark-{case.profile}",
                    "task_id": f"p{case.prompt_target_tokens}-c{case.concurrency}",
                },
            },
        ) as response:
            sample["http_status"] = response.status_code
            queue_header = response.headers.get("X-Queue-Wait-Seconds")
            try:
                queue_seconds = float(queue_header) if queue_header is not None else None
            except ValueError:
                queue_seconds = None
            if queue_seconds is not None and queue_seconds >= 0:
                sample["queue_seconds"] = queue_seconds
            if response.status_code != 200:
                response.read()
                body = response.text.lower()
                sample["error_code"] = f"http_{response.status_code}"
                sample["oom"] = "out of memory" in body or "cuda" in body
            else:
                for line in response.iter_lines():
                    event = _parse_sse_line(line)
                    if event is None:
                        continue
                    error = event.get("error")
                    if isinstance(error, Mapping):
                        code = error.get("code")
                        sample["error_code"] = str(code or "stream_error")
                        error_text = json.dumps(error, ensure_ascii=False).lower()
                        sample["oom"] = (
                            "out of memory" in error_text or "cuda" in error_text
                        )
                    usage = event.get("usage")
                    if isinstance(usage, Mapping):
                        value = usage.get("completion_tokens")
                        if type(value) is int:
                            completion_tokens = max(completion_tokens, value)
                    choices = event.get("choices")
                    if isinstance(choices, list) and choices:
                        choice = choices[0]
                        if isinstance(choice, Mapping):
                            delta = choice.get("delta")
                            content = (
                                delta.get("content")
                                if isinstance(delta, Mapping)
                                else None
                            )
                            if (
                                isinstance(content, str)
                                and content
                                and first_content_at is None
                            ):
                                first_content_at = time.perf_counter()
        finished = time.perf_counter()
        latency = finished - started
        ttft = first_content_at - started if first_content_at is not None else None
        sample["latency_seconds"] = latency
        sample["ttft_seconds"] = ttft
        sample["completion_tokens"] = completion_tokens
        if ttft is not None and completion_tokens > 0:
            generation_seconds = max(latency - ttft, 1e-9)
            sample["tokens_per_second"] = completion_tokens / generation_seconds
        if response.status_code == 200 and completion_tokens <= 0:
            sample["error_code"] = sample["error_code"] or "usage_missing"
        if response.status_code == 200 and ttft is None:
            sample["error_code"] = sample["error_code"] or "first_token_missing"
    except Exception as exc:
        sample["error_code"] = f"{type(exc).__name__}: {exc}"
        error_text = str(exc).lower()
        sample["oom"] = "out of memory" in error_text or "cuda" in error_text
    return sample


def _run_batch(
    client: httpx.Client,
    case: BenchmarkCase,
    *,
    phase: str,
    round_index: int,
) -> list[dict[str, Any]]:
    reader = case.memory_reader or _gpu_memory
    idle = dict(reader())
    memory_rows: list[Mapping[str, Any]] = [idle]
    stop = Event()
    monitor = Thread(
        target=_memory_samples,
        args=(reader, stop, memory_rows),
        daemon=True,
    )
    monitor.start()
    barrier = Barrier(case.concurrency)
    try:
        with ThreadPoolExecutor(max_workers=case.concurrency) as executor:
            futures = [
                executor.submit(
                    _request_sample,
                    client,
                    case,
                    phase=phase,
                    round_index=round_index,
                    worker_index=index,
                    barrier=barrier,
                )
                for index in range(case.concurrency)
            ]
            rows = [future.result() for future in futures]
    finally:
        stop.set()
        monitor.join(timeout=5)
        try:
            memory_rows.append(dict(reader()))
        except Exception:
            pass
    used_values: list[int] = []
    for memory_row in memory_rows:
        used = memory_row.get("gpu_used_bytes")
        if isinstance(used, int) and not isinstance(used, bool):
            used_values.append(used)
    peak_used = max(used_values) if used_values else None
    for row in rows:
        row["gpu_idle_used_bytes"] = idle.get("gpu_used_bytes")
        row["gpu_peak_used_bytes"] = peak_used
        row["gpu_total_bytes"] = idle.get("gpu_total_bytes")
        row["gpu_name"] = idle.get("gpu_name")
        row["driver_version"] = idle.get("driver_version")
        row["gpu_allocated_bytes"] = None
        row["gpu_reserved_bytes"] = None
    return rows


def run_benchmark_cell(
    client: httpx.Client,
    case: BenchmarkCase,
) -> list[dict[str, Any]]:
    if case.profile not in PROFILES:
        raise ServingBenchmarkError("benchmark profile is invalid")
    if case.prompt_target_tokens not in PROMPT_TARGETS:
        raise ServingBenchmarkError("prompt target is invalid")
    if case.concurrency not in CONCURRENCY_LEVELS:
        raise ServingBenchmarkError("concurrency is invalid")
    if abs(case.prompt_tokens - case.prompt_target_tokens) / case.prompt_target_tokens > 0.02:
        raise ServingBenchmarkError("prompt token error exceeds 2%")
    rows: list[dict[str, Any]] = []
    for index in range(case.warmup_rounds):
        rows.extend(_run_batch(client, case, phase="warmup", round_index=index))
    for index in range(case.measured_rounds):
        rows.extend(_run_batch(client, case, phase="measurement", round_index=index))
    return rows


def _percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        raise ServingBenchmarkError("cannot summarize empty values")
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summarize_profile(samples: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    measured = [row for row in samples if row.get("phase") == "measurement"]
    failures: list[str] = []
    profiles = {row.get("profile") for row in measured}
    model_ids = {row.get("model_id") for row in measured}
    revisions = {row.get("git_revision") for row in measured}
    dirty_values = {row.get("git_dirty") for row in measured}
    if len(profiles) != 1 or next(iter(profiles), None) not in PROFILES:
        failures.append("profile_identity")
    if model_ids != {MODEL_ID}:
        failures.append("model_identity")
    if len(revisions) != 1 or not next(iter(revisions), ""):
        failures.append("git_revision")
    if dirty_values != {False}:
        failures.append("git_dirty")
    cells = []
    for target in PROMPT_TARGETS:
        for concurrency in CONCURRENCY_LEVELS:
            rows = [
                row
                for row in measured
                if row.get("prompt_target_tokens") == target
                and row.get("concurrency") == concurrency
            ]
            expected = MEASURED_ROUNDS * concurrency
            cell_failures = []
            if len(rows) != expected:
                cell_failures.append("sample_count")
            for row in rows:
                actual = row.get("prompt_tokens")
                if type(actual) is not int or abs(actual - target) / target > 0.02:
                    cell_failures.append("prompt_tokens")
                if row.get("http_status") != 200 or row.get("error_code") is not None:
                    cell_failures.append("request_error")
                if row.get("oom"):
                    cell_failures.append("oom")
                if not isinstance(row.get("ttft_seconds"), (int, float)):
                    cell_failures.append("ttft")
                if not isinstance(row.get("latency_seconds"), (int, float)):
                    cell_failures.append("latency")
                if not isinstance(row.get("queue_seconds"), (int, float)):
                    cell_failures.append("queue")
                if not isinstance(row.get("tokens_per_second"), (int, float)) or row.get(
                    "tokens_per_second", 0
                ) <= 0:
                    cell_failures.append("throughput")
                if type(row.get("gpu_peak_used_bytes")) is not int:
                    cell_failures.append("gpu_memory")
            ttft_values = [
                float(row["ttft_seconds"])
                for row in rows
                if isinstance(row.get("ttft_seconds"), (int, float))
            ]
            latency_values = [
                float(row["latency_seconds"])
                for row in rows
                if isinstance(row.get("latency_seconds"), (int, float))
            ]
            throughput_values = [
                float(row["tokens_per_second"])
                for row in rows
                if isinstance(row.get("tokens_per_second"), (int, float))
                and float(row["tokens_per_second"]) > 0
            ]
            cell = {
                "prompt_target_tokens": target,
                "concurrency": concurrency,
                "sample_count": len(rows),
                "gate_pass": not cell_failures,
                "failures": sorted(set(cell_failures)),
                "ttft_seconds_p50": _percentile(ttft_values, 0.50)
                if ttft_values
                else None,
                "ttft_seconds_p95": _percentile(ttft_values, 0.95)
                if ttft_values
                else None,
                "latency_seconds_p50": _percentile(latency_values, 0.50)
                if latency_values
                else None,
                "latency_seconds_p95": _percentile(latency_values, 0.95)
                if latency_values
                else None,
                "tokens_per_second_p50": statistics.median(throughput_values)
                if throughput_values
                else None,
                "tokens_per_second_p95": _percentile(throughput_values, 0.95)
                if throughput_values
                else None,
                "gpu_peak_used_bytes": max(
                    (
                        int(row["gpu_peak_used_bytes"])
                        for row in rows
                        if type(row.get("gpu_peak_used_bytes")) is int
                    ),
                    default=None,
                ),
            }
            if cell_failures:
                failures.append(f"cell_{target}_c{concurrency}")
            cells.append(cell)
    return {
        "contract_version": "localrag-serving-benchmark-summary-v1",
        "profile": next(iter(profiles), None),
        "model_id": next(iter(model_ids), None),
        "git_revision": next(iter(revisions), None),
        "measurement_sample_count": len(measured),
        "warmup_sample_count": sum(
            1 for row in samples if row.get("phase") == "warmup"
        ),
        "gpu_peak_used_bytes": max(
            (
                int(row["gpu_peak_used_bytes"])
                for row in measured
                if type(row.get("gpu_peak_used_bytes")) is int
            ),
            default=None,
        ),
        "gate_pass": not failures,
        "failures": sorted(set(failures)),
        "cells": cells,
    }


def _cell_map(summary: Mapping[str, Any]) -> dict[tuple[int, int], Mapping[str, Any]]:
    rows = summary.get("cells")
    if not isinstance(rows, list):
        return {}
    return {
        (int(row["prompt_target_tokens"]), int(row["concurrency"])): row
        for row in rows
        if isinstance(row, Mapping)
        and type(row.get("prompt_target_tokens")) is int
        and type(row.get("concurrency")) is int
    }


def compare_profiles(
    bf16: Mapping[str, Any],
    q4: Mapping[str, Any],
) -> dict[str, Any]:
    failures = []
    if bf16.get("profile") != "e6_1_adapter_bf16":
        failures.append("bf16_profile")
    if q4.get("profile") != "e6_1_q4_k_m":
        failures.append("q4_profile")
    if not bf16.get("gate_pass"):
        failures.append("bf16_gate")
    if not q4.get("gate_pass"):
        failures.append("q4_gate")
    if bf16.get("model_id") != q4.get("model_id") or bf16.get("model_id") != MODEL_ID:
        failures.append("model_identity")
    if bf16.get("git_revision") != q4.get("git_revision"):
        failures.append("git_revision")
    bf16_peak = bf16.get("gpu_peak_used_bytes")
    q4_peak = q4.get("gpu_peak_used_bytes")
    vram_reduction = None
    if isinstance(bf16_peak, (int, float)) and isinstance(q4_peak, (int, float)) and bf16_peak > 0:
        vram_reduction = 1.0 - float(q4_peak) / float(bf16_peak)
        if vram_reduction < 0.30:
            failures.append("q4_vram_reduction")
    else:
        failures.append("gpu_memory")
    bf16_cells = _cell_map(bf16)
    q4_cells = _cell_map(q4)
    if len(bf16_cells) != 9 or len(q4_cells) != 9:
        failures.append("cell_matrix")
    throughput_rows = []
    for target in PROMPT_TARGETS:
        key = (target, 1)
        left = bf16_cells.get(key, {}).get("tokens_per_second_p50")
        right = q4_cells.get(key, {}).get("tokens_per_second_p50")
        passed = (
            isinstance(left, (int, float))
            and isinstance(right, (int, float))
            and float(right) >= float(left)
        )
        if not passed:
            failures.append(f"q4_throughput_{target}")
        throughput_rows.append(
            {
                "prompt_target_tokens": target,
                "bf16_tokens_per_second_p50": left,
                "q4_tokens_per_second_p50": right,
                "gate_pass": passed,
            }
        )
    return {
        "contract_version": "localrag-serving-benchmark-comparison-v1",
        "gate_pass": not failures,
        "failures": sorted(set(failures)),
        "bf16_profile": "e6_1_adapter_bf16",
        "q4_profile": "e6_1_q4_k_m",
        "vram_reduction_ratio": vram_reduction,
        "single_concurrency_throughput": throughput_rows,
    }


def _git_state(repo_root: Path) -> tuple[str, bool]:
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return revision, bool(status)


def _json_write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(
        path,
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
    )


def _jsonl_write(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(
        path,
        "".join(json.dumps(dict(row), ensure_ascii=False) + "\n" for row in rows),
    )


def _atomic_write_text(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, Mapping):
                raise ValueError("row is not an object")
            rows.append(dict(value))
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise ServingBenchmarkError("benchmark checkpoint is invalid") from exc
    return rows


def _is_finite_number(value: object) -> TypeGuard[int | float]:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)


def _validate_request_timeout_seconds(value: object) -> float:
    if not _is_finite_number(value) or float(value) <= 0:
        raise ServingBenchmarkError("benchmark request timeout must be positive and finite")
    return float(value)


def _validate_resume_identity(
    manifest: object,
    expected_identity: Mapping[str, Any],
) -> None:
    if not isinstance(manifest, Mapping) or any(
        manifest.get(key) != value for key, value in expected_identity.items()
    ):
        raise ServingBenchmarkError("benchmark resume identity does not match")


def _completed_cells(
    samples: Sequence[Mapping[str, Any]],
    *,
    profile: str | None = None,
    git_revision: str | None = None,
    git_dirty: bool | None = None,
) -> set[tuple[int, int]]:
    completed = set()
    for target in PROMPT_TARGETS:
        for concurrency in CONCURRENCY_LEVELS:
            rows = [
                row
                for row in samples
                if row.get("prompt_target_tokens") == target
                and row.get("concurrency") == concurrency
            ]
            expected = {
                (phase, round_index, worker)
                for phase, rounds in (
                    ("warmup", WARMUP_ROUNDS),
                    ("measurement", MEASURED_ROUNDS),
                )
                for round_index in range(rounds)
                for worker in range(concurrency)
            }
            actual = {
                (row.get("phase"), row.get("round"), row.get("worker"))
                for row in rows
            }
            request_ids = [row.get("request_id") for row in rows]
            semantic_valid = all(
                (profile is None or row.get("profile") == profile)
                and row.get("model_id") == MODEL_ID
                and (git_revision is None or row.get("git_revision") == git_revision)
                and (git_dirty is None or row.get("git_dirty") is git_dirty)
                and row.get("prompt_target_tokens") == target
                and type(row.get("prompt_tokens")) is int
                and abs(int(row["prompt_tokens"]) - target) / target <= 0.02
                and row.get("output_token_limit") == OUTPUT_TOKENS
                and row.get("concurrency") == concurrency
                and row.get("http_status") == 200
                and row.get("error_code") is None
                and row.get("oom") is False
                and _is_finite_number(row.get("queue_seconds"))
                and float(row["queue_seconds"]) >= 0
                and _is_finite_number(row.get("ttft_seconds"))
                and float(row["ttft_seconds"]) >= 0
                and _is_finite_number(row.get("latency_seconds"))
                and float(row["latency_seconds"]) >= 0
                and _is_finite_number(row.get("tokens_per_second"))
                and float(row["tokens_per_second"]) > 0
                and type(row.get("completion_tokens")) is int
                and int(row["completion_tokens"]) > 0
                and type(row.get("gpu_peak_used_bytes")) is int
                for row in rows
            )
            if (
                len(rows) == len(expected)
                and actual == expected
                and len(request_ids) == len(set(request_ids))
                and all(isinstance(value, str) and value for value in request_ids)
                and semantic_valid
            ):
                completed.add((target, concurrency))
    return completed


def run_profile(
    *,
    profile: str,
    endpoint: str,
    tokenizer_path: Path,
    out_dir: Path,
    api_token: str | None,
    request_timeout_seconds: float = REQUEST_TIMEOUT_SECONDS,
    resume_run: Path | None = None,
) -> dict[str, Any]:
    if profile not in PROFILES:
        raise ServingBenchmarkError("benchmark profile is invalid")
    parsed = httpx.URL(endpoint)
    if parsed.host not in {"127.0.0.1", "localhost"} or parsed.path.rstrip("/") != "/v1":
        raise ServingBenchmarkError("benchmark endpoint must be loopback and end with /v1")
    request_timeout_seconds = _validate_request_timeout_seconds(
        request_timeout_seconds
    )
    manifest_path = REPO_ROOT / PROFILE_MANIFESTS[profile]
    manifest = load_manifest(manifest_path)
    validate_manifest(REPO_ROOT, manifest)
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        REPO_ROOT / tokenizer_path,
        local_files_only=True,
        trust_remote_code=False,
    )
    prompts = {
        target: build_prompt(tokenizer, target) for target in PROMPT_TARGETS
    }
    revision, dirty = _git_state(REPO_ROOT)
    prompt_fingerprint = hashlib.sha256(
        "\n".join(prompts[target] for target in PROMPT_TARGETS).encode("utf-8")
    ).hexdigest()
    out_root = Path(out_dir).resolve()
    try:
        output_root = out_root.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        raise ServingBenchmarkError(
            "benchmark output must remain inside the repository"
        ) from None
    command = [sys.executable, *sys.argv]
    if resume_run is None:
        run_id = (
            f"serving-benchmark-{profile}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-"
            f"{uuid4().hex[:8]}"
        )
        run_dir = out_root / run_id
        run_manifest = {
            "contract_version": "localrag-serving-benchmark-v1",
            "run_id": run_id,
            "profile": profile,
            "model_id": MODEL_ID,
            "model_manifest_path": PROFILE_MANIFESTS[profile].as_posix(),
            "model_manifest_sha256": sha256_file(manifest_path),
            "git_revision": revision,
            "git_dirty": dirty,
            "service_revision": revision,
            "prompt_fingerprint": prompt_fingerprint,
            "prompt_targets": list(PROMPT_TARGETS),
            "concurrency_levels": list(CONCURRENCY_LEVELS),
            "output_tokens": OUTPUT_TOKENS,
            "warmup_rounds": WARMUP_ROUNDS,
            "measured_rounds": MEASURED_ROUNDS,
            "request_timeout_seconds": request_timeout_seconds,
            "output_root": output_root,
            "gpu": dict(_gpu_memory()),
            "commands": [command],
        }
        samples: list[dict[str, Any]] = []
        _json_write(run_dir / "manifest.json", run_manifest)
        _jsonl_write(run_dir / "samples.jsonl", samples)
    else:
        run_dir = Path(resume_run).resolve()
        if run_dir.parent != out_root or not run_dir.is_dir():
            raise ServingBenchmarkError("resume run must remain inside benchmark output")
        if (run_dir / "summary.json").exists():
            raise ServingBenchmarkError("benchmark run is already complete")
        try:
            run_manifest = json.loads(
                (run_dir / "manifest.json").read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ServingBenchmarkError("benchmark resume manifest is invalid") from exc
        expected_identity = {
            "contract_version": "localrag-serving-benchmark-v1",
            "profile": profile,
            "model_id": MODEL_ID,
            "model_manifest_sha256": sha256_file(manifest_path),
            "git_revision": revision,
            "git_dirty": dirty,
            "service_revision": revision,
            "prompt_fingerprint": prompt_fingerprint,
            "prompt_targets": list(PROMPT_TARGETS),
            "concurrency_levels": list(CONCURRENCY_LEVELS),
            "output_tokens": OUTPUT_TOKENS,
            "warmup_rounds": WARMUP_ROUNDS,
            "measured_rounds": MEASURED_ROUNDS,
            "request_timeout_seconds": request_timeout_seconds,
            "output_root": output_root,
        }
        _validate_resume_identity(run_manifest, expected_identity)
        resume_run_id = run_manifest.get("run_id")
        if not isinstance(resume_run_id, str) or run_dir.name != resume_run_id:
            raise ServingBenchmarkError("benchmark resume run ID does not match")
        run_id = resume_run_id
        commands = run_manifest.get("commands")
        if not isinstance(commands, list):
            raise ServingBenchmarkError("benchmark resume commands are invalid")
        commands.append(command)
        _json_write(run_dir / "manifest.json", run_manifest)
        samples = _load_jsonl(run_dir / "samples.jsonl")
    complete = _completed_cells(
        samples,
        profile=profile,
        git_revision=revision,
        git_dirty=dirty,
    )
    headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
    with httpx.Client(
        base_url=endpoint.rstrip("/") + "/",
        headers=headers,
        timeout=httpx.Timeout(request_timeout_seconds, connect=10.0),
    ) as client:
        models = client.get("models")
        if models.status_code != 200:
            raise ServingBenchmarkError("benchmark model identity request failed")
        try:
            ids = [row.get("id") for row in models.json()["data"]]
        except (ValueError, KeyError, TypeError):
            raise ServingBenchmarkError("benchmark model identity is invalid") from None
        if ids != [MODEL_ID]:
            raise ServingBenchmarkError("benchmark model identity does not match")
        for target in PROMPT_TARGETS:
            prompt = prompts[target]
            actual_tokens = len(_encode(tokenizer, prompt))
            for concurrency in CONCURRENCY_LEVELS:
                cell = (target, concurrency)
                if cell in complete:
                    continue
                samples = [
                    row
                    for row in samples
                    if not (
                        row.get("prompt_target_tokens") == target
                        and row.get("concurrency") == concurrency
                    )
                ]
                samples.extend(
                    run_benchmark_cell(
                        client,
                        BenchmarkCase(
                            profile=profile,
                            prompt=prompt,
                            prompt_target_tokens=target,
                            prompt_tokens=actual_tokens,
                            concurrency=concurrency,
                            git_revision=revision,
                            git_dirty=dirty,
                        ),
                    )
                )
                _jsonl_write(run_dir / "samples.jsonl", samples)
    summary = summarize_profile(samples)
    output = {
        "run_id": run_id,
        "profile": profile,
        "summary": summary,
        "manifest": run_manifest,
        "artifacts": {"run_dir": str(run_dir)},
    }
    _json_write(run_dir / "summary.json", output)
    return output


def _deterministic_samples(profile: str, *, peak: int, throughput: float) -> list[dict[str, Any]]:
    rows = []
    for target in PROMPT_TARGETS:
        for concurrency in CONCURRENCY_LEVELS:
            for phase, rounds in (("warmup", WARMUP_ROUNDS), ("measurement", MEASURED_ROUNDS)):
                for round_index in range(rounds):
                    for worker in range(concurrency):
                        rows.append(
                            {
                                "profile": profile,
                                "model_id": MODEL_ID,
                                "git_revision": "a" * 40,
                                "git_dirty": False,
                                "phase": phase,
                                "round": round_index,
                                "worker": worker,
                                "request_id": f"fixture-{profile}-{target}-{concurrency}-{phase}-{round_index}-{worker}",
                                "prompt_target_tokens": target,
                                "prompt_tokens": target,
                                "output_token_limit": OUTPUT_TOKENS,
                                "completion_tokens": OUTPUT_TOKENS,
                                "concurrency": concurrency,
                                "http_status": 200,
                                "error_code": None,
                                "oom": False,
                                "queue_seconds": 0.0,
                                "ttft_seconds": 0.1 + target / 100000,
                                "latency_seconds": 5.0,
                                "tokens_per_second": throughput,
                                "gpu_idle_used_bytes": peak - 1024,
                                "gpu_peak_used_bytes": peak,
                                "gpu_total_bytes": 16 * 1024**3,
                                "gpu_name": "fixture-gpu",
                                "driver_version": "fixture",
                                "gpu_allocated_bytes": None,
                                "gpu_reserved_bytes": None,
                            }
                        )
    return rows


def deterministic_fixture() -> dict[str, Any]:
    bf16 = summarize_profile(
        _deterministic_samples(
            "e6_1_adapter_bf16",
            peak=10 * 1024**3,
            throughput=30.0,
        )
    )
    q4 = summarize_profile(
        _deterministic_samples(
            "e6_1_q4_k_m",
            peak=5 * 1024**3,
            throughput=50.0,
        )
    )
    return {
        "gate_pass": compare_profiles(bf16, q4)["gate_pass"],
        "profiles": {"e6_1_adapter_bf16": bf16, "e6_1_q4_k_m": q4},
        "comparison": compare_profiles(bf16, q4),
    }


def _latest_summary(root: Path, profile: str) -> Mapping[str, Any]:
    candidates = sorted(root.glob(f"serving-benchmark-{profile}-*/summary.json"))
    if not candidates:
        raise ServingBenchmarkError(f"latest benchmark run is missing: {profile}")
    payload = json.loads(candidates[-1].read_text(encoding="utf-8"))
    summary = payload.get("summary") if isinstance(payload, Mapping) else None
    if not isinstance(summary, Mapping):
        raise ServingBenchmarkError("latest benchmark summary is invalid")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark LocalRAG model serving.")
    parser.add_argument("--mode", choices=("deterministic",))
    parser.add_argument("--profile", choices=PROFILES)
    parser.add_argument("--endpoint")
    parser.add_argument("--tokenizer-path", type=Path, default=Path("models/Qwen3-4B"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/model_benchmark"))
    parser.add_argument("--api-token-env", default="LOCALRAG_MODEL_API_TOKEN")
    parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=REQUEST_TIMEOUT_SECONDS,
    )
    parser.add_argument("--resume-run", type=Path)
    parser.add_argument("--compare-latest", type=Path)
    return parser


def main() -> dict[str, Any]:
    args = build_parser().parse_args()
    if args.mode == "deterministic":
        output = deterministic_fixture()
    elif args.compare_latest is not None:
        bf16 = _latest_summary(args.compare_latest, "e6_1_adapter_bf16")
        q4 = _latest_summary(args.compare_latest, "e6_1_q4_k_m")
        output = compare_profiles(bf16, q4)
        _json_write(args.compare_latest / "comparison-latest.json", output)
    else:
        if args.profile is None or args.endpoint is None:
            raise ServingBenchmarkError("profile and endpoint are required")
        output = run_profile(
            profile=args.profile,
            endpoint=args.endpoint,
            tokenizer_path=args.tokenizer_path,
            out_dir=args.out_dir,
            api_token=os.environ.get(args.api_token_env),
            request_timeout_seconds=args.request_timeout_seconds,
            resume_run=args.resume_run,
        )
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
