# Architecture Review: exact/ Module

## Document Reviewed
- `architecture/exact.md`
- Implementation in `nl_calc/exact/`

## Summary

The architecture document describes a Unicode text inspection toolkit, but **there is a significant mismatch between the documented purpose and the actual implementation**. The document describes low-level text primitives focused on "deterministic, independently testable" operations without semantic interpretation, yet several key claims about functionality (exact arithmetic, fractions) are **completely absent** from the codebase.

---

## 1. Document Claims vs. Implementation Verification

### 1.1 Module Structure - MATCHES

| Document | Implementation |
|----------|---------------|
| `primitives.py` | EXISTS |
| `unicode_tools.py` | EXISTS |
| `confusables.py` | EXISTS |
| `validate.py` | EXISTS |
| `diff.py` | EXISTS |
| `measure.py` | EXISTS |
| `synthesis.py` | EXISTS |

All documented modules are present and correctly structured.

### 1.2 Core Primitives - PARTIAL MATCH

| Document Claim | Implementation | Status |
|---------------|----------------|--------|
| `utf8_bytes(text: str) -> int` | Returns `bytes` not `int` (line 75-84) | **BUG**: Doc says `int`, code returns `bytes` |
| `codepoints(text: str) -> list[CodepointInfo]` | MATCHES | OK |
| `normalize_unicode(text: str, form: str)` | MATCHES | OK |
| `casefold_text(text: str) -> str` | MATCHES | OK |
| `raw_equal(a: str, b: str) -> bool` | MATCHES | OK |
| `normalized_equal(a: str, b: str) -> bool` | MATCHES | OK |
| `measure_basic(text: str) -> MeasureBasic` | `graphemes_estimate` always `None` | **ISSUE**: Documented as estimate, always null |
| `find_invisibles(text: str) -> list[InvisibleCharInfo]` | MATCHES | OK |
| `visible_repr(text: str) -> str` | MATCHES | OK |

### 1.3 Documented Functions NOT in Implementation

The architecture document does **NOT** list these functions, but they exist in the implementation:
- `check_brackets()` - bracket validation
- `validate_json()` - JSON validation  
- `regex_test()` - regex testing
- `line_metrics()` - line-level metrics
- `word_metrics()` - word-level metrics
- `char_category_metrics()` - character categorization
- `measure_text()` - comprehensive text metrics
- `text_equal()` - multi-mode string comparison
- `explain_diff()` - detailed diff explanation
- `inspect_text()` - text inspection
- `count_chars()` - character counting
- `list_compare()` - list comparison

### 1.4 MAJOR DISCREPANCY: Exact Arithmetic / Fractions

**The architecture document contains no mention of exact arithmetic or fraction handling.** The document's purpose states:

> "Low-level Unicode text primitives for detecting hidden characters, confusables, and text metrics."

There is **NO** implementation of:
- Exact rational arithmetic
- Fraction representation
- Any mathematical precision handling

This appears to be a **copy-paste error** from another architecture document that was meant to cover a math-related module.

---

## 2. Identified Bugs

### Bug 1: `utf8_bytes` Return Type Mismatch
**File**: `primitives.py` lines 75-84
```python
def utf8_bytes(s: str) -> bytes:
    """Return raw UTF-8 bytes of the string.
    ...
    Returns:
        UTF-8 encoded bytes.
    """
    return s.encode("utf-8")
```

**Issue**: The architecture document says it returns `int` (number of bytes), but the implementation returns `bytes` object. The docstring says "number of UTF-8 bytes" but the actual return is the encoded bytes.

**Fix**: Either:
- Change implementation to return `int` (count): `return len(s.encode("utf-8"))`
- Or update doc to say returns `bytes`

### Bug 2: `graphemes_estimate` Always None
**File**: `measure_basic()` lines 165-188
```python
class MeasureBasic(TypedDict):
    """Basic text measurements."""
    bytes_utf8: int
    codepoints: int
    graphemes_estimate: None  # Always None!
    chars_no_whitespace: int
    ascii: int
    non_ascii: int
```

**Issue**: `graphemes_estimate` is typed as `None` and always set to `None`. No grapheme cluster estimation is ever performed.

**Recommendation**: Either implement proper grapheme counting or remove this field entirely.

### Bug 3: `measure_basic` Result Type Issue
**File**: `primitives.py` line 181
```python
return MeasureBasic(
    bytes_utf8=bytes_utf8,
    codepoints=codepoints_count,
    graphemes_estimate=None,  # Always None
    ...
)
```

The return type annotation says `graphemes_estimate: None` (meaning it can only ever be `None`), but this appears intentional. However, the architecture document doesn't mention this limitation.

---

## 3. Architecture Discrepancies

### 3.1 `utf8_bytes` Function

**Document says**:
```
### `utf8_bytes(text: str) -> int`

Returns number of UTF-8 bytes in text.
```

