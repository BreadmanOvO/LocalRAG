from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_platform.capability_packs import LocalObjectStore
from agent_platform.runtime.production_backup import BackupError, _postgres_cli_connection, backup_database, export_object_store, restore_database, restore_object_store


class ProductionBackupTests(unittest.TestCase):
    def test_object_store_manifest_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "objects"
            asset = LocalObjectStore(root).ingest("note.txt", b"hello", space_id="space-a")
            archive = Path(directory) / "objects.zip"
            manifest = export_object_store(root, archive)
            self.assertTrue(manifest.verify())
            restored = Path(directory) / "restored"
            restored_manifest = restore_object_store(archive, restored)
            self.assertEqual(manifest.checksum, restored_manifest.checksum)
            self.assertEqual(b"hello", LocalObjectStore(restored).read_asset(asset.record.asset_id))

    def test_sqlite_database_backup_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.db"
            target = Path(directory) / "target.db"
            import sqlite3
            conn = sqlite3.connect(source)
            conn.execute("create table records (value text)")
            conn.execute("insert into records values ('ok')")
            conn.commit(); conn.close()
            backup_database(f"sqlite:///{source}", target)
            restore = Path(directory) / "restored.db"
            restore_database(f"sqlite:///{restore}", target)
            check = sqlite3.connect(restore)
            self.assertEqual("ok", check.execute("select value from records").fetchone()[0])
            check.close()

    def test_postgres_without_pg_dump_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(BackupError):
                backup_database("postgresql+psycopg://user:pass@localhost/db", Path(directory) / "db.dump")

    def test_postgres_password_is_kept_out_of_process_arguments(self) -> None:
        url, environment = _postgres_cli_connection("postgresql+psycopg://user:s%40cret@localhost:5432/db")
        self.assertNotIn("cret", url)
        self.assertEqual("s@cret", environment["PGPASSWORD"])
        self.assertEqual("postgresql://user@localhost:5432/db", url)


if __name__ == "__main__":
    unittest.main()
