# validate.py Architecture Review

## Summary

The `nl_calc/exact/validate.py` module provides three validation primitives for text validation:
- `check_brackets()` - validates delimiter/bracket matching
- `validate_json()` - validates JSON syntax with detailed error reporting
- `regex_test()` - tests regex patterns against sample strings

These are low-level, deterministic utilities used by the MCP tools layer and normalization pipeline.

---

## Verified Claims (Doc ↔ Code Matches)

### 1. `check_brackets()`

| Claim (document) | Implementation | Status |
|------------------|----------------|--------|
| Default bracket pairs `()`, `[]`, `{}`, `<>` | `DEFAULT_BRACKET_PAIRS` at line 57-62 | ✅ MATCH |
| Returns `balanced`, `unmatched_openers`, `unmatched_closers` | `CheckBracketsResult` TypedDict lines 22-26 | ✅ MATCH |
| Function signature `check_brackets(text: str, pairs: dict | None = None)` | Line 86-89 | ✅ MATCH |
| Tracks positions (line/column) for errors | `_get_line_column()` lines 65-83 used in BracketError | ✅ MATCH |
| Handles mismatch by marking both opener and closer as unmatched | Lines 119-132 | ✅ MATCH |

### 2. `validate_json()`

| Claim (document) | Implementation | Status |
|------------------|----------------|--------|
| Returns `valid`, `error`, `error_position`, `error_line`, `error_column`, `structure` | `ValidateJsonResult` TypedDict lines 29-37 with `line`, `column`, `position`, `type` | ⚠️ PARTIAL - Field names differ (`error_line` vs `line`, `error_column` vs `column`, `structure` vs `type`) |
| Correctly identifies `object`, `array` types | Lines 172-176 | ✅ MATCH |
| Returns `top_level_keys` for objects | Line 174 | ✅ MATCH (undocumented in doc) |

### 3. `regex_test()`

| Claim (document) | Implementation | Status |
|------------------|----------------|--------|
| Returns `valid_pattern`, `error`, `results` | `RegexTestResult` lines 50-53 - **NO `error` field** | ❌ BUG |
| `RegexSampleResult` has `sample`, `matches`, `fullmatch`, `spans`, `groups`, `groupdict` | `RegexMatch` TypedDict lines 40-47 has `span` (singular), not `spans` | ❌ BUG |
| Supports flags `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`, `UNICODE`, `DEBUG` | Lines 223-230 | ⚠️ BUG - Documented `ASCII` but implementation has `UNICODE` and `DEBUG` instead |

---

## Issues Found

### Issue 1: `RegexTestResult` missing `error` field (CRITICAL)

**Document says:**
```python
class RegexTestResult(NamedTuple):
    valid_pattern: bool
    error: str | None        # <-- Documented
    results: list[RegexSampleResult]
```

**Actual code (lines 50-53):**
```python
class RegexTestResult(TypedDict):
    valid_pattern: bool
    results: list[RegexMatch]      # <-- NO error field!
```

**Impact:** When an invalid regex pattern is provided, `regex_test()` returns an empty results list with no error message. Callers cannot distinguish *why* the pattern was invalid.

**Fix:** Add `error: str | None` to `RegexTestResult` and return it when `re.error` is caught at line 237.

### Issue 2: `spans` vs `span` singular mismatch

**Document says:** `spans: list[tuple[int, int]]`

**Actual code (line 45):** `span: list[int] | None`

**Impact:** The field name and type both differ - document implies multiple spans per match, but code stores a single span (start, end as a flat list). While the document example shows a single span tuple in a list `[(0, 3)]`, the inconsistency is the bug.

**Fix:** Either update code to support multiple spans, or update doc to say `span: list[int] | None` and note it's `[start, end]` format.

### Issue 3: Flag list mismatch - `ASCII` documented but `UNICODE`/`DEBUG` implemented

