"""Room execution leases and frozen bindings, shared by API processes.

Credentials are loaded from local configuration and never stored here.
Step checkpoints remain in the existing append-only SQL event store.
"""
from contextlib import contextmanager
from time import time
from uuid import uuid4

from sqlalchemy import Column, Float, JSON, MetaData, String, Table, insert, select, update
from sqlalchemy.exc import IntegrityError


class RoomLeaseBusy(RuntimeError):
    pass


class DurableTeamStore:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = MetaData()
        self.rooms = Table("runtime_room_leases", self.metadata,
            Column("room_id", String(255), primary_key=True),
            Column("owner", String(255), nullable=False),
            Column("expires_at", Float, nullable=False),
            Column("bindings", JSON, nullable=False))
        if engine.dialect.name == "sqlite":
            self.metadata.create_all(engine)

    def claim(self, room_id: str, ttl: float = 90) -> str:
        token = uuid4().hex
        now = time()
        try:
            with self.engine.begin() as conn:
                existing = conn.execute(select(self.rooms.c.room_id).where(self.rooms.c.room_id == room_id)).first()
                if existing is None:
                    conn.execute(insert(self.rooms).values(room_id=room_id, owner=token, expires_at=now + ttl, bindings=[]))
                else:
                    changed = conn.execute(update(self.rooms).where(self.rooms.c.room_id == room_id,
                        self.rooms.c.expires_at <= now).values(owner=token, expires_at=now + ttl))
                    if changed.rowcount != 1:
                        raise RoomLeaseBusy("房间仍有任务执行；中断后最多等待 90 秒再恢复")
        except IntegrityError as exc:
            raise RoomLeaseBusy("房间已被其他执行器领取") from exc
        return token

    def heartbeat(self, room_id: str, token: str, ttl: float = 90) -> None:
        with self.engine.begin() as conn:
            changed = conn.execute(update(self.rooms).where(self.rooms.c.room_id == room_id,
                self.rooms.c.owner == token, self.rooms.c.expires_at > time()).values(expires_at=time() + ttl))
            if changed.rowcount != 1:
                raise RoomLeaseBusy("执行租约已失效，拒绝继续提交")

    def release(self, room_id: str, token: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(update(self.rooms).where(self.rooms.c.room_id == room_id,
                self.rooms.c.owner == token).values(expires_at=0))

    def save_bindings(self, room_id: str, token: str, bindings: list[dict]) -> None:
        with self.engine.begin() as conn:
            result = conn.execute(update(self.rooms).where(self.rooms.c.room_id == room_id,
                self.rooms.c.owner == token, self.rooms.c.expires_at > time()).values(bindings=bindings))
            if result.rowcount != 1:
                raise RoomLeaseBusy("执行租约已失效")

    def bindings(self, room_id: str) -> list[dict]:
        with self.engine.connect() as conn:
            row = conn.execute(select(self.rooms.c.bindings).where(self.rooms.c.room_id == room_id)).first()
            return row[0] if row else []

    def active(self, room_id: str) -> bool:
        with self.engine.connect() as conn:
            return conn.execute(select(self.rooms.c.room_id).where(self.rooms.c.room_id == room_id,
                self.rooms.c.expires_at > time())).first() is not None

    @contextmanager
    def exclusive(self, room_id: str):
        token = self.claim(room_id)
        try:
            yield token
        finally:
            self.release(room_id, token)
