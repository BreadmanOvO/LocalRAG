from __future__ import annotations

import json
import sqlite3

from agent.research.models import EvidenceRef, ResearchFinding, ResearchRun, ResearchStep


def run_from_row(row: sqlite3.Row) -> ResearchRun:
    return ResearchRun(
        run_id=row["run_id"],
        task_id=row["task_id"],
        goal=row["goal"],
        status=row["status"],
        current_step_id=row["current_step_id"],
        plan_revision=int(row["plan_revision"]),
        revision=int(row["revision"]),
        tool_call_count=int(row["tool_call_count"]),
        model_call_count=int(row["model_call_count"]),
        no_progress_count=int(row["no_progress_count"]),
        stop_reason=row["stop_reason"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )

def step_from_row(row: sqlite3.Row, evidence_ids: tuple[str, ...]) -> ResearchStep:
    return ResearchStep(
        step_id=row["step_id"],
        run_id=row["run_id"],
        position=int(row["position"]),
        objective=row["objective"],
        action=row["action"],
        arguments=json.loads(row["arguments_json"]),
        status=row["status"],
        attempt_count=int(row["attempt_count"]),
        result_summary=row["result_summary"],
        error_code=row["error_code"],
        evidence_ids=evidence_ids,
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def evidence_from_row(row: sqlite3.Row) -> EvidenceRef:
    return EvidenceRef(
        evidence_id=row["evidence_id"],
        run_id=row["run_id"],
        step_id=row["step_id"],
        source_id=row["source_id"],
        locator=row["locator"],
        chunk_order=row["chunk_order"],
        chunk_strategy=row["chunk_strategy"],
        created_at=row["created_at"],
    )


def finding_from_row(
    row: sqlite3.Row,
    evidence_ids: tuple[str, ...],
) -> ResearchFinding:
    return ResearchFinding(
        finding_id=row["finding_id"],
        run_id=row["run_id"],
        text=row["text"],
        status=row["status"],
        evidence_ids=evidence_ids,
        created_by_step_id=row["created_by_step_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
