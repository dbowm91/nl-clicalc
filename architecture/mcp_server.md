# mcp/ - MCP Server for AI Agents

## Purpose

Model Context Protocol server for exposing exact text tools to AI agents via stdio.

## Module Structure

```
mcp/
├── __init__.py      # Re-exports, package init
├── server.py        # stdio request handling
├── tools.py         # MCP tool definitions
└── schemas.py       # JSON schemas for tools
```

## Running the MCP Server

```bash
calc --mcp
```

The server reads JSON-RPC requests from stdin and writes responses to stdout.

## Server Implementation (server.py)

### `handle_request(request: dict) -> dict`

Main request handler:

```python
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "math_eval",
        "arguments": {"expression": "5 + 3"}
    }
}
```

### `main() -> int`

Entry point for `--mcp` mode.

## Available Tools (tools.py)

| Tool | Description |
|------|-------------|
| `math_eval` | Evaluate math expressions |
| `text_measure` | Text metrics (UTF-8 bytes, codepoints, words, lines) |
| `text_equal` | String comparison with normalization |
| `text_diff_explain` | Explain differences between strings |
| `text_inspect` | Hidden characters, confusables, mixed scripts |
| `text_count` | Character counting and frequency |
| `validate_brackets` | Bracket pair matching |
| `validate_json` | JSON parsing validation |
| `validate_regex` | Regex pattern testing |
| `list_compare` | List comparison |

## Tool Schemas (schemas.py)

JSON schemas defining tool inputs/outputs:

```python
TOOL_SCHEMAS = {
    "math_eval": {
        "name": "math_eval",
        "description": "Evaluate a mathematical expression",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"}
            },
            "required": ["expression"]
        }
    },
    ...
}
```

## Protocol Details

Uses JSON-RPC 2.0 over stdio:

1. Initialize handshake on startup
2. Tools/list to enumerate available tools
3. Tools/call to execute a tool
4. Notifications for progress/cancel

## Security

The MCP server inherits the security model of the underlying tools:
- Math evaluation uses AST-based parser
- Text tools are read-only primitives
- No arbitrary code execution
- Input validation on all tools