"""Model, MCP, external-tool, and legacy-system adapters."""
from .capabilities import Capability, CapabilityRegistry
from .mcp_registry import MCPTool, ToolRegistry
from .multi_agent_config import CloudAgentClient, CloudAgentSpec, load_cloud_agents

__all__ = ["Capability", "CapabilityRegistry", "MCPTool", "ToolRegistry", "CloudAgentClient", "CloudAgentSpec", "load_cloud_agents"]
