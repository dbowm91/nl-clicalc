# MCP Module Architecture Review

## Verified Claims

### Module Structure
- `__init__.py` exports `main`, `handle_request`, `TOOL_SCHEMAS`, `tools` — **Correct**
- `schemas.py` defines `ErrorEnvelope`, `SuccessEnvelope`, `TOOL_SCHEMAS` — **Correct**

### TOOL_SCHEMAS
- All 11 tools present: `math_eval`, `text_measure`, `text_equal`, `text_diff_explain`, `text_inspect`, `text_count`, `text_truncate`, `validate_brackets`, `validate_json`, `validate_regex`, `list_compare` — **Correct**

### Input Limits
- `MAX_TEXT_LENGTH = 100_000` — **Correct**
- `MAX_EXPRESSION_LENGTH = 10_000` — **Correct**
- `MAX_LIST_ITEMS = 10_000` — **Correct**
- `MAX_REGEX_SAMPLES = 100` — **Correct**

### Error Handling
- `_error_response()` creates standardized error envelope — **Correct**
- `_success_response()` creates standardized success envelope — **Correct**
- `_sanitize_error()` removes non-ASCII — **Correct**

### Server Implementation
- `handle_request()` routes `tools/list` and `tools/call` — **Correct**
- `TOOL_HANDLERS` maps all 11 tools — **Correct**
- `_find_close_match()` provides case-insensitive suggestions — **Correct**
- Error codes: `-32600`, `-32602`, `-32603`, `-32000` — **Correct**

### Tool Wrappers
- All 11 tools wrap correct `exact/` functions — **Correct**

---

## Discrepancies

### 1. `SuccessEnvelope` Defined but Never Used
**severity: Medium**

`schemas.py:21-24` defines `SuccessEnvelope(TypedDict)` with fields `ok: bool` and `result: dict`, but `tools.py:67-69` returns plain dict `{"ok": True, "result": result}` instead of using the typed envelope. The architecture doc claims all tools use Success/Error envelopes, but the actual code does not use the TypedDict.

### 2. `text_truncate` Returns Extra Field
**severity: Low**

`tools.py:377-417` returns `truncated_graphemes` in the result dict, but `schemas.py:152-166` does not document this field in the output schema. Minor inconsistency.

### 3. `text_count` Schema Documents Output Inconsistently
**severity: Low**

`schemas.py:132-151` schema says `target` must be a single character, but the actual implementation (`tools.py:238-243`) correctly validates this. No discrepancy here — just verifying.

---

## Bugs Found

### 1. `_sanitize_error()` Uses `replace` Mode — Loses Information
**severity: Low**

`tools.py:52-54` uses `message.encode("ascii", "replace").decode("ascii")`. Non-ASCII characters are replaced with `?`, making error messages harder to debug. The architecture doc at line 149 claims it "removes" non-ASCII, but it actually replaces them.

**Recommendation**: Use `errors="ignore"` to truly remove, or document the replacement behavior.

### 2. `text_truncate` Missing `text` in Schema Output
**severity: Low**

`schemas.py:152-166` does not document that `text_truncate` returns a `text` field containing the truncated string. The schema only shows `max_graphemes` as input.

**Fix**: Add output schema documenting `text`, `original_graphemes`, `truncated_graphemes`, `truncated` fields.

---

## Improvements with Priority

### High Priority

1. **Use `SuccessEnvelope` TypedDict in `tools.py`**
   - Currently `_success_response()` returns a plain dict
   - Should construct and return `SuccessEnvelope(...)` to match architecture and type safety
   - Only `ErrorEnvelope` is used via `_error_response()`

2. **Update `text_truncate` Schema Output**
   - Schema at `schemas.py:152-166` missing output fields
   - Should document: `text`, `original_graphemes`, `truncated_graphemes`, `truncated`

### Medium Priority

3. **Clarify `_sanitize_error()` Behavior in Docstring**
   - Currently says "Remove non-ASCII" but actually replaces with `?`
   - Either change to `errors="ignore"` or update docstring to say "replaces"

4. **Consider Adding `text_truncate` to `__init__.py` Exports**
   - `text_truncate` is in `TOOL_HANDLERS` but not explicitly exported from package
   - `__init__.py:13` exports `tools` module, so `tools.text_truncate` is accessible
   - Could add explicit export for parity

### Low Priority

5. **Add `text_measure` `include_codepoints` Output Schema**
   - Schema at line 55 says "not yet implemented" for codepoint details
   - If/when implemented, update schema and remove note

6. **Consider Adding Unit Tests for MCP Tools**
   - No tests in `tests/` directory for MCP module
   - Would help verify tool behavior against schema

---

## Summary

The architecture document accurately describes the MCP module structure. All 11 tools are implemented, wired to correct handlers, and follow consistent error/success envelope patterns. The main issue is that `SuccessEnvelope` TypedDict is defined but not used — `_success_response()` returns a plain dict instead. Secondary issues are minor schema/documentation gaps for `text_truncate` output fields.