# synthesis.py Architecture Review

## Document: synthesis.md

## Verified Claims
| Claim | Status | Evidence |
|-------|--------|----------|
| `measure_text(text: str) -> MeasureTextResult` exists | VERIFIED | synthesis.py:267 |
| `text_equal` function exists | VERIFIED | synthesis.py:342 |
| `explain_diff` function exists | VERIFIED | synthesis.py:531 |
| `inspect_text` function exists | VERIFIED | synthesis.py:702 |
| `count_chars` function exists | VERIFIED | synthesis.py:889 |
| `list_compare` function exists | VERIFIED | synthesis.py:985 |
| `text_window` function exists | VERIFIED | synthesis.py:1107 |
| `_classify_difference` internal function exists | VERIFIED | synthesis.py:453 |
| `_generate_agent_instruction` internal function exists | VERIFIED | synthesis.py:682 |
| `_codepoint_details` internal function exists | VERIFIED | synthesis.py:485 |
| Dependencies from primitives, unicode_tools, diff, measure | VERIFIED | synthesis.py:14-60 |
| Combines primitives from listed modules | VERIFIED | synthesis.py:14-60 |
| `_classify_difference` returns documented classification strings | VERIFIED | synthesis.py:462-482 |
| `text_equal` returns `TextEqualResult` with documented fields | PARTIAL | synthesis.py:430-450 - mode dict has undocumented extra keys |
| `MeasureTextResult` TypedDict fields (bytes_utf8, codepoints, graphemes, etc.) | VERIFIED | synthesis.py:82-108 |
| `TextEqualResult` TypedDict fields (equal, mode, raw_equal, nfc_equal, etc.) | VERIFIED | synthesis.py:111-125 |
| `ExplainDiffResult` TypedDict fields (equal, classification, summary, diffs, etc.) | VERIFIED | synthesis.py:141-151 |
| `CountCharsResult` TypedDict fields (target, normalization, count, positions) | VERIFIED | synthesis.py:186-193 |
| `ListCompareResult` TypedDict fields (same_ordered, same_unordered, only_in_a, only_in_b, near_matches) | VERIFIED | synthesis.py:222-231 |
| `TextWindowPosition` TypedDict fields (byte_offset, codepoint_index, grapheme_index, line, column) | VERIFIED | synthesis.py:1086-1093 |
| `TextWindowResult` TypedDict fields (position, line_text, before, after, newline_style, at_codepoint, warnings) | VERIFIED | synthesis.py:1095-1104 |

## Discrepancies

### 1. [MISMATCH] Dependencies claimed but not used
- **Document states**: "synthesis.py combines functions from... validate - Validation utilities"
- **Code actually**: `synthesis.py` does NOT import from `validate.py`. The imports (lines 14-60) include primitives, unicode_tools, diff, and measure only.

### 2. [MISMATCH] MeasureTextResult missing field in documentation
- **Document states**: `MeasureTextResult` fields (lines 16-40) do not include `warnings: list[str]`
- **Code actually**: `MeasureTextResult` includes `warnings: list[str]` field at line 108

### 3. [MISMATCH] text_equal undocumented parameters
- **Document states**: `text_equal(a: str, b: str, normalization: str = "raw", casefold: bool = False, trim: bool = False) -> TextEqualResult`
- **Code actually**: Function has additional parameters `ignore_newline_style: bool = False`, `ignore_trailing_whitespace: bool = False`, `ignore_final_newline: bool = False` (lines 348-350)

### 4. [MISMATCH] explain_diff missing parameter and return field
- **Document states**: `explain_diff(a: str, b: str, max_diffs: int = 20, include_codepoints: bool = True, include_context: bool = True)`
- **Code actually**: `include_context` parameter does not exist; replaced with `detail: str = "normal"` (line 537). Also missing `limits_applied` field in return type.

### 5. [MISMATCH] inspect_text undocumented parameters
- **Document states**: `inspect_text(text: str, include_codepoints: bool = True, include_confusables: bool = True) -> InspectTextResult`
- **Code actually**: Has additional parameters `detail: str = "normal"`, `normalize: str = "none"`, `compare_normalized: bool = False` (lines 706-708)

### 6. [MISMATCH] InspectTextResult missing many fields in documentation
- **Document states**: `InspectTextResult` fields (lines 104-114): `safe_repr`, `metrics`, `normalization`, `invisibles`, `scripts`, `confusables`, `bidi_controls`, `normalization_findings`, `warnings`
- **Code actually**: Additional undocumented fields: `normalization_diff`, `normals_repr`, `mixed_scripts`, `limits_applied`, `normalize`, `compare_normalized`, `original`, `normalized`, `normalization_findings` (lines 166-183)
- **Also**: Document shows `scripts: dict[str, Any]` but code has `mixed_scripts: dict[str, Any]` - different field name

### 7. [MISMATCH] InspectTextNormalized missing safe_repr field
- **Document states**: `InspectTextNormalized` fields (lines 116-121): `form`, `text`, `changed`, `diff`
- **Code actually**: Also has `safe_repr: str` field (line 157)

