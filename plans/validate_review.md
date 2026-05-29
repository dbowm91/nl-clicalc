# validate.py Architecture Review

## Overview

Reviewed `architecture/validate.md` against `nl_calc/exact/validate.py` (2601 lines).

---

## Verified Claims

### `check_brackets()`
- **MATCHES**: Function signature `check_brackets(s: str, pairs: dict[str, str] | None = None) -> CheckBracketsResult`
- **MATCHES**: Default bracket pairs `{"(": ")", "[": "]", "{": "}", "<": ">"}`
- **MATCHES**: TypedDict structure `BracketError` and `CheckBracketsResult`
- **MATCHES**: Returns balanced bool, unmatched_openers list, unmatched_closers list
- **MATCHES**: Raises `ValueError` when input exceeds `MAX_INPUT_LENGTH`

### `validate_json()`
- **MATCHES**: Function signature `validate_json(s: str) -> ValidateJsonResult`
- **MATCHES**: TypedDict structure with `valid`, `error`, `line`, `column`, `position`, `type`, `top_level_keys`
- **MATCHES**: Returns `top_level_keys=None` for arrays and primitives
- **MATCHES**: Raises `ValueError` when input exceeds `MAX_INPUT_LENGTH`

### `regex_test()`
- **MATCHES**: Function signature and return type structure
- **MATCHES**: `RegexMatch` TypedDict with `sample`, `matches`, `fullmatch`, `span`, `groups`, `groupdict`
- **MATCHES**: Supported flags include `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`
- **MATCHES**: `MAX_PATTERN_LENGTH = 1000` and `MAX_PATTERN_NESTING = 5` limits
- **MATCHES**: `MAX_SAMPLE_LENGTH = 10_000` limit

---

## Discrepancies Found

### 1. Document is severely incomplete (Major)
**Status**: MISMATCH

The document only describes 3 functions, but the actual code contains **25+ functions**:

| Function | Documented |
|----------|-----------|
| `check_brackets` | Yes |
| `validate_json` | Yes |
| `regex_test` | Yes |
| `validate_toml_text` | No |
| `toml_shape` | No |
| `version_compare` | No |
| `list_dedupe` | No |
| `list_sort` | No |
| `regex_replace_preview` | No |
| `json_compare` | No |
| `json_extract` | No |
| `json_shape` | No |
| `regex_finditer` | No |
| `regex_safety_check` | No |
| `validate_schema_light` | No |
| `json_canonicalize` | No |
| `json_query` | No |

Additionally, **14 TypedDicts** and **6 constants** are not documented.

### 2. `RegexTestResult.flags_used` missing from document
**Status**: MISMATCH

Document shows:
```python
class RegexTestResult(TypedDict):
    valid_pattern: bool
    results: list[RegexMatch]
    error: str | None
```

Actual code has:
```python
class RegexTestResult(TypedDict):
    valid_pattern: bool
    results: list[RegexMatch]
    error: str | None
    flags_used: RegexFlags  # NOT DOCUMENTED
```

### 3. Supported flags discrepancy
**Status**: PARTIAL MATCH

Document claims: `IGNORECASE`, `MULTILINE`, `DOTALL`, `UNICODE`, `DEBUG`, `VERBOSE`

Code's flag_map (line 723-730) includes `UNICODE` and `DEBUG`, but `DEBUG` flag is never actually used to enable regex debug mode (it's ignored when passed).

---

## Bugs Identified

### BUG 1: Wrong exception type in `toml_shape()` (Medium Severity)
**Location**: `validate.py:413`

```python
except json.JSONDecodeError as e:  # WRONG - should be tomllib exception
    return TomlShapeResult(
        valid=False,
        ...
        summary=f"Invalid TOML: {e.msg}",
    )
```

`toml_shape()` parses TOML with `tomllib.loads()`, but catches `json.JSONDecodeError`. Since `tomllib` uses different exception types (not JSONDecodeError), this exception handler will never catch TOML parse errors.

**Fix**: Catch general `Exception` or use `tomllib.TOMLDecodeError` (Python 3.11+).

---

## Missing Constants Not Documented

| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_SAMPLE_LENGTH` | 10,000 | Max sample string length for regex_test |
| `MAX_TEXT_LENGTH_REGEX` | 100,000 | Max text length for regex_finditer |
| `MAX_PATTERN_LENGTH_REGEX` | 1,000 | Max pattern length for regex_finditer |
| `MAX_MATCHES` | 100 | Default max matches for regex_finditer |
| `MAX_GROUPS` | 100 | Max groups captured in regex_finditer |
| `MAX_SCHEMA_VIOLATIONS` | 100 | Max violations in validate_schema_light |

---

## Improvements Suggested

### Priority 1 (High) - Documentation Update
The architecture document is incomplete. It should document:
1. All public functions with their signatures
2. All TypedDicts with field descriptions
3. All constants with their purposes
4. Error handling behavior for each function

### Priority 2 (Medium) - Bug Fix
Fix `toml_shape()` exception handling (line 413) to catch the correct exception type for TOML parsing.

### Priority 3 (Low) - Code Cleanup
The `DEBUG` flag in `regex_test`'s flag_map is listed but never applied. Either remove it or implement debug mode properly.

---

## Priority Summary

| Priority | Item | Severity |
|----------|------|----------|
| 1 | Update architecture document to match code | High |
| 1 | Fix `toml_shape()` wrong exception type | Medium |
| 2 | Remove or implement `DEBUG` flag handling | Low |

---

## Additional Notes

The code is generally well-structured with comprehensive TypedDict definitions. The architecture document appears to be an early draft that was never fully updated as the module grew beyond its initial scope. All functions have proper type annotations and docstrings that could serve as the basis for documentation updates.
