"""Deterministic replay and fault-injection records for D29."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class FaultCase:
    name: str
    injected_at: str
    expected_state: str

class ReplayHarness:
    def __init__(self, cases: tuple[FaultCase, ...]) -> None: self.cases = cases
    def validate(self) -> None:
        if not self.cases: raise ValueError("fault matrix must not be empty")
        if any(not case.expected_state.strip() for case in self.cases): raise ValueError("expected state is required")
    def replay(self, case_name: str) -> FaultCase:
        self.validate()
        for case in self.cases:
            if case.name == case_name: return case
        raise KeyError(case_name)
