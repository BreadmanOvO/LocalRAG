from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


STABILITY_GATE_CONTRACT_VERSION = "agent-stability-gate-v1"
DEFAULT_REQUIRED_RUNS = 3
DEFAULT_RESULTS_DIR = Path("results/agent_eval")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _nonnegative_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _is_formal_run(manifest: dict[str, Any]) -> bool:
    scope = manifest.get("evaluation_scope")
    if isinstance(scope, dict) and "selection_complete" in scope:
        return scope.get("selection_complete") is True
    return manifest.get("max_cases") is None and not manifest.get("case_ids")


def _run_is_complete(manifest: dict[str, Any], summary: dict[str, Any]) -> bool:
    scope = manifest.get("evaluation_scope")
    gate_checks = summary.get("gate_checks")
    return (
        isinstance(scope, dict)
        and scope.get("evaluation_complete") is True
        and isinstance(gate_checks, dict)
        and gate_checks.get("evaluation_complete") is True
    )


def _error_counts(predictions: list[Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for case in predictions:
        if not isinstance(case, dict):
            continue
        attempts = case.get("attempts")
        if not isinstance(attempts, list) or not attempts:
            attempts = [case]
        for attempt in attempts:
            if not isinstance(attempt, dict):
                continue
            for turn in attempt.get("turns", []):
                if not isinstance(turn, dict):
                    continue
                error = str(turn.get("error") or "")
                if error:
                    counts[error] += 1
    return dict(sorted(counts.items()))


def _identity(manifest: dict[str, Any], summary: dict[str, Any]) -> str:
    corpus = manifest.get("corpus") if isinstance(manifest.get("corpus"), dict) else {}
    identity = {
        "contract_version": manifest.get("contract_version"),
        "git_revision": manifest.get("git_revision"),
        "dataset_path": manifest.get("dataset_path"),
        "dataset_version": manifest.get("dataset_version"),
        "registry_path": manifest.get("registry_path"),
        "runtime": manifest.get("runtime"),
        "execution": manifest.get("execution"),
        "allow_stale_corpus": manifest.get("allow_stale_corpus"),
        "gate_thresholds": summary.get("gate_thresholds"),
        "corpus": {
            key: corpus.get(key)
            for key in (
                "persist_directory",
                "collection_name",
                "registry_source_count",
                "chroma_source_count",
                "chunk_count",
                "corpus_fingerprint",
                "registry_fingerprint",
            )
        },
    }
    return json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _identity_is_complete(manifest: dict[str, Any], summary: dict[str, Any]) -> bool:
    corpus = manifest.get("corpus")
    scope = manifest.get("evaluation_scope")
    return (
        bool(manifest.get("contract_version"))
        and bool(manifest.get("git_revision"))
        and bool(manifest.get("dataset_version"))
        and isinstance(manifest.get("runtime"), dict)
        and bool(manifest["runtime"])
        and isinstance(manifest.get("execution"), dict)
        and manifest["execution"].get("mode") == "formal"
        and manifest.get("allow_stale_corpus") is False
        and isinstance(scope, dict)
        and isinstance(scope.get("expected_case_count"), int)
        and isinstance(scope.get("expected_turn_count"), int)
        and isinstance(corpus, dict)
        and bool(corpus.get("corpus_fingerprint"))
        and bool(corpus.get("registry_fingerprint"))
        and isinstance(summary.get("gate_thresholds"), dict)
        and bool(summary["gate_thresholds"])
    )


def _has_graph_recursion(run: dict[str, Any]) -> bool:
    return any(
        "graph_recursion" in error.lower() or "graphrecursionerror" in error.lower()
        for error in run["error_counts"]
    )


def load_formal_agent_runs(results_dir: str | Path) -> list[dict[str, Any]]:
    runs = []
    for run_dir in Path(results_dir).glob("agent-eval-*"):
        manifest_path = run_dir / "manifest.json"
        summary_path = run_dir / "summary.json"
        predictions_path = run_dir / "predictions.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = _read_json(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if not isinstance(manifest, dict) or not _is_formal_run(manifest):
            continue

        artifact_valid = summary_path.is_file() and predictions_path.is_file()
        summary: dict[str, Any] = {}
        predictions: list[Any] = []
        if artifact_valid:
            try:
                raw_summary = _read_json(summary_path)
                raw_predictions = _read_json(predictions_path)
            except (OSError, ValueError, json.JSONDecodeError):
                artifact_valid = False
            else:
                if isinstance(raw_summary, dict) and isinstance(raw_predictions, list):
                    summary = raw_summary
                    predictions = raw_predictions
                else:
                    artifact_valid = False
        runs.append(
            {
                "run_id": str(manifest.get("run_id") or run_dir.name),
                "created_at": str(manifest.get("created_at") or ""),
                "manifest": manifest,
                "summary": summary,
                "artifact_valid": artifact_valid,
                "error_counts": _error_counts(predictions),
                "infrastructure_retry_count": sum(
                    _nonnegative_int(case.get("infrastructure_retry_count", 0))
                    for case in predictions
                    if isinstance(case, dict)
                ),
            }
        )
    return sorted(runs, key=lambda run: (run["created_at"], run["run_id"]))


def evaluate_agent_stability_gate(
    results_dir: str | Path,
    *,
    required_runs: int = DEFAULT_REQUIRED_RUNS,
) -> dict[str, Any]:
    if required_runs <= 0:
        raise ValueError("required_runs must be greater than zero")

    available_runs = load_formal_agent_runs(results_dir)
    selected_runs = available_runs[-required_runs:]
    enough_runs = len(selected_runs) == required_runs
    identities = {
        _identity(run["manifest"], run["summary"])
        for run in selected_runs
    }
    checks = {
        "required_run_count": enough_runs,
        "all_artifacts_valid": enough_runs
        and all(run["artifact_valid"] for run in selected_runs),
        "all_gates_pass": enough_runs
        and all(run["summary"].get("gate_pass") is True for run in selected_runs),
        "all_evaluations_complete": enough_runs
        and all(
            _run_is_complete(run["manifest"], run["summary"])
            for run in selected_runs
        ),
        "all_revisions_clean": enough_runs
        and all(run["manifest"].get("git_dirty") is False for run in selected_runs),
        "all_runs_formal": enough_runs
        and all(
            isinstance(run["manifest"].get("execution"), dict)
            and run["manifest"]["execution"].get("mode") == "formal"
            and run["manifest"].get("allow_stale_corpus") is False
            for run in selected_runs
        ),
        "identity_complete": enough_runs
        and all(
            _identity_is_complete(run["manifest"], run["summary"])
            for run in selected_runs
        ),
        "identity_consistent": enough_runs and len(identities) == 1,
        "no_graph_recursion": enough_runs
        and all(not _has_graph_recursion(run) for run in selected_runs),
    }
    run_rows = []
    for run in selected_runs:
        summary = run["summary"]
        run_rows.append(
            {
                "run_id": run["run_id"],
                "created_at": run["created_at"],
                "git_revision": run["manifest"].get("git_revision", ""),
                "git_dirty": run["manifest"].get("git_dirty"),
                "artifact_valid": run["artifact_valid"],
                "gate_pass": summary.get("gate_pass") is True,
                "evaluation_complete": _run_is_complete(run["manifest"], summary),
                "case_pass_ratio": summary.get("case_pass_ratio", 0),
                "infrastructure_retry_count": run["infrastructure_retry_count"],
                "error_counts": run["error_counts"],
            }
        )
    return {
        "contract_version": STABILITY_GATE_CONTRACT_VERSION,
        "required_run_count": required_runs,
        "available_formal_run_count": len(available_runs),
        "selected_run_ids": [run["run_id"] for run in selected_runs],
        "runs": run_rows,
        "checks": checks,
        "failure_reasons": [name for name, passed in checks.items() if not passed],
        "gate_pass": all(checks.values()),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate consecutive Agent release gates.")
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--required-runs", type=int, default=DEFAULT_REQUIRED_RUNS)
    parser.add_argument("--out", type=Path, default=None)
    return parser


def main() -> dict[str, Any]:
    args = build_parser().parse_args()
    result = evaluate_agent_stability_gate(
        args.results_dir,
        required_runs=args.required_runs,
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return result


if __name__ == "__main__":
    run_result = main()
    raise SystemExit(0 if run_result["gate_pass"] else 1)
