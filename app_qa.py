import json
import uuid

import streamlit as st

from agent import ReactAgent
from agent.observability import (
    build_source_observations,
    diff_task_memory,
    finalize_agent_answer,
    has_pending_tool_calls,
    load_runtime_observability,
    tool_label,
)
from config import settings as config
from utils.session import validate_task_id


WELCOME_MESSAGE = "你好，我是自动驾驶领域的问答助手，有什么可以帮助你？"
EDITABLE_MEMORY_FIELDS = {
    "主题": "topic",
    "阶段结论": "finding",
    "证据缺口": "evidence_gap",
    "待解决问题": "open_question",
    "已确认来源": "confirmed_source",
}
MEMORY_VALUE_FIELDS = {
    "topic": "topic",
    "finding": "findings",
    "evidence_gap": "evidence_gaps",
    "open_question": "open_questions",
    "confirmed_source": "confirmed_sources",
}


st.set_page_config(page_title="LocalRAG 研究助手", layout="wide")


def _new_runtime_id() -> str:
    return str(uuid.uuid4())


def _reset_runtime_for_task(task_id: str) -> None:
    st.session_state["task_id"] = validate_task_id(task_id)
    st.session_state["session_id"] = _new_runtime_id()
    st.session_state["message"] = [{"role": "assistant", "content": WELCOME_MESSAGE}]
    st.session_state.pop("agent", None)


def _query_task_id() -> str | None:
    raw_task_id = st.query_params.get("task")
    if not raw_task_id:
        return None
    try:
        return validate_task_id(raw_task_id)
    except (TypeError, ValueError):
        return None


@st.cache_data(ttl=60, show_spinner=False)
def _runtime_observability(persist_directory: str, collection_name: str) -> dict:
    return load_runtime_observability(
        persist_directory=persist_directory,
        collection_name=collection_name,
    )


def _memory_payload(task_memory) -> dict:
    return {
        "主题": task_memory.topic,
        "已检索问题": list(task_memory.searched_queries),
        "检索命中来源": list(task_memory.retrieved_sources),
        "已确认来源": list(task_memory.confirmed_sources),
        "阶段结论": list(task_memory.findings),
        "证据缺口": list(task_memory.evidence_gaps),
        "待解决问题": list(task_memory.open_questions),
    }


def _memory_values(task_memory, category: str) -> list[str]:
    value = getattr(task_memory, MEMORY_VALUE_FIELDS[category])
    if category == "topic":
        return [value] if value else []
    return list(value)


def _clear_memory_editor_state() -> None:
    for key in list(st.session_state):
        if str(key).startswith("memory_editor_"):
            st.session_state.pop(key, None)


def _render_memory_editor(agent: ReactAgent, task_memory, *, enabled: bool) -> None:
    with st.sidebar.expander("编辑任务记忆"):
        if not enabled:
            st.caption("启用任务记忆后可编辑")
            return

        category_label = st.selectbox(
            "类别",
            list(EDITABLE_MEMORY_FIELDS),
            key="memory_editor_category",
        )
        category = EDITABLE_MEMORY_FIELDS[category_label]
        values = _memory_values(task_memory, category)
        record_options = ["新增记录", *values]
        selected_record = st.selectbox(
            "现有记录",
            record_options,
            key=f"memory_editor_record_{category}",
        )
        old_value = "" if selected_record == "新增记录" else selected_record
        record_index = record_options.index(selected_record)
        new_value = st.text_area(
            "内容",
            value=old_value,
            height=100,
            key=f"memory_editor_value_{category}_{record_index}",
        )
        save_column, delete_column = st.columns(2)
        if save_column.button("保存", use_container_width=True, key="memory_editor_save"):
            try:
                agent.replace_task_memory_entry(category, old_value, new_value)
            except (TypeError, ValueError) as exc:
                st.sidebar.error(str(exc))
            else:
                _clear_memory_editor_state()
                st.rerun()
        if delete_column.button(
            "删除",
            use_container_width=True,
            disabled=not bool(old_value),
            key="memory_editor_delete",
        ):
            agent.delete_task_memory_entry(category, old_value)
            _clear_memory_editor_state()
            st.rerun()


def _render_runtime_header(runtime_status: dict) -> None:
    corpus = runtime_status["current_corpus"]
    source_count = corpus.get("chroma_source_count", 0)
    registry_count = corpus.get("registry_source_count", 0)
    chunk_count = corpus.get("chunk_count", 0)

    source_column, chunk_column, gate_column = st.columns(3)
    source_column.metric("语料来源", f"{source_count} / {registry_count}")
    chunk_column.metric("知识片段", str(chunk_count))
    gate_column.metric("Agent Gate", "通过" if runtime_status["gate_pass"] else "未通过")

    if runtime_status["gate_status"] != "passed":
        st.warning(runtime_status["message"])


