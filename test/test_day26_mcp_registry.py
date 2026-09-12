from __future__ import annotations
import unittest
from agent_platform.integrations import MCPTool, ToolRegistry

class Day26MCPRegistryTests(unittest.TestCase):
    def test_scope_checked_tool_lookup(self) -> None:
        registry = ToolRegistry(); registry.register(MCPTool("search_evidence", "stdio", {}, {}, "space-demo"))
        self.assertEqual("stdio", registry.get("search_evidence", data_scope="space-demo").server)
        with self.assertRaises(PermissionError): registry.get("search_evidence", data_scope="other-space")

if __name__ == "__main__": unittest.main()
