# Unicode Tools Code Review

## Summary

The `unicode_tools.py` module provides functions to detect Unicode scripts and identify confusable homoglyph characters that could be used for spoofing attacks (e.g., Cyrillic 'а' vs Latin 'a').

**Core Functions:**
- `unicode_script(char: str) -> str` - Determines the Unicode script of a single character
- `detect_mixed_scripts(s: str) -> dict` - Detects mixed-script strings
- `detect_confusables(s: str) -> list[ConfusableInfo]` - Detects confusable homoglyph characters

**Dependencies:**
- `unicodedata` - Standard library for Unicode data
- `confusables` - Confusables table from `exact/confusables.py`

---

## Verified Claims

The following claims in `architecture/unicode_tools.md` match the actual implementation:

### 1. Function Signatures
- `unicode_script(char: str) -> str` - Matches implementation at `nl_calc/exact/unicode_tools.py:98`
- `detect_mixed_scripts(s: str) -> dict` - Matches implementation at `nl_calc/exact/unicode_tools.py:117`
- `detect_confusables(s: str) -> list[ConfusableInfo]` - Matches implementation at `nl_calc/exact/unicode_tools.py:152`

### 2. Return Type Structures
- `ScriptInfo` TypedDict with fields `index: int`, `char: str`, `script: str`, `codepoint: str` - Matches `nl_calc/exact/unicode_tools.py:20-25`
- `ConfusableInfo` TypedDict with fields `index: int`, `char: str`, `codepoint: str`, `name: str`, `confusable_with: str`, `confusable_name: str` - Matches `nl_calc/exact/unicode_tools.py:28-35`

### 3. Script Names Returned
The documented script names (Latin, Cyrillic, Greek, Han, Hiragana, Katakana, Arabic, Hebrew, Devanagari, Common, Inherited, Other) are correctly returned by the implementation.

### 4. Unicode Examples
The documented examples for `unicode_script`:
```python
>>> unicode_script("A")  # Returns 'Latin' ✓
>>> unicode_script("Ж")  # Returns 'Cyrillic' ✓
>>> unicode_script("Ω")  # Returns 'Greek' ✓
>>> unicode_script("日") # Returns 'Han' ✓
```

### 5. Basic Mixed Script Detection
The `detect_mixed_scripts` function correctly:
- Returns `mixed_scripts: True` when multiple scripts are present
- Excludes Common and Inherited scripts from the mixed-script verdict
- Returns script positions with codepoints in "U+XXXX" format

### 6. Data Source
The confusables table is correctly noted as being derived from Unicode Standard Annex #39, generated from `confusables.txt` via `scripts/generate_confusables.py`.

---

## Issues Found

### BUG 1: Incorrect Example in Documentation (Minor)

**Location:** `architecture/unicode_tools.md:75-84`

**Issue:** The `detect_confusables("pаypal")` example in the documentation shows TWO confusables detected:
```python
[{'index': 1, 'char': 'а', 'codepoint': 'U+0430',
  'name': 'CYRILLIC SMALL LETTER A',
  'confusable_with': 'a',
  'confusable_name': 'LATIN SMALL LETTER A'},
 {'index': 2, 'char': 'y', 'codepoint': 'U+0443',
  'name': 'CYRILLIC SMALL LETTER YERU',
  'confusable_with': 'y',
  'confusable_name': 'LATIN SMALL LETTER Y'}]
```

**Reality:** Only ONE confusable is detected at index 1. The Latin 'y' at index 2 (U+0079) is NOT a confusable - the table maps U+0443 (Cyrillic y) to U+0079, but the character 'y' in "pаypal" is already Latin.

**Recommended Fix:** Update the example to use a string with actual Cyrillic 'у' at the position being documented, or update to show only the single confusable that is actually detected.

### BUG 2: `detect_mixed_scripts` Returns All Positions, Not Just Non-Common/Inherited

**Location:** `architecture/unicode_tools.md:36-37`

**Issue:** The documentation states:
```
"positions": list[ScriptInfo]  # Positions of non-Common/Inherited chars
```

**Reality:** The implementation at `nl_calc/exact/unicode_tools.py:117-149` returns ALL character positions, not just non-Common/Inherited ones. Looking at the code:

```python
for index, char in enumerate(s):
    script = _get_script_heuristic(char)
    if script not in ("Common", "Inherited", "Other"):
        scripts.add(script)
        codepoint_str = f"U+{ord(char):04X}"
        positions.append(ScriptInfo(...))
```

This means `positions` only contains non-Common/Inherited/Other characters, which is actually correct behavior. However, the documentation example shows only Cyrillic positions in the output while Latin positions are omitted - this is the documented example being incomplete/incorrect, not the implementation.

### ISSUE 3: `detect_mixed_scripts` Documentation Example Incomplete

