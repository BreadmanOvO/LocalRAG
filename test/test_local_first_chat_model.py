from __future__ import annotations

import unittest

from langchain_core.messages import AIMessage, HumanMessage

from model_gateway.fallback_chat_model import CloudFirstChatModel, LocalFirstChatModel


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


class FakeHTTPError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


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


class CloudFirstChatModelTests(unittest.TestCase):
    def test_cloud_timeout_falls_back_to_local(self):
        cloud = FakeToolModel(error=TimeoutError("cloud timeout"))
        local = FakeToolModel(AIMessage(content="local answer"))

        response = CloudFirstChatModel(
            primary=cloud,
            fallback=local,
        ).invoke([HumanMessage(content="hello")])

        self.assertEqual("local answer", response.content)
        route = response.response_metadata["localrag_route"]
        self.assertEqual("local", route["route"])
        self.assertTrue(route["fallback_used"])
        self.assertEqual("TimeoutError", route["fallback_reason"])

    def test_openai_connection_error_falls_back_to_local(self):
        # Keep the test independent of an actual network call while matching
        # the exception type raised by ChatOpenAI/openai on connection failure.
        import httpx
        import openai

        cloud = FakeToolModel(
            error=openai.APIConnectionError(
                request=httpx.Request("POST", "https://example.invalid")
            )
        )
        local = FakeToolModel(AIMessage(content="local answer"))

        response = CloudFirstChatModel(primary=cloud, fallback=local).invoke(
            [HumanMessage(content="hello")]
        )

        self.assertEqual("local answer", response.content)

    def test_cloud_success_does_not_call_local(self):
        cloud = FakeToolModel(AIMessage(content="cloud answer"))
        local = FakeToolModel(error=AssertionError("local must not run"))

        response = CloudFirstChatModel(
            primary=cloud,
            fallback=local,
        ).invoke([HumanMessage(content="hello")])

        self.assertEqual("cloud answer", response.content)
        route = response.response_metadata["localrag_route"]
        self.assertEqual("cloud", route["route"])
        self.assertFalse(route["fallback_used"])

    def test_non_transient_cloud_error_is_not_silently_fallback(self):
        cloud = FakeToolModel(error=ValueError("invalid request"))
        local = FakeToolModel(error=AssertionError("local must not run"))

        with self.assertRaisesRegex(ValueError, "invalid request"):
            CloudFirstChatModel(primary=cloud, fallback=local).invoke(
                [HumanMessage(content="hello")]
            )

    def test_http_5xx_falls_back_but_http_4xx_does_not(self):
        local = FakeToolModel(AIMessage(content="local answer"))
        response = CloudFirstChatModel(
            primary=FakeToolModel(error=FakeHTTPError(503)),
            fallback=local,
        ).invoke([HumanMessage(content="hello")])
        self.assertEqual("local answer", response.content)

        local = FakeToolModel(error=AssertionError("local must not run"))
        with self.assertRaisesRegex(FakeHTTPError, "HTTP 401"):
            CloudFirstChatModel(
                primary=FakeToolModel(error=FakeHTTPError(401)),
                fallback=local,
            ).invoke([HumanMessage(content="hello")])

    def test_tool_binding_keeps_schema_on_local_fallback(self):
        cloud = FakeToolModel(error=ConnectionError("offline"))
        local = FakeToolModel(
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
        tools = [{"type": "function", "function": {"name": "rag_search"}}]

        bound = CloudFirstChatModel(primary=cloud, fallback=local).bind_tools(
            tools,
            tool_choice="auto",
        )
        response = bound.invoke([HumanMessage(content="search")])

        self.assertEqual("rag_search", response.tool_calls[0]["name"])
        self.assertIsNotNone(cloud.bound_tools)
        self.assertIsNotNone(local.bound_tools)
        self.assertEqual(tools, cloud.bound_tools[0])
        self.assertEqual(tools, local.bound_tools[0])


if __name__ == "__main__":
    unittest.main()
