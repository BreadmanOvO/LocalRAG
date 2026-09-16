"""Persistent upload status and the real format-aware knowledge publishing path."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from uuid import uuid4
from filelock import FileLock

from processing.document_parser import SUPPORTED_EXTENSIONS, DocumentParseError

STAGES = ("queued", "parsing", "cleaning", "chunking", "indexing", "publishing", "completed")


class _AssetKnowledgeBase:
    """Parsing and chunking need no model; load embeddings only for the index."""
    def __init__(self, directory, embedding_factory):
        self.directory = directory
        self.embedding_factory = embedding_factory
        self._kb = None

    @property
    def chroma(self):
        if self._kb is None:
            from core.knowledge_base import KnowledgeBaseService
            self._kb = KnowledgeBaseService(persist_directory=self.directory, collection_name="assets", embedding_model=self.embedding_factory())
        return self._kb.chroma

    def _chunk_upload(self, text, metadata, chunking_strategy=None):
        from core.chunking import chunk_text_doc_type_aware
        return chunk_text_doc_type_aware(text, source_metadata=metadata)

    def add_chunk_records(self, chunks, *, ids):
        self.chroma.add_texts(texts=[chunk.text for chunk in chunks], metadatas=[chunk.metadata for chunk in chunks], ids=ids)


class AssetIngestionService:
    def __init__(self, object_store, *, root=None, workflow_factory=None, vision=None):
        self.object_store = object_store
        self.root = Path(root or os.environ.get("LOCALRAG_ASSET_LIBRARY", "results/asset_library")).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.database = self.root / "jobs.sqlite3"
        self.workflow_factory = workflow_factory or self._workflow
        self.vision = vision
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="asset-ingest")
        self._lock = RLock()
        self._futures = {}
        self._workflows = {}
        self._embedding = None
        with self._connection() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS asset_jobs(job_id TEXT PRIMARY KEY, space_id TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)")
            pending = conn.execute("SELECT job_id FROM asset_jobs WHERE status IN ('queued','running') ORDER BY rowid").fetchall()
        for (job_id,) in pending:
            self._futures[job_id] = self._pool.submit(self._process, job_id)

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.database, timeout=30)
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def _save(self, record):
        record["updated_at"] = datetime.now(timezone.utc).isoformat()
        with self._connection() as conn:
            conn.execute("INSERT INTO asset_jobs VALUES(?,?,?,?) ON CONFLICT(job_id) DO UPDATE SET status=excluded.status,payload=excluded.payload", (record["job_id"], record["space_id"], record["status"], json.dumps(record, ensure_ascii=False)))

    def get(self, job_id):
        with self._connection() as conn:
            row = conn.execute("SELECT payload FROM asset_jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return json.loads(row[0])

    def list(self, space_id):
        with self._connection() as conn:
            rows = conn.execute("SELECT payload FROM asset_jobs WHERE space_id=? ORDER BY rowid DESC", (space_id,)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def submit(self, filename, content, space_id, *, evaluate=False):
        if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise DocumentParseError("不支持此格式；请将旧版 Word/Excel 转为 DOCX/XLSX")
        if len(content) > 30 * 1024 * 1024:
            raise DocumentParseError("单个文件不能超过 30 MB")
        result = self.object_store.ingest(filename, content, space_id=space_id)
        record = {"job_id": f"ingest-{uuid4().hex}", "space_id": space_id, "filename": Path(filename).name,
                  "asset_id": result.record.asset_id, "size_bytes": len(content), "status": "queued", "stage": "queued",
                  "chunk_count": 0, "source_id": None, "error": None, "history": [],
                  "evaluation_status": "not_requested" if not evaluate else "not_configured"}
        self._save(record)
        self._futures[record["job_id"]] = self._pool.submit(self._process, record["job_id"])
        return record

    def retry(self, job_id):
        with self._lock:
            record = self.get(job_id)
            if record["status"] != "failed":
                raise ValueError("只有处理失败的资料需要重试")
            future = self._futures.get(job_id)
            if future is not None and not future.done():
                raise ValueError("资料仍在处理")
            record.update(status="queued", stage="queued", error=None)
            self._save(record)
            self._futures[job_id] = self._pool.submit(self._process, job_id)
            return record

    def delete(self, job_id):
        """Remove a completed asset from index, registry, staging and object store."""
        with self._lock, FileLock(str(self.root / "publish.lock")):
            record = self.get(job_id)
            if record["status"] in {"queued", "running"}:
                raise ValueError("资料仍在处理，完成后才能删除")
            workflow = self.workflow_factory(record["space_id"])
            source_id = record.get("source_id")
            if source_id:
                ids = []
                try:
                    existing = workflow.knowledge_base.chroma.get(where={"source_id": source_id})
                    ids = list(existing.get("ids") or [])
                except Exception:
                    pass
                if ids:
                    workflow.knowledge_base.chroma.delete(ids=ids)
                registry = workflow._read_registry()
                registry = [item for item in registry if item.get("source_id") != source_id]
                workflow.registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
                workflow.active_profile_path.write_text(json.dumps(workflow._build_profile(registry), ensure_ascii=False, indent=2), encoding="utf-8")
                staged_dir = workflow.staging_directory / source_id
                import shutil
                shutil.rmtree(staged_dir, ignore_errors=True)
                (workflow.uploaded_documents_directory / f"{source_id}.md").unlink(missing_ok=True)
            try:
                self.object_store.delete_asset(record["asset_id"])
            except AttributeError:
                pass
            record.update(status="deleted", stage="deleted", error=None)
            self._save(record)
            return record

    def _process(self, job_id):
        # All processes sharing this local library serialize registry/index writes.
        # Recovery can schedule the same job; the terminal-state check avoids replay.
        with FileLock(str(self.root / "publish.lock")):
            if self.get(job_id)["status"] in {"completed", "failed"}:
                return
            self._process_locked(job_id)

    def _process_locked(self, job_id):
        record = self.get(job_id)
        def progress(stage):
            record.update(stage=stage, status="running")
            record["history"].append({"stage": stage, "at": datetime.now(timezone.utc).isoformat()})
            self._save(record)
        try:
            content = self.object_store.read_asset(record["asset_id"])
            workflow = self.workflow_factory(record["space_id"])
            staged = workflow.stage_file(record["filename"], content, metadata={"space_id": record["space_id"], "asset_id": record["asset_id"]}, vision=self.vision, on_progress=progress)
            record.update(source_id=staged.source_id, chunk_count=staged.chunk_count)
            self._save(record)
            result = workflow.publish(staged, evaluate=False, on_progress=progress)
            if not result.published and result.reason != "already_published":
                raise RuntimeError("publication did not complete")
            record.update(status="completed", stage="completed", error=None)
            record["history"].append({"stage": "completed", "at": datetime.now(timezone.utc).isoformat()})
        except DocumentParseError as exc:
            record.update(status="failed", error=str(exc))
        except Exception as exc:
            # Provider exceptions may include headers or credentials.
            record.update(status="failed", error=f"{record['stage']} 阶段失败（{type(exc).__name__}），请检查文件和嵌入/视觉模型配置后重试")
        self._save(record)

    def _workflow(self, space_id):
        from core.ingestion_workflow import IngestionWorkflow
        with self._lock:
            if space_id not in self._workflows:
                directory = self.root / hashlib.sha256(space_id.encode()).hexdigest()
                kb = _AssetKnowledgeBase(directory / "chroma", self._embedding_model)
                self._workflows[space_id] = IngestionWorkflow(knowledge_base=kb, staging_directory=directory / "staging", registry_path=directory / "sources.json", active_profile_path=directory / "corpus.json", uploaded_documents_directory=directory / "documents")
            return self._workflows[space_id]

    def _embedding_model(self):
        if self._embedding is None:
            from config.provider_factory import LocalSentenceTransformerEmbeddings
            from config.model_paths import get_bge_m3_path
            model_path = os.environ.get("LOCALRAG_ASSET_EMBEDDING_MODEL") or get_bge_m3_path()
            if not Path(model_path).exists():
                raise DocumentParseError("未找到本地嵌入模型，请配置 LOCALRAG_ASSET_EMBEDDING_MODEL 后重试")
            self._embedding = LocalSentenceTransformerEmbeddings(model_path)
        return self._embedding

    def search(self, space_id, query):
        # Do not expose partially indexed documents while a publish may still roll back.
        with FileLock(str(self.root / "publish.lock")):
            if not any(job["status"] == "completed" for job in self.list(space_id)):
                return []
            workflow = self.workflow_factory(space_id)
            return [{"text": doc.page_content, "metadata": doc.metadata} for doc in workflow.knowledge_base.chroma.similarity_search(query, k=5)]

    def close(self):
        self._pool.shutdown(wait=True)


def configured_vision(model_config):
    """Resolve only an explicitly image-capable enabled profile at call time."""
    def extract(content, media_type):
        from openai import OpenAI
        raw = model_config.load()
        candidates = [(key, value) for key, value in raw["model_profiles"].items() if value.get("enabled") and "image" in value.get("modalities", [])]
        for _, profile in sorted(candidates):
            key = profile.get("api_key") or os.environ.get(profile.get("api_key_env", ""), "")
            if not key:
                continue
            with OpenAI(api_key=key, base_url=profile["base_url"], timeout=90, max_retries=1) as client:
                response = client.chat.completions.create(model=profile["model"], messages=[{"role": "user", "content": [{"type": "text", "text": "提取图中可读文字、表格与图示说明。保持原文和表格对应关系，不推测不可见内容。"}, {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{base64.b64encode(content).decode()}"}}]}], max_tokens=4096)
            text = response.choices[0].message.content
            if not text or not text.strip():
                raise DocumentParseError("视觉模型没有返回可索引内容")
            return text
        raise DocumentParseError("需要在模型设置中启用一个支持图片且已配置 API Key 的模型")
    return extract
