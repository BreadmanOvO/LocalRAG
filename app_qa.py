import streamlit as st
import time
from rag import RagService
import config_data as config

st.title("智能助手")
st.divider()

if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "你好，有什么可以帮助你？"}]

if "rag" not in st.session_state:
    st.session_state["rag"] = RagService()

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    ai_res_list = []
    with st.spinner("思考中..."):
        response_stream = st.session_state["rag"].chain.stream({"question": prompt}, config.session_config)
        
        def capture(generator, cache_list):
            for chunk in generator:
                ai_res_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(response_stream, ai_res_list))
        response = st.session_state["message"].append({"role": "assistant", "content": "".join(ai_res_list)})

