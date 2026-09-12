"""MCP tool registry; adapters share the Runtime tool contract."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class MCPTool:
    name: str
    server: str
    input_schema: dict
    output_schema: dict
    data_scope: str

class ToolRegistry:
    def __init__(self) -> None: self._tools: dict[str, MCPTool] = {}
    def register(self, tool: MCPTool) -> MCPTool:
        self._tools[tool.name] = tool; return tool
    def get(self, name: str, *, data_scope: str | None = None) -> MCPTool:
        tool = self._tools.get(name)
        if tool is None: raise ValueError(f"tool unavailable: {name}")
        if data_scope is not None and tool.data_scope != data_scope: raise PermissionError("tool data scope mismatch")
        return tool
