"""
MCP server implementation for eggcalc.

Provides a stdio-based MCP server that exposes exact text, Unicode,
and measurement tools to agents.
"""

from __future__ import annotations

import concurrent.futures
import inspect
import json
import sys
import time
from collections import deque
from typing import Any

from .. import __version__
from .. import evaluator as _evaluator
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
MAX_REQUEST_ID_LENGTH = 1024
MAX_TOOL_TIMEOUT_SECONDS = 30
_SHARED_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="mcp-tool")


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


_MAX_TOOL_NAME_LENGTH = 200


def _find_close_match(name: str, handlers: dict[str, Any]) -> str | None:
    """Find a case-insensitive close match for tool name using edit distance.

    Returns the best matching tool name, or None if no good match found.
    A match is considered good if the edit distance is at most half the length
    of the shorter string, or if it's a prefix/substring match.
    """
    if len(name) > _MAX_TOOL_NAME_LENGTH:
        return None
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

        # Prefix/substring match at word boundary is always good
        def _at_word_boundary(sub: str, s: str) -> bool:
            idx = s.find(sub)
            if idx == -1:
                return False
            if idx == 0:
                return True
            return s[idx - 1] in ('_', '-')

        if _at_word_boundary(name_lower, tool_lower) or _at_word_boundary(tool_lower, name_lower):
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
    has_var_keyword = any(
        p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()
    )

    # Check for unexpected keyword arguments (skip if handler accepts **kwargs)
    if not has_var_keyword:
        unexpected = set(arguments.keys()) - set(params.keys())
        if unexpected:
            return f"Unexpected argument(s): {', '.join(sorted(unexpected))}"

    # Check for missing required arguments (no default)
    for name, param in params.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        if param.default is inspect.Parameter.empty and name not in arguments:
            return f"Missing required argument: {name}"

    return None


