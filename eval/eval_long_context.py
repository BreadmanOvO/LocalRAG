from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from pathlib import Path
import statistics
import subprocess
import sys
from typing import Any, cast
from uuid import uuid4

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.context.budget import count_message_tokens


CONTRACT_VERSION = "long-context-eval-v1"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = Path("data/evaluation/agent/long_context_eval_set.json")
DEFAULT_OUT_DIR = Path("results/v1_6_long_context")
EXPECTED_CASE_IDS = (
    "constraint-retention-001",
    "evidence-retention-001",
    "unresolved-question-001",
    "failed-tool-001",
    "tool-pair-boundary-001",
    "rolling-summary-001",
    "session-resume-001",
    "revision-conflict-001",
    "local-summary-fallback-001",
    "dual-summary-failure-001",
)
_DATASET_FIELDS = frozenset({"contract_version", "cases"})
_CASE_FIELDS = frozenset(
    {
        "id",
        "description",
        "fixture",
        "answer_contract",
        "required_constraints",
        "required_findings",
        "required_evidence_ids",
        "required_source_ids",
        "required_recent_message_ids",
        "expected_compression_count",
        "expected_error_code",
    }
)
_LIST_FIELDS = (
    "required_constraints",
    "required_findings",
    "required_evidence_ids",
    "required_source_ids",
    "required_recent_message_ids",
)
_FIXTURE_FIELDS = frozenset(
    {
        "messages",
        "previous_summary",
        "expected_observations",
        "expected_summary",
    }
)
_EXPECTED_SUMMARY_FIELDS = frozenset(
    {"unresolved_questions", "failed_attempts"}
)
_OBSERVATION_FIELDS = frozenset(
    {
        "failed_tool_call_ids",
        "tool_pair_call_ids",
        "compression_round_count",
        "resumed_revision",
        "revision_conflict_count",
        "local_summary_status",
        "fallback_summary_status",
    }
)
_ANSWER_CONTRACT_FIELDS = frozenset(
    {"required_terms", "forbidden_terms", "min_chars", "required_source_ids"}
)
_SUMMARY_FIELDS = frozenset(
    {
        "goal",
        "user_constraints",
        "confirmed_findings",
        "decisions",
        "unresolved_questions",
        "failed_attempts",
        "referenced_source_ids",
    }
)
_MESSAGE_COMMON_FIELDS = frozenset(
    {"id", "role", "content", "evidence_ids", "source_ids"}
)
_PASS_FIELDS = (
    "compression_trigger_pass",
    "compression_count_pass",
    "constraint_retention_pass",
    "finding_retention_pass",
    "identifier_retention_pass",
    "recent_message_retention_pass",
    "audit_integrity_pass",
    "summary_state_pass",
    "scenario_contract_pass",
    "compressed_view_pass",
    "token_reduction_pass",
    "answer_contract_pass",
    "error_contract_pass",
)
_SUMMARY_STATUSES = frozenset({"success", "failed", "not_used"})
_EXECUTION_EVENT_FIELDS = {
    "session_resumed": frozenset({"type", "revision"}),
    "revision_conflict": frozenset(
        {"type", "round", "expected_revision", "actual_revision"}
    ),
    "tool_call": frozenset({"type", "call_id"}),
    "tool_result": frozenset({"type", "call_id", "status"}),
    "summary_attempt": frozenset({"type", "round", "provider", "status"}),
    "compression_committed": frozenset({"type", "round"}),
}
_TEXT_IDENTIFIER_PATTERN = re.compile(
    r"(?<![\w-])(?:evidence|source)-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)+(?![\w-])",
    re.IGNORECASE,
)


def _non_empty_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value.strip()


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    result = [
        _non_empty_string(item, f"{field_name}[{index}]")
        for index, item in enumerate(value)
    ]
    if len(set(result)) != len(result):
        raise ValueError(f"{field_name} must not contain duplicates")
    return result


