"""P3 integration guard: compose capabilities through shared Runtime boundary."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class IntegrationCheck:
    architecture: str
    published_generation: str
    route_mode: str
    evaluation_requested: bool = False

class IntegrationGate:
    def validate(self, check: IntegrationCheck) -> None:
        if not check.architecture or not check.published_generation: raise ValueError("integration check is incomplete")
        if check.route_mode not in {"direct", "delegate"}: raise ValueError("invalid route mode")
    def publish_without_evaluation(self, generation_id: str) -> IntegrationCheck:
        check = IntegrationCheck("direct", generation_id, "direct", False); self.validate(check); return check
