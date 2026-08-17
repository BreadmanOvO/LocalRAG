"""Streamlit UI for staged document ingestion.

Uploading only prepares a pending document.  A separate publish action is
required before the active Chroma collection and source registry are changed.
"""
import hashlib
import json

import streamlit as st

from core.ingestion_workflow import IngestionWorkflow
from core.knowledge_base import KnowledgeBaseService


st.title("知识库更新服务")
st.caption("上传后会先清洗、分块并生成预览；确认后再发布到正式知识库。")

uploader_file = st.file_uploader(
    "上传知识库文件",
    type=["txt", "md", "markdown"],
    accept_multiple_files=False,
    key="file_uploader",
    help="支持 UTF-8 或 GBK 编码的文本/Markdown 文件",
)

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()
if "ingestion_workflow" not in st.session_state:
    st.session_state["ingestion_workflow"] = IngestionWorkflow(
        knowledge_base=st.session_state["service"]
    )


if uploader_file is not None:
    file_name = uploader_file.name
    file_size = uploader_file.size / 1024
    st.subheader(f"上传文件信息：{file_name}")
    st.write(f"文件类型：{uploader_file.type or 'unknown'}, 文件大小：{file_size:.2f} KB")

    raw_bytes = uploader_file.getvalue()
    try:
        try:
            text = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw_bytes.decode("gbk")
    except UnicodeDecodeError:
        st.error("文件编码无法识别，请使用 UTF-8 或 GBK 编码后重试。")
        st.stop()

    col1, col2, col3 = st.columns(3)
    with col1:
        doc_type = st.selectbox(
            "文档类型",
            ["untyped", "official_doc", "standard", "paper", "report"],
            help="选择结构化类型可启用按页/标题分块；untyped 使用 baseline。",
        )
    with col2:
        category = st.text_input("分类", value="uploads")
    with col3:
        language = st.text_input("语言", value="unknown")
    topic_tags = st.text_input("主题标签（逗号分隔）", value="")
    chunking_strategy = st.selectbox(
        "分块策略",
        ["baseline", "doc_type_aware", "semantic"],
        help="semantic 需要本地语义嵌入模型，耗时更长。",
    )

    metadata = {
        "doc_type": doc_type,
        "category": category,
        "language": language,
        "topic_tags": topic_tags,
    }
    signature = hashlib.sha256(
        raw_bytes + json.dumps(metadata, ensure_ascii=False, sort_keys=True).encode("utf-8")
        + chunking_strategy.encode("ascii")
    ).hexdigest()

    if st.session_state.get("staged_signature") != signature:
        with st.spinner("清洗并分块中（暂不写入正式知识库）..."):
            try:
                st.session_state["staged_document"] = st.session_state["ingestion_workflow"].stage_text(
                    text,
                    file_name,
                    metadata=metadata,
                    chunking_strategy=chunking_strategy,
                )
                st.session_state["staged_signature"] = signature
                st.session_state.pop("publish_result", None)
            except Exception as exc:
                st.error(f"预处理失败：{exc}")
                st.stop()

    staged = st.session_state.get("staged_document")
    workflow: IngestionWorkflow = st.session_state["ingestion_workflow"]
    if staged is not None:
        preview = workflow.preview(staged)
        st.success(f"已暂存：{preview['source_id']}，共 {preview['chunk_count']} 个 chunk。")
        st.text_area("规范化文本预览", preview["text_preview"], height=160, disabled=True)
        st.write("首个 chunk 预览")
        for item in preview["chunks"][:3]:
            st.code(item["text"], language="text")

        evaluate = st.checkbox(
            "发布后运行评测（可选）",
            value=False,
            help="默认跳过耗时评测。通过 API 注入 evaluator 后才会执行；评测失败不会撤销已发布内容。",
        )
        if st.button("发布到正式知识库", type="primary"):
            with st.spinner("发布中：写入 Chroma、registry 和 active profile..."):
                result = workflow.publish(
                    staged,
                    evaluate=evaluate,
                    evaluator=st.session_state.get("ingestion_evaluator"),
                    rag_service=st.session_state.get("rag_service"),
                )
            st.session_state["publish_result"] = result
            if result.published:
                st.success(f"发布成功：{result.source_id}（{result.chunk_count} 个 chunk）。")
                if result.sparse_index_refreshed:
                    st.info("BM25 稀疏索引已刷新；问答服务若在独立进程，请重建 RagService。")
                else:
                    message = "内容已发布，但当前进程未提供 BM25 刷新回调；问答服务需刷新/重启。"
                    if result.sparse_index_error:
                        message = f"内容已发布，但 BM25 刷新失败：{result.sparse_index_error}"
                    st.warning(message)
                if result.evaluation_error:
                    st.warning(f"评测未执行或失败：{result.evaluation_error}")
            else:
                st.info(f"无需重复发布：{result.reason or 'already_published'}")
