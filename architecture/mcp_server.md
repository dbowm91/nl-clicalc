# mcp_server.md - MCP Server Implementation

## Purpose

Model Context Protocol (MCP) server for exposing nl-calc exact tools to AI agents via stdio-based communication.

## Architecture

```
AI Agent <--JSON-RPC--> MCP Server <---> nl-calc exact tools
                              |
                              +-- primitives
                              +-- unicode_tools
                              +-- diff
                              +-- validate
                              +-- measure
                              +-- synthesis
```

## Protocol

Uses JSON-RPC 2.0 over stdio:
- Requests read from stdin
- Responses written to stdout
- Errors written to stderr with JSON-RPC error format

## Request Handling

### `handle_request(request: Any) -> dict | None`

Routes MCP requests to appropriate handlers:

| Method | Handler | Description |
|--------|---------|-------------|
| `initialize` | `_handle_initialize()` | Initialize connection |
| `tools/list` | `_handle_list_tools()` | List available tools |
| `tools/call` | `_handle_call_tool()` | Execute a tool |
| `notifications/initialized` | None | Acknowledgment |

### `_handle_list_tools(request: dict) -> dict`

Returns tool definitions with schemas:

```python
{
    "jsonrpc": "2.0",
    "id": request["id"],
    "result": {
        "tools": [
            {
                "name": "math_eval",
                "description": "...",
                "inputSchema": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            },
            ...
        ]
    }
}
```

### `_handle_call_tool(request: dict) -> dict`

Executes a tool and returns results:

```python
{
    "jsonrpc": "2.0",
    "id": request["id"],
    "result": {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result)
            }
        ]
    }
}
```

## Available Tools

### `math_eval`

Evaluate arithmetic, unit conversions, constants, and scientific expressions.

### `text_measure`

Measure exact text properties (UTF-8 bytes, codepoints, words, lines, etc.).

### `text_equal`

Compare two strings under raw, Unicode-normalized, casefolded, or trimmed modes.

### `text_diff_explain`

Explain why two strings differ with diff spans, codepoints, and classification.

### `text_inspect`

Inspect a string for hidden characters, confusables, mixed scripts.

### `text_count`

Count exact characters or produce frequency table.

### `validate_brackets`

Check bracket balance.

### `validate_json`

Validate JSON syntax.

### `validate_regex`

Test regex patterns against samples.

### `list_compare`

Compare two lists with optional ignore_order, casefold, normalization.

## Error Handling

Errors are wrapped in standardized envelopes:

```python
class ErrorEnvelope(TypedDict):
    ok: Literal[False]
    error_type: str      # "ValidationError", "InputTooLarge", etc.
    error: str           # Error message
    hints: list[str]    # Suggestions for fixing
```

## Entry Point

### `main() -> int`

Main entry point:
1. Reads JSON-RPC requests from stdin (line by line)
2. Handles each request
3. Writes responses to stdout
4. Returns exit code

## Files

| File | Purpose |
|------|---------|
| `server.py` | MCP protocol handling |
| `tools.py` | Tool implementations |
| `schemas.py` | JSON schemas for tool definitions |

## Index

See [overview.md](overview.md) for the module index.