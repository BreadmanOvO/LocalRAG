from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings as config


@dataclass(frozen=True)
class ChunkRecord:
    text: str
    metadata: dict[str, Any]


def build_locator(page_start: int | None, section_path: str | None) -> str | None:
    if page_start is not None and section_path:
        return f"p.{page_start} | § {section_path}"
    if page_start is not None:
        return f"p.{page_start}"
    if section_path:
        return f"§ {section_path}"
    return None


def extract_page_aware_segments(
    text: str, *, split_on_page: bool = True, split_on_heading: bool = True
) -> list[dict[str, Any]]:
    heading_stack: list[str] = []
    segments: list[dict[str, Any]] = []
    current_lines: list[str] = []
    current_page_start: int | None = None
    current_page_end: int | None = None

    def flush_current() -> None:
        nonlocal current_page_start, current_page_end
        if not current_lines:
            return
        content = "\n".join(current_lines).strip()
        if not content:
            return
        segments.append(
            {
                "text": content,
                "page_start": current_page_start,
                "page_end": current_page_end,
                "section_path": " > ".join(heading_stack) if heading_stack else None,
            }
        )
        current_page_start = None
        current_page_end = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if split_on_heading:
                flush_current()
                current_lines = []
            level = len(line) - len(line.lstrip("#"))
            heading = line[level:].strip()
            if heading:
                heading_stack = heading_stack[: max(level - 1, 0)]
                heading_stack.append(heading)
            continue

        page_match = re.match(r"^\[p\.(\d+)\]\s*(.*)$", line)
        if page_match:
            page_number = int(page_match.group(1))
            if split_on_page:
                flush_current()
                current_lines = []
                current_page_start = page_number
            elif current_page_start is None:
                current_page_start = page_number
            current_page_end = page_number
            remainder = page_match.group(2).strip()
            if remainder:
                current_lines.append(remainder)
            continue

        current_lines.append(line)

    flush_current()
    return segments or [
        {
            "text": text,
            "page_start": None,
            "page_end": None,
            "section_path": None,
        }
    ]


def build_baseline_splitter(
    *, chunk_size: int | None = None, chunk_overlap: int | None = None, separators: list[str] | None = None
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or config.chunk_size,
        chunk_overlap=chunk_overlap or config.chunk_overlap,
        separators=separators or config.separators,
        length_function=len,
    )


def build_doc_type_splitter(doc_type: str) -> RecursiveCharacterTextSplitter:
    config_map = getattr(config, "doc_type_chunking", {})
    settings = config_map.get(doc_type) or {"chunk_size": config.chunk_size, "chunk_overlap": config.chunk_overlap}
    return build_baseline_splitter(
        chunk_size=settings["chunk_size"],
        chunk_overlap=settings["chunk_overlap"],
    )


def choose_chunking_strategy(doc_type: str, requested_strategy: str | None) -> str:
    if requested_strategy != "doc_type_aware":
        return "baseline"
    if doc_type in {"official_doc", "standard", "paper", "report"}:
        return "doc_type_aware"
    return "baseline"


def build_chunk_metadata(
    *,
    source_metadata: dict[str, Any],
    chunk_order: int,
    chunk_strategy: str,
    page_start: int | None = None,
    page_end: int | None = None,
    section_path: str | None = None,
) -> dict[str, Any]:
    metadata = {
        **source_metadata,
        "chunk_order": chunk_order,
        "chunk_strategy": chunk_strategy,
    }
    locator = build_locator(page_start=page_start, section_path=section_path)
    if page_start is not None:
        metadata["page_start"] = page_start
    if page_end is not None:
        metadata["page_end"] = page_end
    if section_path:
        metadata["section_path"] = section_path
    if locator:
        metadata["locator"] = locator
    return metadata


def chunk_text_baseline(text: str, *, source_metadata: dict[str, Any]) -> list[ChunkRecord]:
    splitter = build_baseline_splitter()
    min_split_length = getattr(config, "min_split_length", 0)
    parts = splitter.split_text(text) if len(text) > min_split_length else [text]
    return [
        ChunkRecord(
            text=part,
            metadata=build_chunk_metadata(
                source_metadata=source_metadata,
                chunk_order=index,
                chunk_strategy="baseline",
            ),
        )
        for index, part in enumerate(parts)
    ]


def chunk_text_doc_type_aware(text: str, *, source_metadata: dict[str, Any]) -> list[ChunkRecord]:
    doc_type = source_metadata["doc_type"]
    split_on_page = doc_type == "official_doc"
    split_on_heading = doc_type == "official_doc"
    segments = extract_page_aware_segments(
        text,
        split_on_page=split_on_page,
        split_on_heading=split_on_heading,
    )
    records: list[ChunkRecord] = []
    chunk_order = 0
    min_split_length = getattr(config, "min_split_length", 0)
    splitter = build_doc_type_splitter(doc_type)

    for segment in segments:
        segment_text = segment["text"]
        parts = splitter.split_text(segment_text) if len(segment_text) > min_split_length else [segment_text]
        for part in parts:
            records.append(
                ChunkRecord(
                    text=part,
                    metadata=build_chunk_metadata(
                        source_metadata=source_metadata,
                        chunk_order=chunk_order,
                        chunk_strategy="doc_type_aware",
                        page_start=segment["page_start"],
                        page_end=segment["page_end"],
                        section_path=segment["section_path"],
                    ),
                )
            )
            chunk_order += 1
    return records
