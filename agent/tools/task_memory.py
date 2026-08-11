import logging

from langchain_core.tools import tool

from agent.memory import TaskMemoryPolicy, TaskMemorySnapshot, TaskMemoryStore
from agent.tools.failures import (
    build_tool_failure,
    render_tool_error,
    render_tool_validation_error,
)
from utils.session import validate_task_id

logger = logging.getLogger(__name__)


def format_task_memory(snapshot: TaskMemorySnapshot) -> str:
    if snapshot.is_empty:
        return "当前任务还没有持久化记忆。"

    lines = [f"任务 ID：{snapshot.task_id}"]
    if snapshot.topic:
        lines.append(f"主题：{snapshot.topic}")

    sections = (
        ("已检索问题", snapshot.searched_queries),
        ("检索命中来源", snapshot.retrieved_sources),
        ("已确认来源", snapshot.confirmed_sources),
        ("阶段结论", snapshot.findings),
        ("证据缺口", snapshot.evidence_gaps),
        ("待解决问题", snapshot.open_questions),
    )
    for title, values in sections:
        if values:
            lines.append(f"{title}：")
            lines.extend(f"- {value}" for value in values)
    return "\n".join(lines)


def build_show_task_memory_tool(
    task_id: str,
    task_memory_store: TaskMemoryStore,
    policy: TaskMemoryPolicy,
):
    bound_task_id = validate_task_id(task_id)

    @tool("show_task_memory")
    def show_task_memory() -> str:
        """展示当前研究任务已保存的主题、来源、结论、证据缺口和待解决问题。"""
        try:
            if not policy.enabled:
                return "当前任务记忆已禁用。"
            return format_task_memory(task_memory_store.get_task(bound_task_id))
        except Exception as exc:
            raise build_tool_failure(
                "任务记忆读取",
                exc,
                default_code="task_memory_read_failed",
                logger=logger,
            ) from exc

    show_task_memory.handle_tool_error = render_tool_error
    show_task_memory.handle_validation_error = render_tool_validation_error

    return show_task_memory


def build_update_task_memory_tool(
    task_id: str,
    task_memory_store: TaskMemoryStore,
    policy: TaskMemoryPolicy,
):
    bound_task_id = validate_task_id(task_id)

    @tool("update_task_memory")
    def update_task_memory(
        topic: str = "",
        finding: str = "",
        evidence_gap: str = "",
        open_question: str = "",
        confirmed_source: str = "",
    ) -> str:
        """更新当前研究任务记忆；仅保存用户明确要求记住或已经确认的任务信息。"""
        try:
            if not policy.enabled:
                return "当前任务记忆已禁用，未保存任何内容。"
            task_memory_store.update_task(
                bound_task_id,
                topic=topic,
                finding=finding,
                evidence_gap=evidence_gap,
                open_question=open_question,
                confirmed_source=confirmed_source,
            )
            return format_task_memory(task_memory_store.get_task(bound_task_id))
        except Exception as exc:
            raise build_tool_failure(
                "任务记忆更新",
                exc,
                default_code="task_memory_update_failed",
                logger=logger,
            ) from exc

    update_task_memory.handle_tool_error = render_tool_error
    update_task_memory.handle_validation_error = render_tool_validation_error

    return update_task_memory
