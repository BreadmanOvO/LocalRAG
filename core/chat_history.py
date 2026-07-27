import hashlib
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


def message_identity(message: BaseMessage) -> str:
    message_id = getattr(message, "id", None)
    if message_id is not None:
        stripped_id = str(message_id).strip()
        if stripped_id:
            return f"id:{stripped_id}"

    serialized = json.dumps(
        message_to_dict(message),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


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

    def add_messages_unique(self, messages: Sequence[BaseMessage]) -> None:
        incoming_messages = list(messages)
        if not incoming_messages:
            return

        with self._lock:
            stored_messages = self.messages
            stored_identities = [message_identity(message) for message in stored_messages]
            incoming_identities = [
                message_identity(message) for message in incoming_messages
            ]
            overlap = 0
            for size in range(
                min(len(stored_identities), len(incoming_identities)),
                0,
                -1,
            ):
                if stored_identities[-size:] == incoming_identities[:size]:
                    overlap = size
                    break

            # Prefer transcript completeness for a single hash overlap;
            # replay inference requires a multi-message state envelope.
            if overlap == 1 and incoming_identities[0].startswith("sha256:"):
                overlap = 0

            seen_explicit_ids = {
                identity for identity in stored_identities if identity.startswith("id:")
            }
            additions = []
            for message, identity in zip(
                incoming_messages[overlap:],
                incoming_identities[overlap:],
                strict=True,
            ):
                if identity.startswith("id:"):
                    if identity in seen_explicit_ids:
                        continue
                    seen_explicit_ids.add(identity)
                additions.append(message)

            if additions:
                self._write_messages([*stored_messages, *additions])

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
