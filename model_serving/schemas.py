from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ToolCallFunction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    arguments: str = Field(max_length=200000)


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, max_length=128)
    type: Literal["function"] = "function"
    function: ToolCallFunction


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = Field(default=None, max_length=200000)
    name: str | None = Field(default=None, min_length=1, max_length=128)
    tool_call_id: str | None = Field(default=None, min_length=1, max_length=128)
    tool_calls: list[ToolCall] | None = Field(default=None, max_length=64)

    @model_validator(mode="after")
    def validate_role_fields(self) -> ChatMessage:
        has_content = isinstance(self.content, str) and bool(self.content)
        if self.role in {"system", "user"} and not has_content:
            raise ValueError("system and user messages require content")
        if self.role == "tool":
            if not has_content or not self.tool_call_id:
                raise ValueError("tool messages require content and tool_call_id")
        if self.role == "assistant" and not has_content and not self.tool_calls:
            raise ValueError("assistant messages require content or tool_calls")
        if self.role != "assistant" and self.tool_calls is not None:
            raise ValueError("tool_calls are only valid on assistant messages")
        if self.role != "tool" and self.tool_call_id is not None:
            raise ValueError("tool_call_id is only valid on tool messages")
        return self


class RequestMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str | None = Field(default=None, min_length=1, max_length=128)
    task_id: str | None = Field(default=None, min_length=1, max_length=128)
    run_id: str | None = Field(default=None, min_length=1, max_length=128)


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(min_length=1, max_length=128)
    messages: list[ChatMessage] = Field(min_length=1, max_length=512)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=256, ge=1)
    stream: bool = False
    purpose: Literal["agent_planning", "rag_generation", "conversation_summary"]
    metadata: RequestMetadata = Field(default_factory=RequestMetadata)
    tools: list[dict[str, Any]] = Field(default_factory=list, max_length=64)
    tool_choice: str | dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_tools(self) -> ChatCompletionRequest:
        if self.tools and self.purpose != "agent_planning":
            raise ValueError("tools are only accepted for agent planning")
        if self.tool_choice is not None and not self.tools:
            raise ValueError("tool_choice requires tools")
        for tool in self.tools:
            if (
                not isinstance(tool, dict)
                or tool.get("type") != "function"
                or not isinstance(tool.get("function"), dict)
                or not isinstance(tool["function"].get("name"), str)
                or not tool["function"]["name"]
            ):
                raise ValueError("invalid function tool definition")
        return self
