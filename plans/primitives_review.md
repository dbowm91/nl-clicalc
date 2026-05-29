# primitives.py Architecture Review

## Source Files Reviewed
- `architecture/primitives.md` (documentation)
- `nl_calc/exact/primitives.py` (702 lines, implementation)

## Verification Results

### ✅ MATCHES - Verified Claims

| Claim | Status | Evidence |
|-------|--------|----------|
| `utf8_bytes(s)` returns `bytes` | MATCHES | Code at line 84: `return s.encode("utf-8")` |
| `CodepointInfo` as NamedTuple | MATCHES | Lines 16-22, all 5 fields present |
| `MeasureBasic` as TypedDict | MATCHES | Lines 25-32, all 6 fields present |
| `InvisibleCharInfo` as TypedDict | MATCHES | Lines 35-42, all 7 fields present |
| `_INVISIBLE_CHARS` contains 22 characters | MATCHES | Verified: 22 entries in dict |
| Variation selectors (U+FE00-U+FE0F) detection | MATCHES | Lines 71-72, `_VARIATION_SELECTORS` set defined |
| `visible_repr()` VS check before combining marks | MATCHES | Lines 273 (VS range) checked before line 275 (category 'M') |
| `count_graphemes()` handles family emoji as 1 | MATCHES | ZWJ sequence handling at lines 323-333 |
| `casefold_text()` handles German ß | MATCHES | Uses `str.casefold()` at line 135 |
| `normalize_unicode()` raises `ValueError` for invalid form | MATCHES | Lines 119-122 with explicit error message |
| `raw_equal()` checks byte identity | MATCHES | Simply `a == b` at line 148 |
| `normalized_equal()` defaults to NFC | MATCHES | Line 151: `form: str = "NFC"` |

### Discrepancies Found

None - the architecture document is fully accurate.

### 🐛 Bugs Identified

#### Bug 1: ZWSP not treated as Extend in `_is_extend_char` (Low Severity)

**Location:** `primitives.py:351-369`

**Description:** ZWSP (U+200B) is a Cf (Format) character but incorrectly fails the Extend check. Per Unicode UAX #29, ZWSP functions as an Extend character in grapheme cluster boundary detection (GB9), similar to ZWNJ (U+200C) which IS correctly included.

**Code:**
```python
def _is_extend_char(char: str) -> bool:
    cat = unicodedata.category(char)
    cp = ord(char)
    if cat.startswith('M'):
        return True
    if cp == 0x200C:  # ZWNJ only (not ZWJ)
        return True
    if 0xFE00 <= cp <= 0xFE0F:
        return True
    return False
```

ZWSP (0x200B) is excluded, so `count_graphemes("a\u200bb")` returns 3 instead of 2.

**Impact:** Low - Only affects grapheme counting and truncation for strings containing ZWSP. ZWNJ (0x200C) is correctly included.

**Fix suggestion:** Add ZWSP to _is_extend_char:
```python
if cp == 0x200C or cp == 0x200B:  # ZWNJ and ZWSP
    return True
```

---

### Improvements Suggested

| Priority | Item | Description |
|----------|------|-------------|
| Low | Add `_is_extend_char` to exports | The function exists (lines 351-369) but is not in module's `__all__` or tested directly |
| Low | Add tests for ZWSP extend behavior | No test currently verifies that ZWSP is correctly treated as Extend |
| Medium | Document ZWSP exclusion rationale | If exclusion is intentional, add comment explaining why ZWSP differs from ZWNJ |
| Low | Add edge case test for empty string truncation | `truncate_to_grapheme("", 0)` returns "" correctly, but not tested |

---

### Priority Summary

1. **Bug 1 (Low):** ZWSP not treated as Extend - affects `count_graphemes()` accuracy
2. **Documentation:** Architecture doc is accurate; the prose note about "22 vs 12" is itself documented (lines 12 references missing docs)
3. **No critical bugs found**
4. All 22 invisible characters present and correctly detected
5. Variation selector ordering is correct
6. All 125 tests pass

---

## Additional Notes

### Verified Correct Behaviors
- `byte_offset_to_codepoint_index()` correctly raises `ValueError` when byte offset falls inside multi-byte character
- `truncate_to_grapheme()` correctly handles emoji (🏳️‍🌈, 👨‍👩‍👧‍👦), combining marks, and regional indicators
- `visible_repr()` correctly wraps combining chars with ◌ prefix (line 276)
- BIDI characters U+202A-202E and U+2066-206F are correctly handled
- `detect_newline_style()` correctly returns mixed when multiple styles present

### Test Coverage
- 125 tests in `test_exact.py` covering primitives module
- All tests passing (verified via pytest)
- No direct test for `_is_extend_char()` function (only indirect via `_is_extended_pictographic_cjk_not_emoji`)
