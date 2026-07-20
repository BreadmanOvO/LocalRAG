import json
from pathlib import Path
from typing import Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

from utils.path_tools import get_abs_path
from utils.session import validate_session_id


def get_history(session_id: str) -> "FileChatMessageHistory":
    return FileChatMessageHistory(session_id, get_abs_path("chat_history"))


class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str, storage_path: str):
        self.session_id = validate_session_id(session_id)
        self.storage_path = Path(storage_path).resolve()
        self.file_path = self.storage_path / self.session_id
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        all_messages = [*self.messages, *messages]
        serialized = [message_to_dict(message) for message in all_messages]
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(serialized, file, ensure_ascii=False)

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                return messages_from_dict(json.load(file))
        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump([], file)
