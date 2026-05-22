# Synthesis Module Review

## Verified Claims

### Architecture Doc Accurate
- **Module location** (`nl_calc/exact/synthesis.py`) - Correct
- **Dependencies** - All imports from primitives, unicode_tools, diff, measure, validate are accurate
- **Purpose** - Provides higher-level text inspection, comparison, and measurement - Correct

### TypedDicts Match Implementation
- `MeasureTextResult` - Fields match implementation (lines 81-106)
- `TextEqualResult` - Fields match implementation (lines 109-122)
- `ExplainDiffResult` - Fields match implementation (lines 139-148)
- `InspectTextResult` - Fields match implementation (lines 151-159)
- `CountCharsResult` - Fields match implementation (lines 162-168)

### Core Functions Implemented
- `measure_text()` - Implemented at line 171
- `text_equal()` - Implemented at line 232
- `explain_diff()` - Implemented at line 364
- `inspect_text()` - Implemented at line 513
- `count_chars()` - Implemented at line 579
- `list_compare()` - Implemented at line 620

### Internal Helpers Implemented
- `_classify_difference()` - Implemented at line 321
- `_generate_agent_instruction()` - Implemented at line 498
- `_codepoint_details()` - Implemented at line 351

## Discrepancies

### Doc Claims `graphemes: None` But Implementation Returns `int`
**Architecture doc** (line 19): `graphemes: None`

**Implementation** (line 85): `graphemes: int`

The doc incorrectly shows `graphemes: None` but `measure_text()` returns `graphemes=grapheme_count` (line 197) where `_count_graphemes()` returns `int` (primitives.py:291).

### Doc Missing `include_codepoints` Parameter Default
**Architecture doc** (line 11): `measure_text(text: str, include_codepoints: bool = False)`

**Implementation** (line 171): `def measure_text(text: str)` - No `include_codepoints` parameter exists.

The `include_codepoints` parameter is not used in the implementation. The doc signature is incorrect.

## Bugs Found

### Bug 1: `_classify_difference` Logic Error (Medium Priority)
**Location**: `synthesis.py:321-348`

The function checks `casefold_equal` at line 334 and returns `"case_only"`, but then at line 337 checks `nfc_equal` again. However, if `casefold_equal` is True but `nfc_equal` is False, it will return `"accent_or_diacritic_difference"` at line 339, which is incorrect - casefold being equal means no case difference, so returning `"case_only"` at line 334 is correct but the subsequent check for `nfc_equal` when `casefold_equal` is True is unreachable code.

**Problem**: The logic flow is:
1. If `raw_equal` → `"exact_match"` ✓
2. If `casefold_equal` → `"case_only"` (returns immediately) ✓
3. If `nfc_equal` but `not casefold_equal` → `"accent_or_diacritic_difference"`
4. If `nfc_equal` and `casefold_equal` → `"unicode_normalization_only"` (unreachable)

**Impact**: The `"unicode_normalization_only"` classification is unreachable via normal flow since we already returned on `casefold_equal` at line 334. However, if called directly with `casefold_equal=True` passed as a parameter, this could cause issues.

### Bug 2: `explain_diff` Overwrites `same_length_codepoints` (Low Priority)
**Location**: `synthesis.py:392, 414`

Line 392 sets `same_length_codepoints = len(a) == len(b)` and line 414 sets it again, making line 392 redundant.

### Bug 3: `_generate_agent_instruction` Missing `"accent_or_diacritic_difference"` Case (Medium Priority)
**Location**: `synthesis.py:498-510`

The function does not handle `"accent_or_diacritic_difference"` classification. When a string has NFC equal but casefold differs, `_classify_difference` returns `"accent_or_diacritic_difference"`, but `_generate_agent_instruction` falls through to the generic return at line 510.

**Fix needed**: Add case for `"accent_or_diacritic_difference"`.

### Bug 4: `list_compare` May Return Duplicate Near Matches (Medium Priority)
**Location**: `synthesis.py:689-705`

When an item matches both by casefold AND normalization, it can appear in `near_matches` twice with different classifications. The `seen_pairs` set deduplicates by value but doesn't prevent one item from appearing in multiple matches with different items.

## Improvements

### High Priority

1. **Add missing `"accent_or_diacritic_difference"` case to `_generate_agent_instruction`**
   - Location: `synthesis.py:498-510`
   - Suggestion: Add handling for this classification to provide useful agent instructions

2. **Fix architecture doc: `graphemes` type is `int`, not `None`**
   - Location: `architecture/synthesis.md:19`
   - Change `graphemes: None` to `graphemes: int`

3. **Remove unused `include_codepoints` parameter from doc or implement it**
   - Location: `architecture/synthesis.md:11`
   - Either remove from doc signature or implement the functionality

### Medium Priority

4. **Remove redundant assignment in `explain_diff`**
   - Location: `synthesis.py:414`
   - Remove duplicate `same_length_codepoints = len(a) == len(b)`

5. **Consider adding `accent_or_diacritic_difference` handling in `explain_diff`**
   - Location: `synthesis.py:421-422`
   - Current logic sets `"compatibility_normalization_only"` but should also handle accent/diacritic classification

6. **Add tests for `_classify_difference` edge cases**
   - Particularly `"unicode_normalization_only"` which appears unreachable through normal flow

### Low Priority

7. **Consider adding docstring with example to `_codepoint_details`**
   - Location: `synthesis.py:351-361`
   - Function is used internally but could benefit from documentation

8. **Add type annotation for `DiffInfo` in `explain_diff` return**
   - Currently `diffs: list[DiffInfo]` but the intermediate `diffs_raw` uses generic dict
   - This is fine but could be clearer

## Summary

The synthesis module is well-structured and mostly matches its architecture documentation. The main issues are:
1. Doc/implementation mismatch on `graphemes` type
2. Unused `include_codepoints` parameter in doc
3. Missing case in `_generate_agent_instruction` 
4. Logic flow issue in `_classify_difference` making one classification unreachable