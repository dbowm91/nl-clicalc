# Synthesis Module Review

## Summary

The `synthesis.py` module provides higher-level text analysis functions that combine primitives from five submodules (`primitives.py`, `unicode_tools.py`, `diff.py`, `measure.py`, `validate.py`). It offers text measurement, comparison, diff explanation, inspection, character counting, and list comparison capabilities.

---

## Verified Claims

The following claims in `architecture/synthesis.md` accurately match the implementation:

1. **Dependencies** - `synthesis.py` correctly imports from all five modules: `primitives`, `unicode_tools`, `diff`, `measure`, `validate` (lines 13-56).

2. **`MeasureTextResult` structure** - All fields documented match the implementation at `synthesis.py:78-103`.

3. **`measure_text()` function** - Implemented at `synthesis.py:168-226`, correctly combines `measure_basic`, `line_metrics`, `word_metrics`, `char_category_metrics`, `find_invisibles`, and `detect_mixed_scripts`.

4. **`text_equal()` function** - Implemented at `synthesis.py:229-310`, provides normalization, casefold, trim parameters, and returns all documented fields.

5. **`explain_diff()` function** - Implemented at `synthesis.py:353-486`, returns `ExplainDiffResult` with all documented fields including `security_findings` and `agent_instruction`.

6. **`inspect_text()` function** - Implemented at `synthesis.py:504-567`, returns `InspectTextResult` with `safe_repr`, `metrics`, `invisibles`, `scripts`, `confusables`, `warnings`.

7. **`count_chars()` function** - Implemented at `synthesis.py:570-608`, when `target` is `None` returns frequency dict, otherwise returns `CountCharsResult`.

8. **`list_compare()` function** - Implemented at `synthesis.py:611-695`, returns all documented fields including `same_ordered`, `same_unordered`, `only_in_a`, `only_in_b`, `duplicates_a`, `duplicates_b`, `near_matches`.

9. **Helper functions** - `_classify_difference()` at `synthesis.py:313-337`, `_generate_agent_instruction()` at `synthesis.py:489-501`, `_codepoint_details()` at `synthesis.py:340-350` all implemented as documented.

10. **Internal constants** - `MAX_TEXT_LENGTH = 100_000` and `MAX_DIFF_SPANS = 50` are defined as documented (lines 58-59).

---

## Issues Found

### 1. `explain_diff()` returns `equal=raw_equal` but document says nothing about this field

The `ExplainDiffResult` TypedDict includes `equal: bool` which is returned as `raw_equal` (line 468). This is a reasonable implementation but not documented. The document only specifies the structure; missing detail is not a bug per se.

### 2. `_classify_difference()` ignores `invisibles_detected` parameter

At `synthesis.py:334-335`:
```python
if invisibles_detected:
    return "invisible_character"
```
This parameter is passed from `text_equal()` (line 280) but always set to `False`, so the classification never returns `"invisible_character"`. However, `explain_diff()` has its own logic for detecting invisibles and uses `security_findings` instead of classification, so this is only a latent bug in `text_equal()`.

### 3. `list_compare()` has O(n²) complexity in near_matches detection

At `synthesis.py:656-673`, nested loops compare every pair of items:
```python
for a_item, a_t in zip(a, a_transformed, strict=True):
    for b_item, b_t in zip(b, b_transformed, strict=True):
```
For large lists this is inefficient. A more efficient approach would use set-based matching.

### 4. `count_chars()` returns inconsistent types

The docstring at line 570 says:
```python
def count_chars(...) -> CountCharsResult | dict[str, int]:
```
But at lines 591-595 when `target is None`, it returns `dict[str, int]`. The documented `CountCharsResult` has fields like `positions: list[int]` and `count: int` which only make sense when a target is specified. This is a documentation discrepancy—the implementation is correct but the return type annotation is misleading.

### 5. `measure_text()` has unimplemented parameter

At line 173:
```python
include_codepoints: If True, include detailed codepoint info (not implemented).
```
The parameter is accepted but silently ignored. This should either be implemented or the parameter removed.

### 6. Missing `normalize_unicode` import in `list_compare`

At `synthesis.py:631-637`, the `transform()` function calls `_normalize_unicode` which must be available:
```python
from .primitives import normalize_unicode as _normalize_unicode
```
Checked at line 41 - this import exists. Not a bug.

