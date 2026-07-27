from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from langchain_core.messages.utils import count_tokens_approximately

from .models import CompressionDecision, CompressionPolicy


def count_message_tokens(
    messages: Iterable[Any],
    *,
    tools: Iterable[Any] | None = None,
) -> int:
    token_count = count_tokens_approximately(
        messages,
        chars_per_token=2.0,
        tools=list(tools or ()),
        use_usage_metadata_scaling=True,
    )
    if token_count < 0:
        raise ValueError("token count must be at least 0")
    return int(token_count)


def decide_compression(
    message_tokens: int,
    policy: CompressionPolicy,
) -> CompressionDecision:
    if type(message_tokens) is not int:
        raise TypeError("message_tokens must be an int")
    if message_tokens < 0:
        raise ValueError("message_tokens must be at least 0")

    available_message_tokens = (
        policy.context_limit
        - policy.fixed_overhead_tokens
        - policy.output_reserve_tokens
    )
    if available_message_tokens <= 0:
        raise ValueError("available message budget must be greater than 0")

    trigger_message_tokens = int(available_message_tokens * policy.trigger_ratio)
    target_message_tokens = int(available_message_tokens * policy.target_ratio)
    hard_message_tokens = int(available_message_tokens * policy.hard_limit_ratio)
    return CompressionDecision(
        should_compress=message_tokens >= trigger_message_tokens,
        available_message_tokens=available_message_tokens,
        trigger_message_tokens=trigger_message_tokens,
        target_message_tokens=target_message_tokens,
        hard_message_tokens=hard_message_tokens,
    )
