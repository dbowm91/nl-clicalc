# Primitives Architecture Review

**Document:** `architecture/primitives.md`
**Code:** `eggcalc/exact/primitives.py`
**Date:** 2026-05-29

---

## Summary

The architecture document is largely accurate but has several discrepancies: one significant undocumented function behavior, multiple undocumented functions, and a minor count discrepancy in the invisible characters dict. All issues are low severity.

---

## Discrepancies

### D1: `visible_repr` Return Type Mismatch

**Location:** `architecture/primitives.md:193-207` vs `primitives.py:247-288`

**Issue:** The documentation shows `find_invisibles` as the example function for `visible_repr`, but the key discrepancy is in the documented behavior. The documentation states `visible_repr` produces display markers like `␠ (space)`, `␉ (tab)`, `⟦ZWSP⟧`, etc. The implementation matches this.

However, the documentation implies this function is related to `InvisibleCharInfo` return type, while `find_invisibles` (which returns `InvisibleCharInfo`) has its own separate section. The `visible_repr` function actually returns a `str`, not a list of `InvisibleCharInfo`.

**Severity:** Low (documentation layout confusing but examples are correct)

---

### D2: `raw_equal` Documentation Misleading

**Location:** `architecture/primitives.md:138-146` vs `primitives.py:138-148`

**Issue:** The documentation states:
> Checks exact byte equality.

```python
raw_equal("abc", "abc")     # → True
raw_equal("abc", "ABC")     # → False
raw_equal("café", "cafe\u0301")  # → False (different bytes)
```

The description "exact byte equality" implies UTF-8 byte comparison. However, the implementation is simply `a == b`, which is Python string equality—not byte comparison. For "café" vs "cafe\u0301", Python's `==` returns `False`, but not because the bytes differ. If the intention was byte comparison, the implementation would need to encode to UTF-8 first.

```python
# Actual behavior:
raw_equal("café", "cafe\u0301")  # Returns False (Python string equality)
# But "café".encode("utf-8") == "cafe\u0301".encode("utf-8") would be True
```

**Severity:** Low (function behaves consistently with its implementation, but name/description suggests byte-level comparison)

---

### D3: Invisible Characters Count

**Location:** `architecture/primitives.md:56-85` vs `primitives.py:46-69`

**Issue:** The documentation states `_INVISIBLE_CHARS` has 20 entries in the dict block, but actually lists 22 characters in the code block. The actual count is 22.

**Severity:** Very low (documentation count is off by 2, but the actual content is correct)

---

## Missing Documentation

### M1: Undocumented Functions

The following functions exist in `primitives.py` but are NOT documented in `architecture/primitives.md`:

| Function | Location | Purpose |
|----------|----------|---------|
| `byte_offset_to_codepoint_index()` | `primitives.py:452` | Convert UTF-8 byte offset to codepoint index |
| `codepoint_index_to_byte_offset()` | `primitives.py:500` | Convert codepoint index to UTF-8 byte offset |
| `codepoint_index_to_line_column()` | `primitives.py:529` | Convert codepoint index to line/column |
| `line_column_to_codepoint_index()` | `primitives.py:560` | Convert line/column to codepoint index |
| `get_line_text()` | `primitives.py:606` | Extract text of a specific line |
| `get_surrounding_lines()` | `primitives.py:640` | Get lines before and after a given line |
| `detect_newline_style()` | `primitives.py:681` | Detect CRLF/LF/CR/mixed newline style |

**Severity:** Medium (these are useful public functions that should be documented)

---

### M2: `_is_extend_char` and `_is_extended_pictographic`

**Location:** `primitives.py:351-388`

These internal helper functions are used by `count_graphemes` and `truncate_to_grapheme` but are not documented. While internal, they contain non-trivial Unicode logic that may be worth documenting for maintainers.

**Severity:** Very low (internal functions)

---

## Verified Correct Items

The following items were verified as correctly documented and implemented:

