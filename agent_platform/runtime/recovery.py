"""D10 checkpoint, archive, backup, deletion, and persona contracts.

This module is an in-memory reference implementation for the recovery boundary.
It deliberately keeps persistence and process coordination out of scope while
making the safety rules executable: a checkpoint is pinned to plan/control
versions, archived runs are read-only, backups are checksummed, and a deletion
tombstone is never undone by restoring an older backup.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from threading import RLock
from typing import Any, Literal

from agent_platform.contracts.identity import new_identifier, validate_identifier


class RecoveryError(RuntimeError):
    """Base class for recovery contract failures."""


class CheckpointConflictError(RecoveryError):
    """The checkpoint or execution version is stale or inconsistent."""


class ArchivedRunError(RecoveryError):
    """An archived run cannot be resumed or mutated."""


class BackupIntegrityError(RecoveryError):
    """A backup checksum does not match its contents."""


class DeletionConflictError(RecoveryError):
    """A deleted resource cannot be restored or changed by an old request."""


class PersonaSnapshotConflictError(RecoveryError):
    """A binding id was reused with a different persona payload."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value.strip()


def _version(value: int, field_name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{field_name} must be an int >= {minimum}")
    return value


def _payload(value: dict[str, Any], field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{field_name} must be a mapping")
    copied = deepcopy(value)
    try:
        json.dumps(copied, ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{field_name} must be JSON serializable") from exc
    return copied


def _tuple_text(values: tuple[str, ...] | list[str], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, (tuple, list)):
        raise TypeError(f"{field_name} must be a sequence")
    normalized = tuple(_text(value, field_name) for value in values)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{field_name} must not contain duplicates")
    return normalized


@dataclass(frozen=True)
class Checkpoint:
    checkpoint_id: str
    run_id: str
    step_id: str
    plan_revision: int
    control_epoch: int
    state: dict[str, Any] = field(default_factory=dict)
    completed_step_ids: tuple[str, ...] = ()
    row_version: int = 1
    created_at: str = ""
    plan_fingerprint: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "checkpoint_id", validate_identifier(self.checkpoint_id, "checkpoint"))
        object.__setattr__(self, "run_id", validate_identifier(self.run_id, "run"))
        object.__setattr__(self, "step_id", validate_identifier(self.step_id, "step"))
        object.__setattr__(self, "plan_revision", _version(self.plan_revision, "plan_revision", 1))
        object.__setattr__(self, "control_epoch", _version(self.control_epoch, "control_epoch"))
        fingerprint = self.plan_fingerprint.strip() if isinstance(self.plan_fingerprint, str) else ""
        if fingerprint and len(fingerprint) > 128:
            raise ValueError("plan_fingerprint is too long")
        object.__setattr__(self, "plan_fingerprint", fingerprint)
        object.__setattr__(self, "state", _payload(self.state, "state"))
        object.__setattr__(self, "completed_step_ids", _tuple_text(self.completed_step_ids, "completed_step_ids"))
        object.__setattr__(self, "row_version", _version(self.row_version, "row_version", 1))
        object.__setattr__(self, "created_at", _text(self.created_at or _now(), "created_at"))


@dataclass(frozen=True)
class ArchiveRecord:
    archive_id: str
    run_id: str
    reason: str
    archived_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "archive_id", validate_identifier(self.archive_id, "archive"))
        object.__setattr__(self, "run_id", validate_identifier(self.run_id, "run"))
        object.__setattr__(self, "reason", _text(self.reason, "reason"))
        object.__setattr__(self, "archived_at", _text(self.archived_at or _now(), "archived_at"))


@dataclass(frozen=True)
class DeletionTombstone:
    deletion_id: str
    target_type: Literal["run", "step", "persona", "binding", "room", "message", "asset"]
    target_id: str
    reason: str
    deleted_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "deletion_id", validate_identifier(self.deletion_id, "deletion"))
        if self.target_type not in {"run", "step", "persona", "binding", "room", "message", "asset"}:
            raise ValueError(f"unsupported target_type: {self.target_type}")
        object.__setattr__(self, "target_id", _text(self.target_id, "target_id"))
        object.__setattr__(self, "reason", _text(self.reason, "reason"))
        object.__setattr__(self, "deleted_at", _text(self.deleted_at or _now(), "deleted_at"))


