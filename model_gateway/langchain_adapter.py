from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import Runnable

from .gateway import LocalModelGateway, RoutedResponse
from .models import GatewayResponse, GatewayRequestContext, GatewayUsage, ModelPurpose


class LocalGatewayChatModel(Runnable):
    """Adapt the local gateway to a LangChain chat model without tool calls."""

    def __init__(self, gateway: LocalModelGateway, fallback_model: object) -> None:
        if not callable(getattr(gateway, "complete", None)):
            raise TypeError("gateway must provide complete")
        if not callable(getattr(fallback_model, "invoke", None)):
            raise TypeError("fallback_model must provide invoke")
        self.gateway = gateway
        self.fallback_model = fallback_model
        self.last_route: dict[str, object] | None = None

    def invoke(self, input: Any, config: Any | None = None, **kwargs: Any) -> AIMessage:
        messages = _to_openai_messages(input)
        configurable = (
            config.get("configurable", {})
            if isinstance(config, Mapping)
            else {}
        )
        if not isinstance(configurable, Mapping):
            configurable = {}
        request_id = uuid4().hex
        context = GatewayRequestContext(
            request_id=request_id,
            purpose=ModelPurpose.RAG_GENERATION,
            session_id=str(configurable.get("session_id", "") or ""),
            task_id=str(configurable.get("task_id", "") or ""),
            run_id=str(configurable.get("run_id", "") or ""),
        )

        def fallback() -> GatewayResponse:
            return _invoke_cloud_fallback(
                self.fallback_model,
                input,
                config,
                request_id,
                kwargs,
            )

        result = self.gateway.complete(
            messages,
            context=context,
            fallback=fallback,
            temperature=float(kwargs.get("temperature", 0.0)),
            max_tokens=int(kwargs.get("max_tokens", 256)),
        )
        route = _route_metadata(result)
        self.last_route = route
        return AIMessage(content=result.text, response_metadata={"localrag_route": route})


def _to_openai_messages(value: object) -> list[dict[str, str]]:
    if hasattr(value, "to_messages"):
        messages = value.to_messages()
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        messages = value
    else:
        messages = [value]
    converted = []
    for message in messages:
        role: object
        content: object
        if isinstance(message, BaseMessage):
            role = _message_role(message)
            content = _message_content(message)
        elif isinstance(message, Mapping):
            role = message.get("role")
            content = message.get("content")
        else:
            role = "user"
            content = str(message)
        if role not in {"system", "user", "assistant"}:
            raise ValueError("local RAG gateway does not accept tool messages")
        if not isinstance(content, str) or not content:
            raise ValueError("chat message content must be non-empty text")
        converted.append({"role": role, "content": content})
    if not converted:
        raise ValueError("chat messages must not be empty")
    return converted


def _message_role(message: BaseMessage) -> str:
    if message.type == "system":
        return "system"
    if message.type == "ai":
        return "assistant"
    if message.type == "human":
        return "user"
    return "tool"


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


def _invoke_cloud_fallback(
    model: object,
    input: object,
    config: object,
    request_id: str,
    kwargs: Mapping[str, object],
) -> GatewayResponse:
    invoke = getattr(model, "invoke")
    try:
        response = invoke(input, config=config)
    except TypeError:
        response = invoke(input)
    text = response if isinstance(response, str) else _response_content(response)
    metadata = getattr(response, "response_metadata", {})
    if not isinstance(metadata, Mapping):
        metadata = {}
    usage_data = metadata.get("token_usage") or metadata.get("usage") or {}
    usage = GatewayUsage(
        _non_negative_int(usage_data.get("prompt_tokens", 0)),
        _non_negative_int(usage_data.get("completion_tokens", 0)),
        _non_negative_int(usage_data.get("total_tokens", 0)),
    ) if isinstance(usage_data, Mapping) else GatewayUsage(0, 0, 0)
    model_name = str(
        metadata.get("model_name")
        or metadata.get("model")
        or getattr(model, "model_name", None)
        or "cloud"
    )
    del kwargs
    return GatewayResponse(
        text=text,
        model=model_name,
        usage=usage,
        request_id=request_id,
        backend="cloud",
        quantization="none",
    )


def _response_content(response: object) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, Mapping) else str(item)
            for item in content
        )
    return str(content)


def _route_metadata(result: RoutedResponse) -> dict[str, object]:
    usage = result.usage
    return {
        "request_id": result.request_id,
        "primary_model": result.primary_model,
        "actual_model": result.actual_model,
        "backend": result.backend,
        "quantization": result.quantization,
        "fallback_used": result.fallback_used,
        "fallback_reason": result.fallback_reason,
        "attempt_count": result.attempt_count,
        "input_tokens": getattr(usage, "prompt_tokens", 0),
        "output_tokens": getattr(usage, "completion_tokens", 0),
        "ttft_seconds": result.ttft_seconds,
        "latency_seconds": result.latency_seconds,
    }


def _non_negative_int(value: object) -> int:
    return value if type(value) is int and value >= 0 else 0
