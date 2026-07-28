from __future__ import annotations

import copy
import hashlib
import json
import logging
import threading
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict

from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
)
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from typing_extensions import override

from core.chat_history import FileChatMessageHistory, get_history, message_identity
from utils.session import validate_session_id

from .compressor import CompressionOutcome, ConversationCompressor
from .models import ConversationSummary
from .store import (
    ConversationContextStore,
    ConversationSummarySnapshot,
    TokenObservationCommand,
)


logger = logging.getLogger(__name__)
_REQUEST_ID_MAX_LENGTH = 256
_SESSION_TURN_LOCKS_GUARD = threading.Lock()
_SESSION_TURN_LOCKS: dict[str, threading.RLock] = {}


def _empty_ids() -> tuple[str, ...]:
    return ()


def _session_turn_lock(session_id: str) -> threading.RLock:
    with _SESSION_TURN_LOCKS_GUARD:
        return _SESSION_TURN_LOCKS.setdefault(session_id, threading.RLock())


def _safe_provider_values(
    provider: Callable[[], Sequence[str]],
    field_name: str,
) -> tuple[str, ...]:
    values = provider()
    if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
        raise TypeError(f"{field_name} provider must return a sequence")
    normalized = tuple(values)
    if not all(isinstance(value, str) for value in normalized):
        raise TypeError(f"{field_name} provider must return only str values")
    return normalized


def _summary_text(summary: ConversationSummary, revision: int) -> str:
    payload = json.dumps(
        asdict(summary),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"Conversation summary revision {revision}:\n{payload}"


def _system_with_summary(
    system_message: SystemMessage | None,
    summary: ConversationSummary | None,
    revision: int,
) -> SystemMessage | None:
    if summary is None:
        return system_message.model_copy(deep=True) if system_message is not None else None

    summary_content = _summary_text(summary, revision)
    if system_message is None:
        return SystemMessage(content=summary_content)

    if isinstance(system_message.content, str):
        content = (
            f"{system_message.content}\n\n{summary_content}"
            if system_message.content
            else summary_content
        )
        return system_message.model_copy(deep=True, update={"content": content})

    structured_content = [
        *copy.deepcopy(system_message.content),
        {"type": "text", "text": summary_content},
    ]
    return system_message.model_copy(
        deep=True,
        update={"content": structured_content},
    )


def _response_messages(response: ModelResponse | AIMessage) -> tuple[BaseMessage, ...]:
    if isinstance(response, ModelResponse):
        messages = tuple(response.result)
        if not all(isinstance(message, BaseMessage) for message in messages):
            raise TypeError("ModelResponse.result must contain only BaseMessage values")
        return messages
    if isinstance(response, AIMessage):
        return (response,)
    raise TypeError("handler must return a ModelResponse or AIMessage")


def _usage_tokens(message: AIMessage) -> tuple[int, int] | None:
    usage: object = message.usage_metadata
    if usage is None and isinstance(message.response_metadata, Mapping):
        usage = message.response_metadata.get("usage_metadata")
    if not isinstance(usage, Mapping):
        return None

    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    if (
        type(input_tokens) is not int
        or input_tokens < 0
        or type(output_tokens) is not int
        or output_tokens < 0
    ):
        return None
    return input_tokens, output_tokens


def _revision_request_id(value: str, revision: int) -> str:
    namespace = f"revision-{revision}:"
    namespaced_value = f"{namespace}{value}"
    if len(namespaced_value) <= _REQUEST_ID_MAX_LENGTH:
        return namespaced_value
    digest = hashlib.sha256(namespaced_value.encode("utf-8")).hexdigest()
    return f"{namespace}response-sha256:{digest}"


def _request_id(message: AIMessage, revision: int) -> str:
    if message.id is not None and str(message.id).strip():
        return _revision_request_id(str(message.id).strip(), revision)

    metadata = message.response_metadata
    if isinstance(metadata, Mapping):
        for key in ("request_id", "response_id", "id"):
            value = metadata.get(key)
            if value is not None and str(value).strip():
                return _revision_request_id(str(value).strip(), revision)

    identity = message_identity(message)
    return _revision_request_id(identity, revision)


class ConversationContextMiddleware(AgentMiddleware):
    def __init__(
        self,
        *,
        session_id: str,
        compressor: ConversationCompressor,
        store: ConversationContextStore,
        history: FileChatMessageHistory | None = None,
        protected_evidence_ids: Callable[[], Sequence[str]] | None = None,
        protected_source_ids: Callable[[], Sequence[str]] | None = None,
    ) -> None:
        super().__init__()
        self.session_id = validate_session_id(session_id)
        if not isinstance(compressor, ConversationCompressor):
            raise TypeError("compressor must be a ConversationCompressor")
        if not isinstance(store, ConversationContextStore):
            raise TypeError("store must be a ConversationContextStore")
        resolved_history = history if history is not None else get_history(self.session_id)
        if not isinstance(resolved_history, FileChatMessageHistory):
            raise TypeError("history must be a FileChatMessageHistory")
        if resolved_history.session_id != self.session_id:
            raise ValueError("history session_id must match session_id")

        evidence_provider = (
            _empty_ids if protected_evidence_ids is None else protected_evidence_ids
        )
        source_provider = (
            _empty_ids if protected_source_ids is None else protected_source_ids
        )
        if not callable(evidence_provider):
            raise TypeError("protected_evidence_ids must be callable")
        if not callable(source_provider):
            raise TypeError("protected_source_ids must be callable")

        self.compressor = compressor
        self.store = store
        self.history = resolved_history
        self._turn_lock = _session_turn_lock(self.session_id)
        self.protected_evidence_ids = evidence_provider
        self.protected_source_ids = source_provider

    @override
    def wrap_model_call(self, request: ModelRequest, handler):
        with self._turn_lock:
            self.history.add_messages_unique(request.messages)
            outcome = self.compressor.prepare_model_view(
                session_id=self.session_id,
                messages=self.history.messages,
                tools=request.tools or (),
                protected_evidence_ids=_safe_provider_values(
                    self.protected_evidence_ids,
                    "protected_evidence_ids",
                ),
                protected_source_ids=_safe_provider_values(
                    self.protected_source_ids,
                    "protected_source_ids",
                ),
            )
            overridden = request.override(
                messages=[copy.deepcopy(message) for message in outcome.recent_messages],
                system_message=_system_with_summary(
                    request.system_message,
                    outcome.summary,
                    outcome.revision,
                ),
            )
            response = handler(overridden)
            response_messages = _response_messages(response)
            self.history.add_messages_unique(response_messages)
            self._record_actual_usage(response_messages, outcome)
            return response

    def _record_actual_usage(
        self,
        response_messages: Sequence[BaseMessage],
        outcome: CompressionOutcome,
    ) -> None:
        if outcome.revision <= 0:
            return
        response_message = next(
            (
                message
                for message in reversed(response_messages)
                if isinstance(message, AIMessage)
            ),
            None,
        )
        if response_message is None:
            return
        usage = _usage_tokens(response_message)
        if usage is None:
            return

        try:
            self.store.record_token_observation(
                TokenObservationCommand(
                    session_id=self.session_id,
                    revision=outcome.revision,
                    request_id=_request_id(response_message, outcome.revision),
                    estimated_input_tokens=outcome.tokens_after,
                    actual_input_tokens=usage[0],
                    actual_output_tokens=usage[1],
                )
            )
        except Exception:
            logger.exception("Failed to record conversation token usage")

    def get_snapshot(self) -> ConversationSummarySnapshot | None:
        return self.store.get_summary(self.session_id)
