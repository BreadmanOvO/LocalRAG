from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeVar


T = TypeVar("T")


def _normalize_sequence(
    value: object,
    *,
    field_name: str,
    item_type: type[T],
) -> tuple[T, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise TypeError(f"{field_name} must be a sequence")
    if not all(isinstance(item, item_type) for item in value):
        raise TypeError(
            f"{field_name} must contain only {item_type.__name__} values"
        )
    if isinstance(value, tuple):
        return value
    return tuple(value)


@dataclass(frozen=True)
class SummaryFinding:
    claim: str
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.claim, str):
            raise TypeError("claim must be a str")
        object.__setattr__(
            self,
            "evidence_ids",
            _normalize_sequence(
                self.evidence_ids,
                field_name="evidence_ids",
                item_type=str,
            ),
        )


@dataclass(frozen=True)
class ConversationSummary:
    goal: str
    user_constraints: tuple[str, ...] = ()
    confirmed_findings: tuple[SummaryFinding, ...] = ()
    decisions: tuple[str, ...] = ()
    unresolved_questions: tuple[str, ...] = ()
    failed_attempts: tuple[str, ...] = ()
    referenced_source_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.goal, str):
            raise TypeError("goal must be a str")

        for field_name in (
            "user_constraints",
            "decisions",
            "unresolved_questions",
            "failed_attempts",
            "referenced_source_ids",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalize_sequence(
                    getattr(self, field_name),
                    field_name=field_name,
                    item_type=str,
                ),
            )
        object.__setattr__(
            self,
            "confirmed_findings",
            _normalize_sequence(
                self.confirmed_findings,
                field_name="confirmed_findings",
                item_type=SummaryFinding,
            ),
        )


@dataclass(frozen=True)
class CompressionPolicy:
    context_limit: int = 40960
    fixed_overhead_tokens: int = 4096
    output_reserve_tokens: int = 1024
    trigger_ratio: float = 0.70
    target_ratio: float = 0.45
    hard_limit_ratio: float = 0.90
    recent_turns: int = 4

    def __post_init__(self) -> None:
        for field_name in (
            "context_limit",
            "fixed_overhead_tokens",
            "output_reserve_tokens",
            "recent_turns",
        ):
            if type(getattr(self, field_name)) is not int:
                raise TypeError(f"{field_name} must be an int")

        if self.context_limit <= 0:
            raise ValueError("context_limit must be greater than 0")
        if self.fixed_overhead_tokens < 0:
            raise ValueError("fixed_overhead_tokens must be at least 0")
        if self.output_reserve_tokens < 0:
            raise ValueError("output_reserve_tokens must be at least 0")
        if self.recent_turns <= 0:
            raise ValueError("recent_turns must be greater than 0")
        if not (
            0
            < self.target_ratio
            < self.trigger_ratio
            < self.hard_limit_ratio
            < 1
        ):
            raise ValueError(
                "ratios must satisfy "
                "0 < target_ratio < trigger_ratio < hard_limit_ratio < 1"
            )


@dataclass(frozen=True)
class CompressionDecision:
    should_compress: bool
    available_message_tokens: int
    trigger_message_tokens: int
    target_message_tokens: int
    hard_message_tokens: int


class ConversationCompressionError(RuntimeError):
    error_code = "conversation_compression_failed"
