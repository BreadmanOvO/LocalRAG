import uuid

import streamlit as st

from agent import ReactAgent
from utils.session import validate_task_id


WELCOME_MESSAGE = "你好，我是自动驾驶领域的问答助手，有什么可以帮助你？"


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


requested_task_id = _query_task_id()
if "task_id" not in st.session_state:
    _reset_runtime_for_task(requested_task_id or _new_runtime_id())
elif requested_task_id and requested_task_id != st.session_state["task_id"]:
    _reset_runtime_for_task(requested_task_id)

if st.query_params.get("task") != st.session_state["task_id"]:
    st.query_params["task"] = st.session_state["task_id"]

st.title("自动驾驶问答助手")
st.divider()

if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": WELCOME_MESSAGE}]

if "session_id" not in st.session_state:
    st.session_state["session_id"] = _new_runtime_id()

if "task_memory_enabled" not in st.session_state:
    st.session_state["task_memory_enabled"] = True

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
st.sidebar.code(st.session_state["task_id"], language=None)
new_task_column, clear_memory_column = st.sidebar.columns(2)
if new_task_column.button("新任务", use_container_width=True):
    new_task_id = _new_runtime_id()
    _reset_runtime_for_task(new_task_id)
    st.query_params["task"] = new_task_id
    st.rerun()
if clear_memory_column.button("清除记忆", use_container_width=True):
    agent.clear_task_memory()
    st.rerun()

task_memory = agent.get_task_memory()
with st.sidebar.expander("任务记忆", expanded=not task_memory.is_empty):
    if task_memory.is_empty:
        st.caption("当前任务暂无持久化记忆")
    else:
        st.json(
            {
                "主题": task_memory.topic,
                "已检索问题": list(task_memory.searched_queries),
                "检索命中来源": list(task_memory.retrieved_sources),
                "已确认来源": list(task_memory.confirmed_sources),
                "阶段结论": list(task_memory.findings),
                "证据缺口": list(task_memory.evidence_gaps),
                "待解决问题": list(task_memory.open_questions),
            }
        )

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    ai_res_list = []
    with st.spinner("思考中..."):
        response_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator):
            for chunk in generator:
                ai_res_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(response_stream))
        st.session_state["message"].append({"role": "assistant", "content": "".join(ai_res_list)})
        st.rerun()
