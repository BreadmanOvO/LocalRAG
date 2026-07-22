import unittest
import tempfile
from pathlib import Path
from unittest import mock

from config.runtime_keys import RuntimeProviderConfig


class ProviderFactoryTests(unittest.TestCase):
    def test_local_sentence_transformer_uses_existing_path_without_network(self):
        from config import provider_factory

        with tempfile.TemporaryDirectory() as temp_dir:
            model_path = str(Path(temp_dir) / "bge-m3")
            Path(model_path).mkdir()
            with mock.patch(
                "sentence_transformers.SentenceTransformer"
            ) as sentence_transformer:
                provider_factory.LocalSentenceTransformerEmbeddings(model_path)

        sentence_transformer.assert_called_once_with(
            model_path,
            local_files_only=True,
        )

    def test_openai_compatible_chat_model_has_bounded_requests(self):
        from config import provider_factory

        runtime_config = RuntimeProviderConfig(
            provider="bailian",
            api_key="test-key",
            base_url="https://example.invalid/v1",
            chat_model_name="test-chat",
            embedding_model_name="test-embedding",
        )

        with mock.patch.object(provider_factory, "ChatOpenAI") as chat_model:
            provider_factory.build_chat_model(runtime_config, temperature=0.7)

        chat_model.assert_called_once_with(
            model="test-chat",
            api_key="test-key",
            base_url="https://example.invalid/v1",
            timeout=60,
            max_retries=0,
            temperature=0.7,
        )

    def test_build_local_transformers_chat_model_passes_adapter_path(self):
        from config import provider_factory

        runtime_config = RuntimeProviderConfig(
            provider="local_transformers",
            api_key="local",
            base_url="local",
            chat_model_name="models/Qwen3-4B",
            embedding_model_name="models/bge-m3",
            adapter_path="saves/Qwen3-4B-Thinking/lora/localrag_sft_e1_qlora_smoke",
        )

        with mock.patch.object(provider_factory, "LocalTransformersChatModel") as chat_model:
            provider_factory.build_chat_model(runtime_config)

        chat_model.assert_called_once_with(
            "models/Qwen3-4B",
            device="auto",
            torch_dtype="float16",
            max_new_tokens=128,
            adapter_path="saves/Qwen3-4B-Thinking/lora/localrag_sft_e1_qlora_smoke",
        )


if __name__ == "__main__":
    unittest.main()
