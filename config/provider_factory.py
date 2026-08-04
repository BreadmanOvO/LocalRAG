from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

import httpx
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.runnables import Runnable

from config.model_paths import get_bge_m3_path
from config.runtime_keys import RuntimeProviderConfig

OPENAI_COMPATIBLE_PROVIDERS = {"bailian", "modelscope", "sensenova", "local_embedding", "local_sentence_transformer"}
DEFAULT_CHAT_TIMEOUT_SECONDS = 60
DEFAULT_CHAT_MAX_RETRIES = 0


def _resolve_torch_dtype(torch_module: Any, dtype_name: str):
    if dtype_name == "auto":
        return "auto"
    if dtype_name == "float16":
        return torch_module.float16
    if dtype_name == "bfloat16":
        return torch_module.bfloat16
    if dtype_name == "float32":
        return torch_module.float32
    raise ValueError(f"unsupported torch dtype: {dtype_name}")


def _select_device(torch_module: Any, requested_device: str) -> str:
    if requested_device != "auto":
        return requested_device
    return "cuda" if torch_module.cuda.is_available() else "cpu"


def _message_role(message: Any) -> str:
    message_type = getattr(message, "type", "")
    if message_type == "system":
        return "system"
    if message_type == "ai":
        return "assistant"
    return "user"


def _message_content(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in content
        )
    return str(content)


class LocalTransformersChatModel(Runnable):
    def __init__(
        self,
        model_name: str,
        *,
        device: str = "auto",
        torch_dtype: str = "float16",
        max_new_tokens: int = 128,
        adapter_path: str | None = None,
    ) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.device = _select_device(torch, device)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            local_files_only=True,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=_resolve_torch_dtype(torch, torch_dtype),
            trust_remote_code=True,
            local_files_only=True,
        )
        if self.device == "cuda":
            self.model = self.model.to(self.device)
        if adapter_path:
            from peft import PeftModel

            self.model = PeftModel.from_pretrained(
                self.model,
                adapter_path,
                local_files_only=True,
            )
        self.model.eval()
        self.max_new_tokens = max_new_tokens

    def _format_prompt(self, value: Any) -> str:
        if hasattr(value, "to_messages"):
            messages = [
                {"role": _message_role(message), "content": _message_content(message)}
                for message in value.to_messages()
            ]
            try:
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                    enable_thinking=False,
                )
            except TypeError:
                return self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
        return str(value)

    def invoke(self, input: Any, config: Any | None = None, **kwargs: Any) -> str:
        prompt = self._format_prompt(input)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if self.device == "cuda":
            inputs = inputs.to(self.device)
        input_length = inputs["input_ids"].shape[-1]
        max_new_tokens = int(kwargs.get("max_new_tokens", self.max_new_tokens))
        with self.torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated_ids = outputs[0][input_length:]
        return self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()


class LocalSentenceTransformerEmbeddings:
    def __init__(self, model_name: str | None = None) -> None:
        from sentence_transformers import SentenceTransformer

        resolved_model_name = model_name
        if not resolved_model_name or resolved_model_name == "BAAI/bge-m3":
            resolved_model_name = get_bge_m3_path()
        local_files_only = Path(resolved_model_name).exists()
        self.model = SentenceTransformer(
            resolved_model_name,
            local_files_only=local_files_only,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return [e.tolist() for e in embeddings]

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()


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


def build_agent_chat_model(runtime_config: RuntimeProviderConfig, **overrides):
    if runtime_config.provider == "local_transformers":
        return LocalTransformersChatModel(
            runtime_config.chat_model_name,
            device=overrides.pop("device", runtime_config.device),
            torch_dtype=overrides.pop("torch_dtype", runtime_config.torch_dtype),
            max_new_tokens=int(overrides.pop("max_new_tokens", runtime_config.max_new_tokens)),
            adapter_path=overrides.pop("adapter_path", runtime_config.adapter_path),
        )

    if runtime_config.provider not in OPENAI_COMPATIBLE_PROVIDERS:
        raise ValueError(f"Unsupported runtime provider: {runtime_config.provider}")

    options = {
        "model": runtime_config.chat_model_name,
        "api_key": runtime_config.api_key,
        "base_url": runtime_config.base_url,
        "timeout": DEFAULT_CHAT_TIMEOUT_SECONDS,
        "max_retries": DEFAULT_CHAT_MAX_RETRIES,
    }
    if runtime_config.provider in {"local_embedding", "modelscope", "local_sentence_transformer"} and runtime_config.chat_model_name.startswith("Qwen/Qwen3"):
        options["extra_body"] = {"enable_thinking": False}
    if runtime_config.provider == "sensenova":
        options["http_client"] = httpx.Client(verify=False)
        options["http_async_client"] = httpx.AsyncClient(verify=False)
    options.update(overrides)
    return ChatOpenAI(**options)


def build_chat_model(runtime_config: RuntimeProviderConfig, **overrides):
    return build_agent_chat_model(runtime_config, **overrides)


def build_rag_chat_model(
    runtime_config: RuntimeProviderConfig,
    gateway=None,
    **overrides,
):
    local_config = getattr(runtime_config, "local_model_gateway", None)
    if (
        local_config is not None
        and local_config.rag_generation_enabled
        and gateway is not None
    ):
        return gateway
    return build_agent_chat_model(runtime_config, **overrides)


def build_summary_chat_model(
    runtime_config: RuntimeProviderConfig,
    gateway=None,
    **overrides,
):
    local_config = getattr(runtime_config, "local_model_gateway", None)
    if (
        local_config is not None
        and local_config.conversation_summary_enabled
        and gateway is not None
    ):
        return gateway
    return build_agent_chat_model(runtime_config, **overrides)


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
            model_kwargs={"encoding_format": "float"},
            max_retries=5,
            retry_min_seconds=2,
            retry_max_seconds=30,
        )

    if runtime_config.provider == "local_embedding":
        return LocalHashEmbeddings()

    if runtime_config.provider in ("local_sentence_transformer", "local_transformers", "sensenova"):
        return LocalSentenceTransformerEmbeddings(model_name=runtime_config.embedding_model_name)

    raise ValueError(f"Unsupported runtime provider: {runtime_config.provider}")
