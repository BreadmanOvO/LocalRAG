from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Annotated, Any

from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ModelCallLimitMiddleware,
    ToolCallLimitMiddleware,
)
from langchain.agents.middleware.types import PrivateStateAttr
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.channels.untracked_value import UntrackedValue
from typing_extensions import NotRequired, override


LIMIT_EXIT_BEHAVIOR = "error"


class ExecutionGuardState(AgentState):
    run_tool_call_signatures: NotRequired[
        Annotated[tuple[str, ...], UntrackedValue, PrivateStateAttr]
    ]
    run_processed_tool_call_ids: NotRequired[
        Annotated[tuple[str, ...], UntrackedValue, PrivateStateAttr]
    ]
    run_progress_fingerprints: NotRequired[
        Annotated[tuple[str, ...], UntrackedValue, PrivateStateAttr]
    ]
    run_progress_token: NotRequired[Annotated[str, UntrackedValue, PrivateStateAttr]]
    run_no_progress_count: NotRequired[Annotated[int, UntrackedValue, PrivateStateAttr]]


class DuplicateToolCallError(Exception):
    def __init__(self, tool_name: str, signature: str) -> None:
        self.tool_name = tool_name
        self.signature = signature
        super().__init__(f"Duplicate tool call blocked: {tool_name}")


class NoProgressLimitExceededError(Exception):
    def __init__(self, count: int, limit: int) -> None:
        self.count = count
        self.limit = limit
        super().__init__(f"No progress limit reached: {count}/{limit}")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _tool_call_signature(tool_call: dict[str, Any], plan_revision: int) -> str:
    return _digest(
        {
            "tool_name": str(tool_call.get("name") or "unknown"),
            "arguments": tool_call.get("args") or {},
            "plan_revision": plan_revision,
        }
    )


def _source_progress_fingerprints(message: ToolMessage) -> tuple[str, ...]:
    if getattr(message, "status", None) == "error":
        return ()
    artifact = getattr(message, "artifact", None)
    observations = artifact.get("source_observations") if isinstance(artifact, dict) else None
    if not isinstance(observations, list) or not observations:
        return ()
    identities = (
        {
            field: observation.get(field)
            for field in (
                "source_id",
                "locator",
                "chunk_order",
                "chunk_strategy",
                "evidence_status",
            )
        }
        for observation in observations
        if isinstance(observation, dict)
    )
    return tuple(_digest(identity) for identity in identities)


class ExecutionGuardMiddleware(AgentMiddleware):
    state_schema = ExecutionGuardState

    def __init__(
        self,
        *,
        duplicate_tool_call_detection: bool,
        no_progress_limit: int | None,
        progress_token: Callable[[], Any] | None = None,
    ) -> None:
        super().__init__()
        self.duplicate_tool_call_detection = duplicate_tool_call_detection
        self.no_progress_limit = no_progress_limit
        self.progress_token = progress_token

    def _current_progress_token(self) -> str:
        return _digest(self.progress_token()) if self.progress_token is not None else ""

    @staticmethod
    def _updated_tool_call_signatures(
        state: ExecutionGuardState,
        tool_calls: list[dict[str, Any]],
    ) -> tuple[str, ...]:
        seen_signatures = list(state.get("run_tool_call_signatures", ()))
        plan_revision = int(state.get("plan_revision", 0))
        for tool_call in tool_calls:
            signature = _tool_call_signature(tool_call, plan_revision)
            if signature in seen_signatures:
                raise DuplicateToolCallError(
                    str(tool_call.get("name") or "unknown"),
                    signature,
                )
            seen_signatures.append(signature)
        return tuple(seen_signatures)

    def _progress_updates(
        self,
        state: ExecutionGuardState,
        messages: list[Any],
    ) -> dict[str, Any]:
        if self.no_progress_limit is None:
            return {}

        processed_ids = set(state.get("run_processed_tool_call_ids", ()))
        progress_fingerprints = set(state.get("run_progress_fingerprints", ()))
        tool_messages = [
            message
            for message in messages
            if isinstance(message, ToolMessage)
        ]
        current_token = self._current_progress_token()
        previous_token = state.get("run_progress_token")
        if previous_token is None:
            processed_ids.update(str(message.tool_call_id) for message in tool_messages)
            new_tool_messages = []
        else:
            new_tool_messages = [
                message
                for message in tool_messages
                if str(message.tool_call_id) not in processed_ids
            ]
        made_progress = previous_token is not None and current_token != previous_token

        for message in new_tool_messages:
            for fingerprint in _source_progress_fingerprints(message):
                if fingerprint not in progress_fingerprints:
                    made_progress = True
                    progress_fingerprints.add(fingerprint)
            processed_ids.add(str(message.tool_call_id))

        no_progress_count = int(state.get("run_no_progress_count", 0))
        if new_tool_messages:
            no_progress_count = 0 if made_progress else no_progress_count + 1
            if no_progress_count >= self.no_progress_limit:
                raise NoProgressLimitExceededError(
                    no_progress_count,
                    self.no_progress_limit,
                )

        return {
            "run_processed_tool_call_ids": tuple(sorted(processed_ids)),
            "run_progress_fingerprints": tuple(sorted(progress_fingerprints)),
            "run_progress_token": current_token,
            "run_no_progress_count": no_progress_count,
        }

    @override
    def after_model(self, state: ExecutionGuardState, runtime) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        last_ai_message = next(
            (message for message in reversed(messages) if isinstance(message, AIMessage)),
            None,
        )
        if last_ai_message is None or not last_ai_message.tool_calls:
            return None

        updates: dict[str, Any] = {}
        if self.duplicate_tool_call_detection:
            updates["run_tool_call_signatures"] = self._updated_tool_call_signatures(
                state,
                last_ai_message.tool_calls,
            )
        updates.update(self._progress_updates(state, messages))
        return updates or None

    async def aafter_model(self, state: ExecutionGuardState, runtime) -> dict[str, Any] | None:
        return self.after_model(state, runtime)


