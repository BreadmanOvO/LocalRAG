"""Explicit modality and provider capability registry for D22."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Capability:
    capability_id: str
    modality: str
    provider: str
    cost_units: int = 1

class CapabilityRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Capability] = {}
    def register(self, capability: Capability) -> Capability:
        if capability.cost_units < 0: raise ValueError("cost_units must be non-negative")
        self._items[capability.capability_id] = capability
        return capability
    def require(self, capability_id: str) -> Capability:
        try: return self._items[capability_id]
        except KeyError as exc: raise ValueError(f"capability unavailable: {capability_id}") from exc
    def list(self, modality: str | None = None) -> tuple[Capability, ...]:
        return tuple(item for item in self._items.values() if modality is None or item.modality == modality)
