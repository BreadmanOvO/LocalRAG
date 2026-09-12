"""Durable JSON backup wrapper around the D10 RecoveryService contract."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .recovery import BackupBundle, Checkpoint, ArchiveRecord, PersonaSnapshot, DeletionTombstone

def write_backup(bundle: BackupBundle, path: str | Path) -> Path:
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(bundle.to_dict(), ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    return target

def read_backup(path: str | Path) -> BackupBundle:
    payload: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    checkpoints = tuple(Checkpoint(**item) for item in payload.pop("checkpoints", []))
    archives = tuple(ArchiveRecord(**item) for item in payload.pop("archives", []))
    personas = tuple(PersonaSnapshot(**item) for item in payload.pop("persona_snapshots", []))
    deletions = tuple(DeletionTombstone(**item) for item in payload.pop("deletions", []))
    return BackupBundle(checkpoints=checkpoints, archives=archives, persona_snapshots=personas, deletions=deletions, **payload)
