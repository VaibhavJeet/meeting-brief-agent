"""MCP (Model Context Protocol) integrations."""

from app.mcp.base import BaseMCPIntegration, MCPConfig
from app.mcp.calendar import CalendarMCP
from app.mcp.email import EmailMCP
from app.mcp.crm import CRMMCP
from app.mcp.database import DatabaseMCP

__all__ = [
    "BaseMCPIntegration",
    "MCPConfig",
    "CalendarMCP",
    "EmailMCP",
    "CRMMCP",
    "DatabaseMCP",
]
