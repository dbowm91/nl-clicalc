# MCP Architecture Review

Review of `architecture/mcp.md` against actual implementation in `nl_calc/mcp/`.

---

## Module Structure

| Claim | Status | Notes |
|-------|--------|-------|
| `__init__.py` empty package marker | **MATCHES** | Exists but not referenced in doc |
| `schemas.py` | **MATCHES** | |
| `tools.py` | **MATCHES** | |
| `server.py` | **MATCHES** | |

---

## ErrorEnvelope

| Claim | Status | Notes |
|-------|--------|-------|
| `ok: bool` | **MATCHES** | schemas.py:15 |
| `error_type: str` | **MATCHES** | schemas.py:16 |
| `error: str` | **MATCHES** | schemas.py:17 |
| `hints: list[str]` | **MATCHES** | schemas.py:18 |

**ISSUE (LOW):** The `ErrorEnvelope` TypedDict in schemas.py only defines 4 fields, but `_error_response()` in tools.py adds `tool`, `warnings`, and `limits_applied` fields at runtime. This works in Python (TypedDict is not enforced at runtime) but is inconsistent with the documented schema.

---

## TOOL_SCHEMAS

| Claim | Status | Notes |
|-------|--------|-------|
| 11 tools documented | **MISMATCH** | Actual implementation has **39 tools** |
| Documented tool list | **MISMATCH** | List is stale; many tools missing |

**Documented (11):**
- math_eval ✓
- text_measure ✓
- text_equal ✓
- text_diff_explain ✓
- text_inspect ✓
- text_count ✓
- text_truncate ✓
- validate_brackets ✓
- validate_json ✓
- validate_regex ✓
- list_compare ✓

**Missing from document (28):**
- unit_convert
- unit_info
- constant_lookup
- text_transform
- validate_toml
- json_compare
- json_extract
- json_shape
- regex_finditer
- regex_safety_check
- validate_schema_light
- text_hash
- text_position
- escape_text
- unescape_text
- path_analyze
- path_normalize
- identifier_analyze
- glob_match
- text_fingerprint
- identifier_inspect
- version_compare
- toml_shape
- list_dedupe
- list_sort
- json_canonicalize
- json_query

---

## TOOL_HANDLERS

Document claims at server.py:213-225:
```python
TOOL_HANDLERS: dict[str, Any] = {
    "math_eval": math_eval,
    "text_measure": text_measure,
    ...
}
```

| Item | Status | Notes |
|------|--------|-------|
| Defined in server.py | **MATCHES** | Lines 57-97 |
| 39 actual tools | **MISMATCH** | Document shows only 11 |

The TOOL_HANDLERS dict in server.py matches the actual 39 tools in TOOL_SCHEMAS, but the documentation lists only 11.

---

## server.py — MCP Protocol Handler

### Request Handling

| Claim | Status | Notes |
|-------|--------|-------|
| `initialize` handled | **MATCHES** | server.py:228-243, routed at line 257 |
| `tools/list` handled | **MATCHES** | server.py:190-225 |
| `tools/call` handled | **MATCHES** | server.py:125-187 |
| `notifications/initialized` returns None | **MATCHES** | server.py:259-260 |

### `_handle_initialize()` Notes

Document says (line 208):
> "Note: `_handle_initialize` is a separate function in `server.py` called directly from `handle_request`'s routing logic."

This is **ACCURATE** — the function is at lines 228-243 and called at server.py:257.

### Close Match Suggestions

| Claim | Status | Notes |
|-------|--------|-------|
| `_find_close_match()` exists | **MATCHES** | server.py:114-122 |
| Case-insensitive matching | **MATCHES** | server.py:116-121 |

### Error Codes

| Code | Name | Claim | Actual (server.py) | Status |
|------|------|-------|-------------------|--------|
| -32700 | ParseError | ✓ | Line 287 | **MATCHES** |
| -32600 | InvalidRequest | ✓ | Line 108 | **MATCHES** |
| -32601 | MethodNotFound | ✓ | Line 266 | **MATCHES** |
| -32602 | InvalidParams | ✓ | Line 145 | **MATCHES** |
| -32603 | InternalError | ✓ | Line 324 | **MATCHES** |
| -32000 | ToolError | ✓ | Line 160, 184 | **MATCHES** |

### Response Format

| Claim | Status | Notes |
|-------|--------|-------|
| Success format with `content` array | **MATCHES** | server.py:169-176 |
| Error format with `data` error envelope | **MATCHES** | server.py:159-163 |

---

## tools.py — Tool Implementations

### Input Limits

| Claim | Status | Actual | Notes |
|-------|--------|--------|-------|
| MAX_TEXT_LENGTH = 100,000 | **MATCHES** | tools.py:116 | |
| MAX_EXPRESSION_LENGTH = 10,000 | **MATCHES** | tools.py:117 | |
| MAX_LIST_ITEMS = 10,000 | **MATCHES** | tools.py:118 | |
| MAX_REGEX_SAMPLES = 100 | **MISMATCH** | **NOT DEFINED** | Actual limit is within each function via `_regex_test()` |

**ISSUE (LOW):** `MAX_REGEX_SAMPLES` is used in `validate_regex()` docstring but is not actually a module-level constant. The limit is enforced inside `_regex_test()` indirectly.

### Response Helpers

| Claim | Status | Notes |
|-------|--------|-------|
| `_error_response()` function | **MATCHES** | tools.py:222-236 |
| `_success_response()` function | **MATCHES** | tools.py:239-252 |

