-- v1.8 D05-D09 PostgreSQL baseline.
-- IDs remain text so legacy mappings and prefixed Runtime IDs can coexist.
-- This migration creates storage only; it does not import or execute old data.

CREATE TABLE IF NOT EXISTS runtime_schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS spaces (
    space_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version > 0)
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id TEXT PRIMARY KEY,
    space_id TEXT NOT NULL REFERENCES spaces(space_id),
    status TEXT NOT NULL CHECK (status IN ('active', 'archived', 'deleted')),
    title TEXT NOT NULL DEFAULT '',
    room_sequence BIGINT NOT NULL DEFAULT 0 CHECK (room_sequence >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version > 0)
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(room_id),
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'completed', 'blocked', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version > 0)
);

CREATE TABLE IF NOT EXISTS task_memory_items (
    item_id BIGSERIAL PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    category TEXT NOT NULL CHECK (category IN (
        'searched_query', 'retrieved_source', 'confirmed_source',
        'finding', 'evidence_gap', 'open_question'
    )),
    value TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (task_id, category, value)
);

CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(room_id),
    task_id TEXT REFERENCES tasks(task_id),
    turn_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('saved', 'queued', 'applied', 'rejected', 'tombstoned')),
    content_sha256 TEXT NOT NULL,
    room_sequence BIGINT NOT NULL CHECK (room_sequence > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (room_id, room_sequence)
);

-- Legacy file-backed messages may lack turn/sequence metadata. They are
-- staged here for review instead of being assigned invented runtime IDs.
CREATE TABLE IF NOT EXISTS legacy_message_staging (
    staging_id BIGSERIAL PRIMARY KEY,
    source_store TEXT NOT NULL,
    source_message_id TEXT NOT NULL,
    room_id TEXT REFERENCES rooms(room_id),
    raw_content TEXT NOT NULL,
    source_hash TEXT NOT NULL,
    migration_status TEXT NOT NULL CHECK (migration_status IN ('staged', 'mapped', 'needs_review', 'rejected')),
    warning TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source_store, source_message_id)
);

CREATE TABLE IF NOT EXISTS message_revisions (
    revision_id BIGSERIAL PRIMARY KEY,
    message_id TEXT NOT NULL REFERENCES messages(message_id) ON DELETE CASCADE,
    revision_no INTEGER NOT NULL CHECK (revision_no > 0),
    content TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('partial', 'complete', 'rejected')),
    content_sha256 TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (message_id, revision_no)
);

CREATE TABLE IF NOT EXISTS plans (
    plan_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(task_id),
    plan_revision INTEGER NOT NULL CHECK (plan_revision > 0),
    plan_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (task_id, plan_revision)
);

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    space_id TEXT NOT NULL REFERENCES spaces(space_id),
    room_id TEXT NOT NULL REFERENCES rooms(room_id),
    task_id TEXT NOT NULL REFERENCES tasks(task_id),
    plan_id TEXT NOT NULL REFERENCES plans(plan_id),
    plan_revision INTEGER NOT NULL CHECK (plan_revision > 0),
    control_epoch BIGINT NOT NULL DEFAULT 0 CHECK (control_epoch >= 0),
    status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'paused', 'needs_input', 'completed', 'failed', 'cancelled')),
    source_run_id TEXT REFERENCES runs(run_id),
    trigger_turn_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version > 0)
);

CREATE TABLE IF NOT EXISTS steps (
    step_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    position INTEGER NOT NULL CHECK (position > 0),
    objective TEXT NOT NULL,
    action TEXT NOT NULL,
    arguments_json JSONB,
    result_summary TEXT,
    error_code TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    status TEXT NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'blocked', 'skipped', 'failed')),
    plan_revision INTEGER NOT NULL CHECK (plan_revision > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version > 0),
    UNIQUE (run_id, position)
);

CREATE TABLE IF NOT EXISTS attempts (
    attempt_id TEXT PRIMARY KEY,
    step_id TEXT NOT NULL REFERENCES steps(step_id),
    run_id TEXT NOT NULL REFERENCES runs(run_id),
    plan_revision INTEGER NOT NULL CHECK (plan_revision > 0),
    control_epoch BIGINT NOT NULL CHECK (control_epoch >= 0),
    fencing_token BIGINT NOT NULL CHECK (fencing_token >= 0),
    worker_id TEXT NOT NULL DEFAULT '',
    lease_expires_at TIMESTAMPTZ,
    operation_id TEXT,
    status TEXT NOT NULL CHECK (status IN ('leased', 'running', 'succeeded', 'failed', 'expired', 'cancelled', 'late_audit', 'rejected')),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    UNIQUE (step_id, attempt_id)
);

