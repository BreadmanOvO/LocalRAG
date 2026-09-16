"""Copy an idle legacy in-memory API into the local durable database.

Keeps an independent JSON backup; refuses to overwrite existing room IDs.
Run as ``python -m scripts.preserve_local_rooms`` before restarting the API.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from sqlalchemy import update

from agent_platform.conversations.sql_repository import SqlAlchemyConversationRepository
from agent_platform.runtime.sql_event_store import SqlAlchemyEventStore


def main():
    root = Path(__file__).resolve().parents[1] / ".localrag"
    root.mkdir(exist_ok=True)
    session = requests.Session()
    base = "http://127.0.0.1:8000"

    def get(path, **params):
        response = session.get(base + path, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def pages(room_id, kind):
        items, after = [], 0
        while True:
            batch = get(f"/rooms/{room_id}/{kind}", after=after, limit=1000)
            items.extend(batch["items"])
            if len(batch["items"]) < 1000:
                return items
            after = batch["next"]

    snapshots = []
    for room in get("/rooms")["items"]:
        rid = room["room_id"]
        events = pages(rid, "events")
        running = {e["run_id"] for e in events if e["event_type"] == "run_started"}
        finished = {e["run_id"] for e in events if e["event_type"] in {"run_completed", "run_failed", "run_cancelled"}}
        if running - finished:
            raise RuntimeError("A room is still running; wait for completion before migration")
        snapshots.append({"room": room, "events": events, "messages": pages(rid, "messages"), "members": get(f"/rooms/{rid}/members")["items"]})
    backup = root / ("rooms-before-persistence-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".json")
    backup.write_text(json.dumps(snapshots, ensure_ascii=False, indent=2), encoding="utf-8")
    repo = SqlAlchemyConversationRepository.from_url(f"sqlite:///{(root / 'workspace.sqlite3').as_posix()}")
    store = SqlAlchemyEventStore(repo.engine)
    existing = {r.room_id for r in repo.list_rooms()}
    migrated = 0
    for snapshot in snapshots:
        room = snapshot["room"]
        rid = room["room_id"]
        if rid in existing:
            continue
        repo.create_room(room["space_id"], room["title"], room_id=rid)
        for m in snapshot["messages"]:
            repo.save_message(rid, m["content"], role=m["role"], message_id=m["message_id"], idempotency_key=m.get("idempotency_key"))
        for member in snapshot["members"]:
            repo.join_member(rid, member["agent_id"])
        for e in snapshot["events"]:
            store.append(rid, e["event_type"], event_id=e["identity"]["event_id"], task_id=e.get("task_id"), run_id=e.get("run_id"), step_id=e.get("step_id"), attempt_id=e.get("attempt_id"),
                caused_by=tuple(e.get("caused_by", [])), payload=e["payload"], run_sequence=e.get("run_sequence", 0))
            with repo.engine.begin() as conn:
                conn.execute(update(store.events).where(store.events.c.event_id == e["identity"]["event_id"]).values(timestamp=e["timestamp"]))
        if room["status"] == "archived":
            repo.archive_room(rid)
        migrated += 1
    print(f"Preserved {migrated} rooms; backup: {backup.name}")
    repo.close()


if __name__ == "__main__":
    main()
