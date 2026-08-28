from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import ConfigDict


# OpenAI-compatible providers expose a few different exception classes for
# the same network condition.  Keep the policy intentionally fail-closed:
# only errors that are unambiguously transient are allowed to switch from the
# cloud Planner to the local endpoint.  Authentication and request/parameter
# errors (the common 4xx cases) must remain visible to the caller.
_TRANSIENT_EXCEPTION_NAMES = frozenset(
    {
        "APIConnectionError",
        "APITimeoutError",
        "BadGatewayError",
        "ConnectError",
        "ConnectTimeout",
        "ConnectionError",
        "GatewayTimeoutError",
        "InternalServerError",
        "PoolTimeout",
        "RateLimitError",
        "ReadError",
        "ReadTimeout",
        "RemoteProtocolError",
        "ServiceUnavailableError",
        "Timeout",
        "TimeoutException",
        "TimeoutError",
        "TooManyRequestsError",
        "WriteError",
        "WriteTimeout",
    }
)
_NON_TRANSIENT_EXCEPTION_NAMES = frozenset(
    {
        "AuthenticationError",
        "BadRequestError",
        "CancelledError",
        "ConflictError",
        "NotFoundError",
        "PermissionDeniedError",
        "UnprocessableEntityError",
    }
)
_TRANSIENT_STATUS_CODES = frozenset({408, 409, 425, 429})


def _status_code(exc: BaseException) -> int | None:
    """Extract an HTTP status code from OpenAI/httpx-style exceptions."""

    value = getattr(exc, "status_code", None)
    if value is None:
        value = getattr(exc, "status", None)
    if value is None:
        response = getattr(exc, "response", None)
        value = getattr(response, "status_code", None)
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return int(value)


def _is_transient_exception(
    exc: BaseException,
    *,
    _seen: set[int] | None = None,
) -> bool:
    """Return whether a model error is safe to handle with local fallback.

    The status code takes precedence over the class name.  This prevents an
    exception with a misleading ``*Error`` name from silently bypassing a
    deterministic 4xx request/authentication failure.  Cause/context are
    inspected only when the outer exception does not carry a decision.
    """

    status_code = _status_code(exc)
    if status_code is not None:
        if status_code >= 500 or status_code in _TRANSIENT_STATUS_CODES:
            return True
        if 400 <= status_code < 500:
            return False

    exception_name = type(exc).__name__
    if exception_name in _NON_TRANSIENT_EXCEPTION_NAMES:
        return False
    if exception_name in _TRANSIENT_EXCEPTION_NAMES:
        return True

    # A few HTTP clients wrap a timeout/connection error in a generic error.
    # Follow the causal chain, while guarding against malformed cyclic causes.
    seen = _seen if _seen is not None else set()
    marker = id(exc)
    if marker in seen:
        return False
    seen.add(marker)
    for nested in (getattr(exc, "__cause__", None), getattr(exc, "__context__", None)):
        if nested is not None and _is_transient_exception(nested, _seen=seen):
            return True
    return False


class LocalFirstChatModel(BaseChatModel):
    """Use a local OpenAI-compatible chat model and fall back to cloud.

    The wrapper deliberately implements ``bind_tools`` itself. LangChain binds
    tools after the Agent is created, so wrapping only ``invoke`` would leave
    the Planner unable to expose its tool schema to either endpoint.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    primary: Any
    fallback: Any
    role: str = "planner"
    last_route: dict[str, object] | None = None
    disable_streaming: bool = True

    @property
    def _llm_type(self) -> str:
        return "localrag-local-first"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        del run_manager
        try:
            response = self._invoke(self.primary, messages, stop=stop, **kwargs)
            route = {
                "role": self.role,
                "route": "local",
                "fallback_used": False,
                "fallback_reason": "",
            }
        except Exception as exc:
            response = self._invoke(self.fallback, messages, stop=stop, **kwargs)
            route = {
                "role": self.role,
                "route": "cloud",
                "fallback_used": True,
                "fallback_reason": type(exc).__name__,
            }
        self.last_route = route
        message = self._as_ai_message(response, route)
        return ChatResult(generations=[ChatGeneration(message=message)])

    @staticmethod
    def _invoke(
        model: object,
        messages: Sequence[BaseMessage],
        *,
        stop: Sequence[str] | None,
        **kwargs: Any,
    ) -> object:
        invoke = getattr(model, "invoke")
        options = dict(kwargs)
        if stop is not None:
            options["stop"] = list(stop)
        return invoke(list(messages), **options)

    @staticmethod
    def _as_ai_message(
        response: object, route: Mapping[str, object]
    ) -> AIMessage:
        if isinstance(response, AIMessage):
            metadata = dict(response.response_metadata)
            metadata["localrag_route"] = dict(route)
            return response.model_copy(update={"response_metadata": metadata})
        content = getattr(response, "content", response)
        if not isinstance(content, (str, list)):
            content = str(content)
        return AIMessage(
            content=content,
            response_metadata={"localrag_route": dict(route)},
        )

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Callable[..., Any]],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> LocalFirstChatModel:
        primary = self.primary.bind_tools(
            tools,
            tool_choice=tool_choice,
            **kwargs,
        )
        fallback = self.fallback.bind_tools(
            tools,
            tool_choice=tool_choice,
            **kwargs,
        )
        return LocalFirstChatModel(
            primary=primary,
            fallback=fallback,
            role=self.role,
        )


class CloudFirstChatModel(LocalFirstChatModel):
    """Use the cloud Planner first and fail over only on transient errors.

    The local model is deliberately opt-in at the provider-factory layer: it
    is used only when its tool-calling capability has been verified.  Keeping
    this wrapper as a ``BaseChatModel`` means LangChain's Agent can bind tools
    once and retain the same schema on both cloud and local clients.
    """

    @property
    def _llm_type(self) -> str:
        return "localrag-cloud-first"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        del run_manager
        try:
            response = self._invoke(self.primary, messages, stop=stop, **kwargs)
            route = {
                "role": self.role,
                "route": "cloud",
                "fallback_used": False,
                "fallback_reason": "",
            }
        except Exception as exc:
            if not _is_transient_exception(exc):
                raise
            response = self._invoke(self.fallback, messages, stop=stop, **kwargs)
            route = {
                "role": self.role,
                "route": "local",
                "fallback_used": True,
                "fallback_reason": type(exc).__name__,
            }
        self.last_route = route
        message = self._as_ai_message(response, route)
        return ChatResult(generations=[ChatGeneration(message=message)])

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Callable[..., Any]],
        *,
        tool_choice: str | None = None,
        **kwargs: Any,
    ) -> CloudFirstChatModel:
        primary = self.primary.bind_tools(
            tools,
            tool_choice=tool_choice,
            **kwargs,
        )
        fallback = self.fallback.bind_tools(
            tools,
            tool_choice=tool_choice,
            **kwargs,
        )
        return CloudFirstChatModel(
            primary=primary,
            fallback=fallback,
            role=self.role,
        )
