# nl-clicalc Consolidated Plan

## Wave 1: Critical Bugs (Fix First - Sequential)

### 1.1 Force/Voltage/Current UNIT_ALIASES Bug
**File:** `nl_calc/units.py` lines 900-931
**Issue:** Prefixed units like `kN`, `mV`, `mA` incorrectly alias to base units (`N`, `V`, `A`), causing `get_conversion_factor("kN", "N")` to return `1.0` instead of `1000.0`.
**Fix:** Change aliases to map to themselves (e.g., `"kN": "kN"` instead of `"kN": "N"`).
**Verification:** After fix, `get_conversion_factor("kN", "N")` should return `1000.0`

### 1.2 Temperature F→C Offset Precision
**File:** `nl_calc/units.py` line 1038
**Issue:** Offset `-17.777778` has rounding error.
**Fix:** Change to `-17.77777777777778` for exact freezing point conversion.

### 1.3 Newline Detection Bug
**File:** `nl_calc/exact/measure.py` line 52
**Issue:** `"\r" not in "\n"` always returns True since they're different single characters. Any text with CRLF is incorrectly reported as "mixed".
**Fix:** Rewrite the `mixed` newline detection logic at lines 45-62 to properly detect standalone LF/CR outside CRLF sequences.

### 1.4 RegexTestResult Missing error Field
**File:** `nl_calc/exact/validate.py` lines 50-53
**Issue:** The TypedDict is missing `error: str | None` field. When invalid regex is provided, callers cannot get error details.
**Fix:** Add `error: str | None` field to `RegexTestResult` TypedDict.

### 1.5 regex_test() Error Handling
**File:** `nl_calc/exact/validate.py` lines 237-241
**Issue:** The `re.error` exception message is lost and not returned.
**Fix:** Capture and return the error message when `re.error` is raised.

### 1.6 CLI --mcp Flag Missing
**File:** `nl_calc/normalize.py` lines 1220-1252
**Issue:** The `--mcp` argument only exists in the built single-file version. When running via `python -m nl_calc`, argparse does not include `--mcp`.
**Fix:** Add `--mcp` argument to normalize.py argparse and handle import/call to `mcp_main()`.

### 1.7 visible_repr() Variation Selector Display
**File:** `nl_calc/exact/primitives.py` lines 272-275
**Issue:** Variation selectors (U+FE00 to U+FE0F) should display as `⟦VS⟧` per documentation but display as `◌︀` because the combining mark check (`M` category) fires first.
**Fix:** Move VS check before combining mark check.

### 1.8 visible_repr() Missing WORD JOINER
**File:** `nl_calc/exact/primitives.py` lines 269-285
**Issue:** U+2060 (WORD JOINER) is detected by `find_invisibles()` but `visible_repr()` has no case for it—it falls through and returns the character as-is.
**Fix:** Add handling for U+2060 in `visible_repr()`.

### 1.9 mps Missing from UNIT_CATEGORIES
**File:** `nl_calc/units.py` lines 1089-1226
**Issue:** `get_unit_category("mps")` returns None, causing `are_units_compatible("mps", "km/h")` incorrectly return True.
**Fix:** Add `mps` to `UNIT_CATEGORIES`.

## Wave 2: High Priority Bugs (Can Run Parallel with Wave 1)

### 2.1 MCP Double-Wrapped Response
**File:** `nl_calc/mcp/server.py`
**Issue:** Success responses are double-wrapped, deeply nested with JSON string inside text content block.
**Fix:** Simplify response structure to avoid double-wrapping of results.

### 2.2 MCP math_eval Missing MAX_TEXT_LENGTH
**File:** `nl_calc/mcp/tools.py`
**Issue:** `math_eval` tool does not enforce `MAX_TEXT_LENGTH` like other tools do.
**Fix:** Add `MAX_TEXT_LENGTH` check to `math_eval`.

### 2.3 utf8_bytes Return Type Mismatch
**File:** `nl_calc/exact/primitives.py`
**Issue:** `utf8_bytes` return type is ambiguous - decide whether it returns `int` (count) or `bytes` and fix implementation accordingly.
**Fix:** Clarify return type and ensure implementation matches.

### 2.4 invisibles_detected Always False
**File:** `nl_calc/exact/synthesis.py` line 280
**Issue:** `invisibles_detected` is hardcoded to `False` instead of detecting actual invisibles state.
**Fix:** Detect and pass actual invisibles state.