def _non_negative_int(value: Any, field_name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer")
    return value


def _positive_int(value: Any, field_name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


def _exact_dict(value: Any, fields: frozenset[str], field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{field_name} must contain the exact {field_name} contract")
    return value


def _normalize_summary(value: Any, field_name: str) -> dict[str, Any]:
    summary = _exact_dict(value, _SUMMARY_FIELDS, field_name)
    findings = summary["confirmed_findings"]
    if not isinstance(findings, list):
        raise ValueError(f"{field_name}.confirmed_findings must be a list")
    normalized_findings: list[dict[str, Any]] = []
    for index, finding in enumerate(findings):
        item_name = f"{field_name}.confirmed_findings[{index}]"
        finding_dict = _exact_dict(
            finding, frozenset({"claim", "evidence_ids"}), item_name
        )
        normalized_findings.append(
            {
                "claim": _non_empty_string(finding_dict["claim"], f"{item_name}.claim"),
                "evidence_ids": _string_list(
                    finding_dict["evidence_ids"], f"{item_name}.evidence_ids"
                ),
            }
        )
    return {
        "goal": _non_empty_string(summary["goal"], f"{field_name}.goal"),
        "user_constraints": _string_list(
            summary["user_constraints"], f"{field_name}.user_constraints"
        ),
        "confirmed_findings": normalized_findings,
        "decisions": _string_list(summary["decisions"], f"{field_name}.decisions"),
        "unresolved_questions": _string_list(
            summary["unresolved_questions"],
            f"{field_name}.unresolved_questions",
        ),
        "failed_attempts": _string_list(
            summary["failed_attempts"], f"{field_name}.failed_attempts"
        ),
        "referenced_source_ids": _string_list(
            summary["referenced_source_ids"],
            f"{field_name}.referenced_source_ids",
        ),
    }


def _normalize_message(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    role = value.get("role")
    expected_fields = _MESSAGE_COMMON_FIELDS
    if role == "assistant" and "tool_calls" in value:
        expected_fields |= frozenset({"tool_calls"})
    elif role == "tool":
        expected_fields |= frozenset({"tool_call_id", "tool_status"})
    if set(value) != expected_fields:
        raise ValueError(f"{field_name} must contain the exact message contract")
    if role not in {"system", "human", "assistant", "tool"}:
        raise ValueError(f"{field_name}.role is invalid")

    normalized: dict[str, Any] = {
        "id": _non_empty_string(value["id"], f"{field_name}.id"),
        "role": role,
        "content": _non_empty_string(value["content"], f"{field_name}.content"),
        "evidence_ids": _string_list(
            value["evidence_ids"], f"{field_name}.evidence_ids"
        ),
        "source_ids": _string_list(value["source_ids"], f"{field_name}.source_ids"),
    }
    if role == "assistant" and "tool_calls" in value:
        tool_calls = value["tool_calls"]
        if not isinstance(tool_calls, list) or not tool_calls:
            raise ValueError(f"{field_name}.tool_calls must be a non-empty list")
        normalized_calls: list[dict[str, Any]] = []
        for index, call in enumerate(tool_calls):
            call_name = f"{field_name}.tool_calls[{index}]"
            call_dict = _exact_dict(
                call, frozenset({"id", "name", "args"}), call_name
            )
            if not isinstance(call_dict["args"], dict):
                raise ValueError(f"{call_name}.args must be an object")
            normalized_calls.append(
                {
                    "id": _non_empty_string(call_dict["id"], f"{call_name}.id"),
                    "name": _non_empty_string(call_dict["name"], f"{call_name}.name"),
                    "args": copy.deepcopy(call_dict["args"]),
                }
            )
        normalized["tool_calls"] = normalized_calls
    if role == "tool":
        normalized["tool_call_id"] = _non_empty_string(
            value["tool_call_id"], f"{field_name}.tool_call_id"
        )
        status = value["tool_status"]
        if status not in {"succeeded", "failed"}:
            raise ValueError(f"{field_name}.tool_status is invalid")
        normalized["tool_status"] = status
    return normalized


def _normalize_messages(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    messages = [
        _normalize_message(message, f"{field_name}[{index}]")
        for index, message in enumerate(value)
    ]
    message_ids = [message["id"] for message in messages]
    if len(set(message_ids)) != len(message_ids):
        raise ValueError(f"{field_name} message IDs must be unique")
    return messages


def _normalize_observations(value: Any, field_name: str) -> dict[str, Any]:
    observations = _exact_dict(value, _OBSERVATION_FIELDS, field_name)
    local_status = observations["local_summary_status"]
    fallback_status = observations["fallback_summary_status"]
    if local_status not in _SUMMARY_STATUSES - {"not_used"}:
        raise ValueError(f"{field_name}.local_summary_status is invalid")
    if fallback_status not in _SUMMARY_STATUSES:
        raise ValueError(f"{field_name}.fallback_summary_status is invalid")
    return {
        "failed_tool_call_ids": _string_list(
            observations["failed_tool_call_ids"],
            f"{field_name}.failed_tool_call_ids",
        ),
        "tool_pair_call_ids": _string_list(
            observations["tool_pair_call_ids"],
            f"{field_name}.tool_pair_call_ids",
        ),
        "compression_round_count": _non_negative_int(
            observations["compression_round_count"],
            f"{field_name}.compression_round_count",
        ),
        "resumed_revision": _non_negative_int(
            observations["resumed_revision"], f"{field_name}.resumed_revision"
        ),
        "revision_conflict_count": _non_negative_int(
            observations["revision_conflict_count"],
            f"{field_name}.revision_conflict_count",
        ),
        "local_summary_status": local_status,
        "fallback_summary_status": fallback_status,
    }


def _normalize_answer_contract(value: Any, field_name: str) -> dict[str, Any]:
    contract = _exact_dict(value, _ANSWER_CONTRACT_FIELDS, field_name)
    min_chars = contract["min_chars"]
    if type(min_chars) is not int or min_chars <= 0:
        raise ValueError(f"{field_name}.min_chars must be a positive integer")
    required_terms = _string_list(
        contract["required_terms"], f"{field_name}.required_terms"
    )
    if not required_terms:
        raise ValueError(f"{field_name}.required_terms must not be empty")
    return {
        "required_terms": required_terms,
        "forbidden_terms": _string_list(
            contract["forbidden_terms"], f"{field_name}.forbidden_terms"
        ),
        "min_chars": min_chars,
        "required_source_ids": _string_list(
            contract["required_source_ids"],
            f"{field_name}.required_source_ids",
        ),
    }


def _normalize_expected_summary(value: Any, field_name: str) -> dict[str, Any]:
    expected = _exact_dict(value, _EXPECTED_SUMMARY_FIELDS, field_name)
    return {
        "unresolved_questions": _string_list(
            expected["unresolved_questions"],
            f"{field_name}.unresolved_questions",
        ),
        "failed_attempts": _string_list(
            expected["failed_attempts"],
            f"{field_name}.failed_attempts",
        ),
    }


def _collect_message_ids(
    messages: Sequence[Mapping[str, Any]], field_name: str
) -> set[str]:
    values: set[str] = set()
    singular_name = field_name.removesuffix("s")
    for message in messages:
        for key in (field_name, singular_name):
            value = message.get(key)
            if isinstance(value, str) and value.strip():
                values.add(value.strip())
            elif isinstance(value, list):
                values.update(
                    item.strip()
                    for item in value
                    if isinstance(item, str) and item.strip()
                )
    return values


def _collect_structured_ids(
    value: Any,
    *,
    singular_field: str,
    plural_field: str,
) -> set[str]:
    values: set[str] = set()
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key == singular_field and isinstance(item, str) and item.strip():
                values.add(item.strip())
            elif key == plural_field and isinstance(item, list):
                values.update(
                    identifier.strip()
                    for identifier in item
                    if isinstance(identifier, str) and identifier.strip()
                )
            values.update(
                _collect_structured_ids(
                    item,
                    singular_field=singular_field,
                    plural_field=plural_field,
                )
            )
    elif isinstance(value, list):
        for item in value:
            values.update(
                _collect_structured_ids(
                    item,
                    singular_field=singular_field,
                    plural_field=plural_field,
                )
            )
    return values


def _collect_text_identifiers(value: Any) -> set[str]:
    if isinstance(value, str):
        return set(_TEXT_IDENTIFIER_PATTERN.findall(value))
    if isinstance(value, Mapping):
        result: set[str] = set()
        for item in value.values():
            result.update(_collect_text_identifiers(item))
        return result
    if isinstance(value, list):
        result = set()
        for item in value:
            result.update(_collect_text_identifiers(item))
        return result
    return set()


def _validate_fixture_consistency(
    case: Mapping[str, Any], field_name: str
) -> None:
    fixture = cast(Mapping[str, Any], case["fixture"])
    messages = cast(list[dict[str, Any]], fixture["messages"])
    observations = cast(Mapping[str, Any], fixture["expected_observations"])
    message_ids = [message["id"] for message in messages]
    recent_ids = cast(list[str], case["required_recent_message_ids"])
    if message_ids[-len(recent_ids) :] != recent_ids:
        raise ValueError(f"{field_name} recent messages must be the frozen transcript tail")

    calls: dict[str, Mapping[str, Any]] = {}
    results: dict[str, Mapping[str, Any]] = {}
    for message in messages:
        for call in message.get("tool_calls", ()):
            call_id = str(call["id"])
            if call_id in calls:
                raise ValueError(f"{field_name} tool call IDs must be unique")
            calls[call_id] = call
        if message["role"] == "tool":
            call_id = str(message["tool_call_id"])
            if call_id in results:
                raise ValueError(f"{field_name} tool result IDs must be unique")
            results[call_id] = message
    if set(calls) != set(results):
        raise ValueError(f"{field_name} must contain complete tool call/result pairs")
    if set(observations["tool_pair_call_ids"]) != set(calls):
        raise ValueError(f"{field_name} tool_pair_call_ids must match frozen messages")
    failed_ids = {
        call_id
        for call_id, result in results.items()
        if result.get("tool_status") == "failed"
    }
    if set(observations["failed_tool_call_ids"]) != failed_ids:
        raise ValueError(f"{field_name} failed_tool_call_ids must match failed results")

    if observations["compression_round_count"] != case["expected_compression_count"]:
        raise ValueError(f"{field_name} compression round count is inconsistent")
    previous = fixture["previous_summary"]
    previous_revision = previous["revision"] if previous is not None else 0
    if observations["resumed_revision"] != previous_revision:
        raise ValueError(f"{field_name} resumed revision is inconsistent")
    local_status = observations["local_summary_status"]
    fallback_status = observations["fallback_summary_status"]
    if local_status == "success" and fallback_status != "not_used":
        raise ValueError(f"{field_name} successful local summary cannot use fallback")
    if local_status == "failed" and fallback_status == "not_used":
        raise ValueError(f"{field_name} failed local summary must exercise fallback")
    if fallback_status == "failed" and (
        case["expected_error_code"] != "conversation_compression_failed"
        or case["expected_compression_count"] != 0
    ):
        raise ValueError(f"{field_name} dual summary failure must fail closed")

    allowed_evidence_ids = _collect_message_ids(messages, "evidence_ids")
    allowed_source_ids = _collect_message_ids(messages, "source_ids")
    if not set(case["required_evidence_ids"]).issubset(allowed_evidence_ids):
        raise ValueError(f"{field_name} required evidence IDs must exist in messages")
    if not set(case["required_source_ids"]).issubset(allowed_source_ids):
        raise ValueError(f"{field_name} required source IDs must exist in messages")
    if not set(case["answer_contract"]["required_source_ids"]).issubset(
        allowed_source_ids
    ):
        raise ValueError(f"{field_name} answer sources must exist in messages")


def validate_dataset(payload: Any) -> dict[str, Any]:
    dataset = _exact_dict(payload, _DATASET_FIELDS, "dataset")
    if dataset.get("contract_version") != CONTRACT_VERSION:
        raise ValueError(f"contract_version must be {CONTRACT_VERSION}")
    cases = dataset.get("cases")
    if not isinstance(cases, list):
        raise ValueError("cases must be a list")
    case_ids = [case.get("id") if isinstance(case, dict) else None for case in cases]
    if tuple(case_ids) != EXPECTED_CASE_IDS:
        raise ValueError("dataset must contain the exact ordered long-context case set")

    normalized_cases: list[dict[str, Any]] = []
    for index, case_value in enumerate(cases):
        field_name = f"cases[{index}]"
        case = _exact_dict(case_value, _CASE_FIELDS, field_name)
        normalized: dict[str, Any] = {
            "id": _non_empty_string(case["id"], f"{field_name}.id"),
            "description": _non_empty_string(
                case["description"], f"{field_name}.description"
            ),
        }
        for list_field in _LIST_FIELDS:
            normalized[list_field] = _string_list(
                case[list_field], f"{field_name}.{list_field}"
            )
        normalized["expected_compression_count"] = _non_negative_int(
            case["expected_compression_count"],
            f"{field_name}.expected_compression_count",
        )
        error_code = case["expected_error_code"]
        if not isinstance(error_code, str):
            raise ValueError(f"{field_name}.expected_error_code must be a string")
        normalized["expected_error_code"] = error_code.strip()
        normalized["answer_contract"] = _normalize_answer_contract(
            case["answer_contract"], f"{field_name}.answer_contract"
        )

        fixture = _exact_dict(case["fixture"], _FIXTURE_FIELDS, "fixture")
        previous_value = fixture["previous_summary"]
        previous: dict[str, Any] | None = None
        if previous_value is not None:
            previous_dict = _exact_dict(
                previous_value,
                frozenset({"revision", "summary"}),
                f"{field_name}.fixture.previous_summary",
            )
            revision = _non_negative_int(
                previous_dict["revision"],
                f"{field_name}.fixture.previous_summary.revision",
            )
            if revision == 0:
                raise ValueError(
                    f"{field_name}.fixture.previous_summary.revision must be positive"
                )
            previous = {
                "revision": revision,
                "summary": _normalize_summary(
                    previous_dict["summary"],
                    f"{field_name}.fixture.previous_summary.summary",
                ),
            }
        normalized["fixture"] = {
            "messages": _normalize_messages(
                fixture["messages"], f"{field_name}.fixture.messages"
            ),
            "previous_summary": previous,
            "expected_observations": _normalize_observations(
                fixture["expected_observations"],
                f"{field_name}.fixture.expected_observations",
            ),
            "expected_summary": _normalize_expected_summary(
                fixture["expected_summary"],
                f"{field_name}.fixture.expected_summary",
            ),
        }
        _validate_fixture_consistency(normalized, field_name)
        normalized_cases.append(normalized)
    return {"contract_version": CONTRACT_VERSION, "cases": normalized_cases}


def _messages(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [copy.deepcopy(item) for item in value if isinstance(item, dict)]


def _message_id(message: Mapping[str, Any]) -> str:
    value = message.get("id")
    return value if isinstance(value, str) and value.strip() else ""


def _message_map(
    messages: Sequence[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for message in messages:
        message_id = _message_id(message)
        if message_id and message_id not in result:
            result[message_id] = message
    return result


def _canonical_message(message: Mapping[str, Any]) -> str:
    return json.dumps(message, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _summary_fields(
    outcome: Mapping[str, Any],
) -> tuple[
    dict[str, Any] | None,
    list[str],
    list[dict[str, Any]],
    list[str],
    list[str],
    list[str],
]:
    summary = outcome.get("summary")
    if not isinstance(summary, Mapping):
        return None, [], [], [], [], []
    try:
        normalized = _normalize_summary(dict(summary), "outcome.summary")
    except ValueError:
        return None, [], [], [], [], []
    return (
        normalized,
        cast(list[str], normalized["user_constraints"]),
        cast(list[dict[str, Any]], normalized["confirmed_findings"]),
        cast(list[str], normalized["referenced_source_ids"]),
        cast(list[str], normalized["unresolved_questions"]),
        cast(list[str], normalized["failed_attempts"]),
    )


def _orphan_tool_message_ids(messages: Sequence[Mapping[str, Any]]) -> list[str]:
    calls: dict[str, list[tuple[int, str]]] = {}
    results: dict[str, list[tuple[int, str]]] = {}
    for index, message in enumerate(messages):
        tool_calls = message.get("tool_calls")
        if message.get("role") == "assistant" and isinstance(tool_calls, list):
            for call in tool_calls:
                if isinstance(call, Mapping) and isinstance(call.get("id"), str):
                    calls.setdefault(str(call["id"]), []).append(
                        (index, _message_id(message))
                    )
        tool_call_id = message.get("tool_call_id")
        if message.get("role") == "tool" and isinstance(tool_call_id, str):
            results.setdefault(tool_call_id, []).append((index, _message_id(message)))

    invalid_ids: set[str] = set()
    for call_id in set(calls) | set(results):
        call_entries = calls.get(call_id, [])
        result_entries = results.get(call_id, [])
        if len(call_entries) != 1 or len(result_entries) != 1:
            invalid_ids.update(message_id for _, message_id in call_entries)
            invalid_ids.update(message_id for _, message_id in result_entries)
            continue
        call_entry = call_entries[0]
        result_entry = result_entries[0]
        if call_entry[0] >= result_entry[0]:
            invalid_ids.update((call_entry[1], result_entry[1]))
    return sorted(identifier for identifier in invalid_ids if identifier)


def _to_base_message(message: Mapping[str, Any]) -> BaseMessage:
    role = message.get("role")
    content = message.get("content")
    message_id = message.get("id")
    if not isinstance(content, str) or not isinstance(message_id, str):
        raise ValueError("model message content and id must be strings")
    metadata: dict[str, Any] = {
        "evidence_ids": list(message.get("evidence_ids", ())),
        "source_ids": list(message.get("source_ids", ())),
    }
    if role == "system":
        return SystemMessage(content=content, id=message_id, additional_kwargs=metadata)
    if role == "human":
        return HumanMessage(content=content, id=message_id, additional_kwargs=metadata)
    if role == "assistant":
        tool_calls = message.get("tool_calls", [])
        if not isinstance(tool_calls, list):
            raise ValueError("assistant tool_calls must be a list")
        return AIMessage(
            content=content,
            id=message_id,
            additional_kwargs=metadata,
            tool_calls=copy.deepcopy(tool_calls),
        )
    if role == "tool":
        tool_call_id = message.get("tool_call_id")
        if not isinstance(tool_call_id, str):
            raise ValueError("tool_call_id must be a string")
        metadata["tool_status"] = message.get("tool_status")
        return ToolMessage(
            content=content,
            id=message_id,
            tool_call_id=tool_call_id,
            additional_kwargs=metadata,
        )
    raise ValueError("model message role is invalid")


def _message_tokens(messages: Sequence[Mapping[str, Any]]) -> int | None:
    try:
        converted = [_to_base_message(message) for message in messages]
        return count_message_tokens(converted)
    except (TypeError, ValueError):
        return None


def _answer_contract_pass(
    case: Mapping[str, Any], outcome: Mapping[str, Any]
) -> bool:
    contract = case.get("answer_contract")
    answer = outcome.get("answer")
    if not isinstance(contract, Mapping) or not isinstance(answer, str):
        return False
    folded_answer = answer.casefold()
    required_terms = contract.get("required_terms")
    forbidden_terms = contract.get("forbidden_terms")
    required_source_ids = contract.get("required_source_ids")
    min_chars = contract.get("min_chars")
    return (
        isinstance(required_terms, list)
        and isinstance(forbidden_terms, list)
        and isinstance(required_source_ids, list)
        and type(min_chars) is int
        and len(answer.strip()) >= min_chars
        and all(
            isinstance(term, str) and term.casefold() in folded_answer
            for term in required_terms
        )
        and all(
            isinstance(term, str) and term.casefold() not in folded_answer
            for term in forbidden_terms
        )
        and all(
            isinstance(source_id, str) and source_id.casefold() in folded_answer
            for source_id in required_source_ids
        )
    )


def _derive_execution_observations(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, list) or not value:
        return None

    events: list[dict[str, Any]] = []
    try:
        for index, raw_event in enumerate(value):
            field_name = f"outcome.execution_trace[{index}]"
            if not isinstance(raw_event, dict):
                return None
            event_type = raw_event.get("type")
            if event_type not in _EXECUTION_EVENT_FIELDS:
                return None
            event = _exact_dict(
                raw_event,
                _EXECUTION_EVENT_FIELDS[event_type],
                field_name,
            )
            normalized: dict[str, Any] = {"type": event_type}
            if event_type == "session_resumed":
                normalized["revision"] = _positive_int(
                    event["revision"], f"{field_name}.revision"
                )
            elif event_type == "revision_conflict":
                normalized["round"] = _positive_int(
                    event["round"], f"{field_name}.round"
                )
                normalized["expected_revision"] = _non_negative_int(
                    event["expected_revision"], f"{field_name}.expected_revision"
                )
                normalized["actual_revision"] = _non_negative_int(
                    event["actual_revision"], f"{field_name}.actual_revision"
                )
                if normalized["expected_revision"] >= normalized["actual_revision"]:
                    return None
            elif event_type == "tool_call":
                normalized["call_id"] = _non_empty_string(
                    event["call_id"], f"{field_name}.call_id"
                )
            elif event_type == "tool_result":
                normalized["call_id"] = _non_empty_string(
                    event["call_id"], f"{field_name}.call_id"
                )
                if event["status"] not in {"succeeded", "failed"}:
                    return None
                normalized["status"] = event["status"]
            elif event_type == "summary_attempt":
                normalized["round"] = _positive_int(
                    event["round"], f"{field_name}.round"
                )
                if event["provider"] not in {"local", "fallback"}:
                    return None
                if event["status"] not in {"success", "failed"}:
                    return None
                normalized["provider"] = event["provider"]
                normalized["status"] = event["status"]
            elif event_type == "compression_committed":
                normalized["round"] = _positive_int(
                    event["round"], f"{field_name}.round"
                )
            events.append(normalized)
    except (KeyError, ValueError):
        return None

    resume_events = [
        (index, event)
        for index, event in enumerate(events)
        if event["type"] == "session_resumed"
    ]
    if len(resume_events) > 1:
        return None
    resumed_revision = resume_events[0][1]["revision"] if resume_events else 0

    call_events: dict[str, tuple[int, dict[str, Any]]] = {}
    result_events: dict[str, tuple[int, dict[str, Any]]] = {}
    for index, event in enumerate(events):
        if event["type"] == "tool_call":
            if event["call_id"] in call_events:
                return None
            call_events[event["call_id"]] = (index, event)
        elif event["type"] == "tool_result":
            if event["call_id"] in result_events:
                return None
            result_events[event["call_id"]] = (index, event)
    if set(call_events) != set(result_events):
        return None
    ordered_call_ids = [
        call_id
        for call_id, _ in sorted(call_events.items(), key=lambda item: item[1][0])
    ]
    for call_id in ordered_call_ids:
        if call_events[call_id][0] >= result_events[call_id][0]:
            return None
    failed_call_ids = [
        call_id
        for call_id in ordered_call_ids
        if result_events[call_id][1]["status"] == "failed"
    ]

    attempts: dict[tuple[int, str], tuple[int, dict[str, Any]]] = {}
    commits: dict[int, int] = {}
    conflicts: list[tuple[int, dict[str, Any]]] = []
    for index, event in enumerate(events):
        if event["type"] == "summary_attempt":
            key = (event["round"], event["provider"])
            if key in attempts:
                return None
            attempts[key] = (index, event)
        elif event["type"] == "compression_committed":
            if event["round"] in commits:
                return None
            commits[event["round"]] = index
        elif event["type"] == "revision_conflict":
            conflicts.append((index, event))

    local_rounds = sorted(
        round_number
        for round_number, provider in attempts
        if provider == "local"
    )
    if not local_rounds or local_rounds != list(range(1, max(local_rounds) + 1)):
        return None
    if any(
        provider == "fallback" and round_number not in local_rounds
        for round_number, provider in attempts
    ):
        return None
    if resume_events and resume_events[0][0] >= attempts[(1, "local")][0]:
        return None
    if sorted(commits) not in ([], list(range(1, len(commits) + 1))):
        return None

    local_statuses: set[str] = set()
    fallback_statuses: set[str] = set()
    successful_attempt_indexes: dict[int, int] = {}
    for round_number in local_rounds:
        local_index, local_event = attempts[(round_number, "local")]
        local_status = str(local_event["status"])
        local_statuses.add(local_status)
        fallback = attempts.get((round_number, "fallback"))
        if local_status == "success":
            if fallback is not None:
                return None
            successful_index: int | None = local_index
        else:
            if fallback is None or fallback[0] <= local_index:
                return None
            fallback_status = str(fallback[1]["status"])
            fallback_statuses.add(fallback_status)
            successful_index = fallback[0] if fallback_status == "success" else None

        commit_index = commits.get(round_number)
        if successful_index is None:
            if commit_index is not None:
                return None
        elif commit_index is None or commit_index <= successful_index:
            return None
        if successful_index is not None:
            successful_attempt_indexes[round_number] = successful_index

    expected_conflict_revision = resumed_revision
    for conflict_index, conflict_event in conflicts:
        round_number = conflict_event["round"]
        if round_number not in local_rounds:
            return None
        successful_index = successful_attempt_indexes.get(round_number)
        commit_index = commits.get(round_number)
        if (
            successful_index is None
            or conflict_index <= successful_index
            or commit_index is None
            or conflict_index >= commit_index
            or conflict_event["expected_revision"] != expected_conflict_revision
        ):
            return None
        expected_conflict_revision = conflict_event["actual_revision"]
    if len(local_statuses) != 1 or len(fallback_statuses) > 1:
        return None
    return {
        "failed_tool_call_ids": failed_call_ids,
        "tool_pair_call_ids": ordered_call_ids,
        "compression_round_count": len(commits),
        "resumed_revision": resumed_revision,
        "revision_conflict_count": len(conflicts),
        "local_summary_status": next(iter(local_statuses)),
        "fallback_summary_status": (
            next(iter(fallback_statuses)) if fallback_statuses else "not_used"
        ),
    }


def _row_pass(row: Mapping[str, Any]) -> bool:
    return (
        all(row.get(field) is True for field in _PASS_FIELDS)
        and not row.get("fabricated_evidence_ids")
        and not row.get("fabricated_source_ids")
        and not row.get("orphan_tool_message_ids")
        and not row.get("runtime_error")
    )


def evaluate_case(case: Mapping[str, Any], outcome: Mapping[str, Any]) -> dict[str, Any]:
    case_id = str(case.get("id") or "") if isinstance(case, Mapping) else ""
    if not isinstance(outcome, Mapping):
        outcome = {}
    fixture = case.get("fixture")
    fixture_messages = (
        _messages(fixture.get("messages")) if isinstance(fixture, Mapping) else []
    )
    audit_messages = _messages(outcome.get("audit_messages"))
    model_messages = _messages(outcome.get("model_messages"))
    fixture_by_id = _message_map(fixture_messages)
    (
        normalized_summary,
        summary_constraints,
        summary_findings,
        summary_source_ids,
        summary_unresolved_questions,
        summary_failed_attempts,
    ) = _summary_fields(outcome)

    required_constraints = list(case.get("required_constraints", ()))
    required_findings = list(case.get("required_findings", ()))
    required_evidence_ids = set(case.get("required_evidence_ids", ()))
    required_source_ids = set(case.get("required_source_ids", ()))
    required_recent_ids = list(case.get("required_recent_message_ids", ()))
    expected_compression_count = case.get("expected_compression_count")
    expected_error_code = case.get("expected_error_code")
    expected_failure = bool(expected_error_code)
    expected_summary = (
        fixture.get("expected_summary") if isinstance(fixture, Mapping) else None
    )

    model_texts = {
        message["content"]
        for message in model_messages
        if isinstance(message.get("content"), str)
    }
    retained_texts = set(summary_constraints) | model_texts
    finding_claims = {
        finding["claim"]
        for finding in summary_findings
        if isinstance(finding.get("claim"), str)
    } | model_texts
    summary_evidence_ids = {
        evidence_id
        for finding in summary_findings
        for evidence_id in finding.get("evidence_ids", ())
        if isinstance(evidence_id, str)
    }

    allowed_evidence_ids = _collect_structured_ids(
        fixture_messages,
        singular_field="evidence_id",
        plural_field="evidence_ids",
    )
    allowed_source_ids = _collect_structured_ids(
        fixture_messages,
        singular_field="source_id",
        plural_field="source_ids",
    )
    model_evidence_ids = _collect_structured_ids(
        model_messages,
        singular_field="evidence_id",
        plural_field="evidence_ids",
    )
    model_source_ids = _collect_structured_ids(
        model_messages,
        singular_field="source_id",
        plural_field="source_ids",
    )
    output_text_identifiers = (
        _collect_text_identifiers(normalized_summary)
        | _collect_text_identifiers(model_messages)
        | _collect_text_identifiers(outcome.get("answer"))
    )
    output_text_identifiers.discard(case_id)
    output_text_evidence_ids = {
        identifier
        for identifier in output_text_identifiers
        if identifier.casefold().startswith("evidence-")
    }
    output_text_source_ids = output_text_identifiers - output_text_evidence_ids
    fabricated_evidence_ids = sorted(
        (summary_evidence_ids | model_evidence_ids | output_text_evidence_ids)
        - allowed_evidence_ids
    )
    fabricated_source_ids = sorted(
        (set(summary_source_ids) | model_source_ids | output_text_source_ids)
        - allowed_source_ids
    )
    orphan_ids = _orphan_tool_message_ids(model_messages)

    model_id_sequence = [_message_id(message) for message in model_messages]
    recent_messages = (
        model_messages[-len(required_recent_ids) :] if required_recent_ids else []
    )
    recent_message_retention_pass = (
        bool(required_recent_ids)
        and model_id_sequence[-len(required_recent_ids) :] == required_recent_ids
        and all(model_id_sequence.count(message_id) == 1 for message_id in required_recent_ids)
        and all(
            message_id in fixture_by_id
            and _canonical_message(fixture_by_id[message_id])
            == _canonical_message(model_message)
            for message_id, model_message in zip(
                required_recent_ids, recent_messages, strict=True
            )
        )
    )
    audit_integrity_pass = (
        len(fixture_messages) == len(audit_messages)
        and all(
            _canonical_message(original) == _canonical_message(audited)
            for original, audited in zip(
                fixture_messages, audit_messages, strict=True
            )
        )
    )
    summary_state_pass = (
        normalized_summary is None
        if expected_failure
        else normalized_summary is not None
        and isinstance(expected_summary, Mapping)
        and summary_unresolved_questions
        == expected_summary.get("unresolved_questions")
        and summary_failed_attempts == expected_summary.get("failed_attempts")
    )
    derived_observations = _derive_execution_observations(
        outcome.get("execution_trace")
    )
    scenario_contract_pass = (
        derived_observations is not None
        and isinstance(fixture, Mapping)
        and derived_observations == fixture.get("expected_observations")
    )

    tokens_before_value = _message_tokens(fixture_messages)
    tokens_after_value = _message_tokens(model_messages)
    valid_tokens = (
        tokens_before_value is not None
        and tokens_after_value is not None
        and tokens_before_value > 0
        and 0 <= tokens_after_value <= tokens_before_value
    )
    tokens_before = tokens_before_value or 0
    tokens_after = tokens_after_value or 0
    reduction_ratio = (
        (tokens_before - tokens_after) / tokens_before if valid_tokens else 0.0
    )

    fixture_canonical = [_canonical_message(message) for message in fixture_messages]
    model_canonical = {_canonical_message(message) for message in model_messages}
    old_prefix = [
        message
        for message in fixture_messages
        if _message_id(message) not in set(required_recent_ids)
    ]
    complete_transcript_retained = (
        len(fixture_messages) == len(model_messages)
        and all(
            original == model
            for original, model in zip(
                fixture_canonical,
                [_canonical_message(message) for message in model_messages],
                strict=True,
            )
        )
    )
    old_prefix_removed = bool(old_prefix) and not all(
        _canonical_message(message) in model_canonical for message in old_prefix
    )
    if expected_failure:
        compressed_view_pass = complete_transcript_retained
        token_reduction_pass = (
            valid_tokens and tokens_before == tokens_after and complete_transcript_retained
        )
    else:
        compressed_view_pass = old_prefix_removed and not complete_transcript_retained
        token_reduction_pass = (
            valid_tokens and reduction_ratio >= 0.4 and compressed_view_pass
        )

    row: dict[str, Any] = {
        "id": case_id,
        "compression_triggered": outcome.get("compression_triggered") is True,
        "compression_count": outcome.get("compression_count"),
        "expected_compression_count": expected_compression_count,
        "constraint_retention_pass": all(
            constraint in retained_texts for constraint in required_constraints
        ),
        "finding_retention_pass": all(
            finding in finding_claims for finding in required_findings
        ),
        "identifier_retention_pass": required_evidence_ids.issubset(
            summary_evidence_ids
        )
        and required_source_ids.issubset(set(summary_source_ids)),
        "fabricated_evidence_ids": fabricated_evidence_ids,
        "fabricated_source_ids": fabricated_source_ids,
        "orphan_tool_message_ids": orphan_ids,
        "recent_message_retention_pass": recent_message_retention_pass,
        "audit_integrity_pass": audit_integrity_pass,
        "summary_state_pass": summary_state_pass,
        "scenario_contract_pass": scenario_contract_pass,
        "derived_observations": derived_observations,
        "compressed_view_pass": compressed_view_pass,
        "tokens_before": tokens_before,
        "tokens_after": tokens_after,
        "reported_tokens_before": outcome.get("tokens_before"),
        "reported_tokens_after": outcome.get("tokens_after"),
        "token_reduction_ratio": round(reduction_ratio, 6),
        "token_reduction_pass": token_reduction_pass,
        "answer_contract_pass": _answer_contract_pass(case, outcome),
        "error_code": outcome.get("error_code")
        if isinstance(outcome.get("error_code"), str)
        else "invalid_outcome",
        "expected_error_code": expected_error_code,
        "summary_model": outcome.get("summary_model", ""),
        "fallback_reason": outcome.get("fallback_reason", ""),
        "runtime_error": outcome.get("runtime_error", ""),
    }
    row["compression_trigger_pass"] = row["compression_triggered"]
    row["compression_count_pass"] = (
        type(row["compression_count"]) is int
        and row["compression_count"] == expected_compression_count
    )
    row["error_contract_pass"] = row["error_code"] == expected_error_code
    row["case_pass"] = _row_pass(row)
    return row


def _ratio(rows: Sequence[Mapping[str, Any]], field_name: str) -> float:
    if not rows:
        return 0.0
    return round(sum(row.get(field_name) is True for row in rows) / len(rows), 6)


def _row_reduction(row: Mapping[str, Any]) -> float | None:
    before = row.get("tokens_before")
    after = row.get("tokens_after")
    if (
        type(before) is not int
        or type(after) is not int
        or before <= 0
        or after < 0
        or after > before
    ):
        return None
    return (before - after) / before


def summarize_long_context(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_case_ids: Sequence[str] = EXPECTED_CASE_IDS,
    dataset_contract_pass: bool = True,
    contract_errors: Sequence[str] = (),
) -> dict[str, Any]:
    materialized = [row for row in rows if isinstance(row, Mapping)]
    expected_ids = tuple(expected_case_ids)
    executed_ids = tuple(str(row.get("id") or "") for row in materialized)
    evaluation_complete = executed_ids == expected_ids
    reduction_ratios = [
        reduction
        for row in materialized
        if not row.get("expected_error_code")
        for reduction in (_row_reduction(row),)
        if reduction is not None
    ]
    median_reduction = statistics.median(reduction_ratios) if reduction_ratios else 0.0
    fabricated_count = sum(
        len(row.get("fabricated_evidence_ids", ()))
        + len(row.get("fabricated_source_ids", ()))
        for row in materialized
    )
    orphan_count = sum(
        len(row.get("orphan_tool_message_ids", ())) for row in materialized
    )
    all_case_contracts = evaluation_complete and all(
        _row_pass(row) for row in materialized
    )
    metrics: dict[str, Any] = {
        "compression_trigger_ratio": _ratio(materialized, "compression_trigger_pass"),
        "compression_count_ratio": _ratio(materialized, "compression_count_pass"),
        "constraint_retention_ratio": _ratio(
            materialized, "constraint_retention_pass"
        ),
        "finding_retention_ratio": _ratio(materialized, "finding_retention_pass"),
        "identifier_retention_ratio": _ratio(
            materialized, "identifier_retention_pass"
        ),
        "fabricated_identifier_count": fabricated_count,
        "orphan_tool_message_count": orphan_count,
        "recent_message_retention_ratio": _ratio(
            materialized, "recent_message_retention_pass"
        ),
        "audit_integrity_ratio": _ratio(materialized, "audit_integrity_pass"),
        "summary_state_ratio": _ratio(materialized, "summary_state_pass"),
        "scenario_contract_ratio": _ratio(materialized, "scenario_contract_pass"),
        "compressed_view_ratio": _ratio(materialized, "compressed_view_pass"),
        "token_reduction_case_ratio": _ratio(materialized, "token_reduction_pass"),
        "median_token_reduction_ratio": round(median_reduction, 6),
        "answer_contract_ratio": _ratio(materialized, "answer_contract_pass"),
        "error_contract_ratio": _ratio(materialized, "error_contract_pass"),
    }
    gate_checks = {
        "dataset_contract": dataset_contract_pass is True,
        "evaluation_complete": evaluation_complete,
        "all_case_contracts": all_case_contracts,
        "compression_triggered": metrics["compression_trigger_ratio"] == 1.0,
        "compression_count": metrics["compression_count_ratio"] == 1.0,
        "constraint_retention": metrics["constraint_retention_ratio"] == 1.0,
        "finding_retention": metrics["finding_retention_ratio"] == 1.0,
        "identifier_retention": metrics["identifier_retention_ratio"] == 1.0,
        "no_fabricated_identifiers": fabricated_count == 0,
        "no_orphan_tool_messages": orphan_count == 0,
        "recent_message_retention": metrics["recent_message_retention_ratio"] == 1.0,
        "audit_integrity": metrics["audit_integrity_ratio"] == 1.0,
        "summary_state": metrics["summary_state_ratio"] == 1.0,
        "scenario_contract": metrics["scenario_contract_ratio"] == 1.0,
        "compressed_view": metrics["compressed_view_ratio"] == 1.0,
        "token_reduction_cases": metrics["token_reduction_case_ratio"] == 1.0,
        "token_reduction": median_reduction >= 0.4,
        "answer_contract": metrics["answer_contract_ratio"] == 1.0,
        "error_contract": metrics["error_contract_ratio"] == 1.0,
    }
    return {
        "contract_version": CONTRACT_VERSION,
        "evaluated_case_count": len(materialized),
        "passed_case_count": sum(_row_pass(row) for row in materialized),
        "metrics": metrics,
        "gate_thresholds": {
            "all_ratios": 1.0,
            "fabricated_identifier_count": 0,
            "orphan_tool_message_count": 0,
            "median_token_reduction_ratio": 0.4,
        },
        "gate_checks": gate_checks,
        "gate_pass": all(gate_checks.values()),
        "contract_errors": list(contract_errors),
    }


def _git_identity() -> tuple[str, bool]:
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                [
                    "git",
                    "status",
                    "--porcelain",
                    "--",
                    ".",
                    ":(exclude)results/**",
                    ":(exclude)RAG_md/**",
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown", True
    return revision, dirty


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_long_context_eval(
    dataset_path: Path,
    out_dir: Path,
    compressor_factory: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    *,
    mode: str = "formal",
    case_ids: Sequence[str] | None = None,
    dataset_payload: Any | None = None,
) -> dict[str, Any]:
    if mode not in {"formal", "deterministic"}:
        raise ValueError("mode must be formal or deterministic")
    if not callable(compressor_factory):
        raise TypeError("compressor_factory must be callable")

    git_revision, git_dirty = _git_identity()
    dataset_path = Path(dataset_path)
    out_dir = Path(out_dir)
    if dataset_payload is None:
        dataset_bytes = dataset_path.read_bytes()
        raw_payload = json.loads(dataset_bytes.decode("utf-8"))
    else:
        raw_payload = dataset_payload
        dataset_bytes = json.dumps(
            raw_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")

    contract_errors: list[str] = []
    factory_mode = getattr(compressor_factory, "evaluation_mode", "")
    if factory_mode != mode:
        contract_errors.append(
            f"{mode} mode requires a factory declaring evaluation_mode={mode}"
        )
    try:
        dataset = validate_dataset(raw_payload)
    except (TypeError, ValueError) as exc:
        dataset = {"contract_version": CONTRACT_VERSION, "cases": []}
        contract_errors.append(str(exc))

    selected_ids = tuple(case_ids) if case_ids is not None else EXPECTED_CASE_IDS
    selected_set = set(selected_ids)
    selected_cases = [
        case for case in dataset["cases"] if case["id"] in selected_set
    ]
    selection_valid = (
        len(selected_ids) == len(selected_set)
        and all(case_id in EXPECTED_CASE_IDS for case_id in selected_ids)
        and tuple(case["id"] for case in selected_cases) == selected_ids
    )
    if not selection_valid:
        contract_errors.append("case selection contains unknown, duplicate, or reordered IDs")
        selected_cases = []

    rows: list[dict[str, Any]] = []
    for case in selected_cases:
        try:
            outcome = compressor_factory(copy.deepcopy(case))
        except Exception as exc:  # A case crash is a recorded Gate failure.
            outcome = {
                "runtime_error": f"{type(exc).__name__}: {exc}",
                "error_code": "evaluation_runtime_error",
            }
        rows.append(evaluate_case(case, outcome))

    summary = summarize_long_context(
        rows,
        expected_case_ids=EXPECTED_CASE_IDS,
        dataset_contract_pass=not contract_errors,
        contract_errors=contract_errors,
    )
    run_id = f"long-context-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "contract_version": CONTRACT_VERSION,
        "pipeline": "long_context_eval",
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "runner_script": "eval/eval_long_context.py",
        "dataset_path": str(dataset_path),
        "dataset_version": CONTRACT_VERSION,
        "dataset_fingerprint": hashlib.sha256(dataset_bytes).hexdigest(),
        "git_revision": git_revision,
        "git_dirty": git_dirty,
        "execution": {"mode": mode},
        "factory_evaluation_mode": factory_mode,
        "policy": getattr(
            compressor_factory,
            "policy",
            {
                "trigger_ratio": 0.70,
                "target_ratio": 0.45,
                "hard_limit_ratio": 0.90,
            },
        ),
        "counter": getattr(
            compressor_factory, "counter_identity", "agent.context.budget"
        ),
        "summary_client_identity": getattr(
            compressor_factory,
            "summary_client_identity",
            getattr(compressor_factory, "__name__", type(compressor_factory).__name__),
        ),
        "evaluation_scope": {
            "expected_case_count": len(EXPECTED_CASE_IDS),
            "selected_case_count": len(selected_cases),
            "executed_case_count": len(rows),
            "selected_case_ids": [case["id"] for case in selected_cases],
            "selection_complete": tuple(case["id"] for case in selected_cases)
            == EXPECTED_CASE_IDS,
            "evaluation_complete": summary["gate_checks"]["evaluation_complete"],
        },
    }
    _write_json(run_dir / "manifest.json", manifest)
    _write_json(run_dir / "predictions.json", rows)
    _write_json(run_dir / "summary.json", summary)
    return {
        "run_dir": run_dir,
        "manifest": manifest,
        "predictions": rows,
        "summary": summary,
    }


def _fixture_message(message_id: str, role: str, content: str) -> dict[str, Any]:
    return {
        "id": message_id,
        "role": role,
        "content": content,
        "evidence_ids": [],
        "source_ids": [],
    }


def _deterministic_fixture_trace(case: Mapping[str, Any]) -> list[dict[str, Any]]:
    fixture = cast(Mapping[str, Any], case["fixture"])
    observations = cast(Mapping[str, Any], fixture["expected_observations"])
    trace: list[dict[str, Any]] = []
    resumed_revision = cast(int, observations["resumed_revision"])
    if resumed_revision:
        trace.append({"type": "session_resumed", "revision": resumed_revision})
    failed_call_ids = set(cast(list[str], observations["failed_tool_call_ids"]))
    for call_id in cast(list[str], observations["tool_pair_call_ids"]):
        trace.extend(
            [
                {"type": "tool_call", "call_id": call_id},
                {
                    "type": "tool_result",
                    "call_id": call_id,
                    "status": "failed" if call_id in failed_call_ids else "succeeded",
                },
            ]
        )
    compression_count = cast(int, observations["compression_round_count"])
    for round_number in range(1, max(1, compression_count) + 1):
        trace.append(
            {
                "type": "summary_attempt",
                "round": round_number,
                "provider": "local",
                "status": observations["local_summary_status"],
            }
        )
        fallback_status = observations["fallback_summary_status"]
        if fallback_status != "not_used":
            trace.append(
                {
                    "type": "summary_attempt",
                    "round": round_number,
                    "provider": "fallback",
                    "status": fallback_status,
                }
            )
        if round_number == 1:
            for index in range(cast(int, observations["revision_conflict_count"])):
                trace.append(
                    {
                        "type": "revision_conflict",
                        "round": round_number,
                        "expected_revision": resumed_revision + index,
                        "actual_revision": resumed_revision + index + 1,
                    }
                )
        if round_number <= compression_count:
            trace.append({"type": "compression_committed", "round": round_number})
    return trace


def deterministic_compressor_factory(case: Mapping[str, Any]) -> dict[str, Any]:
    fixture = cast(Mapping[str, Any], case["fixture"])
    original_messages = copy.deepcopy(cast(list[dict[str, Any]], fixture["messages"]))
    original_by_id = {message["id"]: message for message in original_messages}
    dual_failure = case["id"] == "dual-summary-failure-001"
    if dual_failure:
        model_messages = copy.deepcopy(original_messages)
    else:
        model_messages = [
            _fixture_message(
                f"summary-{case['id']}",
                "system",
                f"Compressed structured summary for {case['id']}.",
            ),
            *(
                copy.deepcopy(original_by_id[message_id])
                for message_id in case["required_recent_message_ids"]
            ),
        ]
    answer_contract = cast(Mapping[str, Any], case["answer_contract"])
    expected_summary = cast(Mapping[str, Any], fixture["expected_summary"])
    answer = " ".join(
        [
            "The compressed conversation preserves",
            *cast(list[str], answer_contract["required_terms"]),
            *cast(list[str], answer_contract["required_source_ids"]),
            "with verified context and no unverified claims.",
        ]
    )
    return {
        "compression_triggered": True,
        "compression_count": case["expected_compression_count"],
        "summary": None
        if dual_failure
        else {
            "goal": case["description"],
            "user_constraints": list(case["required_constraints"]),
            "confirmed_findings": [
                {
                    "claim": finding,
                    "evidence_ids": list(case["required_evidence_ids"]),
                }
                for finding in case["required_findings"]
            ],
            "decisions": [],
            "unresolved_questions": list(
                cast(list[str], expected_summary["unresolved_questions"])
            ),
            "failed_attempts": list(
                cast(list[str], expected_summary["failed_attempts"])
            ),
            "referenced_source_ids": list(case["required_source_ids"]),
        },
        "original_messages": copy.deepcopy(original_messages),
        "audit_messages": copy.deepcopy(original_messages),
        "model_messages": model_messages,
        "tokens_before": 1,
        "tokens_after": 1,
        "answer": answer,
        "execution_trace": _deterministic_fixture_trace(case),
        "error_code": case["expected_error_code"],
        "summary_model": "deterministic-cloud-fallback-v1"
        if case["id"] == "local-summary-fallback-001"
        else "deterministic-summary-v1",
        "fallback_reason": "primary_summary_failed"
        if case["id"] == "local-summary-fallback-001"
        else "",
    }


setattr(
    deterministic_compressor_factory,
    "evaluation_mode",
    "deterministic",
)
setattr(
    deterministic_compressor_factory,
    "policy",
    {"trigger_ratio": 0.70, "target_ratio": 0.45, "hard_limit_ratio": 0.90},
)
setattr(
    deterministic_compressor_factory,
    "counter_identity",
    "agent.context.budget.count_message_tokens",
)
setattr(
    deterministic_compressor_factory,
    "summary_client_identity",
    "deterministic-summary-v1",
)


def _load_factory(spec: str) -> Callable[[Mapping[str, Any]], Mapping[str, Any]]:
    module_name, separator, attribute_name = spec.partition(":")
    if not separator or not module_name or not attribute_name:
        raise ValueError("factory must use module:attribute syntax")
    module = importlib.import_module(module_name)
    factory = getattr(module, attribute_name)
    if not callable(factory):
        raise TypeError("imported factory must be callable")
    return cast(Callable[[Mapping[str, Any]], Mapping[str, Any]], factory)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the v1.6 long-context Gate.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--mode", choices=("deterministic", "formal"), default="formal")
    parser.add_argument("--case-id", action="append", dest="case_ids", default=None)
    parser.add_argument(
        "--factory",
        help="Importable formal adapter factory using module:attribute syntax.",
    )
    return parser


def main() -> dict[str, Any]:
    args = build_parser().parse_args()
    if args.factory:
        factory = _load_factory(args.factory)
    elif args.mode == "deterministic":
        factory = deterministic_compressor_factory
    else:

        def factory(case: Mapping[str, Any]) -> Mapping[str, Any]:
            raise RuntimeError("formal compressor factory is not configured")

    result = run_long_context_eval(
        args.dataset,
        args.out_dir,
        factory,
        mode=args.mode,
        case_ids=args.case_ids,
    )
    for row in result["predictions"]:
        status = "PASS" if _row_pass(row) else "FAIL"
        print(f"{status}: {row['id']}")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"run_id={result['manifest']['run_id']}")
    print(f"summary_path={result['run_dir'] / 'summary.json'}")
    return result


if __name__ == "__main__":
    run_result = main()
    raise SystemExit(0 if run_result["summary"]["gate_pass"] else 1)