**Note:** Both functions add `tool`, `warnings`, and `limits_applied` fields that are not in the `ErrorEnvelope` TypedDict definition.

### Default Parameters

`text_equal` has additional parameters not documented:
- `ignore_newline_style: bool = False` (server.py:484)
- `ignore_trailing_whitespace: bool = False` (server.py:485)
- `ignore_final_newline: bool = False` (server.py:486)

### Detail Levels

Multiple functions support `detail: str` parameter with values `"summary"`, `"normal"`, `"full"` — this is consistent across tools but **not documented** in the architecture doc.

---

## Entry Point

| Claim | Status | Notes |
|-------|--------|-------|
| `main()` entry point | **MATCHES** | server.py:272-332 |
| `mcp_main` alias | **MATCHES** | server.py:340 |

---

## Discrepancies Found

1. **Document lists only 11 tools, actual implementation has 39** — The architecture doc is severely outdated
2. **ErrorEnvelope TypedDict missing fields** — `tool`, `warnings`, `limits_applied` used in tools.py but not defined in schemas.py ErrorEnvelope
3. **MAX_REGEX_SAMPLES not defined as constant** — Referenced in docstring but not a module constant
4. **Multiple tool parameters not documented** — e.g., `text_equal` has 8 parameters, doc shows only 5

---

## Bugs

### BUG-1: Duplicate `_VALID_TRANSFORM_OPERATIONS` Definition (MEDIUM)
- **Location:** tools.py:839-853 and tools.py:1337-1351
- **Severity:** MEDIUM
- **Description:** The same constant `_VALID_TRANSFORM_OPERATIONS` is defined twice in tools.py. The first definition is at line 839 and the second at line 1337. This works because Python evaluates the module-level constant once, but it's confusing and the second definition will overwrite the first.
- **Impact:** No runtime error, but the first definition is shadowed. If the definitions were different (they're currently identical), the second one would take precedence unexpectedly.

### BUG-2: ErrorEnvelope Missing Runtime Fields (LOW)
- **Location:** schemas.py:13-18, tools.py:222-252
- **Severity:** LOW
- **Description:** `_error_response()` and `_success_response()` add `tool`, `warnings`, and `limits_applied` fields that are not declared in the `ErrorEnvelope` TypedDict. This works because Python TypedDict is not enforced at runtime, but violates the documented schema.
- **Impact:** Type checkers would flag this as an error. MCP clients relying on schema validation may reject these responses.

---

## Improvements Suggested

### IMPROVEMENT-1: Update Architecture Document (HIGH PRIORITY)
The architecture doc is completely out of sync with the implementation. It:
- Shows 11 tools instead of 39
- Doesn't document any tools added in recent updates
- Missing documentation for tier/tag filtering in `tools/list`
- Missing JSON tools, path tools, identifier tools, list tools, etc.

### IMPROVEMENT-2: Add Missing Fields to ErrorEnvelope TypedDict (MEDIUM)
Either:
- Add `tool`, `warnings`, and `limits_applied` to the `ErrorEnvelope` TypedDict definition
- Or change `_error_response()` and `_success_response()` to not add these fields

### IMPROVEMENT-3: Fix Duplicate Constant Definition (LOW)
Remove the duplicate `_VALID_TRANSFORM_OPERATIONS` at line 1337-1351.

### IMPROVEMENT-4: Define MAX_REGEX_SAMPLES as Actual Constant (LOW)
Currently `MAX_REGEX_SAMPLES = 100` appears only in docstrings. Define it as a module-level constant for consistency with other limits.

### IMPROVEMENT-5: Document Detail Level Parameter (LOW)
Many tools support a `detail` parameter with values `"summary"`, `"normal"`, `"full"`. This is worth documenting in the architecture doc as it's a common pattern.

### IMPROVEMENT-6: Document Tier/Tag Filtering (LOW)
The `tools/list` handler supports `tier`, `tags`, and `names` filter parameters (server.py:194-196) which are not documented in the architecture doc.

---

## Priority Summary

| Priority | Item | Issue |
|----------|------|-------|
| HIGH | Update architecture doc to reflect 39 tools | Document is stale |
| MEDIUM | Add missing fields to ErrorEnvelope TypedDict | Schema mismatch |
| MEDIUM | Remove duplicate `_VALID_TRANSFORM_OPERATIONS` definition | Code clarity |
| LOW | Define MAX_REGEX_SAMPLES as actual constant | Documentation accuracy |
| LOW | Document detail parameter common pattern | Missing documentation |
| LOW | Document tier/tag filtering in tools/list | Missing documentation |

---

## Verified Claims Summary

**MATCHES (verified correct):**
- ErrorEnvelope fields (4 basic fields only)
- Protocol handler routing logic
- Error codes all match
- Response formats
- main() and mcp_main alias
- _handle_initialize inline call
- _find_close_match function
- Input limit constants (MAX_TEXT_LENGTH, MAX_EXPRESSION_LENGTH, MAX_LIST_ITEMS)

**MISMATCHES:**
- Tool count: doc says 11, actual is 39
- Tool list: doc is stale, missing 28 tools
- ErrorEnvelope extended fields missing from TypedDict
- MAX_REGEX_SAMPLES not defined as actual constant (only in docstring)

**NOT VERIFIABLE (items not in current codebase):**
- None — all documented structures exist and were verified
