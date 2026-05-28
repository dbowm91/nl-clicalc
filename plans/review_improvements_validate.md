# validate.py Module Review — Improvement Plan

**Reviewed:** architecture/validate.md against nl_calc/exact/validate.py
**Date:** 2026-05-28

## Verified Claims (with line references)

- Purpose statement ("Provides validation utilities for checking brackets, JSON syntax, and testing regex patterns") — VERIFIED at validate.py:1-5 (docs lines 3-5)
- `BracketError` TypedDict structure (char, index, line, column) — VERIFIED at validate.py:19-24 (docs lines 14-18)
- `CheckBracketsResult` TypedDict structure (balanced, unmatched_openers, unmatched_closers) — VERIFIED at validate.py:27-31 (docs lines 21-25)
- Default bracket pairs `{"(": ")", "[": "]", "{": "}", "<": ">"}` — VERIFIED at validate.py:63-68 (docs lines 28-30)
- `ValidateJsonResult` TypedDict structure (valid, error, line, column, position, type, top_level_keys) — VERIFIED at validate.py:34-42 (docs lines 46-54)
- `RegexMatch` TypedDict structure (sample, matches, fullmatch, span, groups, groupdict) — VERIFIED at validate.py:45-52 (docs lines 71-77)
- `RegexTestResult` TypedDict structure (valid_pattern, results, error) — VERIFIED at validate.py:55-59 (docs lines 80-83)
- Supported flags (IGNORECASE, MULTILINE, DOTALL, UNICODE, DEBUG, VERBOSE) — VERIFIED at validate.py:295-302 (docs line 103)
- `MAX_INPUT_LENGTH = 100_000` — VERIFIED at validate.py:14 (docs line 108)
- `MAX_PATTERN_LENGTH = 1000` — VERIFIED at validate.py:15 (docs line 109)
- `MAX_PATTERN_NESTING = 5` — VERIFIED at validate.py:16 (docs line 110)
- `check_brackets()` and `validate_json()` raise `ValueError` for oversized input — VERIFIED at validate.py:111-112, 183-184 (docs line 113)
- Error handling pattern (return result dicts rather than raise) — VERIFIED at validate.py:163-167, 210-219, 287-314 (docs lines 117-120)

## Discrepancies Between Documentation and Code

- [LOW] Parameter name `text` in docs vs `s` in code
  - Documentation says: `check_brackets(text: str, ...)` (docs line 9)
  - Code actually does: `def check_brackets(s: str, ...)` (validate.py:93)
  - Documentation says: `validate_json(text: str) -> ...` (docs line 41)
  - Code actually does: `def validate_json(s: str) -> ...` (validate.py:170)
  - Impact: Minor - parameter name differs but semantics identical

- [LOW] `regex_test` success case omits `error` field
  - Documentation example shows only `valid_pattern=True, results=[...]` for success (docs lines 89-100)
  - Code returns `RegexTestResult(valid_pattern=True, results=results)` with no `error` field on success (validate.py:344-347)
  - `error` key is absent (not `None`) in successful returns
  - Impact: Minor - JSON serialization may have different keys present vs null

- [MEDIUM] `validate_json` success return includes `top_level_keys=None` for non-objects
  - Documentation shows `type='object'` but doesn't mention top_level_keys behavior (docs lines 57-64)
  - Code returns `top_level_keys=None` when type is `array` or primitive (validate.py:195, 198)
  - Impact: Docs don't clarify that top_level_keys is only populated for objects

## Potential Bugs

- [LOW] Redundant `fullmatch` call when no match found
  - Location: `validate.py:318-328`
  - Issue: When `match` is None, `compiled.fullmatch(sample)` is never called since it's inside the else block. The code is correct here - the `fullmatch` in line 330 is only executed when `match` is not None (i.e., in the else block).
  - Actually this is NOT a bug - the code is correct. Keeping for documentation purposes only.

- [MEDIUM] Inconsistent error handling for oversized input
  - Location: `validate.py:111-112` vs `validate.py:285-291`
  - Issue: `check_brackets()` and `validate_json()` raise `ValueError` for oversized input (lines 111-112, 183-184), but `regex_test()` returns `RegexTestResult(valid_pattern=False, ...)` for pattern complexity issues including length (lines 287-291). There's no size check for samples input in `regex_test`.
  - If `samples` list is huge or individual sample strings are enormous, there's no protection.
  - Suggested investigation: Consider whether `regex_test` should also enforce MAX_INPUT_LENGTH on samples, and whether the pattern complexity error should be raised as ValueError for consistency.

- [LOW] Line/column computation called multiple times for same indices
  - Location: `validate.py:125-161`
  - Issue: In error cases, `_get_line_column` is called twice per character (once for opener, once for closer). For large inputs, this could be optimized.
  - Not a bug, just inefficiency.

## Improvement Suggestions

### MEDIUM Priority

- **Document `top_level_keys` behavior for non-object JSON**
  - Add note that `top_level_keys` is only populated for objects, returns `None` for arrays and primitives
  - This clarifies the semantics of the `ValidateJsonResult` return value

- **Consistent error handling approach**
  - Consider having `regex_test` raise `ValueError` for oversized patterns (like `check_brackets` and `validate_json` do) for consistency
  - Or document that `regex_test` returns error results instead of raising for pattern issues

### LOW Priority

- **Add `MAX_SAMPLE_LENGTH` for regex_test**
  - `regex_test` doesn't check if individual samples exceed any length limit
  - Consider adding protection against very long sample strings

- **Parameter name alignment** (cosmetic)
  - Docs use `text` parameter name but code uses `s`
  - Either is acceptable; suggest aligning docs to code (`s`) since it's a common short name in this codebase

- **Document that regex_test returns results for all samples regardless of match**
  - The function always returns a results list with one entry per sample, with `matches: False` for non-matches
  - This is implicit in the structure but could be clearer

## Summary

The validate.md documentation is accurate and comprehensive. All public functions, TypedDicts, and constants are correctly documented. The main discrepancies are minor (parameter name `s` vs `text`) and the success case omission of the `error` key in `RegexTestResult`. The code has no critical bugs. The primary improvement opportunity is clarifying the inconsistency in error handling approaches between functions and documenting the `top_level_keys` behavior for non-object JSON values.