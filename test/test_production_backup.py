from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_platform.capability_packs import LocalObjectStore
from agent_platform.runtime.production_backup import BackupError, backup_database, export_object_store, restore_database, restore_object_store


class ProductionBackupTests(unittest.TestCase):
    def test_object_store_manifest_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "objects"
            LocalObjectStore(root).ingest("note.txt", b"hello", space_id="space-a")
            archive = Path(directory) / "objects.zip"
            manifest = export_object_store(root, archive)
            self.assertTrue(manifest.verify())
            restored = Path(directory) / "restored"
            restored_manifest = restore_object_store(archive, restored)
            self.assertEqual(manifest.checksum, restored_manifest.checksum)
            self.assertEqual(b"hello", LocalObjectStore(restored).read_asset("asset-2cf24dba5fb0a30e"))

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


if __name__ == "__main__":
    unittest.main()

