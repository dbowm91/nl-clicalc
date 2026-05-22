# Architecture Review: MCP Server

## Document Reviewed
- `architecture/mcp_server.md`
- Implementation in `nl_calc/mcp/` (server.py, tools.py, schemas.py)
- Integration via `build_single.py` and `nl_calc.py`

---

## Summary

The architecture document accurately describes the MCP server structure and protocol handling. The implementation is largely correct, but there are **several discrepancies** between the document and implementation, and **some bugs/edge cases** that need attention.

---

## 1. Document Claims vs. Implementation Verification

### 1.1 Module Structure - MATCHES ✓

| Document | Implementation |
|----------|---------------|
| `__init__.py` | EXISTS - Re-exports tools, schemas, server |
| `server.py` | EXISTS - handle_request(), main() |
| `tools.py` | EXISTS - 10 tool implementations |
| `schemas.py` | EXISTS - TOOL_SCHEMAS and TypedDicts |

All documented modules are present.

### 1.2 Running the Server - MATCHES ✓

```bash
calc --mcp
```

The CLI argument `--mcp` is correctly implemented in both `__main__.py` and `nl_calc.py` (via build_single.py).

### 1.3 Server Implementation - MATCHES ✓

`handle_request(request: dict) -> dict` correctly routes:
- `initialize` → Returns protocol version 2024-11-05, capabilities, server info
- `tools/list` → Returns tool list with schemas
- `tools/call` → Delegates to handlers
- `notifications/initialized` → Returns None (no response needed)
- Unknown methods → Error -32601

### 1.4 Available Tools - MATCHES ✓

All 10 tools documented are implemented:
| Tool | Status |
|------|--------|
| `math_eval` | ✓ Implemented |
| `text_measure` | ✓ Implemented |
| `text_equal` | ✓ Implemented |
| `text_diff_explain` | ✓ Implemented |
| `text_inspect` | ✓ Implemented |
| `text_count` | ✓ Implemented |
| `validate_brackets` | ✓ Implemented |
| `validate_json` | ✓ Implemented |
| `validate_regex` | ✓ Implemented |
| `list_compare` | ✓ Implemented |

### 1.5 Protocol Details - MATCHES ✓

- JSON-RPC 2.0 over stdio ✓
- Initialize handshake on startup ✓
- tools/list to enumerate ✓
- tools/call to execute ✓
- Notifications for progress/cancel (handled as no-op) ✓

### 1.6 Security - MATCHES ✓

- Math evaluation uses AST-based parser ✓
- Text tools are read-only primitives ✓
- No arbitrary code execution ✓
- Input validation on all tools ✓

---

## 2. DISCREPANCIES

### 2.1 Tool Names in schemas.py vs server.py - MISMATCH

**Issue**: `schemas.py` defines tool names with `nl_` prefix:
- `nl_calculate`
- `nl_measure_text`
- `nl_text_equal`
- etc.

But `server.py` uses non-prefixed names in `TOOL_HANDLERS`:
- `math_eval`
- `text_measure`
- `text_equal`
- etc.

**Impact**: The schemas in `schemas.py` are never used at runtime. The actual tool names are defined inline in `server.py` `_handle_list_tools()`. The `TOOL_SCHEMAS` dict in `schemas.py` appears to be dead code.

### 2.2 Error Envelope Inconsistency

**Issue**: In `tools.py`, error responses use `error_type` with capital letters:
```python
_error_response("InputTooLarge", ...)
_error_response("ValidationError", ...)
```

But in `server.py` error responses use lowercase error codes in the message:
```python
"message": result.get("error", "Unknown error")
```

The JSON-RPC error responses do not include the `error_type` field from the envelope.

### 2.3 Success Response Double-Wrapping

**Issue**: Tool results go through two wrapping layers:

1. Tool returns `_success_response({"result": str(result_val), "type": type(result_val).__name__})` - wraps with `ok=True`
2. Server wraps again: `{"content": [{"type": "text", "text": json.dumps(result)}]}`