@dataclass(frozen=True)
class PersonaSnapshot:
    binding_id: str
    space_id: str
    persona_id: str
    version: str
    profile: dict[str, Any]
    room_id: str | None = None
    agent_id: str | None = None
    created_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "binding_id", validate_identifier(self.binding_id, "binding"))
        object.__setattr__(self, "space_id", validate_identifier(self.space_id, "space"))
        object.__setattr__(self, "persona_id", _text(self.persona_id, "persona_id"))
        object.__setattr__(self, "version", _text(self.version, "version"))
        object.__setattr__(self, "profile", _payload(self.profile, "profile"))
        if self.room_id is not None:
            object.__setattr__(self, "room_id", validate_identifier(self.room_id, "room"))
        if self.agent_id is not None:
            object.__setattr__(self, "agent_id", _text(self.agent_id, "agent_id"))
        object.__setattr__(self, "created_at", _text(self.created_at or _now(), "created_at"))


@dataclass(frozen=True)
class BackupBundle:
    backup_id: str
    schema_version: str
    checkpoints: tuple[Checkpoint, ...]
    archives: tuple[ArchiveRecord, ...]
    persona_snapshots: tuple[PersonaSnapshot, ...]
    deletions: tuple[DeletionTombstone, ...]
    checksum: str
    created_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "backup_id", validate_identifier(self.backup_id, "backup"))
        object.__setattr__(self, "schema_version", _text(self.schema_version, "schema_version"))
        object.__setattr__(self, "created_at", _text(self.created_at or _now(), "created_at"))
        object.__setattr__(self, "checkpoints", tuple(self.checkpoints))
        object.__setattr__(self, "archives", tuple(self.archives))
        object.__setattr__(self, "persona_snapshots", tuple(self.persona_snapshots))
        object.__setattr__(self, "deletions", tuple(self.deletions))
        object.__setattr__(self, "checksum", _text(self.checksum, "checksum"))

    def content_dict(self) -> dict[str, Any]:
        return {
            "backup_id": self.backup_id,
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "checkpoints": [_checkpoint_dict(item) for item in self.checkpoints],
            "archives": [_archive_dict(item) for item in self.archives],
            "persona_snapshots": [_persona_dict(item) for item in self.persona_snapshots],
            "deletions": [_deletion_dict(item) for item in self.deletions],
        }

    def verify(self) -> bool:
        return self.checksum == _checksum(self.content_dict())

    def to_dict(self) -> dict[str, Any]:
        payload = self.content_dict()
        payload["checksum"] = self.checksum
        return payload


@dataclass(frozen=True)
class RestoreReport:
    backup_id: str
    restored_checkpoints: int
    restored_archives: int
    restored_personas: int
    skipped_deleted: int


def _checkpoint_dict(item: Checkpoint) -> dict[str, Any]:
    return {
        "checkpoint_id": item.checkpoint_id,
        "run_id": item.run_id,
        "step_id": item.step_id,
        "plan_revision": item.plan_revision,
        "control_epoch": item.control_epoch,
        **({"plan_fingerprint": item.plan_fingerprint} if item.plan_fingerprint else {}),
        "state": deepcopy(item.state),
        "completed_step_ids": list(item.completed_step_ids),
        "row_version": item.row_version,
        "created_at": item.created_at,
    }


def _archive_dict(item: ArchiveRecord) -> dict[str, Any]:
    return {
        "archive_id": item.archive_id,
        "run_id": item.run_id,
        "reason": item.reason,
        "archived_at": item.archived_at,
    }


def _deletion_dict(item: DeletionTombstone) -> dict[str, Any]:
    return {
        "deletion_id": item.deletion_id,
        "target_type": item.target_type,
        "target_id": item.target_id,
        "reason": item.reason,
        "deleted_at": item.deleted_at,
    }


