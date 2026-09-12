"""Release readiness checks for D31-D33."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Readiness:
    security: bool
    accessibility: bool
    deployment: bool
    backup_restore: bool
    critical_failures: int = 0

    def decision(self) -> str:
        return "go" if all((self.security, self.accessibility, self.deployment, self.backup_restore)) and self.critical_failures == 0 else "no-go"

    def blockers(self) -> tuple[str, ...]:
        items = []
        if not self.security: items.append("security")
        if not self.accessibility: items.append("accessibility")
        if not self.deployment: items.append("deployment")
        if not self.backup_restore: items.append("backup_restore")
        if self.critical_failures: items.append("critical_failures")
        return tuple(items)
