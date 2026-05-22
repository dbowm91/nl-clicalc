# primitives.py Architecture Review

## Summary

The `nl_calc/exact/primitives.py` module provides low-level Unicode text primitives for the `exact/` package. It offers functions for encoding, codepoint analysis, normalization, equality checking, text measurement, and invisible character detection. The module is deterministic, uses only Python standard library, and does not perform semantic interpretation.

## Verified Claims

The following claims in `architecture/primitives.md` are **confirmed** by the implementation:

### Core Encoding and Codepoints
- `utf8_bytes(s: str) -> bytes` - Correctly returns raw UTF-8 encoded bytes (primitives.py:75-84)
- `codepoints(s: str) -> list[CodepointInfo]` - Returns correct CodepointInfo namedtuples with index, char, codepoint (U+XXXX format), Unicode name, and category (primitives.py:87-103)
- `CodepointInfo` NamedTuple has correct fields: index, char, codepoint, name, category (primitives.py:16-22)

### Normalization
- `normalize_unicode(s: str, form: str) -> str` - Validates forms (NFC, NFD, NFKC, NFKD) and raises ValueError for invalid forms (primitives.py:106-123)
- `casefold_text(s: str) -> str` - Uses str.casefold() for case-insensitive comparison (primitives.py:126-135)

### Equality Checking
- `raw_equal(a: str, b: str) -> bool` - Checks exact string equality (primitives.py:138-148)
- `normalized_equal(a: str, b: str, form: str = "NFC") -> bool` - Normalizes both strings before comparison (primitives.py:151-162)

### Measurement
- `measure_basic(s: str) -> MeasureBasic` - Returns all documented fields: bytes_utf8, codepoints, graphemes_estimate (None), chars_no_whitespace, ascii, non_ascii (primitives.py:165-188)
- `MeasureBasic` TypedDict has all documented fields (primitives.py:25-32)

### Invisible Character Detection
- `find_invisibles(s: str) -> list[InvisibleCharInfo]` - Detects all documented character types:
  - ZWSP, ZWNJ, ZWJ (primitives.py:47-49)
  - LRM, RLM, LRE, RLE, PDF, LRO, RLO (primitives.py:50-60, 219-221)
  - LRI, RLI, FSI, PDI (primitives.py:61-64, 219-221)
  - BOM (primitives.py:52)
  - NBSP (primitives.py:53)
  - LINE SEPARATOR, PARAGRAPH SEPARATOR (primitives.py:54-55)
  - SOFT HYPHEN (primitives.py:66)
  - VARIATION SELECTORS (primitives.py:71-72, 215-217)
  - COMBINING GRAPHEME JOINER (primitives.py:68)
- `InvisibleCharInfo` TypedDict has all documented fields: index, char, codepoint, name, category, display (primitives.py:35-42)
- `_INVISIBLE_CHARS` dictionary maps codepoints to (name, display) tuples (primitives.py:46-69)
- `_VARIATION_SELECTORS` set contains U+FE00 to U+FE0F (15 variation selectors + 1 = 16 total) (primitives.py:72)
- Control characters (category C*) are detected but newlines are excluded (primitives.py:227)

### Dependencies
- Uses only `unicodedata` and `typing` from standard library (confirmed)

## Issues Found

### Bug 1: visible_repr() Variation Selector Display is Inconsistent

**Severity:** Low (display inconsistency)

**Document says:** Variation selectors should be displayed as `⟦VS⟧`
```
| VS | ⟦VS⟧ |
```

**Actual implementation:** Variation selectors (U+FE00 to U+FE0F) are displayed as `◌︀` (combining circle with variation selector)

**Root cause:** In `visible_repr()` (primitives.py:274), the variation selector check comes AFTER the combining mark check (primitives.py:272-273):
```python
elif unicodedata.category(char).startswith("M"):
    result.append(f"◌{char}")  # This catches VS because VS is Mn category!
elif 0xfe00 <= ord(char) <= 0xfe0f:
    result.append("⟦VS⟧")  # Never reached for VS characters
```

**Reference:** primitives.py:272-275

### Bug 2: visible_repr() does not handle WORD JOINER (U+2060)

**Severity:** Medium (missing feature / inconsistency)

**Document says:** WORD JOINER is in `_INVISIBLE_CHARS` and should have a display marker.

**Actual behavior:** WORD JOINER (U+2060) IS detected by `find_invisibles()` (returns `display: "WORD JOINER"`), but `visible_repr()` does NOT have a specific case for it. It falls through to the else branch and is returned as-is.

**Reference:** primitives.py:269-285 (visible_repr has no case for U+2060)

**Note:** This is documented in `find_invisibles` section but NOT in the `visible_repr` table, so technically not a bug, but an inconsistency between expected behavior and implementation.

## Improvement Recommendations

### Recommendation 1: Fix visible_repr() Variation Selector Handling

Move the variation selector check before the combining mark check, or add an explicit check for variation selectors that precedes the combining mark check:

**File:** `nl_calc/exact/primitives.py`
**Line:** ~272-275

**Suggested fix:**
```python
# Check variation selectors first (before combining marks)
if 0xfe00 <= ord(char) <= 0xfe0f:
    result.append("⟦VS⟧")
elif unicodedata.category(char).startswith("M"):
    result.append(f"◌{char}")
```

### Recommendation 2: Add visible_repr() Handling for WORD JOINER

WORD JOINER (U+2060) is detected by `find_invisibles()` but not handled by `visible_repr()`. Add a case:

**File:** `nl_calc/exact/primitives.py`
**Line:** ~269 (after the `_INVISIBLE_CHARS` check)

**Suggested fix:**
Add after line 271:
```python
elif char == "\u2060":  # WORD JOINER
    result.append("⟦WORD JOINER⟧")
```

### Recommendation 3: Consider adding grapheme cluster estimation

The document notes that `graphemes_estimate` is "Not implemented" and always returns `None`. If accurate grapheme cluster counting is needed (for correct visual character counting), consider implementing using `unicodedata` or regex approaches.

**Reference:** primitives.py:184 (always None), architecture/primitives.md:103

## Test Coverage Assessment

The existing tests in `tests/test_exact.py` (TestPrimitives class, lines 46-188) adequately cover:
- Basic function signatures
- ASCII and Unicode inputs
- Edge cases (empty strings, combining characters)
- Known invisible characters (ZWSP, BOM, NBSP, BIDI, combining)
- The documented behaviors match implementation

However, tests do not cover:
- Variation selector edge cases
- WORD JOINER in `visible_repr`
- Soft hyphen in `visible_repr`

## Conclusion

The primitives module implementation is largely correct and matches the architectural specification. The main issues are:

1. **Bug 1 (Display Inconsistency):** Variation selectors should display as `⟦VS⟧` per documentation but display as `◌︀` in practice
2. **Bug 2 (Missing Feature):** WORD JOINER is detected by `find_invisibles()` but not properly represented in `visible_repr()`

Both issues are low-to-medium severity and affect only display formatting, not correctness of detection logic.