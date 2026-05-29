# unicode_tools.py Architecture Review

## Overview

Reviewed `architecture/unicode_tools.md` against the actual implementation in `nl_calc/exact/unicode_tools.py`.

---

## Verified Claims (MATCHES)

| Claim | Status | Notes |
|-------|--------|-------|
| **ScriptInfo TypedDict** | MATCHES | Fields: index, char, script, codepoint - matches exactly |
| **ConfusableInfo TypedDict** | MATCHES | Fields: index, char, codepoint, name, confusable_with, confusable_name - matches exactly |
| **unicode_script(char)** | MATCHES | Returns "Latin", "Cyrillic", etc. Examples in doc work correctly |
| **unicode_scripts(s)** | MATCHES | Returns list with one script name per character (per-character analysis) |
| **detect_mixed_scripts(s)** | MATCHES | Returns dict with mixed_scripts, scripts, positions. Ignores Common/Inherited/Other |
| **detect_confusables(s)** | MATCHES | Returns list of ConfusableInfo; document example works correctly |
| **confusables_count(s)** | MATCHES | Fast helper that counts confusables without building full list |
| **reverse_confusables(char)** | MATCHES | Function exists at line 278. Returns list of characters confusable-map TO the input |
| **Supported Scripts table** | MATCHES | All 14 scripts listed are present in _SCRIPT_RANGES (lines 56-79) |
| **Confusables Database** | MATCHES | Uses CONFUSABLES from confusables.py (~180KB data file) |
| **Data Source (UTS #39)** | MATCHES | Documented in code header (lines 7-9) and confusables.py |
| **Function Index** | MATCHES | Lists all 6 public functions including reverse_confusables |

---

## Discrepancies Found

### 1. Missing TypedDict Documentation

**Document says:** `detect_mixed_scripts()` returns a dict with mixed_scripts, scripts, positions.

**Actual code:** Returns `MixedScriptsResult` TypedDict (lines 45-52).

```python
class MixedScriptsResult(TypedDict):
    mixed_scripts: bool
    scripts: list[str]
    positions: list[ScriptInfo]
```

**Severity:** Low - TypedDict is dict-compatible, but should be documented for accuracy.

### 2. reverse_confusables() Not Described

**Document:** Listed in Index (line 228) but only as a bare reference. Not documented in Functions section.

**Code:** Function fully implemented at lines 278-303 with docstring and example.

**Severity:** Low - Function exists but lacks proper documentation in the arch document.

### 3. Dependencies Section Incomplete

**Document says:** `unicode_tools.py` depends on `primitives.py` (utf8_bytes, casefold_text).

**Actual code:** `unicode_tools.py` only imports:
- `functools` (standard library)
- `unicodedata` (standard library)
- `confusables` (local data file)

It does NOT use primitives.py directly.

**Severity:** Medium - Documentation is misleading about dependencies.

---

## Bugs Identified

### Bug 1: Security Example Code is Wrong (Severity: Medium)

**Location:** `architecture/unicode_tools.md` lines 182-187

**Document shows:**
```python
def check_domain_safety(domain: str) -> bool:
    mixed = detect_mixed_scripts(domain)
    return len(mixed) <= 1
```

**Problem:** `detect_mixed_scripts()` returns a dict with keys `mixed_scripts`, `scripts`, `positions`. Calling `len(mixed)` on a dict returns the number of keys (always 3), not the number of scripts.

**Correct implementation would be:**
```python
def check_domain_safety(domain: str) -> bool:
    mixed = detect_mixed_scripts(domain)
    return not mixed['mixed_scripts']  # or len(mixed['scripts']) <= 1
```

**Note:** This bug is in the documentation, not the code.

---

### Bug 2: Docstring Example Has Backwards Logic (Severity: Low)

**Location:** `nl_calc/exact/unicode_tools.py` line 295

**Docstring shows:**
```python
>>> "0" in reverse_confusables("O")  # digit 0 looks like letter O
```

**Problem:** The example checks if `"0"` is in `reverse_confusables("O")`, which tests if digit zero (U+0030) is confusable with letter O. But the comment says "digit 0 looks like letter O" - which is correct directionally, but the expression is checking if the INPUT char looks like the TARGET char.

Actually, looking more carefully: `reverse_confusables("O")` returns all characters that look like "O" (could be confused FOR "O"). So `"0" in reverse_confusables("O")` is correct - it asks "is digit zero one of the things that looks like letter O?"

The comment is accurate. This is not a bug, just confusing code.

**Severity:** Very Low - Code is correct, comment is confusing.

---

## Edge Cases and Potential Issues

### Edge Case 1: Empty String Handling

**Code behavior:**
- `unicode_script("")` - Would fail (raises ValueError: "char must be a single character")
- `unicode_scripts("")` - Returns empty list `[]`
- `detect_mixed_scripts("")` - Returns `{'mixed_scripts': False, 'scripts': [], 'positions': []}`
- `detect_confusables("")` - Returns empty list `[]`
- `confusables_count("")` - Returns 0

**Assessment:** Correct behavior. Empty string is a valid input for multi-character functions.

### Edge Case 2: Combining Marks

**Code behavior:** Combining marks (category M*) return "Inherited" script.

**Example:** `unicode_script("\u0301")` returns "Inherited" (combining acute).

**Assessment:** Correct per Unicode script assignment.

### Edge Case 3: Mixed Scripts with Digits/Punctuation

**Code behavior:** `detect_mixed_scripts("hello 123")` returns `mixed_scripts=False` because digits are classified as "Other" script and are excluded from the mixed-script verdict.

**Assessment:** Documented correctly - "Other" characters are excluded.

---

## Improvements Suggested

### Priority 1: Fix Security Example Code

The example in `check_domain_safety()` is broken and could mislead users. Should be:
```python
def check_domain_safety(domain: str) -> bool:
    """Check for mixed scripts in domain (common attack vector)."""
    mixed = detect_mixed_scripts(domain)
    return not mixed['mixed_scripts']
```

### Priority 2: Document reverse_confusables() Properly

Add a proper description in the Functions section:

```markdown
### `reverse_confusables(char: str) -> list[str]`

Find all characters that confusable-map TO the given character (i.e., characters that look like the input and could be confused with it).

```python
reverse_confusables("O")  # → ['0', 'Ø', 'Ο', ...]  (chars that look like O)
```

**Returns:** List of characters that are confusable with the input.

**Note:** Uses cached inverted index for performance.
```

### Priority 3: Document MixedScriptsResult TypedDict

Add to Type Definitions section:
```markdown
### MixedScriptsResult (TypedDict)

```python
class MixedScriptsResult(TypedDict):
    mixed_scripts: bool      # True if multiple scripts present
    scripts: list[str]       # Distinct scripts (excluding Common/Inherited/Other)
    positions: list[ScriptInfo]  # Position details for non-Common/Inherited/Other chars
```
```

### Priority 4: Fix Dependencies Section

Dependencies should list only:
```
Dependencies
├── confusables.py (CONFUSABLES data)
└── (standard library only: functools, unicodedata)
```

### Priority 5: Add Test Coverage

Current tests in `test_exact.py` (lines 250-276) cover:
- `detect_confusables` with Cyrillic, Greek, fullwidth, math symbols

Missing tests:
- `confusables_count` - no direct tests
- `reverse_confusables` - no tests
- `unicode_script` edge cases (combining marks, invalid input)
- `detect_mixed_scripts` with empty string

---

## Priority Summary

| Priority | Item | Severity |
|----------|------|----------|
| **High** | Fix `check_domain_safety()` example code in doc | Medium (misleads users) |
| **Medium** | Document `reverse_confusables()` properly | Low (function works, just undocumented) |
| **Medium** | Add `MixedScriptsResult` to Type Definitions | Low (dict-compatible but imprecise) |
| **Medium** | Fix Dependencies section | Low (misleading) |
| **Low** | Add tests for `confusables_count` and `reverse_confusables` | Enhancement |

---

## Conclusion

The core implementation in `unicode_tools.py` is **correct and well-structured**. All public functions work as documented. The document has minor accuracy issues (especially the security example code), but these are in the documentation, not the code itself.

**Key strengths:**
- `_get_script_heuristic` has LRU caching (line 82) for performance
- `_build_reverse_index` is cached (line 260) for reverse lookups
- All TypedDict definitions match the documented structure
- Proper handling of edge cases (empty strings, combining marks, "Other" script)

**Key issues:**
- Documentation example code for `check_domain_safety` is broken
- `reverse_confusables()` is undocumented in the Functions section
- Dependencies section incorrectly claims primitives.py is used