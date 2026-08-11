import os

from config.corpus_profile import load_active_corpus_profile


############################################################
version = "1.4.1"
author = "breadman"
email = "gluweinzhu@hotmail.com"
description = "A local RAG system"
############################################################
uploader = "breadman"

# md5文件路径
md5_path = "./md5.txt"

# Chroma 参数
active_corpus_profile = load_active_corpus_profile()
collection_name = os.environ.get(
    "LOCALRAG_COLLECTION_NAME",
    active_corpus_profile.collection_name,
)  # 数据库的表名
persist_directory = os.environ.get(
    "LOCALRAG_PERSIST_DIRECTORY",
    str(active_corpus_profile.persist_directory),
)  # 数据库本地存储文件夹路径
using_active_corpus_profile = "LOCALRAG_PERSIST_DIRECTORY" not in os.environ
expected_corpus_fingerprint = (
    active_corpus_profile.corpus_fingerprint if using_active_corpus_profile else ""
)
expected_registry_fingerprint = (
    active_corpus_profile.registry_fingerprint if using_active_corpus_profile else ""
)
expected_source_count = active_corpus_profile.source_count if using_active_corpus_profile else None
expected_chunk_count = active_corpus_profile.chunk_count if using_active_corpus_profile else None

# RecursiveCharacterTextSplitter 参数
chunk_size = 500
chunk_overlap = 50
separators = ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
min_split_length = 500 # 文本分割的最小长度
chunking_strategy = "baseline"
doc_type_chunking = {
    "official_doc": {"chunk_size": 500, "chunk_overlap": 50},
    "standard": {"chunk_size": 900, "chunk_overlap": 100},
    "paper": {"chunk_size": 700, "chunk_overlap": 80},
    "report": {"chunk_size": 700, "chunk_overlap": 80},
}

# Semantic chunking 参数
semantic_chunk_threshold = 0.5  # 相邻句子余弦相似度断点阈值
semantic_max_chunk_size = 1000  # 语义段最大字符数，超长则二次拆分
semantic_embedding_model = "models/bge-m3"  # 本地模型路径，fallback 到 HuggingFace

# VectorStoreService 参数
similarity_top_k = 5 # 相似度top k
retrieval_debug_top_k = 10 # 调试/实验分析使用的候选召回 top k
retrieval_candidate_top_k = 20 # Dense/BM25 分别召回的候选数量
retrieval_rrf_k = 60 # Reciprocal Rank Fusion 常量
same_source_context_extension_per_source = 1 # 生成前从调试候选中为已命中 source_id 追加的同源 chunk 数

# 模型参数
embedding_model_name = "text-embedding-v4"
chat_model_name = "gpt-5.4"
