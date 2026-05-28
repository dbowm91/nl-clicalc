# Synthesis Module Review — Improvement Plan

**Reviewed:** architecture/synthesis.md against nl_calc/exact/synthesis.py
**Date:** 2026-05-28

## Verified Claims (with line references)

- `measure_text()` function signature and return type — VERIFIED at synthesis.py:171-229
- `text_equal()` function signature and return type — VERIFIED at synthesis.py:232-318
- `explain_diff()` function signature and return type — VERIFIED at synthesis.py:366-495
- `inspect_text()` function signature and return type — VERIFIED at synthesis.py:515-578
- `count_chars()` function signature and return type — VERIFIED at synthesis.py:581-619
- `list_compare()` function signature and return type — VERIFIED at synthesis.py:622-727
- `MeasureTextResult` TypedDict — VERIFIED at synthesis.py:81-106
- `TextEqualResult` TypedDict — VERIFIED at synthesis.py:109-122
- `ExplainDiffResult` TypedDict — VERIFIED at synthesis.py:139-148
- `InspectTextResult` TypedDict — VERIFIED at synthesis.py:151-159
- `CountCharsResult` TypedDict — VERIFIED at synthesis.py:162-168
- `_classify_difference()` function — VERIFIED at synthesis.py:321-350
- `_generate_agent_instruction()` function — VERIFIED at synthesis.py:498-512
- `_codepoint_details()` function — VERIFIED at synthesis.py:353-363
- `MAX_TEXT_LENGTH` constant (100,000) — VERIFIED at synthesis.py:61
- Dependencies (primitives, unicode_tools, diff, measure, validate) — VERIFIED at synthesis.py:13-59

## Discrepancies Between Documentation and Code

- [LOW] `count_chars()` return documentation incomplete
  - Documentation says: Returns `CountCharsResult` when `target` is specified, otherwise returns a frequency dictionary (synthesis.md:102-115)
  - Code actually does: Returns `CountCharsResult | dict[str, int]` with proper type union (synthesis.py:585)
  - Impact: Minor — documentation describes behavior correctly but doesn't show the union type in signature

## Potential Bugs

- [HIGH] `_classify_difference()` unreachable branch for `"accent_or_diacritic_difference"`
  - Location: `synthesis.py:337-338`
  - Issue: When `nfc_equal=True` and `byte_equal=False`, code returns `"accent_or_diacritic_difference"` if `casefold_equal=False`. However, this branch is unreachable because Python's `str.casefold()` internally applies NFC normalization. If two strings are NFC-equal, their casefold versions will also be equal.
  - Analysis: If `nfc_equal=True`, then `casefold(_normalize(a, "NFC")) == casefold(_normalize(b, "NFC"))`. Since NFC normalization is idempotent, `casefold(a)` and `casefold(b)` will match. Thus `casefold_equal=False` is impossible when `nfc_equal=True`.
  - Test that would confirm: `text_equal("café", "CAFÉ", normalization="NFC")` should return `classification="case_only"` not `"accent_or_diacritic_difference"`
  - Suggested investigation: Add test and verify classification for "café" vs "CAFÉ" — the branch at line 337-338 is dead code

- [HIGH] `list_compare()` near_matches `"unicode_normalization_only"` classification is unreachable
  - Location: `synthesis.py:704-714`
  - Issue: The code logic for detecting `"unicode_normalization_only"` near_matches iterates through `norm_groups` where keys are NFC-normalized strings. If two different strings normalize to the same NFC form, they will be:
    1. In the same group (norm_groups)
    2. Treated as equivalent when computing `a_set == b_set`
    3. Matched as normal equivalents, not "near matches"
  - The near_matches dictionary only captures items that are "close but not equivalent". Items that normalize to identical NFC forms ARE equivalent, so they never appear as near_matches.
  - Suggested investigation: Trace `list_compare(["café"], ["cafe\u0301"], ignore_order=True)` — items normalize to same NFC and are treated as matches, not near_matches

## Improvement Suggestions

### HIGH Priority

1. **Remove dead code in `_classify_difference()` (synthesis.py:337-338)**
   - The `"accent_or_diacritic_difference"` branch when `nfc_equal=True` is unreachable
   - Since NFC equality implies casefold equality, this case can never trigger
   - Either remove the branch or clarify the intended logic

2. **Clarify or remove `list_compare()` near_matches `"unicode_normalization_only"` logic**
   - The logic at lines 704-714 cannot be triggered through normal usage
   - When items normalize to the same NFC form, they are matched as equivalents, not near_matches
   - Consider either removing this classification or documenting that it only triggers for items already in `norm_groups` but not matched via casefold

### MEDIUM Priority

3. **Add test for `text_equal("café", "CAFÉ")` classification**
   - Verify correct classification when strings differ by both case and diacritics
   - Current test at test_exact.py:585-590 shows the classification can be either "unicode_normalization_only" or "accent_or_diacritic_difference"

4. **Add test for `explain_diff("hello!", "hello")` vs `explain_diff("hello", "hello!")`**
   - Current test at test_exact.py:600-602 shows `"hello!"` vs `"hello"` returns `"length_only"`
   - Verify symmetry — the shorter string should also classify as `"length_only"`

### LOW Priority

5. **Document `count_chars()` return type union more clearly**
   - Consider adding explicit union type annotation in documentation

6. **Add `return TextEqualResult` type annotation to `text_equal()`**
   - Code uses TypedDict but function lacks return type annotation (line 238)

## Summary

The synthesis module documentation is generally accurate with all major functions properly documented. The code correctly implements the documented behavior with proper TypedDict definitions and well-structured helper functions. Two logical issues exist: (1) an unreachable branch in `_classify_difference()` where the `"accent_or_diacritic_difference"` classification can never occur when `nfc_equal=True` due to casefold applying NFC internally, and (2) unreachable `unicode_normalization_only` near_match logic in `list_compare()` that cannot trigger because items normalizing to the same NFC form are already treated as equivalents. The module is well-tested but could benefit from additional edge case coverage for string classification scenarios involving combined case and diacritic differences.
