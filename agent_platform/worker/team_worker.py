"""Bounded background worker for Runtime jobs.

This is the process-local D36 worker boundary. Jobs are claimed before model
execution and report success/failure through callbacks; a later PostgreSQL
worker can implement the same interface with the lease rows from the schema.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from threading import RLock
from typing import Callable, Generic, TypeVar
from uuid import uuid4


T = TypeVar("T")


@dataclass(frozen=True)
class WorkerJob(Generic[T]):
    job_id: str
    status: str
    result: T | None = None
    error: str | None = None


class TeamWorker:
    """One bounded executor with observable jobs and clean shutdown."""

    def __init__(self, *, max_workers: int = 2) -> None:
        if type(max_workers) is not int or max_workers < 1:
            raise ValueError("max_workers must be positive")
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="localrag-worker")
        self._lock = RLock()
        self._jobs: dict[str, WorkerJob[object]] = {}
        self._futures: dict[str, Future[object]] = {}

    def submit(self, operation: Callable[[], T]) -> WorkerJob[T]:
        job_id = f"job-{uuid4().hex}"
        with self._lock:
            self._jobs[job_id] = WorkerJob(job_id, "queued")
            future: Future[T] = self._executor.submit(operation)
            self._futures[job_id] = future  # type: ignore[assignment]
            self._jobs[job_id] = WorkerJob(job_id, "running")
            future.add_done_callback(lambda done: self._finish(job_id, done))
            return self._jobs[job_id]  # type: ignore[return-value]

    def get(self, job_id: str) -> WorkerJob[object]:
        with self._lock:
            if job_id not in self._jobs:
                raise KeyError(job_id)
            return self._jobs[job_id]

    def _finish(self, job_id: str, future: Future[object]) -> None:
        with self._lock:
            try:
                self._jobs[job_id] = WorkerJob(job_id, "completed", result=future.result())
            except Exception as exc:
                self._jobs[job_id] = WorkerJob(job_id, "failed", error=type(exc).__name__)

    def close(self) -> None:
        self._executor.shutdown(wait=True, cancel_futures=True)
