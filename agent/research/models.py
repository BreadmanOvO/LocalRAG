from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


RunStatus = Literal[
    "planned",
    "running",
    "completed",
    "blocked",
    "cancelled",
    "failed",
]
StepStatus = Literal[
    "pending",
    "running",
    "completed",
    "blocked",
    "skipped",
    "failed",
]
FindingStatus = Literal["candidate", "verified", "rejected"]


@dataclass(frozen=True)
class ResearchStepDraft:
    objective: str
    action: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvidenceRefDraft:
    source_id: str
    locator: str = "unknown"
    chunk_order: int | None = None
    chunk_strategy: str = "unknown"
    evidence_id: str | None = None


@dataclass(frozen=True)
class ResearchFindingDraft:
    text: str
    status: FindingStatus = "candidate"
    evidence_ids: tuple[str, ...] = ()
    finding_id: str | None = None


@dataclass(frozen=True)
class ResearchStepTransition:
    status: StepStatus
    result_summary: str = ""
    error_code: str = ""
    tool_call_count: int = 0
    model_call_count: int = 0


@dataclass(frozen=True)
class ResearchStepCommit:
    result_summary: str
    evidence_refs: tuple[EvidenceRefDraft, ...] = ()
    findings: tuple[ResearchFindingDraft, ...] = ()
    commit_id: str | None = None
    tool_call_count: int = 0
    model_call_count: int = 0


@dataclass(frozen=True)
class ResearchExecutionIdentity:
    corpus_fingerprint: str
    registry_fingerprint: str
    code_revision: str
    code_dirty: bool = False


@dataclass(frozen=True)
class ResearchRun:
    run_id: str
    task_id: str
    goal: str
    status: RunStatus
    current_step_id: str | None
    plan_revision: int
    revision: int
    tool_call_count: int
    model_call_count: int
    no_progress_count: int
    stop_reason: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ResearchStep:
    step_id: str
    run_id: str
    position: int
    objective: str
    action: str
    arguments: dict[str, Any]
    status: StepStatus
    attempt_count: int
    result_summary: str
    error_code: str
    evidence_ids: tuple[str, ...]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    run_id: str
    step_id: str
    source_id: str
    locator: str
    chunk_order: int | None
    chunk_strategy: str
    created_at: str


@dataclass(frozen=True)
class ResearchFinding:
    finding_id: str
    run_id: str
    text: str
    status: FindingStatus
    evidence_ids: tuple[str, ...]
    created_by_step_id: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ResearchPlanSnapshot:
    run: ResearchRun
    steps: tuple[ResearchStep, ...]
    evidence_refs: tuple[EvidenceRef, ...]
    findings: tuple[ResearchFinding, ...]
