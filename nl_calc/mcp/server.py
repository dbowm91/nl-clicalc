"""
MCP server implementation for nl-calc exact tools.

Provides a stdio-based MCP server that exposes exact text, Unicode,
and measurement tools to agents.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .schemas import TOOL_SCHEMAS
from .tools import (
    canonicalize_text_mcp,
    code_fence_extract_mcp,
    constant_lookup,
    dotenv_validate_mcp,
    escape_text,
    glob_match_mcp,
    identifier_analyze,
    identifier_inspect_mcp,
    ini_validate_mcp,
    json_canonicalize,
    json_compare,
    json_extract,
    json_query,
    json_shape,
    line_range_compare,
    line_range_extract,
    list_compare,
    list_dedupe_mcp,
    list_sort_mcp,
    markdown_structure_mcp,
    math_eval,
    patch_apply_check_mcp,
    patch_summary_mcp,
    path_analyze_mcp,
    path_compare_mcp,
    path_normalize,
    path_scope_check_mcp,
    regex_finditer,
    regex_safety_check,
    shell_argv_compare,
    shell_quote_join,
    shell_split,
    text_count,
    text_diff_explain,
    text_equal,
    text_fingerprint_mcp,
    text_hash,
    text_inspect,
    text_measure,
    text_position,
    text_replace_check,
    text_transform,
    text_truncate,
    text_window,
    toml_shape_mcp,
    unescape_text,
    unicode_policy_check_mcp,
    unit_convert,
    unit_info,
    validate_brackets,
    validate_json,
    validate_regex,
    validate_schema_light,
    validate_toml,
    version_compare_mcp,
)

TOOL_HANDLERS: dict[str, Any] = {
    "code_fence_extract": code_fence_extract_mcp,
    "dotenv_validate": dotenv_validate_mcp,
    "ini_validate": ini_validate_mcp,
    "escape_text": escape_text,
    "line_range_compare": line_range_compare,
    "line_range_extract": line_range_extract,
    "unescape_text": unescape_text,
    "json_canonicalize": json_canonicalize,
    "json_compare": json_compare,
    "json_extract": json_extract,
    "json_query": json_query,
    "json_shape": json_shape,
    "list_compare": list_compare,
    "list_dedupe": list_dedupe_mcp,
    "list_sort": list_sort_mcp,
    "math_eval": math_eval,
    "patch_apply_check": patch_apply_check_mcp,
    "patch_summary": patch_summary_mcp,
    "path_analyze": path_analyze_mcp,
    "path_compare": path_compare_mcp,
    "path_normalize": path_normalize,
    "path_scope_check": path_scope_check_mcp,
    "regex_finditer": regex_finditer,
    "regex_safety_check": regex_safety_check,
    "shell_split": shell_split,
    "shell_quote_join": shell_quote_join,
    "argv_compare": shell_argv_compare,
    "text_count": text_count,
    "text_diff_explain": text_diff_explain,
    "text_equal": text_equal,
    "text_hash": text_hash,
    "text_inspect": text_inspect,
    "text_measure": text_measure,
    "text_position": text_position,
    "text_replace_check": text_replace_check,
    "text_truncate": text_truncate,
    "text_transform": text_transform,
    "text_window": text_window,
    "toml_shape": toml_shape_mcp,
    "unit_convert": unit_convert,
    "unit_info": unit_info,
    "constant_lookup": constant_lookup,
    "validate_brackets": validate_brackets,
    "validate_json": validate_json,
    "validate_regex": validate_regex,
    "validate_schema_light": validate_schema_light,
    "validate_toml": validate_toml,
    "version_compare": version_compare_mcp,
    "identifier_analyze": identifier_analyze,
    "glob_match": glob_match_mcp,
    "text_fingerprint": text_fingerprint_mcp,
    "identifier_inspect": identifier_inspect_mcp,
    "markdown_structure": markdown_structure_mcp,
    "unicode_policy_check": unicode_policy_check_mcp,
    "canonicalize_text": canonicalize_text_mcp,
}

MAX_REQUEST_BYTES = 1_000_000


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
    """Handle a tools/list MCP request with optional filtering."""
    params = request.get("params", {})

    tier_filter: int | None = params.get("tier")
    tags_filter: list[str] | None = params.get("tags")
    names_filter: list[str] | None = params.get("names")

    tools = []
    for name, schema in TOOL_SCHEMAS.items():
        if names_filter is not None:
            if name not in names_filter:
                continue

        if tier_filter is not None:
            if schema.get("tier") != tier_filter:
                continue

        if tags_filter is not None:
            tool_tags = set(schema.get("tags", []))
            if not all(tag in tool_tags for tag in tags_filter):
                continue

        tools.append({
            "name": name,
            "description": schema["description"],
            "inputSchema": schema["inputSchema"],
            "tier": schema.get("tier"),
            "tags": schema.get("tags", []),
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

        if len(line.encode('utf-8')) > MAX_REQUEST_BYTES:
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"Request exceeds maximum size of {MAX_REQUEST_BYTES} bytes",
                },
            }
            print(json.dumps(response), flush=True)
            continue

        if line.startswith('['):
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Batch requests are not supported",
                },
            }
            print(json.dumps(response), flush=True)
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
