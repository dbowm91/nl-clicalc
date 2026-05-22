"""
MCP server implementation for nl-calc exact tools.

Provides a stdio-based MCP server that exposes exact text, Unicode,
and measurement tools to agents.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .tools import (
    list_compare,
    math_eval,
    text_count,
    text_diff_explain,
    text_equal,
    text_inspect,
    text_measure,
    text_truncate,
    validate_brackets,
    validate_json,
    validate_regex,
)
from .schemas import TOOL_SCHEMAS

TOOL_HANDLERS: dict[str, Any] = {
    "math_eval": math_eval,
    "text_measure": text_measure,
    "text_equal": text_equal,
    "text_diff_explain": text_diff_explain,
    "text_inspect": text_inspect,
    "text_count": text_count,
    "text_truncate": text_truncate,
    "validate_brackets": validate_brackets,
    "validate_json": validate_json,
    "validate_regex": validate_regex,
    "list_compare": list_compare,
}


def _invalid_request(request_id: Any, message: str) -> dict:
    """Build JSON-RPC invalid request/params error."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32600,
            "message": message,
        },
    }


def _find_close_match(name: str, handlers: dict[str, Any]) -> str | None:
    """Find a case-insensitive close match for tool name."""
    name_lower = name.lower()
    for tool_name in handlers:
        if tool_name.lower() == name_lower:
            return tool_name
        if name_lower in tool_name.lower() or tool_name.lower() in name_lower:
            return tool_name
    return None


def _handle_call_tool(request: dict) -> dict:
    """Handle a tools/call MCP request."""
    params = request.get("params", {})
    if not isinstance(params, dict):
        return _invalid_request(request.get("id"), "Invalid params: expected object")

    name = params.get("name", "")
    arguments = params.get("arguments", {})
    if not isinstance(arguments, dict):
        return _invalid_request(request.get("id"), "Invalid arguments: expected object")

    if name not in TOOL_HANDLERS:
        close = _find_close_match(name, TOOL_HANDLERS)
        msg = f"Unknown tool: {name}"
        if close:
            msg += f". Did you mean: {close}?"
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32602,
                "message": msg,
            },
        }

    try:
        handler = TOOL_HANDLERS[name]
        result = handler(**arguments)

        # If result is an error envelope, return as error
        if isinstance(result, dict) and result.get("ok") is False:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32000,
                    "message": result.get("error", "Unknown error"),
                    "data": result,
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result),
                    }
                ]
            },
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32000,
                "message": f"Tool execution error: {str(e)}",
            },
        }


def _handle_list_tools(request: dict) -> dict:
    """Handle a tools/list MCP request."""
    tools = []
    for name, schema in TOOL_SCHEMAS.items():
        tools.append({
            "name": name,
            "description": schema["description"],
            "inputSchema": schema["inputSchema"],
        })

    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {"tools": tools},
    }


def _handle_initialize(request: dict) -> dict:
    """Handle an initialize MCP request."""
    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": False},
            },
            "serverInfo": {
                "name": "nl-calc-exact",
                "version": "1.0.0",
            },
        },
    }


def handle_request(request: Any) -> dict | None:
    """Route MCP request to appropriate handler."""
    if not isinstance(request, dict):
        return _invalid_request(None, "Invalid Request: expected JSON object")

    method = request.get("method", "")

    if method == "tools/list":
        return _handle_list_tools(request)
    elif method == "tools/call":
        return _handle_call_tool(request)
    elif method == "initialize":
        return _handle_initialize(request)
    elif method == "notifications/initialized":
        return None
    else:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}",
            },
        }


def main() -> int:
    """Main entry point for MCP server.

    Reads JSON-RPC requests from stdin and writes responses to stdout.
    """
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error: invalid JSON",
                },
            }
            print(json.dumps(response), flush=True)
            continue

        try:
            response = handle_request(request)
        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if isinstance(request, dict) else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                },
            }

        if response is not None:
            print(json.dumps(response), flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# Build-time alias for MCP entry point
mcp_main = main
