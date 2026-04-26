# import time
import streamlit as st
from core.knowledge_base import KnowledgeBaseService

# 页面标题
st.title("知识库更新服务")

# 上传文件
uploader_file = st.file_uploader(
    "上传知识库文件",
    type=["txt"],
    accept_multiple_files=False, # accept_multiple_files 如果是True，则上传多个文件
                                 # uploader_file是一个列表，每个元素是一个文件对象 
    key="file_uploader", 
    help="上传知识库文件，支持txt格式"
)

# streamlit特性：当web页面元素发生变化，代码会重新执行，造成资源浪费
# 内置的session_state可以存储变量，刷新页面，变量值不变
# session_state是字典
if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()


if uploader_file is not None:
    # 处理上传的文件
    file_name = uploader_file.name
    file_type = uploader_file.type
    file_size = uploader_file.size / 1024 # KB
    st.subheader(f"上传文件信息：{file_name}")
    st.write(f"文件类型：{file_type}, 文件大小：{file_size:.2f} KB")
    raw_bytes = uploader_file.getvalue()
    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = raw_bytes.decode("gbk")
        except UnicodeDecodeError:
            st.error("文件编码无法识别，请使用 UTF-8 或 GBK 编码后重试。")
            st.stop()

    with st.spinner("载入知识库中..."):    # spinner执行过程中显示转圈动画
        # result = st.session_state['service'].upload_by_str(text, file_name)
        service: KnowledgeBaseService = st.session_state["service"]
        result = service.upload_by_str(text, file_name)
        st.write(result)

