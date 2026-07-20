import re


_SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
_MAX_SESSION_ID_LENGTH = 128


def validate_session_id(session_id: str) -> str:
    """Validate a session id before using it as runtime state or a file name."""
    if not isinstance(session_id, str):
        raise TypeError("session_id must be a string")

    normalized = session_id.strip()
    if not normalized:
        raise ValueError("session_id must not be empty")
    if len(normalized) > _MAX_SESSION_ID_LENGTH:
        raise ValueError(f"session_id must not exceed {_MAX_SESSION_ID_LENGTH} characters")
    if not _SESSION_ID_PATTERN.fullmatch(normalized):
        raise ValueError("session_id may only contain letters, numbers, '.', '_' and '-'")
    return normalized
