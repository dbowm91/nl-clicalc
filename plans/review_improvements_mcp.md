# mcp Module Review — Improvement Plan

**Reviewed:** architecture/mcp.md against nl_calc/mcp/server.py, tools.py, schemas.py
**Date:** 2026-05-28

## Verified Claims (with line references)

### Protocol & Architecture
- **stdio-based JSON-RPC 2.0**: Verified in `server.py:193-231` - reads from `sys.stdin`, writes to `sys.stdout`
- **JSON-RPC version**: All responses include `"jsonrpc": "2.0"` (server.py:47, 144, 152, etc.)

### Error Codes (server.py:44-53, 186-189, 222-225)
| Code | Name | Used |
|------|------|------|
| -32600 | InvalidRequest | _invalid_request(), line 50 |
| -32601 | MethodNotFound | handle_request() else branch, line 187 |
| -32602 | InvalidParams | _handle_call_tool() unknown tool, line 87 |
| -32603 | InternalError | main() exception handler, line 223 |
| -32000 | ToolError | _handle_call_tool() error envelope, line 102; exception, line 126 |
| -32700 | ParseError | main() JSON decode error, line 209 |

### TOOL_SCHEMAS (schemas.py:21-331)
All 11 tools present and match documentation:
- math_eval (line 22)
- text_measure (line 42)
- text_equal (line 67)
- text_diff_explain (line 101)
- text_inspect (line 136)
- text_count (line 166)
- text_truncate (line 194)
- validate_brackets (line 218)
- validate_json (line 240)
- validate_regex (line 259)
- list_compare (line 287)

### ErrorEnvelope TypedDict (schemas.py:13-18)
```python
class ErrorEnvelope(TypedDict):
    ok: bool
    error_type: str
    error: str
    hints: list[str]
```
Matches documentation exactly.

### Input Limits (tools.py:46-49)
```python
MAX_TEXT_LENGTH = 100_000
MAX_EXPRESSION_LENGTH = 10_000
MAX_LIST_ITEMS = 10_000
MAX_REGEX_SAMPLES = 100
```
Match documentation exactly.

### Response Helpers (tools.py:52-69)
`_sanitize_error()`, `_error_response()`, `_success_response()` all match documented signatures.

### TOOL_HANDLERS Map (server.py:29-41)
All 11 tools correctly mapped to handler functions.

---

## Discrepancies Between Documentation and Code

- [MEDIUM] **Entry point line number mismatch**
  - Documentation says: `mcp_main` is defined in `server.py:234`
  - Code actually does: `mcp_main = main` is at line **239**
  - Impact: Debugging/reference confusion

- [MEDIUM] **Error response "data" field underspecified**
  - Documentation shows error format (lines 262-271) with `"data": error_envelope` but doesn't clarify that `error_envelope` is the full ErrorEnvelope dict (with `ok`, `error_type`, `error`, `hints` nested inside `data`)
  - Code at server.py:103-104 puts `result` (the ErrorEnvelope) directly in `data`
  - Impact: API consumers may not know to look inside `data` for `error_type` and `hints`

- [LOW] **`initialize` not in TOOL_HANDLERS**
  - Documentation acknowledges this (line 208: "Note: `_handle_initialize` is a separate function... called directly") but shows `TOOL_HANDLERS` as a map (lines 212-225) that implies all methods should be in it
  - The `initialize` method is handled via conditional at server.py:178-179, not via the handler map
  - Impact: Minor confusion about architecture

- [LOW] **text_truncate schema shows `"default": null for max_graphemes**
  - Documentation shows `text_truncate` schema with `max_graphemes` having no default (lines 194-207)
  - Code in tools.py:382-423 requires `max_graphemes` as a required positional argument
  - This is actually **correct in both** - the schema requires it and the function requires it
  - Impact: No issue, but could note that `max_graphemes` is required

---

## Potential Bugs

- [MEDIUM] **Bare `except Exception` in _handle_call_tool (server.py:121)**
  ```python
  except Exception as e:
      return {
          "jsonrpc": "2.0",
          "id": request.get("id"),
          "error": {
              "code": -32000,
              "message": f"Tool execution error: {str(e)}",
          },
      }
  ```
  This catches all exceptions including `KeyboardInterrupt`, `SystemExit`, `MemoryError`, etc. Should catch only expected tool errors:
  ```python
  except (ValueError, TypeError, EvaluationError) as e:
  ```
  or at minimum use `except BaseException as e` and re-raise `SystemExit`/`KeyboardInterrupt`.

- [LOW] **Notification with id returns None, client never receives response**
  - Per JSON-RPC 2.0 spec, a response should be sent if `id` is present, even for notifications
  - Current code at server.py:180-181 returns `None` for `notifications/initialized`, which is correct for proper notifications (no id)
  - However, if a client sends `{"jsonrpc": "2.0", "id": 1, "method": "notifications/initialized"}` (incorrect but possible), they get no response
  - Impact: Non-compliant clients may hang waiting for response

- [LOW] **No input size limit at main() entry before json.loads**
  - `main()` at server.py:198 reads entire line and calls `json.loads(line)` without size check
  - A malicious client could send multi-MB input causing memory exhaustion before any tool limit checks
  - `MAX_TEXT_LENGTH` etc. are checked INSIDE tool handlers, after parsing
  - Impact: Potential DoS vector

---

## Improvement Suggestions

### HIGH Priority

1. **Fix bare `except Exception` in `_handle_call_tool`** (server.py:121)
   - Change to catch specific expected exceptions or re-raise `SystemExit`/`KeyboardInterrupt`
   - Prevents masking serious errors like `MemoryError` or `RecursionError`

2. **Add input size limit at stdio read** (server.py:198-204)
   - Add `MAX_LINE_LENGTH = 1_000_000` constant
   - Check `len(line) > MAX_LINE_LENGTH` before `json.loads()` to prevent memory exhaustion

### MEDIUM Priority

3. **Clarify error "data" field structure in documentation**
   - Add explicit note that `data` contains the full ErrorEnvelope object
   - Example: `"data": {"ok": false, "error_type": "...", "error": "...", "hints": [...]}`

4. **Fix `mcp_main` line reference in docstring** (server.py:238)
   - Change "server.py:234" to "server.py:239"

### LOW Priority

5. **Consider adding `id` check for notifications**
   - If client sends notification with an `id`, return an error instead of silently ignoring
   - Aligns with JSON-RPC 2.0 spec "A method call that returns false NO result" - notifications shouldn't have id

6. **Add `MAX_LINE_LENGTH` documentation to architecture/mcp.md Input Limits section**
   - Document the raw stdio input limit alongside tool-level limits

---

## Summary

The MCP module documentation is largely accurate and well-structured. The core protocol implementation (stdio-based JSON-RPC 2.0), tool registry, error codes, and input limits all match between documentation and code. 

The main concerns are:
1. A potential bug where `except Exception` is too broad in the tool call handler
2. Missing stdio-level input size limit before JSON parsing
3. Minor documentation gaps around error response structure and one incorrect line reference

All HIGH and MEDIUM issues are straightforward to address and don't affect the core functionality for well-behaved clients.