def _persona_dict(item: PersonaSnapshot) -> dict[str, Any]:
    return {
        "binding_id": item.binding_id,
        "space_id": item.space_id,
        "persona_id": item.persona_id,
        "version": item.version,
        "profile": deepcopy(item.profile),
        "room_id": item.room_id,
        "agent_id": item.agent_id,
        "created_at": item.created_at,
    }


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _checksum(payload: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(_canonical(payload)).hexdigest()


class RecoveryService:
    """Thread-safe in-memory recovery service used by D10 contract probes."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._checkpoints: dict[str, Checkpoint] = {}
        self._latest: dict[tuple[str, str], str] = {}
        self._archives: dict[str, ArchiveRecord] = {}
        self._personas: dict[str, PersonaSnapshot] = {}
        self._deletions: dict[tuple[str, str], DeletionTombstone] = {}

    def save_checkpoint(
        self,
        run_id: str,
        step_id: str,
        *,
        plan_revision: int,
        control_epoch: int,
        plan_fingerprint: str = "",
        state: dict[str, Any],
        completed_step_ids: tuple[str, ...] = (),
        checkpoint_id: str | None = None,
        expected_row_version: int | None = None,
    ) -> Checkpoint:
        run_id = validate_identifier(run_id, "run")
        step_id = validate_identifier(step_id, "step")
        with self._lock:
            self._ensure_not_deleted("run", run_id)
            if run_id in {record.run_id for record in self._archives.values()}:
                raise ArchivedRunError(run_id)
            key = (run_id, step_id)
            previous = self._checkpoints.get(self._latest[key]) if key in self._latest else None
            if expected_row_version is not None:
                if previous is None or previous.row_version != expected_row_version:
                    raise CheckpointConflictError("checkpoint row version is stale")
            identifier = validate_identifier(checkpoint_id, "checkpoint") if checkpoint_id else new_identifier("checkpoint")
            if identifier in self._checkpoints:
                existing = self._checkpoints[identifier]
                candidate = Checkpoint(identifier, run_id, step_id, plan_revision, control_epoch, state, completed_step_ids, existing.row_version, existing.created_at, plan_fingerprint)
                if existing != candidate:
                    raise CheckpointConflictError("checkpoint id is already bound to another payload")
                return deepcopy(existing)
            checkpoint = Checkpoint(
                identifier,
                run_id,
                step_id,
                plan_revision,
                control_epoch,
                state,
                completed_step_ids,
                (previous.row_version + 1) if previous else 1,
                plan_fingerprint=plan_fingerprint,
            )
            self._checkpoints[identifier] = checkpoint
            self._latest[key] = identifier
            return deepcopy(checkpoint)

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint:
        checkpoint_id = validate_identifier(checkpoint_id, "checkpoint")
        with self._lock:
            try:
                return deepcopy(self._checkpoints[checkpoint_id])
            except KeyError as exc:
                raise RecoveryError("unknown checkpoint") from exc

    def resume(
        self,
        run_id: str,
        *,
        plan_revision: int,
        control_epoch: int,
        plan_fingerprint: str = "",
        checkpoint_id: str | None = None,
    ) -> Checkpoint:
        run_id = validate_identifier(run_id, "run")
        with self._lock:
            if run_id in {record.run_id for record in self._archives.values()}:
                raise ArchivedRunError("archived run is read-only")
            self._ensure_not_deleted("run", run_id)
            if checkpoint_id:
                checkpoint = self.get_checkpoint(checkpoint_id)
            else:
                candidates = [item for item in self._checkpoints.values() if item.run_id == run_id]
                if not candidates:
                    raise RecoveryError("run has no checkpoint")
                checkpoint = max(candidates, key=lambda item: item.row_version)
            if checkpoint.run_id != run_id:
                raise CheckpointConflictError("checkpoint belongs to another run")
            if checkpoint.plan_revision != plan_revision or checkpoint.control_epoch != control_epoch:
                raise CheckpointConflictError("checkpoint version does not match current run")
            if checkpoint.plan_fingerprint != plan_fingerprint.strip():
                raise CheckpointConflictError("checkpoint plan fingerprint does not match current plan")
            return deepcopy(checkpoint)

    def archive_run(self, run_id: str, *, reason: str = "completed") -> ArchiveRecord:
        run_id = validate_identifier(run_id, "run")
        reason = _text(reason, "reason")
        with self._lock:
            self._ensure_not_deleted("run", run_id)
            existing = next((item for item in self._archives.values() if item.run_id == run_id), None)
            if existing:
                if existing.reason != reason:
                    raise RecoveryError("archived run reason differs")
                return deepcopy(existing)
            record = ArchiveRecord(new_identifier("archive"), run_id, reason)
            self._archives[record.archive_id] = record
            return deepcopy(record)

    def unarchive_run(self, run_id: str) -> None:
        run_id = validate_identifier(run_id, "run")
        with self._lock:
            self._ensure_not_deleted("run", run_id)
            for archive_id, record in tuple(self._archives.items()):
                if record.run_id == run_id:
                    del self._archives[archive_id]

    def is_archived(self, run_id: str) -> bool:
        run_id = validate_identifier(run_id, "run")
        with self._lock:
            return any(record.run_id == run_id for record in self._archives.values())

    def save_persona_snapshot(
        self,
        space_id: str,
        persona_id: str,
        version: str,
        profile: dict[str, Any],
        *,
        room_id: str | None = None,
        agent_id: str | None = None,
        binding_id: str | None = None,
    ) -> PersonaSnapshot:
        space_id = validate_identifier(space_id, "space")
        if room_id is not None:
            room_id = validate_identifier(room_id, "room")
        identifier = validate_identifier(binding_id, "binding") if binding_id else new_identifier("binding")
        with self._lock:
            self._ensure_not_deleted("binding", identifier)
            snapshot = PersonaSnapshot(identifier, space_id, persona_id, version, profile, room_id, agent_id)
            existing = self._personas.get(identifier)
            if existing and existing != snapshot:
                raise PersonaSnapshotConflictError("binding id is already bound to another persona")
            self._personas[identifier] = existing or snapshot
            return deepcopy(self._personas[identifier])

    def get_persona_snapshot(self, binding_id: str) -> PersonaSnapshot:
        binding_id = validate_identifier(binding_id, "binding")
        with self._lock:
            try:
                return deepcopy(self._personas[binding_id])
            except KeyError as exc:
                raise RecoveryError("unknown persona snapshot") from exc

    def record_deletion(
        self,
        target_type: Literal["run", "step", "persona", "binding", "room", "message", "asset"],
        target_id: str,
        *,
        reason: str,
        deletion_id: str | None = None,
    ) -> DeletionTombstone:
        target_id = _text(target_id, "target_id")
        reason = _text(reason, "reason")
        with self._lock:
            key = (target_type, target_id)
            existing = self._deletions.get(key)
            if existing:
                if existing.reason != reason:
                    raise DeletionConflictError("deletion reason differs")
                return deepcopy(existing)
            tombstone = DeletionTombstone(
                validate_identifier(deletion_id, "deletion") if deletion_id else new_identifier("deletion"),
                target_type,
                target_id,
                reason,
            )
            self._deletions[key] = tombstone
            self._remove_deleted_target(target_type, target_id)
            return deepcopy(tombstone)

    def list_deletions(self) -> tuple[DeletionTombstone, ...]:
        with self._lock:
            return tuple(deepcopy(item) for item in self._deletions.values())

    def create_backup(self, *, schema_version: str = "v1.8-d10-recovery-0.1") -> BackupBundle:
        with self._lock:
            deletions = tuple(deepcopy(item) for item in self._deletions.values())
            active_checkpoints = tuple(
                deepcopy(item) for item in self._checkpoints.values() if not self._is_deleted_checkpoint(item)
            )
            active_archives = tuple(
                deepcopy(item) for item in self._archives.values() if not self._is_deleted("run", item.run_id)
            )
            active_personas = tuple(
                deepcopy(item)
                for item in self._personas.values()
                if not self._is_deleted("binding", item.binding_id)
                and not self._is_deleted("persona", item.persona_id)
                and not (item.room_id and self._is_deleted("room", item.room_id))
            )
            content = {
                "backup_id": new_identifier("backup"),
                "schema_version": _text(schema_version, "schema_version"),
                "created_at": _now(),
                "checkpoints": [_checkpoint_dict(item) for item in active_checkpoints],
                "archives": [_archive_dict(item) for item in active_archives],
                "persona_snapshots": [_persona_dict(item) for item in active_personas],
                "deletions": [_deletion_dict(item) for item in deletions],
            }
            bundle = BackupBundle(
                content["backup_id"],
                content["schema_version"],
                active_checkpoints,
                active_archives,
                active_personas,
                deletions,
                _checksum(content),
                content["created_at"],
            )
            return deepcopy(bundle)

    def restore_backup(self, bundle: BackupBundle) -> RestoreReport:
        if not isinstance(bundle, BackupBundle):
            raise TypeError("bundle must be a BackupBundle")
        if not bundle.verify():
            raise BackupIntegrityError("backup checksum mismatch")
        with self._lock:
            for deletion in bundle.deletions:
                key = (deletion.target_type, deletion.target_id)
                existing_deletion = self._deletions.get(key)
                if existing_deletion and existing_deletion != deletion:
                    raise DeletionConflictError("deletion tombstone conflicts during restore")
                if existing_deletion is None:
                    self._deletions[key] = deepcopy(deletion)
                    self._remove_deleted_target(deletion.target_type, deletion.target_id)
            restored_checkpoints = restored_archives = restored_personas = skipped_deleted = 0
            for checkpoint in bundle.checkpoints:
                if self._is_deleted_checkpoint(checkpoint):
                    skipped_deleted += 1
                    continue
                existing = self._checkpoints.get(checkpoint.checkpoint_id)
                if existing and existing != checkpoint:
                    raise RecoveryError("checkpoint id conflicts during restore")
                if not existing:
                    self._checkpoints[checkpoint.checkpoint_id] = deepcopy(checkpoint)
                    self._latest[(checkpoint.run_id, checkpoint.step_id)] = checkpoint.checkpoint_id
                    restored_checkpoints += 1
            for archive in bundle.archives:
                if self._is_deleted("run", archive.run_id):
                    skipped_deleted += 1
                    continue
                if archive.archive_id not in self._archives:
                    self._archives[archive.archive_id] = deepcopy(archive)
                    restored_archives += 1
            for persona in bundle.persona_snapshots:
                if self._is_deleted("binding", persona.binding_id) or self._is_deleted("persona", persona.persona_id) or (persona.room_id and self._is_deleted("room", persona.room_id)):
                    skipped_deleted += 1
                    continue
                existing = self._personas.get(persona.binding_id)
                if existing and existing != persona:
                    raise PersonaSnapshotConflictError("persona binding conflicts during restore")
                if not existing:
                    self._personas[persona.binding_id] = deepcopy(persona)
                    restored_personas += 1
            return RestoreReport(bundle.backup_id, restored_checkpoints, restored_archives, restored_personas, skipped_deleted)

    def _ensure_not_deleted(self, target_type: str, target_id: str) -> None:
        if self._is_deleted(target_type, target_id):
            raise DeletionConflictError(f"{target_type} is deleted: {target_id}")

    def _is_deleted(self, target_type: str, target_id: str) -> bool:
        return (target_type, target_id) in self._deletions

    def _is_deleted_checkpoint(self, checkpoint: Checkpoint) -> bool:
        return self._is_deleted("run", checkpoint.run_id) or self._is_deleted("step", checkpoint.step_id)

    def _remove_deleted_target(self, target_type: str, target_id: str) -> None:
        if target_type == "run":
            for checkpoint_id, item in tuple(self._checkpoints.items()):
                if item.run_id == target_id:
                    del self._checkpoints[checkpoint_id]
                    self._latest.pop((item.run_id, item.step_id), None)
            for archive_id, item in tuple(self._archives.items()):
                if item.run_id == target_id:
                    del self._archives[archive_id]
        elif target_type == "step":
            for checkpoint_id, item in tuple(self._checkpoints.items()):
                if item.step_id == target_id:
                    del self._checkpoints[checkpoint_id]
                    self._latest.pop((item.run_id, item.step_id), None)
        elif target_type in {"binding", "persona", "room"}:
            for binding_id, item in tuple(self._personas.items()):
                if (target_type == "binding" and item.binding_id == target_id) or (target_type == "persona" and item.persona_id == target_id) or (target_type == "room" and item.room_id == target_id):
                    del self._personas[binding_id]
