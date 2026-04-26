from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REQUIRED_KEY_FIELDS = (
    "dashscope_api_key",
    "dashscope_base_url",
    "chat_model_name",
    "embedding_model_name",
)


@dataclass(frozen=True)
class BailianRuntimeConfig:
    dashscope_api_key: str
    dashscope_base_url: str
    chat_model_name: str
    embedding_model_name: str


def get_root_key_path() -> Path:
    return Path(__file__).resolve().parent / "key.json"


def load_bailian_runtime_config(path: Path | None = None) -> BailianRuntimeConfig:
    key_path = get_root_key_path() if path is None else path

    if not key_path.exists():
        raise RuntimeError("Missing required root key.json file")

    try:
        raw_data = json.loads(key_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Malformed key.json") from exc

    if not isinstance(raw_data, dict):
        raise RuntimeError("Malformed key.json")

    values: dict[str, str] = {}
    for field in REQUIRED_KEY_FIELDS:
        if field not in raw_data:
            raise RuntimeError(f"Missing required key.json field: {field}")
        value = raw_data[field]
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"Empty required key.json field: {field}")
        values[field] = value.strip()

    return BailianRuntimeConfig(**values)
