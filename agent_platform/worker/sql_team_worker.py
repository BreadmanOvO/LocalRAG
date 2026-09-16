"""Cross-process worker backed by the Runtime SQL job queue."""
from __future__ import annotations

import threading
import time
from typing import Any, Callable

from agent_platform.runtime.sql_runtime_store import SqlRuntimeStore


class SqlTeamWorker:
    """Poll, lease and execute durable jobs.

    The handler receives the persisted payload and must be idempotent. API
    keys are intentionally not present in payloads; handlers resolve secrets
    from the local model configuration at execution time.
    """
    def __init__(self, store: SqlRuntimeStore, handler: Callable[[dict[str, Any]], Any], *, worker_id: str, lease_seconds: int = 60, poll_interval: float = 0.25) -> None:
        self.store, self.handler, self.worker_id = store, handler, worker_id
        self.lease_seconds, self.poll_interval = lease_seconds, poll_interval
        self._stop = threading.Event()

    def run_once(self) -> bool:
        job = self.store.claim_job(self.worker_id, lease_seconds=self.lease_seconds)
        if not job:
            return False
        try:
            self.handler(dict(job.get("payload") or {}))
        except Exception as exc:
            self.store.finish_job(job["job_id"], worker_id=self.worker_id, attempt_count=int(job["attempt_count"]), status="failed", error_code=type(exc).__name__)
        else:
            self.store.finish_job(job["job_id"], worker_id=self.worker_id, attempt_count=int(job["attempt_count"]), status="completed")
        return True

    def run_forever(self) -> None:
        while not self._stop.is_set():
            if not self.run_once():
                self._stop.wait(self.poll_interval)

    def stop(self) -> None:
        self._stop.set()
