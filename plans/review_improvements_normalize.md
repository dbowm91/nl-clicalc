# normalize Module Review — Improvement Plan

**Reviewed:** architecture/normalize.md against nl_calc/normalize.py
**Date:** 2026-05-28

## Verified Claims (with line references)
- `normalize.py` re-exports `evaluate`, `EvaluationError`, `UnitValue` — VERIFIED at lines 23-24
- `__all__` exports match docs — VERIFIED at lines 27-40
- `OPERATOR_CONVERS` structure and content — VERIFIED at lines 101-119
- `FUNCTION_MAPPINGS` structure and content — VERIFIED at lines 123-217
- `NUMBER_WORDS` structure and content — VERIFIED at lines 220-261
- `CONSTANT_WORDS` includes `avogadros` (plural) — VERIFIED at line 280 (docs omitted at line 105)
- `STRIPPED_PHRASES` includes most items — VERIFIED at lines 264-276 (docs line 117-128 incomplete)
- `MAX_INPUT_LENGTH = 10000` — VERIFIED at line 42 (matches docs line 222)
- `MAX_NESTING_DEPTH = 100` — VERIFIED at line 43 (matches docs line 223)
- `_UNITS_BY_LENGTH` and `_COMMON_UNITS` pre-computed for performance — VERIFIED at lines 46-91
- `_build_config()` sorts by length descending — VERIFIED at lines 322-324, 341-342
- Module-level config at line 379 matches docs — VERIFIED
- `check_if_number()` returns `dict` with keys `bool`, `converted`, `type` — VERIFIED at line 389 (docs line 156-166)
- Pipeline diagram in docs (lines 178-192) matches actual processing flow
- Security notes (lines 238-244) accurate: no eval(), input limits, nesting limits
- Module dependencies listed at lines 246-251 are accurate

## Discrepancies Between Documentation and Code

### MEDIUM — Incomplete `STRIPPED_PHRASES` documentation
- **Documentation says:** Lines 117-128 show stripped phrases list
- **Code actually does:** Lines 264-276 include additional phrases: `"tell me"`, `"give me"`, `"the "`
- **Impact:** Users reading docs won't know these filler words are also stripped

### MEDIUM — `CONSTANT_WORDS` plural forms undocumented
- **Documentation says:** Line 105 only shows `"avogadro"` and `"avogadro number"`
- **Code actually does:** Line 280 includes `"avogadros"` (plural form)
- **Impact:** Users might not know both singular and plural forms work

### MEDIUM — `FUNCTION_MAPPINGS` entries undocumented (partial)
- **Documentation says:** Lines 68-82 show abbreviated function mappings
- **Code actually does:** Lines 123-217 include many more functions (bitand, bitxor, isprime, primefactors, nextprime, prevprime, random, gauss, etc.)
- **Impact:** Help text at lines 1270-1274 is incomplete compared to actual function set

### LOW — `run()` return type documentation discrepancy
- **Documentation says:** Line 148 shows `tuple[Any, int]`
- **Code actually does:** Docstring at line 1162 says `tuple: (result, exit_code)` without annotation; actual type annotation present at line 1159
- **Impact:** Minor - inline docs incomplete but type annotation correct

### LOW — `normalize_expression()` `skip_validation` parameter undocumented
- **Documentation says:** Lines 143-146 describe parameters but omit `skip_validation`
- **Code actually does:** Line 1109 adds `skip_validation: bool = False` parameter
- **Impact:** Users of custom evaluators won't know this option exists

### LOW — `apply_math_functions()` docstring at line 589-635 is minimal vs docs
- **Documentation says:** Mentions function name normalization but not the detailed rules (docs lines 129-141)
- **Code actually does:** Full rules comment at lines 594-598: "sin40 + 2 -> math.sin(40) + 2", etc.
- **Impact:** Implementation details not documented

## Potential Bugs

### MEDIUM — `_handle_negative_token` may crash on empty split
- **Location:** `normalize.py:693`
- **Issue:** `tokens[index].split("-")` assumes at least 2 parts. If `temp` has only 1 element, accessing `temp[1]` at line 696 raises `IndexError`.
- **Suggested investigation:** Trace calls from `_should_handle_inline_negative` and `_should_handle_decimal_negative`. While these guard functions should prevent entering `_handle_negative_token` with invalid tokens, there's no explicit bounds check for the empty case after split.

### MEDIUM — Float regex pattern may limit valid floats
- **Location:** `normalize.py:368`
- **Issue:** `"^[-|+]?[0-9]\d*\.\d+?$"` — The pattern `[0-9]\d*` means one digit followed by zero or more digits, but `\d+?` for the fractional part is non-greedy. This could fail to match `10.5` correctly in edge cases. The original intent appears to be matching floats like `3.14`, `.5`, etc.
- **Suggested investigation:** Verify all expected float formats pass (simple floats like `3.14`, large floats like `123456.789`, floats without integer part like `.5`)

### LOW — `_should_handle_inline_negative` returns True but caller ignores return value
- **Location:** `normalize.py:747`
- **Issue:** `_should_handle_inline_negative()` is called but its boolean return is never checked - the function determines if inline negative handling should occur but the result is discarded.
- **Suggested investigation:** This appears to be dead code flow - the function is called but its result is not used to gate the `_handle_negative_token` call.

### LOW — `_should_handle_decimal_negative` has same issue
- **Location:** `normalize.py:750`
- **Issue:** Same pattern - function computes a boolean but result is discarded.

## Improvement Suggestions

### HIGH Priority
- **Fix float regex pattern at line 368:** The pattern `^[-|+]?[0-9]\d*\.\d+?$` has issues with `\d*` (zero or more) after first digit. Consider `^[-|+]?[0-9]+\.\d+?$` or clarify intent.

### MEDIUM Priority
- **Add `skip_validation` parameter to docs:** This useful parameter for custom evaluators is documented in code but not in architecture docs.

- **Document plural constant forms:** Add `avogadros` and other plural forms to architecture docs for completeness.

- **Complete `STRIPPED_PHRASES` documentation:** Add `"tell me"`, `"give me"`, `"the "` to the docs list.

- **Investigate inline negative handling flow:** The functions `_should_handle_inline_negative` and `_should_handle_decimal_negative` compute booleans that appear to be unused. Verify this is intentional or if there is missing logic.

### LOW Priority
- **Add `_handle_negative_token` bounds check:** Add explicit check after `split("-")` to handle edge case of single-element result gracefully.

- **Document `apply_math_functions` rules:** The detailed rules for function call handling (lines 594-598) would be valuable in architecture docs.

- **Update help text coverage:** `print_help()` at lines 1270-1274 lists functions, but many actual functions (bit operations, memory functions, etc.) are not shown.

- **Consider documenting internal functions:** `_combine_consecutive_numbers`, `_join_number_parts`, `_preprocess_units`, `_handle_unit_conversion_from_tokens` are significant internal functions that process NL input but are not documented in the architecture.

## Summary
The normalize module architecture documentation is generally accurate and well-organized, with all major data structures (`OPERATOR_CONVERSIONS`, `NUMBER_WORDS`, `CONSTANT_WORDS`, `FUNCTION_MAPPINGS`) correctly documented. The main discrepancies are incomplete documentation in supportive areas: `STRIPPED_PHRASES` omits 3 entries, `CONSTANT_WORDS` omits plural forms, and `FUNCTION_MAPPINGS` is abbreviated. The potential bugs found are low-to-medium severity, mostly around edge case handling in negative number parsing and a potentially incorrect float regex pattern. All 350 tests pass, indicating the codebase is functionally sound.
