from __future__ import annotations

import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from agent.context.compressor import ConversationCompressor, SummaryRequest
from agent.context.models import CompressionPolicy, ConversationCompressionError
from agent.context.store import ConversationContextStore
from config.runtime_keys import LocalModelGatewayConfig, RuntimeProviderConfig
from core import rag
from model_gateway import (
    GatewayQueueFullError,
    GatewayResponse,
    GatewayUsage,
    LocalGatewayChatModel,
    LocalModelGateway,
    ModelPurpose,
    RoutedResponse,
)
from model_gateway.summary_adapter import LocalGatewaySummaryClient


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


class SummaryPrimary:
    model = "localrag-qwen3-4b-e6.1"

    def __init__(self, text):
        self.text = text
        self.calls = []

    def complete(self, messages, *, context, **kwargs):
        self.calls.append((messages, context, kwargs))
        return GatewayResponse(
            text=self.text,
            model=self.model,
            usage=GatewayUsage(100, 30, 130),
            request_id=context.request_id,
            backend="llama.cpp",
            quantization="Q4_K_M",
        )


def _summary_json(**overrides):
    payload = {
        "goal": "Answer the current question",
        "user_constraints": [],
        "confirmed_findings": [],
        "decisions": [],
        "unresolved_questions": [],
        "failed_attempts": [],
        "referenced_source_ids": [],
    }
    payload.update(overrides)
    return json.dumps(payload)


def _summary_request(**overrides):
    values = {
        "previous_summary": None,
        "messages": (HumanMessage(content="old question", id="message-1"),),
        "allowed_evidence_ids": frozenset(),
        "allowed_source_ids": frozenset(),
        "input_token_limit": 40960,
        "session_id": "session-001",
    }
    values.update(overrides)
    return SummaryRequest(**values)


def _compression_messages():
    return (
        HumanMessage(content="old question " + "x" * 6000, id="message-1"),
        AIMessage(content="old answer " + "y" * 2000, id="message-2"),
        HumanMessage(content="recent question", id="message-3"),
        AIMessage(content="recent answer", id="message-4"),
    )