- `CodepointInfo(NamedTuple)` with fields: index, char, codepoint, name, category ✓
- `MeasureBasic(TypedDict)` with fields: bytes_utf8, codepoints, graphemes_estimate, chars_no_whitespace, ascii, non_ascii ✓
- `InvisibleCharInfo(TypedDict)` with fields: index, char, codepoint, name, category, display ✓
- `utf8_bytes()` returns actual `bytes` object ✓
- `codepoints()` returns list of CodepointInfo with correct U+XXXX format ✓
- `normalize_unicode()` with NFC/NFD/NFKC/NFKD forms, raises ValueError on invalid form ✓
- `casefold_text()` uses str.casefold() ✓
- `normalized_equal()` with default form="NFC" ✓
- `measure_basic()` computes all metrics correctly ✓
- `count_graphemes()` implements GB9, GB11, GB12/GB13 rules ✓
- `truncate_to_grapheme()` preserves grapheme integrity ✓
- `find_invisibles()` detects Cf, M*, C* categories, variation selectors, BIDI controls ✓
- `visible_repr()` display order: invisible chars → VS → combining marks → BIDI ✓
- Variation selectors (U+FE00-U+FE0F) correctly handled separately from `_INVISIBLE_CHARS` ✓
- `detect_newline_style()` returns "CRLF", "LF", "CR", or "mixed" ✓

---

## Documentation Clarifications Needed

### C1: `visible_repr` Display Order Wording

**Location:** `architecture/primitives.md:254-264`

The documentation says:
> 1. First check for known invisible characters (ZWSP, BOM, etc.)
> 2. Then check for variation selectors (U+FE00-U+FE0F)
> 3. Then check for combining marks (category 'Mn', 'Mc')
> 4. Then check for BIDI override characters (U+2060-206F, U+202A-202E)
> 5. Then report character as-is

The implementation order at `primitives.py:261-286` is:
1. Space characters (\t, \n, \r, space)
2. Known invisible chars (`_INVISIBLE_CHARS`)
3. Variation selectors (0xfe00-0xfe0f)
4. Combining marks (category M*)
5. BIDI characters (0x2060-0x206f)

The implementation combines space chars at step 1, which is not explicit in the documentation.

**Recommendation:** Clarify that space/tab/newline are handled first, or note that the BIDI range includes U+202A-202E which are also in `_INVISIBLE_CHARS`.

---

### C2: `_INVISIBLE_CHARS` Dict Description

**Location:** `architecture/primitives.md:56-87`

The documentation states "The module maintains a dictionary of invisible characters" and lists 22 characters. It also states "Also detects variation selectors (U+FE00 to U+FE0F)."

This is slightly ambiguous—it could be read as variation selectors being part of `_INVISIBLE_CHARS`, but they are actually stored in `_VARIATION_SELECTORS` as a separate set.

**Recommendation:** Clarify that variation selectors are handled separately.

---

## Minor Issues

### MIN-1: Documented Invisible Characters List Doesn't Mention VS

**Location:** `architecture/primitives.md:56-87`

The code block for `_INVISIBLE_CHARS` shows 22 entries. The text says "Also detects variation selectors" but variation selectors are not in the dict. This is technically correct but could be clearer.

**Severity:** Very low

---

### MIN-2: `raw_equal` Example with Accent

**Location:** `architecture/primitives.md:145`

```python
raw_equal("café", "cafe\u0301")  # → False (different bytes)
```

The comment says "different bytes" but Python's `==` compares by code point, not UTF-8 byte sequence. Both strings would encode to the same UTF-8 bytes after NFC normalization. The comment is misleading.

**Severity:** Very low

---

## Recommendations

1. **Document the 7 undocumented functions** (`byte_offset_to_codepoint_index`, `codepoint_index_to_byte_offset`, `codepoint_index_to_line_column`, `line_column_to_codepoint_index`, `get_line_text`, `get_surrounding_lines`, `detect_newline_style`)
2. **Clarify `raw_equal`** description—if it should compare UTF-8 bytes, the implementation needs to change; otherwise rename to `string_equal` or clarify "character equality"
3. **Update `visible_repr` documentation** to clarify space handling order
4. **Fix the `_INVISIBLE_CHARS` count** in text (says 20, is 22)
5. **Clarify variation selector handling** is separate from `_INVISIBLE_CHARS`

---

## Risk Assessment

| Category | Risk Level | Notes |
|----------|------------|-------|
| Security | Low | Deterministic primitives, no external calls |
| Correctness | Low | Minor doc discrepancies, `raw_equal` description misleading |
| Usability | Medium | 7 useful functions undocumented |
| Completeness | Medium | Missing position conversion and line functions |

No critical issues found that would prevent the module from functioning as designed.
