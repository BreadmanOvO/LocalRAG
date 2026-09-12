"""Model, MCP, external-tool, and legacy-system adapters."""
from .capabilities import Capability, CapabilityRegistry
from .mcp_registry import MCPTool, ToolRegistry

__all__ = ["Capability", "CapabilityRegistry", "MCPTool", "ToolRegistry"]
