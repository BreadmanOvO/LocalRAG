from __future__ import annotations

import unittest

from langchain_core.messages import AIMessage, HumanMessage

from model_gateway.fallback_chat_model import LocalFirstChatModel


class FakeToolModel:
    def __init__(self, response=None, error: Exception | None = None) -> None:
        self.response = response or AIMessage(content="ok")
        self.error = error
        self.bound_tools = None

    def invoke(self, messages, **kwargs):
        del messages, kwargs
        if self.error is not None:
            raise self.error
        return self.response

    def bind_tools(self, tools, **kwargs):
        self.bound_tools = (tools, kwargs)
        return self


class LocalFirstChatModelTests(unittest.TestCase):
    def test_local_failure_falls_back_after_tools_are_bound(self):
        local = FakeToolModel(error=ConnectionError("offline"))
        cloud = FakeToolModel(
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "rag_search",
                        "args": {"query": "Apollo"},
                        "id": "call-1",
                        "type": "tool_call",
                    }
                ],
            )
        )
        model = LocalFirstChatModel(primary=local, fallback=cloud)

        bound = model.bind_tools(
            [{"type": "function", "function": {"name": "rag_search"}}],
            tool_choice="auto",
        )
        response = bound.invoke([HumanMessage(content="search")])

        self.assertEqual("rag_search", response.tool_calls[0]["name"])
        self.assertTrue(response.response_metadata["localrag_route"]["fallback_used"])
        self.assertEqual("ConnectionError", response.response_metadata["localrag_route"]["fallback_reason"])
        self.assertIsNotNone(local.bound_tools)
        self.assertIsNotNone(cloud.bound_tools)

    def test_successful_local_response_does_not_call_cloud(self):
        local = FakeToolModel(AIMessage(content="local"))
        cloud = FakeToolModel(error=AssertionError("cloud must not run"))
        response = LocalFirstChatModel(primary=local, fallback=cloud).invoke(
            [HumanMessage(content="hello")]
        )

        self.assertEqual("local", response.content)
        self.assertFalse(response.response_metadata["localrag_route"]["fallback_used"])


if __name__ == "__main__":
    unittest.main()
