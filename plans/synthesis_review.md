# Synthesis Module Architecture Review

## Verified Claims

### Core Functions Present
- `measure_text()` - Comprehensive text measurement combining primitives
- `text_equal()` - Multi-mode string comparison with classification
- `explain_diff()` - Detailed diff explanation with security findings
- `inspect_text()` - Text inspection for hidden characters and confusables
- `count_chars()` - Character counting and frequency tables
- `list_compare()` - List comparison with near-match detection

### TypedDict Classes Match Documentation
All documented TypedDict classes are correctly defined in the code:
- `MeasureTextResult` (lines 78-103)
- `TextEqualResult` (lines 106-119)
- `ExplainDiffResult` (lines 136-145)
- `InspectTextResult` (lines 148-156)
- `CountCharsResult` (lines 159-165)

### Internal Helper Functions
- `_classify_difference()` exists (lines 317-342)
- `_generate_agent_instruction()` exists (lines 492-504)
- `_codepoint_details()` exists (lines 345-355)

### Dependencies
Documentation accurately lists dependencies: primitives, unicode_tools, diff, measure, validate.

---

## Discrepancies

### 1. `measure_text()` signature mismatch (Medium)
**Documentation**: `measure_text(text: str, include_codepoints: bool = False) -> MeasureTextResult`
**Actual**: `measure_text(text: str) -> MeasureTextResult`

The `include_codepoints` parameter is documented but not implemented.

### 2. `inspect_text()` signature mismatch (Medium)
**Documentation**: `inspect_text(text: str, include_codepoints: bool = True, include_confusables: bool = True) -> InspectTextResult`
**Actual**: Signature matches, but the `include_codepoints` parameter is never used - codepoint details are not included in invisibles regardless of this flag.

### 3. Classification values differ (Medium)
**Documentation lists**:
- `"accent_or_diacritic_difference"` - NFC equal but casefold differs

**Actual code** (`_classify_difference` line 326-342):
- `"case_only"` - casefold equal but not raw equal

The documentation describes a classification that doesn't exist in the code. The actual classification is `"case_only"`, not `"accent_or_diacritic_difference"`.

### 4. `list_compare()` near_matches description incomplete (Low)
**Documentation**: `near_matches: list[dict]  # Items that differ only by case or normalization`

**Actual**: Returns two types of matches:
- `"case_only"` - casefold matches
- `"unicode_normalization_only"` - NFC normalization matches

---

## Bugs Found

### Bug 1: `visible_repr()` Variation Selector Check Order (Priority: Low)
**Location**: `nl_calc/exact/primitives.py:273-276`

```python
elif 0xfe00 <= ord(char) <= 0xfe0f:
    result.append("⟦VS⟧")
elif unicodedata.category(char).startswith("M"):
    result.append(f"◌{char}")
```

Variation selector check comes BEFORE combining mark check. Per AGENTS.md conventions, variation selectors should be checked after combining marks. However, this is a low-level primitive issue, not synthesis.

---

## Improvements

### Improvement 1: Documented parameters not implemented
**Location**: `synthesis.py:168`
**Issue**: `include_codepoints` documented but not used
**Suggestion**: Either implement the feature or remove from documentation

### Improvement 2: `measure_text()` always returns `graphemes: None`
**Location**: `synthesis.py:193`
**Issue**: `graphemes` field is hardcoded to `None` rather than actual grapheme count
**Suggestion**: Implement grapheme counting using `unicodedata.normalize("NFD", text)` segmentation or remove from TypedDict if not implementable

### Improvement 3: `_classify_difference()` missing classification for accent/diacritic differences
**Location**: `synthesis.py:326-342`
**Issue**: The classification logic doesn't distinguish between case differences and accent-only differences
**Suggestion**: Add `"accent_or_diacritic_difference"` classification when NFC equal but casefold differs due to diacritics only

### Improvement 4: `count_chars()` documentation is sparse
**Location**: `synthesis.py:573-611`
**Issue**: The function handles "raw", "NFC", and "NFKC" per doc, but only "NFC" is explicitly used in code
**Suggestion**: Clarify normalization behavior for `count_chars()`

---

## Priority Summary

| Item | Type | Priority |
|------|------|----------|
| `include_codepoints` parameter unused in `measure_text()` | Discrepancy | Medium |
| `include_codepoints` not respected in `inspect_text()` | Discrepancy | Medium |
| Missing `accent_or_diacritic_difference` classification | Improvement | Medium |
| `graphemes: None` hardcoded value | Improvement | Low |
| `visible_repr()` check order (per conventions) | Bug | Low |
| Documentation lists non-existent function signature | Discrepancy | Medium |

---

## Summary

The synthesis module is well-structured and mostly matches its documentation. Core functions work as intended, combining lower-level primitives effectively. The main issues are:

1. **Documentation imprecision**: Some signatures don't match implementation
2. **Missing classifications**: `accent_or_diacritic_difference` is documented but not implemented
3. **Incomplete features**: `graphemes` always returns `None`, `include_codepoints` is unused

The module provides good high-level text analysis capabilities with appropriate use of lower-level exact/ primitives.