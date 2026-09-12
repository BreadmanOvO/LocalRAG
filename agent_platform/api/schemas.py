"""Pydantic wire models for the v1.8 API boundary."""

from __future__ import annotations

from datetime import datetime
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


class HealthResponse(BaseModel):
    status: str
    contract: str


class RoomResponse(BaseModel):
    space_id: str
    room_id: str
    title: str
    status: Literal["active", "archived", "deleted"]
    room_sequence: int
    row_version: int


class MessageResponse(BaseModel):
    message_id: str
    room_id: str
    content: str
    role: Literal["user", "assistant", "system", "tool"]
    status: str
    room_sequence: int
    idempotency_key: str | None
    content_sha256: str
    created_at: datetime | None


class MessageListResponse(BaseModel):
    items: list[MessageResponse]


class EventIdentityResponse(BaseModel):
    room_id: str
    event_id: str
    room_sequence: int


class EventResponse(BaseModel):
    identity: EventIdentityResponse
    event_type: str
    room_id: str
    task_id: str | None
    run_id: str | None
    step_id: str | None
    attempt_id: str | None
    run_sequence: int
    caused_by: list[str]
    consumes: list[str]
    produces: list[str]
    usage: dict[str, int]
    payload: dict[str, Any]
    timestamp: str


class EventListResponse(BaseModel):
    items: list[EventResponse]
    next: int


class TaskResponse(BaseModel):
    task_id: str
    room_id: str
    title: str
    status: str
    version: int
    active_run_id: str | None


class FollowupResponse(BaseModel):
    task: TaskResponse
    message: MessageResponse
    status: Literal["accepted"]
    run_id: str | None


class RunResponse(BaseModel):
    run_id: str
    plan_revision: int
    status: str
    control_epoch: int
    row_version: int


class CommandResponse(BaseModel):
    command_id: str
    status: Literal["accepted"]
    run: RunResponse
