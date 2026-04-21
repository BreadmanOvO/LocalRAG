import hashlib
import os
import sys
import sqlite3
from langchain_community.embeddings import DashScopeEmbeddings
import datetime
import config_data as config
from chunking import choose_chunking_strategy, chunk_text_baseline, chunk_text_doc_type_aware
from runtime_keys import load_bailian_runtime_config

if tuple(map(int, sqlite3.sqlite_version.split("."))) < (3, 35, 0):
    import pysqlite3

    sys.modules["sqlite3"] = pysqlite3

from langchain_chroma import Chroma

def check_md5(md5_str: str):
    # 检查传入的md5值是否已经传入，True表示已经传入，False表示没有传入
    if not os.path.exists(config.md5_path):
        # 不存在，创建一个空文件
        open(config.md5_path, "w", encoding='utf-8').close()
        return False
    else:
        with open(config.md5_path, "r", encoding='utf-8') as f:
            for md5 in f:
                if md5_str == md5.strip():
                    return True
        return False

def save_md5(md5_str: str):
    # 保存传入的md5值
    with open(config.md5_path, "a", encoding='utf-8') as f:
        f.write(md5_str + "\n")

def get_string_md5(input_str : str, encoding_style="utf-8"):
    # 获取传入的字符串的md5值
    # 将字符串转换成字节串
    input_bytes = input_str.encode(encoding=encoding_style)
    return hashlib.md5(input_bytes).hexdigest()
    # 一次性返回对大文件不友好，可以循环读取大文件，每次读取一部分，然后计算md5值
    # md5_obj = hashlib.md5()
    # with open(file_path, "rb") as f:
    #     while True:
    #         chunk = f.read(chunk_size)  # 读一块
    #         if not chunk:               # 读完了
    #             break
    #         md5_obj.update(chunk)       # 用这一块更新 MD5

    # return md5_obj.hexdigest()

class KnowledgeBaseService(object):
    def __init__(self) -> None:
        runtime_config = load_bailian_runtime_config()
        os.makedirs(config.persist_directory, exist_ok=True)
        # Chroma向量库对象，用来存储向量数据
        self.chroma = Chroma(
            collection_name=config.collection_name, # 数据库的表名
            embedding_function=DashScopeEmbeddings(
                model=runtime_config.embedding_model_name,
                dashscope_api_key=runtime_config.dashscope_api_key,
            ),
            persist_directory=config.persist_directory, # 数据库本地存储文件夹
        )

    def _build_upload_source_metadata(self, filename: str) -> dict:
        return {
            "source": filename,
            "source_id": f"upload::{filename}",
            "doc_type": "untyped",
            "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": config.uploader,
        }

    def _chunk_upload(self, data: str, source_metadata: dict, chunking_strategy: str | None = None):
        chunk_strategy = choose_chunking_strategy(
            source_metadata["doc_type"],
            chunking_strategy or getattr(config, "chunking_strategy", "baseline"),
        )
        if chunk_strategy == "doc_type_aware":
            return chunk_text_doc_type_aware(data, source_metadata=source_metadata)
        return chunk_text_baseline(data, source_metadata=source_metadata)

    def _add_chunk_records(self, chunk_records):
        self.chroma.add_texts(
            texts=[record.text for record in chunk_records],
            metadatas=[record.metadata for record in chunk_records]
        )

    def ingest_document(self, data: str, source_metadata: dict, chunking_strategy: str | None = None):
        chunk_records = self._chunk_upload(data, source_metadata, chunking_strategy=chunking_strategy)
        self._add_chunk_records(chunk_records)
        return chunk_records

    def upload_by_str(self, data: str, filename):
        # 将传入字符串向量化，并上传到向量库
        data_md5_hex = get_string_md5(data)
        if check_md5(data_md5_hex):
            return "【失败】该数据已存在知识库中，请勿重复上传"
        else:
            source_metadata = self._build_upload_source_metadata(filename)
            self.ingest_document(data, source_metadata)

            save_md5(data_md5_hex)
            return "【成功】向数据库更新成功"
