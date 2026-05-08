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
    validate_brackets,
    validate_json,
    validate_regex,
)

TOOL_HANDLERS: dict[str, Any] = {
    "math_eval": math_eval,
    "text_measure": text_measure,
    "text_equal": text_equal,
    "text_diff_explain": text_diff_explain,
    "text_inspect": text_inspect,
    "text_count": text_count,
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
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32602,
                "message": f"Unknown tool: {name}",
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
    tools = [
        {
            "name": "math_eval",
            "description": "Deterministically evaluate arithmetic, unit conversions, constants, and simple scientific expressions. Use for math and unit tasks instead of asking the model to calculate.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate (e.g., '5 + 3', '30m + 100ft', 'five plus three')",
                    },
                },
                "required": ["expression"],
            },
        },
        {
            "name": "text_measure",
            "description": "Measure exact text properties: UTF-8 byte length, codepoint count, words, lines, whitespace, newline style, Unicode normalization state, invisibles, and mixed-script signals.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Input string to measure",
                    },
                    "include_codepoints": {
                        "type": "boolean",
                        "description": "Include codepoint details (not yet implemented)",
                        "default": False,
                    },
                },
                "required": ["text"],
            },
        },
        {
            "name": "text_equal",
            "description": "Compare two strings under raw, Unicode-normalized, casefolded, or trimmed modes and report exact equality evidence.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "string", "description": "First string"},
                    "b": {"type": "string", "description": "Second string"},
                    "normalization": {
                        "type": "string",
                        "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"],
                        "default": "raw",
                        "description": "Unicode normalization form",
                    },
                    "casefold": {
                        "type": "boolean",
                        "default": False,
                        "description": "Use casefolded comparison",
                    },
                    "trim": {
                        "type": "boolean",
                        "default": False,
                        "description": "Trim whitespace",
                    },
                },
                "required": ["a", "b"],
            },
        },
        {
            "name": "text_diff_explain",
            "description": "Explain why two strings differ, including spans, codepoints, Unicode names, normalization equivalence, confusables, invisibles, and agent-facing classification.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "string", "description": "First string"},
                    "b": {"type": "string", "description": "Second string"},
                    "max_diffs": {
                        "type": "integer",
                        "default": 20,
                        "description": "Maximum diff spans to return",
                    },
                    "include_codepoints": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include codepoint details",
                    },
                    "include_context": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include context notes",
                    },
                },
                "required": ["a", "b"],
            },
        },
        {
            "name": "text_inspect",
            "description": "Inspect a string for hidden characters, Unicode confusables, mixed scripts, normalization state, and display-safe representation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Input string to inspect"},
                    "include_codepoints": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include codepoint details in invisibles",
                    },
                    "include_confusables": {
                        "type": "boolean",
                        "default": True,
                        "description": "Check for confusables",
                    },
                },
                "required": ["text"],
            },
        },
        {
            "name": "text_count",
            "description": "Count exact characters or produce a character frequency table with codepoint positions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Input string"},
                    "target": {
                        "type": "string",
                        "description": "Single character to count (None for frequency table)",
                    },
                    "normalization": {
                        "type": "string",
                        "enum": ["raw", "NFC", "NFKC"],
                        "default": "raw",
                        "description": "Unicode normalization form",
                    },
                },
                "required": ["text"],
            },
        },
        {
            "name": "validate_brackets",
            "description": "Check whether delimiters are structurally balanced and report unmatched delimiters with line/column positions.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Input string"},
                    "pairs": {
                        "type": "object",
                        "description": "Bracket pair mapping (default: () [] {} <>)",
                    },
                },
                "required": ["text"],
            },
        },
        {
            "name": "validate_json",
            "description": "Validate JSON and report precise parse errors or top-level structure information.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Input string to validate as JSON"},
                },
                "required": ["text"],
            },
        },
        {
            "name": "validate_regex",
            "description": "Test a Python regular expression against sample strings and report match/fullmatch status, spans, groups, and errors.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regular expression pattern"},
                    "samples": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of strings to test against",
                    },
                    "flags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Flag names (IGNORECASE, MULTILINE, etc.)",
                    },
                },
                "required": ["pattern", "samples"],
            },
        },
        {
            "name": "list_compare",
            "description": "Compare two lists exactly, optionally ignoring order, casefolding, or Unicode-normalizing elements. Report missing, duplicate, and near-match items.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "First list",
                    },
                    "b": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Second list",
                    },
                    "ignore_order": {
                        "type": "boolean",
                        "default": True,
                        "description": "Compare as sets",
                    },
                    "casefold": {
                        "type": "boolean",
                        "default": False,
                        "description": "Casefold elements before comparison",
                    },
                    "normalization": {
                        "type": "string",
                        "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"],
                        "default": "NFC",
                        "description": "Unicode normalization form",
                    },
                },
                "required": ["a", "b"],
            },
        },
    ]

    return {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {"tools": tools},
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
