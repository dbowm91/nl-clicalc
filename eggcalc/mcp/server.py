"""
MCP server implementation for eggcalc.

Provides a stdio-based MCP server that exposes exact text, Unicode,
and measurement tools to agents.
"""

from __future__ import annotations

import inspect
import json
import sys
import time
from collections import deque
from typing import Any

from .. import __version__
from .schemas import TOOL_SCHEMAS
from .tools import (
    _sanitize_error,
    canonicalize_text_mcp,
    cargo_toml_inspect_mcp,
    code_fence_extract_mcp,
    constant_lookup,
    dotenv_validate_mcp,
    escape_text,
    glob_match_mcp,
    identifier_analyze,
    identifier_inspect_mcp,
    identifier_table_inspect_mcp,
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
    prompt_input_inspect_mcp,
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
    version_constraint_check_mcp,
)

TOOL_HANDLERS: dict[str, Any] = {
    "cargo_toml_inspect": cargo_toml_inspect_mcp,
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
    "version_constraint_check": version_constraint_check_mcp,
    "identifier_analyze": identifier_analyze,
    "glob_match": glob_match_mcp,
    "text_fingerprint": text_fingerprint_mcp,
    "identifier_inspect": identifier_inspect_mcp,
    "identifier_table_inspect": identifier_table_inspect_mcp,
    "markdown_structure": markdown_structure_mcp,
    "unicode_policy_check": unicode_policy_check_mcp,
    "canonicalize_text": canonicalize_text_mcp,
    "prompt_input_inspect": prompt_input_inspect_mcp,
}

MAX_REQUEST_BYTES = 1_000_000
MAX_OUTPUT_BYTES = 1_000_000
MAX_REQUESTS_PER_SECOND = 10


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


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    prev_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = prev_row[j + 1] + 1
            deletions = curr_row[j] + 1
            substitutions = prev_row[j] + (c1 != c2)
            curr_row.append(min(insertions, deletions, substitutions))
        prev_row = curr_row

    return prev_row[-1]


def _find_close_match(name: str, handlers: dict[str, Any]) -> str | None:
    """Find a case-insensitive close match for tool name using edit distance.

    Returns the best matching tool name, or None if no good match found.
    A match is considered good if the edit distance is at most half the length
    of the shorter string, or if it's a prefix/substring match.
    """
    name_lower = name.lower()

    # First check for exact case-insensitive match
    for tool_name in handlers:
        if tool_name.lower() == name_lower:
            return tool_name

    # Find best match by edit distance
    best_match: str | None = None
    best_distance = float('inf')

    for tool_name in handlers:
        tool_lower = tool_name.lower()

        # Prefix/substring match is always good
        if name_lower in tool_lower or tool_lower in name_lower:
            if best_match is None or len(tool_name) < len(best_match):
                best_match = tool_name
                best_distance = 0
            continue

        # Compute edit distance
        distance = _levenshtein_distance(name_lower, tool_lower)
        threshold = max(len(name_lower), len(tool_lower)) // 2

        if distance < best_distance and distance <= threshold:
            best_distance = distance
            best_match = tool_name

    return best_match


def _validate_arguments(handler: Any, arguments: dict[str, Any]) -> str | None:
    """Validate that arguments match the handler's signature.

    Returns None if valid, or an error message string if invalid.
    """
    try:
        sig = inspect.signature(handler)
    except (ValueError, TypeError):
        # Can't introspect; allow call (handler will raise on bad args)
        return None

    params = sig.parameters

    # Check for unexpected keyword arguments
    unexpected = set(arguments.keys()) - set(params.keys())
    if unexpected:
        return f"Unexpected argument(s): {', '.join(sorted(unexpected))}"

    # Check for missing required arguments (no default)
    for name, param in params.items():
        if param.default is inspect.Parameter.empty and name not in arguments:
            return f"Missing required argument: {name}"

    return None