### 2.5 Unit Conversion Space-Separated Bug
**File:** `nl_calc/normalize.py` lines 842-898
**Issue:** `_handle_unit_conversion_from_tokens()` only detects patterns when "from" unit is attached (e.g., `2meters`). Space-separated `2 meters in feet` doesn't work after splitting.
**Fix:** Fix unit conversion detection to handle space-separated number and unit tokens.

## Wave 3: Documentation Fixes (Can Run Parallel with Implementation)

### 3.1 Index Links to Non-Existent Files
**File:** `architecture/*.md`
**Issue:** References docs like `primitives.md`, `unicode_tools.md` that don't exist - actual docs are `exact.md` and `mcp_server.md`.
**Fix:** Update index links to use correct file names.

### 3.2 Confusables Documentation Return Format
**File:** `docs/exact.md` lines 146-153
**Issue:** Documentation shows `confusable_with='U+0041'` (codepoint format) but actual implementation returns character `'A'`.
**Fix:** Update documentation to show actual return format (character not codepoint string).

### 3.3 Confusables Table Size
**File:** `docs/exact.md` line 138
**Issue:** Documentation says "~1800 entries" but actual table has 6564 entries.
**Fix:** Update to "~6500 entries".

### 3.4 detect_confusables Example Wrong
**File:** `architecture/unicode_tools.md` lines 75-84
**Issue:** Example shows TWO confusables in "pаypal" but only ONE is actually detected.
**Fix:** Fix example to show correct detection result.

### 3.5 detect_mixed_scripts Example Incomplete
**File:** `architecture/unicode_tools.md` lines 50-55
**Issue:** Example shows only Cyrillic positions but function returns ALL non-Common/Inherited positions.
**Fix:** Update example to show complete return value.

### 3.6 Missing Cyrillic Range in Docs
**File:** `architecture/unicode_tools.md` lines 93-109
**Issue:** Missing `(0x0500, 0x052f, "Cyrillic")` that's present in implementation.
**Fix:** Add missing Cyrillic range documentation.

### 3.7 first_diff Documentation Wrong Field Names
**File:** `architecture/diff.md`
**Issue:** Docs claim `a_context` and `b_context` fields but implementation has `a_codepoint` and `b_codepoint`.
**Fix:** Update to `a_codepoint`/`b_codepoint`.

### 3.8 common_prefix_suffix Example Incorrect
**File:** `architecture/diff.md`
**Issue:** Example `("testing", "ing")` does not have suffix=2.
**Fix:** Fix or remove the incorrect example.

### 3.9 diff Algorithm Documentation
**File:** `architecture/diff.md` line 76
**Issue:** Says "Levenshtein" but implementation uses `difflib.SequenceMatcher`.
**Fix:** Update to say "Uses difflib.SequenceMatcher to compute opcodes".

### 3.10 ValidateJsonResult Field Names
**File:** `architecture/validate.md`
**Issue:** Doc says `error_position`, `error_line`, `error_column`, `structure` but code has `position`, `line`, `column`, `type`.
**Fix:** Unify field names between documentation and implementation.

### 3.11 spans vs span Mismatch
**File:** `nl_calc/exact/validate.py`
**Issue:** Document says `spans: list[tuple[int, int]]` but code has `span: list[int] | None` (singular, different type).
**Fix:** Unify the field name and type.

### 3.12 Duplicate Line in confusables Architecture
**File:** `architecture/confusables.md` line 29
**Issue:** Line 29 duplicates line 28.
**Fix:** Remove duplicate line.

### 3.13 Undocumented Memory Type
**File:** `nl_calc/__init__.py`
**Issue:** `Memory` type exported but not documented in Types documentation.
**Fix:** Document the `Memory` type.

### 3.14 Temperature Base Unit Misleading
**File:** `architecture/units.md` line 41
**Issue:** Table shows `K` for temperature but conversions use offset math, not multiplicative factors.
**Fix:** Change to show `(offset-based)` instead of `K`.

## Wave 4: Medium Priority Items (Parallel Work)

### 4.1 Add lru_cache to _get_script_heuristic
**File:** `nl_calc/exact/unicode_tools.py`
**Issue:** Called for every character in `detect_mixed_scripts`; memoization would improve performance.
**Fix:** Add `@lru_cache` decorator to `_get_script_heuristic`.

### 4.2 include_codepoints Parameter Ignored
**File:** `nl_calc/exact/synthesis.py` line 173
**Issue:** Parameter accepted but silently ignored in `measure_text()`.
**Fix:** Either implement the parameter or remove it.

