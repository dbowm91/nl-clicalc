# Confusables Module Review

## Summary

The `nl_calc.exact.confusables` module provides a lookup table of Unicode homoglyph characters derived from Unicode Standard Annex #39 (UTS #39). The `CONFUSABLES` dict maps characters (identified by `U+XXXX` codepoint strings) to their confusable equivalents (space-separated `U+XXXX` codepoint strings). The `detect_confusables()` function in `unicode_tools.py` uses this table to scan text for potentially deceptive homoglyphs that could be used in spoofing attacks.

---

## Verified Claims

### Document Claims vs Implementation

| Claim (architecture/confusables.md) | Status | Implementation |
|-----------------------------------|--------|-----------------|
| **Data Source**: Derived from Unicode `confusables.txt` at unicode.org | ✅ VERIFIED | `scripts/generate_confusables.py:15` fetches from `https://www.unicode.org/Public/security/latest/confusables.txt` |
| **Data Structure**: `CONFUSABLES: dict[str, str]` mapping codepoint → space-separated codepoints | ✅ VERIFIED | `confusables.py:14` defines `CONFUSABLES: dict[str, str]` with format `"U+XXXX": "U+YYYY U+ZZZZ"` |
| **Key format**: `"U+XXXX"` codepoint strings | ✅ VERIFIED | `generate_confusables.py:125` formats keys as `U+{ord(source):04X}` |
| **Value format**: space-separated codepoints | ✅ VERIFIED | `generate_confusables.py:126` formats values as `" ".join(f"U+{ord(c):04X}" for c in sub)` |
| **Generation script**: `scripts/generate_confusables.py` regenerates the table | ✅ VERIFIED | `confusables.py:5` states "DO NOT EDIT - regenerate with scripts/generate_confusables.py" |
| **Example mappings**: `U+0430` → `U+0061` (Cyrillic а → Latin a) | ✅ VERIFIED | `CONFUSABLES['U+0430']` == `'U+0061'` |
| **Example mappings**: `U+0443` → `U+0079` (Cyrillic y → Latin y) | ✅ VERIFIED | `CONFUSABLES['U+0443']` == `'U+0079'` |
| **Example mappings**: `U+0410` → `U+0041` (Cyrillic А → Latin A) | ✅ VERIFIED | `CONFUSABLES['U+0410']` == `'U+0041'` |

### Functional Verification

| Test | Result |
|------|--------|
| `detect_confusables("АBC")` detects Cyrillic А | ✅ Returns 1 confusable with `char='А'`, `confusable_with='A'` |
| `detect_confusables("ΑBC")` detects Greek Α | ✅ Returns 1 confusable with `char='Α'`, `confusable_with='A'` |
| `detect_confusables("\uff21")` detects Fullwidth A | ✅ Returns 1 confusable with `char='Ａ'`, `confusable_with='A'` |
| `detect_confusables("\U0001d670")` detects Math Script A | ✅ Returns 1 confusable with `char='𝙰'`, `confusable_with='A'` |
| `detect_confusables("paypal")` Latin-only string | ✅ Returns 0 confusables (no false positives) |
| `detect_confusables("")` empty string | ✅ Returns empty list |

### Documentation Claims (docs/exact.md)

| Claim | Status |
|-------|--------|
| Line 138: "~1800 entries" in confusables table | ❌ ACTUAL: 6564 entries (3.6x larger than documented) |
| Line 146: `confusable_with` is a codepoint string like `U+0041` | ❌ ACTUAL: Returns the actual character string `'A'` not codepoint |
| Line 148-154: Example return structure for `detect_confusables("pаypal")` | ❌ **BUG**: `confusable_with='U+0041'` shows codepoint format, but actual return is `confusable_with='a'` (character) |
| Line 157: `detect_confusables("10")` may detect '0' confusable with 'O' | ✅ VERIFIED (U+0030 → U+004F exists in table) |

---

## Issues Found

### Issue 1: Documentation Mismatch on Return Format (BUG)

**File:** `docs/exact.md:146-153`

The documentation shows:
```python
confusable_with='U+0041',      # Shows codepoint format
confusable_name='LATIN CAPITAL LETTER A'
```

