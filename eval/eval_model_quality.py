from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any
from uuid import uuid4

import httpx

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.eval_finetune_behavior import evaluate_row, summarize_rows
from eval.eval_finetune_compare import (
    analyze_answer_hardening,
    summarize_hardening_rows,
)
from model_deployment.manifest import load_manifest, sha256_file, validate_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "localrag-qwen3-4b-e6.1"
PROFILE_NAMES = (
    "adapter_bf16",
    "merged_bf16",
    "gguf_f16",
    "gguf_q4_k_m",
)
STAGES = (
    ("adapter_to_merged", "adapter_bf16", "merged_bf16"),
    ("merged_to_gguf_f16", "merged_bf16", "gguf_f16"),
    ("gguf_f16_to_q4_k_m", "gguf_f16", "gguf_q4_k_m"),
)
MAX_TOKENS = 256
SYSTEM_PROMPT = (
    "你是 LocalRAG 的证据约束回答助手。只能使用参考资料中的信息回答问题；"
    "如果参考资料不足以支持答案，请明确说明无法根据资料确定。回答必须简洁、直接，"
    "并且答案末尾必须包含“引用：”小节，逐条列出使用到的 source_id 和 locator，"
    "格式为“- source_id locator”。参考资料：\n{context}"
)
RISK_RATIOS = (
    "unsupported_claim_risk_ratio",
    "answer_contract_risk_ratio",
    "citation_support_risk_ratio",
    "required_term_risk_ratio",
    "forbidden_term_risk_ratio",
    "over_refusal_risk_ratio",
)


class ModelQualityError(RuntimeError):
    pass


@dataclass(frozen=True)
class QualityProfile:
    name: str
    repo_root: Path
    manifest_path: Path
    model_id: str = MODEL_ID
    endpoint: str | None = None
    model_path: Path | None = None
    api_token: str | None = None
    client: httpx.Client | None = None


def _json_write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ModelQualityError("quality dataset is invalid") from exc
    if not isinstance(payload, list) or len(payload) != 10:
        raise ModelQualityError("quality dataset must contain exactly 10 cases")
    ids = [row.get("id") for row in payload if isinstance(row, Mapping)]
    if len(ids) != 10 or any(not isinstance(value, str) or not value for value in ids):
        raise ModelQualityError("quality dataset IDs are invalid")
    if len(ids) != len(set(ids)):
        raise ModelQualityError("quality dataset IDs must be unique")
    return [dict(row) for row in payload]


def _dataset_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


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


def _retrieved_rows(sample: Mapping[str, Any]) -> list[dict[str, str]]:
    evidence = sample.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        raise ModelQualityError("quality case evidence is missing")
    rows = []
    for item in evidence:
        if not isinstance(item, Mapping):
            raise ModelQualityError("quality case evidence is invalid")
        source_id = item.get("source_id")
        locator = item.get("locator")
        quote = item.get("quote")
        if (
            not isinstance(source_id, str)
            or not source_id
            or not isinstance(locator, str)
            or not locator
            or not isinstance(quote, str)
            or not quote
        ):
            raise ModelQualityError("quality case evidence fields are invalid")
        rows.append(
            {"source_id": source_id, "locator": locator, "content": quote}
        )
    return rows


