from __future__ import annotations

import copy
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Literal, Protocol

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import BaseTool

from core.chat_history import message_identity
from utils.session import validate_session_id

from .budget import count_message_tokens, decide_compression, partition_messages
from .models import (
    CompressionDecision,
    CompressionPolicy,
    ConversationCompressionError,
    ConversationSummary,
    SummaryFinding,
)
from .store import (
    ConversationContextStore,
    ConversationRevisionConflictError,
    ConversationSummarySnapshot,
    SummaryCommitCommand,
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
_FINDING_FIELDS = frozenset({"claim", "evidence_ids"})
_MAX_SUMMARY_ITEM_LENGTH = 4000
_DEFAULT_LOCAL_CONTEXT_LIMIT = 40960
_ERROR_CODE = ConversationCompressionError.error_code
_OPERATIONAL_CLIENT_ERRORS = (
    ConnectionError,
    TimeoutError,
    OSError,
    ConversationCompressionError,
)
_EVIDENCE_ID_KEYS = frozenset({"evidence_id", "evidence_ids"})
_SOURCE_ID_KEYS = frozenset({"source_id", "source_ids"})


@dataclass(frozen=True)
class SummaryRequest:
    previous_summary: ConversationSummary | None
    messages: tuple[BaseMessage, ...]
    allowed_evidence_ids: frozenset[str]
    allowed_source_ids: frozenset[str]
    input_token_limit: int

    def __post_init__(self) -> None:
        if self.previous_summary is not None and not isinstance(
            self.previous_summary,
            ConversationSummary,
        ):
            raise TypeError("previous_summary must be a ConversationSummary or None")
        if not isinstance(self.messages, tuple):
            raise TypeError("messages must be a tuple")
        if not all(isinstance(message, BaseMessage) for message in self.messages):
            raise TypeError("messages must contain only BaseMessage values")
        _validate_id_frozenset(self.allowed_evidence_ids, "allowed_evidence_ids")
        _validate_id_frozenset(self.allowed_source_ids, "allowed_source_ids")
        _positive_int(self.input_token_limit, "input_token_limit")


@dataclass(frozen=True)
class SummaryClientResult:
    payload: Mapping[str, object]
    model_id: str
    fallback_reason: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must be a mapping")
        _validate_text(self.model_id, "model_id")
        _validate_text(
            self.fallback_reason,
            "fallback_reason",
            allow_empty=True,
        )


@dataclass(frozen=True)
class CompressionOutcome:
    status: Literal["not_needed", "compressed", "skipped_with_error"]
    summary: ConversationSummary | None
    recent_messages: tuple[BaseMessage, ...]
    revision: int
    tokens_before: int
    tokens_after: int
    messages_before: int
    messages_after: int
    summary_model: str
    fallback_reason: str
    error_code: str

    def __post_init__(self) -> None:
        if self.status not in {"not_needed", "compressed", "skipped_with_error"}:
            raise ValueError("status is invalid")
        if self.summary is not None and not isinstance(self.summary, ConversationSummary):
            raise TypeError("summary must be a ConversationSummary or None")
        if not isinstance(self.recent_messages, tuple) or not all(
            isinstance(message, BaseMessage) for message in self.recent_messages
        ):
            raise TypeError("recent_messages must be a tuple of BaseMessage values")
        for field_name in (
            "revision",
            "tokens_before",
            "tokens_after",
            "messages_before",
            "messages_after",
        ):
            _non_negative_int(getattr(self, field_name), field_name)
        for field_name in ("summary_model", "fallback_reason", "error_code"):
            _validate_text(getattr(self, field_name), field_name, allow_empty=True)


class SummaryClient(Protocol):
    def summarize(self, request: SummaryRequest) -> SummaryClientResult:
        raise NotImplementedError


def _positive_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{field_name} must be an int")
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return value


def _non_negative_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be at least 0")
    return value


def _validate_text(
    value: object,
    field_name: str,
    *,
    allow_empty: bool = False,
) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    if not allow_empty and not value.strip():
        raise ValueError(f"{field_name} must not be blank")
    if len(value) > _MAX_SUMMARY_ITEM_LENGTH:
        raise ValueError(
            f"{field_name} must not exceed {_MAX_SUMMARY_ITEM_LENGTH} characters"
        )
    return value


def _validate_id_frozenset(value: object, field_name: str) -> None:
    if not isinstance(value, frozenset):
        raise TypeError(f"{field_name} must be a frozenset")
    for item in value:
        _validate_text(item, field_name)


def _parse_string_sequence(value: object, field_name: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise TypeError(f"{field_name} must be a sequence")
    parsed = tuple(
        _validate_text(item, f"{field_name} item")
        for item in value
    )
    return parsed


def _parse_id_sequence(value: object, field_name: str) -> tuple[str, ...]:
    parsed = _parse_string_sequence(value, field_name)
    if len(set(parsed)) != len(parsed):
        raise ValueError(f"{field_name} must not contain duplicate IDs")
    return parsed


def parse_summary(payload: Mapping[str, object]) -> ConversationSummary:
    if not isinstance(payload, Mapping):
        raise TypeError("summary payload must be a mapping")
    if set(payload) != _SUMMARY_FIELDS:
        raise ValueError("summary payload must contain exactly the seven contract fields")

    findings_payload = payload["confirmed_findings"]
    if isinstance(findings_payload, (str, bytes, bytearray)) or not isinstance(
        findings_payload,
        Sequence,
    ):
        raise TypeError("confirmed_findings must be a sequence")

    findings = []
    for index, finding_payload in enumerate(findings_payload):
        if not isinstance(finding_payload, Mapping):
            raise TypeError("confirmed_findings items must be mappings")
        if set(finding_payload) != _FINDING_FIELDS:
            raise ValueError(
                "confirmed_findings items must contain exactly claim and evidence_ids"
            )
        findings.append(
            SummaryFinding(
                claim=_validate_text(
                    finding_payload["claim"],
                    f"confirmed_findings[{index}].claim",
                ),
                evidence_ids=_parse_id_sequence(
                    finding_payload["evidence_ids"],
                    f"confirmed_findings[{index}].evidence_ids",
                ),
            )
        )

    return ConversationSummary(
        goal=_validate_text(payload["goal"], "goal"),
        user_constraints=_parse_string_sequence(
            payload["user_constraints"],
            "user_constraints",
        ),
        confirmed_findings=tuple(findings),
        decisions=_parse_string_sequence(payload["decisions"], "decisions"),
        unresolved_questions=_parse_string_sequence(
            payload["unresolved_questions"],
            "unresolved_questions",
        ),
        failed_attempts=_parse_string_sequence(
            payload["failed_attempts"],
            "failed_attempts",
        ),
        referenced_source_ids=_parse_id_sequence(
            payload["referenced_source_ids"],
            "referenced_source_ids",
        ),
    )


def _finding_evidence_ids(summary: ConversationSummary | None) -> set[str]:
    if summary is None:
        return set()
    return {
        evidence_id
        for finding in summary.confirmed_findings
        for evidence_id in finding.evidence_ids
    }


def _equivalent_claim(value: str) -> str:
    return " ".join(value.split()).casefold()


def validate_summary(
    summary: ConversationSummary,
    request: SummaryRequest,
) -> None:
    if not isinstance(summary, ConversationSummary):
        raise TypeError("summary must be a ConversationSummary")
    if not isinstance(request, SummaryRequest):
        raise TypeError("request must be a SummaryRequest")

    previous = request.previous_summary
    allowed_evidence_ids = set(request.allowed_evidence_ids)
    allowed_source_ids = set(request.allowed_source_ids)
    if previous is not None:
        allowed_evidence_ids.update(_finding_evidence_ids(previous))
        allowed_source_ids.update(previous.referenced_source_ids)

    candidate_evidence_ids = _finding_evidence_ids(summary)
    if not candidate_evidence_ids.issubset(allowed_evidence_ids):
        raise ValueError("summary contains evidence IDs outside the request allowlist")
    if not set(summary.referenced_source_ids).issubset(allowed_source_ids):
        raise ValueError("summary contains source IDs outside the request allowlist")

    if previous is None:
        return
    if not set(previous.user_constraints).issubset(summary.user_constraints):
        raise ValueError("summary removed a previous user constraint")
    if not set(previous.failed_attempts).issubset(summary.failed_attempts):
        raise ValueError("summary removed a previous failed attempt")

    candidate_claims = {
        _equivalent_claim(finding.claim) for finding in summary.confirmed_findings
    }
    exact_decisions = set(summary.decisions)
    for finding in previous.confirmed_findings:
        if (
            _equivalent_claim(finding.claim) not in candidate_claims
            and finding.claim not in exact_decisions
        ):
            raise ValueError("summary removed an unresolved previous finding")

    exact_finding_claims = {finding.claim for finding in summary.confirmed_findings}
    for question in previous.unresolved_questions:
        if (
            question not in summary.unresolved_questions
            and question not in exact_decisions
            and question not in exact_finding_claims
        ):
            raise ValueError("summary removed an unresolved question without resolution")


def parse_and_validate_summary(
    payload: Mapping[str, object],
    request: SummaryRequest,
) -> ConversationSummary:
    summary = parse_summary(payload)
    validate_summary(summary, request)
    return summary


class FallbackSummaryClient:
    def __init__(self, primary: SummaryClient, fallback: SummaryClient) -> None:
        if not callable(getattr(primary, "summarize", None)):
            raise TypeError("primary must provide summarize(request)")
        if not callable(getattr(fallback, "summarize", None)):
            raise TypeError("fallback must provide summarize(request)")
        self._primary = primary
        self._fallback = fallback

    def summarize(self, request: SummaryRequest) -> SummaryClientResult:
        if not isinstance(request, SummaryRequest):
            raise TypeError("request must be a SummaryRequest")
        try:
            primary_result = self._primary.summarize(request)
        except _OPERATIONAL_CLIENT_ERRORS:
            primary_result = None
        else:
            try:
                _validate_client_result(primary_result, request)
            except (TypeError, ValueError):
                primary_result = None
        if primary_result is not None:
            return primary_result

        try:
            fallback_result = self._fallback.summarize(request)
        except _OPERATIONAL_CLIENT_ERRORS:
            raise ConversationCompressionError("summary clients failed") from None
        try:
            _validate_client_result(fallback_result, request)
        except (TypeError, ValueError):
            raise ConversationCompressionError("summary clients failed") from None
        return SummaryClientResult(
            payload=fallback_result.payload,
            model_id=fallback_result.model_id,
            fallback_reason=(
                fallback_result.fallback_reason or "primary_summary_failed"
            ),
        )


def _validate_client_result(
    result: object,
    request: SummaryRequest,
) -> ConversationSummary:
    if not isinstance(result, SummaryClientResult):
        raise TypeError("summary client must return SummaryClientResult")
    return parse_and_validate_summary(result.payload, request)


@dataclass(frozen=True)
class _AttemptState:
    snapshot: ConversationSummarySnapshot | None
    uncovered_messages: tuple[BaseMessage, ...]
    tokens_before: int
    decision: CompressionDecision


class _CompressionAttemptError(RuntimeError):
    pass


def _summary_payload(summary: ConversationSummary) -> dict[str, object]:
    return {
        "goal": summary.goal,
        "user_constraints": list(summary.user_constraints),
        "confirmed_findings": [
            {
                "claim": finding.claim,
                "evidence_ids": list(finding.evidence_ids),
            }
            for finding in summary.confirmed_findings
        ],
        "decisions": list(summary.decisions),
        "unresolved_questions": list(summary.unresolved_questions),
        "failed_attempts": list(summary.failed_attempts),
        "referenced_source_ids": list(summary.referenced_source_ids),
    }


def _summary_message(summary: ConversationSummary) -> SystemMessage:
    content = json.dumps(
        _summary_payload(summary),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return SystemMessage(content=f"Conversation summary:\n{content}")


def _stable_unique(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _normalize_sequence(value: object, field_name: str) -> tuple[object, ...]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise TypeError(f"{field_name} must be a sequence")
    return tuple(value)


def _normalize_protected_ids(value: object, field_name: str) -> tuple[str, ...]:
    materialized = _normalize_sequence(value, field_name)
    parsed = tuple(_validate_text(item, f"{field_name} item") for item in materialized)
    if len(set(parsed)) != len(parsed):
        raise ValueError(f"{field_name} must not contain duplicate IDs")
    return parsed


def _normalize_tools(value: object) -> tuple[dict[str, object] | BaseTool, ...]:
    materialized = _normalize_sequence(value, "tools")
    if not all(isinstance(tool, (dict, BaseTool)) for tool in materialized):
        raise TypeError("tools must contain only tool schema dictionaries or BaseTool values")
    return materialized


def _add_structured_id(value: object, destination: set[str]) -> None:
    if (
        isinstance(value, str)
        and value.strip()
        and len(value) <= _MAX_SUMMARY_ITEM_LENGTH
    ):
        destination.add(value)


def _extract_structured_ids(
    value: object,
    evidence_ids: set[str],
    source_ids: set[str],
) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            destination = None
            if key in _EVIDENCE_ID_KEYS:
                destination = evidence_ids
            elif key in _SOURCE_ID_KEYS:
                destination = source_ids

            if destination is not None:
                if key.endswith("_ids") and isinstance(nested, Sequence) and not isinstance(
                    nested,
                    (str, bytes, bytearray),
                ):
                    for item in nested:
                        _add_structured_id(item, destination)
                else:
                    _add_structured_id(nested, destination)
            _extract_structured_ids(nested, evidence_ids, source_ids)
        return

    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        for item in value:
            _extract_structured_ids(item, evidence_ids, source_ids)


def _message_structured_ids(
    messages: Sequence[BaseMessage],
) -> tuple[set[str], set[str]]:
    evidence_ids: set[str] = set()
    source_ids: set[str] = set()
    for message in messages:
        containers = [message.additional_kwargs, message.response_metadata]
        if not isinstance(message.content, str):
            containers.append(message.content)
        artifact = getattr(message, "artifact", None)
        if artifact is not None:
            containers.append(artifact)
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            containers.append(tool_calls)
        for container in containers:
            _extract_structured_ids(container, evidence_ids, source_ids)
    return evidence_ids, source_ids


class ConversationCompressor:
    def __init__(
        self,
        store: ConversationContextStore,
        summary_client: SummaryClient,
        policy: CompressionPolicy | None = None,
        *,
        target_model_context_limit: int = _DEFAULT_LOCAL_CONTEXT_LIMIT,
        summary_model_context_limit: int = _DEFAULT_LOCAL_CONTEXT_LIMIT,
    ) -> None:
        if not callable(getattr(store, "get_summary", None)) or not callable(
            getattr(store, "commit_summary", None)
        ):
            raise TypeError("store must provide summary read and commit operations")
        if not callable(getattr(summary_client, "summarize", None)):
            raise TypeError("summary_client must provide summarize(request)")
        if policy is None:
            policy = CompressionPolicy()
        if not isinstance(policy, CompressionPolicy):
            raise TypeError("policy must be a CompressionPolicy")

        self._store = store
        self._summary_client = summary_client
        self._target_model_context_limit = _positive_int(
            target_model_context_limit,
            "target_model_context_limit",
        )
        self._summary_model_context_limit = _positive_int(
            summary_model_context_limit,
            "summary_model_context_limit",
        )
        self._policy = replace(
            policy,
            context_limit=min(policy.context_limit, self._target_model_context_limit),
        )

    def prepare_model_view(
        self,
        session_id: str,
        messages: Sequence[BaseMessage],
        tools: Sequence[object] = (),
        protected_evidence_ids: Sequence[str] = (),
        protected_source_ids: Sequence[str] = (),
    ) -> CompressionOutcome:
        session_id = validate_session_id(session_id)
        materialized_messages = _normalize_sequence(messages, "messages")
        if not all(
            isinstance(message, BaseMessage) for message in materialized_messages
        ):
            raise TypeError("messages must contain only BaseMessage values")
        materialized_tools = _normalize_tools(tools)
        evidence_ids = _normalize_protected_ids(
            protected_evidence_ids,
            "protected_evidence_ids",
        )
        source_ids = _normalize_protected_ids(
            protected_source_ids,
            "protected_source_ids",
        )
        immutable_messages = tuple(materialized_messages)

        for attempt in range(2):
            state = self._load_state(
                session_id,
                immutable_messages,
                materialized_tools,
            )
            if not state.decision.should_compress:
                return self._not_needed(state)
            try:
                return self._compress_once(
                    session_id,
                    state,
                    materialized_tools,
                    evidence_ids,
                    source_ids,
                )
            except ConversationRevisionConflictError:
                if attempt == 0:
                    continue
                latest = self._load_state(
                    session_id,
                    immutable_messages,
                    materialized_tools,
                )
                return self._failed_outcome(latest)
            except _CompressionAttemptError:
                return self._failed_outcome(state)

        raise AssertionError("compression retry loop exhausted")

    def _load_state(
        self,
        session_id: str,
        messages: tuple[BaseMessage, ...],
        tools: tuple[object, ...],
    ) -> _AttemptState:
        snapshot = self._store.get_summary(session_id)
        remaining_covered = (
            set(snapshot.covered_message_ids) if snapshot is not None else set()
        )
        uncovered_messages = []
        for message in messages:
            identity = message_identity(message)
            if identity in remaining_covered:
                remaining_covered.remove(identity)
            else:
                uncovered_messages.append(message)
        uncovered = tuple(uncovered_messages)
        model_view = list(uncovered)
        if snapshot is not None:
            model_view.insert(0, _summary_message(snapshot.summary))
        tokens_before = count_message_tokens(model_view, tools=tools)
        return _AttemptState(
            snapshot=snapshot,
            uncovered_messages=uncovered,
            tokens_before=tokens_before,
            decision=decide_compression(tokens_before, self._policy),
        )

    def _compress_once(
        self,
        session_id: str,
        state: _AttemptState,
        tools: tuple[object, ...],
        protected_evidence_ids: tuple[str, ...],
        protected_source_ids: tuple[str, ...],
    ) -> CompressionOutcome:
        prefix, recent = partition_messages(
            state.uncovered_messages,
            recent_turns=self._policy.recent_turns,
            target_tokens=state.decision.target_message_tokens,
        )
        if not prefix:
            raise _CompressionAttemptError("no safe message boundary for compression")

        previous = state.snapshot.summary if state.snapshot is not None else None
        previous_evidence_ids = _finding_evidence_ids(previous)
        previous_source_ids = set(previous.referenced_source_ids) if previous else set()
        extracted_evidence_ids, extracted_source_ids = _message_structured_ids(prefix)
        input_token_limit = min(
            self._target_model_context_limit,
            self._summary_model_context_limit,
            self._policy.context_limit,
        )
        summary_input_view = list(prefix)
        if previous is not None:
            summary_input_view.insert(0, _summary_message(previous))
        if count_message_tokens(summary_input_view, tools=tools) > input_token_limit:
            raise _CompressionAttemptError("summary request exceeds its input limit")

        prefix_identities = tuple(message_identity(message) for message in prefix)
        request = SummaryRequest(
            previous_summary=previous,
            messages=copy.deepcopy(prefix),
            allowed_evidence_ids=frozenset(
                (
                    *protected_evidence_ids,
                    *previous_evidence_ids,
                    *extracted_evidence_ids,
                )
            ),
            allowed_source_ids=frozenset(
                (*protected_source_ids, *previous_source_ids, *extracted_source_ids)
            ),
            input_token_limit=input_token_limit,
        )
        try:
            result = self._summary_client.summarize(request)
        except _OPERATIONAL_CLIENT_ERRORS:
            raise _CompressionAttemptError("summary client failed") from None
        try:
            summary = _validate_client_result(result, request)
        except (TypeError, ValueError):
            raise _CompressionAttemptError("summary contract is invalid") from None

        tokens_after = count_message_tokens(
            (_summary_message(summary), *recent),
            tools=tools,
        )
        if tokens_after >= state.decision.target_message_tokens:
            raise _CompressionAttemptError("compressed view exceeds target budget")

        old_covered = state.snapshot.covered_message_ids if state.snapshot else ()
        covered_message_ids = _stable_unique(
            (*old_covered, *prefix_identities)
        )
        expected_revision = state.snapshot.revision if state.snapshot else 0
        committed = self._store.commit_summary(
            SummaryCommitCommand(
                session_id=session_id,
                summary=summary,
                covered_message_ids=covered_message_ids,
                tokens_before=state.tokens_before,
                tokens_after=tokens_after,
                messages_before=len(state.uncovered_messages),
                messages_after=len(recent),
                summary_model=result.model_id,
                compression_reason="trigger_ratio",
                fallback_reason=result.fallback_reason,
            ),
            expected_revision=expected_revision,
        )
        return CompressionOutcome(
            status="compressed",
            summary=committed.summary,
            recent_messages=recent,
            revision=committed.revision,
            tokens_before=committed.tokens_before,
            tokens_after=committed.tokens_after,
            messages_before=committed.messages_before,
            messages_after=committed.messages_after,
            summary_model=committed.summary_model,
            fallback_reason=committed.fallback_reason,
            error_code="",
        )

    @staticmethod
    def _not_needed(state: _AttemptState) -> CompressionOutcome:
        snapshot = state.snapshot
        return CompressionOutcome(
            status="not_needed",
            summary=snapshot.summary if snapshot else None,
            recent_messages=state.uncovered_messages,
            revision=snapshot.revision if snapshot else 0,
            tokens_before=state.tokens_before,
            tokens_after=state.tokens_before,
            messages_before=len(state.uncovered_messages),
            messages_after=len(state.uncovered_messages),
            summary_model=snapshot.summary_model if snapshot else "",
            fallback_reason=snapshot.fallback_reason if snapshot else "",
            error_code="",
        )

    @staticmethod
    def _failed_outcome(state: _AttemptState) -> CompressionOutcome:
        if state.tokens_before >= state.decision.hard_message_tokens:
            raise ConversationCompressionError("conversation compression failed") from None
        snapshot = state.snapshot
        return CompressionOutcome(
            status="skipped_with_error",
            summary=snapshot.summary if snapshot else None,
            recent_messages=state.uncovered_messages,
            revision=snapshot.revision if snapshot else 0,
            tokens_before=state.tokens_before,
            tokens_after=state.tokens_before,
            messages_before=len(state.uncovered_messages),
            messages_after=len(state.uncovered_messages),
            summary_model=snapshot.summary_model if snapshot else "",
            fallback_reason=snapshot.fallback_reason if snapshot else "",
            error_code=_ERROR_CODE,
        )
