import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.runtime_keys import load_runtime_config
from config.provider_factory import build_chat_model
from eval.eval_ragas import write_json

JUDGE_PROMPT_VERSION = "v1.1-pairwise-judge"


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



def _build_judge_model() -> tuple[Any, Any]:
    runtime_config = load_runtime_config()
    return build_chat_model(runtime_config, temperature=0), runtime_config



def _serialize_prediction(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "answer": row.get("answer", ""),
        "retrieved_rows": row.get("retrieved_rows", []),
        "evidence": row.get("evidence", []),
        "metadata": row.get("metadata", {}),
    }



def _build_judge_prompt(baseline_row: dict[str, Any], candidate_row: dict[str, Any]) -> str:
    payload = {
        "question": baseline_row.get("question", ""),
        "reference_answer": baseline_row.get("reference_answer", ""),
        "baseline": _serialize_prediction(baseline_row),
        "candidate": _serialize_prediction(candidate_row),
    }
    return (
        "你是自动驾驶 RAG 的 pairwise 裁判。请只依据 question、reference_answer、retrieved_rows、evidence 和 answer 做判断。"
        "优先比较：1) 是否更接近 reference_answer；2) 是否更忠于 evidence/retrieved_rows；3) 是否更少出现无依据扩写。"
        "不要奖励更长的答案；只有在两边质量无法区分时才输出 tie。"
        "只输出一个 JSON 对象，不要输出 markdown，不要输出额外解释。"
        "JSON 结构必须是 {\"winner\":\"baseline|candidate|tie\",\"reason\":\"...\"}。\n\n"
        f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
    )



def _extract_response_text(response: Any) -> str:
    if isinstance(response, str):
        return response
    content = getattr(response, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content)



def _extract_json_payload(response_text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    for index, char in enumerate(response_text):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(response_text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise ValueError("judge response must contain a JSON object")



def _parse_judge_response(response_text: str) -> tuple[str, str]:
    payload = _extract_json_payload(response_text)
    winner = payload.get("winner", "tie")
    if winner not in {"baseline", "candidate", "tie"}:
        raise ValueError(f"invalid judge winner: {winner}")
    reason = payload.get("reason", "")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("judge reason must be a non-empty string")
    return winner, reason.strip()



def _judge_pair(model: Any, baseline_row: dict[str, Any], candidate_row: dict[str, Any]) -> tuple[str, str]:
    prompt = _build_judge_prompt(baseline_row, candidate_row)
    response = model.invoke(prompt)
    return _parse_judge_response(_extract_response_text(response))


def _index_predictions(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for row in rows:
        sample_id = row["id"]
        if sample_id in indexed:
            raise ValueError("prediction files must not contain duplicate sample ids")
        indexed[sample_id] = row
    return indexed


def run_pairwise_judge(
    baseline_predictions_path: Path,
    candidate_predictions_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    baseline_predictions = load_predictions(baseline_predictions_path)
    candidate_predictions = load_predictions(candidate_predictions_path)
    baseline_by_id = _index_predictions(baseline_predictions)
    candidate_by_id = _index_predictions(candidate_predictions)
    if set(baseline_by_id) != set(candidate_by_id):
        raise ValueError("baseline and candidate predictions must contain the same sample ids")

    judge_model, _ = _build_judge_model()
    rows = []
    for sample_id in sorted(baseline_by_id):
        baseline_row = baseline_by_id[sample_id]
        candidate_row = candidate_by_id[sample_id]
        winner, reason = _judge_pair(judge_model, baseline_row, candidate_row)
        rows.append(
            {
                "id": sample_id,
                "question": baseline_row.get("question", ""),
                "reference_answer": baseline_row.get("reference_answer", ""),
                "baseline_answer": baseline_row.get("answer", ""),
                "candidate_answer": candidate_row.get("answer", ""),
                "winner": winner,
                "reason": reason,
            }
        )

    summary = summarize_judgements(rows)
    write_json(output_path, {"summary": summary, "rows": rows})
    return summary


def build_run_id(baseline_predictions_path: Path, candidate_predictions_path: Path) -> str:
    return f"{baseline_predictions_path.stem}-vs-{candidate_predictions_path.stem}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def build_manifest(
    *,
    run_id: str,
    baseline_predictions_path: Path,
    candidate_predictions_path: Path,
    runtime_config: Any,
) -> dict[str, Any]:
    return {
        "contract_version": "v1.1",
        "pipeline": "judge_eval",
        "run_id": run_id,
        "baseline_predictions_path": str(baseline_predictions_path),
        "candidate_predictions_path": str(candidate_predictions_path),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runner_script": "eval/eval_llm_judge.py",
        "provider": runtime_config.provider,
        "chat_model_name": runtime_config.chat_model_name,
        "judge_prompt_version": JUDGE_PROMPT_VERSION,
    }


def run_pairwise_judge_to_dir(
    baseline_predictions_path: Path | str,
    candidate_predictions_path: Path | str,
    out_dir: Path | str,
) -> dict[str, Any]:
    baseline_predictions_path = Path(baseline_predictions_path)
    candidate_predictions_path = Path(candidate_predictions_path)
    out_dir = Path(out_dir)
    runtime_config = load_runtime_config()
    run_id = build_run_id(baseline_predictions_path, candidate_predictions_path)
    run_dir = out_dir / run_id
    judgements_path = run_dir / "judgements.json"
    summary = run_pairwise_judge(
        baseline_predictions_path,
        candidate_predictions_path,
        judgements_path,
    )
    write_json(run_dir / "summary.json", summary)
    write_json(
        run_dir / "manifest.json",
        build_manifest(
            run_id=run_id,
            baseline_predictions_path=baseline_predictions_path,
            candidate_predictions_path=candidate_predictions_path,
            runtime_config=runtime_config,
        ),
    )
    return summary


def main() -> dict[str, Any]:
    parser = argparse.ArgumentParser(description="Run pairwise LLM judge")
    parser.add_argument("--baseline-predictions", required=True, type=Path)
    parser.add_argument("--candidate-predictions", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    summary = run_pairwise_judge(
        args.baseline_predictions,
        args.candidate_predictions,
        args.out,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == "__main__":
    main()
