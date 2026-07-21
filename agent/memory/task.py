import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from utils.path_tools import get_abs_path
from utils.session import validate_task_id


_ITEM_CATEGORIES = {
    "searched_query",
    "retrieved_source",
    "confirmed_source",
    "finding",
    "evidence_gap",
    "open_question",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_memory_value(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if len(normalized) > 4000:
        raise ValueError(f"{field_name} must not exceed 4000 characters")
    return normalized


@dataclass(frozen=True)
class TaskMemorySnapshot:
    task_id: str
    topic: str
    searched_queries: tuple[str, ...]
    retrieved_sources: tuple[str, ...]
    confirmed_sources: tuple[str, ...]
    findings: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    open_questions: tuple[str, ...]
    created_at: str
    updated_at: str

    @property
    def is_empty(self) -> bool:
        return not any(
            (
                self.topic,
                self.searched_queries,
                self.retrieved_sources,
                self.confirmed_sources,
                self.findings,
                self.evidence_gaps,
                self.open_questions,
            )
        )

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "topic": self.topic,
            "searched_queries": list(self.searched_queries),
            "retrieved_sources": list(self.retrieved_sources),
            "confirmed_sources": list(self.confirmed_sources),
            "findings": list(self.findings),
            "evidence_gaps": list(self.evidence_gaps),
            "open_questions": list(self.open_questions),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class TaskMemoryPolicy:
    enabled: bool = True


class TaskMemoryStore:
    """Persist task-scoped research memory without storing developer preferences."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        default_path = Path(get_abs_path("agent_memory/task_memory.sqlite3"))
        self.db_path = Path(db_path).resolve() if db_path is not None else default_path.resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode = WAL;

                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    topic TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS task_memory_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    category TEXT NOT NULL CHECK (
                        category IN (
                            'searched_query',
                            'retrieved_source',
                            'confirmed_source',
                            'finding',
                            'evidence_gap',
                            'open_question'
                        )
                    ),
                    value TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(task_id, category, value),
                    FOREIGN KEY(task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_task_memory_items_task_category
                ON task_memory_items(task_id, category, id);
                """
            )

    def ensure_task(self, task_id: str, topic: str = "") -> None:
        task_id = validate_task_id(task_id)
        topic = _clean_memory_value(topic, "topic")
        now = _utc_now()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO tasks(task_id, topic, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (task_id, topic, now, now),
            )
            if topic:
                connection.execute(
                    "UPDATE tasks SET topic = ?, updated_at = ? WHERE task_id = ?",
                    (topic, now, task_id),
                )

    def set_topic(self, task_id: str, topic: str) -> None:
        task_id = validate_task_id(task_id)
        topic = _clean_memory_value(topic, "topic")
        self.ensure_task(task_id)
        with self._lock, self._connect() as connection:
            connection.execute(
                "UPDATE tasks SET topic = ?, updated_at = ? WHERE task_id = ?",
                (topic, _utc_now(), task_id),
            )

    def add_item(self, task_id: str, category: str, value: str, source: str) -> None:
        task_id = validate_task_id(task_id)
        if category not in _ITEM_CATEGORIES:
            raise ValueError(f"unsupported task memory category: {category}")
        value = _clean_memory_value(value, category)
        source = _clean_memory_value(source, "source")
        if not value:
            return

        self.ensure_task(task_id)
        now = _utc_now()
        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO task_memory_items(task_id, category, value, source, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (task_id, category, value, source or "unknown", now),
            )
            connection.execute(
                "UPDATE tasks SET updated_at = ? WHERE task_id = ?",
                (now, task_id),
            )

    def remove_item(self, task_id: str, category: str, value: str) -> None:
        task_id = validate_task_id(task_id)
        if category not in _ITEM_CATEGORIES:
            raise ValueError(f"unsupported task memory category: {category}")
        value = _clean_memory_value(value, category)
        if not value:
            return

        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM task_memory_items WHERE task_id = ? AND category = ? AND value = ?",
                (task_id, category, value),
            )
            if cursor.rowcount:
                connection.execute(
                    "UPDATE tasks SET updated_at = ? WHERE task_id = ?",
                    (_utc_now(), task_id),
                )

    def replace_item(
        self,
        task_id: str,
        category: str,
        old_value: str,
        new_value: str,
        *,
        source: str = "ui_correction",
    ) -> None:
        task_id = validate_task_id(task_id)
        if category not in _ITEM_CATEGORIES:
            raise ValueError(f"unsupported task memory category: {category}")
        old_value = _clean_memory_value(old_value, category)
        new_value = _clean_memory_value(new_value, category)
        source = _clean_memory_value(source, "source")
        if not new_value:
            raise ValueError("new_value must not be empty")

        self.ensure_task(task_id)
        now = _utc_now()
        with self._lock, self._connect() as connection:
            if old_value:
                connection.execute(
                    "DELETE FROM task_memory_items "
                    "WHERE task_id = ? AND category = ? AND value = ?",
                    (task_id, category, old_value),
                )
            connection.execute(
                """
                INSERT OR IGNORE INTO task_memory_items(task_id, category, value, source, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (task_id, category, new_value, source or "ui_correction", now),
            )
            connection.execute(
                "UPDATE tasks SET updated_at = ? WHERE task_id = ?",
                (now, task_id),
            )

    def record_retrieval(self, task_id: str, query: str, source_ids: list[str]) -> None:
        self.add_item(task_id, "searched_query", query, source="rag_search")
        for source_id in source_ids:
            self.add_item(task_id, "retrieved_source", str(source_id), source="rag_search")

    def update_task(
        self,
        task_id: str,
        *,
        topic: str = "",
        finding: str = "",
        evidence_gap: str = "",
        open_question: str = "",
        confirmed_source: str = "",
    ) -> None:
        topic = _clean_memory_value(topic, "topic")
        if topic:
            self.set_topic(task_id, topic)
        for category, value in (
            ("finding", finding),
            ("evidence_gap", evidence_gap),
            ("open_question", open_question),
            ("confirmed_source", confirmed_source),
        ):
            self.add_item(task_id, category, value, source="agent_memory_tool")

    def get_task(self, task_id: str) -> TaskMemorySnapshot:
        task_id = validate_task_id(task_id)
        with self._lock, self._connect() as connection:
            task_row = connection.execute(
                "SELECT task_id, topic, created_at, updated_at FROM tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            item_rows = connection.execute(
                """
                SELECT category, value
                FROM task_memory_items
                WHERE task_id = ?
                ORDER BY id
                """,
                (task_id,),
            ).fetchall()

        grouped = {category: [] for category in _ITEM_CATEGORIES}
        for row in item_rows:
            grouped[row["category"]].append(row["value"])

        return TaskMemorySnapshot(
            task_id=task_id,
            topic=task_row["topic"] if task_row else "",
            searched_queries=tuple(grouped["searched_query"]),
            retrieved_sources=tuple(grouped["retrieved_source"]),
            confirmed_sources=tuple(grouped["confirmed_source"]),
            findings=tuple(grouped["finding"]),
            evidence_gaps=tuple(grouped["evidence_gap"]),
            open_questions=tuple(grouped["open_question"]),
            created_at=task_row["created_at"] if task_row else "",
            updated_at=task_row["updated_at"] if task_row else "",
        )

    def clear_task(self, task_id: str) -> None:
        task_id = validate_task_id(task_id)
        with self._lock, self._connect() as connection:
            connection.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
