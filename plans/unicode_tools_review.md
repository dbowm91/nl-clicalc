# unicode_tools.py Architecture Review

## Verified Claims

### ✅ Core Functions Match Documentation
- `unicode_script()` - Returns correct script names (Latin, Cyrillic, Greek, Han, Hiragana, Katakana, Arabic, Hebrew, Devanagari, Common, Inherited, Other)
- `detect_mixed_scripts()` - Returns dict with `mixed_scripts`, `scripts`, `positions` as documented
- `detect_confusables()` - Returns list of `ConfusableInfo` dicts with index, char, codepoint, name, confusable_with, confusable_name
- `_SCRIPT_RANGES` array matches documentation exactly (lines 40-57)
- Dataclasses `ScriptInfo` and `ConfusableInfo` match the documented structure

### ✅ Data Source Citation Accurate
- Documentation correctly states confusables table is derived from Unicode Standard Annex #39
- Implementation imports from `confusables.py` which is auto-generated from `confusables.txt`

### ✅ Algorithm Description
- `detect_mixed_scripts()` correctly ignores Common and Inherited scripts for the mixed-script verdict (line 135)
- Confusable parsing correctly handles multi-codepoint substitutions (e.g., "U+00C6" → "U+0041 U+0045")

## Discrepancies

### ⚠️ unicode_script() Implementation vs Documentation

**Documentation says:** "Uses Unicode script property with heuristic fallback"

**Actual implementation:** Uses ONLY heuristic detection via `_get_script_heuristic()`. The function never calls `unicodedata.script()`.

```python
# Line 114
return _get_script_heuristic(char)
```

**Impact:** Documentation is misleading. The actual approach uses codepoint range heuristics exclusively, which is actually more reliable than `unicodedata.script()` for the supported scripts. The doc should say "Uses codepoint range heuristics" not "Unicode script property with heuristic fallback".

### ⚠️ detect_mixed_scripts() "Other" Script Handling

**Documentation doesn't mention:** The function excludes "Other" from the `mixed_scripts` count (line 135: `if script not in ("Common", "Inherited", "Other")`).

**Impact:** A string with only "Other" script characters would report `mixed_scripts: False` with empty `scripts` list. This may or may not be intentional behavior, but it's undocumented.

## Bugs Found

### 🐛 BUG: `visible_repr()` Variation Selector Check Ordering (primitives.py:273)

**Location:** `nl_calc/exact/primitives.py` line 273

**Issue:** Variation selector check (`0xfe00 <= ord(char) <= 0xfe0f`) comes AFTER the combining mark check (`unicodedata.category(char).startswith("M")`).

```python
elif 0xfe00 <= ord(char) <= 0xfe0f:  # Line 273 - VS check
    result.append("⟦VS⟧")
elif unicodedata.category(char).startswith("M"):  # Line 275 - combining mark check
    result.append(f"◌{char}")
```

**Problem:** Variation selectors are category 'Mn' (Mark, Nonspacing). The combining mark check triggers first, so VS characters get rendered as `◌char` instead of `⟦VS⟧`.

**Per AGENTS.md:** "Variation selector checks must come BEFORE combining mark checks (U+FE00-U+FE0F should be checked before category 'M')"

**Example:**
```python
>>> visible_repr("\ufe00")  # Variation selector U+FE00
'◌\ufe00'  # Wrong - should be '⟦VS⟧'
```

**Fix:** Move the VS check before the combining mark check.

### 🐛 Minor: unicode_script() No NamedTuple Return Type

**Location:** `unicode_tools.py`

**Issue:** `unicode_script()` returns `str` directly, but `ScriptInfo` is a TypedDict. The `detect_mixed_scripts()` function returns positions as `ScriptInfo` TypedDicts, but `unicode_script()` doesn't have a corresponding NamedTuple for single-character results. This is inconsistent but not a bug.

## Improvements

### 💡 IMPROVEMENT: Add `unicode_scripts()` Batch Function

**Priority:** Medium

**Rationale:** Currently `detect_mixed_scripts()` must iterate and call `_get_script_heuristic()` for every character. A batch function `unicode_scripts(s: str) -> list[str]` that returns script for every character would be more efficient and useful for testing.

### 💡 IMPROVEMENT: Expand Script Detection Coverage

**Priority:** Low

**Rationale:** Current `_SCRIPT_RANGES` only covers 11 scripts. Unicode has 150+ scripts. Notable missing scripts:
- Thai (0x0E00-0x0E7F)
- Korean Hangul (0xAC00-0xD7AF)
- Georgian (0x10A0-0x10FF)
- Armenian (0x0530-0x058F)
- Cherokee (0x13A0-0x13FF)
- Canadian Aboriginal Syllabics (0x1400-0x167F)

### 💡 IMPROVEMENT: Add Mixed-Script Threshold Option

**Priority:** Low

**Rationale:** `detect_mixed_scripts()` treats any mixing of 2+ scripts as mixed. A threshold parameter (e.g., "flag if >X% of chars are mixed") would be useful for fuzz testing where small amounts of foreign script might be legitimate.

### 💡 IMPROVEMENT: Document "Other" Script Behavior

**Priority:** Low

**Rationale:** Clarify whether strings containing only "Other" script characters should be considered "mixed_scripts: False". Add test cases for this edge case.

## Priority Summary

| Item | Type | Priority |
|------|------|----------|
| `visible_repr()` VS check ordering | Bug | **High** |
| `unicode_script()` doc accuracy | Discrepancy | Medium |
| Add batch `unicode_scripts()` function | Improvement | Medium |
| Document "Other" script behavior | Improvement | Low |
| Expand script range coverage | Improvement | Low |

## Testing Recommendations

```python
# Test VS detection ordering (should fail with current code)
from nl_calc.exact.primitives import visible_repr
result = visible_repr("\ufe00")
assert result == "⟦VS⟧", f"Expected ⟦VS⟧, got {repr(result)}"

# Test "Other" script edge case
from nl_calc.exact.unicode_tools import detect_mixed_scripts
result = detect_mixed_scripts("\uFFFF")  # Non-existent script
# Currently returns {'mixed_scripts': False, 'scripts': [], 'positions': [...]}
```