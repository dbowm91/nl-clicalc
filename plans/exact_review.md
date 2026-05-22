# exact/ Module Review - Improvement Plan

## Verified Claims

| Claim | Status |
|-------|--------|
| `utf8_bytes()` returns `bytes` | ✅ Verified |
| `visible_repr()` variation selector check before combining marks | ✅ Verified (primitives.py:273-276) |
| `_get_script_heuristic()` has `@functools.lru_cache` | ✅ Verified (unicode_tools.py:66) |
| Cf (format) characters excluded from control_chars | ✅ Verified (measure.py:245-246) |
| `confusables_count()` helper exists | ✅ Verified (unicode_tools.py:218-232) |
| Word Joiner (U+2060) handled | ✅ Verified (primitives.py:65 in `_INVISIBLE_CHARS`) |
| TypedDict used for all type definitions | ✅ Verified |
| `count_graphemes()` implements UAX #29 | ✅ Verified |

---

## Discrepancies

### 1. Missing Exports in `__init__.py`
**Priority: High**

`unicode_scripts` and `confusables_count` are defined in `unicode_tools.py` and used internally but **not re-exported** from the package.

```python
# Documented in exact.md (lines 31-32):
unicode_scripts, unicode_scripts, detect_mixed_scripts,
detect_confusables, confusables_count,

# Actual __init__.py (lines 43-50):
from .unicode_tools import (
    ConfusableInfo,
    ScriptInfo,
    detect_confusables,
    detect_mixed_scripts,
    unicode_script,  # Missing: unicode_scripts, confusables_count
)
```

### 2. `diff_spans` Return Type Mismatch
**Priority: Medium**

Architecture doc (line 205) shows `DiffSpan` fields:
```
a_start=int, a_end=int, a_text=str, b_start=int, b_end=int, b_text=str, diff_type=str
```

Actual implementation (diff.py:31-37):
```python
class DiffSpan(TypedDict):
    kind: str
    a_span: list[int]
    b_span: list[int]
    a_text: str
    b_text: str
```

Fields are `a_span`/`b_span` (list[int]), not `a_start`/`a_end`/`b_start`/`b_end`.

### 3. `RegexTestResult` Field Name Mismatch
**Priority: Low**

Architecture doc (line 253) shows `valid: bool`.
Actual implementation (validate.py:63) has `valid_pattern: bool`.

---

## Bugs Found

### 1. `__slots__` on TypedDict Classes
**Priority: High**

`measure.py` lines 26, 38, 52 have invalid `__slots__` declarations:
```python
LineMetrics.__slots__ = ['lines', 'nonempty_lines', 'blank_lines', ...]
```

`TypedDict` classes do NOT support `__slots__`. This would cause `AttributeError` at runtime if accessed.

### 2. `_is_extended_pictographic()` Invalid Unicode Range
**Priority: Medium**

primitives.py:382 has:
```python
if 0x1F300 <= cp <= 0x1FFFF:
```

Maximum valid Unicode codepoint is `0x10FFFF`, not `0x1FFFF`. This check will never match codepoints in the range `0x10000-0x1FFFF` (which actually includes many emoji).

### 3. Unused Import
**Priority: Low**

`validate.py` line 11 imports `signal` but never uses it.

### 4. Unused Import
**Priority: Low**

`synthesis.py` imports `normalize_unicode as _normalize_unicode` (line 44) but never uses it.

---

## Improvements

### High Priority

1. **Fix `__init__.py` exports** - Add `unicode_scripts` and `confusables_count` to re-exports from `unicode_tools`.

2. **Remove invalid `__slots__`** - Remove `__slots__` declarations from all TypedDict classes in `measure.py`:
   - `LineMetrics.__slots__` (line 26)
   - `WordMetrics.__slots__` (line 38)
   - `CharCategoryMetrics.__slots__` (line 52)

3. **Fix `_is_extended_pictographic()` range** - Change upper bound from `0x1FFFF` to `0x10FFFF`:
   ```python
   if 0x1F300 <= cp <= 0x10FFFF:  # Not 0x1FFFF
   ```

### Medium Priority

4. **Update architecture doc `DiffSpan` fields** - Match actual implementation with `a_span`/`b_span` (list[int]) instead of individual start/end fields.

5. **Add `longest_common_subsequence` to `__init__.py` exports** - Function is defined in `diff.py` but not exported in package `__init__.py`.

6. **Fix `RegexTestResult` doc** - Either rename `valid_pattern` to `valid` in code, or note the discrepancy in docs.

### Low Priority

7. **Remove unused `signal` import** from `validate.py`

8. **Remove unused `normalize_unicode` import** from `synthesis.py`

9. **Add proper return type to `list_compare`** - Currently returns `dict`, could use a TypedDict for consistency.

---

## Summary

| Category | Count |
|----------|-------|
| Verified Claims | 8 |
| Discrepancies | 3 |
| Bugs | 4 |
| Improvements | 9 |