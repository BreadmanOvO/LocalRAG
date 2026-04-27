from __future__ import annotations

import hashlib
import math

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from config.runtime_keys import RuntimeProviderConfig

OPENAI_COMPATIBLE_PROVIDERS = {"bailian", "modelscope", "local_embedding"}


class LocalHashEmbeddings:
    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.split() or [text]:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if not norm:
            return vector
        return [value / norm for value in vector]


def build_chat_model(runtime_config: RuntimeProviderConfig, **overrides):
    if runtime_config.provider not in OPENAI_COMPATIBLE_PROVIDERS:
        raise ValueError(f"Unsupported runtime provider: {runtime_config.provider}")

    options = {
        "model": runtime_config.chat_model_name,
        "api_key": runtime_config.api_key,
        "base_url": runtime_config.base_url,
    }
    if runtime_config.provider == "local_embedding" and runtime_config.chat_model_name.startswith("Qwen/Qwen3"):
        options["extra_body"] = {"enable_thinking": False}
    options.update(overrides)
    return ChatOpenAI(**options)


def build_embedding_model(runtime_config: RuntimeProviderConfig):
    if runtime_config.provider == "bailian":
        return DashScopeEmbeddings(
            model=runtime_config.embedding_model_name,
            dashscope_api_key=runtime_config.api_key,
        )

    if runtime_config.provider == "modelscope":
        return OpenAIEmbeddings(
            model=runtime_config.embedding_model_name,
            api_key=runtime_config.api_key,
            base_url=runtime_config.base_url,
        )

    if runtime_config.provider == "local_embedding":
        return LocalHashEmbeddings()

    raise ValueError(f"Unsupported runtime provider: {runtime_config.provider}")