def _messages(sample: Mapping[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rows = _retrieved_rows(sample)
    blocks = [
        f"[{index}] source_id={row['source_id']} locator={row['locator']}\n{row['content']}"
        for index, row in enumerate(rows, start=1)
    ]
    question = sample.get("question")
    if not isinstance(question, str) or not question:
        raise ModelQualityError("quality case question is invalid")
    return (
        [
            {"role": "system", "content": SYSTEM_PROMPT.format(context="\n\n".join(blocks))},
            {"role": "user", "content": question},
        ],
        rows,
    )


def _endpoint_generator(profile: QualityProfile) -> Callable[[list[dict[str, str]], str], str]:
    if profile.endpoint is None or profile.model_path is not None:
        raise ModelQualityError("endpoint profile configuration is invalid")
    parsed = httpx.URL(profile.endpoint)
    if parsed.host not in {"127.0.0.1", "localhost"} or parsed.path.rstrip("/") != "/v1":
        raise ModelQualityError("quality endpoint must be loopback and end with /v1")
    headers = (
        {"Authorization": f"Bearer {profile.api_token}"}
        if profile.api_token is not None
        else {}
    )
    client = profile.client or httpx.Client(
        base_url=profile.endpoint.rstrip("/") + "/",
        headers=headers,
        timeout=180.0,
    )
    models = client.get("models")
    if models.status_code != 200:
        raise ModelQualityError("quality endpoint model identity request failed")
    try:
        model_rows = models.json()["data"]
    except (ValueError, KeyError, TypeError):
        raise ModelQualityError("quality endpoint model identity is invalid") from None
    if [row.get("id") for row in model_rows] != [profile.model_id]:
        raise ModelQualityError("quality endpoint model identity does not match")

    def generate(messages: list[dict[str, str]], case_id: str) -> str:
        response = client.post(
            "chat/completions",
            headers={"X-Request-ID": f"quality-{profile.name}-{case_id}"},
            json={
                "model": profile.model_id,
                "messages": messages,
                "temperature": 0,
                "max_tokens": MAX_TOKENS,
                "stream": False,
                "purpose": "rag_generation",
                "metadata": {"run_id": profile.name, "task_id": case_id},
            },
        )
        if response.status_code != 200:
            raise ModelQualityError(f"quality request failed with HTTP {response.status_code}")
        try:
            payload = response.json()
            return str(payload["choices"][0]["message"]["content"])
        except (ValueError, KeyError, IndexError, TypeError):
            raise ModelQualityError("quality response is invalid") from None

    return generate


def _direct_generator(profile: QualityProfile) -> Callable[[list[dict[str, str]], str], str]:
    if profile.model_path is None or profile.endpoint is not None:
        raise ModelQualityError("direct profile configuration is invalid")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_path = profile.model_path
    if not model_path.is_absolute():
        model_path = profile.repo_root / model_path
    if not model_path.is_dir():
        raise ModelQualityError("direct merged model is missing")
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        local_files_only=True,
        trust_remote_code=False,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        dtype=torch.bfloat16,
        local_files_only=True,
        trust_remote_code=False,
        low_cpu_mem_usage=True,
    )
    model.eval()
    model.to("cuda")

    def generate(messages: list[dict[str, str]], case_id: str) -> str:
        del case_id
        rendered = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = tokenizer(rendered, return_tensors="pt", add_special_tokens=False)
        inputs = {key: value.to("cuda") for key, value in inputs.items()}
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=MAX_TOKENS,
                do_sample=False,
                temperature=None,
                top_p=None,
                top_k=None,
            )
        input_tokens = inputs["input_ids"].shape[-1]
        return tokenizer.decode(output[0, input_tokens:], skip_special_tokens=True)

    return generate


def _quality_gate(summary: Mapping[str, Any]) -> tuple[bool, list[str]]:
    checks = {
        "sample_count": summary.get("sample_count") == 10,
        "request_success": summary.get("request_success_count") == 10,
        "request_error": summary.get("request_error_count") == 0,
        "evidence_source_hit": summary.get("evidence_source_hit_ratio") == 1.0,
        **{key: summary.get(key) == 0.0 for key in RISK_RATIOS},
    }
    failures = [key for key, passed in checks.items() if not passed]
    return not failures, failures


