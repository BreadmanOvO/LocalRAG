"""Run a durable Runtime worker against PostgreSQL.

This command intentionally executes a small injectable acknowledgement handler
by default. Production deployments should import their execution handler and
keep credentials in the model-config secret provider, never in job payloads.
"""
from __future__ import annotations

import argparse
import os
import uuid

from sqlalchemy import create_engine

from agent_platform.runtime.sql_runtime_store import SqlRuntimeStore
from agent_platform.worker.sql_team_worker import SqlTeamWorker


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.environ.get("LOCALRAG_DATABASE_URL"))
    parser.add_argument("--worker-id", default=f"worker-{uuid.uuid4().hex[:8]}")
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if not args.database_url:
        parser.error("--database-url or LOCALRAG_DATABASE_URL is required")
    store = SqlRuntimeStore(create_engine(args.database_url, pool_pre_ping=True), create_schema=False)
    worker = SqlTeamWorker(store, lambda payload: None, worker_id=args.worker_id)
    if args.once:
        worker.run_once()
    else:
        worker.run_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
