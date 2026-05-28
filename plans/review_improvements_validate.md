# validate Module Review — Improvement Plan

**Reviewed:** architecture/validate.md against nl_calc/exact/validate.py
**Date:** 2026-05-28

## Verified Claims (with line references)

1. **check_brackets()** - validate.py:92-167
   - Returns `CheckBracketsResult` with `balanced`, `unmatched_openers`, `unmatched_closers`
   - Default bracket pairs `{"(": ")", "[": "]", "{": "}", "<": ">"}` (lines 63-68) - MATCHES docs
   - Raises `ValueError` when input exceeds MAX_INPUT_LENGTH (line 111-112) - MATCHES docs

2. **validate_json()** - validate.py:170-219
   - Returns `ValidateJsonResult` with `valid`, `error`, `line`, `column`, `position`, `type`, `top_level_keys`
   - Raises `ValueError` when input exceeds MAX_INPUT_LENGTH (line 183-184) - MATCHES docs
   - Returns `top_level_keys` for objects (line 207) - MATCHES docs

3. **regex_test()** - validate.py:269-347
   - Returns `RegexTestResult` with `valid_pattern`, `results`, `error`
   - `RegexMatch` TypedDict with `sample`, `matches`, `fullmatch`, `span`, `groups`, `groupdict` (lines 45-52) - MATCHES docs

4. **MAX_INPUT_LENGTH = 100_000** (line 14) - MATCHES docs:108

5. **MAX_PATTERN_LENGTH = 1000** (line 15) - MATCHES docs:109

6. **MAX_PATTERN_NESTING = 5** (line 16) - MATCHES docs:110

7. **Supported flags** - validate.py:295-302
   - IGNORECASE, MULTILINE, DOTALL, UNICODE, DEBUG, VERBOSE
   - Documentation line 103 shows: IGNORECASE, MULTILINE, DOTALL, UNICODE, DEBUG, VERBOSE
   - ACTUAL: `ASCII` is NOT in code, `UNICODE` and `DEBUG` ARE in code - DISCREPANCY

## Discrepancies Between Documentation and Code

- [MEDIUM] **Flag name mismatch - `ASCII` vs `UNICODE`**
  - Documentation says (validate.md:103): `ASCII` is a supported flag
  - Code actually does (validate.py:299): Has `UNICODE` instead
  - Impact: User relying on docs would try `flags=["ASCII"]` which is silently ignored

- [LOW] **Example syntax for TypedDict results**
  - Documentation shows (validate.md:34-38): `CheckBracketsResult(balanced=True, unmatched_openers=[], unmatched_closers=[])`
  - Code actually returns: Python dict literals `{"balanced": True, "unmatched_openers": [], "unmatched_closers": []}`
  - TypedDict requires dict literal syntax, not constructor syntax
  - Impact: Examples in documentation cannot be copy-pasted and run

- [LOW] **Error Handling section says functions "raise ValueError" but they don't**
  - Documentation (validate.md:117-120): Describes error handling for all three functions
  - Mentions `regex_test` raises `ValueError` for invalid patterns or input exceeding size limits
  - Code: `regex_test` returns `valid_pattern=False` with error in result dict (line 287-291), it does NOT raise
  - Impact: Misleading documentation - users may expect exceptions and not check result dicts

## Potential Bugs

- [MEDIUM] **regex_test() has no sample length limit**
  - `check_brackets()` and `validate_json()` both enforce MAX_INPUT_LENGTH = 100_000
  - `regex_test()` accepts arbitrary-length sample strings with no limit
  - Impact: A malicious caller could pass samples of enormous size causing memory exhaustion
  - Location: validate.py:269-347 - no length check on samples

- [LOW] **_check_pattern_complexity() doesn't validate character class closure**
  - Pattern `[` (unclosed character class) passes complexity check
  - Python's `re.compile()` will reject it with `re.error: unterminated character set`
  - The error is caught later (line 307-314) but inconsistency in validation approach
  - Location: validate.py:222-266 - missing `[`/`]` pair validation outside of char classes

## Improvement Suggestions

### HIGH Priority

1. **Add sample length limit to regex_test()**
   - Add `MAX_SAMPLE_LENGTH = 100_000` constant
   - Check each sample length before processing
   - Return error in result dict if any sample exceeds limit (consistent with complexity check pattern)

### MEDIUM Priority

2. **Fix flag documentation**
   - Option A: Add `ASCII` to code (line 296 area) alongside `UNICODE`
   - Option B: Change documentation to list `UNICODE` instead of `ASCII`
   - Recommend Option A for backward compatibility

3. **Improve character class validation**
   - Track whether we're inside a character class and validate `]` has matching `[`
   - Return error for patterns like `[` that will fail at compile time

### LOW Priority

4. **Fix documentation examples**
   - Change `CheckBracketsResult(balanced=True, ...)` to dict literal syntax
   - Change `ValidateJsonResult(...)` to dict literal syntax
   - Change `RegexTestResult(...)` to dict literal syntax

5. **Fix Error Handling section**
   - Remove claim that `regex_test` "raises ValueError"
   - Clarify that all functions return result dicts with embedded error info

## Summary

| Issue | Priority | Type |
|-------|----------|------|
| regex_test() has no sample length limit | MEDIUM | Bug |
| Flag name mismatch (ASCII vs UNICODE) | MEDIUM | Discrepancy |
| Character class closure not validated | LOW | Bug |
| TypedDict example syntax wrong | LOW | Documentation |
| Error Handling section inaccurate | LOW | Documentation |

**Recommended immediate actions:**
1. Add sample length limit to `regex_test()` to prevent memory exhaustion
2. Either add `ASCII` flag to code or update docs to say `UNICODE`
3. Fix TypedDict example syntax in documentation

**Overall assessment:** The module is well-implemented with good test coverage. The main concern is the lack of input length limits on `regex_test()` samples, which differs from the other two functions. The flag documentation discrepancy is minor but could confuse users.