def run_quality_profile(
    profile: QualityProfile,
    dataset_path: Path,
    out_dir: Path,
) -> dict[str, Any]:
    if (
        not isinstance(profile, QualityProfile)
        or not isinstance(profile.name, str)
        or not profile.name.strip()
        or not isinstance(profile.model_id, str)
        or not profile.model_id.strip()
    ):
        raise ModelQualityError("quality profile is invalid")
    repo_root = Path(profile.repo_root).resolve()
    manifest_path = profile.manifest_path
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path
    manifest = load_manifest(manifest_path)
    validate_manifest(repo_root, manifest)
    dataset_path = Path(dataset_path).resolve()
    dataset = _load_dataset(dataset_path)
    revision, dirty = _git_state(repo_root)
    generate = (
        _endpoint_generator(profile)
        if profile.endpoint is not None
        else _direct_generator(profile)
    )

    predictions = []
    request_success_count = 0
    for sample in dataset:
        messages, retrieved_rows = _messages(sample)
        error = None
        answer = ""
        try:
            answer = generate(messages, str(sample["id"]))
            request_success_count += 1
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        predictions.append(
            {
                **sample,
                "answer": answer,
                "retrieved_context": "\n".join(row["content"] for row in retrieved_rows),
                "retrieved_rows": retrieved_rows,
                "error": error,
            }
        )

    behavior_rows = [evaluate_row(row) for row in predictions]
    hardening_rows = [analyze_answer_hardening(row) for row in predictions]
    summary = {
        **summarize_rows(behavior_rows),
        **summarize_hardening_rows(hardening_rows),
        "request_success_count": request_success_count,
        "request_error_count": 10 - request_success_count,
    }
    gate_pass, gate_failures = _quality_gate(summary)
    summary["gate_pass"] = gate_pass
    summary["gate_failures"] = gate_failures
    run_id = f"model-quality-{profile.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"
    run_dir = Path(out_dir) / run_id
    run_manifest = {
        "contract_version": "localrag-model-quality-v1",
        "run_id": run_id,
        "profile": profile.name,
        "model_id": MODEL_ID,
        "model_manifest_path": manifest_path.relative_to(repo_root).as_posix(),
        "model_manifest_sha256": sha256_file(manifest_path),
        "dataset_path": dataset_path.relative_to(repo_root).as_posix(),
        "dataset_sha256": _dataset_sha256(dataset_path),
        "generation": {
            "temperature": 0,
            "max_tokens": MAX_TOKENS,
            "enable_thinking": False,
        },
        "git_revision": revision,
        "git_dirty": dirty,
    }
    output = {
        "run_id": run_id,
        "profile": profile.name,
        "summary": summary,
        "manifest": run_manifest,
        "prediction_ids": [row["id"] for row in predictions],
        "artifacts": {"run_dir": str(run_dir)},
    }
    _json_write(run_dir / "predictions.json", predictions)
    _json_write(run_dir / "behavior_rows.json", behavior_rows)
    _json_write(run_dir / "hardening_rows.json", hardening_rows)
    _json_write(run_dir / "summary.json", output)
    _json_write(run_dir / "manifest.json", run_manifest)
    return output


def compare_quality_stage(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    stage: str,
) -> dict[str, Any]:
    stage_rows = {name: (left, right) for name, left, right in STAGES}
    if stage not in stage_rows:
        raise ModelQualityError("quality comparison stage is invalid")
    expected_baseline, expected_candidate = stage_rows[stage]
    failures = []
    if baseline.get("profile") != expected_baseline:
        failures.append("baseline_profile")
    if candidate.get("profile") != expected_candidate:
        failures.append("candidate_profile")
    baseline_manifest = baseline.get("manifest")
    candidate_manifest = candidate.get("manifest")
    if not isinstance(baseline_manifest, Mapping) or not isinstance(candidate_manifest, Mapping):
        failures.append("run_manifest")
    else:
        for key in ("model_id", "dataset_sha256", "generation"):
            if baseline_manifest.get(key) != candidate_manifest.get(key):
                failures.append(key)
        if baseline_manifest.get("git_dirty") or candidate_manifest.get("git_dirty"):
            failures.append("git_dirty")
    if baseline.get("prediction_ids") != candidate.get("prediction_ids"):
        failures.append("prediction_ids")
    baseline_summary = baseline.get("summary")
    candidate_summary = candidate.get("summary")
    if not isinstance(baseline_summary, Mapping) or not baseline_summary.get("gate_pass"):
        failures.append("baseline_gate")
    if not isinstance(candidate_summary, Mapping) or not candidate_summary.get("gate_pass"):
        failures.append("candidate_gate")
    return {
        "stage": stage,
        "baseline": expected_baseline,
        "candidate": expected_candidate,
        "gate_pass": not failures,
        "failures": failures,
    }