### 4.3 Unify text_equal() and explain_diff() Classification
**File:** `nl_calc/exact/synthesis.py` lines 313-337, 397-408
**Issue:** Two functions use different classification schemes for the same comparisons.
**Fix:** Unify classification logic between the two functions.

### 4.4 Optimize list_compare() near_matches
**File:** `nl_calc/exact/synthesis.py` lines 656-673
**Issue:** Current O(n²) nested loops can be improved with set-based matching.
**Fix:** Implement set-based matching for near_matches detection.

### 4.5 Case-Insensitive MCP Tool Matching
**File:** `nl_calc/mcp/server.py`
**Issue:** Tool names are case-sensitive with no suggestion for close matches.
**Fix:** Add case-insensitive tool name matching or document case-sensitivity.

### 4.6 MCP Error Message Sanitization
**File:** `nl_calc/mcp/tools.py`
**Issue:** Unicode characters in error messages not sanitized.
**Fix:** Add error message sanitization to prevent control characters in JSON-RPC error messages.

### 4.7 _classify_difference Accent/Diacritic Logic
**File:** `nl_calc/exact/synthesis.py` lines 326-328
**Issue:** Logic appears backwards—NFC equality means strings are canonically equivalent.
**Fix:** Review and correct the classification logic.

### 4.8 TOOL_SCHEMAS Dead Code
**File:** `nl_calc/mcp/schemas.py` and `nl_calc/mcp/server.py`
**Issue:** Tool names in `schemas.py` use `nl_` prefix but `server.py` uses non-prefixed names - TOOL_SCHEMAS is dead code.
**Fix:** Refactor to use TOOL_SCHEMAS as single source of truth, or remove dead code.

### 4.9 Regex Flags Documentation Mismatch
**File:** `nl_calc/exact/validate.py`
**Issue:** Document lists `ASCII` but implementation has `UNICODE` and `DEBUG`.
**Fix:** Either add `ASCII` support or update docs.

### 4.10 Missing Functions in Registry
**File:** `nl_calc/evaluator.py`
**Issue:** `abs`, `floor`, `ceil`, `trunc` not documented in Functions Registry.
**Fix:** Add missing functions to documentation.

### 4.11 Missing Percentage Functions Documentation
**File:** `nl_calc/evaluator.py`
**Issue:** `percentof`, `percent_of`, `aspercent`, `as_percent` not documented.
**Fix:** Document percentage functions.

### 4.12 Missing Base Conversion Documentation
**File:** `nl_calc/evaluator.py`
**Issue:** `bin`, `hex`, `oct` not documented.
**Fix:** Document base conversion functions.

### 4.13 evaluate_cached Not in __all__
**File:** `nl_calc/evaluator.py` line 29
**Issue:** Function is public but not exported in `__all__` list.
**Fix:** ~~Add `"evaluate_cached"` to `__all__`.~~ **RESOLVED: Already present in __all__ at line 34**

### 4.14 get_default_evaluator Not in __all__
**File:** `nl_calc/__init__.py`
**Issue:** Function exported but not listed in `__all__`.
**Fix:** ~~Add `get_default_evaluator` to `__all__`.~~ **RESOLVED: Already present in __all__ at line 96**

### 4.15 load_user_config_extended Not Exported
**File:** `nl_calc/__init__.py`
**Issue:** `load_user_config_extended()` exists in `evaluator.py` (line 157) but is NOT exported from `__init__.py`. Only `load_user_config` is exported.
**Fix:** Either export `load_user_config_extended` from `__init__.py` or document that custom number/operator words via external config are not officially supported.

### 4.16 Timeout Example Fails Before Timeout
**File:** `nl_calc/__init__.py` or docs
**Issue:** Example uses expression that fails with `EvaluationError` ("Exponent too large") before timeout due to `MAX_EXPONENT = 10000`.
**Fix:** Change example to one that would actually timeout or add note about limitation.

### 4.17 Memory Functions Return Type Documentation
**File:** `nl_calc/evaluator.py` or docs
**Issue:** Documentation claims functions return `Memory` objects but they actually return `float`.
**Fix:** Rewrite documentation to clarify return types are `float`.

### 4.18 evaluate_raw skip_validation Scope
**File:** `nl_calc/evaluator.py`
**Issue:** Docstring says "skip_validation=True" but it only skips normalization validation, not AST security validation.
**Fix:** Clarify docstring to indicate scope of skip_validation.

### 4.19 _cached_normalize_and_evaluate Visibility
**File:** `nl_calc/evaluator.py`
**Issue:** Not exported and not clearly marked as internal.
**Fix:** Either add to `__all__` if public, or rename with underscore prefix.

