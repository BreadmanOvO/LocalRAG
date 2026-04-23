############################################################
version = "1.0.0"
author = "breadman"
email = "gluweinzhu@hotmail.com"
description = "A local RAG system"
############################################################
uploader = "breadman"

# md5文件路径
md5_path = "./md5.txt"

# Chroma 参数
collection_name = "rag" # 数据库的表名
persist_directory = "./chroma_db" # 数据库本地存储文件夹路径

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

# VectorStoreService 参数
similarity_top_k = 5 # 相似度top k
retrieval_debug_top_k = 10 # 调试/实验分析使用的候选召回 top k

# 模型参数
embedding_model_name = "text-embedding-v4"
chat_model_name = "gpt-5.4"
