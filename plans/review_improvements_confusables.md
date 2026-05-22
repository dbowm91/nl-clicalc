# Confusables Module Review - Improvement Plan

## Verified Claims (with code references)

### Data Structure
- **VERIFIED**: `CONFUSABLES` is `dict[str, str]` mapping codepoint strings to space-separated substitution codepoints (confusables.py:14)
- **VERIFIED**: Entry format is `"U+XXXX": "U+0061 U+0062"` (confusables.py:15-16)
- **VERIFIED**: Generator script at `scripts/generate_confusables.py` downloads from Unicode and generates the table

### Detection Logic
- **VERIFIED**: `detect_confusables()` in unicode_tools.py:172-215 iterates characters and looks up `U+XXXX` keys in CONFUSABLES table
- **VERIFIED**: Substitution codepoints are parsed back to characters via `chr(int(cp[2:], 16))` (unicode_tools.py:195)
- **VERIFIED**: `confusable_name` is constructed by joining `unicodedata.name()` for each confusable character (unicode_tools.py:197-204)
- **VERIFIED**: `confusables_count()` is a fast path that just checks membership without building full result (unicode_tools.py:218-232)

### Integration Points
- **VERIFIED**: `inspect_text()` in synthesis.py:559-565 iterates confusables and appends warnings with `confusable_with` field
- **VERIFIED**: `normalize.py` debug command at line 1150 prints `conf['confusable_with']` to show what character looks like
- **VERIFIED**: Tests in test_exact.py:242-268 verify confusable detection works for Cyrillic, Greek, fullwidth, and mathematical variants

### Table Size and Format
- **VERIFIED**: confusables.py contains 6581 lines of mappings (auto-generated)
- **VERIFIED**: The `__all__ = ["CONFUSABLES"]` export is present at line 13331 (confusables.py:6581)

---

## Discrepancies Between Documentation and Code

### 1. Architecture Documentation Incomplete (MEDIUM PRIORITY)

**Documentation** (`architecture/confusables.md`, lines 14-22):
```python
CONFUSABLES: dict[str, str] = {
    # key: "U+XXXX" (codepoint of confusable character)
    # value: space-separated codepoints it confusable with
    "U+0430": "U+0061",      # Cyrillic 'а' confusable with Latin 'a'
    ...
}
```

**Issue**: Documentation shows a simple single-codepoint example, but the actual table contains many multi-codepoint substitutions like:
- `"U+00A2": "U+0063 U+0338"` (cent sign → c + combining long solidus overlay)
- `"U+0133": "U+0069 U+006A"` (ij ligature → i + j)

**Code Reference**: confusables.py:24 shows `"U+00A2": "U+0063 U+0338"` with comment `# e.g., 'U+0410' (Cyrillic A) -> 'U+0041' (Latin A)` which is misleading since it shows single mapping but the entry has two codepoints.

### 2. ConfusableInfo TypedDict Mismatch (HIGH PRIORITY)

**Documentation** (`architecture/exact-unicode_tools.md`, lines 29-36):
```python
class ConfusableInfo(TypedDict):
    char: str              # The confusable character
    codepoint: str         # "U+XXXX" format
    name: str              # Unicode name
    confusable_for: str    # What it might be confused with
    confusable_codepoint: str  # Confusing character's codepoint
    script: str            # Script of the character
```

**Actual Code** (`nl_calc/exact/unicode_tools.py`, lines 29-36):
```python
class ConfusableInfo(TypedDict):
    index: int
    char: str
    codepoint: str
    name: str
    confusable_with: str   # Different field name
    confusable_name: str    # Different field name
```

**Discrepancies**:
- Field `confusable_for` vs actual `confusable_with` - naming mismatch (unicode_tools.py:35)
- Field `confusable_codepoint` missing, replaced by `confusable_name` which is the Unicode name of the confusable character, not its codepoint (unicode_tools.py:36)
- Field `script` missing entirely
- Field `index` present in code but not documented

**Impact**: Known issue per AGENTS.md line 247. Code using documentation would reference non-existent fields.

### 3. Confusables.py Documentation Misleading Comment (LOW PRIORITY)

**Code** (confusables.py:11-12):
```python
# e.g., 'U+0410' (Cyrillic A) -> 'U+0041' (Latin A)
# Names are derived at runtime via unicodedata.name().
```

**Issue**: The comment describes single-codepoint mapping, but many entries have multi-codepoint substitutions (e.g., `"U+00A2": "U+0063 U+0338"`). The comment should clarify that values can be single or multiple space-separated codepoints.

---

## Potential Bugs

### 1. No Reverse Lookup Capability (MEDIUM)

**Issue**: The CONFUSABLES table only maps confusable characters to their Latin/likely substitutions. There is no reverse lookup to find if a legitimate Latin character could be confused with a homoglyph.

**Example**: If you want to check if "paypal" contains characters that look like Cyrillic equivalents, you need forward lookup only. But if you want to check if Cyrillic text could be confused with valid Latin identifiers, you need reverse mapping.

**Current limitation**: The table is unidirectional. The documentation at line 30-31 mentions `unicode_tools.detect_confusables()` scans text using forward lookup only.

**Severity**: Medium - may be by design for specific use case, but worth documenting.

### 2. confusable_name Construction Bug with Empty Names (LOW)

**Code** (unicode_tools.py:197-204):
```python
confusable_name = ""
for c in confusable_with:
    n = unicodedata.name(c, "")
    if n:
        confusable_name += n + " "
    else:
        confusable_name += c
confusable_name = confusable_name.strip()
```

**Issue**: If `unicodedata.name(c, "")` returns empty string, the character itself is used. However, for combining marks (e.g., U+0338 combining long solidus overlay), the name might be non-empty but the resulting string representation in `confusable_with` could still be confusing when displayed.

**Severity**: Low - actually correct behavior for combining marks, but the resulting message could be confusing.

---

## Improvement Suggestions

### HIGH PRIORITY

1. **Update `architecture/exact-unicode_tools.md` ConfusableInfo TypedDict**
   - Fix field names to match actual implementation
   - Add `index` field documentation
   - Remove `script` field since it doesn't exist
   - Change `confusable_codepoint` to `confusable_name` with accurate description

2. **Update `architecture/confusables.md` data structure examples**
   - Add example of multi-codepoint substitution
   - Clarify that values are space-separated codepoints that may represent ligatures or combining characters

### MEDIUM PRIORITY

3. **Add reverse lookup function** (optional enhancement)
   - `get_confusable_by(target: str) -> list[ConfusableInfo]` to find which characters confusable with a given target
   - Would enable checking if Cyrillic text could spoof Latin identifiers

4. **Update confusables.py header comment**
   - Clarify multi-codepoint nature of substitutions
   - Keep generating script documentation accurate

### LOW PRIORITY

5. **Add docstrings to ConfusableInfo TypedDict fields**
   - Currently TypedDict fields lack documentation (unicode_tools.py:29-36)
   - Would help users understand the return structure

---

## Summary

The confusables module architecture is sound:
- Data table is correctly generated from official Unicode source
- Detection logic correctly identifies confusables via forward lookup
- Integration with `inspect_text()` and debug commands works properly

**Primary Issue**: Documentation in `architecture/exact-unicode_tools.md` has incorrect `ConfusableInfo` structure that doesn't match actual implementation. This is a known issue per AGENTS.md.

**Secondary Issue**: `architecture/confusables.md` examples don't reflect the multi-codepoint nature of many substitutions.

**Recommendation**: Update documentation to accurately reflect the actual implementation, particularly the `ConfusableInfo` TypedDict fields.