### 4.20 Cache Size Documentation Mismatch
**File:** `nl_calc/__init__.py` or docs
**Issue:** Documentation says `cache_size=1000` but actual default is `1024`.
**Fix:** Update documentation to say `cache_size=1024`.

### 4.21 Missing Functions in Documentation
**File:** `architecture/evaluator.md`
**Issue:** `variance_sample`, `conjugate`, `is_prime`, `prime_factors`, `next_prime`, `prev_prime`, `var` not documented.
**Fix:** Document all function aliases and missing functions.

### 4.22 Missing Architecture Items
**File:** `architecture/*.md`
**Issue:** `normalize_expression`, `CONSTANT_WORDS`, `STRIPPED_PHRASES`, `FUNCTION_MAPPINGS`, `TimeoutError`, `get_default_evaluator()`, memory functions not documented.
**Fix:** Add documentation for undocumented data structures and functions.

### 4.23 Variance Sample Not in Functions Dict
**File:** `nl_calc/evaluator.py`
**Issue:** `variance_sample` defined but not exposed to users.
**Fix:** Add to FUNCTIONS dict or document why not exposed.

### 4.24 Undocumented Fields in measure
**File:** `nl_calc/exact/measure.py`
**Issue:** `trailing_whitespace_lines`, `sentences_estimate`, `paragraphs`, `mixed` newline style not documented.
**Fix:** Document all fields in architecture/measure.md.

### 4.25 avg_word_length vs average_word_length
**File:** `nl_calc/exact/measure.py` line 31
**Issue:** Document specifies `avg_word_length` but code has `average_word_length`.
**Fix:** Align field name between docs and code.

### 4.26 max_word_length Missing
**File:** `nl_calc/exact/measure.py`
**Issue:** Document specifies `max_word_length` in WordMetrics but implementation doesn't include it.
**Fix:** Either add to implementation or remove from docs.

### 4.27 Pipeline Diagram Inaccurate
**File:** `architecture/*.md` lines 52-61
**Issue:** Shows `normalize() → normalize_expression() → evaluate()` but actual flow is `run() → normalize_expression() → normalize()`.
**Fix:** Update diagram to reflect actual flow.

### 4.28 Entry Point Description Misleading
**File:** `architecture/cli.md` lines 5-8
**Issue:** Docs say `__main__.py` provides entry point but it's just a bootstrap.
**Fix:** Update description to clarify bootstrap behavior.

### 4.29 Build Function Renaming Undocumented
**File:** `architecture/*.md`
**Issue:** `normalize.main()` → `normalize_main()`, MCP `main()` → `mcp_main()` not documented.
**Fix:** Document the renaming behavior.

### 4.30 Duplicate MAX_NESTING_DEPTH
**File:** `normalize.py:43` and `evaluator.py:51`
**Issue:** Defined in two places.
**Fix:** Consider consolidating to single definition.

### 4.31 Silent Fallthrough in Temperature Conversion
**File:** `nl_calc/units.py`
**Issue:** `100 K` to `ft` might silently give wrong result.
**Fix:** Add validation or warning for invalid temperature conversions.

### 4.32 Typo in Docstring
**File:** `nl_calc/normalize.py:843`
**Issue:** `2meters` → `2 meters`.
**Fix:** Fix typo.

### 4.33 NFKD Equal Not Documented
**File:** `architecture/synthesis.md`
**Issue:** `TextEqualResult` includes `nfkd_equal` but not mentioned in architecture.
**Fix:** Document `nfkd_equal` field.

### 4.34 count_chars Return Type Confusing
**File:** `nl_calc/exact/synthesis.py` lines 570-608
**Issue:** Union return type is confusing.
**Fix:** Consider splitting into two functions.

### 4.35 Graphemes Estimate Unimplemented
**File:** `nl_calc/exact/primitives.py` line 184
**Issue:** `graphemes_estimate` always returns `None`. If accurate visual character counting is needed, implement or clarify.
**Fix:** Either implement with `unicodedata` or label clearly as unavailable.

### 4.36 Remove Redundant Codepoint Entries
**File:** `nl_calc/exact/unicode_tools.py`
**Issue:** Duplicate entries like `(0x0401, 0x0401, "Cyrillic")` should be removed.
**Fix:** Remove redundant single-codepoint range entries.

## Wave 5: Testing (Parallel with Documentation)

