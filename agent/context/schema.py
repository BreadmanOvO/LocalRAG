from __future__ import annotations

import sqlite3


MIGRATION_VERSION = 4
MIGRATION_NAME = "v1.6-c2-conversation-context"

_MIGRATION_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS agent_schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL
)
"""

_CONVERSATION_TABLE_DDLS = (
    """
    CREATE TABLE IF NOT EXISTS conversation_summary_state (
        session_id TEXT PRIMARY KEY,
        revision INTEGER NOT NULL CHECK (revision > 0),
        summary_json TEXT NOT NULL,
        covered_message_ids_json TEXT NOT NULL,
        tokens_before INTEGER NOT NULL CHECK (tokens_before >= 0),
        tokens_after INTEGER NOT NULL CHECK (tokens_after >= 0),
        messages_before INTEGER NOT NULL CHECK (messages_before >= 0),
        messages_after INTEGER NOT NULL CHECK (messages_after >= 0),
        summary_model TEXT NOT NULL,
        compression_reason TEXT NOT NULL,
        fallback_reason TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS conversation_summary_events (
        session_id TEXT NOT NULL,
        revision INTEGER NOT NULL CHECK (revision > 0),
        summary_json TEXT NOT NULL,
        covered_message_ids_json TEXT NOT NULL,
        tokens_before INTEGER NOT NULL,
        tokens_after INTEGER NOT NULL,
        messages_before INTEGER NOT NULL,
        messages_after INTEGER NOT NULL,
        summary_model TEXT NOT NULL,
        compression_reason TEXT NOT NULL,
        fallback_reason TEXT NOT NULL,
        created_at TEXT NOT NULL,
        PRIMARY KEY(session_id, revision)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS conversation_token_observations (
        session_id TEXT NOT NULL,
        revision INTEGER NOT NULL CHECK (revision > 0),
        request_id TEXT NOT NULL,
        estimated_input_tokens INTEGER NOT NULL CHECK (estimated_input_tokens >= 0),
        actual_input_tokens INTEGER NOT NULL CHECK (actual_input_tokens >= 0),
        actual_output_tokens INTEGER NOT NULL CHECK (actual_output_tokens >= 0),
        created_at TEXT NOT NULL,
        PRIMARY KEY(session_id, request_id),
        FOREIGN KEY(session_id, revision)
            REFERENCES conversation_summary_events(session_id, revision) ON DELETE CASCADE
    )
    """,
)

_COLUMN_CONTRACTS = {
    "conversation_summary_state": (
        ("session_id", "TEXT", 0, 1),
        ("revision", "INTEGER", 1, 0),
        ("summary_json", "TEXT", 1, 0),
        ("covered_message_ids_json", "TEXT", 1, 0),
        ("tokens_before", "INTEGER", 1, 0),
        ("tokens_after", "INTEGER", 1, 0),
        ("messages_before", "INTEGER", 1, 0),
        ("messages_after", "INTEGER", 1, 0),
        ("summary_model", "TEXT", 1, 0),
        ("compression_reason", "TEXT", 1, 0),
        ("fallback_reason", "TEXT", 1, 0),
        ("created_at", "TEXT", 1, 0),
        ("updated_at", "TEXT", 1, 0),
    ),
    "conversation_summary_events": (
        ("session_id", "TEXT", 1, 1),
        ("revision", "INTEGER", 1, 2),
        ("summary_json", "TEXT", 1, 0),
        ("covered_message_ids_json", "TEXT", 1, 0),
        ("tokens_before", "INTEGER", 1, 0),
        ("tokens_after", "INTEGER", 1, 0),
        ("messages_before", "INTEGER", 1, 0),
        ("messages_after", "INTEGER", 1, 0),
        ("summary_model", "TEXT", 1, 0),
        ("compression_reason", "TEXT", 1, 0),
        ("fallback_reason", "TEXT", 1, 0),
        ("created_at", "TEXT", 1, 0),
    ),
    "conversation_token_observations": (
        ("session_id", "TEXT", 1, 1),
        ("revision", "INTEGER", 1, 0),
        ("request_id", "TEXT", 1, 2),
        ("estimated_input_tokens", "INTEGER", 1, 0),
        ("actual_input_tokens", "INTEGER", 1, 0),
        ("actual_output_tokens", "INTEGER", 1, 0),
        ("created_at", "TEXT", 1, 0),
    ),
}

_CHECK_CONTRACTS = {
    "conversation_summary_state": (
        "revision integer not null check (revision > 0)",
        "tokens_before integer not null check (tokens_before >= 0)",
        "tokens_after integer not null check (tokens_after >= 0)",
        "messages_before integer not null check (messages_before >= 0)",
        "messages_after integer not null check (messages_after >= 0)",
    ),
    "conversation_summary_events": (
        "revision integer not null check (revision > 0)",
    ),
    "conversation_token_observations": (
        "revision integer not null check (revision > 0)",
        "estimated_input_tokens integer not null check (estimated_input_tokens >= 0)",
        "actual_input_tokens integer not null check (actual_input_tokens >= 0)",
        "actual_output_tokens integer not null check (actual_output_tokens >= 0)",
    ),
}

_OBSERVATION_FOREIGN_KEY = (
    (
        0,
        0,
        "conversation_summary_events",
        "session_id",
        "session_id",
        "NO ACTION",
        "CASCADE",
    ),
    (
        0,
        1,
        "conversation_summary_events",
        "revision",
        "revision",
        "NO ACTION",
        "CASCADE",
    ),
)


def _normalize_sql(value: str) -> str:
    return " ".join(value.lower().split())


def _validate_migration_identity(connection: sqlite3.Connection) -> bool:
    rows = connection.execute(
        """
        SELECT version, name FROM agent_schema_migrations
        WHERE version = ? OR name = ?
        """,
        (MIGRATION_VERSION, MIGRATION_NAME),
    ).fetchall()
    if not rows:
        return False
    if len(rows) == 1 and (int(rows[0][0]), rows[0][1]) == (
        MIGRATION_VERSION,
        MIGRATION_NAME,
    ):
        return True
    identities = [(int(row[0]), row[1]) for row in rows]
    raise RuntimeError(f"migration identity conflict: {identities}")


def _validate_table_columns(connection: sqlite3.Connection, table_name: str) -> None:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    actual = tuple(
        (row[1], str(row[2]).upper(), int(row[3]), int(row[5])) for row in rows
    )
    expected = _COLUMN_CONTRACTS[table_name]
    if actual != expected:
        raise RuntimeError(
            f"incompatible schema for {table_name}: expected {expected}, actual {actual}"
        )


def _validate_table_checks(connection: sqlite3.Connection, table_name: str) -> None:
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    if row is None or not isinstance(row[0], str):
        raise RuntimeError(f"incompatible schema for {table_name}: table is missing")
    table_sql = _normalize_sql(row[0])
    missing = [
        contract
        for contract in _CHECK_CONTRACTS[table_name]
        if contract not in table_sql
    ]
    if missing:
        raise RuntimeError(
            f"incompatible schema for {table_name}: missing CHECK constraints {missing}"
        )


def _validate_observation_foreign_key(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        "PRAGMA foreign_key_list(conversation_token_observations)"
    ).fetchall()
    actual = tuple(
        (
            int(row[0]),
            int(row[1]),
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
        )
        for row in rows
    )
    if actual != _OBSERVATION_FOREIGN_KEY:
        raise RuntimeError(
            "incompatible schema for conversation_token_observations: "
            f"expected foreign key {_OBSERVATION_FOREIGN_KEY}, actual {actual}"
        )


def _validate_conversation_schema(connection: sqlite3.Connection) -> None:
    for table_name in _COLUMN_CONTRACTS:
        _validate_table_columns(connection, table_name)
        _validate_table_checks(connection, table_name)
    _validate_observation_foreign_key(connection)


def apply_conversation_context_migration(
    connection: sqlite3.Connection,
    applied_at: str,
) -> None:
    if connection.in_transaction:
        raise RuntimeError("conversation migration requires an idle connection")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("BEGIN IMMEDIATE")
    try:
        connection.execute(_MIGRATION_TABLE_DDL)
        already_registered = _validate_migration_identity(connection)
        if already_registered:
            _validate_conversation_schema(connection)
        else:
            for statement in _CONVERSATION_TABLE_DDLS:
                connection.execute(statement)
            _validate_conversation_schema(connection)
            connection.execute(
                """
                INSERT INTO agent_schema_migrations(version, name, applied_at)
                VALUES (?, ?, ?)
                """,
                (MIGRATION_VERSION, MIGRATION_NAME, applied_at),
            )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
