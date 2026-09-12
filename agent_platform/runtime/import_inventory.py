"""Build a read-only inventory for importing v1.7 SQLite stores.

The inventory records file hashes, table counts, columns, and missing identity
fields. It never mutates a source database and never invents missing history.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


EXPECTED_FIELDS = {
    "tasks": ("task_id", "topic", "created_at", "updated_at"),
    "task_memory_items": ("task_id", "category", "value", "source", "created_at"),
    "research_runs": ("run_id", "task_id", "plan_revision", "revision", "created_at", "updated_at"),
    "research_steps": ("step_id", "run_id", "position", "status", "attempt_count"),
    "research_run_identities": ("run_id", "corpus_fingerprint", "registry_fingerprint", "code_revision"),
    "conversation_summary_state": ("session_id", "revision", "summary_json", "covered_message_ids_json"),
    "conversation_summary_events": ("session_id", "revision", "summary_json", "covered_message_ids_json"),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return f"sha256:{digest.hexdigest()}"


def _table_inventory(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    names = [row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )]
    tables: list[dict[str, Any]] = []
    for name in names:
        columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{name}")')]
        count = int(connection.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0])
        expected = EXPECTED_FIELDS.get(name, ())
        tables.append(
            {
                "name": name,
                "row_count": count,
                "columns": columns,
                "missing_expected_fields": [field for field in expected if field not in columns],
            }
        )
    return tables


def inventory_sqlite(path: str | Path) -> dict[str, Any]:
    source = Path(path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    connection = sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True)
    try:
        tables = _table_inventory(connection)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        connection.close()
    missing = {
        table["name"]: table["missing_expected_fields"]
        for table in tables
        if table["missing_expected_fields"]
    }
    return {
        "source_store": str(source),
        "source_sha256": _sha256(source),
        "source_bytes": source.stat().st_size,
        "integrity_check": integrity,
        "tables": tables,
        "missing_fields": missing,
        "import_policy": {
            "read_only": True,
            "generate_missing_history": False,
            "legacy_verified_becomes_human_confirmed": False,
        },
    }


def build_inventory(paths: list[str | Path]) -> dict[str, Any]:
    inventories = [inventory_sqlite(path) for path in paths]
    return {
        "manifest_version": "v1.8-d05-import-inventory-0.1",
        "source_count": len(inventories),
        "stores": inventories,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory v1.7 SQLite stores without mutation")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = json.dumps(build_inventory(args.paths), ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
