import argparse
import json
import shlex
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval import eval_chunking
from eval import eval_llm_judge as judge_runner
from eval import eval_ragas as ragas_runner


def build_judge_formal_run(*, dataset_path: Path, baseline_run_dir: Path, chunking_run_dir: Path, judge_run_dir: Path) -> dict[str, Path]:
    return {
        "dataset_path": Path(dataset_path),
        "baseline_run_dir": Path(baseline_run_dir),
        "baseline_predictions_path": Path(baseline_run_dir) / "predictions.json",
        "baseline_metrics_path": Path(baseline_run_dir) / "metrics.json",
        "baseline_manifest_path": Path(baseline_run_dir) / "manifest.json",
        "chunking_run_dir": Path(chunking_run_dir),
        "candidate_predictions_path": Path(chunking_run_dir) / "doc_type_aware" / "predictions.json",
        "candidate_metrics_path": Path(chunking_run_dir) / "doc_type_aware" / "metrics.json",
        "chunking_manifest_path": Path(chunking_run_dir) / "manifest.json",
        "chunking_summary_path": Path(chunking_run_dir) / "comparison" / "summary.json",
        "judge_run_dir": Path(judge_run_dir),
        "judge_judgements_path": Path(judge_run_dir) / "judgements.json",
        "judge_summary_path": Path(judge_run_dir) / "summary.json",
        "judge_manifest_path": Path(judge_run_dir) / "manifest.json",
        "report_path": Path(judge_run_dir) / "test_report.md",
    }


def list_run_dirs(parent: Path) -> list[Path]:
    return sorted(
        child
        for child in Path(parent).iterdir()
        if child.is_dir() and (child / "manifest.json").exists()
    )


def discover_new_run_dir(parent: Path, previous_run_dirs: list[Path]) -> Path:
    previous_paths = {Path(path) for path in previous_run_dirs}
    new_run_dirs = [child for child in list_run_dirs(parent) if child not in previous_paths]
    if len(new_run_dirs) != 1:
        raise ValueError(f"Expected exactly one new run directory in {parent}, found {len(new_run_dirs)}")
    return new_run_dirs[0]


def run_chunking_to_dir(dataset_path: Path, out_dir: Path) -> dict[str, object]:
    argv = sys.argv[:]
    try:
        sys.argv = [
            "eval_chunking.py",
            "--dataset",
            str(dataset_path),
            "--out-dir",
            str(out_dir),
        ]
        return eval_chunking.main()
    finally:
        sys.argv = argv


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def shell_quote_path(path: Path) -> str:
    return shlex.quote(str(path))


def shell_quote_text(value: str) -> str:
    return shlex.quote(value)


def build_python_replay_command(python_code: str) -> str:
    return (
        f"cd {shell_quote_path(REPO_ROOT)} && "
        f"{shell_quote_text(sys.executable)} -c {shell_quote_text(python_code)}"
    )


def build_helper_replay_command(module_name: str, helper_name: str, run_id: str, helper_args: list[Path]) -> str:
    helper_args_text = ", ".join(f"Path({str(path.resolve())!r})" for path in helper_args)
    python_code = (
        f"from pathlib import Path; import {module_name} as module; "
        f"module.build_run_id = lambda *_: {run_id!r}; "
        f"module.{helper_name}({helper_args_text})"
    )
    return build_python_replay_command(python_code)


def build_main_replay_command(*, dataset_path: Path, chunking_out_dir: Path, run_id: str) -> str:
    absolute_dataset_path = Path(dataset_path).resolve()
    absolute_chunking_out_dir = Path(chunking_out_dir).resolve()
    python_code = (
        "import sys; "
        "from eval import eval_chunking as module; "
        f"module.build_run_id = lambda *_: {run_id!r}; "
        f"sys.argv = {repr(['eval_chunking.py', '--dataset', str(absolute_dataset_path), '--out-dir', str(absolute_chunking_out_dir)])}; "
        "module.main()"
    )
    return build_python_replay_command(python_code)


def verify_formal_run_artifacts(run: dict[str, Path]) -> list[str]:
    required_files = {
        "baseline predictions": run["baseline_predictions_path"],
        "baseline metrics": run["baseline_metrics_path"],
        "baseline manifest": run["baseline_manifest_path"],
        "candidate predictions": run["candidate_predictions_path"],
        "candidate metrics": run["candidate_metrics_path"],
        "chunking manifest": run["chunking_manifest_path"],
        "chunking comparison summary": run["chunking_summary_path"],
        "judge judgements": run["judge_judgements_path"],
        "judge summary": run["judge_summary_path"],
        "judge manifest": run["judge_manifest_path"],
    }
    missing = [f"missing {label}: {path}" for label, path in required_files.items() if not path.exists()]
    if missing:
        return missing

    failures: list[str] = []

    judge_summary = read_json(run["judge_summary_path"])
    if judge_summary.get("sample_count") != 30:
        failures.append("judge summary sample_count must be 30")

    judge_manifest = read_json(run["judge_manifest_path"])
    if judge_manifest.get("judge_prompt_version") != judge_runner.JUDGE_PROMPT_VERSION:
        failures.append("judge manifest must include the current judge_prompt_version")
    if judge_manifest.get("baseline_predictions_path") != str(run["baseline_predictions_path"]):
        failures.append("judge manifest baseline_predictions_path must point to the fresh baseline run")
    if judge_manifest.get("candidate_predictions_path") != str(run["candidate_predictions_path"]):
        failures.append("judge manifest candidate_predictions_path must point to the fresh candidate run")

    return failures