### 8. [MISMATCH] count_chars undocumented count_mode parameter
- **Document states**: `count_chars(text: str, target: str | None = None, normalization: str = "raw") -> CountCharsResult | dict[str, int]`
- **Code actually**: Has additional parameter `count_mode: str = "codepoint"` (line 893) which affects behavior significantly

### 9. [MISMATCH] list_compare undocumented trim parameter
- **Document states**: `list_compare(a: list[str], b: list[str], ignore_order: bool = True, casefold: bool = False, normalization: str = "NFC", treat_as_multiset: bool = True, include_near_matches: bool = False, near_match_threshold: int = 2)`
- **Code actually**: Has additional `trim: bool = False` parameter (line 991)

### 10. [MISMATCH] ListCompareOrderedResult, ListCompareSetResult, ListCompareMultisetResult are unused TypedDicts
- **Document states**: Document shows `ListCompareOrderedResult`, `ListCompareSetResult`, `ListCompareMultisetResult` as part of list_compare documentation (lines 162-177)
- **Code actually**: These TypedDicts are defined in code (lines 195-213) but are NOT returned by `list_compare`. The function only returns `ListCompareResult`. These appear to be design artifacts or planned but unimplemented features.

### 11. [MISMATCH] text_window position parameter not fully documented
- **Document states**: `text_window(text: str, position: dict, context_lines: int = 2, include_visible_repr: bool = True)`
- **Code actually**: `position` dict supports multiple `kind` values (`byte_offset`, `codepoint_index`, `grapheme_index`, `line_column`), `line_base`, `column_base` parameters that are not documented (lines 1158-1224)

### 12. [MISSING] _truncate_diff_spans not documented
- **Document states**: Lists only `_classify_difference`, `_generate_agent_instruction`, `_codepoint_details` as internal helpers (lines 213-229)
- **Code actually**: `_truncate_diff_spans` function exists at lines 498-528 but is not documented

### 13. [MISSING] _detect_special_sequences not documented
- **Code actually**: `_detect_special_sequences` function exists at lines 233-264 but is not documented at all in the architecture document

### 14. [MISSING] Three major functions completely undocumented
- **Code actually**: The following functions exist but are NOT mentioned in the architecture document at all:
  - `text_replace_check` (lines 1309-1508)
  - `line_range_extract` (lines 1515-1672)
  - `line_range_compare` (lines 1679-1788)

## Bugs Identified

| Bug | Location | Severity | Description |
|-----|----------|----------|-------------|
| Incorrect list comprehension for bidi omitted count | synthesis.py:790 | Medium | Code `[b for b in bidi_controls if b in warnings]` checks if dict objects are in warnings list, but warnings contains different dict instances (created fresh at lines 767-773). This will always be False, making `total_bidi_omitted` always equal `len(bidi_controls)` rather than the actual count omitted. |
| Unused TypedDict classes | synthesis.py:195-213 | Low | `ListCompareOrderedResult`, `ListCompareSetResult`, `ListCompareMultisetResult` are defined but never returned by any function. These appear to be design artifacts that were planned but never integrated. |

## Improvements Surface

| Area | Priority | Description |
|------|----------|-------------|
| Documentation | High | The architecture document is missing documentation for 3 major functions (`text_replace_check`, `line_range_extract`, `line_range_compare`) and several undocumented parameters across multiple functions. The document is significantly out of sync with the implementation. |
| Dead Code | Medium | `ListCompareOrderedResult`, `ListCompareSetResult`, `ListCompareMultisetResult` TypedDicts are defined but never used. Either remove them or implement the functionality they were designed for. |
| Bug Fix | Medium | The `total_bidi_omitted` calculation at line 790 is logically incorrect. It should compare counts of items that were truncated vs kept, not check dict identity. |
| Consistency | Medium | `InspectTextResult` has different field names between doc (`scripts`) and code (`mixed_scripts`). The `unicode_risks` structure in `MeasureTextResult` contains `scripts` as a list, while `InspectTextResult` has `mixed_scripts` as a dict - inconsistent naming. |
| Documentation | Low | The `_detect_special_sequences` helper at lines 233-264 is undocumented but provides useful metrics about combining marks, ZWJ sequences, variation selectors, etc. Consider documenting or moving to a more prominent location. |

## Notes

1. The architecture document at `architecture/synthesis.md` appears to be significantly outdated. The implementation has grown beyond the documented functions, particularly with the addition of `text_replace_check`, `line_range_extract`, and `line_range_compare`.

2. The `detail` parameter replaces `include_context` in `explain_diff` but retains similar functionality through the `max_equal_context` mechanism. The document should be updated to reflect this parameter rename.

3. The `_truncate_diff_spans` helper function at lines 498-528 is an internal implementation detail not documented, but it properly handles truncation of diff spans with context limiting.

4. The `count_mode` parameter in `count_chars` is a significant feature addition not present in the original design, enabling grapheme-based and byte-based counting in addition to codepoint-based.

5. The `inspect_text` function has grown significantly with `normalize`, `compare_normalized`, and related fields to support normalization analysis - these are useful additions that should be documented.

6. The dependencies section claims `validate.py` is used, but no imports from validate exist in the code. This appears to be an error in the documentation.