def _validate_value_against_schema(
    value: Any, prop: dict, path: str, max_depth: int = 10
) -> str | None:
    """Validate a single value against a JSON schema property definition.

    Returns None if valid, or an error message string if invalid.
    Supports recursive validation for nested objects and arrays.
    """
    if max_depth <= 0:
        return f"Schema nesting too deep at '{path}'"

    expected_type = prop.get("type")
    if expected_type is None:
        return None

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
        return f"Argument '{path}' must be {expected_type}, got {type(value).__name__}"

    # Bool is subclass of int in Python; reject bool for integer/number
    if expected_type in ("integer", "number") and isinstance(value, bool):
        return f"Argument '{path}' must be {expected_type}, got bool"

    enum_values = prop.get("enum")
    if enum_values is not None and value not in enum_values:
        return f"Argument '{path}' must be one of: {', '.join(str(v) for v in enum_values)}"

    # String length constraints
    if expected_type == "string" and isinstance(value, str):
        min_length = prop.get("minLength")
        if min_length is not None and len(value) < min_length:
            return f"Argument '{path}' length {len(value)} is less than minLength {min_length}"
        max_length = prop.get("maxLength")
        if max_length is not None and len(value) > max_length:
            return f"Argument '{path}' length {len(value)} exceeds maxLength {max_length}"

    # Numeric range constraints
    if expected_type in ("number", "integer") and isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = prop.get("minimum")
        if minimum is not None and value < minimum:
            return f"Argument '{path}' value {value} is less than minimum {minimum}"
        maximum = prop.get("maximum")
        if maximum is not None and value > maximum:
            return f"Argument '{path}' value {value} exceeds maximum {maximum}"

    # Recursive validation for nested objects (only when sub-schema defines properties)
    if expected_type == "object" and isinstance(value, dict):
        sub_props = prop.get("properties", {})
        sub_required = prop.get("required", [])
        sub_additional = prop.get("additionalProperties", False)

        # Only validate recursively if the schema actually defines sub-properties
        # or required fields. Opaque object types (no sub-schema) are accepted as-is.
        if sub_props or sub_required:
            for field in sub_required:
                if field not in value:
                    return f"Missing required field '{field}' in '{path}'"

            if not sub_additional:
                unknown = set(value.keys()) - set(sub_props.keys())
                if unknown:
                    return f"Unexpected field(s) in '{path}': {', '.join(sorted(unknown))}"

            for sub_key, sub_val in value.items():
                if sub_key in sub_props:
                    err = _validate_value_against_schema(
                        sub_val, sub_props[sub_key], f"{path}.{sub_key}", max_depth=max_depth - 1
                    )
                    if err:
                        return err

    # Recursive validation for arrays
    if expected_type == "array" and isinstance(value, list):
        max_items = prop.get("maxItems")
        if max_items is not None and len(value) > max_items:
            return f"Argument '{path}' has {len(value)} items, exceeds maxItems {max_items}"

        items_schema = prop.get("items")
        if items_schema:
            for i, item in enumerate(value):
                err = _validate_value_against_schema(
                    item, items_schema, f"{path}[{i}]", max_depth=max_depth - 1
                )
                if err:
                    return err

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
    additional_allowed = schema.get("additionalProperties", False)

    for field in required:
        if field not in arguments:
            return f"Missing required argument: {field}"

    if not additional_allowed:
        unknown = set(arguments.keys()) - set(props.keys())
        if unknown:
            return f"Unexpected argument(s): {', '.join(sorted(unknown))}"

    for key, value in arguments.items():
        if key not in props:
            continue
        err = _validate_value_against_schema(value, props[key], key)
        if err:
            return err

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

    timed_out = False
    result = None
    future: concurrent.futures.Future | None = None
    try:
        future = _SHARED_EXECUTOR.submit(handler, **arguments)
        try:
            result = future.result(timeout=MAX_TOOL_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            timed_out = True
            if future is not None:
                future.cancel()
            import logging as _logging
            _logging.warning(
                "MCP tool '%s' timed out after %ds",
                name, MAX_TOOL_TIMEOUT_SECONDS,
            )
    except Exception as e:
        if not timed_out:
            message = _sanitize_error(str(e))[:500]
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32000,
                    "message": f"Tool execution error: {message}",
                },
            }

    if timed_out:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "ok": False,
                                "error": f"Tool '{name}' execution timed out after {MAX_TOOL_TIMEOUT_SECONDS}s",
                                "error_type": "timeout",
                                "tool": name,
                                "hints": ["Try a simpler input or shorter text"],
                            }
                        ),
                    }
                ],
                "isError": True,
            },
        }

    # If result is an error envelope, return as MCP tool result with isError
    if isinstance(result, dict) and result.get("ok") is False:
        serialized = json.dumps(result)
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "content": [{"type": "text", "text": serialized}],
                "isError": True,
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
                ],
                "isError": True,
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
    if names_filter is not None and not all(isinstance(n, str) for n in names_filter):
        return _invalid_request(request_id, "Invalid 'names' parameter: all items must be strings")

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
            "deprecated": schema.get("deprecated", False),
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

    # Validate JSON-RPC version
    jsonrpc_version = request.get("jsonrpc")
    if jsonrpc_version != "2.0":
        return _invalid_request(
            request.get("id"),
            f"Invalid Request: jsonrpc must be '2.0', got '{jsonrpc_version}'",
        )

    if "method" not in request:
        return _invalid_request(request.get("id"), "Invalid Request: missing 'method'")

    request_id = request.get("id")
    if request_id is not None:
        id_str = str(request_id)
        if len(id_str) > MAX_REQUEST_ID_LENGTH:
            return _invalid_request(
                None,
                f"Invalid Request: 'id' exceeds maximum length of {MAX_REQUEST_ID_LENGTH}",
            )

    method = request["method"]
    if not isinstance(method, str):
        return _invalid_request(
            request.get("id"),
            "Invalid Request: 'method' must be a string",
        )

    if method == "tools/list":
        return _handle_list_tools(request)
    elif method == "tools/call":
        return _handle_call_tool(request)
    elif method == "initialize":
        return _handle_initialize(request)
    elif method == "notifications/initialized":
        return None
    elif method == "notifications/cancelled":
        return None
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {},
        }
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
    import os
    os.environ["EGGCALC_NO_CONFIG"] = "1"
    _evaluator._mcp_mode = True
    request_times: deque[float] = deque()
    window = 1.0  # sliding window in seconds

    for line in sys.stdin:
        try:
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
                message = _sanitize_error(str(e))[:500]
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if isinstance(request, dict) else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {message}",
                    },
                }

            if response is not None:
                try:
                    print(json.dumps(response), flush=True)
                except TypeError:
                    fallback = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32603,
                            "message": "Internal error: response not JSON-serializable",
                        },
                    }
                    print(json.dumps(fallback), flush=True)
        except BrokenPipeError:
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# Build-time alias for MCP entry point
mcp_main = main
