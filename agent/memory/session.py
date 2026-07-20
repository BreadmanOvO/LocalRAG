from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from typing import Any

from utils.session import validate_session_id


@dataclass(frozen=True)
class RetrievalSnapshot:
    query: str
    documents: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "documents": deepcopy(list(self.documents)),
        }


class SessionRetrievalMemory:
    """Keep the latest retrieval result isolated by agent session."""

    def __init__(self) -> None:
        self._snapshots: dict[str, RetrievalSnapshot] = {}
        self._lock = RLock()

    def remember(self, session_id: str, query: str, documents: list[dict[str, Any]]) -> None:
        session_id = validate_session_id(session_id)
        snapshot = RetrievalSnapshot(
            query=str(query),
            documents=tuple(deepcopy(documents)),
        )
        with self._lock:
            self._snapshots[session_id] = snapshot

    def recall(self, session_id: str) -> RetrievalSnapshot | None:
        session_id = validate_session_id(session_id)
        with self._lock:
            snapshot = self._snapshots.get(session_id)
            if snapshot is None:
                return None
            return RetrievalSnapshot(snapshot.query, tuple(deepcopy(snapshot.documents)))

    def clear(self, session_id: str) -> None:
        session_id = validate_session_id(session_id)
        with self._lock:
            self._snapshots.pop(session_id, None)
