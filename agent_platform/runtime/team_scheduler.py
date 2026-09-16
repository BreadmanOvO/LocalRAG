"""Bounded DAG execution for cloud-model steps (not side-effecting tools).

Ownership and transitions live here, never in model-generated prose. The
caller persists every transition before further work through ``emit``.
"""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field, replace
from threading import RLock
from time import monotonic, sleep
from typing import Any, Callable

from .context_engineering import build_handoff_packet
from .error_details import serialize_exception


class CircuitOpenError(RuntimeError):
    pass


def exhausted_quota(exc: Exception) -> bool:
    body = getattr(exc, "body", None)
    if not isinstance(body, dict):
        return False
    error = body.get("error", body)
    return isinstance(error, dict) and error.get("code") in {"insufficient_quota", "quota_exceeded", "billing_hard_limit_reached"}


def transient_error(exc: Exception) -> bool:
    """Retry transport/server failures, never credentials or arbitrary bugs."""
    if exhausted_quota(exc):
        return False
    status = getattr(exc, "status_code", None)
    return isinstance(exc, (TimeoutError, ConnectionError)) or status in {408, 429, 500, 502, 503, 504} or type(exc).__name__ in {"APITimeoutError", "APIConnectionError"}


class ModelCircuitBreaker:
    """Process-local, shared across rooms; one probe after the cooldown."""

    def __init__(self, threshold: int = 3, cooldown: float = 30, clock=monotonic):
        self.threshold, self.cooldown, self.clock = threshold, cooldown, clock
        self._lock = RLock()
        self._states: dict[tuple, tuple[int, float, bool]] = {}

    def acquire(self, key: tuple) -> bool:
        with self._lock:
            count, opened, probing = self._states.get(key, (0, 0, False))
            if count < self.threshold:
                return False
            if probing or self.clock() - opened < self.cooldown:
                raise CircuitOpenError("模型服务暂时熔断，请稍后重试")
            self._states[key] = (count, opened, True)
            return True

    def success(self, key: tuple, probe: bool) -> None:
        with self._lock:
            count, _, _ = self._states.get(key, (0, 0, False))
            # An old in-flight request must not close a newer open circuit.
            if probe or count < self.threshold:
                self._states.pop(key, None)

    def failure(self, key: tuple, probe: bool) -> None:
        with self._lock:
            count, opened, probing = self._states.get(key, (0, 0, False))
            count += 1
            if count == self.threshold or probe:
                opened, probing = self.clock(), False
            self._states[key] = (count, opened, probing)


@dataclass(frozen=True)
class TeamStep:
    sequence: int
    agent_id: str
    title: str
    dependencies: tuple[int, ...]
    prompt: Callable[[dict[int, Any]], str] = field(repr=False)
    final_output: bool = False


