"""Explicit PostgreSQL migration runner for the v1.8 Runtime schema."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine


MIGRATION_DIR = Path(__file__).resolve().parent


def _migration_files(directory: Path = MIGRATION_DIR) -> tuple[Path, ...]:
    return tuple(sorted(directory.glob("[0-9][0-9][0-9][0-9]_*.sql")))


def apply_migrations(engine: Engine, *, directory: Path = MIGRATION_DIR) -> tuple[int, ...]:
    """Apply pending migrations in one transaction per file.

    The runner is intentionally explicit: production startup must not silently
    mutate a database. It requires PostgreSQL because the baseline uses JSONB,
    BIGSERIAL, and PostgreSQL locking semantics.
    """
    if engine.dialect.name != "postgresql":
        raise ValueError("v1.8 runtime migrations require a PostgreSQL engine")
    applied: list[int] = []
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE IF NOT EXISTS runtime_schema_migrations ("
            "version INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, "
            "applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())"
        )
    for path in _migration_files(directory):
        version = int(path.name[:4])
        with engine.begin() as conn:
            current = conn.execute(text("SELECT 1 FROM runtime_schema_migrations WHERE version=:version"), {"version": version}).first()
            if current is not None:
                continue
            # psycopg3 supports a multi-statement script in exec_driver_sql;
            # the migration files contain no bind parameters.
            conn.exec_driver_sql(path.read_text(encoding="utf-8"))
            applied.append(version)
    return tuple(applied)


def migrate_url(url: str, *, directory: Path = MIGRATION_DIR) -> tuple[int, ...]:
    engine = create_engine(url, future=True, pool_pre_ping=True)
    try:
        return apply_migrations(engine, directory=directory)
    finally:
        engine.dispose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Apply LocalRAG v1.8 PostgreSQL migrations")
    parser.add_argument("url", help="PostgreSQL SQLAlchemy URL")
    args = parser.parse_args()
    print({"applied": migrate_url(args.url)})
