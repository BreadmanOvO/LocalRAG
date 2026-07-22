import json
import os
import threading
from pathlib import Path
from typing import Sequence
from uuid import uuid4

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

from utils.path_tools import get_abs_path
from utils.session import validate_session_id


class ChatHistoryCorruptionError(ValueError):
    pass


_LOCKS_GUARD = threading.Lock()
_FILE_LOCKS: dict[Path, threading.RLock] = {}


def _file_lock(path: Path) -> threading.RLock:
    with _LOCKS_GUARD:
        return _FILE_LOCKS.setdefault(path, threading.RLock())


def get_history(session_id: str) -> "FileChatMessageHistory":
    return FileChatMessageHistory(session_id, get_abs_path("chat_history"))


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, storage_path: str):
        self.session_id = validate_session_id(session_id)
        self.storage_path = Path(storage_path).resolve()
        self.file_path = self.storage_path / self.session_id
        self._lock = _file_lock(self.file_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        with self._lock:
            all_messages = [*self.messages, *messages]
            self._write_messages(all_messages)

    def _write_messages(self, messages: Sequence[BaseMessage]) -> None:
        serialized = [message_to_dict(message) for message in messages]
        temp_path = self.storage_path / f".{self.session_id}.{uuid4().hex}.tmp"
        try:
            with temp_path.open("x", encoding="utf-8") as file:
                json.dump(serialized, file, ensure_ascii=False)
                file.flush()
                os.fsync(file.fileno())
            temp_path.replace(self.file_path)
        finally:
            temp_path.unlink(missing_ok=True)

    @property
    def messages(self) -> list[BaseMessage]:
        with self._lock:
            try:
                with self.file_path.open("r", encoding="utf-8") as file:
                    return messages_from_dict(json.load(file))
            except FileNotFoundError:
                return []
            except (json.JSONDecodeError, UnicodeDecodeError, TypeError, KeyError, ValueError) as exc:
                raise ChatHistoryCorruptionError(
                    f"chat history is corrupt: {self.file_path}"
                ) from exc

    def clear(self) -> None:
        with self._lock:
            self._write_messages([])
