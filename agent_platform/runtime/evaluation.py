"""Fixed-task and long-session release evaluation records for D30."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class EvaluationResult:
    task_count: int
    passed: int
    long_sessions: int
    compression_followups: int
    evaluation_requested: bool = True

    @property
    def completion_rate(self) -> float:
        return self.passed / self.task_count if self.task_count else 0.0

    def validate(self) -> None:
        if self.task_count < 1 or not 0 <= self.passed <= self.task_count: raise ValueError("invalid task counts")
        if self.long_sessions < 0 or self.compression_followups < 0: raise ValueError("evaluation counts must be non-negative")
