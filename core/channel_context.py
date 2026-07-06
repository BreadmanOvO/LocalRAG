from __future__ import annotations

import re
from typing import Any


CHANNEL_TABLE_HEADER = "channel_table_rows:"

_CHANNEL_PATTERN = r"/(?:apollo|Apollo|perception)(?:/[A-Za-z0-9_.-]+)+"
_CHANNEL_RE = re.compile(_CHANNEL_PATTERN)
_BEFORE_INPUT_DESC_RE = re.compile(
    rf"(?P<desc>输入[^\s/，。；:：]{{1,30}}?信息)\s+(?P<channel>{_CHANNEL_PATTERN})"
)
_BEFORE_KNOWN_DESC_RE = re.compile(
    rf"(?P<desc>局部地图信息)\s+(?P<channel>{_CHANNEL_PATTERN})"
)
_PATH_INPUT_IS_DESC_RE = re.compile(
    rf"(?P<channel>{_CHANNEL_PATTERN})\s*输入是\s*(?P<desc>[^/\s，。；:：][^/。；\n]{{0,40}}?信息)"
)
_PATH_MARKED_DESC_RE = re.compile(
    rf"(?P<channel>{_CHANNEL_PATTERN})\s*(?P<desc>(?:输入|输出)[^\s/，。；:：]{{1,40}}?信息)"
)
_PATH_SPACED_MARKER_DESC_RE = re.compile(
    rf"(?P<channel>{_CHANNEL_PATTERN})\s*(?:输入|输出)\s+"
    r"(?P<desc>[^\s/，。；:：][^/。；\n]{0,50}?信息(?:，[^/。；\n]{0,50})?)"
)
_PATH_SIMPLE_DESC_RE = re.compile(
    rf"(?P<channel>{_CHANNEL_PATTERN})\s+"
    r"(?P<desc>(?:定位信息|规划信息|预测轨迹|控制信息|感知信息)[^/。；\n]{0,50})"
)


def should_structure_apollo_channel_context(
    text: str,
    metadata: dict[str, Any] | None = None,
) -> bool:
    if not text or "channel" not in text.lower() or not _CHANNEL_RE.search(text):
        return False

    if metadata is None:
        return True

    source_id = str(metadata.get("source_id", "")).lower()
    source_path = str(metadata.get("source", "")).replace("\\", "/").lower()
    doc_type = str(metadata.get("doc_type", "")).lower()
    is_apollo_source = (
        source_id.startswith("apollo-doc-")
        or "data/sources/apollo/" in source_path
        or source_path.startswith("apollo/")
    )
    is_official_doc = doc_type in {"", "official_doc"}
    return is_apollo_source and is_official_doc


def _normalize_space(text: str) -> str:
    return " ".join(str(text or "").split())


def _clean_channel(channel: str) -> str:
    return str(channel or "").strip(" ,，。；;:：)]}》")


def _clean_description(description: str) -> str:
    value = _normalize_space(description)
    value = value.strip(" -:：,，。；;")
    value = re.sub(r"^(输入是|对应|说明为)\s*", "", value)
    if not value or "channel名称" in value or "channel说明" in value:
        return ""
    if len(value) > 90:
        return ""
    return value


def _add_row(
    rows: list[dict[str, Any]],
    seen: set[tuple[str, str]],
    *,
    channel: str,
    description: str,
    position: int,
) -> None:
    cleaned_channel = _clean_channel(channel)
    cleaned_description = _clean_description(description)
    if not cleaned_channel or not cleaned_description:
        return

    key = (cleaned_channel.lower(), cleaned_description)
    if key in seen:
        return

    seen.add(key)
    rows.append(
        {
            "channel": cleaned_channel,
            "description": cleaned_description,
            "position": position,
        }
    )


def extract_apollo_channel_rows(text: str) -> list[dict[str, str]]:
    normalized = _normalize_space(text)
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    patterns = (
        _PATH_INPUT_IS_DESC_RE,
        _BEFORE_INPUT_DESC_RE,
        _BEFORE_KNOWN_DESC_RE,
        _PATH_MARKED_DESC_RE,
        _PATH_SPACED_MARKER_DESC_RE,
        _PATH_SIMPLE_DESC_RE,
    )

    for pattern in patterns:
        for match in pattern.finditer(normalized):
            _add_row(
                rows,
                seen,
                channel=match.group("channel"),
                description=match.group("desc"),
                position=match.start("channel"),
            )

    rows.sort(key=lambda row: row["position"])
    return [
        {
            "description": str(row["description"]),
            "channel": str(row["channel"]),
        }
        for row in rows
    ]


def structure_apollo_channel_context(
    text: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    if not should_structure_apollo_channel_context(text, metadata):
        return ""

    rows = extract_apollo_channel_rows(text)
    if len(rows) < 2:
        return ""

    lines = [CHANNEL_TABLE_HEADER]
    for row in rows:
        lines.append(f"- 说明: {row['description']} | channel: {row['channel']}")
    return "\n".join(lines)


def enrich_apollo_channel_context(
    text: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    structured_context = structure_apollo_channel_context(text, metadata)
    if not structured_context or structured_context in text:
        return text
    return f"{text}\n\n{structured_context}"
