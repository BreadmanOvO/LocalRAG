import unittest
import tempfile
from pathlib import Path
from unittest import mock

from config.runtime_keys import (
    CloudModelConfig,
    EmbeddingModelConfig,
    LocalModelGatewayConfig,
    ModelRoleConfig,
    RuntimeProviderConfig,
)
from model_gateway.fallback_chat_model import LocalFirstChatModel


class ProviderFactoryTests(unittest.TestCase):
    @staticmethod
    def _runtime_config(*, rag_enabled=True, summary_enabled=True):
        return RuntimeProviderConfig(
            provider="bailian",
            api_key="test-key",
            base_url="https://example.invalid/v1",
            chat_model_name="test-chat",
            embedding_model_name="test-embedding",
            local_model_gateway=LocalModelGatewayConfig(
                base_url="http://127.0.0.1:8002/v1",
                model="localrag-qwen3-4b-e6.1",
                api_token="secret",
                rag_generation_enabled=rag_enabled,
                conversation_summary_enabled=summary_enabled,
            ),
        )

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
            max_retries=1,
            temperature=0.7,
        )

    def test_sensenova_keeps_default_tls_verification(self):
        from config import provider_factory

        runtime_config = RuntimeProviderConfig(
            provider="sensenova",
            api_key="test-key",
            base_url="https://example.invalid/v1",
            chat_model_name="test-chat",
            embedding_model_name="test-embedding",
        )

        with mock.patch.object(provider_factory, "ChatOpenAI") as chat_model:
            provider_factory.build_agent_chat_model(runtime_config)

        options = chat_model.call_args.kwargs
        self.assertNotIn("http_client", options)
        self.assertNotIn("http_async_client", options)

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

    def test_agent_factory_ignores_local_gateway_and_compatibility_alias_matches(self):
        from config import provider_factory

        runtime_config = self._runtime_config()
        gateway = object()
        with mock.patch.object(
            provider_factory,
            "ChatOpenAI",
            side_effect=lambda **kwargs: object(),
        ) as cloud:
            agent = provider_factory.build_agent_chat_model(runtime_config)
            legacy = provider_factory.build_chat_model(runtime_config)

        self.assertIsNot(agent, gateway)
        self.assertIsNot(legacy, gateway)
        self.assertEqual(2, cloud.call_count)

    def test_rag_and_summary_factories_select_only_enabled_injected_gateway(self):
        from config import provider_factory

        gateway = object()
        enabled = self._runtime_config()
        self.assertIs(
            gateway,
            provider_factory.build_rag_chat_model(enabled, gateway=gateway),
        )
        self.assertIs(
            gateway,
            provider_factory.build_summary_chat_model(enabled, gateway=gateway),
        )

        disabled = self._runtime_config(rag_enabled=False, summary_enabled=False)
        with mock.patch.object(
            provider_factory,
            "ChatOpenAI",
            side_effect=lambda **kwargs: object(),
        ) as cloud:
            rag = provider_factory.build_rag_chat_model(disabled, gateway=gateway)
            summary = provider_factory.build_summary_chat_model(
                disabled,
                gateway=gateway,
            )
        self.assertIsNot(rag, gateway)
        self.assertIsNot(summary, gateway)
        self.assertEqual(2, cloud.call_count)

    def test_cloud_route_mode_bypasses_injected_local_gateway(self):
        from config import provider_factory

        gateway = object()
        cloud_route = RuntimeProviderConfig(
            **{
                **self._runtime_config().__dict__,
                "model_route_mode": "cloud",
            }
        )
        with mock.patch.object(
            provider_factory,
            "ChatOpenAI",
            side_effect=lambda **kwargs: object(),
        ) as cloud:
            rag = provider_factory.build_rag_chat_model(cloud_route, gateway=gateway)
            summary = provider_factory.build_summary_chat_model(cloud_route, gateway=gateway)
        self.assertIsNot(rag, gateway)
        self.assertIsNot(summary, gateway)
        self.assertEqual(2, cloud.call_count)

    def test_v2_planner_local_route_builds_tool_capable_cloud_fallback(self):
        from config import provider_factory

        cloud = CloudModelConfig(
            provider="sensenova",
            api_key="cloud-secret",
            base_url="https://example.invalid/v1",
            model="cloud-planner",
        )
        local = LocalModelGatewayConfig(
            base_url="http://127.0.0.1:8001/v1",
            model="local-planner",
            api_token="local-secret",
        )
        roles = {
            role: ModelRoleConfig(
                route="local" if role == "planner" else "cloud",
                cloud=cloud,
                local=local,
            )
            for role in ("planner", "rag", "summary")
        }
        runtime = RuntimeProviderConfig(
            provider="sensenova",
            api_key="cloud-secret",
            base_url=cloud.base_url,
            chat_model_name=cloud.model,
            embedding_model_name="models/bge-m3",
            roles=roles,
            embedding=EmbeddingModelConfig(
                provider="local_sentence_transformer",
                model="models/bge-m3",
            ),
        )

        with mock.patch.object(provider_factory, "ChatOpenAI") as chat_model:
            chat_model.side_effect = lambda **kwargs: mock.Mock(**{"bind_tools.return_value": mock.Mock()})
            result = provider_factory.build_agent_chat_model(runtime, temperature=0.0)

        self.assertIsInstance(result, LocalFirstChatModel)
        self.assertEqual(2, chat_model.call_count)
        local_call = next(
            call.kwargs
            for call in chat_model.call_args_list
            if call.kwargs["base_url"] == local.base_url
        )
        self.assertEqual("agent_planning", local_call["extra_body"]["purpose"])
        self.assertEqual("local-secret", local_call["api_key"])


if __name__ == "__main__":
    unittest.main()
