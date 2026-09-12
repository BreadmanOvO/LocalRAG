"""Pydantic wire models for the v1.8 API boundary."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class RoomCreateRequest(BaseModel):
    space_id: str = Field(min_length=1)
    title: str = ""
    room_id: str | None = None


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1)
    role: Literal["user", "assistant", "system", "tool"] = "user"
    message_id: str | None = None


class TaskCreateRequest(BaseModel):
    room_id: str
    title: str = Field(min_length=1)
    task_id: str | None = None


class FollowupRequest(BaseModel):
    content: str = Field(min_length=1)
    expected_task_version: int | None = Field(default=None, ge=1)


class RunCreateRequest(BaseModel):
    run_id: str | None = None
    task_id: str | None = None
    plan_revision: int = Field(default=1, ge=1)
    status: Literal["queued", "running"] = "queued"


class CommandRequest(BaseModel):
    action: Literal["start", "pause", "cancel"]
    run_id: str
    expected_row_version: int = Field(ge=1)
    expected_control_epoch: int | None = Field(default=None, ge=0)


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str
    control_epoch: int | None = None
    row_version: int | None = None