### 7. `text_equal()` classification logic inconsistency with `explain_diff()`

The two functions use different classification logic:
- `text_equal()` uses `_classify_difference()` (lines 278-281)
- `explain_diff()` has inline classification (lines 397-408)

For example, `explain_diff()` has `"compatibility_normalization_only"` classification but `_classify_difference()` does not handle NFKC differences. This means the same pair of strings could be classified differently by the two functions.

### 8. `_classify_difference()` never returns `"accent_or_diacritic_difference"` in practice

At `synthesis.py:326-328`:
```python
if nfc_equal:
    if casefold_equal:
        return "accent_or_diacritic_difference"
    return "unicode_normalization_only"
```

But in `text_equal()` at line 280, `invisibles_detected=False` is always passed. More critically, when `nfc_equal` is true but `casefold_equal` is false, it returns `"unicode_normalization_only"` - which is misleading because NFC equality means the strings are canonically equivalent, not that they differ only in normalization.

### 9. `text_equal()` returns `nfkd_equal` (line 305) but document doesn't list it

The `TextEqualResult` TypedDict at line 107 includes `nfkd_equal` which is returned at line 305, but the architecture document only mentions NFC/NFD/NFKC in the result structure. This is a documentation gap.

---

## Improvement Recommendations

### 1. Implement `include_codepoints` parameter in `measure_text()`
**File**: `synthesis.py:168-226`

Currently the parameter is accepted but ignored. Either implement it by adding codepoint details to the result, or remove the parameter and update the docstring.

### 2. Fix `invisibles_detected` being always `False` in `text_equal()`
**File**: `synthesis.py:280`

Change:
```python
classification = _classify_difference(
    raw_equal, nfc_equal, casefold_equal, byte_equal,
    len(a_work) != len(b_work), first_difference, invisibles_detected=False
)
```
To detect invisibles and pass the result:
```python
invisibles_a = _find_invisibles(a_work)
invisibles_b = _find_invisibles(b_work)
classification = _classify_difference(
    raw_equal, nfc_equal, casefold_equal, byte_equal,
    len(a_work) != len(b_work), first_difference,
    invisibles_detected=len(invisibles_a) > 0 or len(invisibles_b) > 0
)
```

### 3. Unify classification logic between `text_equal()` and `explain_diff()`
**Files**: `synthesis.py:313-337` and `synthesis.py:397-408`

The two functions use different classification schemes. Consider extracting common classification logic into a shared helper function.

### 4. Optimize `list_compare()` near_matches detection
**File**: `synthesis.py:656-673`

Current O(n²) approach can be improved by building lookup tables for casefold and NFC-normalized forms.

### 5. Clarify `count_chars()` return type
**File**: `synthesis.py:570-608`

Consider splitting into two functions: `count_char(text, target)` returning `CountCharsResult` and `char_frequency(text)` returning `dict[str, int]`, to avoid union return type confusion.

### 6. Document `nfkd_equal` in architecture
**File**: `architecture/synthesis.md`

Add `nfkd_equal: bool` to the `TextEqualResult` structure documented at lines 50-63.

### 7. Fix `_classify_difference()` accent/diacritic classification
**File**: `synthesis.py:326-328`

The condition `nfc_equal and casefold_equal` returning `"accent_or_diacritic_difference"` seems backwards. If NFC-normalized forms are equal but casefolded forms differ, the difference is likely case, not accents. Re-examine this logic.

---

## Files Referenced

| File | Purpose |
|------|---------|
| `architecture/synthesis.md` | Architecture documentation |
| `nl_calc/exact/synthesis.py` | Main synthesis module (695 lines) |
| `nl_calc/exact/primitives.py` | Low-level text primitives (287 lines) |
| `nl_calc/exact/unicode_tools.py` | Script and confusable detection (195 lines) |
| `nl_calc/exact/diff.py` | Diff algorithms (185 lines) |
| `nl_calc/exact/measure.py` | Text measurement (250 lines) |
| `nl_calc/exact/validate.py` | Validation utilities (274 lines) |
| `nl_calc/exact/confusables.py` | Confusables table (auto-generated) |