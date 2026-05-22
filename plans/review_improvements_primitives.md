# primitives.py Review - Improvement Plan

## Verified Claims (Code References)

### UTF-8 Handling ✓
- `utf8_bytes()` at line 75-84 returns actual `bytes` object (not count) - **Verified**
- Empty string returns `b''` - **Verified**

### Codepoint Iteration ✓
- `codepoints()` at line 87-103 returns `list[CodepointInfo]` with correct fields - **Verified**
- Uses `unicodedata.name()` and `unicodedata.category()` correctly - **Verified**

### Unicode Normalization ✓
- `normalize_unicode()` at line 106-123 validates forms and returns normalized string - **Verified**
- `normalized_equal()` at line 151-162 defaults to NFC and calls `normalize_unicode()` - **Verified**
- `casefold_text()` at line 126-135 correctly delegates to `str.casefold()` - **Verified**

### Grapheme Counting ✓
- `count_graphemes()` at line 291-348 implements UAX #29 rules - **Verified**
- `truncate_to_grapheme()` at line 398-463 correctly preserves grapheme integrity - **Verified**

### Invisible Character Detection ✓
- `visible_repr()` at line 247-288 correctly handles display order: known invisibles → VS → combining → bidi - **Verified**
- Variation selector check at line 273 comes BEFORE combining mark check at line 275 - **Verified**

---

## Discrepancies Between Documentation and Code

### 1. `graphemes_estimate` Type Mismatch
**File:** `architecture/primitives.md:102`
```
graphemes_estimate: None # Not implemented
```

**File:** `architecture/exact-primitives.md:39`
```
graphemes_estimate: int      # Estimated grapheme clusters
```

**Code:** `primitives.py:29` and `measure_basic()` at line 165-189
```python
graphemes_estimate: int      # Code and exact-primitives.md show int
graphemes_estimate=grapheme_count  # Actually implemented and working
```

**Verdict:** `primitives.md` is outdated. The feature is implemented.

---

### 2. `visible_repr` Return Format
**File:** `architecture/primitives.md:134-145`
Shows `␠`, `␉`, `␊`, `␍` markers

**Code:** `primitives.py:261-269`
Uses same markers: `␠`, `␉`, `␊`, `␍`

**Verdict:** Correct

---

### 3. `_INVISIBLE_CHARS` Coverage
Both docs show same structure. Code includes additional entries not documented:
- `\u202a` (LRE), `\u202b` (RLE), `\u202c` (PDF), `\u202d` (LRO), `\u202e` (RLO)
- `\u2066` (LRI), `\u2067` (RLI), `\u2068` (FSI), `\u2069` (PDI)
- `\u180e` (MVS), `\u034f` (CGJ)

**Verdict:** Documentation is incomplete but not incorrect.

---

## Potential Bugs

### Bug 1: Stale Comment References Removed Function
**Location:** `primitives.py:355`
```python
"""Note: ZWJ (U+200D) is NOT included here because it's part of emoji
    ZWJ sequences (GB11) and must be handled specially in _advance_past_sequence.
```

**Issue:** `_advance_past_sequence()` was removed (dead code). The comment still references it.

**Severity:** Low (cosmetic/developer confusion)

---

### Bug 2: `_is_extended_pictographic` Overly Broad Range
**Location:** `primitives.py:382`
```python
if 0x1F300 <= cp <= 0x10FFFF:
    return True
```

**Issue:** Range covers U+1F300 to U+10FFFF which is 186,896 codepoints. Most are NOT pictographic. The function will incorrectly accept any character in this range including private use areas (U+E000-U+EFFF), supplementary private use areas, and unassigned codepoints.

**Severity:** Medium (false positives in grapheme counting could cause truncation issues with specially crafted strings)

---

### Bug 3: BIDI Character Detection Gap in `find_invisibles()`
**Location:** `primitives.py:219-222`
```python
# Check bidi control characters (U+2060 to U+206F)
elif 0x2060 <= codepoint_val <= 0x206f:
    name = unicodedata.name(char, "<unknown>")
    display = f"BIDI:{name.split()[-1]}"
```

**Issue:** Range `0x2060-0x206F` is checked AFTER checking `_INVISIBLE_CHARS` (which already contains some bidi chars at different codepoints like LRE at U+202A). However, U+202A-U+202E are handled by `_INVISIBLE_CHARS`, but U+2066-U+2069 (LRI, RLI, FSI, PDI) are ALSO in `_INVISIBLE_CHARS`. This means the BIDI elif branch only catches U+2060-U+2065 and U+206A-U+206F which are not in `_INVISIBLE_CHARS`.

**Impact:** Low - these codepoints are rarely used and the function still detects them.

---

## Improvement Suggestions

### High Priority

#### 1. Fix Stale Comment
**Location:** `primitives.py:355`
```python
# Before:
ZWJ sequences (GB11) and must be handled specially in _advance_past_sequence.

# After:
ZWJ sequences (GB11) and must be handled specially in count_graphemes().
```

---

#### 2. Refine `_is_extended_pictographic` Range Check
**Location:** `primitives.py:382`

The range `0x1F300 <= cp <= 0x10FFFF` is too broad. Consider using the Unicode database instead:

```python
def _is_extended_pictographic(char: str) -> bool:
    """Check if char is an Extended Pictographic (for emoji ZWJ sequences)."""
    cp = ord(char)
    # Check via Unicode name pattern or explicit emoji blocks
    name = unicodedata.name(char, '')
    if 'EMOJI' in name or 'FLAG' in name:
        return True
    # Explicit emoji blocks per UAX #51
    if (0x1F300 <= cp <= 0x1F9FF or  # Emoticons, Transport, Symbols, etc.
        0x2600 <= cp <= 0x26FF or    # Misc symbols
        0x2700 <= cp <= 0x27BF):     # Dingbats
        return True
    return False
```

---

### Medium Priority

#### 3. Update `primitives.md` Documentation
**Location:** `architecture/primitives.md:102`

Update to reflect that `graphemes_estimate` is implemented:
```
graphemes_estimate: int      # Estimated grapheme clusters
```

Also add documentation for:
- `count_graphemes()`
- `truncate_to_grapheme()`
- `_is_extend_char()`
- `_is_extended_pictographic()`

---

#### 4. Add Complete `_INVISIBLE_CHARS` List to Documentation
Both architecture docs show partial lists. Add remaining entries for completeness.

---

### Low Priority

#### 5. Consider Adding `normalized_equal` Default Form to Signature
**Location:** `primitives.py:151`

The function signature shows `form: str = "NFC"` but the doc doesn't emphasize this. Consider documenting in docstring.

---

## Summary

| Item | Priority | Type |
|------|----------|------|
| Fix stale comment referencing removed function | High | Bug |
| Refine `_is_extended_pictographic` range | High | Bug |
| Update primitives.md graphemes_estimate | Medium | Documentation |
| Document count_graphemes/truncate functions | Medium | Documentation |
| Complete invisible chars list in docs | Low | Documentation |

The core UTF-8, codepoint, normalization, and grapheme functionality is **correct and working**. The issues are minor documentation inconsistencies and one potential bug (overly broad pictographic range check).