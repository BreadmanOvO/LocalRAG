import logging
import uuid

import streamlit as st

from agent import ReactAgent
from agent.context.store import ConversationContextStore
from agent.observability import (
    build_source_observations,
    build_tool_trace_rows,
    diff_task_memory,
    finalize_agent_answer,
    has_pending_tool_calls,
    load_runtime_observability,
    merge_source_observations,
    tool_label,
)
from agent.research import (
    ResearchAgentRuntime,
    ResearchControlError,
    ResearchRevisionConflictError,
    ResearchRunService,
    ResearchRunStore,
    ResearchStateError,
    build_evidence_rows,
    build_finding_rows,
    build_step_rows,
    execution_identity_from_observability,
    is_active_plan,
    research_progress,
    run_status_label,
)
from agent.research.presentation import (
    build_conversation_context_view,
    build_model_gateway_view,
)
from config import settings as config
from config.runtime_keys import (
    MODEL_ROLES,
    MODEL_ROUTE_MODES,
    load_runtime_config,
    update_model_routes,
)
from core.chat_history import get_history
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
logger = logging.getLogger(__name__)

MODEL_ROUTE_LABELS = {
    "local": "本地（失败自动转云端）",
    "cloud": "云端",
}
MODEL_ROLE_LABELS = {
    "planner": "Planner",
    "rag": "RAG 生成",
    "summary": "会话摘要",
}


st.set_page_config(page_title="LocalRAG 研究助手", layout="wide")