def _render_runtime_sidebar(runtime_status: dict) -> None:
    corpus = runtime_status["current_corpus"]
    latest_eval = runtime_status["latest_eval"]
    with st.sidebar.expander("运行状态"):
        if corpus.get("available"):
            st.caption("当前知识库")
            st.write(
                f"来源 {corpus.get('chroma_source_count', 0)} / "
                f"{corpus.get('registry_source_count', 0)}"
            )
            st.write(f"片段 {corpus.get('chunk_count', 0)}")
            st.write(f"覆盖率 {corpus.get('coverage_ratio', 0):.1%}")
            st.code(str(corpus.get("persist_directory", "")), language=None)
        else:
            st.error(corpus.get("error", "当前知识库不可用"))

        st.caption("最近一次 Agent 评测")
        if latest_eval.get("available"):
            summary = latest_eval.get("summary", {})
            st.write(latest_eval.get("run_id", ""))
            st.write("Gate 通过" if summary.get("gate_pass") else "Gate 未通过")
            st.write(f"案例通过率 {summary.get('case_pass_ratio', 0):.1%}")
        else:
            st.write(latest_eval.get("error", "暂无评测结果"))


def _trace_rows(trace: list[dict], *, mark_pending_interrupted: bool = False) -> list[dict]:
    rows = []
    pending = []
    for event in trace:
        if event.get("kind") == "tool_started":
            row = {
                "工具": tool_label(str(event.get("tool_name") or "unknown")),
                "状态": "运行中",
                "耗时": "",
                "参数": json.dumps(event.get("arguments") or {}, ensure_ascii=False),
                "_tool_name": event.get("tool_name"),
                "_call_id": event.get("call_id"),
                "_started_ms": event.get("elapsed_ms") or 0,
            }
            rows.append(row)
            pending.append(row)
        elif event.get("kind") == "tool_completed":
            match = next(
                (
                    row
                    for row in pending
                    if row["状态"] == "运行中"
                    and (
                        (
                            event.get("call_id")
                            and row["_call_id"] == event.get("call_id")
                        )
                        or (
                            not event.get("call_id")
                            and row["_tool_name"] == event.get("tool_name")
                        )
                    )
                ),
                None,
            )
            if match is None:
                continue
            success = event.get("status") not in {"error", "failed"}
            match["状态"] = "完成" if success else "失败"
            elapsed_ms = max(0, (event.get("elapsed_ms") or 0) - match["_started_ms"])
            match["耗时"] = f"{elapsed_ms / 1000:.2f}s"

    if mark_pending_interrupted:
        for row in pending:
            if row["状态"] == "运行中":
                row["状态"] = "中断"

    return [
        {key: value for key, value in row.items() if not key.startswith("_")}
        for row in rows
    ]


def _render_sources(sources: list[dict]) -> None:
    if not sources:
        st.caption("本轮没有新的检索来源")
        return
    for index, source in enumerate(sources, start=1):
        with st.container(border=True):
            title_column, status_column = st.columns([4, 1])
            title_column.markdown(f"**{index}. {source['source_id']}**")
            status_column.caption(
                "已确认" if source["evidence_status"] == "confirmed" else "待核验"
            )
            st.caption(
                f"locator: {source['locator']} | chunk_order: {source['chunk_order']} | "
                f"strategy: {source['chunk_strategy']}"
            )
            if source.get("summary"):
                st.write(source["summary"])


def _render_trace(trace: list[dict], *, run_failed: bool = False) -> None:
    rows = _trace_rows(trace, mark_pending_interrupted=run_failed)
    if not rows:
        st.caption("本轮未调用工具")
        return
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_memory_changes(changes: list[dict]) -> None:
    if not changes:
        st.caption("本轮未变更任务记忆")
        return
    for change in changes:
        action = "新增" if change["action"] == "added" else "移除"
        st.write(f"**{action} · {change['label']}**")
        st.caption(change["value"])


def _render_assistant_details(message: dict) -> None:
    trace = message.get("trace", [])
    sources = message.get("sources", [])
    memory_changes = message.get("memory_changes", [])
    if not trace and not sources and not memory_changes:
        return

    with st.expander("运行详情"):
        source_tab, trace_tab, memory_tab = st.tabs(["来源", "工具轨迹", "记忆变更"])
        with source_tab:
            _render_sources(sources)
        with trace_tab:
            _render_trace(trace, run_failed=bool(message.get("error")))
        with memory_tab:
            _render_memory_changes(memory_changes)


requested_task_id = _query_task_id()
if "task_id" not in st.session_state:
    _reset_runtime_for_task(requested_task_id or _new_runtime_id())
elif requested_task_id and requested_task_id != st.session_state["task_id"]:
    _reset_runtime_for_task(requested_task_id)

if st.query_params.get("task") != st.session_state["task_id"]:
    st.query_params["task"] = st.session_state["task_id"]