def write_test_report(
    *,
    run: dict[str, Path],
    baseline_summary: dict[str, object],
    chunking_summary: dict[str, object],
    judge_summary: dict[str, object],
    verification_failures: list[str],
) -> Path:
    status = "PASS" if not verification_failures else "FAIL"
    baseline_command = build_helper_replay_command(
        "eval.eval_ragas",
        "run_baseline_to_dir",
        run["baseline_run_dir"].name,
        [run["dataset_path"], run["baseline_run_dir"].parent],
    )
    chunking_command = build_main_replay_command(
        dataset_path=run["dataset_path"],
        chunking_out_dir=run["chunking_run_dir"].parent,
        run_id=run["chunking_run_dir"].name,
    )
    judge_command = build_helper_replay_command(
        "eval.eval_llm_judge",
        "run_pairwise_judge_to_dir",
        run["judge_run_dir"].name,
        [run["baseline_predictions_path"], run["candidate_predictions_path"], run["judge_run_dir"].parent],
    )
    report_lines = [
        "# Judge formal run test report",
        "",
        f"- Generated at: {datetime.now().isoformat(timespec='seconds')}",
        f"- Dataset: `{run['dataset_path'].resolve()}`",
        f"- Baseline run: `{run['baseline_run_dir'].resolve()}`",
        f"- Candidate run: `{run['chunking_run_dir'].resolve()}`",
        f"- Judge run: `{run['judge_run_dir'].resolve()}`",
        "",
        "## Commands",
        f"- `{baseline_command}`",
        f"- `{chunking_command}`",
        f"- `{judge_command}`",
        "",
        "## Summaries",
        f"- baseline_summary: `{json.dumps(baseline_summary, ensure_ascii=False, sort_keys=True)}`",
        f"- chunking_summary: `{json.dumps(chunking_summary, ensure_ascii=False, sort_keys=True)}`",
        f"- judge_summary: `{json.dumps(judge_summary, ensure_ascii=False, sort_keys=True)}`",
        "",
        "## Verification",
        f"- Result: **{status}**",
    ]
    if verification_failures:
        report_lines.append("- Failures:")
        report_lines.extend(f"  - {failure}" for failure in verification_failures)
    else:
        report_lines.append("- Failures: none")

    run["report_path"].parent.mkdir(parents=True, exist_ok=True)
    run["report_path"].write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return run["report_path"]


def run_formal_judge_pipeline(
    *,
    dataset_path: Path,
    baseline_out_dir: Path,
    chunking_out_dir: Path,
    judge_out_dir: Path,
) -> dict[str, object]:
    baseline_run_dirs_before = list_run_dirs(baseline_out_dir) if Path(baseline_out_dir).exists() else []
    baseline_summary = ragas_runner.run_baseline_to_dir(dataset_path, baseline_out_dir)
    baseline_run_dir = discover_new_run_dir(baseline_out_dir, baseline_run_dirs_before)

    chunking_run_dirs_before = list_run_dirs(chunking_out_dir) if Path(chunking_out_dir).exists() else []
    chunking_summary = run_chunking_to_dir(dataset_path, chunking_out_dir)
    chunking_run_dir = discover_new_run_dir(chunking_out_dir, chunking_run_dirs_before)

    run = build_judge_formal_run(
        dataset_path=dataset_path,
        baseline_run_dir=baseline_run_dir,
        chunking_run_dir=chunking_run_dir,
        judge_run_dir=Path(judge_out_dir) / "pending",
    )
    judge_run_dirs_before = list_run_dirs(judge_out_dir) if Path(judge_out_dir).exists() else []
    judge_summary = judge_runner.run_pairwise_judge_to_dir(
        run["baseline_predictions_path"],
        run["candidate_predictions_path"],
        judge_out_dir,
    )
    judge_run_dir = discover_new_run_dir(judge_out_dir, judge_run_dirs_before)
    run = build_judge_formal_run(
        dataset_path=dataset_path,
        baseline_run_dir=baseline_run_dir,
        chunking_run_dir=chunking_run_dir,
        judge_run_dir=judge_run_dir,
    )

    verification_failures = verify_formal_run_artifacts(run)
    write_test_report(
        run=run,
        baseline_summary=baseline_summary,
        chunking_summary=chunking_summary,
        judge_summary=judge_summary,
        verification_failures=verification_failures,
    )
    return {
        "baseline_summary": baseline_summary,
        "chunking_summary": chunking_summary,
        "judge_summary": judge_summary,
        "verification_failures": verification_failures,
        "run": run,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the formal judge evaluation pipeline.")
    parser.add_argument("--dataset", type=Path, default=Path("data/evaluation/gold/gold_set.json"))
    parser.add_argument("--baseline-out-dir", type=Path, default=Path("results/baseline_eval"))
    parser.add_argument("--chunking-out-dir", type=Path, default=Path("results/chunking_eval"))
    parser.add_argument("--judge-out-dir", type=Path, default=Path("results/judge_eval"))
    return parser


def main() -> dict[str, object]:
    args = build_parser().parse_args()
    summary = run_formal_judge_pipeline(
        dataset_path=args.dataset,
        baseline_out_dir=args.baseline_out_dir,
        chunking_out_dir=args.chunking_out_dir,
        judge_out_dir=args.judge_out_dir,
    )
    print(json.dumps(summary["judge_summary"], ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    main()
