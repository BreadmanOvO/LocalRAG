"""Small MCP-style stdio server boundary for Runtime tool adapters."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Iterable, TextIO

from .mcp_registry import MCPTool, ToolRegistry


@dataclass(frozen=True)
class MCPCallContext:
    space_id: str
    request_id: str


class MCPStdioServer:
    """Line-delimited JSON RPC adapter; business effects stay in callbacks."""

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()
        self._handlers: dict[str, Callable[[dict[str, Any], MCPCallContext], Any]] = {}
        self._tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool, handler: Callable[[dict[str, Any], MCPCallContext], Any]) -> None:
        self.registry.register(tool)
        self._handlers[tool.name] = handler
        self._tools[tool.name] = tool

    def handle(self, request: dict[str, Any], *, space_id: str) -> dict[str, Any]:
        request_id = str(request.get("id", ""))
        method = request.get("method")
        params = request.get("params") or {}
        try:
            if method == "tools/list":
                return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": [tool.__dict__ for tool in self._tools.values()]}}
            if method != "tools/call":
                raise ValueError("unsupported MCP method")
            name = params.get("name")
            arguments = params.get("arguments") or {}
            tool = self.registry.get(name, data_scope=space_id)
            result = self._handlers[tool.name](arguments, MCPCallContext(space_id, request_id))
            return {"jsonrpc": "2.0", "id": request_id, "result": {"content": result}}
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": type(exc).__name__, "message": str(exc)}}

    def serve(self, stdin: TextIO, stdout: TextIO, *, space_id: str) -> None:
        for line in stdin:
            if not line.strip():
                continue
            response = self.handle(json.loads(line), space_id=space_id)
            stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            stdout.flush()
