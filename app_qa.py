# app_qa.py
import streamlit as st
import uuid
from agent import ReactAgent

st.title("自动驾驶问答助手")
st.divider()

if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "你好，我是自动驾驶领域的问答助手，有什么可以帮助你？"}]

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

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
