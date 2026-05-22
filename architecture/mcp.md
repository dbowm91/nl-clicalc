# mcp/ — Model Context Protocol Server

MCP server providing AI agent tool access to nl-calc's exact text analysis functions via a stdio-based JSON-RPC interface.

## Module Structure

```
mcp/
├── __init__.py   # Empty package marker
├── schemas.py    # Tool input/output schemas
├── tools.py      # Tool implementations
└── server.py     # MCP protocol handler
```

## Overview

The MCP server exposes exact text analysis tools to AI agents. It provides:
- JSON-RPC 2.0 protocol handling
- Tool discovery via `tools/list`
- Tool execution via `tools/call`
- Standardized error envelopes
- Input validation and sanitization

## schemas.py — Tool Schemas

Defines input/output schemas for each MCP tool.

### Error Envelope

```python
class ErrorEnvelope(TypedDict):
    ok: bool                    # Always False for errors
    error_type: str             # Error category
    error: str                  # Error message (ASCII-safe)
    hints: list[str]           # Suggested fixes
```

### Success Envelope

```python
class SuccessEnvelope(TypedDict):
    ok: bool                    # Always True for success
    result: dict               # Tool-specific result
```

### TOOL_SCHEMAS

Registry of all available tools:

| Tool Name | Description |
|-----------|-------------|
| `math_eval` | Evaluate arithmetic, unit conversions, constants |
| `text_measure` | Measure text properties (bytes, codepoints, words, lines) |
| `text_equal` | Compare strings with multiple equality modes |
| `text_diff_explain` | Explain string differences |
| `text_inspect` | Inspect for hidden characters, confusables |
| `text_count` | Count characters or frequency table |
| `text_truncate` | Truncate to grapheme boundary |
| `validate_brackets` | Check balanced brackets |
| `validate_json` | Validate JSON syntax |
| `validate_regex` | Test regex against samples |
| `list_compare` | Compare two lists |

### math_eval Schema

```python
"math_eval": {
    "description": "Deterministically evaluate arithmetic...",
    "inputSchema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression (e.g., '5 + 3', '30m + 100ft')"
            }
        },
        "required": ["expression"]
    }
}
```

### text_measure Schema

```python
"text_measure": {
    "description": "Measure exact text properties...",
    "inputSchema": {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "include_codepoints": {"type": "boolean", "default": False}
        },
        "required": ["text"]
    }
}
```

### text_equal Schema

```python
"text_equal": {
    "description": "Compare two strings under raw, NFC, casefolded...",
    "inputSchema": {
        "type": "object",
        "properties": {
            "a": {"type": "string"},
            "b": {"type": "string"},
            "normalization": {
                "type": "string",
                "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"],
                "default": "raw"
            },
            "casefold": {"type": "boolean", "default": False},
            "trim": {"type": "boolean", "default": False}
        },
        "required": ["a", "b"]
    }
}
```

---

## tools.py — Tool Implementations

Wraps exact/ functions with error handling, sanitization, and response envelopes.

### Response Helpers

```python
def _error_response(error_type: str, error: str, hints: list[str] | None = None) -> dict:
    """Create standardized error envelope."""
    return ErrorEnvelope(
        ok=False,
        error_type=error_type,
        error=_sanitize_error(error),
        hints=[_sanitize_error(h) for h in (hints or [])]
    )

def _success_response(result: Any) -> dict:
    """Create standardized success envelope."""
    return {"ok": True, "result": result}
```

### Error Sanitization

```python
def _sanitize_error(message: str) -> str:
    """Remove non-ASCII characters from error messages."""
    return message.encode("ascii", "replace").decode("ascii")
```

### Tool Implementations

