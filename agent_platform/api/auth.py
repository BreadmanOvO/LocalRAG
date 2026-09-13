"""Small, dependency-free bearer authentication boundary for v1.8.

The API keeps identity and space authorization separate from business logic.
Tokens are supplied by deployment configuration (never persisted in events or
messages); this module only retains a hash-derived lookup in process memory.
It is intentionally a boundary adapter, not a user-management system.
"""

from __future__ import annotations

import hmac
import json
import os
from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Principal:
    subject: str
    spaces: frozenset[str]

    def can_access(self, space_id: str) -> bool:
        return "*" in self.spaces or space_id in self.spaces


class AuthConfigError(RuntimeError):
    """Raised when production authentication configuration is incomplete."""


class BearerAuthenticator:
    def __init__(self, tokens: Mapping[str, str | Sequence[str]]) -> None:
        if not tokens:
            raise AuthConfigError("auth tokens are required when authentication is enabled")
        self._tokens: dict[str, tuple[str, frozenset[str]]] = {}
        for raw_token, raw_spaces in tokens.items():
            token = str(raw_token).strip()
            if not token:
                raise AuthConfigError("auth token must not be empty")
            if isinstance(raw_spaces, str):
                spaces = (raw_spaces,)
            else:
                spaces = tuple(raw_spaces)
            normalized = frozenset(str(space).strip() for space in spaces if str(space).strip())
            if not normalized:
                raise AuthConfigError(f"auth token has no spaces: {token[:4]}…")
            digest = sha256(token.encode("utf-8")).hexdigest()
            self._tokens[digest] = (token, normalized)

    def authenticate(self, token: str | None) -> Principal | None:
        if not token:
            return None
        digest = sha256(token.encode("utf-8")).hexdigest()
        for known_digest, (known_token, spaces) in self._tokens.items():
            if hmac.compare_digest(digest, known_digest) and hmac.compare_digest(token, known_token):
                return Principal(subject=f"token:{known_digest[:12]}", spaces=spaces)
        return None

    @classmethod
    def from_env(cls) -> "BearerAuthenticator":
        raw = os.environ.get("LOCALRAG_AUTH_TOKENS_JSON", "").strip()
        if not raw:
            raise AuthConfigError("LOCALRAG_AUTH_TOKENS_JSON is required")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise AuthConfigError("LOCALRAG_AUTH_TOKENS_JSON must be valid JSON") from exc
        if not isinstance(payload, dict):
            raise AuthConfigError("LOCALRAG_AUTH_TOKENS_JSON must be an object")
        return cls(payload)


def env_auth_required() -> bool:
    return os.environ.get("LOCALRAG_AUTH_REQUIRED", "0").strip().lower() in {"1", "true", "yes", "on"}