**Result**: Final response is:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{"type": "text", "text": "{\"ok\": true, \"result\": {\"result\": \"8\", \"type\": \"int\"}}"}]
  }
}
```

The actual result is deeply nested and double-encoded as JSON string inside a text content block.

### 2.4 tool/call Missing "arguments" Parameter Structure

**Issue**: The document shows `tools/call` with `arguments` as a dict:
```json
{"name": "math_eval", "arguments": {"expression": "5 + 3"}}
```

But MCP protocol typically uses:
```json
{"name": "math_eval", "arguments": {"expression": "5 + 3"}}
```

Actually this is correct per the code at line 43-44:
```python
name = request.get("params", {}).get("name", "")
arguments = request.get("params", {}).get("arguments", {})
```

This matches the MCP protocol spec.

---

## 3. BUGS AND EDGE CASES

### 3.1 BUG: Missing Response for Initialize Request ID

**Location**: `server.py` lines 329-343

**Issue**: The `initialize` handler correctly returns `id: request.get("id")`, but MCP clients may send the request without an ID (notifications), or with a null ID. The code handles this, but...

**Edge case**: If `initialize` returns an error response (e.g., unsupported protocol version), it should still have an ID if the request had one.

**Status**: Currently works but could be more robust.

### 3.2 BUG: Input Validation Gap in math_eval

**Location**: `tools.py` line 62-81

**Issue**: `math_eval` does not enforce `MAX_TEXT_LENGTH` like other tools do. A very long expression could be passed to `evaluate_raw()`.

**Code**:
```python
def math_eval(expression: str) -> dict:
    try:
        result = evaluate_raw(expression)  # No length check!
```

While `evaluate_raw` may have its own limits, there's no explicit check in the MCP tool.

### 3.3 BUG: _handle_list_tools Uses Inline Definitions Instead of schemas.py

**Location**: `server.py` lines 96-318

**Issue**: The tool list is hardcoded inline in `_handle_list_tools()` instead of using the `TOOL_SCHEMAS` from `schemas.py`. This creates a duplication issue where changes must be made in two places.

**Example**: `text_inspect` schema in `_handle_list_tools`:
```python
{
    "name": "text_inspect",
    "description": "Inspect a string for hidden characters...",
    "inputSchema": {...}
}
```

Should potentially use `TOOL_SCHEMAS["nl_inspect_text"]` but doesn't.

### 3.4 EDGE CASE: Empty Request ID Handling

**Location**: `server.py` line 369 and elsewhere

**Issue**: When JSON parsing fails, the error response uses:
```python
{"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error: invalid JSON"}}
```

No `id` field is included, which is correct for parse errors per JSON-RPC spec. This is actually correct behavior.

### 3.5 EDGE CASE: Unicode in Error Messages

**Location**: `server.py` line 91

**Issue**: Error messages from tool execution are passed through directly:
```python
"message": f"Tool execution error: {str(e)}"
```

If `str(e)` contains non-ASCII characters or control sequences, they could cause issues for the client parsing JSON. There's no sanitization.

### 3.6 EDGE CASE: Tool Names Are Case-Sensitive

**Location**: `server.py` line 46

**Issue**: `if name not in TOOL_HANDLERS:` - tool names are case-sensitive. A client sending `"MathEval"` or `"MATH_EVAL"` would get "Unknown tool" instead of a suggestion.

The MCP spec typically allows mixed-case tool names, but this implementation expects exact lowercase matching.

### 3.7 Missing: Progress/Cancel Notification Handling

**Location**: `server.py` line 344-345

**Issue**: `notifications/initialized` returns `None` and prints nothing. But MCP also defines:
- `notifications/cancel` - to cancel a request
- `notifications/progress` - for long-running operations

These are not handled. For `cancel`, the server would need to track request IDs and support cancellation of `evaluate_raw` calls (which they don't currently).

### 3.8 Missing: tools/list Changed Notification

**Location**: `server.py` `_handle_list_tools`

**Issue**: The server advertises `"listChanged": False` in capabilities, which is correct if tools are static. However, there's no mechanism to send a `notifications/tools/list_changed` if tools were dynamically updated.

---

## 4. IMPROVEMENTS

### 4.1 High Priority: Fix Double-Wrapping of Results

The response structure is over-nested. Consider simplifying to:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"ok\": true, \"result\": {...}}"
      }
    ]
  }
}
```

