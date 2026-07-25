from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.agent_eval_contract import (
    A5_MIN_CASE_COUNT,
    AGENT_EVAL_CONTRACT_VERSION,
    CONTROL_PROBE_NAMES,
    DUPLICATE_CONTROL_PROBES,
    EVIDENCE_BINDING_CONTROL_PROBES,
    RESUME_CONTROL_PROBES,
    STABILITY_GATE_CONTRACT_VERSION,
    TERMINATION_CONTROL_PROBES,
)

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


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _is_ratio(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0.0 <= float(value) <= 1.0
    )


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
        "expected_probe_types": summary.get("expected_probe_types"),
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
    scope_probes = scope.get("expected_probe_types") if isinstance(scope, dict) else None
    summary_probes = summary.get("expected_probe_types")
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
        and scope.get("expected_case_count", 0) >= A5_MIN_CASE_COUNT
        and scope.get("probe_selection_complete") is True
        and isinstance(scope_probes, list)
        and bool(scope_probes)
        and isinstance(corpus, dict)
        and bool(corpus.get("corpus_fingerprint"))
        and bool(corpus.get("registry_fingerprint"))
        and isinstance(summary.get("gate_thresholds"), dict)
        and bool(summary["gate_thresholds"])
        and isinstance(summary_probes, list)
        and bool(summary_probes)
        and scope_probes == summary_probes
    )


def _has_graph_recursion(run: dict[str, Any]) -> bool:
    return _nonnegative_int(run["summary"].get("graph_recursion_error_count")) > 0 or any(
        "graph_recursion" in error.lower() or "graphrecursionerror" in error.lower()
        for error in run["error_counts"]
    )


def _a5_case_contracts_pass(summary: dict[str, Any]) -> bool:
    case_count = _nonnegative_int(summary.get("case_count"))
    return (
        case_count >= A5_MIN_CASE_COUNT
        and _nonnegative_int(summary.get("expected_case_count")) == case_count
        and _nonnegative_int(summary.get("passed_case_count")) == case_count
        and _nonnegative_int(summary.get("case_tool_contract_pass_count")) == case_count
        and _nonnegative_int(summary.get("case_answer_contract_pass_count")) == case_count
    )


def _a5_contract_is_complete(manifest: dict[str, Any], summary: dict[str, Any]) -> bool:
    required_counts = (
        "case_count",
        "expected_case_count",
        "passed_case_count",
        "case_tool_contract_pass_count",
        "case_answer_contract_pass_count",
        "termination_case_count",
        "termination_contract_pass_count",
        "classified_termination_count",
        "graph_recursion_error_count",
        "duplicate_probe_case_count",
        "duplicate_tool_violation_count",
        "unclassified_termination_count",
        "evidence_binding_case_count",
        "verified_finding_count",
        "bound_verified_finding_count",
        "checkpoint_resume_case_count",
        "checkpoint_resume_pass_count",
        "forbidden_tool_violation_count",
    )
    required_ratios = (
        "verified_finding_evidence_binding_ratio",
        "checkpoint_resume_pass_ratio",
    )
    gate_checks = summary.get("gate_checks")
    required_gate_checks = (
        "evaluation_complete",
        "control_probe_coverage",
        "graph_recursion_errors",
        "classified_termination",
        "termination_contracts",
        "duplicate_tool_violations",
        "verified_finding_evidence_binding",
        "checkpoint_resume",
        "forbidden_tool_violations",
        "control_contracts",
    )
    return (
        manifest.get("contract_version") == AGENT_EVAL_CONTRACT_VERSION
        and all(_is_nonnegative_int(summary.get(field)) for field in required_counts)
        and all(_is_ratio(summary.get(field)) for field in required_ratios)
        and isinstance(gate_checks, dict)
        and all(isinstance(gate_checks.get(field), bool) for field in required_gate_checks)
    )


def _probe_types(value: Any) -> frozenset[str] | None:
    if not isinstance(value, list) or not value:
        return None
    if any(not isinstance(item, str) or not item for item in value):
        return None
    normalized = frozenset(value)
    return normalized if len(normalized) == len(value) else None