@dataclass(frozen=True)
class AgentExecutionBudget:
    """Hard per-run limits applied by the Agent graph."""

    tool_call_limit: int = 3
    model_call_limit: int = 4
    duplicate_tool_call_detection: bool = True
    no_progress_limit: int | None = 2
    recursion_limit: int = 28

    def __post_init__(self) -> None:
        for field_name in ("tool_call_limit", "model_call_limit", "recursion_limit"):
            if getattr(self, field_name) <= 0:
                raise ValueError(f"{field_name} must be greater than zero")
        if self.no_progress_limit is not None and self.no_progress_limit <= 0:
            raise ValueError("no_progress_limit must be greater than zero")

    def build_middleware(
        self,
        *,
        progress_token: Callable[[], Any] | None = None,
        prefix: Sequence[AgentMiddleware] = (),
    ) -> list[AgentMiddleware]:
        if isinstance(prefix, (str, bytes, bytearray)) or not isinstance(prefix, Sequence):
            raise TypeError("prefix must be a sequence of AgentMiddleware values")
        if not all(isinstance(item, AgentMiddleware) for item in prefix):
            raise TypeError("prefix must contain only AgentMiddleware values")

        middleware = list(prefix)
        if self.duplicate_tool_call_detection or self.no_progress_limit is not None:
            middleware.append(
                ExecutionGuardMiddleware(
                    duplicate_tool_call_detection=self.duplicate_tool_call_detection,
                    no_progress_limit=self.no_progress_limit,
                    progress_token=progress_token,
                )
            )
        middleware.extend(
            [
                ToolCallLimitMiddleware(
                    run_limit=self.tool_call_limit,
                    exit_behavior=LIMIT_EXIT_BEHAVIOR,
                ),
                ModelCallLimitMiddleware(
                    run_limit=self.model_call_limit,
                    exit_behavior=LIMIT_EXIT_BEHAVIOR,
                ),
            ]
        )
        return middleware

    def to_manifest(self) -> dict:
        return {
            "middleware": [type(item).__name__ for item in self.build_middleware()],
            "tool_call_run_limit": self.tool_call_limit,
            "model_call_run_limit": self.model_call_limit,
            "duplicate_tool_call_detection": self.duplicate_tool_call_detection,
            "no_progress_limit": self.no_progress_limit,
            "limit_exit_behavior": LIMIT_EXIT_BEHAVIOR,
            "recursion_limit": self.recursion_limit,
        }


DEFAULT_AGENT_EXECUTION_BUDGET = AgentExecutionBudget()
