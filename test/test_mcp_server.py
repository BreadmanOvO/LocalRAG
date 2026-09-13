from __future__ import annotations

import io
import json
import unittest

from agent_platform.integrations import MCPStdioServer, MCPTool


class MCPServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = MCPStdioServer()
        self.server.register(MCPTool("search_evidence", "localrag", {"type": "object"}, {"type": "array"}, "space-demo"), lambda args, context: [{"query": args["query"], "space": context.space_id}])

    def test_list_call_and_scope_error(self) -> None:
        listed = self.server.handle({"jsonrpc": "2.0", "id": "1", "method": "tools/list"}, space_id="space-demo")
        self.assertEqual("search_evidence", listed["result"]["tools"][0]["name"])
        called = self.server.handle({"jsonrpc": "2.0", "id": "2", "method": "tools/call", "params": {"name": "search_evidence", "arguments": {"query": "bev"}}}, space_id="space-demo")
        self.assertEqual("bev", called["result"]["content"][0]["query"])
        denied = self.server.handle({"jsonrpc": "2.0", "id": "3", "method": "tools/call", "params": {"name": "search_evidence", "arguments": {"query": "bev"}}}, space_id="other")
        self.assertEqual("PermissionError", denied["error"]["code"])

    def test_stdio_round_trip(self) -> None:
        stdin = io.StringIO(json.dumps({"id": "1", "method": "tools/list"}) + "\n")
        stdout = io.StringIO()
        self.server.serve(stdin, stdout, space_id="space-demo")
        self.assertIn("search_evidence", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
