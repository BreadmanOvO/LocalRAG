from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ACTIVE_CORPUS_CONTRACT_VERSION = "active-corpus-v2"
DEFAULT_ACTIVE_CORPUS_PATH = Path(__file__).resolve().with_name("active_corpus.json")


@dataclass(frozen=True)
class ActiveCorpusProfile:
    contract_version: str
    release_version: str
    persist_directory: Path
    collection_name: str
    source_count: int
    chunk_count: int
    corpus_fingerprint: str
    registry_fingerprint: str


def _required_string(payload: dict[str, Any], field_name: str) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"Invalid active corpus field: {field_name}")
    return value.strip()


def _fingerprint(payload: dict[str, Any], field_name: str) -> str:
    value = _required_string(payload, field_name)
    prefix, separator, digest = value.partition(":")
    if separator != ":" or prefix != "sha256" or len(digest) != 64:
        raise RuntimeError(f"Invalid active corpus fingerprint: {field_name}")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise RuntimeError(f"Invalid active corpus fingerprint: {field_name}") from exc
    return value


def _positive_int(payload: dict[str, Any], field_name: str) -> int:
    value = payload.get(field_name)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise RuntimeError(f"Invalid active corpus field: {field_name}")
    return value


def load_active_corpus_profile(
    path: str | Path = DEFAULT_ACTIVE_CORPUS_PATH,
    *,
    project_root: str | Path | None = None,
) -> ActiveCorpusProfile:
    profile_path = Path(path).resolve()
    try:
        payload = json.loads(profile_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing active corpus profile: {profile_path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Malformed active corpus profile: {profile_path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Malformed active corpus profile: {profile_path}")

    contract_version = _required_string(payload, "contract_version")
    if contract_version != ACTIVE_CORPUS_CONTRACT_VERSION:
        raise RuntimeError(f"Unsupported active corpus contract: {contract_version}")

    raw_persist_directory = Path(_required_string(payload, "persist_directory"))
    root = Path(project_root or Path(__file__).resolve().parents[1]).resolve()
    persist_directory = (
        raw_persist_directory
        if raw_persist_directory.is_absolute()
        else root / raw_persist_directory
    ).resolve()

    return ActiveCorpusProfile(
        contract_version=contract_version,
        release_version=_required_string(payload, "release_version"),
        persist_directory=persist_directory,
        collection_name=_required_string(payload, "collection_name"),
        source_count=_positive_int(payload, "source_count"),
        chunk_count=_positive_int(payload, "chunk_count"),
        corpus_fingerprint=_fingerprint(payload, "corpus_fingerprint"),
        registry_fingerprint=_fingerprint(payload, "registry_fingerprint"),
    )
