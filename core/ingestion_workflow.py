"""Staged document ingestion for the upload UI and automation callers.

The workflow deliberately separates preparing a document from making it part
of the active corpus::

    stage_text -> preview -> publish -> (optional) evaluate -> refresh BM25

Staging is filesystem-only.  ``publish`` is the only operation that writes to
Chroma, the source registry, and the active corpus profile.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from config import settings as config
from config.corpus_profile import ACTIVE_CORPUS_CONTRACT_VERSION
from core.chunking import ChunkRecord


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGING_CONTRACT_VERSION = "ingestion-staging-v1"


def _resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate.resolve() if candidate.is_absolute() else (PROJECT_ROOT / candidate).resolve()


def normalize_text(text: str) -> str:
    """Normalize uploaded text while retaining paragraph boundaries."""
    if not isinstance(text, str):
        raise TypeError("uploaded text must be a string")
    text = text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t\xa0\u3000]+", " ", line).strip() for line in text.split("\n")]
    normalized = "\n".join(lines).strip()
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    if not normalized:
        raise ValueError("uploaded text is empty after normalization")
    return normalized


def _json_safe(value: Any) -> str | int | float | bool | None:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    return str(value)


def _atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


@dataclass(frozen=True)
class StagedDocument:
    source_id: str
    filename: str
    normalized_text: str
    metadata: dict[str, Any]
    chunks: tuple[ChunkRecord, ...]
    staging_directory: Path

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)

    @property
    def manifest_path(self) -> Path:
        return self.staging_directory / "manifest.json"

    @property
    def text_path(self) -> Path:
        return self.staging_directory / "document.txt"

    @property
    def chunks_path(self) -> Path:
        return self.staging_directory / "chunks.json"

    def manifest(self, *, status: str = "pending", **extra: Any) -> dict[str, Any]:
        return {
            "contract_version": STAGING_CONTRACT_VERSION,
            "status": status,
            "source_id": self.source_id,
            "filename": self.filename,
            "content_sha256": hashlib.sha256(self.normalized_text.encode("utf-8")).hexdigest(),
            "chunk_count": self.chunk_count,
            "metadata": self.metadata,
            "text_path": self.text_path.name,
            "chunks_path": self.chunks_path.name,
            "created_at": self.metadata.get("create_time"),
            **extra,
        }


@dataclass(frozen=True)
class PublishResult:
    source_id: str
    published: bool
    chunk_count: int
    evaluation_requested: bool
    evaluation_result: Any = None
    evaluation_error: str | None = None
    sparse_index_refreshed: bool = False
    sparse_index_error: str | None = None
    profile_path: Path | None = None
    reason: str | None = None


class IngestionWorkflow:
    """Coordinate staging, registry publication, profile refresh and BM25 refresh."""

    def __init__(
        self,
        *,
        knowledge_base=None,
        staging_directory: str | Path | None = None,
        registry_path: str | Path | None = None,
        active_profile_path: str | Path | None = None,
        uploaded_documents_directory: str | Path | None = None,
        refresh_callback: Callable[[], Any] | None = None,
        manifest_builder: Callable[..., dict[str, Any]] | None = None,
    ) -> None:
        if knowledge_base is None:
            from core.knowledge_base import KnowledgeBaseService

            knowledge_base = KnowledgeBaseService()
        self.knowledge_base = knowledge_base
        self.staging_directory = _resolve_path(
            staging_directory or getattr(config, "ingestion_staging_directory", "./results/ingestion_staging")
        )
        self.registry_path = _resolve_path(
            registry_path or "data/evaluation/shared/source_registry.json"
        )
        self.active_profile_path = _resolve_path(
            active_profile_path or "config/active_corpus.json"
        )
        self.uploaded_documents_directory = _resolve_path(
            uploaded_documents_directory
            or getattr(config, "uploaded_documents_directory", "./data/evaluation/shared/uploads")
        )
        self.pending_registry_path = self.staging_directory / "pending_registry.json"
        self.refresh_callback = refresh_callback
        self.manifest_builder = manifest_builder

    @staticmethod
    def _validate_filename(filename: str) -> str:
        if not isinstance(filename, str) or not filename.strip():
            raise ValueError("filename is required")
        name = Path(filename).name.strip()
        if name in {"", ".", ".."}:
            raise ValueError("filename is invalid")
        return name

    def _build_metadata(
        self,
        *,
        filename: str,
        source_id: str,
        metadata: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        supplied = dict(metadata or {})
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        defaults: dict[str, Any] = {
            "source": filename,
            "title": Path(filename).stem or filename,
            "source_id": source_id,
            "doc_type": "untyped",
            "category": "uploads",
            "language": "unknown",
            "origin_url": f"upload://{filename}",
            "version": "uploaded",
            "create_time": now,
            "operator": getattr(config, "uploader", "unknown"),
        }
        defaults.update({key: _json_safe(value) for key, value in supplied.items()})
        defaults["source"] = filename
        defaults["source_id"] = source_id
        defaults["doc_type"] = str(defaults.get("doc_type") or "untyped")
        defaults["category"] = str(defaults.get("category") or "uploads")
        return {key: value for key, value in defaults.items() if value is not None}

    def _write_pending(self, staged: StagedDocument, *, status: str = "pending", **extra: Any) -> None:
        staged.staging_directory.mkdir(parents=True, exist_ok=True)
        staged.text_path.write_text(staged.normalized_text, encoding="utf-8")
        staged.chunks_path.write_text(
            json.dumps(
                [{"text": chunk.text, "metadata": chunk.metadata} for chunk in staged.chunks],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        _atomic_write(
            staged.manifest_path,
            json.dumps(staged.manifest(status=status, **extra), ensure_ascii=False, indent=2, default=str),
        )

        entries = self._read_pending()
        entry = {
            "source_id": staged.source_id,
            "filename": staged.filename,
            "status": status,
            "manifest_path": str(staged.manifest_path),
            "chunk_count": staged.chunk_count,
            "updated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        }
        entries = [item for item in entries if item.get("source_id") != staged.source_id]
        entries.append(entry)
        _atomic_write(self.pending_registry_path, json.dumps(entries, ensure_ascii=False, indent=2, default=str))

    def _read_pending(self) -> list[dict[str, Any]]:
        if not self.pending_registry_path.exists():
            return []
        payload = json.loads(self.pending_registry_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"pending registry must be a list: {self.pending_registry_path}")
        return [item for item in payload if isinstance(item, dict)]

    def list_pending(self) -> list[dict[str, Any]]:
        """Return pending/published staging entries without loading Chroma."""
        return self._read_pending()

    def stage_text(
        self,
        text: str,
        filename: str,
        *,
        metadata: Mapping[str, Any] | None = None,
        chunking_strategy: str | None = None,
    ) -> StagedDocument:
        filename = self._validate_filename(filename)
        normalized = normalize_text(text)
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        source_id = f"upload-{digest[:24]}"
        source_metadata = self._build_metadata(
            filename=filename,
            source_id=source_id,
            metadata=metadata,
        )
        chunks = tuple(
            self.knowledge_base._chunk_upload(
                normalized,
                source_metadata,
                chunking_strategy=chunking_strategy,
            )
        )
        if not chunks:
            raise ValueError("chunking produced no chunks")
        staging_path = self.staging_directory / source_id
        staged = StagedDocument(
            source_id=source_id,
            filename=filename,
            normalized_text=normalized,
            metadata=source_metadata,
            chunks=chunks,
            staging_directory=staging_path,
        )
        self._write_pending(staged)
        return staged

    def load_staged(self, source_id: str) -> StagedDocument:
        if not source_id or Path(source_id).name != source_id:
            raise ValueError("invalid source_id")
        staging_path = self.staging_directory / source_id
        manifest = json.loads((staging_path / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("contract_version") != STAGING_CONTRACT_VERSION:
            raise ValueError("unsupported staging manifest contract")
        normalized = (staging_path / manifest.get("text_path", "document.txt")).read_text(encoding="utf-8")
        raw_chunks = json.loads((staging_path / manifest.get("chunks_path", "chunks.json")).read_text(encoding="utf-8"))
        chunks = tuple(ChunkRecord(text=str(item["text"]), metadata=dict(item["metadata"])) for item in raw_chunks)
        return StagedDocument(
            source_id=str(manifest["source_id"]),
            filename=str(manifest["filename"]),
            normalized_text=normalized,
            metadata=dict(manifest["metadata"]),
            chunks=chunks,
            staging_directory=staging_path,
        )

    def preview(self, staged: StagedDocument | str, *, max_chunks: int = 3, max_chars: int = 800) -> dict[str, Any]:
        document = self.load_staged(staged) if isinstance(staged, str) else staged
        return {
            "source_id": document.source_id,
            "filename": document.filename,
            "metadata": dict(document.metadata),
            "chunk_count": document.chunk_count,
            "text_preview": document.normalized_text[:max_chars],
            "chunks": [
                {
                    "chunk_order": chunk.metadata.get("chunk_order", index),
                    "text": chunk.text[:max_chars],
                    "metadata": dict(chunk.metadata),
                }
                for index, chunk in enumerate(document.chunks[:max_chunks])
            ],
        }

    def _read_registry(self) -> list[dict[str, Any]]:
        if not self.registry_path.exists():
            return []
        payload = json.loads(self.registry_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("source registry must contain a list")
        return [dict(item) for item in payload if isinstance(item, dict)]

    def _registry_entry(self, document: StagedDocument, clean_path: Path) -> dict[str, Any]:
        metadata = document.metadata
        tags = metadata.get("topic_tags", [])
        if isinstance(tags, str):
            tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
        try:
            clean_relpath = clean_path.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            clean_relpath = str(clean_path)
        return {
            "source_id": document.source_id,
            "title": str(metadata.get("title") or document.filename),
            "doc_type": str(metadata.get("doc_type") or "untyped"),
            "category": str(metadata.get("category") or "uploads"),
            "language": str(metadata.get("language") or "unknown"),
            "path_or_url": clean_relpath,
            "raw_path": f"upload://{document.filename}",
            "origin_url": str(metadata.get("origin_url") or f"upload://{document.filename}"),
            "version": str(metadata.get("version") or "uploaded"),
            "topic_tags": list(tags),
            "notes": "staged upload normalized and chunked before publication",
        }

    def _build_profile(self, registry: list[dict[str, Any]], *, release_version: str | None = None) -> dict[str, Any]:
        # Keep the manifest algorithm identical to the evaluator so runtime
        # observability and release-gate fingerprints remain comparable.
        manifest_builder = self.manifest_builder
        if manifest_builder is None:
            from eval.eval_agent import build_corpus_manifest

            manifest_builder = build_corpus_manifest
        chroma = self.knowledge_base.chroma
        collection = getattr(chroma, "_collection", None)
        persist_directory = Path(
            getattr(chroma, "_persist_directory", getattr(config, "persist_directory", "./chroma_db"))
        )
        collection_name = str(getattr(collection, "name", getattr(config, "collection_name", "rag")))
        manifest = manifest_builder(
            registry_path=self.registry_path,
            persist_directory=persist_directory,
            collection_name=collection_name,
            collection=collection,
        )
        persist_directory = persist_directory.resolve()
        try:
            persist_value = persist_directory.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            persist_value = str(persist_directory)
        if release_version is None and self.active_profile_path.exists():
            try:
                current_profile = json.loads(self.active_profile_path.read_text(encoding="utf-8"))
                release_version = current_profile.get("release_version")
            except (OSError, json.JSONDecodeError):
                release_version = None
        corpus_fingerprint = str(manifest["corpus_fingerprint"])
        if not corpus_fingerprint.startswith("sha256:"):
            corpus_fingerprint = f"sha256:{corpus_fingerprint}"
        registry_fingerprint = str(manifest["registry_fingerprint"])
        if not registry_fingerprint.startswith("sha256:"):
            registry_fingerprint = f"sha256:{registry_fingerprint}"
        return {
            "contract_version": ACTIVE_CORPUS_CONTRACT_VERSION,
            "release_version": release_version or f"v{getattr(config, 'version', 'upload')}",
            "persist_directory": persist_value,
            "collection_name": collection_name,
            "source_count": int(manifest["registry_source_count"]),
            "chunk_count": int(manifest["chunk_count"]),
            "corpus_fingerprint": corpus_fingerprint,
            "registry_fingerprint": registry_fingerprint,
        }

    def _refresh_sparse_index(self, rag_service=None, refresh_callback=None) -> tuple[bool, str | None]:
        callback = refresh_callback or self.refresh_callback
        if callback is None and rag_service is not None:
            callback = getattr(rag_service, "refresh_sparse_index", None)
        if not callable(callback):
            return False, None
        try:
            callback()
        except Exception as exc:  # data publication should survive a stale BM25 process
            return False, f"{type(exc).__name__}: {exc}"
        return True, None

    def _chunk_id(self, document: StagedDocument, chunk: ChunkRecord) -> str:
        builder = getattr(self.knowledge_base, "chunk_record_id", None)
        if callable(builder):
            return str(builder(document.source_id, chunk))
        order = chunk.metadata.get("chunk_order", 0)
        strategy = chunk.metadata.get("chunk_strategy", "baseline")
        return hashlib.sha256(
            f"{document.source_id}\0{strategy}\0{order}\0{chunk.text}".encode("utf-8")
        ).hexdigest()

    def publish(
        self,
        staged: StagedDocument | str,
        *,
        evaluate: bool = False,
        evaluator: Callable[[StagedDocument], Any] | None = None,
        rag_service=None,
        refresh_callback: Callable[[], Any] | None = None,
        release_version: str | None = None,
    ) -> PublishResult:
        """Publish a staged document and optionally invoke an evaluator.

        Evaluation is deliberately callback-based.  Publishing does not call a
        cloud model or a long-running benchmark unless ``evaluate=True`` and a
        callback is supplied by the caller.
        """
        document = self.load_staged(staged) if isinstance(staged, str) else staged
        manifest_path = document.manifest_path
        current_manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        if current_manifest.get("status") == "published":
            return PublishResult(
                source_id=document.source_id,
                published=False,
                chunk_count=document.chunk_count,
                evaluation_requested=evaluate,
                profile_path=self.active_profile_path,
                reason="already_published",
            )

        registry_before = self.registry_path.read_text(encoding="utf-8") if self.registry_path.exists() else None
        profile_before = self.active_profile_path.read_text(encoding="utf-8") if self.active_profile_path.exists() else None
        clean_path = self.uploaded_documents_directory / f"{document.source_id}.md"
        clean_before = clean_path.read_bytes() if clean_path.exists() else None
        ids = [self._chunk_id(document, chunk) for chunk in document.chunks]
        inserted_ids: list[str] = []
        try:
            clean_path.parent.mkdir(parents=True, exist_ok=True)
            clean_path.write_text(document.normalized_text, encoding="utf-8")
            existing_ids: set[str] = set()
            get_records = getattr(self.knowledge_base.chroma, "get", None)
            if callable(get_records):
                try:
                    existing = get_records(ids=ids)
                    existing_ids = {str(record_id) for record_id in (existing.get("ids") or [])}
                except Exception:
                    # A compatible vector store may not implement ``get``;
                    # deterministic ids still make the normal path idempotent.
                    existing_ids = set()
            records_to_add = [
                (chunk, record_id)
                for chunk, record_id in zip(document.chunks, ids)
                if record_id not in existing_ids
            ]
            if records_to_add:
                self.knowledge_base.add_chunk_records(
                    [chunk for chunk, _record_id in records_to_add],
                    ids=[record_id for _chunk, record_id in records_to_add],
                )
                inserted_ids = [record_id for _chunk, record_id in records_to_add]

            registry = self._read_registry()
            registry = [entry for entry in registry if entry.get("source_id") != document.source_id]
            registry.append(self._registry_entry(document, clean_path))
            _atomic_write(self.registry_path, json.dumps(registry, ensure_ascii=False, indent=2))
            profile = self._build_profile(registry, release_version=release_version)
            _atomic_write(self.active_profile_path, json.dumps(profile, ensure_ascii=False, indent=2))

            evaluation_result = None
            evaluation_error = None
            if evaluate:
                if evaluator is None:
                    evaluation_error = "evaluate=True requires an evaluator callback"
                else:
                    try:
                        evaluation_result = evaluator(document)
                    except Exception as exc:  # evaluation is optional and must not undo a publish
                        evaluation_error = f"{type(exc).__name__}: {exc}"

            self._write_pending(
                document,
                status="published",
                published_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                evaluation=evaluation_result,
                evaluation_error=evaluation_error,
            )
            refreshed, refresh_error = self._refresh_sparse_index(rag_service, refresh_callback)
            return PublishResult(
                source_id=document.source_id,
                published=True,
                chunk_count=document.chunk_count,
                evaluation_requested=evaluate,
                evaluation_result=evaluation_result,
                evaluation_error=evaluation_error,
                sparse_index_refreshed=refreshed,
                sparse_index_error=refresh_error,
                profile_path=self.active_profile_path,
            )
        except Exception:
            # Chroma and registry/profile are updated as one logical operation;
            # restore files and remove newly inserted records when possible.
            if inserted_ids:
                try:
                    self.knowledge_base.chroma.delete(ids=inserted_ids)
                except Exception:
                    pass
            if registry_before is None:
                self.registry_path.unlink(missing_ok=True)
            else:
                _atomic_write(self.registry_path, registry_before)
            if profile_before is None:
                self.active_profile_path.unlink(missing_ok=True)
            else:
                _atomic_write(self.active_profile_path, profile_before)
            if clean_before is None:
                clean_path.unlink(missing_ok=True)
            else:
                clean_path.parent.mkdir(parents=True, exist_ok=True)
                clean_path.write_bytes(clean_before)
            raise


__all__ = [
    "IngestionWorkflow",
    "PublishResult",
    "StagedDocument",
    "normalize_text",
]
