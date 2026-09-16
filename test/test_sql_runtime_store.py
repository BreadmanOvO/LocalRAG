from sqlalchemy import create_engine, event
import pytest

from agent_platform.runtime.sql_runtime_store import SqlRuntimeStore
from agent_platform.worker.sql_team_worker import SqlTeamWorker
from agent_platform.runtime.control import RunControlState


def make_store():
    return SqlRuntimeStore(create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=__import__("sqlalchemy").pool.StaticPool))


def test_claim_and_fenced_completion():
    store = make_store()
    store.enqueue_job("job-1", "run-1", {"run_id": "run-1", "goal": "x"})
    claimed = store.claim_job("w1", lease_seconds=10)
    assert claimed and claimed["attempt_count"] == 1
    try:
        store.finish_job("job-1", worker_id="w2", attempt_count=1)
    except RuntimeError:
        pass
    else:
        raise AssertionError("stale worker must be fenced")
    assert store.finish_job("job-1", worker_id="w1", attempt_count=1)["status"] == "completed"


def test_worker_executes_durable_job():
    store = make_store(); seen = []
    store.enqueue_job("job-1", "run-1", {"goal": "hello"})
    worker = SqlTeamWorker(store, lambda payload: seen.append(payload["goal"]), worker_id="worker-a")
    assert worker.run_once() is True
    assert seen == ["hello"]
    assert store.get_job("job-1")["status"] == "completed"


def test_cancel_transaction_rolls_back_if_command_save_fails():
    store = make_store()
    store.upsert_task("task-1", "room-1", "test", active_run_id="run-1")
    store.upsert_run("run-1", task_id="task-1", room_id="room-1", plan_revision=1, status="running")
    def fail_command(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO runtime_commands"):
            raise RuntimeError("disk failure")
    event.listen(store.engine, "before_cursor_execute", fail_command)
    try:
        with pytest.raises(RuntimeError, match="disk failure"):
            store.apply_control("operation-cancel", "run-1", "cancel", expected_row_version=1, expected_control_epoch=0)
    finally:
        event.remove(store.engine, "before_cursor_execute", fail_command)
    assert store.get_run("run-1")["status"] == "running"
    assert store.get_task("task-1")["active_run_id"] == "run-1"
    result = store.apply_control("operation-cancel", "run-1", "cancel", expected_row_version=1, expected_control_epoch=0)
    assert result["run"]["status"] == "cancelled"


def test_late_worker_cannot_overwrite_cancelled_state():
    store = make_store()
    store.upsert_task("task-1", "room-1", "test", active_run_id="run-1")
    store.upsert_run("run-1", task_id="task-1", room_id="room-1", plan_revision=1, status="running")
    store.apply_control("operation-cancel", "run-1", "cancel", expected_row_version=1, expected_control_epoch=0)
    row = store.finish_run(RunControlState("run-1", 1, "completed", 0, 2))
    assert row["status"] == "cancelled"
    assert row["control_epoch"] == 1
    assert store.get_task("task-1")["status"] == "cancelled"