But the actual implementation at `unicode_tools.py:175` returns the **character itself**:
```python
confusable_with = "".join(chr(int(cp[2:], 16)) for cp in sub_str.split())
```

So `detect_confusables("АBC")[0]["confusable_with"]` returns `'A'` (character), not `'U+0041'` (codepoint string).

### Issue 2: Table Size Understated in Documentation

**File:** `docs/exact.md:138`

The documentation states "~1800 entries" but the actual table has **6564 entries**.

This is not a bug per se (the data source is authoritative), but the documentation is stale.

### Issue 3: Typo in Architecture Document

**File:** `architecture/confusables.md:29`

Line 29 duplicates line 28:
```
28: - `U+0430` (Cyrillic small letter A) → `U+0061` (Latin small letter A)
29: - `U+0430` (Cyrillic small letter A) → `U+0061` (Latin small letter A)
```

### Issue 4: Documentation Example Uses Wrong Variable Name Pattern

**File:** `docs/exact.md:152`

The doc shows `confusable_name='LATIN CAPITAL LETTER A'` but the actual field name pattern doesn't match the codepoint being substituted. The implementation at `unicode_tools.py:177-184` correctly derives names at runtime, but the example shows `confusable_with='U+0041'` when it should show the character `'A'`.

---

## Improvement Recommendations

### REC-1: Fix Documentation Return Format (docs/exact.md:146-153)

**Priority:** Medium

The example return value should show the actual return format (character, not codepoint):

```python
# CURRENT (incorrect):
#   confusable_with='U+0041',      # Shows codepoint format
#   confusable_name='LATIN CAPITAL LETTER A'

# SHOULD BE:
#   confusable_with='a',            # Actual character
#   confusable_name='LATIN SMALL LETTER A'
```

Or alternatively, the implementation could be changed to return codepoint strings consistently, which would require updating `unicode_tools.py:175` and potentially breaking consumers.

### REC-2: Update Table Size Documentation (docs/exact.md:138)

**Priority:** Low

Change "~1800 entries" to "~6500 entries" to reflect current data.

### REC-3: Remove Duplicate Line (architecture/confusables.md:29)

**Priority:** Trivial

Delete the duplicate line 29.

### REC-4: Consider Adding `confusable_codepoints` Field

**Priority:** Low

If consumers need both the character and the codepoint representation, consider adding a new field to `ConfusableInfo` in `unicode_tools.py:28-35`:

```python
class ConfusableInfo(TypedDict):
    """Information about a confusable character."""
    index: int
    char: str
    codepoint: str
    name: str
    confusable_with: str           # e.g., 'a'
    confusable_codepoint: str      # e.g., 'U+0061' - NEW
    confusable_name: str
```

### REC-5: Add Bidirectional Confusable Detection

**Priority:** Low (Feature Gap)

Currently `detect_confusables` only looks up characters from the CONFUSABLES table (characters that ARE confusable). It does NOT detect when a LATIN character could be confused with a CYRILLIC equivalent (i.e., reverse lookup).

For example, if a user passes `"paypal"` (all Latin), the function returns 0 results. But an attacker could use `"paypal"` to spoof `"pаypal"` (Cyrillic). The current implementation only catches the Cyrillic version, not the Latin original being used deceptively.

This is a design limitation to be aware of, not necessarily a bug. Full bi-directional detection would require building a reverse mapping table.

---

## Code References

| File | Lines | Description |
|------|-------|-------------|
| `nl_calc/exact/confusables.py` | 14-6579 | CONFUSABLES dict (6564 entries) |
| `nl_calc/exact/unicode_tools.py` | 152-194 | `detect_confusables()` implementation |
| `nl_calc/exact/unicode_tools.py` | 169-170 | Key lookup in CONFUSABLES |
| `nl_calc/exact/unicode_tools.py` | 175 | Character reconstruction from codepoints |
| `scripts/generate_confusables.py` | 41-73 | `parse_line()` function |
| `scripts/generate_confusables.py` | 102-133 | `generate_python_file()` function |
| `docs/exact.md` | 138-158 | Documentation of confusables module |
| `architecture/confusables.md` | 14-23 | Architecture doc data structure example |