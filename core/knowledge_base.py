import hashlib
import os
import sys
import sqlite3
import datetime
from config import settings as config
from core.chunking import choose_chunking_strategy, chunk_text_baseline, chunk_text_doc_type_aware, chunk_text_semantic
from config.runtime_keys import load_runtime_config
from config.provider_factory import build_embedding_model

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
    def __init__(
        self,
        *,
        persist_directory: str | os.PathLike[str] | None = None,
        collection_name: str | None = None,
        embedding_model=None,
    ) -> None:
        runtime_config = load_runtime_config()
        persist_directory = persist_directory or config.persist_directory
        collection_name = collection_name or config.collection_name
        os.makedirs(persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=collection_name,
            embedding_function=(
                embedding_model
                if embedding_model is not None
                else build_embedding_model(runtime_config)
            ),
            persist_directory=str(persist_directory),
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
        if chunk_strategy == "semantic":
            return chunk_text_semantic(data, source_metadata=source_metadata)
        return chunk_text_baseline(data, source_metadata=source_metadata)

    def _add_chunk_records(self, chunk_records, *, ids: list[str] | None = None):
        kwargs = {
            "texts": [record.text for record in chunk_records],
            "metadatas": [record.metadata for record in chunk_records],
        }
        if ids is not None:
            if len(ids) != len(chunk_records):
                raise ValueError("ids length must match chunk_records length")
            kwargs["ids"] = ids
        self.chroma.add_texts(**kwargs)

    def add_chunk_records(self, chunk_records, *, ids: list[str] | None = None):
        """Persist already-cleaned chunks.

        The ingestion workflow uses this method so staging never writes to the
        active collection.  The original private method and ``upload_by_str``
        remain compatible with existing callers.
        """
        self._add_chunk_records(chunk_records, ids=ids)

    @staticmethod
    def chunk_record_id(source_id: str, chunk_record) -> str:
        """Return a deterministic Chroma id for an ingested chunk."""
        order = chunk_record.metadata.get("chunk_order", 0)
        strategy = chunk_record.metadata.get("chunk_strategy", "baseline")
        return hashlib.sha256(
            f"{source_id}\0{strategy}\0{order}\0{chunk_record.text}".encode("utf-8")
        ).hexdigest()

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