CREATE TABLE IF NOT EXISTS run_events (
    event_id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(room_id) ON DELETE CASCADE,
    task_id TEXT REFERENCES tasks(task_id),
    run_id TEXT REFERENCES runs(run_id),
    step_id TEXT REFERENCES steps(step_id),
    attempt_id TEXT REFERENCES attempts(attempt_id),
    event_type TEXT NOT NULL,
    room_sequence BIGINT NOT NULL CHECK (room_sequence > 0),
    run_sequence BIGINT NOT NULL DEFAULT 0 CHECK (run_sequence >= 0),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    caused_by JSONB NOT NULL DEFAULT '[]'::jsonb,
    consumes JSONB NOT NULL DEFAULT '[]'::jsonb,
    produces JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (room_id, room_sequence)
);

CREATE TABLE IF NOT EXISTS budget_accounts (
    scope_id TEXT PRIMARY KEY,
    budget_limit NUMERIC(20, 6) NOT NULL CHECK (budget_limit >= 0),
    reserved NUMERIC(20, 6) NOT NULL DEFAULT 0 CHECK (reserved >= 0),
    consumed NUMERIC(20, 6) NOT NULL DEFAULT 0 CHECK (consumed >= 0),
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version > 0)
);

CREATE TABLE IF NOT EXISTS budget_reservations (
    reservation_id TEXT PRIMARY KEY,
    scope_id TEXT NOT NULL REFERENCES budget_accounts(scope_id),
    operation_id TEXT NOT NULL,
    amount NUMERIC(20, 6) NOT NULL CHECK (amount >= 0),
    request_hash TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('reserved', 'consumed', 'released', 'unknown')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (operation_id)
);

CREATE TABLE IF NOT EXISTS budget_consumption (
    consumption_id TEXT PRIMARY KEY,
    reservation_id TEXT NOT NULL REFERENCES budget_reservations(reservation_id),
    operation_id TEXT NOT NULL,
    amount NUMERIC(20, 6) NOT NULL CHECK (amount >= 0),
    provider_call_id TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tool_operations (
    operation_id TEXT PRIMARY KEY,
    request_hash TEXT NOT NULL,
    effect_kind TEXT NOT NULL,
    idempotency_support BOOLEAN NOT NULL,
    reconcile_support BOOLEAN NOT NULL,
    reservation_id TEXT NOT NULL REFERENCES budget_reservations(reservation_id),
    attempt_count INTEGER NOT NULL DEFAULT 1 CHECK (attempt_count > 0),
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed', 'unknown', 'reconciled')),
    effect_state TEXT NOT NULL CHECK (effect_state IN ('none', 'not_applied', 'applied', 'unknown')),
    result_json JSONB,
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS persona_snapshots (
    binding_id TEXT PRIMARY KEY,
    space_id TEXT NOT NULL REFERENCES spaces(space_id),
    room_id TEXT REFERENCES rooms(room_id),
    agent_id TEXT,
    persona_id TEXT NOT NULL,
    version TEXT NOT NULL,
    profile_json JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS room_memberships (
    membership_id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL REFERENCES rooms(room_id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    binding_id TEXT REFERENCES persona_snapshots(binding_id),
    status TEXT NOT NULL CHECK (status IN ('active', 'left', 'removed')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    row_version BIGINT NOT NULL DEFAULT 1 CHECK (row_version > 0),
    UNIQUE (room_id, agent_id, joined_at)
);

CREATE TABLE IF NOT EXISTS legacy_id_map (
    mapping_id BIGSERIAL PRIMARY KEY,
    source_store TEXT NOT NULL,
    legacy_type TEXT NOT NULL,
    legacy_id TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT,
    mapping_status TEXT NOT NULL CHECK (mapping_status IN ('mapped', 'missing', 'needs_review')),
    reason TEXT NOT NULL DEFAULT '',
    source_hash TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source_store, legacy_type, legacy_id)
);

CREATE TABLE IF NOT EXISTS import_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    source_store TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    source_bytes BIGINT NOT NULL CHECK (source_bytes >= 0),
    row_counts JSONB NOT NULL,
    missing_fields JSONB NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO runtime_schema_migrations(version, name)
VALUES (1, 'v1.8-d05-runtime-baseline')
ON CONFLICT (version) DO NOTHING;