def _compression_policy():
    return CompressionPolicy(
        context_limit=5000,
        fixed_overhead_tokens=100,
        output_reserve_tokens=100,
        trigger_ratio=0.20,
        target_ratio=0.10,
        hard_limit_ratio=0.90,
        recent_turns=1,
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

    def test_summary_adapter_uses_summary_purpose_zero_temperature_and_schema(self):
        primary = SummaryPrimary(_summary_json())
        client = LocalGatewaySummaryClient(
            LocalModelGateway(primary),
            FakeCloudModel("unused"),
            task_id="task-001",
        )

        result = client.summarize(
            _summary_request(allowed_source_ids=frozenset({"source-001"}))
        )

        messages, context, kwargs = primary.calls[0]
        self.assertEqual(ModelPurpose.CONVERSATION_SUMMARY, context.purpose)
        self.assertEqual("session-001", context.session_id)
        self.assertEqual("task-001", context.task_id)
        self.assertEqual(0.0, kwargs["temperature"])
        self.assertEqual(2048, kwargs["max_tokens"])
        self.assertEqual(["system", "user"], [message["role"] for message in messages])
        self.assertIn("JSON schema", messages[0]["content"])
        prompt_payload = json.loads(messages[1]["content"])
        self.assertEqual(["source-001"], prompt_payload["allowed_source_ids"])
        self.assertEqual("localrag-qwen3-4b-e6.1", result.model_id)
        self.assertEqual("", result.fallback_reason)

    def test_invalid_local_summary_falls_back_to_cloud_once(self):
        primary = SummaryPrimary("not-json")
        cloud = FakeCloudModel(_summary_json())
        client = LocalGatewaySummaryClient(LocalModelGateway(primary), cloud)

        result = client.summarize(_summary_request())

        self.assertEqual("cloud-model", result.model_id)
        self.assertEqual("responsevalidation", result.fallback_reason)
        self.assertEqual(1, len(primary.calls))
        self.assertEqual(1, len(cloud.calls))
        self.assertTrue(client.last_route["fallback_used"])

    def test_invented_evidence_id_is_rejected_before_local_success(self):
        invented = _summary_json(
            confirmed_findings=[
                {"claim": "unsupported", "evidence_ids": ["invented-evidence"]}
            ]
        )
        cloud = FakeCloudModel(_summary_json())
        client = LocalGatewaySummaryClient(
            LocalModelGateway(SummaryPrimary(invented)),
            cloud,
        )

        result = client.summarize(_summary_request())

        self.assertEqual("cloud-model", result.model_id)
        self.assertEqual("responsevalidation", result.fallback_reason)
        self.assertEqual(1, len(cloud.calls))

    def test_invalid_cloud_summary_fails_closed_after_single_fallback(self):
        cloud = FakeCloudModel("still-not-json")
        client = LocalGatewaySummaryClient(
            LocalModelGateway(SummaryPrimary("not-json")),
            cloud,
        )

        with self.assertRaises(ConversationCompressionError):
            client.summarize(_summary_request())

        self.assertEqual(1, len(cloud.calls))
        self.assertTrue(client.last_route["fallback_used"])

    def test_real_summary_adapter_persists_cloud_route_and_invalid_cloud_never_commits(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "memory.sqlite3"
            store = ConversationContextStore(path)
            cloud = FakeCloudModel(_summary_json())
            client = LocalGatewaySummaryClient(
                LocalModelGateway(SummaryPrimary("not-json")),
                cloud,
            )
            outcome = ConversationCompressor(
                store,
                client,
                policy=_compression_policy(),
            ).prepare_model_view("session-001", _compression_messages())
            snapshot = store.get_summary("session-001")

            invalid_store = ConversationContextStore(Path(temp_dir) / "invalid.sqlite3")
            invalid_cloud = FakeCloudModel("still-not-json")
            invalid_outcome = ConversationCompressor(
                invalid_store,
                LocalGatewaySummaryClient(
                    LocalModelGateway(SummaryPrimary("not-json")),
                    invalid_cloud,
                ),
                policy=_compression_policy(),
            ).prepare_model_view("session-invalid", _compression_messages())
            invalid_snapshot = invalid_store.get_summary("session-invalid")

        self.assertEqual("compressed", outcome.status)
        self.assertEqual("cloud-model", snapshot.summary_model)
        self.assertEqual("responsevalidation", snapshot.fallback_reason)
        self.assertEqual(1, len(cloud.calls))
        self.assertEqual("skipped_with_error", invalid_outcome.status)
        self.assertIsNone(invalid_snapshot)
        self.assertEqual(1, len(invalid_cloud.calls))

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

    def test_rag_service_exposes_provider_route_without_gateway(self):
        runtime_config = RuntimeProviderConfig(
            provider="sensenova",
            api_key="cloud",
            base_url="https://example.invalid/v1",
            chat_model_name="cloud-chat",
            embedding_model_name="embedding",
        )
        with (
            mock.patch.object(rag, "build_embedding_model", return_value=object()),
            mock.patch.object(rag, "VectorStoreService", return_value=mock.Mock()),
            mock.patch.object(rag, "build_agent_chat_model", return_value=object()),
            mock.patch.object(
                rag.RagService,
                "_RagService__get_chain",
                return_value=SimpleNamespace(invoke=lambda *args, **kwargs: "answer"),
            ),
        ):
            service = rag.RagService(runtime_config=runtime_config)

        self.assertEqual(
            "answer",
            service.answer_from_documents("question", [], session_id="session-001"),
        )
        self.assertEqual(
            {
                "primary_model": "cloud-chat",
                "actual_model": "cloud-chat",
                "provider": "sensenova",
                "backend": "cloud",
                "fallback_used": False,
                "fallback_reason": None,
            },
            service.last_generation_route,
        )

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
