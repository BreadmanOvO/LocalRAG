from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import ConfigDict


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
