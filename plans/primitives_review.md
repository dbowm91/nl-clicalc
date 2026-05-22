# primitives.py Architecture Review

## Verified Claims

### Core Function Signatures and Behavior
- `utf8_bytes(s: str) -> bytes` - Returns raw UTF-8 bytes (confirmed: returns `bytes` type, not int)
- `codepoints(s: str) -> list[CodepointInfo]` - Returns detailed codepoint info with index, char, codepoint, name, category
- `normalize_unicode(s: str, form: str) -> str` - Normalizes to NFC/NFD/NFKC/NFKD, raises ValueError for invalid forms
- `casefold_text(s: str) -> str` - Uses str.casefold() for case-insensitive comparison
- `raw_equal(a: str, b: str) -> bool` - Checks byte-level string equality
- `normalized_equal(a: str, b: str, form: str = "NFC") -> bool` - Compares after Unicode normalization
- `measure_basic(s: str) -> MeasureBasic` - Returns TypedDict with bytes_utf8, codepoints, graphemes_estimate (None), chars_no_whitespace, ascii, non_ascii
- `find_invisibles(s: str) -> list[InvisibleCharInfo]` - Returns list of InvisibleCharInfo TypedDicts
- `visible_repr(s: str) -> str` - Returns display-safe representation with visible markers

### _INVISIBLE_CHARS Dictionary
All documented characters are correctly mapped:
- ZWSP (U+200B), ZWNJ (U+200C), ZWJ (U+200D)
- LRM (U+200E), RLM (U+200F)
- BOM/ZWNBSP (U+FEFF)
- NBSP (U+00A0)
- LINE SEP (U+2028), PARA SEP (U+2029)
- LRE (U+202A), RLE (U+202B), PDF (U+202C), LRO (U+202D), RLO (U+202E)
- LRI (U+2066), RLI (U+2067), FSI (U+2068), PDI (U+2069)
- WORD JOINER (U+2060)
- SHY (U+00AD)

### _VARIATION_SELECTORS Constant
Correctly defined as `set(range(0xfe00, 0xfe10))` - covers U+FE00 to U+FE0F.

### Order of Checks (Critical for correctness)
The docs state "Variation selector checks must come BEFORE combining mark checks" - this is correctly implemented:
- `visible_repr`: Line 273 checks `0xfe00 <= ord(char) <= 0xfe0f` before line 275's `unicodedata.category(char).startswith("M")`
- `find_invisibles`: Line 216 checks `_VARIATION_SELECTORS` before line 224's `unicodedata.category(char).startswith("M")`

---

## Discrepancies

### 1. Invisible Characters Not Documented
**Severity: Low**

`_INVISIBLE_CHARS` contains characters not mentioned in the architecture doc:
- **CGJ** (U+034F) - COMBINING GRAPHEME JOINER, displayed as "CGJ"
- **MVS** (U+180E) - MONGOLIAN VOWEL SEPARATOR, displayed as "MVS"

These are in the code but missing from the documentation's list of detected characters.

### 2. Missing from visible_repr Documentation
**Severity: Low**

The visible_repr mapping table doesn't mention:
- CGJ mapped to `⟦CGJ⟧`
- MVS mapped to `⟦MVS⟧`
- Soft hyphen (SHY) mapped to `⟦SHY⟧`

---

## Bugs Found

### 1. Redundant WORD JOINER Check in visible_repr (Medium)
**Location**: `nl_calc/exact/primitives.py:277-278`

```python
elif char == "\u2060":
    result.append("⟦WORD JOINER⟧")
```

WORD JOINER (U+2060) is already in `_INVISIBLE_CHARS` at line 65, so the dict lookup at line 270 will match it first. Lines 277-278 are dead code - never reached.

**Fix**: Remove lines 277-278, or remove WORD JOINER from `_INVISIBLE_CHARS` if explicit handling is desired (e.g., for different display output).

### 2. visible_repr BIDI Range Overlaps with _INVISIBLE_CHARS Keys (Low)
**Location**: `nl_calc/exact/primitives.py:279-286`

```python
elif 0x2060 <= ord(char) <= 0x206f:
    bidi_names = {
        0x2066: "LRI", 0x2067: "RLI", 0x2068: "FSI", 0x2069: "PDI",
        0x202a: "LRE", 0x202b: "RLE", 0x202c: "PDF",
        0x202d: "LRO", 0x202e: "RLO",
    }
```

This covers characters that are also keys in `_INVISIBLE_CHARS` (0x2066-0x2069, 0x202a-0x202e). However, since the `_INVISIBLE_CHARS` check at line 270 comes first, this branch only handles the remaining 0x2060-0x206f characters not in the dict (specifically 0x2060 WORD JOINER and 0x2061-0x2065 unassigned).

**Not a bug**, but confusing logic. Could be refactored for clarity.

---

## Improvements

### 1. Add Missing Characters to Documentation (Medium)
Update `architecture/primitives.md` to document:
- CGJ (U+034F) in find_invisibles list
- MVS (U+180E) in find_invisibles list
- All characters should have their display markers in the visible_repr table

### 2. Refactor visible_repr for Clarity (Low)
Current order of checks is correct but non-obvious:
1. Special whitespace (space, tab, newline, CR)
2. Known invisible chars (dict lookup)
3. VS range
4. Combining marks
5. WORD JOINER explicit (redundant)
6. BIDI range

Suggested refactor:
```python
# 1. Special whitespace
if char in " \t\n\r": ...
# 2. Known invisible chars (includes WORD JOINER, CGJ, MVS, SHY, all BIDI controls)
elif char in _INVISIBLE_CHARS: ...
# 3. Variation selectors
elif 0xfe00 <= ord(char) <= 0xfe0f: ...
# 4. Combining marks
elif unicodedata.category(char).startswith("M"): ...
```

Remove the redundant WORD JOINER explicit check (lines 277-278) and the overlapping BIDI range check (lines 279-286), letting the dict handle all BIDI control characters.

### 3. Consider Adding Type Guard for Valid Normalization Forms (Low)
`normalize_unicode` raises ValueError for invalid forms, which is good. Consider using `typing.Literal` for the `form` parameter:

```python
def normalize_unicode(s: str, form: typing.Literal["NFC", "NFD", "NFKC", "NFKD"]) -> str:
```

### 4. Add Tests for Edge Cases (Medium)
Current tests don't verify:
- Empty string handling
- String with only invisible characters
- All variation selectors (U+FE00 to U+FE0F)
- All BIDI control characters
- Mixed ASCII and combining marks

---

## Priority Summary

| Item | Type | Priority |
|------|------|----------|
| Document CGJ and MVS | Discrepancy | Medium |
| Remove redundant WORD JOINER code | Bug | Medium |
| Refactor visible_repr for clarity | Improvement | Low |
| Add type literal for normalization forms | Improvement | Low |
| Add edge case tests | Improvement | Medium |

---

## Conclusion

The core implementation is **correct and well-architected**. The critical ordering requirement (VS before combining marks) is properly implemented. The main issues are:
1. **Documentation gaps** - missing CGJ, MVS, SHY from the architecture doc
2. **Minor code redundancy** - WORD JOINER explicitly checked after already being in dict

No functional bugs that would cause incorrect behavior were found.