**Actual behavior**: Returns `bytes` object (the encoded string itself, not a count).

### 3.2 Missing Docstring for `_get_script_heuristic`

**File**: `unicode_tools.py` lines 61-95

The internal function `_get_script_heuristic()` has no docstring, but it's a key component of the script detection system.

### 3.3 Missing Error Handling for `unicode_script`

**File**: `unicode_tools.py` line 98-114

The `unicode_script()` function validates single character input but raises `ValueError` with a generic message. The architecture doc doesn't specify error behavior.

---

## 4. Code Quality Issues

### 4.1 Inconsistent Import Style

**File**: `synthesis.py` lines 13-56

Imports are split awkwardly:
```python
from .diff import (
    common_prefix_suffix as _common_prefix_suffix,
)
from .diff import (
    diff_spans as _diff_spans,
)
from .diff import (
    first_diff as _first_diff,
)
```

Could be consolidated into a single import block.

### 4.2 `re` Module Import in `word_metrics`

**File**: `measure.py` line 170
```python
def word_metrics(s: str) -> WordMetrics:
    ...
    import re  # Imported inside function
    sentence_pattern = r"[.!?]+(?:\s|$)"
```

The `re` module is imported inside the function rather than at module level. This is a performance concern if `word_metrics` is called frequently.

### 4.3 Type Annotation Inconsistencies

**File**: `primitives.py` line 16-22
```python
class CodepointInfo(NamedTuple):
    """Information about a single codepoint."""
    index: int
    char: str
    codepoint: str  # Document says "U+XXXX" format, but it's a str not int
    name: str
    category: str
```

The `codepoint` field is documented in "U+XXXX" format but typed as generic `str`.

---

## 5. Missing Documentation

### 5.1 No Mention of MAX Limits in Architecture

The architecture document doesn't mention these runtime limits present in the code:
- `MAX_LEVENSHTEIN_LEN = 10000` in `diff.py`
- `MAX_TEXT_LENGTH = 100_000` in `synthesis.py`
- `MAX_DIFF_SPANS = 50` in `synthesis.py`

### 5.2 Confusables Table Auto-Generation

**File**: `confusables.py` lines 1-6
```python
"""
Unicode confusables table.

Auto-generated from confusables.txt (Unicode UTS #39).
DO NOT EDIT - regenerate with scripts/generate_confusables.py
"""
```

This is good documentation but not mentioned in the architecture document.

---

## 6. Security Considerations (Not in Architecture)

The implementation includes security-focused features not documented:
- Detection of bidirectional control characters (potential homograph attacks)
- Detection of confusables (homoglyph spoofing)
- Invisible character detection (stealth text)

**Recommendation**: Add security considerations section to architecture document.

---

## 7. Improvement Recommendations

### High Priority

1. **Fix `utf8_bytes` return type mismatch** - Decide whether it returns `int` or `bytes` and fix accordingly
2. **Update architecture document** - Remove any references to exact arithmetic/fractions that don't exist
3. **Document runtime limits** - Add MAX_* constants to architecture doc

### Medium Priority

4. **Move `import re` to module level** in `measure.py`
5. **Add docstring to `_get_script_heuristic`** internal function
6. **Implement grapheme cluster estimation** or remove `graphemes_estimate` field

### Low Priority

7. **Consolidate import statements** in `synthesis.py`
8. **Add security considerations section** to architecture document
9. **Document the `confusables.py` auto-generation** process

---

## 8. Test Coverage Assessment

The test file `tests/test_exact.py` provides **good coverage** of the actual implementation:

| Module | Test Coverage |
|--------|--------------|
| primitives.py | Good (UTF-8, codepoints, normalization, casefold, equality, measure, invisibles, visible_repr) |
| unicode_tools.py | Good (script detection, mixed scripts, confusables) |
| diff.py | Good (first_diff, common_prefix_suffix, levenshtein, diff_spans) |
| validate.py | Good (check_brackets, validate_json, regex_test) |
| measure.py | Good (line_metrics, word_metrics, char_category_metrics) |
| synthesis.py | Good (measure_text, text_equal, explain_diff, inspect_text, count_chars, list_compare) |

**Gap**: No tests for the `utf8_bytes` return type mismatch (tests don't catch that doc says `int` but returns `bytes`).

---

## 9. Conclusion

The `exact/` module is a well-implemented Unicode text inspection toolkit. The main issues are:

1. **Documentation mismatch**: `utf8_bytes` return type documented as `int` but returns `bytes`
2. **Missing features**: No exact arithmetic or fraction handling (despite the title suggesting otherwise)
3. **Architectural drift**: The architecture document needs updating to reflect actual implementation

The code quality is generally good, with proper type annotations, comprehensive tests, and security-conscious design for confusable character detection.

---

*Review generated: 2026-05-07*
