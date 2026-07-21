import re


_RUNTIME_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
_MAX_RUNTIME_ID_LENGTH = 128


def _validate_runtime_id(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if len(normalized) > _MAX_RUNTIME_ID_LENGTH:
        raise ValueError(f"{field_name} must not exceed {_MAX_RUNTIME_ID_LENGTH} characters")
    if not _RUNTIME_ID_PATTERN.fullmatch(normalized):
        raise ValueError(f"{field_name} may only contain letters, numbers, '.', '_' and '-'")
    return normalized


def validate_session_id(session_id: str) -> str:
    """Validate a session id before using it as runtime state or a file name."""
    return _validate_runtime_id(session_id, "session_id")


def validate_task_id(task_id: str) -> str:
    """Validate a persistent task identifier."""
    return _validate_runtime_id(task_id, "task_id")