class TeamStepScheduler:
    """One run, fixed model bindings, dependency gates and bounded attempts.

    The dispatcher alone claims a ready step. Each Future owns one claim;
    failed dependencies block descendants while independent siblings finish.
    There is deliberately no whole-run automatic retry.
    """

    def __init__(self, *, emit, invoke, on_turn=None, check_active=lambda: None, max_attempts=2, backoff=0.5):
        self.emit, self.invoke, self.on_turn = emit, invoke, on_turn
        self.check_active = check_active
        self.max_attempts, self.backoff = max_attempts, backoff
        self.states: dict[int, str] = {}
        self.outputs: dict[int, Any] = {}

    @staticmethod
    def validate(steps: list[TeamStep]) -> None:
        ids = {step.sequence for step in steps}
        if not steps or len(steps) > 32 or len(ids) != len(steps):
            raise ValueError("team plan must have 1–32 unique steps")
        done: set[int] = set()
        while len(done) < len(ids):
            ready = {s.sequence for s in steps if set(s.dependencies) <= done} - done
            if not ready:
                raise ValueError("team plan contains a cycle or unknown dependency")
            done.update(ready)

    def _attempt(self, step: TeamStep, prompt: str):
        for attempt in range(1, self.max_attempts + 1):
            self.check_active()
            try:
                return self.invoke(step.agent_id, prompt, step.sequence)
            except Exception as exc:
                if not transient_error(exc) or attempt == self.max_attempts:
                    raise
                self.emit("step_retrying", {"agent_id": step.agent_id, "sequence": step.sequence,
                    "attempt": attempt, "next_attempt": attempt + 1, "error": type(exc).__name__})
                sleep(self.backoff * 2 ** (attempt - 1))
        raise AssertionError("unreachable")

    def execute(self, steps: list[TeamStep], *, completed_turns=None) -> list[Any]:
        self.validate(steps)
        self.states = {s.sequence: "waiting" for s in steps}
        self.outputs = dict(completed_turns or {})
        for step in steps:
            if step.sequence in self.outputs:
                turn = self.outputs[step.sequence]
                if turn.agent_id != step.agent_id or not set(step.dependencies) <= self.outputs.keys():
                    raise ValueError("checkpoint does not match execution plan")
                if hasattr(turn, "is_final"):
                    turn = replace(turn, is_final=step.final_output)
                    self.outputs[step.sequence] = turn
                self.states[step.sequence] = "completed"
                if self.on_turn:
                    self.on_turn(turn)
                self.emit("step_reused", {"agent_id": step.agent_id, "sequence": step.sequence})
        failures: list[Exception] = []
        futures = {}
        with ThreadPoolExecutor(max_workers=min(8, len(steps)), thread_name_prefix="team-step") as pool:
            while any(state in {"waiting", "running"} for state in self.states.values()):
                for step in steps:
                    if self.states[step.sequence] != "waiting":
                        continue
                    if any(self.states[d] in {"failed", "blocked"} for d in step.dependencies):
                        self.states[step.sequence] = "blocked"
                        self.emit("step_blocked", {"agent_id": step.agent_id, "sequence": step.sequence,
                            "error": "上游步骤未完成", "dependencies": list(step.dependencies)})
                        continue
                    if not all(self.states[d] == "completed" for d in step.dependencies):
                        continue
                    try:
                        self.check_active()
                    except Exception as exc:
                        self.states[step.sequence] = "blocked"
                        failures.append(exc)
                        self.emit("step_blocked", {"agent_id": step.agent_id, "sequence": step.sequence, "error": "任务已停止或暂停"})
                        continue
                    sources = {d: self.outputs[d] for d in step.dependencies}
                    inputs = {
                        sequence: build_handoff_packet(source, target_agent_id=step.agent_id, task=step.title)
                        for sequence, source in sources.items()
                    }
                    self.states[step.sequence] = "running"
                    self.emit("step_claimed", {"agent_id": step.agent_id, "sequence": step.sequence, "title": step.title})
                    for packet in inputs.values():
                        self.emit("handoff_created", {
                            "agent_id": step.agent_id,
                            "from_agent_id": packet.source_agent_id,
                            "to_agent_id": step.agent_id,
                            "source_sequence": packet.source_sequence,
                            "sequence": step.sequence,
                            "summary": packet.summary,
                            "handoff_packet": packet.public(),
                            "shared_output": packet.render(),
                        })
                    if inputs:
                        self.emit("handoff_accepted", {"agent_id": step.agent_id, "sequence": step.sequence, "source_sequences": list(inputs)})
                    futures[pool.submit(self._attempt, step, step.prompt(inputs))] = step
                if not futures:
                    continue
                completed, _ = wait(futures, return_when=FIRST_COMPLETED)
                for future in completed:
                    step = futures.pop(future)
                    try:
                        turn = future.result()
                        if hasattr(turn, "is_final"):
                            turn = replace(turn, is_final=step.final_output)
                        self.check_active()
                        if self.on_turn:
                            self.on_turn(turn)
                        self.outputs[step.sequence] = turn
                        self.states[step.sequence] = "completed"
                    except Exception as exc:
                        self.states[step.sequence] = "failed"
                        failures.append(exc)
                        self.emit("step_failed", {"agent_id": step.agent_id, "sequence": step.sequence, **serialize_exception(exc, phase="step_execution", agent_id=step.agent_id), "error": type(exc).__name__, "terminal": True})
        if failures:
            raise failures[0]
        return [self.outputs[s.sequence] for s in steps]
