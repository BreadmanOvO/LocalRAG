import unittest
from types import SimpleNamespace
from unittest import mock

from config.runtime_keys import RuntimeProviderConfig
from scripts.smoke_provider_contract import (
    load_and_run_provider_smoke,
    run_provider_smoke,
)


class FakeProviderModel:
    def invoke(self, _prompt):
        return SimpleNamespace(content="PROVIDER_SMOKE_OK")

    def bind_tools(self, _tools, *, tool_choice):
        return SimpleNamespace(
            invoke=lambda _prompt: SimpleNamespace(
                tool_calls=[{"name": tool_choice, "args": {"text": "PROVIDER_TOOL_OK"}}]
            )
        )

    def stream(self, _prompt):
        return iter(
            [
                SimpleNamespace(content="PROVIDER_"),
                SimpleNamespace(content="STREAM_OK"),
            ]
        )


class WrongProviderModel(FakeProviderModel):
    def invoke(self, _prompt):
        return SimpleNamespace(content="unexpected but nonempty")

    def bind_tools(self, _tools, *, tool_choice):
        return SimpleNamespace(
            invoke=lambda _prompt: SimpleNamespace(
                tool_calls=[{"name": tool_choice, "args": {}}]
            )
        )

    def stream(self, _prompt):
        return iter([SimpleNamespace(content="unexpected stream")])


class ProviderSmokeTests(unittest.TestCase):
    @staticmethod
    def _runtime_config() -> RuntimeProviderConfig:
        return RuntimeProviderConfig(
            provider="sensenova",
            api_key="test-key",
            base_url="https://example.invalid/v1",
            chat_model_name="test-chat",
            embedding_model_name="test-embedding",
        )

    def test_functional_smoke_covers_request_tool_call_and_stream(self):
        factory = mock.Mock(return_value=FakeProviderModel())

        report = run_provider_smoke(self._runtime_config(), model_factory=factory)

        self.assertTrue(report["overall_passed"])
        self.assertFalse(report["quality_evaluation"])
        self.assertEqual("provider_smoke_echo", report["tool_call"]["tool_names"][0])
        factory.assert_called_once_with(
            self._runtime_config(),
            temperature=0.0,
            timeout=30,
        )

    def test_wrong_markers_and_tool_arguments_fail_the_smoke(self):
        report = run_provider_smoke(
            self._runtime_config(),
            model_factory=mock.Mock(return_value=WrongProviderModel()),
        )

        self.assertFalse(report["request"]["passed"])
        self.assertFalse(report["tool_call"]["passed"])
        self.assertFalse(report["stream"]["passed"])
        self.assertFalse(report["overall_passed"])

    def test_missing_runtime_config_is_contract_only(self):
        with mock.patch(
            "scripts.smoke_provider_contract.load_runtime_config",
            side_effect=RuntimeError("private config path"),
        ):
            report = load_and_run_provider_smoke()

        self.assertEqual("contract_only", report["status"])
        self.assertIsNone(report["overall_passed"])
        self.assertNotIn("private config path", str(report))


if __name__ == "__main__":
    unittest.main()
