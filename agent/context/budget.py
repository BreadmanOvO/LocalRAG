from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
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


def _tool_call_ids(message: BaseMessage) -> set[str]:
    if not isinstance(message, AIMessage):
        return set()
    return {
        str(tool_call["id"])
        for tool_call in message.tool_calls
        if tool_call.get("id") is not None
    }


def _safe_tool_boundary(messages: list[BaseMessage], boundary: int) -> int:
    tool_indexes: dict[str, list[int]] = {}
    for index, message in enumerate(messages):
        if isinstance(message, ToolMessage):
            tool_indexes.setdefault(str(message.tool_call_id), []).append(index)

    tool_groups = []
    for ai_index, message in enumerate(messages):
        matching_tool_indexes = [
            tool_index
            for call_id in _tool_call_ids(message)
            for tool_index in tool_indexes.get(call_id, ())
        ]
        if matching_tool_indexes:
            tool_groups.append((ai_index, matching_tool_indexes))

    while boundary:
        split_ai_index = next(
            (
                ai_index
                for ai_index, matching_tool_indexes in tool_groups
                if any(
                    (ai_index < boundary) != (tool_index < boundary)
                    for tool_index in matching_tool_indexes
                )
            ),
            None,
        )

        if split_ai_index is None:
            return boundary

        turn_start = next(
            (
                index
                for index in range(split_ai_index, -1, -1)
                if isinstance(messages[index], HumanMessage)
            ),
            0,
        )
        boundary = turn_start if turn_start < boundary else 0

    return 0


def partition_messages(
    messages: Iterable[BaseMessage],
    *,
    recent_turns: int,
    target_tokens: int,
) -> tuple[tuple[BaseMessage, ...], tuple[BaseMessage, ...]]:
    if type(recent_turns) is not int:
        raise TypeError("recent_turns must be an int")
    if recent_turns <= 0:
        raise ValueError("recent_turns must be greater than 0")
    if type(target_tokens) is not int:
        raise TypeError("target_tokens must be an int")
    if target_tokens < 0:
        raise ValueError("target_tokens must be at least 0")

    if isinstance(messages, (str, bytes)):
        raise TypeError("messages must be an iterable of BaseMessage")
    materialized = list(messages)
    if not all(isinstance(message, BaseMessage) for message in materialized):
        raise TypeError("messages must contain only BaseMessage values")
    if not materialized:
        return (), ()

    human_starts = [
        index
        for index, message in enumerate(materialized)
        if isinstance(message, HumanMessage)
    ]
    if not human_starts:
        return (), tuple(materialized)

    complete_starts = human_starts
    if isinstance(materialized[-1], HumanMessage):
        complete_starts = human_starts[:-1]
    if len(complete_starts) <= recent_turns:
        return (), tuple(materialized)

    boundary = _safe_tool_boundary(
        materialized,
        complete_starts[-recent_turns],
    )

    while boundary:
        preceding_starts = [start for start in complete_starts if start < boundary]
        if len(preceding_starts) <= 1:
            break
        candidate_boundary = _safe_tool_boundary(materialized, preceding_starts[-1])
        if not any(start < candidate_boundary for start in complete_starts):
            break
        if count_message_tokens(materialized[candidate_boundary:]) > target_tokens:
            break
        boundary = candidate_boundary

    return tuple(materialized[:boundary]), tuple(materialized[boundary:])


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
