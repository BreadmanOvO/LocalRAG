from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from typing import Any
from uuid import uuid4

from agent.research.models import (
    EvidenceRefDraft,
    ResearchExecutionIdentity,
    ResearchFindingDraft,
    ResearchStepCommit,
    ResearchStepDraft,
)


RUN_STATUSES = frozenset(
    {"planned", "running", "completed", "blocked", "cancelled", "failed"}
)
STEP_STATUSES = frozenset(
    {"pending", "running", "completed", "blocked", "skipped", "failed"}
)
FINDING_STATUSES = frozenset({"candidate", "verified", "rejected"})

RUN_TRANSITIONS = {
    "planned": frozenset({"running", "blocked", "cancelled", "failed"}),
    "running": frozenset({"completed", "blocked", "cancelled", "failed"}),
    "blocked": frozenset({"cancelled", "failed"}),
    "completed": frozenset(),
    "cancelled": frozenset(),
    "failed": frozenset(),
}
STEP_TRANSITIONS = {
    "pending": frozenset({"running", "skipped"}),
    "running": frozenset({"completed", "blocked", "failed"}),
    "completed": frozenset(),
    "blocked": frozenset(),
    "skipped": frozenset(),
    "failed": frozenset(),
}
FINDING_TRANSITIONS = {
    "candidate": frozenset({"verified", "rejected"}),
    "verified": frozenset({"rejected"}),
    "rejected": frozenset(),
}
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


def clean_identifier(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if len(normalized) > 128:
        raise ValueError(f"{field_name} must not exceed 128 characters")
    if not _IDENTIFIER_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{field_name} may only contain letters, numbers, '.', '_' and '-'"
        )
    return normalized


def clean_text(value: str, field_name: str, *, max_length: int = 4000) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if len(normalized) > max_length:
        raise ValueError(f"{field_name} must not exceed {max_length} characters")
    return normalized


def canonical_arguments(arguments: dict[str, Any]) -> str:
    if not isinstance(arguments, dict):
        raise TypeError("arguments must be a dictionary")
    try:
        return json.dumps(
            arguments,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("arguments must be JSON serializable") from exc


def validate_status(value: str, allowed: frozenset[str], field_name: str):
    if value not in allowed:
        raise ValueError(f"unsupported {field_name}: {value}")
    return value


def validate_revision(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("expected_revision must be a non-negative integer")
    return value


def validate_counter(value: int, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def normalize_execution_identity(
    identity: ResearchExecutionIdentity,
) -> ResearchExecutionIdentity:
    if not isinstance(identity, ResearchExecutionIdentity):
        raise TypeError("identity must be a ResearchExecutionIdentity")
    corpus_fingerprint = clean_text(
        identity.corpus_fingerprint,
        "corpus_fingerprint",
        max_length=256,
    )
    registry_fingerprint = clean_text(
        identity.registry_fingerprint,
        "registry_fingerprint",
        max_length=256,
    )
    code_revision = clean_text(
        identity.code_revision,
        "code_revision",
        max_length=256,
    )
    if not corpus_fingerprint or not registry_fingerprint or not code_revision:
        raise ValueError("research execution identity must be complete")
    if not isinstance(identity.code_dirty, bool):
        raise TypeError("code_dirty must be a boolean")
    return ResearchExecutionIdentity(
        corpus_fingerprint=corpus_fingerprint,
        registry_fingerprint=registry_fingerprint,
        code_revision=code_revision,
        code_dirty=identity.code_dirty,
    )


def step_commit_fingerprint(commit: ResearchStepCommit) -> str:
    if not isinstance(commit, ResearchStepCommit):
        raise TypeError("commit must be a ResearchStepCommit")
    payload = asdict(commit)
    payload.pop("commit_id", None)
    try:
        encoded = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("step commit must be JSON serializable") from exc
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def normalize_step_draft(
    draft: ResearchStepDraft,
) -> tuple[ResearchStepDraft, str]:
    if not isinstance(draft, ResearchStepDraft):
        raise TypeError("steps must contain ResearchStepDraft values")
    objective = clean_text(draft.objective, "objective")
    action = clean_identifier(draft.action, "action")
    if not objective:
        raise ValueError("objective must not be empty")
    arguments_json = canonical_arguments(draft.arguments)
    return ResearchStepDraft(objective, action, json.loads(arguments_json)), arguments_json


def normalize_evidence_draft(
    draft: EvidenceRefDraft,
) -> tuple[str, EvidenceRefDraft]:
    if not isinstance(draft, EvidenceRefDraft):
        raise TypeError("evidence_refs must contain EvidenceRefDraft values")
    evidence_id = clean_identifier(
        draft.evidence_id or new_id("evidence"),
        "evidence_id",
    )
    source_id = clean_text(draft.source_id, "source_id", max_length=512)
    locator = clean_text(draft.locator, "locator", max_length=1000) or "unknown"
    chunk_strategy = (
        clean_text(draft.chunk_strategy, "chunk_strategy", max_length=128) or "unknown"
    )
    if not source_id:
        raise ValueError("source_id must not be empty")
    if draft.chunk_order is not None and (
        isinstance(draft.chunk_order, bool)
        or not isinstance(draft.chunk_order, int)
        or draft.chunk_order < 0
    ):
        raise ValueError("chunk_order must be a non-negative integer or None")
    return evidence_id, EvidenceRefDraft(
        source_id=source_id,
        locator=locator,
        chunk_order=draft.chunk_order,
        chunk_strategy=chunk_strategy,
        evidence_id=evidence_id,
    )

def normalize_finding_draft(
    draft: ResearchFindingDraft,
) -> tuple[str, ResearchFindingDraft]:
    if not isinstance(draft, ResearchFindingDraft):
        raise TypeError("findings must contain ResearchFindingDraft values")
    finding_id = clean_identifier(
        draft.finding_id or new_id("finding"),
        "finding_id",
    )
    text = clean_text(draft.text, "finding text")
    if not text:
        raise ValueError("finding text must not be empty")
    status = validate_status(draft.status, FINDING_STATUSES, "finding status")
    evidence_ids = tuple(
        clean_identifier(item, "evidence_id") for item in draft.evidence_ids
    )
    if len(set(evidence_ids)) != len(evidence_ids):
        raise ValueError("finding evidence_ids must be unique")
    if status == "verified" and not evidence_ids:
        raise ValueError("verified findings require at least one evidence_id")
    return finding_id, ResearchFindingDraft(
        text=text,
        status=status,
        evidence_ids=evidence_ids,
        finding_id=finding_id,
    )
