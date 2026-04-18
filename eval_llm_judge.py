import argparse
import json
from pathlib import Path
from typing import Any

from eval_ragas import write_json


def load_predictions(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_judgements(rows: list[dict[str, Any]]) -> dict[str, Any]:
    sample_count = len(rows)
    candidate_win_count = sum(1 for row in rows if row.get("winner") == "candidate")
    baseline_win_count = sum(1 for row in rows if row.get("winner") == "baseline")
    tie_count = sum(1 for row in rows if row.get("winner") == "tie")

    return {
        "sample_count": sample_count,
        "candidate_win_count": candidate_win_count,
        "baseline_win_count": baseline_win_count,
        "tie_count": tie_count,
    }


def run_self_comparison(predictions_path: Path, output_path: Path) -> dict[str, Any]:
    predictions = load_predictions(predictions_path)
    rows = [
        {
            "id": row["id"],
            "winner": "tie",
            "reason": "Self-comparison baseline run",
        }
        for row in predictions
    ]
    summary = summarize_judgements(rows)
    write_json(output_path, {"summary": summary, "rows": rows})
    return summary


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Run self-comparison judge scaffold")
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    summary = run_self_comparison(args.predictions, args.out)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    main()
