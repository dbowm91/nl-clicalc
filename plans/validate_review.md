# validate.py Module Review - Improvement Plan

## Verified Claims

| Claim | Status |
|-------|--------|
| Core function names (`check_brackets`, `validate_json`, `regex_test`) | Verified |
| Default bracket pairs `{"(": ")", "[": "]","{": "}", "<": ">"}` | Verified |
| BracketError contains `char`, `index`, `line`, `column` | Verified |
| ReDoS prevention via `_check_pattern_complexity()` | Verified |
| Pattern length limit (1000) and nesting limit (5) | Verified |
| Error handling for invalid regex patterns | Verified |
| `validate_json` returns line, column, position for errors | Verified |

## Discrepancies

### 1. `check_brackets` Return Type Mismatch

**Architecture Doc (lines 14-19):**
```python
@dataclass
class CheckBracketsResult(NamedTuple):
    balanced: bool
    unmatched_openers: list[BracketError]  # Unmatched opening brackets
    unmatched_closers: list[BracketError]  # Unmatched closing brackets
```

**Actual Implementation (lines 30-35):**
```python
class CheckBracketsResult(TypedDict):
    balanced: bool
    unmatched_openers: list[BracketError]
    unmatched_closers: list[BracketError]
```

**Issue:** Architecture doc shows NamedTuple but implementation uses TypedDict. The example output in the doc (lines 29-35) shows fields (`error`, `position`, `expected`, `unexpected`) that don't exist in the actual implementation.

### 2. Docstring Examples Show Wrong Output Format

**Architecture Doc (lines 29-35):**
```python
>>> check_brackets("({[]})")
CheckBracketsResult(balanced=True, error=None, position=None,
                    expected=None, unexpected=None)
>>> check_brackets("({]})")
CheckBracketsResult(balanced=False, error='Mismatched bracket',
                    position=2, expected='}', unexpected=']')
```

**Actual Result:**
```python
>>> check_brackets("({[]})")
{'balanced': True, 'unmatched_openers': [], 'unmatched_closers': []}
>>> check_brackets("({]})")
{'balanced': False, 'unmatched_openers': [...], 'unmatched_closers': [...]}
```

**Issue:** Docstring shows NamedTuple-style output but function returns TypedDict. Example shows `error`, `position`, `expected`, `unexpected` fields that don't exist.

### 3. `RegexSampleResult` vs `RegexMatch`

**Architecture Doc (lines 76-84):** References `RegexSampleResult`

**Actual Implementation (lines 51-58):** Uses `RegexMatch`

**Issue:** Architecture doc uses wrong class name.

### 4. Missing `top_level_keys` in Architecture Doc

**Architecture Doc:** `ValidateJsonResult` fields don't mention `top_level_keys`

**Actual Implementation (lines 40-48):**
```python
class ValidateJsonResult(TypedDict):
    valid: bool
    error: str | None
    line: int | None
    column: int | None
    position: int | None
    type: str | None
    top_level_keys: list[str] | None  # NOT DOCUMENTED
```

**Issue:** Implementation returns `top_level_keys` for valid JSON objects, but architecture doc doesn't mention it.

### 5. `validate_json` Return Type Annotation Mismatch

**Architecture Doc (lines 41-50):** Shows `@dataclass class ValidateJsonResult(NamedTuple)`

**Actual Implementation (lines 40-48):** Uses `TypedDict`

### 6. `RegexTestResult` Example Output Incomplete

**Architecture Doc (lines 88-100):** Example shows `RegexTestResult(valid_pattern=True, error=None, results=[...])`

**Actual Implementation:** Returns `RegexTestResult(valid_pattern=True, results=[...])` without error field when valid.

**Issue:** Both match when valid, but the doc structure doesn't reflect that `error` is only present when invalid.

## Bugs Found

1. **No bugs in logic** - The implementation is internally consistent and functions correctly.

2. **Documentation bug only** - Architecture doc is out of sync with implementation.

## Improvements with Priority

### High Priority

1. **Update architecture doc to match implementation**
   - Change `CheckBracketsResult` from `@dataclass class ... (NamedTuple)` to `TypedDict`
   - Fix `check_brackets` examples to show actual output format
   - Add `top_level_keys` to `ValidateJsonResult` documentation
   - Fix `RegexSampleResult` → `RegexMatch`

2. **Align TypedDict class names between doc and implementation**
   - Document uses `RegexSampleResult` but code uses `RegexMatch`

### Medium Priority

3. **Add `top_level_keys` to JSON validation documentation**
   - Document when `top_level_keys` is populated (when JSON is an object)

4. **Document `validate_json` `type` field behavior more clearly**
   - Currently shows `type: str | None` but it always has a value when valid

### Low Priority

5. **Add timeout protection for regex matching**
   - ReDoS prevention exists for pattern compilation, but no timeout for actual matching

6. **Consider adding `check_brackets` example showing mismatch behavior**
   - Current doc shows balanced case, missing example of mismatched brackets

## Summary

The implementation is **correct and functional**. All discrepancies are **documentation issues** - the architecture doc predates or wasn't updated to match the actual TypedDict-based implementation. The code uses TypedDict consistently, not NamedTuple as the architecture doc suggests.