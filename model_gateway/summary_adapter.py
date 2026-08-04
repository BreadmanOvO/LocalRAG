from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from uuid import uuid4

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from agent.context.compressor import (
    SUMMARY_JSON_SCHEMA,
    SummaryClientResult,
    SummaryRequest,
    parse_and_validate_summary,
)
from agent.context.models import ConversationCompressionError, ConversationSummary

from .gateway import GatewayFallbackError, LocalModelGateway, RoutedResponse
from .models import (
    GatewayError,
    GatewayRequestContext,
    GatewayResponse,
    GatewayUsage,
    ModelPurpose,
)


SummaryValidator = Callable[[Mapping[str, object], SummaryRequest], object]

_SUMMARY_SYSTEM_PROMPT = (
    "Summarize the supplied conversation for a later assistant turn. "
    "Preserve constraints, confirmed findings, decisions, unresolved questions, "
    "failed attempts, and source/evidence identities. Never invent IDs. "
    "Return exactly one JSON object and no markdown. The object must conform to "
    f"this JSON schema: {json.dumps(SUMMARY_JSON_SCHEMA, sort_keys=True, separators=(',', ':'))}"
)


def _message_content(message: BaseMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, Mapping) else str(item)
            for item in content
        )
    return str(content)


def _summary_payload(summary: ConversationSummary | None) -> object:
    if summary is None:
        return None
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


def _prompt_messages(request: SummaryRequest) -> list[BaseMessage]:
    payload = {
        "previous_summary": _summary_payload(request.previous_summary),
        "messages": [
            {
                "role": (
                    "system"
                    if message.type == "system"
                    else "assistant"
                    if message.type == "ai"
                    else "tool"
                    if message.type == "tool"
                    else "user"
                ),
                "content": _message_content(message),
            }
            for message in request.messages
        ],
        "allowed_evidence_ids": sorted(request.allowed_evidence_ids),
        "allowed_source_ids": sorted(request.allowed_source_ids),
        "input_token_limit": request.input_token_limit,
    }
    return [
        SystemMessage(content=_SUMMARY_SYSTEM_PROMPT),
        HumanMessage(
            content=json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        ),
    ]


def _parse_payload(text: str) -> Mapping[str, object]:
    try:
        payload = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("summary response must be a JSON object") from exc
    if not isinstance(payload, Mapping):
        raise ValueError("summary response must be a JSON object")
    return payload


def _response_text(response: object) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, Mapping) else str(item)
            for item in content
        )
    return str(content)


def _cloud_response(
    model: object,
    messages: Sequence[BaseMessage],
    request_id: str,
) -> GatewayResponse:
    invoke = getattr(model, "invoke")
    response = invoke(messages)
    metadata = getattr(response, "response_metadata", {})
    if not isinstance(metadata, Mapping):
        metadata = {}
    usage = getattr(response, "usage_metadata", None)
    if not isinstance(usage, Mapping):
        usage = metadata.get("token_usage") or metadata.get("usage") or {}
    if not isinstance(usage, Mapping):
        usage = {}

    def integer(*keys: str) -> int:
        for key in keys:
            value = usage.get(key)
            if type(value) is int and value >= 0:
                return value
        return 0

    prompt_tokens = integer("prompt_tokens", "input_tokens")
    completion_tokens = integer("completion_tokens", "output_tokens")
    total_tokens = integer("total_tokens") or prompt_tokens + completion_tokens
    model_name = str(
        metadata.get("model_name")
        or metadata.get("model")
        or getattr(model, "model_name", None)
        or "cloud"
    )
    return GatewayResponse(
        text=_response_text(response),
        model=model_name,
        usage=GatewayUsage(prompt_tokens, completion_tokens, total_tokens),
        request_id=request_id,
        backend="cloud",
        quantization="none",
    )


class LocalGatewaySummaryClient:
    """Adapt the local gateway to the structured conversation SummaryClient."""

    def __init__(
        self,
        gateway: LocalModelGateway,
        fallback_model: object,
        *,
        summary_validator: SummaryValidator = parse_and_validate_summary,
        task_id: str = "",
        run_id: str = "",
    ) -> None:
        if not callable(getattr(gateway, "complete", None)):
            raise TypeError("gateway must provide complete")
        if not callable(getattr(fallback_model, "invoke", None)):
            raise TypeError("fallback_model must provide invoke")
        if not callable(summary_validator):
            raise TypeError("summary_validator must be callable")
        self.gateway = gateway
        self.fallback_model = fallback_model
        self.summary_validator = summary_validator
        self.task_id = task_id
        self.run_id = run_id
        self.last_route: dict[str, object] | None = None

    def summarize(self, request: SummaryRequest) -> SummaryClientResult:
        if not isinstance(request, SummaryRequest):
            raise TypeError("request must be a SummaryRequest")
        messages = _prompt_messages(request)
        request_id = uuid4().hex
        context = GatewayRequestContext(
            request_id=request_id,
            purpose=ModelPurpose.CONVERSATION_SUMMARY,
            session_id=request.session_id,
            task_id=self.task_id,
            run_id=self.run_id,
        )

        def fallback() -> GatewayResponse:
            return _cloud_response(self.fallback_model, messages, request_id)

        def validate(text: str) -> None:
            self._validate_payload(text, request)

        try:
            result = self.gateway.complete(
                _gateway_messages(messages),
                context=context,
                fallback=fallback,
                response_validator=validate,
                temperature=0.0,
                max_tokens=2048,
            )
        except (GatewayFallbackError, GatewayError):
            raise ConversationCompressionError("summary clients failed") from None

        if not isinstance(result, RoutedResponse):
            raise TypeError("gateway must return RoutedResponse")
        route = {
            "request_id": result.request_id,
            "actual_model": result.actual_model,
            "fallback_used": result.fallback_used,
            "fallback_reason": result.fallback_reason,
        }
        self.last_route = route
        try:
            payload = self._validate_payload(result.text, request)
        except (TypeError, ValueError):
            raise ConversationCompressionError("summary clients failed") from None
        return SummaryClientResult(
            payload=payload,
            model_id=result.actual_model,
            fallback_reason=result.fallback_reason if result.fallback_used else "",
        )

    def _validate_payload(
        self,
        text: str,
        request: SummaryRequest,
    ) -> Mapping[str, object]:
        payload = _parse_payload(text)
        self.summary_validator(payload, request)
        return payload


def _gateway_messages(messages: Sequence[BaseMessage]) -> list[dict[str, str]]:
    return [
        {
            "role": "system" if message.type == "system" else "user",
            "content": _message_content(message),
        }
        for message in messages
    ]