st.markdown(
    """
    <style>
    section.main [data-testid="stBottom"] {
        position: static;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _new_runtime_id() -> str:
    return str(uuid.uuid4())


def _clear_session_artifacts(session_id: str) -> None:
    try:
        ConversationContextStore().clear_session(session_id)
        get_history(session_id).clear()
    except Exception:
        logger.exception("Failed to clear conversation session")


def _reset_runtime_for_task(task_id: str) -> None:
    previous_session_id = st.session_state.get("session_id")
    if previous_session_id:
        _clear_session_artifacts(previous_session_id)
    st.session_state["task_id"] = validate_task_id(task_id)
    st.session_state["session_id"] = _new_runtime_id()
    st.session_state["message"] = [{"role": "assistant", "content": WELCOME_MESSAGE}]
    st.session_state.pop("agent", None)
    st.session_state.pop("research_runtime", None)
    st.session_state.pop("research_autostart_run_id", None)


def _query_task_id() -> str | None:
    raw_task_id = st.query_params.get("task")
    if not raw_task_id:
        return None
    try:
        return validate_task_id(raw_task_id)
    except (TypeError, ValueError):
        return None


@st.cache_data(ttl=60, show_spinner=False)
def _runtime_observability(
    persist_directory: str,
    collection_name: str,
    expected_corpus_fingerprint: str,
    expected_registry_fingerprint: str,
    expected_source_count: int | None,
    expected_chunk_count: int | None,
) -> dict:
    return load_runtime_observability(
        persist_directory=persist_directory,
        collection_name=collection_name,
        expected_corpus_fingerprint=expected_corpus_fingerprint,
        expected_registry_fingerprint=expected_registry_fingerprint,
        expected_source_count=expected_source_count,
        expected_chunk_count=expected_chunk_count,
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
    with st.sidebar.expander("编辑任务记忆", expanded=enabled and not task_memory.is_empty):
        if not enabled:
            st.caption("启用任务记忆后可编辑")
            return

        st.caption("可编辑：主题、确认来源、阶段结论、证据缺口和待解决问题。")

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
    stability_gate = runtime_status.get("stability_gate") or {}
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

        st.caption("连续稳定性 Gate")
        selected_runs = stability_gate.get("selected_run_ids", [])
        st.write("通过" if stability_gate.get("gate_pass") else "未通过")
        st.write(
            f"正式运行 {len(selected_runs)} / "
            f"{stability_gate.get('required_run_count', 3)}"
        )


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
    rows = build_tool_trace_rows(trace, mark_pending_interrupted=run_failed)
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
    error_code = str(message.get("error_code") or "")
    if not trace and not sources and not memory_changes and not error_code:
        return

    with st.expander("运行详情"):
        if error_code:
            st.error(f"运行错误：{error_code}")
        source_tab, trace_tab, memory_tab = st.tabs(["来源", "工具轨迹", "记忆变更"])
        with source_tab:
            _render_sources(sources)
        with trace_tab:
            _render_trace(trace, run_failed=bool(message.get("error")))
        with memory_tab:
            _render_memory_changes(memory_changes)


@st.cache_resource(show_spinner=False)
def _research_service() -> ResearchRunService:
    return ResearchRunService(ResearchRunStore())


def _load_research_runtime(agent: ReactAgent, runtime_status: dict):
    try:
        identity = execution_identity_from_observability(runtime_status)
        if identity.code_dirty:
            raise ResearchControlError(
                "research_identity_unstable",
                "recoverable research runs require a clean code identity",
            )
    except ResearchControlError as exc:
        st.session_state.pop("research_runtime", None)
        return None, exc.error_code

    runtime = st.session_state.get("research_runtime")
    if (
        not isinstance(runtime, ResearchAgentRuntime)
        or runtime.agent is not agent
        or runtime.identity != identity
    ):
        runtime = ResearchAgentRuntime(agent, _research_service(), identity)
        st.session_state["research_runtime"] = runtime
    return runtime, ""


def _research_execute_button_config(run) -> tuple[str, str, str | None]:
    taking_over = run.status == "running" and run.current_step_id is not None
    if run.status == "planned":
        return "开始执行", "primary", None
    if taking_over:
        return (
            "接管并重试",
            "secondary",
            "当前步骤可能仍由另一会话执行；接管后旧执行器会停止，本步骤重新执行。",
        )
    return "继续执行", "primary", None


def _render_research_plan(plan, runtime, identity_error: str) -> str:
    st.subheader("研究执行")
    if plan is None:
        if identity_error:
            st.error(f"研究执行不可用：{identity_error}")
        else:
            st.caption("暂无研究运行")
        return ""

    run = plan.run
    completed_steps = sum(
        step.status in {"completed", "skipped"} for step in plan.steps
    )
    budget = getattr(runtime.agent, "execution_budget", None) if runtime else None
    tool_limit = getattr(budget, "tool_call_limit", "-")
    model_limit = getattr(budget, "model_call_limit", "-")
    status_column, step_column, tool_column, model_column = st.columns(4)
    status_column.metric("运行状态", run_status_label(plan))
    step_column.metric("步骤", f"{completed_steps} / {len(plan.steps)}")
    tool_column.metric("工具调用（累计/单次）", f"{run.tool_call_count} / {tool_limit}")
    model_column.metric("模型调用（累计/单次）", f"{run.model_call_count} / {model_limit}")
    st.progress(research_progress(plan))
    st.caption(f"目标：{run.goal}")
    st.dataframe(build_step_rows(plan), use_container_width=True, hide_index=True)

    if run.stop_reason:
        st.warning(f"停止原因：{run.stop_reason}")
    st.caption(f"run {run.run_id} · revision {run.revision}")

    finding_tab, evidence_tab = st.tabs(["研究结论", "证据"])
    with finding_tab:
        finding_rows = build_finding_rows(plan)
        if finding_rows:
            st.dataframe(finding_rows, use_container_width=True, hide_index=True)
        else:
            st.caption("暂无研究结论")
    with evidence_tab:
        evidence_rows = build_evidence_rows(plan)
        if evidence_rows:
            st.dataframe(evidence_rows, use_container_width=True, hide_index=True)
        else:
            st.caption("暂无证据")

    active = is_active_plan(plan)
    execute_column, pause_column, cancel_column = st.columns(3)
    execute_label, execute_type, execute_help = _research_execute_button_config(run)
    execute = execute_column.button(
        execute_label,
        type=execute_type,
        use_container_width=True,
        disabled=not active or runtime is None,
        help=execute_help,
        key=f"research_execute_{run.run_id}",
    )
    pause = pause_column.button(
        "暂停",
        use_container_width=True,
        disabled=run.status not in {"planned", "running"},
        key=f"research_pause_{run.run_id}",
    )
    cancel = cancel_column.button(
        "取消",
        use_container_width=True,
        disabled=not active,
        key=f"research_cancel_{run.run_id}",
    )
    if identity_error:
        st.error(f"研究执行不可用：{identity_error}")
    if execute:
        return "execute"
    if pause:
        return "pause"
    if cancel:
        return "cancel"
    return ""


def _render_conversation_context(agent) -> None:
    snapshot = None
    event_count = 0
    read_error = ""
    try:
        snapshot = agent.get_conversation_context()
    except Exception as exc:
        read_error = "会话压缩状态读取失败"
        logger.warning("failed to read conversation compression state: %s", exc)
    else:
        context_middleware = getattr(agent, "context_middleware", None)
        if snapshot is not None and context_middleware is not None:
            try:
                events = context_middleware.store.list_events(agent.session_id)
                event_count = len(events)
            except Exception as exc:
                event_count = snapshot.revision
                read_error = "压缩次数读取失败，已使用 revision"
                logger.warning("failed to read conversation compression events: %s", exc)

    view = build_conversation_context_view(snapshot, event_count)
    with st.expander("会话压缩状态", expanded=view["available"]):
        if read_error:
            st.error(read_error)
        if not view["available"]:
            st.caption("尚未触发会话压缩")
            return

        revision_column, count_column, token_column, retained_column = st.columns(4)
        revision_column.metric("Revision", view["revision"])
        count_column.metric("压缩次数", view["compression_count"])
        token_column.metric(
            "Token 降幅",
            f'{view["token_reduction"]} '
            f'({view["token_reduction_ratio"]:.1%})',
        )
        retained_column.metric("保留消息", view["retained_messages"])

        st.caption(f'摘要模型：{view["summary_model"]}')
        if view["fallback_reason"]:
            st.caption(f'降级原因：{view["fallback_reason"]}')
        else:
            st.caption("降级状态：未触发")

        summary = view["summary"]
        summary_payload = {
            "goal": summary["goal"],
            "user_constraints": list(summary["user_constraints"]),
            "confirmed_findings": [
                {
                    "claim": finding["claim"],
                    "evidence_ids": list(finding["evidence_ids"]),
                }
                for finding in summary["confirmed_findings"]
            ],
            "decisions": list(summary["decisions"]),
            "unresolved_questions": list(summary["unresolved_questions"]),
            "failed_attempts": list(summary["failed_attempts"]),
            "referenced_source_ids": list(summary["referenced_source_ids"]),
        }
        st.json(summary_payload)


def _load_model_gateway_view(agent) -> dict[str, object]:
    model_routes = dict(getattr(agent, "model_routes", {}) or {})

    def with_routes(view: dict[str, object]) -> dict[str, object]:
        view["model_routes"] = model_routes
        return view

    configuration_status = str(
        getattr(agent, "local_model_gateway_status", "not_configured")
    )
    gateway = getattr(agent, "local_model_gateway", None)
    if gateway is None:
        return with_routes(
            build_model_gateway_view(
                None,
                None,
                configuration_status=configuration_status,
            )
        )
    try:
        snapshot = gateway.probe_snapshot()
    except Exception:
        logger.warning("failed to probe local model gateway")
        return with_routes(
            build_model_gateway_view(
                None,
                None,
                configuration_status=configuration_status,
            )
        )
    return with_routes(
        build_model_gateway_view(
            snapshot,
            snapshot.last_route,
            configuration_status=configuration_status,
        )
    )


def _render_model_gateway_sidebar(view: dict[str, object]) -> None:
    primary_model = str(view.get("primary_model") or "")
    if not primary_model:
        status = str(view.get("configuration_status") or "not_configured")
        status_label = {
            "not_configured": "RAG 本地服务未配置",
            "disabled_by_config": "已配置但未启用",
            "disabled_by_route": "RAG 选择云端",
            "unhealthy": "RAG 本地服务异常",
        }.get(status, "RAG 本地服务不可用")
        st.sidebar.caption(f"本地模型：{status_label}")
        return
    ready = str(view.get("ready") or "unknown")
    if not view.get("available"):
        ready_label = "离线"
    else:
        ready_label = {"ready": "就绪", "not_ready": "未就绪"}.get(
            ready,
            "未知",
        )
    circuit = str(view.get("circuit_state") or "unknown")
    circuit_label = {
        "closed": "关闭",
        "open": "打开",
        "half_open": "半开",
    }.get(circuit, "未知")
    st.sidebar.caption(f"本地模型：{ready_label} · 熔断：{circuit_label}")


def _render_model_gateway(view: dict[str, object]) -> None:
    fallback_reason = str(view.get("fallback_reason") or "")
    model_routes = view.get("model_routes") or {}
    route_summary = " / ".join(
        f"{MODEL_ROLE_LABELS[role]}={MODEL_ROUTE_LABELS.get(str(model_routes.get(role)), '未配置')}"
        for role in MODEL_ROLES
    )
    with st.expander("模型路由", expanded=bool(fallback_reason)):
        st.caption(route_summary)
        primary_model = str(view.get("primary_model") or "")
        if not primary_model:
            status = str(view.get("configuration_status") or "not_configured")
            message = {
                "not_configured": (
                    "当前 RAG 路由没有可用的本地模型服务。"
                ),
                "disabled_by_config": "本地模型服务未启用。",
                "disabled_by_route": "RAG 生成当前选择云端。",
                "unhealthy": "本地 RAG 服务初始化失败，请求会转到 RAG 的云端配置。",
            }.get(status, "本地 RAG 服务当前不可用，请求会转到云端配置。")
            st.info(message)
            return

        profile = str(view.get("profile") or "未识别")
        backend = str(view.get("backend") or "未知")
        quantization = str(view.get("quantization") or "未知")
        st.caption(f"部署：{profile} · {backend} · {quantization}")
        st.caption("此处显示 RAG 本地 Gateway 的最近一次请求；Planner 和摘要分别记录自己的路由。")
        st.write(f"主模型：{primary_model}")

        actual_model = str(view.get("actual_model") or "")
        if not actual_model:
            st.caption("暂无模型请求")
            return
        st.write(f"实际模型：{actual_model}")
        if fallback_reason:
            st.warning(f"已降级：{fallback_reason}")
        else:
            st.caption("降级状态：未触发")

        ttft = view.get("ttft_seconds")
        latency = view.get("latency_seconds")
        input_tokens = view.get("input_tokens")
        output_tokens = view.get("output_tokens")
        ttft_column, latency_column, input_column, output_column = st.columns(4)
        ttft_column.metric("TTFT", f"{ttft:.3f}s" if isinstance(ttft, float) else "-")
        latency_column.metric(
            "总延迟",
            f"{latency:.3f}s" if isinstance(latency, float) else "-",
        )
        input_column.metric(
            "输入 Token",
            input_tokens if isinstance(input_tokens, int) else "-",
        )
        output_column.metric(
            "输出 Token",
            output_tokens if isinstance(output_tokens, int) else "-",
        )
        st.caption(f'请求 ID：{view.get("request_id") or "-"}')


def _ensure_user_message(goal: str) -> None:
    if any(
        message.get("role") == "user" and message.get("content") == goal
        for message in st.session_state["message"]
    ):
        return
    st.session_state["message"].append({"role": "user", "content": goal})


def _execute_research_run(runtime: ResearchAgentRuntime, run_id: str) -> None:
    agent = runtime.agent
    before_memory = agent.get_task_memory()
    trace = []
    answer_parts = []
    has_error = False
    error_code = ""
    used_tools = set()
    source_observations = []
    max_elapsed_ms = 0
    with st.chat_message("assistant"):
        run_status = st.status("Agent 执行中", expanded=True)
        answer_placeholder = st.empty()
        for event in runtime.execute_events(run_id):
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
                error_code = event.error_code or "agent_execution_failed"
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
        sources = merge_source_observations(retrieval_sources, source_observations)
        assistant_message = {
            "role": "assistant",
            "content": answer,
            "trace": trace,
            "sources": sources,
            "memory_changes": diff_task_memory(before_memory, after_memory),
            "elapsed_ms": max_elapsed_ms,
            "error": has_error,
            "error_code": error_code,
            "research_run_id": run_id,
        }
        st.session_state["message"].append(assistant_message)
        _render_assistant_details(assistant_message)


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
try:
    runtime_model_config = load_runtime_config()
    configured_model_routes = {
        role: runtime_model_config.role(role).route for role in MODEL_ROLES
    }
except Exception:
    runtime_model_config = None
    configured_model_routes = {role: "cloud" for role in MODEL_ROLES}
if "persisted_model_routes" not in st.session_state:
    st.session_state["persisted_model_routes"] = dict(configured_model_routes)
for role in MODEL_ROLES:
    key = f"model_route_{role}"
    if key not in st.session_state:
        st.session_state[key] = configured_model_routes[role]

runtime_status = _runtime_observability(
    config.persist_directory,
    config.collection_name,
    config.expected_corpus_fingerprint,
    config.expected_registry_fingerprint,
    config.expected_source_count,
    config.expected_chunk_count,
)

st.title("LocalRAG 研究助手")
st.caption(f"任务 {st.session_state['task_id']}")
_render_runtime_header(runtime_status)
st.divider()

memory_enabled = st.sidebar.checkbox("启用任务记忆", key="task_memory_enabled")
research_service = _research_service()
try:
    research_plan = research_service.get_latest_plan(st.session_state["task_id"])
    research_identity_error = None
except ResearchControlError as exc:
    research_plan = None
    research_identity_error = exc.error_code
research_active = is_active_plan(research_plan)

st.sidebar.subheader("模型路由")
selected_model_routes: dict[str, str] = {}
for role in MODEL_ROLES:
    local_verified = bool(
        runtime_model_config is not None
        and runtime_model_config.role(role).local.tool_calling_verified
    )

    def route_label(
        value: str,
        *,
        current_role: str = role,
        verified: bool = local_verified,
    ) -> str:
        label = MODEL_ROUTE_LABELS[value]
        if current_role == "planner" and value == "local" and not verified:
            return f"{label} · tool calling 未验证"
        return label

    selected_model_routes[role] = st.sidebar.selectbox(
        MODEL_ROLE_LABELS[role],
        list(MODEL_ROUTE_MODES),
        format_func=route_label,
        key=f"model_route_{role}",
        disabled=research_active,
    )
if research_active:
    st.sidebar.caption("研究任务运行期间不能切换模型路由。")

persisted_model_routes = dict(st.session_state["persisted_model_routes"])
if selected_model_routes != persisted_model_routes:
    try:
        update_model_routes(selected_model_routes)
        st.session_state["persisted_model_routes"] = dict(selected_model_routes)
    except Exception:
        logger.exception("Failed to persist model routes")
        st.sidebar.error("模型路由保存失败，继续使用上一次配置。")
        selected_model_routes = persisted_model_routes

if (
    "agent" not in st.session_state
    or getattr(st.session_state["agent"], "session_id", None) != st.session_state["session_id"]
    or getattr(st.session_state["agent"], "task_id", None) != st.session_state["task_id"]
    or getattr(st.session_state["agent"], "model_routes", {}) != selected_model_routes
):
    st.session_state["agent"] = ReactAgent(
        session_id=st.session_state["session_id"],
        task_id=st.session_state["task_id"],
        task_memory_enabled=memory_enabled,
        model_routes=selected_model_routes,
    )

agent = st.session_state["agent"]
agent.set_task_memory_enabled(memory_enabled)
research_runtime, research_identity_error = _load_research_runtime(
    agent,
    runtime_status,
)

st.sidebar.subheader("研究任务")
st.sidebar.caption(st.session_state["task_id"])
new_task_column, clear_memory_column = st.sidebar.columns(2)
if new_task_column.button("新任务", use_container_width=True):
    new_task_id = _new_runtime_id()
    _reset_runtime_for_task(new_task_id)
    st.query_params["task"] = new_task_id
    st.rerun()
if clear_memory_column.button(
    "清除记忆",
    use_container_width=True,
    disabled=research_active,
):
    agent.clear_task_memory()
    _clear_memory_editor_state()
    st.rerun()

task_memory = agent.get_task_memory()
with st.sidebar.expander("任务记忆", expanded=not task_memory.is_empty):
    if task_memory.is_empty:
        st.caption("当前任务暂无持久化记忆")
    else:
        st.json(_memory_payload(task_memory))
        st.caption(
            "已检索问题和检索命中来源由系统自动记录；其余字段需要用户确认后，"
            "在下方“编辑任务记忆”中保存。"
        )

_render_memory_editor(agent, task_memory, enabled=memory_enabled)
_render_runtime_sidebar(runtime_status)
model_gateway_view = _load_model_gateway_view(agent)
_render_model_gateway_sidebar(model_gateway_view)

research_action = _render_research_plan(
    research_plan,
    research_runtime,
    research_identity_error,
)
_render_conversation_context(agent)
_render_model_gateway(model_gateway_view)
research_run_to_execute = ""
if research_action and research_plan is not None:
    try:
        if research_action == "execute":
            _ensure_user_message(research_plan.run.goal)
            research_run_to_execute = research_plan.run.run_id
        elif research_action == "pause":
            research_service.pause_run(
                research_plan.run.run_id,
                expected_revision=research_plan.run.revision,
            )
        elif research_action == "cancel":
            research_service.cancel_run(
                research_plan.run.run_id,
                expected_revision=research_plan.run.revision,
            )
    except (ResearchControlError, ResearchRevisionConflictError, ResearchStateError) as exc:
        error_code = getattr(exc, "error_code", "research_control_failed")
        st.error(f"研究控制失败：{error_code}")
    else:
        if research_action != "execute":
            st.rerun()

st.divider()

for message in st.session_state["message"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            _render_assistant_details(message)

autostart_run_id = st.session_state.pop("research_autostart_run_id", "")
if autostart_run_id:
    if (
        research_runtime is not None
        and research_plan is not None
        and research_plan.run.run_id == autostart_run_id
        and is_active_plan(research_plan)
    ):
        research_run_to_execute = autostart_run_id
    else:
        st.session_state["message"].append(
            {
                "role": "assistant",
                "content": "研究任务启动失败，请检查运行状态后重试。",
                "error": True,
                "error_code": research_identity_error or "research_runtime_unavailable",
            }
        )
        st.rerun()

if research_run_to_execute:
    _execute_research_run(research_runtime, research_run_to_execute)
    st.rerun()

prompt = st.chat_input(
    "输入研究问题",
    disabled=research_active or research_runtime is None,
)
if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    if research_runtime is None:
        st.session_state["message"].append(
            {
                "role": "assistant",
                "content": "研究任务创建失败，请检查运行状态后重试。",
                "error": True,
                "error_code": research_identity_error or "research_runtime_unavailable",
            }
        )
    else:
        try:
            research_plan = research_runtime.create_run(prompt)
        except (ResearchControlError, ResearchRevisionConflictError, ResearchStateError) as exc:
            error_code = getattr(exc, "error_code", "research_control_failed")
            content = (
                "当前研究任务尚未结束，请在研究执行区域继续或取消当前任务后再提问。"
                if error_code == "research_run_active"
                else "研究任务创建失败，请检查运行状态后重试。"
            )
            st.session_state["message"].append(
                {
                    "role": "assistant",
                    "content": content,
                    "error": True,
                    "error_code": error_code,
                }
            )
        else:
            st.session_state["research_autostart_run_id"] = research_plan.run.run_id
    st.rerun()