def _a5_probe_coverage_pass(
    manifest: dict[str, Any],
    summary: dict[str, Any],
) -> bool:
    scope = manifest.get("evaluation_scope")
    if not isinstance(scope, dict):
        return False
    probe_sets = (
        _probe_types(scope.get("expected_probe_types")),
        _probe_types(scope.get("selected_probe_types")),
        _probe_types(scope.get("executed_probe_types")),
        _probe_types(summary.get("expected_probe_types")),
        _probe_types(summary.get("executed_probe_types")),
    )
    return (
        all(probes == CONTROL_PROBE_NAMES for probes in probe_sets)
        and scope.get("probe_selection_complete") is True
        and isinstance(summary.get("gate_checks"), dict)
        and summary["gate_checks"].get("control_probe_coverage") is True
    )


def _a5_probe_contracts_pass(summary: dict[str, Any]) -> bool:
    gate_checks = summary.get("gate_checks")
    return (
        _nonnegative_int(summary.get("termination_case_count"))
        == len(TERMINATION_CONTROL_PROBES)
        and _nonnegative_int(summary.get("termination_contract_pass_count"))
        == len(TERMINATION_CONTROL_PROBES)
        and _nonnegative_int(summary.get("duplicate_probe_case_count"))
        == len(DUPLICATE_CONTROL_PROBES)
        and _nonnegative_int(summary.get("evidence_binding_case_count"))
        == len(EVIDENCE_BINDING_CONTROL_PROBES)
        and _nonnegative_int(summary.get("checkpoint_resume_case_count"))
        == len(RESUME_CONTROL_PROBES)
        and isinstance(gate_checks, dict)
        and gate_checks.get("termination_contracts") is True
        and gate_checks.get("control_contracts") is True
    )


def _a5_evidence_binding_pass(summary: dict[str, Any]) -> bool:
    verified = _nonnegative_int(summary.get("verified_finding_count"))
    bound = _nonnegative_int(summary.get("bound_verified_finding_count"))
    return (
        verified > 0
        and bound == verified
        and summary.get("verified_finding_evidence_binding_ratio") == 1.0
    )


def _a5_resume_pass(summary: dict[str, Any]) -> bool:
    case_count = _nonnegative_int(summary.get("checkpoint_resume_case_count"))
    return (
        case_count > 0
        and _nonnegative_int(summary.get("checkpoint_resume_pass_count")) == case_count
        and summary.get("checkpoint_resume_pass_ratio") == 1.0
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
        "all_a5_contracts": enough_runs
        and all(
            _a5_contract_is_complete(run["manifest"], run["summary"])
            for run in selected_runs
        ),
        "all_a5_case_contracts": enough_runs
        and all(_a5_case_contracts_pass(run["summary"]) for run in selected_runs),
        "all_a5_probe_contracts": enough_runs
        and all(_a5_probe_contracts_pass(run["summary"]) for run in selected_runs),
        "no_graph_recursion": enough_runs
        and all(not _has_graph_recursion(run) for run in selected_runs),
        "no_duplicate_tool_violations": enough_runs
        and all(
            run["summary"].get("duplicate_tool_violation_count") == 0
            and _is_nonnegative_int(
                run["summary"].get("duplicate_tool_violation_count")
            )
            for run in selected_runs
        ),
        "no_unclassified_termination": enough_runs
        and all(
            run["summary"].get("unclassified_termination_count") == 0
            and _is_nonnegative_int(
                run["summary"].get("unclassified_termination_count")
            )
            for run in selected_runs
        ),
        "verified_finding_evidence_binding": enough_runs
        and all(_a5_evidence_binding_pass(run["summary"]) for run in selected_runs),
        "checkpoint_resume": enough_runs
        and all(_a5_resume_pass(run["summary"]) for run in selected_runs),
        "no_forbidden_tool_violations": enough_runs
        and all(
            run["summary"].get("forbidden_tool_violation_count") == 0
            and _is_nonnegative_int(
                run["summary"].get("forbidden_tool_violation_count")
            )
            for run in selected_runs
        ),
        "control_probe_coverage": enough_runs
        and all(
            _a5_probe_coverage_pass(run["manifest"], run["summary"])
            for run in selected_runs
        ),
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
                "case_count": summary.get("case_count", 0),
                "duplicate_tool_violation_count": summary.get(
                    "duplicate_tool_violation_count", 0
                ),
                "unclassified_termination_count": summary.get(
                    "unclassified_termination_count", 0
                ),
                "verified_finding_evidence_binding_ratio": summary.get(
                    "verified_finding_evidence_binding_ratio", 0
                ),
                "checkpoint_resume_pass_ratio": summary.get(
                    "checkpoint_resume_pass_ratio", 0
                ),
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
