"""Explicit backup adapters used by the D41 deployment boundary.

Backups are byte-oriented and verifiable.  The object adapter is portable;
the database adapter deliberately delegates PostgreSQL to pg_dump/pg_restore
so credentials and engine-specific semantics stay outside application code.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class BackupError(RuntimeError):
    pass


@dataclass(frozen=True)
class BackupManifest:
    backup_id: str
    kind: str
    created_at: str
    files: tuple[dict[str, Any], ...]
    checksum: str

    def verify(self) -> bool:
        payload = {"backup_id": self.backup_id, "kind": self.kind, "created_at": self.created_at, "files": list(self.files)}
        return self.checksum == _checksum(payload)


def _checksum(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def export_object_store(root: str | Path, destination: str | Path) -> BackupManifest:
    source = Path(root).resolve()
    if not source.exists():
        raise BackupError(f"object store does not exist: {source}")
    target = Path(destination).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(item for item in source.rglob("*") if item.is_file()):
            relative = path.relative_to(source).as_posix()
            archive.write(path, relative)
            files.append({"path": relative, "size": path.stat().st_size, "sha256": _file_digest(path)})
        created_at = datetime.now(timezone.utc).isoformat()
        payload = {"backup_id": f"object-backup-{hashlib.sha256((created_at + str(target)).encode()).hexdigest()[:16]}", "kind": "object_store", "created_at": created_at, "files": files}
        manifest = BackupManifest(**payload, checksum=_checksum(payload))
        archive.writestr("backup-manifest.json", json.dumps({**payload, "checksum": manifest.checksum}, ensure_ascii=False, sort_keys=True, indent=2))
    return manifest


def restore_object_store(backup: str | Path, destination: str | Path, *, replace: bool = False) -> BackupManifest:
    archive_path = Path(backup).resolve()
    target = Path(destination).resolve()
    if target.exists() and any(target.iterdir()) and not replace:
        raise BackupError("restore destination is not empty; pass replace=True")
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        try:
            raw = json.loads(archive.read("backup-manifest.json"))
        except (KeyError, json.JSONDecodeError) as exc:
            raise BackupError("backup manifest is missing or invalid") from exc
        manifest = BackupManifest(raw["backup_id"], raw["kind"], raw["created_at"], tuple(raw["files"]), raw["checksum"])
        if manifest.kind != "object_store" or not manifest.verify():
            raise BackupError("backup manifest checksum mismatch")
        for member in archive.namelist():
            member_path = (target / member).resolve()
            if target not in member_path.parents and member_path != target:
                raise BackupError("backup contains an unsafe path")
        archive.extractall(target)
    for item in manifest.files:
        path = target / item["path"]
        if not path.exists() or path.stat().st_size != item["size"] or _file_digest(path) != item["sha256"]:
            raise BackupError(f"restored object failed verification: {item['path']}")
    return manifest


def backup_database(database_url: str, destination: str | Path) -> Path:
    """Create a database dump using the database vendor's supported tool."""
    target = Path(destination).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if database_url.startswith("sqlite:"):
        sqlite_path = database_url.removeprefix("sqlite:///")
        if sqlite_path == ":memory:":
            raise BackupError("in-memory SQLite cannot be backed up")
        source = sqlite3.connect(sqlite_path)
        try:
            output = sqlite3.connect(target)
            try:
                source.backup(output)
            finally:
                output.close()
        finally:
            source.close()
        return target
    if database_url.startswith("postgresql"):
        if shutil.which("pg_dump") is None:
            raise BackupError("pg_dump is required for PostgreSQL backup")
        completed = subprocess.run(["pg_dump", "--format=custom", "--file", str(target), database_url], capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise BackupError("pg_dump failed")
        return target
    raise BackupError("unsupported database URL for backup")


def restore_database(database_url: str, backup: str | Path) -> None:
    if database_url.startswith("sqlite:"):
        sqlite_path = database_url.removeprefix("sqlite:///")
        source = sqlite3.connect(backup)
        try:
            target = sqlite3.connect(sqlite_path)
            try:
                source.backup(target)
            finally:
                target.close()
        finally:
            source.close()
        return
    if database_url.startswith("postgresql"):
        if shutil.which("pg_restore") is None:
            raise BackupError("pg_restore is required for PostgreSQL restore")
        completed = subprocess.run(["pg_restore", "--clean", "--if-exists", "--dbname", database_url, str(backup)], capture_output=True, text=True, check=False)
        if completed.returncode != 0:
            raise BackupError("pg_restore failed")
        return
    raise BackupError("unsupported database URL for restore")
