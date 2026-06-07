import unittest
from unittest import mock

from config.runtime_keys import RuntimeProviderConfig


class ProviderFactoryTests(unittest.TestCase):
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