def summarize_model_quality(runs: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    if set(runs) != set(PROFILE_NAMES):
        return {
            "gate_pass": False,
            "failures": ["profile_set"],
            "stages": [],
        }
    stages = [
        compare_quality_stage(runs[left], runs[right], name)
        for name, left, right in STAGES
    ]
    first_failure = next(
        (row["stage"] for row in stages if not row["gate_pass"]),
        None,
    )
    return {
        "gate_pass": first_failure is None,
        "first_failed_stage": first_failure,
        "stages": stages,
        "profiles": {
            name: runs[name]["summary"]
            for name in PROFILE_NAMES
        },
    }


def deterministic_fixture() -> dict[str, Any]:
    ids = [f"quality-{index:02d}" for index in range(10)]
    runs = {}
    for name in PROFILE_NAMES:
        summary = {
            "sample_count": 10,
            "request_success_count": 10,
            "request_error_count": 0,
            "evidence_source_hit_ratio": 1.0,
            **{key: 0.0 for key in RISK_RATIOS},
            "gate_pass": True,
        }
        runs[name] = {
            "profile": name,
            "summary": summary,
            "prediction_ids": ids,
            "manifest": {
                "model_id": MODEL_ID,
                "dataset_sha256": "a" * 64,
                "generation": {
                    "temperature": 0,
                    "max_tokens": MAX_TOKENS,
                    "enable_thinking": False,
                },
                "git_dirty": False,
            },
        }
    return summarize_model_quality(runs)


def _latest_runs(root: Path) -> dict[str, Mapping[str, Any]]:
    runs = {}
    for profile in PROFILE_NAMES:
        candidates = sorted(root.glob(f"model-quality-{profile}-*/summary.json"))
        if not candidates:
            raise ModelQualityError(f"latest quality run is missing: {profile}")
        runs[profile] = json.loads(candidates[-1].read_text(encoding="utf-8"))
    return runs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate LocalRAG model conversion quality.")
    parser.add_argument("--mode", choices=("deterministic",))
    parser.add_argument("--profile")
    parser.add_argument("--model-id", default=MODEL_ID)
    parser.add_argument("--endpoint")
    parser.add_argument("--model-path", type=Path)
    parser.add_argument("--model-manifest", type=Path)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/evaluation/gold/generation_eval_set.json"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/model_quality"))
    parser.add_argument("--api-token-env", default="LOCALRAG_MODEL_API_TOKEN")
    parser.add_argument("--summarize-latest", type=Path)
    return parser


def main() -> dict[str, Any]:
    args = build_parser().parse_args()
    if args.mode == "deterministic":
        output = deterministic_fixture()
    elif args.summarize_latest is not None:
        output = summarize_model_quality(_latest_runs(args.summarize_latest))
        _json_write(args.summarize_latest / "comparison-latest.json", output)
    else:
        if args.profile is None or args.model_manifest is None:
            raise ModelQualityError("profile and model manifest are required")
        profile = QualityProfile(
            name=args.profile,
            repo_root=REPO_ROOT,
            manifest_path=args.model_manifest,
            model_id=args.model_id,
            endpoint=args.endpoint,
            model_path=args.model_path,
            api_token=os.environ.get(args.api_token_env),
        )
        output = run_quality_profile(profile, args.dataset, args.out_dir)
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return output


if __name__ == "__main__":
    main()