### 5.1 Add Tests for Force/Voltage/Current Conversions
**File:** `tests/`
**Issue:** No tests exist for prefixed unit conversions after UNIT_ALIASES fix.
**Fix:** Add tests verifying `get_conversion_factor("kN", "N")` returns `1000.0`.

### 5.2 Add Test for Temperature Conversion Precision
**File:** `tests/`
**Issue:** No tests for exact temperature offset conversion.
**Fix:** Add test verifying freezing point conversion.

### 5.3 Add Test for "Other" Script Category
**File:** `tests/`
**Issue:** No tests for characters returning "Other" from `unicode_script` (digits, punctuation).
**Fix:** Add tests for `unicode_script()` with digits and punctuation.

### 5.4 Complete Phase 5: Unit Conversion Tests
**File:** `tests/`
**Issue:** Deferred from testing_plan.md.
**Fix:** Complete unit conversion tests using `run()` API (not `evaluate()`).

### 5.5 Complete Phase 6: Natural Language Tests
**File:** `tests/`
**Issue:** Deferred from testing_plan.md.
**Fix:** Complete NL tests using `run()` API (not `evaluate()`).

### 5.6 Complete Phase 7: Test Documentation
**File:** `tests/README.md`
**Issue:** Deferred from testing_plan.md.
**Fix:** Create `tests/README.md` documenting test conventions.

### 5.7 Add MCP Server Integration Tests
**File:** `tests/`
**Issue:** No MCP server tests exist.
**Fix:** Add tests covering protocol handshake, tools/list, tools/call, error handling.

### 5.8 Add Regex Pattern Complexity Limits
**File:** `nl_calc/exact/validate.py` or `nl_calc/mcp/`
**Issue:** ReDoS potential in regex tool.
**Fix:** Add pattern complexity limits or timeout to prevent ReDoS.

### 5.9 Add MAX_EXPRESSION_LENGTH to math_eval
**File:** `nl_calc/mcp/tools.py`
**Issue:** Resource exhaustion possible via math_eval with very long expressions.
**Fix:** Add `MAX_EXPRESSION_LENGTH` limit.

### 5.10 Ensure All 177 Tests Pass
**File:** `tests/`
**Issue:** New tests must not break existing tests.
**Fix:** Run `python -m pytest tests/` and ensure all pass.

## Wave 6: Future Items (Low Priority)

### 6.1 eggsact.md Items
See `plans/eggsact.md` for Rust reimplementation items including:
- Statistical functions (mean, median, std, variance)
- Complex number support
- Remaining physical constants
- Unicode normalization
- Casefold comparison
- Mixed script detection
- Compound unit parsing
- Port remaining test suites
- Interactive REPL and extended CLI options

### 6.2 Add Cancel Notification Support
**File:** `nl_calc/mcp/`
**Issue:** `notifications/cancel` and `notifications/progress` not handled.
**Fix:** Add cancel notification support for long-running operations.

### 6.3 Consider Adding confusable_codepoint Field
**File:** `nl_calc/exact/confusables.py`
**Issue:** Consumers may need both character and codepoint representations.
**Fix:** Consider adding `confusable_codepoint` field to ConfusableInfo TypedDict.

### 6.4 Consider Bidirectional Confusable Detection
**File:** `nl_calc/exact/confusables.py`
**Issue:** Currently only catches confusable characters, not Latin characters being used deceptively.
**Fix:** Consider adding bidirectional confusable detection.

### 6.5 Levenshtein vs difflib
**File:** `nl_calc/exact/diff.py`
**Issue:** Current difflib behavior may be insufficient for some use cases.
**Fix:** Optionally refactor to use true Levenshtein-based LCS diff.

### 6.6 Performance Timing Numbers
**File:** `nl_calc/__init__.py` or docs
**Issue:** Unverified performance timing numbers in documentation.
**Fix:** Remove or qualify since they cannot be verified.

---

## Verification Commands

After implementing changes, verify with these commands:

```bash
# Run all tests
python -m pytest tests/

# Verify unit conversion fix
python -c "from nl_calc.units import get_conversion_factor; print(get_conversion_factor('kN', 'N'))"  # Should be 1000.0

# Verify temperature fix
python -c "from nl_calc.units import get_conversion_factor; print(get_conversion_factor('F', 'C'))"  # Should be exact

# Verify MCP flag exists
python -m nl_calc --help | grep mcp

# Check for lru_cache on _get_script_heuristic
python -c "from nl_calc.exact.unicode_tools import _get_script_heuristic; import functools; print(hasattr(_get_script_heuristic, 'cache_info'))"
```