**Location:** `architecture/unicode_tools.md:50-55`

**Issue:** The documented example shows:
```python
>>> detect_mixed_scripts("HelloМир")
{'mixed_scripts': True, 'scripts': ['Latin', 'Cyrillic'],
 'positions': [{'index': 5, 'char': 'М', 'script': 'Cyrillic', 'codepoint': 'U+041C'},
              {'index': 6, 'char': 'и', 'script': 'Cyrillic', 'codepoint': 'U+0438'},
              {'index': 7, 'char': 'р', 'script': 'Cyrillic', 'codepoint': 'U+0440'}]}
```

**Reality:** The actual implementation returns positions for ALL non-Common/Inherited characters (including all Latin letters), but the documentation only shows Cyrillic positions. The documentation is incomplete.

### ISSUE 4: Documentation Script Ranges Missing Ranges Present in Implementation

**Location:** `architecture/unicode_tools.md:93-109`

**Issue:** The documented `_SCRIPT_RANGES` does not include:
- `(0x0500, 0x052f, "Cyrillic")` - Present in implementation at `nl_calc/exact/unicode_tools.py:46`
- `(0x0401, 0x0401, "Cyrillic")` - Present but redundant (duplicate of 0x0400-0x04ff) at `nl_calc/exact/unicode_tools.py:56`
- `(0x0451, 0x0451, "Cyrillic")` - Present but redundant (duplicate of 0x0400-0x04ff) at `nl_calc/exact/unicode_tools.py:57`

**Recommended Fix:** Update documentation to include the `(0x0500, 0x052f, "Cyrillic")` range and remove the redundant single-codepoint duplicates.

### ISSUE 5: Missing Test Coverage for `unicode_script` with "Common" Script

**Location:** `tests/test_exact.py:190-268`

**Issue:** No test exists for characters that return "Common" from `unicode_script`. Example:
```python
>>> unicode_script("3")  # Should return "Other" since digits aren't in ranges
>>> unicode_script(".")  # Should return "Other"
>>> unicode_script("-")  # Should return "Other"
```

**Recommended Fix:** Add test cases for Common script characters if they're meant to be detected, or clarify expected behavior.

### ISSUE 6: `detect_confusables` Does Not Handle Mixed-Character Confusables

**Location:** `nl_calc/exact/unicode_tools.py:152-195`

**Issue:** The confusables table contains entries like `"U+00A2": "U+0063 U+0338"` where a single character maps to multiple characters. The `confusable_with` field returns a string like "c̸" but there's no indication that this is a multi-character confusable vs. a single character.

**Recommended Fix:** Consider adding a field like `is_multicharacter_substitution: bool` to help consumers understand that the confusable maps to multiple characters.

---

## Improvement Recommendations

### REC 1: Fix `detect_confusables` Example Documentation
**File:** `architecture/unicode_tools.md:75-84`

Update the example to show actual behavior. The example string "pаypal" only contains one confusable character (Cyrillic 'а' at index 1). Either:
- Use a string with actual Cyrillic 'у' to show a two-confusable example, OR
- Update the expected output to show only one result

### REC 2: Update `detect_mixed_scripts` Example Documentation
**File:** `architecture/unicode_tools.md:50-55`

Update the example to show all positions (including Latin characters) or document clearly that only mixed-script characters are shown. The current output is misleading as it shows only Cyrillic positions while the function returns positions for all non-Common/Inherited characters.

### REC 3: Add Missing Cyrillic Range to Documentation
**File:** `architecture/unicode_tools.md:93-109`

Add `(0x0500, 0x052f, "Cyrillic")` to match implementation. Remove redundant single-codepoint entries.

### REC 4: Add Test for "Other" Script Category
**File:** `tests/test_exact.py`

Add test case for characters that fall into the "Other" category:
```python
def test_unicode_script_other(self):
    assert unicode_script("☮") == "Other"
    assert unicode_script("★") == "Other"
```

### REC 5: Document Expected Behavior for Digits and Punctuation
The current behavior classifies digits (0-9) as "Other" since they're not in any script range. The documentation should clarify this or consider adding a numeric/symbol detection.

### REC 6: Consider Performance Optimization
**File:** `nl_calc/exact/unicode_tools.py`

The `_get_script_heuristic` function is called for every character in `detect_mixed_scripts`. Consider:
- Using `functools.lru_cache` on `_get_script_heuristic` to memoize results for repeated characters
- The function is called frequently when processing long strings with repeated scripts

---

## Conclusion

The unicode tools implementation is functionally correct and matches the documented API signatures. The main issues are:
1. Documentation examples are incorrect/incomplete
2. Script ranges in documentation don't fully match implementation
3. No test coverage for "Other" script category

The implementation appears stable and well-structured, following the standard library constraint. The confusables table is comprehensive and derived from the official Unicode source.