Or even direct result (if that's valid MCP):
```json
{
  "jsonrpc": "2.0", 
  "id": 1,
  "result": {"ok": true, "result": {...}}
}
```

### 4.2 High Priority: Add Input Length Check to math_eval

```python
def math_eval(expression: str) -> dict:
    if len(expression) > MAX_TEXT_LENGTH:
        return _error_response(
            "InputTooLarge", 
            f"Expression length {len(expression)} exceeds maximum",
            [f"Maximum input length is {MAX_TEXT_LENGTH}"]
        )
    # ... rest
```

### 4.3 Medium: Unify Tool Definitions

Either:
1. Use `TOOL_SCHEMAS` from `schemas.py` in `_handle_list_tools()`, or
2. Remove `schemas.py` `TOOL_SCHEMAS` as dead code

Recommend option 1 - refactor `_handle_list_tools` to reference a single source of truth.

### 4.4 Medium: Add Case-Insensitive Tool Name Matching

Either reject unknown tools with a suggestion:
```python
if name not in TOOL_HANDLERS:
    # Suggest closest match
    suggestions = [t for t in TOOL_HANDLERS if Levenshtein distance < 3]
    return {"error": {"code": -32602, "message": f"Unknown tool: {name}", "data": {"suggestions": suggestions}}}
```

Or document that tool names are case-sensitive.

### 4.5 Medium: Sanitize Error Messages

Add error message sanitization to prevent control characters in JSON-RPC error messages.

### 4.6 Low: Add Cancel Notification Support

For long-running operations, the server could track running requests and support cancellation via `notifications/cancel`. Currently `evaluate_raw` doesn't support timeout/interrupt.

### 4.7 Low: Document Tool Name Prefix Issue

If the `nl_` prefix in schemas.py was intentional for a different naming scheme, document why `TOOL_SCHEMAS` exists but isn't used.

---

## 5. TESTING GAPS

### 5.1 No MCP Server Tests

**Issue**: There are no tests for the MCP server functionality.

**Coverage needed**:
- Protocol handshake (initialize)
- tools/list returns correct schema
- tools/call with valid and invalid tool names
- Error handling for malformed requests
- Edge cases (empty input, very long input, Unicode in errors)
- JSON parsing errors

### 5.2 No Integration Tests

**Issue**: No end-to-end tests that verify the full MCP request/response cycle.

**Recommendation**: Add tests using subprocess to test `calc --mcp` with JSON-RPC requests.

---

## 6. SECURITY CONSIDERATIONS

### 6.1 ReDoS in Regex Tool

**Location**: `validate_regex` in `tools.py` lines 295-321

**Issue**: `MAX_REGEX_SAMPLES` limits sample count, but regex pattern itself could cause ReDoS (Regular expression Denial of Service) on long input.

**Mitigation**: Consider adding pattern complexity limits or timeout for regex evaluation.

### 6.2 Resource Exhaustion via math_eval

**Location**: `math_eval` - no length limit on expression

**Issue**: Very long expressions could cause excessive CPU/memory usage.

**Recommendation**: Add `MAX_EXPRESSION_LENGTH` similar to `MAX_TEXT_LENGTH`.

---

## 7. RECOMMENDED ACTION ITEMS

| Priority | Issue | Action |
|----------|-------|--------|
| High | Double-wrapping | Simplify response structure or document intentional nesting |
| High | math_eval no length check | Add `MAX_TEXT_LENGTH` check |
| Medium | Tool name mismatch (nl_ prefix) | Decide on naming scheme, remove dead code |
| Medium | Case-sensitive tool names | Add suggestions or document as case-sensitive |
| Medium | Error message sanitization | Add sanitization for non-ASCII in errors |
| Low | Cancel notification support | Add tracking for cancellable operations |
| Low | Missing MCP tests | Add integration tests for MCP protocol |

---

## 8. FILES REVIEWED

| File | Issues Found |
|------|-------------|
| `architecture/mcp_server.md` | Documentation accurate |
| `nl_calc/mcp/__init__.py` | OK - re-exports correct items |
| `nl_calc/mcp/server.py` | 3 bugs, 2 improvements |
| `nl_calc/mcp/tools.py` | 2 bugs, 1 improvement |
| `nl_calc/mcp/schemas.py` | Dead code (TOOL_SCHEMAS unused) |
| `build_single.py` | Correctly handles MCP module |
| `nl_calc.py` | MCP integration correct |

---

## Conclusion

The MCP server implementation is mostly correct and follows the architecture document. The main issues are:

1. **Over-nested response structure** - results are double-wrapped
2. **Input validation gaps** - math_eval lacks length check
3. **Dead code** - schemas.py TOOL_SCHEMAS not used
4. **No test coverage** - MCP protocol not tested

The server is functional but would benefit from the high-priority fixes above before production use with untrusted clients.
