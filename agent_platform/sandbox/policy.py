"""Sandbox policy checks for D25; policy only, no fake isolation claim."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SandboxPolicy:
    allowed_paths: tuple[str, ...] = ()
    allow_network: bool = False
    allow_credentials: bool = False
    memory_mb: int = 512
    timeout_seconds: int = 60

    def validate(self, path: str, *, network: bool = False, credentials: bool = False) -> None:
        if self.allowed_paths and not any(path.startswith(root) for root in self.allowed_paths): raise PermissionError("path outside sandbox policy")
        if network and not self.allow_network: raise PermissionError("network disabled by sandbox policy")
        if credentials and not self.allow_credentials: raise PermissionError("credentials disabled by sandbox policy")
        if self.memory_mb < 1 or self.timeout_seconds < 1: raise ValueError("resource limits must be positive")
