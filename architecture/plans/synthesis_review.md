# synthesis.py Architecture Review

## Verified Claims

1. **Purpose**: Combines primitives from other exact/ modules - MATCHES (lines 1-6)
2. **`measure_text()`**: Function exists (line 168), returns MeasureTextResult - MATCHES
3. **`text_equal()`**: Function exists (line 228), returns TextEqualResult with all documented fields - MATCHES
4. **`explain_diff()`**: Function exists (line 358), returns ExplainDiffResult - MATCHES
5. **`inspect_text()`**: Function exists (line 507), returns InspectTextResult - MATCHES
6. **`count_chars()`**: Function exists (line 573), returns CountCharsResult or frequency dict - MATCHES
7. **`list_compare()`**: Function exists (line 614), returns comparison dict - MATCHES
8. **All TypedDict classes**: MeasureTextResult, TextEqualResult, ExplainDiffResult, InspectTextResult, CountCharsResult, DiffInfo, NormalizationState, UnicodeRisks - MATCHES
9. **Internal helpers**: `_classify_difference()` (line 317), `_generate_agent_instruction()` (line 492), `_codepoint_details()` (line 345) - MATCHES
10. **MAX_TEXT_LENGTH = 100_000** (line 58) - exists but not documented

## Discrepancies

1. **Parameter default mismatch**:
   - Doc says `max_diffs: int = 20` for `explain_diff()`
   - Code has `max_diffs: int = 20` (line 361) - MATCHES

2. **Classification labels mismatch - MAJOR**:
   - Doc shows: "accent_or_diacritic_difference", "compatibility_normalization_only" 
   - Code has: "case_only", "compatibility_normalization_only" (line 330, 416)
   - `accent_or_diacritic_difference` is NOT in code - code uses `case_only` instead

3. **Architecture doc shows `_classify_difference()` returns more classifications than code actually produces**

4. **MAX_TEXT_LENGTH and MAX_DIFF_SPANS not documented** (lines 58-59)

## Bugs Found

No bugs. Code is correct; documentation is slightly outdated.

## Improvements

1. **High Priority**: Update architecture doc to use correct classification labels (`case_only` not `accent_or_diacritic_difference`)
2. **Low Priority**: Document MAX_TEXT_LENGTH and MAX_DIFF_SPANS constants
3. **Low Priority**: Update architecture doc to reflect actual classification labels from `_classify_difference()`

## Priority

- **High**: Fix classification label in documentation
- **Low**: Document internal constants