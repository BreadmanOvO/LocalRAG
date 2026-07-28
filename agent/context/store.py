from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock

from agent.context.models import ConversationSummary, SummaryFinding
from agent.context.schema import apply_conversation_context_migration
from utils.path_tools import get_abs_path
from utils.session import validate_session_id


_SUMMARY_FIELDS = frozenset(
    {
        "goal",
        "user_constraints",
        "confirmed_findings",
        "decisions",
        "unresolved_questions",
        "failed_attempts",
        "referenced_source_ids",
    }
)
_FINDING_FIELDS = frozenset({"claim", "evidence_ids"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _strict_non_negative_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{field_name} must be an int")
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")
    return value


def _strict_positive_int(value: object, field_name: str) -> int:
    normalized = _strict_non_negative_int(value, field_name)
    if normalized == 0:
        raise ValueError(f"{field_name} must be greater than 0")
    return normalized


def _clean_text(
    value: object,
    field_name: str,
    *,
    allow_empty: bool = False,
    max_length: int = 4000,
) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not allow_empty and not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if len(normalized) > max_length:
        raise ValueError(f"{field_name} must not exceed {max_length} characters")
    return normalized


def _normalize_covered_message_ids(
    value: object,
    *,
    field_name: str,
) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{field_name} must be a tuple")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise TypeError(f"{field_name} must contain only strings")
        message_id = item.strip()
        if not message_id:
            raise ValueError(f"{field_name} must not contain blank values")
        normalized.append(message_id)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{field_name} must not contain duplicates")
    return tuple(normalized)


def _summary_to_json(summary: ConversationSummary) -> str:
    payload = {
        "goal": summary.goal,
        "user_constraints": list(summary.user_constraints),
        "confirmed_findings": [
            {
                "claim": finding.claim,
                "evidence_ids": list(finding.evidence_ids),
            }
            for finding in summary.confirmed_findings
        ],
        "decisions": list(summary.decisions),
        "unresolved_questions": list(summary.unresolved_questions),
        "failed_attempts": list(summary.failed_attempts),
        "referenced_source_ids": list(summary.referenced_source_ids),
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _require_string_list(payload: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError(f"{field_name} must be a list of strings")
    return tuple(payload)


def _summary_from_json(value: str) -> ConversationSummary:
    try:
        payload = json.loads(value)
        if not isinstance(payload, dict) or set(payload) != _SUMMARY_FIELDS:
            raise ValueError("summary fields do not match the contract")
        if not isinstance(payload["goal"], str):
            raise ValueError("goal must be a string")

        findings_payload = payload["confirmed_findings"]
        if not isinstance(findings_payload, list):
            raise ValueError("confirmed_findings must be a list")
        findings: list[SummaryFinding] = []
        for finding_payload in findings_payload:
            if not isinstance(finding_payload, dict) or set(finding_payload) != _FINDING_FIELDS:
                raise ValueError("finding fields do not match the contract")
            if not isinstance(finding_payload["claim"], str):
                raise ValueError("finding claim must be a string")
            findings.append(
                SummaryFinding(
                    claim=finding_payload["claim"],
                    evidence_ids=_require_string_list(
                        finding_payload["evidence_ids"],
                        "finding evidence_ids",
                    ),
                )
            )

        return ConversationSummary(
            goal=payload["goal"],
            user_constraints=_require_string_list(
                payload["user_constraints"],
                "user_constraints",
            ),
            confirmed_findings=tuple(findings),
            decisions=_require_string_list(payload["decisions"], "decisions"),
            unresolved_questions=_require_string_list(
                payload["unresolved_questions"],
                "unresolved_questions",
            ),
            failed_attempts=_require_string_list(
                payload["failed_attempts"],
                "failed_attempts",
            ),
            referenced_source_ids=_require_string_list(
                payload["referenced_source_ids"],
                "referenced_source_ids",
            ),
        )
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ValueError("summary_json has invalid structure") from exc


def _covered_message_ids_to_json(message_ids: tuple[str, ...]) -> str:
    return json.dumps(
        list(message_ids),
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _covered_message_ids_from_json(value: str) -> tuple[str, ...]:
    try:
        payload = json.loads(value)
        if not isinstance(payload, list):
            raise ValueError("covered message ids must be a list")
        return _normalize_covered_message_ids(
            tuple(payload),
            field_name="covered_message_ids_json",
        )
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise ValueError("covered_message_ids_json has invalid structure") from exc


@dataclass(frozen=True)
class SummaryCommitCommand:
    session_id: str
    summary: ConversationSummary
    covered_message_ids: tuple[str, ...]
    tokens_before: int
    tokens_after: int
    messages_before: int
    messages_after: int
    summary_model: str
    compression_reason: str
    fallback_reason: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_id", validate_session_id(self.session_id))
        if not isinstance(self.summary, ConversationSummary):
            raise TypeError("summary must be a ConversationSummary")
        object.__setattr__(
            self,
            "covered_message_ids",
            _normalize_covered_message_ids(
                self.covered_message_ids,
                field_name="covered_message_ids",
            ),
        )
        for field_name in (
            "tokens_before",
            "tokens_after",
            "messages_before",
            "messages_after",
        ):
            _strict_non_negative_int(getattr(self, field_name), field_name)
        object.__setattr__(
            self,
            "summary_model",
            _clean_text(self.summary_model, "summary_model"),
        )
        object.__setattr__(
            self,
            "compression_reason",
            _clean_text(self.compression_reason, "compression_reason"),
        )
        object.__setattr__(
            self,
            "fallback_reason",
            _clean_text(self.fallback_reason, "fallback_reason", allow_empty=True),
        )


@dataclass(frozen=True)
class ConversationSummarySnapshot:
    session_id: str
    revision: int
    summary: ConversationSummary
    covered_message_ids: tuple[str, ...]
    tokens_before: int
    tokens_after: int
    messages_before: int
    messages_after: int
    summary_model: str
    compression_reason: str
    fallback_reason: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class TokenObservationCommand:
    session_id: str
    revision: int
    request_id: str
    estimated_input_tokens: int
    actual_input_tokens: int
    actual_output_tokens: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "session_id", validate_session_id(self.session_id))
        _strict_positive_int(self.revision, "revision")
        object.__setattr__(
            self,
            "request_id",
            _clean_text(self.request_id, "request_id", max_length=256),
        )
        for field_name in (
            "estimated_input_tokens",
            "actual_input_tokens",
            "actual_output_tokens",
        ):
            _strict_non_negative_int(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class TokenObservationSnapshot:
    session_id: str
    revision: int
    request_id: str
    estimated_input_tokens: int
    actual_input_tokens: int
    actual_output_tokens: int
    created_at: str


class ConversationRevisionConflictError(RuntimeError):
    def __init__(
        self,
        session_id: str,
        expected_revision: int,
        actual_revision: int | None,
    ) -> None:
        self.session_id = session_id
        self.expected_revision = expected_revision
        self.actual_revision = actual_revision
        actual = "missing" if actual_revision is None else str(actual_revision)
        super().__init__(
            f"Conversation summary revision conflict for {session_id}: "
            f"expected {expected_revision}, actual {actual}"
        )


class ConversationContextStore:
    """Persist current conversation summaries and their append-only revisions."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        default_path = Path(get_abs_path("agent_memory/task_memory.sqlite3"))
        self.db_path = Path(db_path).resolve() if db_path is not None else default_path.resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._initialize()

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            apply_conversation_context_migration(connection, _utc_now())

    @contextmanager
    def _write_transaction(self):
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            yield connection

    def commit_summary(
        self,
        command: SummaryCommitCommand,
        expected_revision: int,
    ) -> ConversationSummarySnapshot:
        if not isinstance(command, SummaryCommitCommand):
            raise TypeError("command must be a SummaryCommitCommand")
        expected_revision = _strict_non_negative_int(
            expected_revision,
            "expected_revision",
        )
        revision = expected_revision + 1
        now = _utc_now()
        summary_json = _summary_to_json(command.summary)
        covered_message_ids_json = _covered_message_ids_to_json(
            command.covered_message_ids
        )

        with self._lock, self._write_transaction() as connection:
            if expected_revision == 0:
                self._insert_initial_state(
                    connection,
                    command,
                    revision,
                    summary_json,
                    covered_message_ids_json,
                    now,
                )
            else:
                cursor = connection.execute(
                    """
                    UPDATE conversation_summary_state
                    SET revision = ?, summary_json = ?, covered_message_ids_json = ?,
                        tokens_before = ?, tokens_after = ?, messages_before = ?,
                        messages_after = ?, summary_model = ?, compression_reason = ?,
                        fallback_reason = ?, updated_at = ?
                    WHERE session_id = ? AND revision = ?
                    """,
                    (
                        revision,
                        summary_json,
                        covered_message_ids_json,
                        command.tokens_before,
                        command.tokens_after,
                        command.messages_before,
                        command.messages_after,
                        command.summary_model,
                        command.compression_reason,
                        command.fallback_reason,
                        now,
                        command.session_id,
                        expected_revision,
                    ),
                )
                if cursor.rowcount != 1:
                    raise self._revision_conflict(
                        connection,
                        command.session_id,
                        expected_revision,
                    )

            try:
                connection.execute(
                    """
                    INSERT INTO conversation_summary_events(
                        session_id, revision, summary_json, covered_message_ids_json,
                        tokens_before, tokens_after, messages_before, messages_after,
                        summary_model, compression_reason, fallback_reason, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        command.session_id,
                        revision,
                        summary_json,
                        covered_message_ids_json,
                        command.tokens_before,
                        command.tokens_after,
                        command.messages_before,
                        command.messages_after,
                        command.summary_model,
                        command.compression_reason,
                        command.fallback_reason,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                existing_event = self._find_summary_event(
                    connection,
                    command.session_id,
                    revision,
                )
                if existing_event is not None:
                    raise ValueError(
                        "conversation summary event/state integrity conflict for "
                        f"{command.session_id} revision {revision}"
                    ) from exc
                raise
            row = connection.execute(
                "SELECT * FROM conversation_summary_state WHERE session_id = ?",
                (command.session_id,),
            ).fetchone()

        return self._snapshot_from_state_row(row)

    def _insert_initial_state(
        self,
        connection: sqlite3.Connection,
        command: SummaryCommitCommand,
        revision: int,
        summary_json: str,
        covered_message_ids_json: str,
        now: str,
    ) -> None:
        try:
            connection.execute(
                """
                INSERT INTO conversation_summary_state(
                    session_id, revision, summary_json, covered_message_ids_json,
                    tokens_before, tokens_after, messages_before, messages_after,
                    summary_model, compression_reason, fallback_reason,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    command.session_id,
                    revision,
                    summary_json,
                    covered_message_ids_json,
                    command.tokens_before,
                    command.tokens_after,
                    command.messages_before,
                    command.messages_after,
                    command.summary_model,
                    command.compression_reason,
                    command.fallback_reason,
                    now,
                    now,
                ),
            )
        except sqlite3.IntegrityError as exc:
            conflict = self._revision_conflict(
                connection,
                command.session_id,
                expected_revision=0,
            )
            if conflict.actual_revision is None:
                raise
            raise conflict from exc

    def get_summary(self, session_id: str) -> ConversationSummarySnapshot | None:
        session_id = validate_session_id(session_id)
        with self._lock, self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM conversation_summary_state WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return self._snapshot_from_state_row(row) if row is not None else None

    def list_events(self, session_id: str) -> tuple[ConversationSummarySnapshot, ...]:
        session_id = validate_session_id(session_id)
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM conversation_summary_events
                WHERE session_id = ?
                ORDER BY revision ASC
                """,
                (session_id,),
            ).fetchall()
        return tuple(self._snapshot_from_event_row(row) for row in rows)

    def record_token_observation(
        self,
        command: TokenObservationCommand,
    ) -> TokenObservationSnapshot:
        if not isinstance(command, TokenObservationCommand):
            raise TypeError("command must be a TokenObservationCommand")
        now = _utc_now()
        with self._lock, self._write_transaction() as connection:
            existing = self._find_observation(
                connection,
                command.session_id,
                command.request_id,
            )
            if existing is not None:
                return self._resolve_observation_replay(command, existing)

            event = self._find_summary_event(
                connection,
                command.session_id,
                command.revision,
            )
            if event is None:
                raise ValueError(
                    "token observation must reference an existing summary event "
                    "for the same session and revision"
                )

            try:
                connection.execute(
                    """
                    INSERT INTO conversation_token_observations(
                        session_id, revision, request_id, estimated_input_tokens,
                        actual_input_tokens, actual_output_tokens, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        command.session_id,
                        command.revision,
                        command.request_id,
                        command.estimated_input_tokens,
                        command.actual_input_tokens,
                        command.actual_output_tokens,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as exc:
                existing = self._find_observation(
                    connection,
                    command.session_id,
                    command.request_id,
                )
                if existing is not None:
                    return self._resolve_observation_replay(command, existing)
                event = self._find_summary_event(
                    connection,
                    command.session_id,
                    command.revision,
                )
                if event is None:
                    raise ValueError(
                        "token observation must reference an existing summary event "
                        "for the same session and revision"
                    ) from exc
                raise

            row = self._find_observation(
                connection,
                command.session_id,
                command.request_id,
            )
        return self._observation_from_row(row)

    def clear_session(self, session_id: str) -> None:
        session_id = validate_session_id(session_id)
        with self._lock, self._write_transaction() as connection:
            connection.execute(
                "DELETE FROM conversation_token_observations WHERE session_id = ?",
                (session_id,),
            )
            connection.execute(
                "DELETE FROM conversation_summary_state WHERE session_id = ?",
                (session_id,),
            )
            connection.execute(
                "DELETE FROM conversation_summary_events WHERE session_id = ?",
                (session_id,),
            )

    @staticmethod
    def _revision_conflict(
        connection: sqlite3.Connection,
        session_id: str,
        expected_revision: int,
    ) -> ConversationRevisionConflictError:
        row = connection.execute(
            "SELECT revision FROM conversation_summary_state WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        actual_revision = int(row["revision"]) if row is not None else None
        return ConversationRevisionConflictError(
            session_id,
            expected_revision,
            actual_revision,
        )

    @staticmethod
    def _find_summary_event(
        connection: sqlite3.Connection,
        session_id: str,
        revision: int,
    ) -> sqlite3.Row | None:
        return connection.execute(
            """
            SELECT 1 FROM conversation_summary_events
            WHERE session_id = ? AND revision = ?
            """,
            (session_id, revision),
        ).fetchone()

    @staticmethod
    def _find_observation(
        connection: sqlite3.Connection,
        session_id: str,
        request_id: str,
    ) -> sqlite3.Row | None:
        return connection.execute(
            """
            SELECT * FROM conversation_token_observations
            WHERE session_id = ? AND request_id = ?
            """,
            (session_id, request_id),
        ).fetchone()

    @classmethod
    def _resolve_observation_replay(
        cls,
        command: TokenObservationCommand,
        row: sqlite3.Row,
    ) -> TokenObservationSnapshot:
        snapshot = cls._observation_from_row(row)
        if (
            snapshot.revision,
            snapshot.estimated_input_tokens,
            snapshot.actual_input_tokens,
            snapshot.actual_output_tokens,
        ) != (
            command.revision,
            command.estimated_input_tokens,
            command.actual_input_tokens,
            command.actual_output_tokens,
        ):
            raise ValueError(
                "request_id was already recorded with a different payload"
            )
        return snapshot

    @staticmethod
    def _snapshot_from_state_row(row: sqlite3.Row) -> ConversationSummarySnapshot:
        return ConversationSummarySnapshot(
            session_id=row["session_id"],
            revision=int(row["revision"]),
            summary=_summary_from_json(row["summary_json"]),
            covered_message_ids=_covered_message_ids_from_json(
                row["covered_message_ids_json"]
            ),
            tokens_before=int(row["tokens_before"]),
            tokens_after=int(row["tokens_after"]),
            messages_before=int(row["messages_before"]),
            messages_after=int(row["messages_after"]),
            summary_model=row["summary_model"],
            compression_reason=row["compression_reason"],
            fallback_reason=row["fallback_reason"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _snapshot_from_event_row(row: sqlite3.Row) -> ConversationSummarySnapshot:
        created_at = row["created_at"]
        return ConversationSummarySnapshot(
            session_id=row["session_id"],
            revision=int(row["revision"]),
            summary=_summary_from_json(row["summary_json"]),
            covered_message_ids=_covered_message_ids_from_json(
                row["covered_message_ids_json"]
            ),
            tokens_before=int(row["tokens_before"]),
            tokens_after=int(row["tokens_after"]),
            messages_before=int(row["messages_before"]),
            messages_after=int(row["messages_after"]),
            summary_model=row["summary_model"],
            compression_reason=row["compression_reason"],
            fallback_reason=row["fallback_reason"],
            created_at=created_at,
            updated_at=created_at,
        )

    @staticmethod
    def _observation_from_row(row: sqlite3.Row) -> TokenObservationSnapshot:
        return TokenObservationSnapshot(
            session_id=row["session_id"],
            revision=int(row["revision"]),
            request_id=row["request_id"],
            estimated_input_tokens=int(row["estimated_input_tokens"]),
            actual_input_tokens=int(row["actual_input_tokens"]),
            actual_output_tokens=int(row["actual_output_tokens"]),
            created_at=row["created_at"],
        )
