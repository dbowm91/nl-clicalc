# MCP Module Architecture Review - Improvement Plan

## Verified Claims

### 1. Module Structure (mcp.md:6-13)
```python
mcp/
├── __init__.py   # Empty package marker ✓
├── schemas.py    # Tool input/output schemas ✓
├── tools.py      # Tool implementations ✓
└── server.py     # MCP protocol handler ✓
```

### 2. TOOL_HANDLERS Map (server.py:29-41)
All 11 tools are correctly registered in server.py:29-41 matching documentation.

### 3. Case-insensitive Tool Matching (server.py:56-64)
`_find_close_match()` correctly implements case-insensitive matching with substring fallback.

### 4. Input Limits (tools.py:46-49)
```python
MAX_TEXT_LENGTH = 100_000
MAX_EXPRESSION_LENGTH = 10_000
MAX_LIST_ITEMS = 10_000
MAX_REGEX_SAMPLES = 100
```
All limits correctly documented in mcp.md:170-175.

### 5. Error Sanitization (tools.py:52-54)
```python
def _sanitize_error(message: str) -> str:
    return message.encode("ascii", "replace").decode("ascii")
```
Correctly removes non-ASCII characters from error messages.

### 6. Success Response Format (tools.py:67-69)
```python
def _success_response(result: Any) -> dict:
    return {"ok": True, "result": result}
```
Matches architecture docs.

---

## Discrepancies

### 1. SuccessEnvelope Documented but Not Implemented

**Location:** mcp.md:38-44 documents `SuccessEnvelope` TypedDict, but schemas.py only defines `ErrorEnvelope`.

**Code Evidence:**
- schemas.py:13-18 only has `ErrorEnvelope`
- No `SuccessEnvelope` class exists
- tools.py:67-69 returns `{"ok": True, "result": result}` as plain dict

**Impact:** Low - code works correctly but documentation is incomplete.

### 2. Error Response Format Inconsistency for math_eval

**Location:** tools.py:89 vs other tools

**Code Evidence:**
```python
# math_eval (line 89):
return {"result": str(result_val), "type": type(result_val).__name__}

# Other tools (e.g., text_measure line 115):
return _success_response(result)
```

**Impact:** Medium - `math_eval` returns raw dict not wrapped in `{"ok": True, "result": ...}` envelope. This is inconsistent with other tools and could break clients expecting uniform response format.

### 3. Missing _handle_initialize Function

**Location:** mcp_server.md:34-35 shows `_handle_initialize()` as separate handler

**Code Evidence:**
- server.py:160-174 handles `initialize` inline in `handle_request()`
- No separate `_handle_initialize()` function exists

**Impact:** Low - functionality works, just differently organized than documented.

### 4. Error Code Table Incomplete

**Location:** mcp_server.md:226-231 missing -32601 MethodNotFound

**Code Evidence:**
- server.py:182 returns -32601 for unknown methods
- mcp_server.md error table only shows -32600, -32602, -32603, -32000

**Impact:** Low - documentation missing an error code.

---

## Potential Bugs

### 1. text_truncate: Negative max_graphemes Validation Missing

**Location:** tools.py:377-419

**Code Evidence:**
```python
if max_graphemes < 0:  # line 394-399
    return _error_response(...)

try:
    original_graphemes = _count_graphemes(text)  # line 402
```

The negative check exists but comes AFTER the max_graphemes parameter is declared without `minimum: 0` in schemas.py:155. The schema should enforce this.

**Fix Priority:** Medium

### 2. Type Validation Missing on Multiple Tools

**Location:** tools.py - multiple functions

**Code Evidence:**
- `math_eval` (line 72): `expression` not validated as string
- `text_measure` (line 96): `include_codepoints` not validated as bool
- `text_equal` (line 120): `casefold`, `trim` not validated as bool
- `text_inspect` (line 187): `include_codepoints`, `include_confusables` not validated
- `validate_regex` (line 307): `flags` items not validated against valid Python regex flags

**Impact:** Low - would cause errors downstream, but errors are caught. However, gives poor error messages.

**Fix Priority:** Low

### 3. validate_brackets: pairs Parameter Not Validated

**Location:** tools.py:260-281

**Code Evidence:**
```python
def validate_brackets(text: str, pairs: dict[str, str] | None = None) -> dict:
    ...
    result = _check_brackets(text, pairs)  # line 278 - no type validation
```

If `pairs` is not a dict or has wrong structure, error message won't be helpful.

**Fix Priority:** Low

---

## Improvement Suggestions

### High Priority

1. **Fix math_eval response format inconsistency**
   - Location: tools.py:89
   - Change to `_success_response({"result": str(result_val), "type": type(result_val).__name__})`
   - Ensures consistent envelope format across all tools

### Medium Priority

2. **Add minimum constraint to text_truncate schema**
   - Location: schemas.py:155
   - Add `"minimum": 0` to `max_graphemes` property

3. **Add type validation to tools**
   - Validate `expression` is str in `math_eval`
   - Validate `include_codepoints`, `casefold`, `trim` etc. are bool
   - Return ValidationError with clear message instead of letting exceptions propagate

### Low Priority

4. **Document SuccessEnvelope removal** or add it back
   - If intentional, remove from mcp.md:38-44

5. **Complete error code table in mcp_server.md**
   - Add -32601 MethodNotFound to error table

6. **Separate _handle_initialize function**
   - If desired for consistency, extract lines 160-174 to `_handle_initialize()`

7. **Validate pairs parameter in validate_brackets**
   - Check `pairs` is dict or None before passing to _check_brackets

8. **Add outputSchema to remaining tools**
   - Only text_truncate has outputSchema in schemas.py

---

## Summary

The MCP implementation is solid with only minor inconsistencies:

| Issue | Severity | Fix Effort |
|-------|----------|------------|
| math_eval response format | Medium | Low (1 line change) |
| Missing type validation | Low | Medium (multiple tools) |
| Schema minimum constraint | Medium | Low (1 line change) |
| SuccessEnvelope discrepancy | Low | Documentation only |
| Error code table incomplete | Low | Documentation only |

Core functionality is correct. All tools work, error handling is in place, and the protocol implementation follows JSON-RPC 2.0 spec correctly.