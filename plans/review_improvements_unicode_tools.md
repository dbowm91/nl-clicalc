# Unicode Tools Module Review - Improvement Plan

## Verified Claims

### Script Detection (`unicode_script`, `unicode_scripts`)
- **VERIFIED**: `unicode_script("A")` returns "Latin" (line 104-120 in code)
- **VERIFIED**: `unicode_script("Ж")` returns "Cyrillic" (line 66-101 - _get_script_heuristic)
- **VERIFIED**: `unicode_script("Ω")` returns "Greek" (line 48 - Greek range 0x0370-0x03FF)
- **VERIFIED**: `unicode_script("日")` returns "Han" (line 50 - Han range 0x4E00-0x9FFF)
- **VERIFIED**: `@lru_cache` decorator on `_get_script_heuristic` at line 66

### Mixed Script Detection (`detect_mixed_scripts`)
- **VERIFIED**: Returns correct structure with `mixed_scripts`, `scripts`, `positions` (line 135-169)
- **VERIFIED**: Properly excludes "Common", "Inherited", "Other" from verdict (line 155)
- **VERIFIED**: `detect_mixed_scripts("HelloМир")` returns `mixed_scripts: True` with both Latin and Cyrillic

### Confusable Detection (`detect_confusables`, `confusables_count`)
- **VERIFIED**: `detect_confusables("pаypal")` correctly identifies Cyrillic 'а' (U+0430) as confusable with Latin 'a'
- **VERIFIED**: Returns proper `ConfusableInfo` structure with index, char, codepoint, name, confusable_with, confusable_name
- **VERIFIED**: `confusables_count` fast path works correctly

---

## Discrepancies Between Documentation and Code

### 1. ScriptInfo TypedDict Structure (HIGH PRIORITY)

**Documentation** (`architecture/exact-unicode_tools.md`, lines 19-24):
```python
class ScriptInfo(TypedDict):
    script: str       # Script name (e.g., "Latin", "Cyrillic")
    count: int        # Number of characters in this script
    start: int        # Starting index in string
    end: int          # Ending index in string
```

**Actual Code** (`nl_calc/exact/unicode_tools.py`, lines 21-26):
```python
class ScriptInfo(TypedDict):
    index: int
    char: str
    script: str
    codepoint: str
```

**Issue**: Completely different structures. Documentation describes "run-based" info (count, start, end) but code provides "position-based" info (index, char, codepoint per character).

### 2. ConfusableInfo TypedDict Structure (HIGH PRIORITY)

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
    confusable_with: str    # Note: different field name
    confusable_name: str    # Note: different field name
```

**Issue**:
- Field `confusable_for` vs `confusable_with` - naming mismatch
- Field `confusable_codepoint` missing, replaced by `confusable_name`
- Field `script` missing entirely
- Field `index` present in code but not documented

### 3. detect_mixed_scripts Return Type (HIGH PRIORITY)

**Documentation** (`architecture/exact-unicode_tools.md`, lines 65-74):
```python
detect_mixed_scripts(s: str) -> list[ScriptInfo]
```

**Actual Code** (`nl_calc/exact/unicode_tools.py`, line 135):
```python
def detect_mixed_scripts(s: str) -> dict:
```

**Issue**: Documentation says it returns `list[ScriptInfo]` but code returns a `dict` with keys `mixed_scripts`, `scripts`, `positions`.

### 4. Script Detection Ranges (MEDIUM PRIORITY)

**Documentation** (`architecture/unicode_tools.md`, lines 111-128): Lists 13 script ranges.

**Actual Code** (`nl_calc/exact/unicode_tools.py`, lines 40-63): Lists 17 script ranges (lines 57-63 have additional: Thai, Hangul, Georgian, Armenian, Cherokee, Canadian_Aboriginal).

**Issue**: Documentation is incomplete - missing 4 scripts that code supports.

---

## Potential Bugs

### 1. confusables_count Returns Count of Matches, Not Unique Confusables

**Code** (lines 218-232):
```python
def confusables_count(s: str) -> int:
    count = 0
    for char in s:
        key = f"U+{ord(char):04X}"
        if key in CONFUSABLES:
            count += 1
    return count
```

**Issue**: If the same confusable character appears multiple times, each occurrence is counted. The function name suggests counting unique confusables. However, this may be intentional behavior - verify intended semantics.

### 2. Combining Mark Detection May Be Incomplete

**Code** (lines 82-83):
```python
if unicodedata.category(char).startswith("M"):
    return "Inherited"
```

**Issue**: Only checks category starting with "M" (Mn, Mc, Me). Combining marks can also be in other categories. Should verify if this handles all combining mark cases correctly.

### 3. Fallback to "Other" Without Trying unicodedata.script()

**Code** (line 101):
```python
return "Other"
```

**Issue**: `_get_script_heuristic` always uses range-based heuristic. It never tries `unicodedata.script()` which is the standard Python API for script detection. The docstring mentions this may not be available, but modern Python always has it. Could improve accuracy by using `unicodedata.script()` as primary and heuristic as fallback.

---

## Improvement Suggestions

### HIGH PRIORITY

1. **Update Documentation to Match Code**
   - Fix `ScriptInfo` TypedDict to match actual implementation (index, char, script, codepoint)
   - Fix `ConfusableInfo` TypedDict to match actual implementation (confusable_with, confusable_name instead of confusable_for, confusable_codepoint)
   - Change `detect_mixed_scripts` return type from `list[ScriptInfo]` to correct `dict` type

2. **Add Missing Documentation**
   - Document the additional script ranges in code (Thai, Hangul, Georgian, Armenian, Cherokee, Canadian_Aboriginal)
   - Document the actual return structure of `detect_mixed_scripts` with `mixed_scripts`, `scripts`, `positions` keys

### MEDIUM PRIORITY

3. **Improve Script Detection**
   - Consider using `unicodedata.script()` as primary detection method
   - Use heuristic only when `unicodedata.script()` returns "Unknown"
   - This would provide more accurate script detection for edge cases

4. **Add docstring Example Correction**
   - The example in `architecture/exact-unicode_tools.md` line 72-73 shows `ScriptInfo(script="Latin", count=3, start=0, end=3)` which doesn't match the actual structure

### LOW PRIORITY

5. **Performance Consideration**
   - `confusables_count` iterates character by character which is O(n) with O(1) lookups
   - Could potentially use a generator expression with sum() for slight improvement

---

## Summary

The core functionality works correctly:
- Script detection for Latin, Cyrillic, Greek, Han, etc. works as documented
- Mixed script detection works correctly
- Confusable detection works correctly

**Primary Issue**: Documentation is significantly out of sync with actual implementation. The `ScriptInfo` and `ConfusableInfo` TypedDict structures in the two documentation files describe different structures than what the code actually implements. This would cause users to write incorrect code if they followed the documentation.

**Recommendation**: Prioritize updating the documentation files to accurately reflect the actual code implementation.