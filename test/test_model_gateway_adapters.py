from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest import mock

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from config.runtime_keys import LocalModelGatewayConfig, RuntimeProviderConfig
from core import rag
from model_gateway import (
    GatewayQueueFullError,
    GatewayUsage,
    LocalGatewayChatModel,
    LocalModelGateway,
    ModelPurpose,
    RoutedResponse,
)


class RecordingGateway:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def complete(self, messages, **kwargs):
        self.calls.append((messages, kwargs))
        return self.result


class FakeCloudModel:
    model_name = "cloud-model"

    def __init__(self, text="cloud answer"):
        self.text = text
        self.calls = []

    def invoke(self, input, config=None):
        self.calls.append((input, config))
        return AIMessage(
            content=self.text,
            response_metadata={
                "model_name": self.model_name,
                "token_usage": {
                    "prompt_tokens": 7,
                    "completion_tokens": 3,
                    "total_tokens": 10,
                },
            },
        )


def _routed_local() -> RoutedResponse:
    return RoutedResponse(
        text="local answer",
        model="localrag-qwen3-4b-e6.1",
        usage=GatewayUsage(5, 2, 7),
        request_id="req-local",
        backend="llama.cpp",
        quantization="Q4_K_M",
        primary_model="localrag-qwen3-4b-e6.1",
        actual_model="localrag-qwen3-4b-e6.1",
        fallback_used=False,
        fallback_reason="",
        attempt_count=1,
        ttft_seconds=0.1,
        latency_seconds=1.0,
    )


class ModelGatewayAdapterTests(unittest.TestCase):
    def test_adapter_maps_messages_context_and_route_metadata(self):
        gateway = RecordingGateway(_routed_local())
        adapter = LocalGatewayChatModel(gateway, FakeCloudModel())
        result = adapter.invoke(
            [SystemMessage(content="system"), HumanMessage(content="question")],
            config={
                "configurable": {
                    "session_id": "session-001",
                    "task_id": "task-001",
                    "run_id": "run-001",
                }
            },
        )

        messages, kwargs = gateway.calls[0]
        self.assertEqual(
            [
                {"role": "system", "content": "system"},
                {"role": "user", "content": "question"},
            ],
            messages,
        )
        context = kwargs["context"]
        self.assertEqual(ModelPurpose.RAG_GENERATION, context.purpose)
        self.assertEqual("session-001", context.session_id)
        route = result.response_metadata["localrag_route"]
        self.assertEqual("Q4_K_M", route["quantization"])
        self.assertEqual("localrag-qwen3-4b-e6.1", route["actual_model"])
        self.assertFalse(route["fallback_used"])

    def test_adapter_uses_cloud_once_when_gateway_falls_back(self):
        class FailingPrimary:
            model = "localrag-qwen3-4b-e6.1"

            def complete(self, messages, **kwargs):
                del messages, kwargs
                raise GatewayQueueFullError("queue", request_id="req-local")

        cloud = FakeCloudModel()
        adapter = LocalGatewayChatModel(
            LocalModelGateway(FailingPrimary()),
            cloud,
        )
        result = adapter.invoke([HumanMessage(content="question")])
        route = result.response_metadata["localrag_route"]
        self.assertEqual("cloud answer", result.content)
        self.assertTrue(route["fallback_used"])
        self.assertEqual("queuefull", route["fallback_reason"])
        self.assertEqual("cloud-model", route["actual_model"])
        self.assertEqual(1, len(cloud.calls))

    def test_adapter_rejects_tool_messages_before_local_request(self):
        gateway = RecordingGateway(_routed_local())
        adapter = LocalGatewayChatModel(gateway, FakeCloudModel())
        with self.assertRaisesRegex(ValueError, "does not accept tool"):
            adapter.invoke(
                [ToolMessage(content="tool output", tool_call_id="call-001")]
            )
        self.assertEqual([], gateway.calls)

    def test_rag_service_selects_gateway_factory_and_exposes_last_route(self):
        runtime_config = RuntimeProviderConfig(
            provider="bailian",
            api_key="cloud",
            base_url="https://example.invalid/v1",
            chat_model_name="cloud-chat",
            embedding_model_name="embedding",
            local_model_gateway=LocalModelGatewayConfig(
                base_url="http://127.0.0.1:8002/v1",
                model="localrag-qwen3-4b-e6.1",
                api_token="secret",
                rag_generation_enabled=True,
                conversation_summary_enabled=False,
            ),
        )
        gateway_model = SimpleNamespace(last_route={"actual_model": "local"})
        with (
            mock.patch.object(rag, "build_embedding_model", return_value=object()),
            mock.patch.object(rag, "VectorStoreService", return_value=mock.Mock()),
            mock.patch.object(
                rag,
                "build_rag_chat_model",
                return_value=gateway_model,
            ) as build_rag,
            mock.patch.object(
                rag.RagService,
                "_RagService__get_chain",
                return_value=SimpleNamespace(invoke=lambda *args, **kwargs: "answer"),
            ),
        ):
            service = rag.RagService(
                gateway=gateway_model,
                runtime_config=runtime_config,
            )

        build_rag.assert_called_once_with(runtime_config, gateway=gateway_model)
        answer = service.answer_from_documents("question", [], session_id="session-001")
        self.assertEqual("answer", answer)
        self.assertEqual({"actual_model": "local"}, service.last_generation_route)

    def test_rag_answer_bundle_contains_generation_route(self):
        service = SimpleNamespace(
            retrieve_documents=lambda question: [],
            retrieve_scored_documents=lambda question: [],
            answer_from_documents=lambda *args, **kwargs: "answer",
            last_generation_route={"fallback_used": True},
        )
        result = rag.RagService.answer_with_retrieval(
            service,
            "question",
            session_id="session-001",
        )
        self.assertEqual({"fallback_used": True}, result["generation_route"])


if __name__ == "__main__":
    unittest.main()
