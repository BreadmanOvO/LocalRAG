"""Budgeted context views for room memory and Agent handoffs.

Raw transcripts and step outputs stay in durable storage for audit. Model
prompts receive only the explicit, bounded views produced by this module.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Any, Iterable, Sequence

from langchain_core.messages import HumanMessage

from agent.context.budget import count_message_tokens


HANDOFF_MAX_TOKENS = 1200
ROOM_MEMORY_MAX_TOKENS = 2400
RECENT_MEMORY_ITEMS = 6
_SOURCE_RE = re.compile(r"(?:source|paper|asset|artifact|event|文献|来源)[-_:#\s]*[A-Za-z0-9._-]+", re.I)
_URL_RE = re.compile(r"https?://[^\s)\]>]+")


def _clean(value: object) -> str:
    return " ".join(str(value or "").strip().split())


def _unique(values: Iterable[str], limit: int = 12) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = _clean(raw)
        key = value.casefold()
        if value and key not in seen:
            seen.add(key)
            result.append(value)
        if len(result) >= limit:
            break
    return tuple(result)


def _token_count(text: str) -> int:
    return count_message_tokens((HumanMessage(content=text),)) if text else 0


def _bounded_lines(text: str, max_tokens: int) -> tuple[str, bool]:
    normalized = str(text or "").strip()
    if _token_count(normalized) <= max_tokens:
        return normalized, False
    lines = [_clean(line.lstrip("-*# ")) for line in normalized.splitlines() if _clean(line.lstrip("-*# "))]
    selected: list[str] = []
    for line in lines:
        candidate = "\n".join((*selected, line))
        if _token_count(candidate) > max_tokens:
            break
        selected.append(line)
    if not selected:
        # Token estimation is conservative for CJK; this remains an emergency
        # bound and never substitutes raw text from another source.
        return normalized[: max(200, max_tokens * 2)].rstrip(), True
    return "\n".join(selected), True


def _section_lines(text: str, keywords: Sequence[str]) -> tuple[str, ...]:
    result = []
    for line in str(text or "").splitlines():
        clean = _clean(line.lstrip("-*# "))
        if clean and any(keyword in clean.casefold() for keyword in keywords):
            result.append(clean)
    return _unique(result, limit=8)


@dataclass(frozen=True)
class HandoffPacket:
    schema_version: str
    source_sequence: int
    source_agent_id: str
    target_agent_id: str
    task: str
    summary: str
    decisions: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    open_questions: tuple[str, ...]
    artifact_refs: tuple[str, ...]
    source_tokens: int
    delivered_tokens: int
    compressed: bool

    def public(self) -> dict[str, Any]:
        return asdict(self)

    def render(self) -> str:
        sections = [f"来自 @{self.source_agent_id} 的交接摘要：\n{self.summary}"]
        if self.decisions:
            sections.append("已确认决策：\n- " + "\n- ".join(self.decisions))
        if self.evidence_refs:
            sections.append("证据引用：\n- " + "\n- ".join(self.evidence_refs))
        if self.open_questions:
            sections.append("待解决：\n- " + "\n- ".join(self.open_questions))
        if self.artifact_refs:
            sections.append("产物引用：\n- " + "\n- ".join(self.artifact_refs))
        return "\n\n".join(sections)


def build_handoff_packet(source: Any, *, target_agent_id: str, task: str) -> HandoffPacket:
    """Convert one completed step into a bounded, provenance-rich handoff."""
    content = str(getattr(source, "content", "") or "")
    source_tokens = _token_count(content)
    decisions = _section_lines(content, ("结论", "决定", "建议", "decision", "recommend"))
    open_questions = _section_lines(content, ("待办", "缺口", "未解决", "风险", "todo", "open question", "risk"))
    references = _unique((*_SOURCE_RE.findall(content), *_URL_RE.findall(content)), limit=16)
    artifact_refs = tuple(item for item in references if item.casefold().startswith(("asset", "artifact")))
    evidence_refs = tuple(item for item in references if item not in artifact_refs)
    summary, compressed = _bounded_lines(content, HANDOFF_MAX_TOKENS)
    if not summary:
        summary = "上游步骤完成，但没有可传递的文本结论。"
    packet = HandoffPacket(
        schema_version="handoff-packet-v1",
        source_sequence=int(getattr(source, "sequence", 0)),
        source_agent_id=str(getattr(source, "agent_id", "unknown")),
        target_agent_id=target_agent_id,
        task=_clean(task),
        summary=summary,
        decisions=decisions,
        evidence_refs=evidence_refs,
        open_questions=open_questions,
        artifact_refs=artifact_refs,
        source_tokens=source_tokens,
        delivered_tokens=0,
        compressed=compressed,
    )
    delivered = _token_count(packet.render())
    return HandoffPacket(**{**packet.public(), "delivered_tokens": delivered})


@dataclass(frozen=True)
class RoomMemoryView:
    text: str
    message_refs: tuple[str, ...]
    tokens_before: int
    tokens_after: int
    compressed: bool

    def public(self) -> dict[str, Any]:
        return asdict(self)


def prepare_room_memory(messages: Sequence[Any], *, exclude_message_id: str = "") -> RoomMemoryView:
    """Build a bounded room-level view without exposing the full transcript."""
    eligible = [message for message in messages if getattr(message, "message_id", "") != exclude_message_id]
    raw = "\n".join(f"{getattr(item, 'role', 'unknown')}: {getattr(item, 'content', '')}" for item in eligible)
    before = _token_count(raw)
    if before <= ROOM_MEMORY_MAX_TOKENS:
        return RoomMemoryView(raw, tuple(getattr(item, "message_id", "") for item in eligible), before, before, False)

    older = eligible[:-RECENT_MEMORY_ITEMS]
    recent = eligible[-RECENT_MEMORY_ITEMS:]
    older_summary: list[tuple[str, str]] = []
    for item in older[-8:]:
        content = _clean(getattr(item, "content", ""))
        if content:
            message_id = str(getattr(item, "message_id", ""))
            snippet, _ = _bounded_lines(
                f"- {getattr(item, 'role', 'unknown')} [{message_id}]: {content}",
                90,
            )
            older_summary.append((message_id, snippet))
    recent_summary: list[tuple[str, str]] = []
    for item in recent:
        message_id = str(getattr(item, "message_id", ""))
        snippet, _ = _bounded_lines(
            f"{getattr(item, 'role', 'unknown')} [{message_id}]: {getattr(item, 'content', '')}",
            260,
        )
        recent_summary.append((message_id, snippet))
    # Recent turns come first so an emergency final bound cannot discard the
    # user's latest constraints in favor of older background.
    view = "最近消息：\n" + "\n".join(value for _, value in recent_summary)
    if older_summary:
        view += "\n\n较早消息摘要：\n" + "\n".join(value for _, value in older_summary)
    bounded, _ = _bounded_lines(view, ROOM_MEMORY_MAX_TOKENS)
    referenced = tuple(message_id for message_id, snippet in (*recent_summary, *older_summary) if message_id and message_id in bounded)
    return RoomMemoryView(
        bounded,
        referenced,
        before,
        _token_count(bounded),
        True,
    )