if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": WELCOME_MESSAGE}]
if "session_id" not in st.session_state:
    st.session_state["session_id"] = _new_runtime_id()
if "task_memory_enabled" not in st.session_state:
    st.session_state["task_memory_enabled"] = True

runtime_status = _runtime_observability(config.persist_directory, config.collection_name)

st.title("LocalRAG 研究助手")
st.caption(f"任务 {st.session_state['task_id']}")
_render_runtime_header(runtime_status)
st.divider()

memory_enabled = st.sidebar.checkbox("启用任务记忆", key="task_memory_enabled")
if (
    "agent" not in st.session_state
    or getattr(st.session_state["agent"], "session_id", None) != st.session_state["session_id"]
    or getattr(st.session_state["agent"], "task_id", None) != st.session_state["task_id"]
):
    st.session_state["agent"] = ReactAgent(
        session_id=st.session_state["session_id"],
        task_id=st.session_state["task_id"],
        task_memory_enabled=memory_enabled,
    )

agent = st.session_state["agent"]
agent.set_task_memory_enabled(memory_enabled)

st.sidebar.subheader("研究任务")
st.sidebar.caption(st.session_state["task_id"])
new_task_column, clear_memory_column = st.sidebar.columns(2)
if new_task_column.button("新任务", use_container_width=True):
    new_task_id = _new_runtime_id()
    _reset_runtime_for_task(new_task_id)
    st.query_params["task"] = new_task_id
    st.rerun()
if clear_memory_column.button("清除记忆", use_container_width=True):
    agent.clear_task_memory()
    _clear_memory_editor_state()
    st.rerun()

task_memory = agent.get_task_memory()
with st.sidebar.expander("任务记忆", expanded=not task_memory.is_empty):
    if task_memory.is_empty:
        st.caption("当前任务暂无持久化记忆")
    else:
        st.json(_memory_payload(task_memory))

_render_memory_editor(agent, task_memory, enabled=memory_enabled)
_render_runtime_sidebar(runtime_status)

for message in st.session_state["message"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            _render_assistant_details(message)

prompt = st.chat_input("输入研究问题")
if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    before_memory = agent.get_task_memory()
    trace = []
    answer_parts = []
    has_error = False
    used_tools = set()
    source_observations = []
    max_elapsed_ms = 0
    with st.chat_message("assistant"):
        run_status = st.status("Agent 执行中", expanded=True)
        answer_placeholder = st.empty()
        for event in agent.execute_events(prompt):
            max_elapsed_ms = max(max_elapsed_ms, event.elapsed_ms or 0)
            if event.kind == "tool_started":
                trace.append(event.to_dict())
                used_tools.add(event.tool_name)
                run_status.write(f"{tool_label(event.tool_name)} · 运行中")
            elif event.kind == "tool_completed":
                trace.append(event.to_dict())
                state_text = "完成" if event.status not in {"error", "failed"} else "失败"
                if event.status in {"error", "failed"}:
                    has_error = True
                source_observations.extend(event.observations)
                run_status.write(f"{tool_label(event.tool_name)} · {state_text}")
            elif event.kind == "answer_delta":
                answer_parts.append(event.content)
                answer_placeholder.markdown("".join(answer_parts))
            elif event.kind == "error":
                has_error = True
                answer_parts.append(event.content)
                answer_placeholder.error(event.content)

        generated_answer = "".join(answer_parts).strip()
        answer, has_error = finalize_agent_answer(answer_parts, has_error=has_error)
        if not generated_answer:
            answer_placeholder.error(answer)
        if has_pending_tool_calls(trace):
            has_error = True
        run_status.update(
            label=f"执行{'失败' if has_error else '完成'} · {max_elapsed_ms / 1000:.1f}s",
            state="error" if has_error else "complete",
            expanded=has_error,
        )

        after_memory = agent.get_task_memory()
        source_tools = {"rag_search", "show_sources"}
        retrieval_sources = (
            build_source_observations(
                agent.get_retrieval_snapshot(),
                confirmed_sources=after_memory.confirmed_sources,
            )
            if used_tools & source_tools
            else []
        )
        sources = []
        seen_sources = set()
        for source in [*retrieval_sources, *source_observations]:
            key = (
                source.get("source_id"),
                source.get("locator"),
                source.get("chunk_order"),
                source.get("chunk_strategy"),
            )
            if key not in seen_sources:
                seen_sources.add(key)
                sources.append(source)
        assistant_message = {
            "role": "assistant",
            "content": answer,
            "trace": trace,
            "sources": sources,
            "memory_changes": diff_task_memory(before_memory, after_memory),
            "elapsed_ms": max_elapsed_ms,
            "error": has_error,
        }
        st.session_state["message"].append(assistant_message)
        _render_assistant_details(assistant_message)
    st.rerun()
