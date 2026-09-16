import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from agent_platform.runtime.import_inventory import inventory_sqlite


ROOT = Path(__file__).parents[1]
MIGRATION = ROOT / "agent_platform" / "runtime" / "migrations" / "0001_initial.sql"
COUNTERS_MIGRATION = ROOT / "agent_platform" / "runtime" / "migrations" / "0003_room_event_counters.sql"
EVENT_COMPAT_MIGRATION = ROOT / "agent_platform" / "runtime" / "migrations" / "0004_event_payload_compatibility.sql"
RUNTIME_STATE_MIGRATION = ROOT / "agent_platform" / "runtime" / "migrations" / "0005_runtime_state.sql"


class Day5MigrationInventoryTests(unittest.TestCase):
    def test_inventory_is_read_only_and_records_missing_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "legacy.sqlite3"
            connection = sqlite3.connect(path)
            try:
                connection.execute("CREATE TABLE tasks (task_id TEXT PRIMARY KEY, topic TEXT)")
                connection.execute("INSERT INTO tasks VALUES ('legacy-task', 'topic')")
                connection.commit()
            finally:
                connection.close()
            before = path.read_bytes()

            result = inventory_sqlite(path)

            self.assertEqual("ok", result["integrity_check"])
            self.assertEqual(before, path.read_bytes())
            self.assertEqual(1, result["tables"][0]["row_count"])
            self.assertEqual(["created_at", "updated_at"], result["missing_fields"]["tasks"])

    def test_inventory_output_is_json_serializable_and_hash_is_stable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "legacy.sqlite3"
            connection = sqlite3.connect(path)
            try:
                connection.execute("CREATE TABLE research_runs (run_id TEXT, task_id TEXT, plan_revision INTEGER, revision INTEGER, created_at TEXT, updated_at TEXT)")
                connection.commit()
            finally:
                connection.close()
            first = inventory_sqlite(path)
            second = inventory_sqlite(path)

        self.assertEqual(first["source_sha256"], second["source_sha256"])
        json.dumps(first, ensure_ascii=False)

    def test_postgres_migration_declares_d05_core_tables_and_constraints(self):
        sql = MIGRATION.read_text(encoding="utf-8")
        for table in (
            "spaces", "rooms", "tasks", "messages", "plans", "runs",
            "steps", "attempts", "persona_snapshots", "room_memberships",
            "task_memory_items", "legacy_message_staging", "message_revisions",
            "run_events", "budget_accounts", "budget_reservations", "budget_consumption",
            "tool_operations", "legacy_id_map", "import_audit",
        ):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", sql)
        for field in ("row_version", "control_epoch", "plan_revision", "room_sequence", "fencing_token"):
            self.assertIn(field, sql)
        self.assertIn("ON CONFLICT (version) DO NOTHING", sql)
        self.assertIn("usage JSONB", sql)
        self.assertIn("timestamp TEXT", sql)

    def test_event_migrations_backfill_counters_and_record_versions(self):
        counters = COUNTERS_MIGRATION.read_text(encoding="utf-8")
        compatibility = EVENT_COMPAT_MIGRATION.read_text(encoding="utf-8")
        self.assertIn("MAX(run_events.room_sequence)", counters)
        self.assertIn("VALUES (3, 'room_event_counters')", counters)
        self.assertIn("ADD COLUMN IF NOT EXISTS usage", compatibility)
        self.assertIn("ADD COLUMN IF NOT EXISTS timestamp", compatibility)
        self.assertIn("VALUES (4, 'event_payload_compatibility')", compatibility)

    def test_runtime_state_migration_declares_durable_execution_tables(self):
        sql = RUNTIME_STATE_MIGRATION.read_text(encoding="utf-8")
        for table in ("runtime_tasks", "runtime_runs", "runtime_jobs", "runtime_commands"):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS {table}", sql)
        self.assertIn("runtime_runs_active_room_idx", sql)
        self.assertIn("VALUES (5, 'runtime_state')", sql)


if __name__ == "__main__":
    unittest.main()