def _validate_arguments_schema(name: str, arguments: dict[str, Any]) -> str | None:
    """Validate arguments against the tool's inputSchema from TOOL_SCHEMAS.

    Returns None if valid, or an error message string if invalid.
    """
    schema = TOOL_SCHEMAS.get(name, {}).get("inputSchema")
    if not schema:
        return None

    props = schema.get("properties", {})
    required = schema.get("required", [])

    for field in required:
        if field not in arguments:
            return f"Missing required argument: {field}"

    for key, value in arguments.items():
        if key not in props:
            continue
        prop = props[key]
        expected_type = prop.get("type")
        if expected_type is None:
            continue

        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        python_type = type_map.get(expected_type)
        if python_type is not None and not isinstance(value, python_type):
            return f"Argument '{key}' must be {expected_type}, got {type(value).__name__}"

        enum_values = prop.get("enum")
        if enum_values is not None and value not in enum_values:
            return f"Argument '{key}' must be one of: {', '.join(str(v) for v in enum_values)}"

    return None


def _handle_call_tool(request: dict) -> dict:
    """Handle a tools/call MCP request."""
    params = request.get("params", {})
    if not isinstance(params, dict):
        return _invalid_request(request.get("id"), "Invalid params: expected object")

    name = params.get("name", "")
    arguments = params.get("arguments", {})
    if not isinstance(name, str) or not name:
        return _invalid_request(request.get("id"), "Invalid params: missing tool name")
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

    # Validate arguments against handler signature before calling
    handler = TOOL_HANDLERS[name]
    validation_error = _validate_arguments(handler, arguments)
    if validation_error is not None:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32602,
                "message": f"Invalid arguments for tool '{name}': {validation_error}",
            },
        }

    schema_error = _validate_arguments_schema(name, arguments)
    if schema_error is not None:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32602,
                "message": f"Invalid arguments for tool '{name}': {schema_error}",
            },
        }

    try:
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

        serialized = json.dumps(result)
        if len(serialized.encode("utf-8")) > MAX_OUTPUT_BYTES:
            truncated = {
                "ok": False,
                "tool": name,
                "error_type": "output_too_large",
                "error": f"Output exceeds {MAX_OUTPUT_BYTES} bytes and was truncated",
                "hints": ["Try reducing input size or using a summary/detail option"],
                "warnings": ["Output was truncated due to size limit"],
            }
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(truncated),
                        }
                    ]
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": serialized,
                    }
                ]
            },
        }

    except Exception as e:
        message = _sanitize_error(str(e))[:200]
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32000,
                "message": f"Tool execution error: {message}",
            },
        }


def _handle_list_tools(request: dict) -> dict:
    """Handle a tools/list MCP request with optional filtering."""
    params = request.get("params", {})
    request_id = request.get("id")

    tier_filter = params.get("tier")
    tags_filter = params.get("tags")
    names_filter = params.get("names")

    if tier_filter is not None and not isinstance(tier_filter, int):
        return _invalid_request(request_id, "Invalid 'tier' parameter: expected integer")
    if tags_filter is not None and not isinstance(tags_filter, list):
        return _invalid_request(request_id, "Invalid 'tags' parameter: expected array")
    if names_filter is not None and not isinstance(names_filter, list):
        return _invalid_request(request_id, "Invalid 'names' parameter: expected array")

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
                "name": "eggcalc",
                "version": __version__,
            },
        },
    }


def handle_request(request: Any) -> dict | None:
    """Route MCP request to appropriate handler."""
    if not isinstance(request, dict):
        return _invalid_request(None, "Invalid Request: expected JSON object")

    if "method" not in request:
        return _invalid_request(request.get("id"), "Invalid Request: missing 'method'")

    method = request["method"]

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
    request_times: deque[float] = deque()
    window = 1.0  # sliding window in seconds

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        if len(line.encode('utf-8')) > MAX_REQUEST_BYTES:
            response = {
                "jsonrpc": "2.0",
                "id": None,
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
                "id": None,
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
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error: invalid JSON",
                },
            }
            print(json.dumps(response), flush=True)
            continue

        now = time.monotonic()
        while request_times and request_times[0] < now - window:
            request_times.popleft()

        if len(request_times) >= MAX_REQUESTS_PER_SECOND:
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if isinstance(request, dict) else None,
                "error": {
                    "code": -32600,
                    "message": f"Rate limit exceeded: max {MAX_REQUESTS_PER_SECOND} requests per second",
                },
            }
            print(json.dumps(response), flush=True)
            continue

        request_times.append(now)

        try:
            response = handle_request(request)
        except Exception as e:
            message = str(e).replace('\n', ' ')[:200]
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if isinstance(request, dict) else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {message}",
                },
            }

        if response is not None:
            print(json.dumps(response), flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# Build-time alias for MCP entry point
mcp_main = main
