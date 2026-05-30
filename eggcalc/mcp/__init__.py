"""
MCP server for eggcalc.

Provides stdio-based MCP server for text, Unicode, and measurement tools.
"""

from __future__ import annotations

from . import tools
from .schemas import TOOL_SCHEMAS
from .server import handle_request, main

__all__ = ["main", "handle_request", "TOOL_SCHEMAS", "tools"]