**Document says (line 103):** `ASCII`, `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`

**Implementation (lines 224-230):**
```python
"IGNORECASE": re.IGNORECASE,
"MULTILINE": re.MULTILINE,
"DOTALL": re.DOTALL,
"UNICODE": re.UNICODE,    # <-- Not in docs
"DEBUG": re.DEBUG,        # <-- Not in docs
"VERBOSE": re.VERBOSE,
```

Also `ASCII` is missing. Unknown if intentional.

### Issue 4: `ValidateJsonResult` field name inconsistencies

**Document says:** `error_position`, `error_line`, `error_column`, `structure`

**Implementation has:** `position`, `line`, `column`, `type`

While semantically equivalent, this is a documentation bug - the doc and code don't agree on field names.

### Issue 5: `RegexTestResult.error` not returned on pattern error

At lines 237-241:
```python
except re.error:
    return RegexTestResult(
        valid_pattern=False,
        results=[],
    )
```

The `re.error` exception message is lost. Should capture and return it.

---

## Improvement Recommendations

### REC-1: Add `error` field to `RegexTestResult` (line 50-53)

```python
# Current
class RegexTestResult(TypedDict):
    valid_pattern: bool
    results: list[RegexMatch]

# Should be
class RegexTestResult(TypedDict):
    valid_pattern: bool
    error: str | None
    results: list[RegexMatch]
```

Then update line 237-241:
```python
except re.error as e:
    return RegexTestResult(
        valid_pattern=False,
        error=str(e),
        results=[],
    )
```

### REC-2: Fix `regex_test()` return signature for invalid patterns (line 271-274)

Currently returns `valid_pattern=True` always when no exception. Need to propagate the error state:
```python
return RegexTestResult(
    valid_pattern=True,  # <-- This should be conditional
    results=results,
)
```

Should track whether compilation succeeded and use that value.

### REC-3: Unify `ValidateJsonResult` field names with documentation

Either update doc to match code (preferred - code is cleaner), or rename fields in code:
- `line` ↔ `error_line`
- `column` ↔ `error_column`
- `position` ↔ `error_position`
- `type` ↔ `structure`

### REC-4: Document discrepancy in regex flag list

Either add `ASCII` support to match docs, or update docs to list `UNICODE` and `DEBUG`.

### REC-5: Consider renaming `RegexMatch.span` to `RegexMatch.spans` for consistency with documentation

If multiple spans are a future possibility, make it plural now. If not, update docs to reflect singular.

---

## Summary Table

| Component | Status | Notes |
|-----------|--------|-------|
| `check_brackets()` signature | ✅ OK | Matches doc |
| `check_brackets()` behavior | ✅ OK | Correct |
| `validate_json()` signature | ⚠️ FIELDS | Names differ (`line` vs `error_line`) |
| `validate_json()` behavior | ✅ OK | Correct |
| `regex_test()` signature | ❌ BROKEN | Missing `error` field, `spans` vs `span` |
| `regex_test()` behavior | ⚠️ BUGGY | Error info lost on invalid pattern |
| Flag support | ⚠️ MISMATCH | `UNICODE`/`DEBUG` present, `ASCII` absent |

---

## Files Referenced

| File | Lines | Content |
|------|-------|---------|
| `nl_calc/exact/validate.py` | 14-53 | TypedDict definitions |
| `nl_calc/exact/validate.py` | 57-62 | `DEFAULT_BRACKET_PAIRS` |
| `nl_calc/exact/validate.py` | 65-83 | `_get_line_column()` |
| `nl_calc/exact/validate.py` | 86-155 | `check_brackets()` |
| `nl_calc/exact/validate.py` | 158-201 | `validate_json()` |
| `nl_calc/exact/validate.py` | 204-274 | `regex_test()` |
| `architecture/validate.md` | 62-101 | regex_test documentation |
| `tests/test_exact.py` | 376-462 | Tests for validate primitives |