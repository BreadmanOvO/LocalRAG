from __future__ import annotations

import sqlite3


MIGRATIONS = (
    (1, "v1.5-a2-research-state"),
    (2, "v1.5-a3-research-recovery"),
    (3, "v1.5-a4-research-usage-checkpoints"),
)

RESEARCH_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS research_runs (
    run_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    goal TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('planned', 'running', 'completed', 'blocked', 'cancelled', 'failed')
    ),
    current_step_id TEXT,
    plan_revision INTEGER NOT NULL CHECK (plan_revision > 0),
    revision INTEGER NOT NULL CHECK (revision >= 0),
    tool_call_count INTEGER NOT NULL DEFAULT 0 CHECK (tool_call_count >= 0),
    model_call_count INTEGER NOT NULL DEFAULT 0 CHECK (model_call_count >= 0),
    no_progress_count INTEGER NOT NULL DEFAULT 0 CHECK (no_progress_count >= 0),
    stop_reason TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_research_runs_task_updated
ON research_runs(task_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS research_steps (
    step_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    position INTEGER NOT NULL CHECK (position > 0),
    objective TEXT NOT NULL,
    action TEXT NOT NULL,
    arguments_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('pending', 'running', 'completed', 'blocked', 'skipped', 'failed')
    ),
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    result_summary TEXT NOT NULL DEFAULT '',
    error_code TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(run_id, position),
    UNIQUE(run_id, step_id),
    FOREIGN KEY(run_id) REFERENCES research_runs(run_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_research_steps_run_status_position
ON research_steps(run_id, status, position);

CREATE TABLE IF NOT EXISTS research_evidence_refs (
    evidence_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    locator TEXT NOT NULL,
    chunk_order INTEGER,
    chunk_strategy TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(run_id, evidence_id),
    UNIQUE(run_id, step_id, source_id, locator, chunk_order, chunk_strategy),
    FOREIGN KEY(run_id, step_id)
        REFERENCES research_steps(run_id, step_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_research_evidence_run_step
ON research_evidence_refs(run_id, step_id);

CREATE TABLE IF NOT EXISTS research_findings (
    finding_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    text TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('candidate', 'verified', 'rejected')
    ),
    primary_evidence_id TEXT,
    created_by_step_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(run_id, finding_id),
    CHECK (status != 'verified' OR primary_evidence_id IS NOT NULL),
    FOREIGN KEY(run_id, created_by_step_id)
        REFERENCES research_steps(run_id, step_id) ON DELETE CASCADE,
    FOREIGN KEY(run_id, primary_evidence_id)
        REFERENCES research_evidence_refs(run_id, evidence_id)
);

CREATE INDEX IF NOT EXISTS idx_research_findings_run_status
ON research_findings(run_id, status);

CREATE TABLE IF NOT EXISTS research_finding_evidence (
    run_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    evidence_id TEXT NOT NULL,
    PRIMARY KEY(finding_id, evidence_id),
    FOREIGN KEY(run_id, finding_id)
        REFERENCES research_findings(run_id, finding_id) ON DELETE CASCADE,
    FOREIGN KEY(run_id, evidence_id)
        REFERENCES research_evidence_refs(run_id, evidence_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS research_run_identities (
    run_id TEXT PRIMARY KEY,
    corpus_fingerprint TEXT NOT NULL,
    registry_fingerprint TEXT NOT NULL,
    code_revision TEXT NOT NULL,
    code_dirty INTEGER NOT NULL CHECK (code_dirty IN (0, 1)),
    created_at TEXT NOT NULL,
    FOREIGN KEY(run_id) REFERENCES research_runs(run_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS research_step_commits (
    run_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    commit_id TEXT NOT NULL,
    payload_fingerprint TEXT NOT NULL,
    committed_revision INTEGER NOT NULL CHECK (committed_revision > 0),
    created_at TEXT NOT NULL,
    PRIMARY KEY(run_id, step_id),
    UNIQUE(run_id, commit_id),
    FOREIGN KEY(run_id, step_id)
        REFERENCES research_steps(run_id, step_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS research_step_usage_events (
    run_id TEXT NOT NULL,
    step_id TEXT NOT NULL,
    attempt_count INTEGER NOT NULL CHECK (attempt_count > 0),
    event_index INTEGER NOT NULL CHECK (event_index > 0),
    event_kind TEXT NOT NULL CHECK (
        event_kind IN ('tool_started', 'model_completed')
    ),
    created_at TEXT NOT NULL,
    PRIMARY KEY(run_id, step_id, attempt_count, event_index),
    FOREIGN KEY(run_id, step_id)
        REFERENCES research_steps(run_id, step_id) ON DELETE CASCADE
);
"""


def apply_research_migration(connection: sqlite3.Connection, applied_at: str) -> None:
    connection.executescript(RESEARCH_SCHEMA)
    connection.executemany(
        """
        INSERT OR IGNORE INTO agent_schema_migrations(version, name, applied_at)
        VALUES (?, ?, ?)
        """,
        ((version, name, applied_at) for version, name in MIGRATIONS),
    )
