"""Route coverage matrix for D27."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RouteCase:
    name: str
    architecture: str
    expected_mode: str
    outcome: str

class RouteCoverage:
    def __init__(self, cases: tuple[RouteCase, ...]) -> None: self.cases = cases
    def validate(self) -> None:
        if not self.cases: raise ValueError("route matrix must not be empty")
        for case in self.cases:
            if case.expected_mode not in {"direct", "delegate"}: raise ValueError("unsupported expected mode")
            if not case.outcome.strip(): raise ValueError("route outcome must be recorded")
    def summary(self) -> dict[str, int]:
        self.validate(); return {"cases": len(self.cases), "direct": sum(c.expected_mode == "direct" for c in self.cases), "delegate": sum(c.expected_mode == "delegate" for c in self.cases)}
