import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from dataclasses import FrozenInstanceError
from pathlib import Path
from threading import Barrier, Event, Thread, current_thread
from unittest.mock import patch

from agent.context.models import ConversationSummary, SummaryFinding
from agent.context.store import (
    ConversationContextStore,
    ConversationRevisionConflictError,
    SummaryCommitCommand,
    TokenObservationCommand,
    TokenObservationSnapshot,
)
from agent.memory import TaskMemoryStore
from agent.research import ResearchRunStore, ResearchStepDraft


class ConversationContextStoreTests(unittest.TestCase):
    def _path(self, temp_dir: str) -> Path:
        return Path(temp_dir) / "task-memory.sqlite3"

    def _summary(self, *, goal: str = "Compare retrieval methods") -> ConversationSummary:
        return ConversationSummary(
            goal=goal,
            user_constraints=("Use Chinese",),
            confirmed_findings=(
                SummaryFinding(
                    "Method A has lower latency.",
                    evidence_ids=("evidence-2", "evidence-1"),
                ),
            ),
            decisions=("Keep the reranker",),
            unresolved_questions=("What is the memory cost?",),
            failed_attempts=("The first source timed out",),
            referenced_source_ids=("source-2", "source-1"),
        )

    def _command(
        self,
        *,
        session_id: str = "session-a",
        goal: str = "Compare retrieval methods",
        covered_message_ids: tuple[str, ...] = ("message-1", "message-2"),
        tokens_before: int = 900,
        tokens_after: int = 400,
    ) -> SummaryCommitCommand:
        return SummaryCommitCommand(
            session_id=session_id,
            summary=self._summary(goal=goal),
            covered_message_ids=covered_message_ids,
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            messages_before=8,
            messages_after=4,
            summary_model="local-e6.1",
            compression_reason="trigger_ratio",
            fallback_reason="",
        )

    def _observation(
        self,
        *,
        session_id: str = "session-a",
        revision: int = 1,
        request_id: str = "request-1",
        actual_input_tokens: int = 380,
    ) -> TokenObservationCommand:
        return TokenObservationCommand(
            session_id=session_id,
            revision=revision,
            request_id=request_id,
            estimated_input_tokens=400,
            actual_input_tokens=actual_input_tokens,
            actual_output_tokens=80,
        )

    def test_migration_preserves_task_and_research_data_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            task_store = TaskMemoryStore(path)
            task_store.update_task("task-legacy", finding="legacy finding")
            research_store = ResearchRunStore(path)
            research_store.create_plan(
                "task-research",
                "Preserve this research run",
                [ResearchStepDraft("Read source", "inspect_source", {})],
                run_id="run-legacy",
            )

            ConversationContextStore(path)
            ConversationContextStore(path)

            task = TaskMemoryStore(path).get_task("task-legacy")
            run = ResearchRunStore(path).get_run("run-legacy")
            with closing(sqlite3.connect(path)) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }
                migration_rows = connection.execute(
                    """
                    SELECT version, name
                    FROM agent_schema_migrations
                    WHERE version = 4 OR name = 'v1.6-c2-conversation-context'
                    """
                ).fetchall()

        self.assertEqual(("legacy finding",), task.findings)
        self.assertEqual("task-research", run.task_id)
        self.assertTrue(
            {
                "tasks",
                "task_memory_items",
                "research_runs",
                "research_steps",
                "conversation_summary_state",
                "conversation_summary_events",
                "conversation_token_observations",
            }.issubset(tables)
        )
        self.assertEqual([(4, "v1.6-c2-conversation-context")], migration_rows)

    def test_migration_identity_conflict_fails_before_conversation_ddl(self):
        conflicting_rows = (
            (4, "future-other"),
            (9, "v1.6-c2-conversation-context"),
        )
        for version, name in conflicting_rows:
            with self.subTest(version=version, name=name), tempfile.TemporaryDirectory() as temp_dir:
                path = self._path(temp_dir)
                with closing(sqlite3.connect(path)) as connection:
                    connection.execute(
                        """
                        CREATE TABLE agent_schema_migrations (
                            version INTEGER PRIMARY KEY,
                            name TEXT NOT NULL UNIQUE,
                            applied_at TEXT NOT NULL
                        )
                        """
                    )
                    connection.execute(
                        "INSERT INTO agent_schema_migrations VALUES (?, ?, ?)",
                        (version, name, "2026-07-28T00:00:00+00:00"),
                    )
                    connection.commit()

                with self.assertRaisesRegex(RuntimeError, "migration identity conflict"):
                    ConversationContextStore(path)

                with closing(sqlite3.connect(path)) as connection:
                    conversation_tables = connection.execute(
                        """
                        SELECT name FROM sqlite_master
                        WHERE type = 'table' AND name LIKE 'conversation_%'
                        """
                    ).fetchall()
                    retained = connection.execute(
                        "SELECT version, name FROM agent_schema_migrations"
                    ).fetchall()

                self.assertEqual([], conversation_tables)
                self.assertEqual([(version, name)], retained)

    def test_incompatible_existing_conversation_table_fails_without_registration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            with closing(sqlite3.connect(path)) as connection:
                connection.execute(
                    """
                    CREATE TABLE agent_schema_migrations (
                        version INTEGER PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        applied_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    "CREATE TABLE conversation_summary_state (session_id TEXT PRIMARY KEY)"
                )
                connection.commit()

            with self.assertRaisesRegex(RuntimeError, "incompatible schema"):
                ConversationContextStore(path)

            with closing(sqlite3.connect(path)) as connection:
                migration_count = connection.execute(
                    "SELECT COUNT(*) FROM agent_schema_migrations WHERE version = 4"
                ).fetchone()[0]
                tables = {
                    row[0]
                    for row in connection.execute(
                        """
                        SELECT name FROM sqlite_master
                        WHERE type = 'table' AND name LIKE 'conversation_%'
                        """
                    )
                }

        self.assertEqual(0, migration_count)
        self.assertEqual({"conversation_summary_state"}, tables)

    def test_migration_creates_exact_columns_primary_keys_and_composite_foreign_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            ConversationContextStore(path)
            with closing(sqlite3.connect(path)) as connection:
                state_columns = connection.execute(
                    "PRAGMA table_info(conversation_summary_state)"
                ).fetchall()
                event_columns = connection.execute(
                    "PRAGMA table_info(conversation_summary_events)"
                ).fetchall()
                observation_columns = connection.execute(
                    "PRAGMA table_info(conversation_token_observations)"
                ).fetchall()
                foreign_keys = connection.execute(
                    "PRAGMA foreign_key_list(conversation_token_observations)"
                ).fetchall()

        self.assertEqual(
            [
                "session_id",
                "revision",
                "summary_json",
                "covered_message_ids_json",
                "tokens_before",
                "tokens_after",
                "messages_before",
                "messages_after",
                "summary_model",
                "compression_reason",
                "fallback_reason",
                "created_at",
                "updated_at",
            ],
            [row[1] for row in state_columns],
        )
        self.assertEqual(["session_id", "revision"], [row[1] for row in event_columns if row[5]])
        self.assertEqual(
            ["session_id", "request_id"],
            [row[1] for row in observation_columns if row[5]],
        )
        self.assertEqual(
            {("session_id", "session_id"), ("revision", "revision")},
            {(row[3], row[4]) for row in foreign_keys},
        )
        self.assertEqual(
            {"conversation_summary_events"},
            {row[2] for row in foreign_keys},
        )
        self.assertEqual({"CASCADE"}, {row[6] for row in foreign_keys})

    def test_original_task4_schema_is_accepted_without_changing_data_or_migration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            summary_json = json.dumps(
                {
                    "goal": "Legacy summary",
                    "user_constraints": [],
                    "confirmed_findings": [],
                    "decisions": [],
                    "unresolved_questions": [],
                    "failed_attempts": [],
                    "referenced_source_ids": [],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            applied_at = "2026-07-27T12:00:00+00:00"
            created_at = "2026-07-27T12:01:00+00:00"
            with closing(sqlite3.connect(path)) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
                connection.executescript(
                    """
                    CREATE TABLE agent_schema_migrations (
                        version INTEGER PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        applied_at TEXT NOT NULL
                    );

                    CREATE TABLE conversation_summary_state (
                        session_id TEXT PRIMARY KEY,
                        revision INTEGER NOT NULL CHECK (revision > 0),
                        summary_json TEXT NOT NULL,
                        covered_message_ids_json TEXT NOT NULL,
                        tokens_before INTEGER NOT NULL CHECK (tokens_before >= 0),
                        tokens_after INTEGER NOT NULL CHECK (tokens_after >= 0),
                        messages_before INTEGER NOT NULL CHECK (messages_before >= 0),
                        messages_after INTEGER NOT NULL CHECK (messages_after >= 0),
                        summary_model TEXT NOT NULL,
                        compression_reason TEXT NOT NULL,
                        fallback_reason TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE conversation_summary_events (
                        session_id TEXT NOT NULL,
                        revision INTEGER NOT NULL CHECK (revision > 0),
                        summary_json TEXT NOT NULL,
                        covered_message_ids_json TEXT NOT NULL,
                        tokens_before INTEGER NOT NULL,
                        tokens_after INTEGER NOT NULL,
                        messages_before INTEGER NOT NULL,
                        messages_after INTEGER NOT NULL,
                        summary_model TEXT NOT NULL,
                        compression_reason TEXT NOT NULL,
                        fallback_reason TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        PRIMARY KEY(session_id, revision)
                    );

                    CREATE TABLE conversation_token_observations (
                        session_id TEXT NOT NULL,
                        revision INTEGER NOT NULL CHECK (revision > 0),
                        request_id TEXT NOT NULL,
                        estimated_input_tokens INTEGER NOT NULL
                            CHECK (estimated_input_tokens >= 0),
                        actual_input_tokens INTEGER NOT NULL
                            CHECK (actual_input_tokens >= 0),
                        actual_output_tokens INTEGER NOT NULL
                            CHECK (actual_output_tokens >= 0),
                        created_at TEXT NOT NULL,
                        PRIMARY KEY(session_id, request_id),
                        FOREIGN KEY(session_id, revision)
                            REFERENCES conversation_summary_events(session_id, revision)
                            ON DELETE CASCADE
                    );
                    """
                )
                connection.execute(
                    "INSERT INTO agent_schema_migrations VALUES (4, ?, ?)",
                    ("v1.6-c2-conversation-context", applied_at),
                )
                state_values = (
                    "legacy-session",
                    1,
                    summary_json,
                    '["legacy-message"]',
                    100,
                    40,
                    4,
                    2,
                    "legacy-model",
                    "trigger_ratio",
                    "",
                    created_at,
                )
                connection.execute(
                    """
                    INSERT INTO conversation_summary_state VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (*state_values, created_at),
                )
                connection.execute(
                    """
                    INSERT INTO conversation_summary_events VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    state_values,
                )
                connection.execute(
                    """
                    INSERT INTO conversation_token_observations VALUES (
                        'legacy-session', 1, 'legacy-request', 40, 38, 8, ?
                    )
                    """,
                    (created_at,),
                )
                connection.commit()

            store = ConversationContextStore(path)
            snapshot = store.get_summary("legacy-session")
            events = store.list_events("legacy-session")
            with closing(sqlite3.connect(path)) as connection:
                migration_row = connection.execute(
                    "SELECT version, name, applied_at FROM agent_schema_migrations WHERE version = 4"
                ).fetchone()
                observation_row = connection.execute(
                    """
                    SELECT revision, request_id, estimated_input_tokens,
                           actual_input_tokens, actual_output_tokens, created_at
                    FROM conversation_token_observations
                    WHERE session_id = 'legacy-session'
                    """
                ).fetchone()

        self.assertEqual("Legacy summary", snapshot.summary.goal)
        self.assertEqual([1], [event.revision for event in events])
        self.assertEqual(
            (4, "v1.6-c2-conversation-context", applied_at),
            migration_row,
        )
        self.assertEqual((1, "legacy-request", 40, 38, 8, created_at), observation_row)

    def test_commit_and_get_summary_round_trip_all_structured_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(self._path(temp_dir))
            committed = store.commit_summary(self._command(), expected_revision=0)
            restored = store.get_summary("session-a")

        self.assertEqual(1, committed.revision)
        self.assertEqual(committed, restored)
        self.assertEqual(self._summary(), restored.summary)
        self.assertEqual(("message-1", "message-2"), restored.covered_message_ids)
        self.assertEqual(restored.created_at, restored.updated_at)

    def test_summary_json_is_deterministic_and_safe_structured_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            store = ConversationContextStore(path)
            store.commit_summary(self._command(), expected_revision=0)
            with closing(sqlite3.connect(path)) as connection:
                summary_json = connection.execute(
                    "SELECT summary_json FROM conversation_summary_state"
                ).fetchone()[0]

        self.assertEqual(
            json.dumps(
                {
                    "goal": "Compare retrieval methods",
                    "user_constraints": ["Use Chinese"],
                    "confirmed_findings": [
                        {
                            "claim": "Method A has lower latency.",
                            "evidence_ids": ["evidence-2", "evidence-1"],
                        }
                    ],
                    "decisions": ["Keep the reranker"],
                    "unresolved_questions": ["What is the memory cost?"],
                    "failed_attempts": ["The first source timed out"],
                    "referenced_source_ids": ["source-2", "source-1"],
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            summary_json,
        )

    def test_get_summary_returns_none_when_session_has_no_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(self._path(temp_dir))
            self.assertIsNone(store.get_summary("missing-session"))

    def test_successive_commits_append_events_in_revision_order(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(self._path(temp_dir))
            first = store.commit_summary(self._command(goal="Goal 1"), expected_revision=0)
            second = store.commit_summary(self._command(goal="Goal 2"), expected_revision=1)
            third = store.commit_summary(self._command(goal="Goal 3"), expected_revision=2)
            events = store.list_events("session-a")

        self.assertEqual([1, 2, 3], [event.revision for event in events])
        self.assertEqual(["Goal 1", "Goal 2", "Goal 3"], [event.summary.goal for event in events])
        self.assertEqual(first.created_at, second.created_at)
        self.assertNotEqual(first.revision, third.revision)

    def test_stale_revision_rolls_back_without_leaving_an_event(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(self._path(temp_dir))
            first = store.commit_summary(self._command(goal="Committed"), expected_revision=0)

            with self.assertRaises(ConversationRevisionConflictError):
                store.commit_summary(self._command(goal="Stale"), expected_revision=0)

            restored = store.get_summary("session-a")
            events = store.list_events("session-a")

        self.assertEqual(first, restored)
        self.assertEqual([1], [event.revision for event in events])
        self.assertEqual("Committed", events[0].summary.goal)

    def test_orphan_event_conflict_rolls_back_state_with_domain_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            store = ConversationContextStore(path)
            command = self._command()
            with closing(sqlite3.connect(path)) as connection:
                connection.execute(
                    """
                    INSERT INTO conversation_summary_events(
                        session_id, revision, summary_json, covered_message_ids_json,
                        tokens_before, tokens_after, messages_before, messages_after,
                        summary_model, compression_reason, fallback_reason, created_at
                    ) VALUES (?, 1, ?, ?, 1, 1, 1, 1, ?, ?, '', ?)
                    """,
                    (
                        command.session_id,
                        json.dumps(
                            {
                                "goal": "Existing event",
                                "user_constraints": [],
                                "confirmed_findings": [],
                                "decisions": [],
                                "unresolved_questions": [],
                                "failed_attempts": [],
                                "referenced_source_ids": [],
                            },
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                        '["existing-message"]',
                        command.summary_model,
                        command.compression_reason,
                        "2026-07-28T00:00:00+00:00",
                    ),
                )
                connection.commit()

            with self.assertRaisesRegex(ValueError, "event/state integrity conflict"):
                store.commit_summary(command, expected_revision=0)

            current = store.get_summary("session-a")
            events = store.list_events("session-a")

        self.assertIsNone(current)
        self.assertEqual(["Existing event"], [event.summary.goal for event in events])

    def test_concurrent_initial_commit_allows_exactly_one_writer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            ConversationContextStore(path)
            barrier = Barrier(2)

            def commit(goal: str) -> str:
                store = ConversationContextStore(path)
                barrier.wait()
                try:
                    store.commit_summary(self._command(goal=goal), expected_revision=0)
                    return "committed"
                except ConversationRevisionConflictError:
                    return "conflict"

            with ThreadPoolExecutor(max_workers=2) as executor:
                outcomes = list(executor.map(commit, ("Goal A", "Goal B")))
            events = ConversationContextStore(path).list_events("session-a")

        self.assertEqual(["committed", "conflict"], sorted(outcomes))
        self.assertEqual([1], [event.revision for event in events])

    def test_concurrent_same_revision_commit_allows_exactly_one_writer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            store = ConversationContextStore(path)
            store.commit_summary(self._command(goal="Initial"), expected_revision=0)
            barrier = Barrier(2)

            def commit(goal: str) -> str:
                concurrent_store = ConversationContextStore(path)
                barrier.wait()
                try:
                    concurrent_store.commit_summary(
                        self._command(goal=goal),
                        expected_revision=1,
                    )
                    return "committed"
                except ConversationRevisionConflictError:
                    return "conflict"

            with ThreadPoolExecutor(max_workers=2) as executor:
                outcomes = list(executor.map(commit, ("Goal A", "Goal B")))
            restored = ConversationContextStore(path)
            restored_revision = restored.get_summary("session-a").revision
            event_revisions = [
                event.revision for event in restored.list_events("session-a")
            ]

        self.assertEqual(["committed", "conflict"], sorted(outcomes))
        self.assertEqual(2, restored_revision)
        self.assertEqual([1, 2], event_revisions)

    def test_record_token_observation_is_idempotent_for_identical_request(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            store = ConversationContextStore(path)
            store.commit_summary(self._command(), expected_revision=0)

            first = store.record_token_observation(self._observation())
            replayed = store.record_token_observation(self._observation())
            with closing(sqlite3.connect(path)) as connection:
                count = connection.execute(
                    "SELECT COUNT(*) FROM conversation_token_observations"
                ).fetchone()[0]

        self.assertIsInstance(first, TokenObservationSnapshot)
        self.assertEqual(first, replayed)
        self.assertEqual(1, count)
        with self.assertRaises(FrozenInstanceError):
            first.actual_input_tokens = 999

    def test_record_token_observation_rejects_changed_payload_for_request_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(self._path(temp_dir))
            store.commit_summary(self._command(), expected_revision=0)
            store.record_token_observation(self._observation())

            with self.assertRaisesRegex(ValueError, "different payload"):
                store.record_token_observation(
                    self._observation(actual_input_tokens=381)
                )

    def test_record_token_observation_requires_same_session_revision_event(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(self._path(temp_dir))
            store.commit_summary(self._command(), expected_revision=0)

            for command in (
                self._observation(revision=2),
                self._observation(session_id="session-b"),
            ):
                with self.subTest(command=command):
                    with self.assertRaisesRegex(ValueError, "summary event"):
                        store.record_token_observation(command)

    def test_observation_and_clear_are_serialized_without_raw_integrity_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            observation_store = ConversationContextStore(path)
            clear_store = ConversationContextStore(path)
            observation_store.commit_summary(self._command(), expected_revision=0)

            event_checked = Event()
            allow_insert = Event()
            write_transaction_started = Event()
            clear_started = Event()
            clear_done = Event()
            observation_results = []
            observation_errors = []
            clear_errors = []
            original_connect = sqlite3.connect

            class CoordinatedCursor:
                def __init__(self, cursor):
                    self._cursor = cursor

                def fetchone(self):
                    row = self._cursor.fetchone()
                    self._cursor.fetchall()
                    event_checked.set()
                    if not allow_insert.wait(timeout=5):
                        raise TimeoutError("observation insert was not released")
                    return row

                def __getattr__(self, name):
                    return getattr(self._cursor, name)

            class CoordinatedConnection(sqlite3.Connection):
                def execute(self, sql, parameters=()):
                    cursor = super().execute(sql, parameters)
                    statement = " ".join(sql.lower().split())
                    if current_thread().name == "observation-writer":
                        if statement == "begin immediate":
                            write_transaction_started.set()
                        if statement.startswith(
                            "select 1 from conversation_summary_events"
                        ):
                            return CoordinatedCursor(cursor)
                    return cursor

            def coordinated_connect(*args, **kwargs):
                kwargs["factory"] = CoordinatedConnection
                return original_connect(*args, **kwargs)

            def record_observation() -> None:
                try:
                    observation_results.append(
                        observation_store.record_token_observation(self._observation())
                    )
                except Exception as exc:  # Captured for deterministic thread assertion.
                    observation_errors.append(exc)

            def clear_summary() -> None:
                clear_started.set()
                try:
                    clear_store.clear_session("session-a")
                except Exception as exc:  # Captured for deterministic thread assertion.
                    clear_errors.append(exc)
                finally:
                    clear_done.set()

            with patch("agent.context.store.sqlite3.connect", coordinated_connect):
                observation_thread = Thread(
                    target=record_observation,
                    name="observation-writer",
                )
                observation_thread.start()
                self.assertTrue(event_checked.wait(timeout=5))

                clear_thread = Thread(target=clear_summary, name="session-clearer")
                clear_thread.start()
                self.assertTrue(clear_started.wait(timeout=5))
                if not write_transaction_started.is_set():
                    self.assertTrue(clear_done.wait(timeout=5))
                allow_insert.set()
                observation_thread.join(timeout=5)
                clear_thread.join(timeout=5)

        self.assertFalse(observation_thread.is_alive())
        self.assertFalse(clear_thread.is_alive())
        self.assertEqual([], clear_errors)
        self.assertFalse(
            any(isinstance(error, sqlite3.IntegrityError) for error in observation_errors),
            observation_errors,
        )
        self.assertTrue(
            bool(observation_results)
            or (
                len(observation_errors) == 1
                and isinstance(observation_errors[0], ValueError)
            )
        )

    def test_clear_session_removes_exact_summary_scope_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            task_store = TaskMemoryStore(path)
            task_store.update_task("session-a", finding="task data must remain")
            store = ConversationContextStore(path)
            store.commit_summary(self._command(session_id="session-a"), expected_revision=0)
            store.record_token_observation(self._observation(session_id="session-a"))
            store.commit_summary(
                self._command(session_id="session-a-extra"),
                expected_revision=0,
            )

            store.clear_session("session-a")

            retained_task = TaskMemoryStore(path).get_task("session-a")
            with closing(sqlite3.connect(path)) as connection:
                remaining = {
                    table: connection.execute(
                        f"SELECT COUNT(*) FROM {table} WHERE session_id = 'session-a'"
                    ).fetchone()[0]
                    for table in (
                        "conversation_summary_state",
                        "conversation_summary_events",
                        "conversation_token_observations",
                    )
                }
            cleared_summary = store.get_summary("session-a")
            cleared_events = store.list_events("session-a")
            retained_summary = store.get_summary("session-a-extra")

        self.assertIsNone(cleared_summary)
        self.assertEqual((), cleared_events)
        self.assertEqual("session-a-extra", retained_summary.session_id)
        self.assertEqual(("task data must remain",), retained_task.findings)
        self.assertEqual({0}, set(remaining.values()))

    def test_corrupt_or_unknown_summary_json_fails_explicitly(self):
        bad_payloads = (
            "not-json",
            '{"goal":"x","unknown":[]}',
            '{"goal":"x","user_constraints":"not-a-list",'
            '"confirmed_findings":[],"decisions":[],"unresolved_questions":[],'
            '"failed_attempts":[],"referenced_source_ids":[]}',
            '{"goal":"x","user_constraints":[],"confirmed_findings":'
            '[{"claim":"c","evidence_ids":[1]}],"decisions":[],'
            '"unresolved_questions":[],"failed_attempts":[],'
            '"referenced_source_ids":[]}',
        )
        for payload in bad_payloads:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as temp_dir:
                path = self._path(temp_dir)
                store = ConversationContextStore(path)
                store.commit_summary(self._command(), expected_revision=0)
                with closing(sqlite3.connect(path)) as connection:
                    connection.execute(
                        "UPDATE conversation_summary_state SET summary_json = ?",
                        (payload,),
                    )
                    connection.commit()
                with self.assertRaisesRegex(ValueError, "summary_json"):
                    store.get_summary("session-a")

    def test_corrupt_covered_message_ids_json_fails_explicitly(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = self._path(temp_dir)
            store = ConversationContextStore(path)
            store.commit_summary(self._command(), expected_revision=0)
            with closing(sqlite3.connect(path)) as connection:
                connection.execute(
                    "UPDATE conversation_summary_state SET covered_message_ids_json = ?",
                    ('["message-1", "message-1"]',),
                )
                connection.commit()

            with self.assertRaisesRegex(ValueError, "covered_message_ids_json"):
                store.get_summary("session-a")

    def test_commit_command_rejects_invalid_boundaries(self):
        invalid_values = (
            ("session_id", {"session_id": "../unsafe"}, (TypeError, ValueError)),
            ("summary", {"summary": {}}, TypeError),
            ("covered list", {"covered_message_ids": ["message-1"]}, TypeError),
            ("blank covered id", {"covered_message_ids": (" ",)}, ValueError),
            (
                "duplicate covered id",
                {"covered_message_ids": ("message-1", "message-1")},
                ValueError,
            ),
            ("bool counter", {"tokens_before": True}, TypeError),
            ("negative counter", {"messages_after": -1}, ValueError),
            ("blank model", {"summary_model": " "}, ValueError),
            ("blank reason", {"compression_reason": ""}, ValueError),
            ("non-string fallback", {"fallback_reason": None}, TypeError),
        )
        base = {
            "session_id": "session-a",
            "summary": self._summary(),
            "covered_message_ids": ("message-1",),
            "tokens_before": 10,
            "tokens_after": 5,
            "messages_before": 2,
            "messages_after": 1,
            "summary_model": "local-e6.1",
            "compression_reason": "trigger_ratio",
            "fallback_reason": "",
        }
        for label, override, error_type in invalid_values:
            with self.subTest(label=label), self.assertRaises(error_type):
                SummaryCommitCommand(**(base | override))

    def test_expected_revision_requires_non_negative_strict_int(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ConversationContextStore(self._path(temp_dir))
            for value, error_type in ((True, TypeError), (1.0, TypeError), (-1, ValueError)):
                with self.subTest(value=value), self.assertRaises(error_type):
                    store.commit_summary(self._command(), expected_revision=value)

    def test_token_observation_command_rejects_invalid_boundaries(self):
        base = {
            "session_id": "session-a",
            "revision": 1,
            "request_id": "request-1",
            "estimated_input_tokens": 10,
            "actual_input_tokens": 9,
            "actual_output_tokens": 2,
        }
        invalid_values = (
            ({"revision": 0}, ValueError),
            ({"revision": True}, TypeError),
            ({"request_id": " "}, ValueError),
            ({"actual_input_tokens": -1}, ValueError),
            ({"actual_output_tokens": False}, TypeError),
        )
        for override, error_type in invalid_values:
            with self.subTest(override=override), self.assertRaises(error_type):
                TokenObservationCommand(**(base | override))


if __name__ == "__main__":
    unittest.main()