| Function | Wraps | Notes |
|----------|-------|-------|
| `math_eval(expression)` | `evaluate_raw()` | Math evaluation |
| `text_measure(text, include_codepoints)` | `measure_text()` | Text metrics |
| `text_equal(a, b, normalization, casefold, trim)` | `text_equal()` | String comparison |
| `text_diff_explain(a, b, max_diffs, ...)` | `explain_diff()` | Diff explanation |
| `text_inspect(text, include_codepoints, ...)` | `inspect_text()` | Hidden char inspection |
| `text_count(text, target, normalization)` | `count_chars()` | Char counting |
| `text_truncate(text, max_graphemes)` | `truncate_to_grapheme()` | Truncation |
| `validate_brackets(text)` | `check_brackets()` | Bracket validation |
| `validate_json(text)` | `validate_json()` | JSON validation |
| `validate_regex(pattern, samples)` | `regex_test()` | Regex testing |
| `list_compare(a, b)` | `list_compare()` | List comparison |

### Input Limits

```python
MAX_TEXT_LENGTH = 100_000      # Maximum input text length
MAX_EXPRESSION_LENGTH = 10_000 # Maximum math expression
MAX_LIST_ITEMS = 10_000       # Maximum list items for comparison
MAX_REGEX_SAMPLES = 100       # Maximum regex test samples
```

---

## server.py — MCP Protocol Handler

stdio-based JSON-RPC 2.0 server implementation.

### Request Handling

```python
def handle_request(request: Any) -> dict | None:
    """Route MCP request to appropriate handler."""
    if request.get("method") == "tools/list":
        return _handle_list_tools(request)
    elif request.get("method") == "tools/call":
        return _handle_call_tool(request)
    else:
        return _invalid_request(request.get("id"), "Method not found")
```

### Tool Handler Map

```python
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
```

### Close Match Suggestions

When an unknown tool is requested, the server suggests close matches:

```python
def _find_close_match(name: str, handlers: dict[str, Any]) -> str | None:
    """Find a case-insensitive close match for tool name."""
    # Returns suggested tool name or None
```

### Error Codes

| Code | Name | Description |
|------|------|-------------|
| -32600 | InvalidRequest | Invalid JSON-RPC request |
| -32602 | InvalidParams | Invalid method parameters |
| -32603 | InternalError | Internal error |
| -32000 | ToolError | Tool execution error |

### Response Format

```python
# Success
{
    "jsonrpc": "2.0",
    "id": request_id,
    "result": {
        "content": [
            {"type": "text", "text": json.dumps(result)}
        ]
    }
}

# Error
{
    "jsonrpc": "2.0",
    "id": request_id,
    "error": {
        "code": -32000,
        "message": "Error description",
        "data": error_envelope
    }
}
```

---

## Usage

### CLI Mode (Calculator)

```bash
python nl_calc.py "five plus three"
# Output: 8
```

### MCP Mode (Server)

```bash
python nl_calc.py --mcp
```

Then send JSON-RPC requests via stdio:

```json
// List tools
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}

// Call tool
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
    "name": "text_measure",
    "arguments": {"text": "Hello, World!"}
}}
```

---

## Architecture Notes

```
┌─────────────────────────────────────────────────────────────────────┐
│                            MCP Server                                │
│                       (stdio-based JSON-RPC)                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐    │
│  │  schemas.py │     │  tools.py   │     │     server.py      │    │
│  │             │     │             │     │                     │    │
│  │ TOOL_SCHEMAS│────▶│ Wraps exact │◀────│ Request routing    │    │
│  │             │     │ functions   │     │ Error handling     │    │
│  └─────────────┘     └──────┬──────┘     └─────────────────────┘    │
│                             │                                        │
├─────────────────────────────┴────────────────────────────────────────┤
│                            exact/                                     │
│                    (Text analysis primitives)                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Features

1. **Unified Tool Registry** — `TOOL_SCHEMAS` in schemas.py is single source of truth
2. **Case-insensitive matching** — Tool names matched case-insensitively with suggestions
3. **Standardized Responses** — All tools use Success/Error envelopes
4. **Error Sanitization** — Non-ASCII stripped from error messages
5. **Input Validation** — Length limits enforced before processing

### MCP vs Direct Usage

| Feature | MCP Server | Direct Import |
|---------|-----------|----------------|
| Interface | stdio/JSON-RPC | Python API |
| Use case | AI agents | Embedded usage |
| Functions | Subset | All |
| Error format | Envelope | Exceptions |