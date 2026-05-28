# nl-clicalc Consolidated Implementation Plan

## Status: ACTIVE

This plan consolidates all improvement items identified across the review process.

---

## Wave 1: Critical Bugs (Fix First)

### 1.1 Temperature-to-non-temperature conversion crashes
- **Location:** `units.py:146-164`
- **Issue:** Warning issued then crashes because K not in UNIT_BASE
- **Fix options:**
  1. Remove warning and let conversion proceed
  2. Implement multiplicative conversion with warning
  3. Raise proper error instead of crashing
- **Status:** PENDING

### 1.2 Dead code branch in `_classify_difference()`
- **Location:** `synthesis.py:337-338`
- **Issue:** `"accent_or_diacritic_difference"` branch unreachable when `nfc_equal=True` because casefold equality implies NFC equality
- **Fix:** Remove unreachable branch or restructure logic
- **Status:** PENDING

### 1.3 Dead code in `list_compare()` near_matches
- **Location:** `synthesis.py:704-714`
- **Issue:** `"unicode_normalization_only"` classification cannot be triggered through normal usage
- **Fix:** Remove classification or clarify when it triggers
- **Status:** PENDING

### 1.4 Float regex pattern has issues
- **Location:** `normalize.py:368`
- **Issue:** Pattern `^[-|+]?[0-9]\d*\.\d+?$` is unusual - `[0-9]\d*` is redundant (digit followed by zero or more digits)
- **Status:** PENDING INVESTIGATION - Needs edge case testing to determine if pattern causes actual bugs

### 1.5 Investigate `_handle_negative_token` crash potential
- **Location:** `normalize.py:693`
- **Issue:** `split("-")` may produce single element, causing IndexError at line 696
- **Status:** PENDING INVESTIGATION

---

## Wave 2: Documentation Corrections (Critical)

### 2.1 `normalize_expression` return type wrong
- **Locations:** `api.md:130`, `normalize.md:143-146`
- **Issue:** Docs show `-> str` but actual is `-> tuple[str, int]` and requires `operators`, `patterns` args
- **Fix:** Update signature documentation to show full parameters and return type
- **Status:** PENDING

### 2.2 `FirstDiff` TypedDict declaration wrong
- **Location:** `diff.md:88-92`
- **Issue:** Docs show 3 fields (`position`, `a_char`, `b_char`) but code has 6 fields (`a_index`, `b_index`, `a_char`, `b_char`, `a_codepoint`, `b_codepoint`)
- **Fix:** Update to 6 correct fields
- **Status:** PENDING

### 2.3 All three `common_prefix_suffix` examples wrong
- **Location:** `diff.md:53-59`
- **Issue:**
  - `"hello", "hell"` doc says `common_prefix_len: 3` → code returns `4`
  - `"hello", "yo"` doc says `common_prefix_len: 0` → code returns `0` but `common_suffix_len: 1` (doc says `0`)
  - `"testing", "ing"` doc says `common_suffix_len: 0` → code returns `3`
- **Fix:** Update all three expected values (code is correct)
- **Status:** PENDING

### 2.4 `normalize_main` alias missing
- **Location:** `cli.md:13,16`
- **Issue:** Documentation claims `main()` is aliased as `normalize_main()` but no such alias exists
- **Fix:** Either add the alias to normalize.py or update docs to remove reference
- **Status:** PENDING

### 2.5 `--verbose` flag behavior mismatch
- **Location:** `cli.md:32` vs `normalize.py:1441,1520`
- **Issue:** Docs say "Show detailed error information and tracebacks" but code shows expression in output
- **Fix:** Update documentation to match actual behavior
- **Status:** PENDING

### 2.6 `reverse_confusables()` undocumented
- **Location:** `unicode_tools.md`
- **Issue:** Fully implemented function (unicode_tools.py:268-292) not documented
- **Fix:** Add complete documentation with signature, description, examples, return type
- **Status:** PENDING

### 2.7 `check_if_number` return type wrong
- **Location:** `normalize.md:156-166`
- **Issue:** Docs show `"type": type(token)` but code returns actual type string (e.g., `"int"`, `"float"`)
- **Fix:** Update documentation
- **Status:** PENDING

### 2.8 `evaluate_with_timeout` docstring uses forbidden syntax
- **Location:** `evaluator.py:1368`
- **Issue:** Docstring shows `sum(i**2 for i in range(10000))` but GeneratorExp is forbidden at evaluator.py:1261
- **Fix:** Remove or change generator expression example
- **Status:** PENDING

### 2.9 `UnitValue` example wrong
- **Location:** `api.md:174` vs `units.py:35-38`
- **Issue:** Docs show `"5 m"` but actual output is `"5.0 m"`
- **Fix:** Update example to show `"5.0 m"` or demonstrate `.value` access
- **Status:** PENDING

---

## Wave 3: Missing Documentation (High)

### 3.1 Add `reverse_confusables` to public API docs
- **Location:** `architecture/exact.md lines 24-47`
- **Issue:** Function exported in `__init__.py:52` but not in public API table
- **Fix:** Add to exports table and function documentation
- **Status:** PENDING

### 3.2 Add `first_diff` and `CommonPrefixSuffix` to public API
- **Location:** `architecture/exact.md lines 24-47, 210-221`
- **Issue:** Both exported in `__init__.py` but not documented
- **Fix:** Add to public API documentation
- **Status:** PENDING

### 3.3 Update invisible characters list
- **Location:** `architecture/exact.md lines 75-89`
- **Issue:** Docs show 10 characters but `_INVISIBLE_CHARS` has 23
- **Fix:** Add missing: U+180e, U+034f, U+202b-202e, U+2066-2069
- **Status:** PENDING

### 3.4 Document `detect_mixed_scripts` "Other" script exclusion
- **Location:** `unicode_tools.md:75`
- **Issue:** Documentation says "non-Common/Inherited" but code also excludes "Other"
- **Fix:** Update to note "non-Common/Inherited/Other chars"
- **Status:** PENDING

### 3.5 Update unicode_tools.md index section
- **Location:** `unicode_tools.md:217-224`
- **Issue:** Index lists only 5 functions, but 6 public functions exist
- **Fix:** Add `reverse_confusables()` to index
- **Status:** PENDING

### 3.6 Document error code -32700
- **Location:** `mcp.md:240-246`
- **Issue:** Error codes table shows -32600 to -32603 and -32000, but -32700 used at server.py:209
- **Fix:** Add `-32700 | ParseError | Invalid JSON` to table
- **Status:** PENDING

### 3.7 Document all UnitValue public methods
- **Location:** `units.md`
- **Issue:** Only `convert_to()` and `__repr__()` documented; missing `__str__`, `__format__`, `__eq__`, `__hash__`, etc.
- **Fix:** Add documentation for all public methods
- **Status:** PENDING

### 3.8 Fix `diff_spans` example output
- **Location:** `diff.md:105-109`
- **Issue:** Example shows `equal` spans but code filters them out
- **Fix:** Remove `equal` spans from example
- **Status:** PENDING

---

## Wave 4: Code Quality Improvements (Medium)

### 4.1 Fix `visible_repr()` documentation
- **Location:** `architecture/primitives.md:253-260`
- **Issue:** Documentation shows 4 steps but code has 5 (missing BIDI handling at lines 277-284)
- **Fix:** Add BIDI character checks step
- **Status:** PENDING

### 4.2 Fix `truncate_to_grapheme` parameter name
- **Location:** `architecture/exact.md line 68` vs `primitives.py:391`
- **Issue:** Docs say `max_len` but code uses `max_graphemes`
- **Fix:** Align documentation to code
- **Status:** PENDING

### 4.3 Add `get_unit_category` to Key Exports
- **Location:** `overview.md`
- **Issue:** Function exists at units.py:1263 but not in Key Exports
- **Fix:** Add to units.py Key exports list
- **Status:** PENDING

### 4.4 Investigate `_is_extended_pictographic()` range
- **Location:** `primitives.py:372-388`
- **Issue:** Line 378 checks range and returns True immediately; subsequent category/name checks only run if NOT in range. This may over-match characters like ☀ (U+2600)
- **Fix:** Investigate and narrow range if needed
- **Status:** PENDING INVESTIGATION

### 4.5 Fix `_handle_negative_token` potential crash
- **Location:** `normalize.py:693`
- **Issue:** `split("-")` may produce single element, causing IndexError at line 696
- **Fix:** Add bounds check after split
- **Status:** PENDING

### 4.6 Fix `load_user_config_extended` documentation
- **Location:** `evaluator.py:168-187` vs docs
- **Issue:** Function exists but not documented (intentionally not exported)
- **Fix:** Add note about existence but intentional non-export
- **Status:** PENDING

### 4.7 Add `enable_cache` parameter to PyCalcApp docs
- **Location:** `api.md` vs `evaluator.py:1414`
- **Issue:** Constructor missing `enable_cache` parameter in documentation
- **Fix:** Add parameter to docs
- **Status:** PENDING

### 4.8 Fix `visible_repr()` display order incomplete
- **Location:** `primitives.md:253-260` vs code:277-284
- **Issue:** Docs missing BIDI handling step
- **Fix:** Add missing step documentation
- **Status:** PENDING

### 4.9 Add `normalize_expression` `skip_validation` param to docs
- **Location:** `normalize.md:143-146` vs code:1109
- **Issue:** Useful parameter for custom evaluators not documented
- **Fix:** Add parameter documentation
- **Status:** PENDING

### 4.10 Complete `STRIPPED_PHRASES` documentation
- **Location:** `normalize.md:117-128` vs code:264-276
- **Issue:** Missing `"tell me"`, `"give me"`, `"the "`
- **Fix:** Add missing phrases
- **Status:** PENDING

### 4.11 Fix newline detection algorithm documentation
- **Location:** `architecture/measure.md:98-102`
- **Issue:** Documentation doesn't show "mixed" detection complexity
- **Fix:** Add explicit "mixed" detection step
- **Status:** PENDING

### 4.12 Document `top_level_keys` behavior for non-object JSON
- **Location:** `validate.md`
- **Issue:** Not clear that `top_level_keys` returns `None` for arrays/primitives
- **Fix:** Add note about behavior for non-objects
- **Status:** PENDING

### 4.13 Add type validation for None input
- **Location:** `measure.py:66,128,200`
- **Issue:** Functions don't validate `s is not None`
- **Fix:** Consider raising TypeError for None input
- **Status:** PENDING

### 4.14 Add `Evaluator` class to Key Exports
- **Location:** `api.md:15-35`
- **Issue:** Class is public but undocumented
- **Fix:** Add to Key Exports
- **Status:** PENDING

### 4.15 Document `evaluate_raw` complete signature
- **Location:** `api.md:19` vs evaluator.py:1314
- **Issue:** Doesn't mention it calls `normalize_expression` internally
- **Fix:** Add note about internal normalization
- **Status:** PENDING

---

## Wave 5: Low Priority Improvements

### 5.1 Remove duplicate `G` entry in constants table
- **Location:** docs:155,161
- **Fix:** Remove duplicate entry
- **Status:** PENDING

### 5.2 Add undocumented constants to docs
- **Location:** evaluator.py:836-902
- **Issue:** `u`/`amu`, `epsilon0`, `mu0`, `rydberg`, `stefan`, `planckbar`/`hbar`, `me`, `mp`, `mn`, `re`, `alpha` not documented
- **Fix:** Add to constants documentation
- **Status:** PENDING

### 5.3 Add undocumented functions to docs
- **Location:** evaluator.py
- **Issue:** `is_prime`, `conjugate`, `nPr`, `nCr`, `var`, `log1p`, `expm1`, `degrees`, `radians`, `floor`, `ceil`, `trunc`, `randrange`, `uniform`, memory shortcuts not documented
- **Fix:** Add function documentation
- **Status:** PENDING

### 5.4 Remove "call during init only" restriction from docs
- **Location:** `api.md:84` vs evaluator.py:73-76
- **Issue:** No such restriction exists in code
- **Fix:** Remove incorrect restriction
- **Status:** PENDING

### 5.5 Add test for `text_equal("café", "CAFÉ")`
- **Location:** synthesis.py tests
- **Issue:** No test for case+diacritic classification
- **Fix:** Add test to verify correct classification
- **Status:** PENDING

### 5.6 Add test for `explain_diff` symmetry
- **Issue:** Verify `"hello!"` vs `"hello"` and `"hello"` vs `"hello!"` both return `"length_only"`
- **Fix:** Add symmetric test
- **Status:** PENDING

### 5.7 Add `MAX_SAMPLE_LENGTH` for regex_test
- **Location:** `validate.py`
- **Issue:** `regex_test` doesn't check if individual samples exceed length limit
- **Fix:** Add size check for samples
- **Status:** PENDING

### 5.8 Fix parameter name alignment in validate.py
- **Location:** docs use `text`, code uses `s`
- **Fix:** Align documentation to code
- **Status:** PENDING

### 5.9 Add test for `reverse_confusables()`
- **Issue:** No direct test coverage (only used indirectly via synthesis.py)
- **Fix:** Add unit test
- **Status:** PENDING

### 5.10 Add example for `detect_mixed_scripts` showing "Other" exclusion
- **Location:** `unicode_tools.md`
- **Issue:** No example showing digits/punctuation exclusion
- **Fix:** Add example with "Other" script characters
- **Status:** PENDING

### 5.11 Clarify multi-character confusable_with
- **Location:** `unicode_tools.md:133`
- **Issue:** Users may not realize it can be multi-character string
- **Fix:** Add note about multi-character capability
- **Status:** PENDING

### 5.12 Add `unicode_scripts` to Supported Scripts table
- **Location:** `unicode_tools.md`
- **Issue:** Not clear it returns per-character scripts
- **Fix:** Add clarification
- **Status:** PENDING

### 5.13 Consider adding TypedDict for `detect_mixed_scripts`
- **Location:** `unicode_tools.py:150`
- **Issue:** Returns `dict` not TypedDict, inconsistent with other functions
- **Fix:** Create `MixedScriptsResult` TypedDict
- **Status:** PENDING

### 5.14 Consider adding TypedDict for `list_compare`
- **Location:** `synthesis.py:622-727`
- **Issue:** Returns `dict` not TypedDict
- **Fix:** Create `ListCompareResult` TypedDict
- **Status:** PENDING

### 5.15 Shell glob detection path component check fragile
- **Location:** `normalize.py:1498`
- **Issue:** Only checks literal "." and ".." but not "./" or "../"
- **Fix:** Improve path component handling
- **Status:** PENDING

### 5.16 `_cli_text_command` uses broad exception
- **Location:** `normalize.py:1396`
- **Issue:** `except Exception` catches KeyboardInterrupt, SystemExit
- **Fix:** Change to `except re.error`
- **Status:** PENDING

### 5.17 JSON output inconsistent
- **Location:** `normalize.py:1179`
- **Issue:** `expression` field omitted when `--json` used without `--show`
- **Fix:** Make JSON schema consistent
- **Status:** PENDING

### 5.18 `visible_repr()` combining mark check order issue
- **Location:** `primitives.py:273-276`
- **Issue:** VS check comes before combining mark check; may process separately
- **Fix:** Investigate and verify no display issues
- **Status:** PENDING INVESTIGATION

### 5.19 Redundant condition in temperature conversion
- **Location:** `units.py:157`
- **Issue:** `self.value < 0` appears twice
- **Fix:** Remove redundant check
- **Status:** PENDING

### 5.20 Fix interactive REPL description
- **Location:** `cli.md:72`
- **Issue:** Missing welcome message description
- **Fix:** Document "nl-calc interactive mode..." message
- **Status:** PENDING

### 5.21 Add line number references to cli.md
- **Issue:** Makes verification harder without references
- **Fix:** Add file:line references
- **Status:** PENDING

### 5.22 Update grapheme counting algorithm docs
- **Location:** `architecture/primitives.md:244-251`
- **Issue:** Doesn't mention Regional Indicator pairs for flags
- **Fix:** Add GB12/GB13 documentation
- **Status:** PENDING

---

## Already Completed Items

Items resolved in prior planning session:

| Item | Description | Resolution |
|------|-------------|------------|
| D1 | `reverse_confusables()` implementation | Implemented with cached inverted index (unicode_tools.py:268-292) |
| D2 | `unicode_normalization_only` classification | Verified reachable in `_classify_difference()` when NFC equal but raw bytes differ |
| D3 | Dead `include_codepoints` parameter | Removed from MCP schema and tool function |
| D4 | Add `normalize_text` to `inspect_text()` | **DEFERRED** - Overlaps with existing `normalize_unicode()` + `inspect_text()` workflow; design review needed |
| D5 | Performance review for confusables_count | **DEFERRED** - O(n) with O(1) lookups is optimal; no action needed |
| D6 | Reorganize documentation | **DEFERRED** - Low priority; current structure is functional |
| D7 | ConfusableInfo docstrings | All fields have comment-based docstrings |
| D8 | `normalize()` vs `normalize_expression()` | Already documented in architecture/normalize.md |
| D9 | Input size limits for validate | MAX_INPUT_LENGTH = 100_000 added to check_brackets() and validate_json() |
| D10 | CLI entry description | Current description is functional |
| D11 | normalize.py dependencies | Documented in architecture/normalize.md |
| D12 | `__all__` for diff.py | Added `__all__` list to diff.py |
| W1-W7 | Implementation waves | All completed in prior session |

---

## File:Line Reference Index

### Critical Locations

| File:Line | Priority | Issue |
|-----------|----------|-------|
| `units.py:146-164` | HIGH | Temperature-to-non-temperature crash |
| `synthesis.py:337-338` | HIGH | Dead code branch in `_classify_difference` |
| `synthesis.py:704-714` | HIGH | Dead code in `list_compare` near_matches |
| `evaluator.py:836-902` | MEDIUM | Constants documented (g, wien exist) - verify doc coverage |
| `normalize.py:368` | HIGH | Float regex pattern has issues |
| `api.md:130` | HIGH | `normalize_expression` return type wrong |
| `diff.md:88-92` | HIGH | `FirstDiff` TypedDict wrong |
| `diff.md:53-59` | HIGH | `common_prefix_suffix` examples wrong |
| `cli.md:13,16` | HIGH | `normalize_main` alias missing |
| `cli.md:32` | HIGH | `--verbose` behavior mismatch |
| `unicode_tools.md` | HIGH | `reverse_confusables()` undocumented |
| `normalize.md:156-166` | HIGH | `check_if_number` return type wrong |
| `evaluator.py:1368` | HIGH | Generator expression in docstring |
| `api.md:174` | HIGH | `UnitValue` example wrong |
| `synthesis.py:238` | MEDIUM | `text_equal()` missing return type annotation |
| `primitives.py:391` | MEDIUM | `truncate_to_grapheme` parameter name |
| `architecture/exact.md lines 24-47` | MEDIUM | Missing exports in docs |
| `architecture/exact.md lines 75-89` | MEDIUM | Invisible characters list incomplete |
| `primitives.md:253-260` | MEDIUM | `visible_repr()` display order incomplete |
| `mcp.md:240-246` | MEDIUM | Error code -32700 undocumented |
| `units.md` | MEDIUM | UnitValue methods undocumented |
| `normalize.py:1109` | MEDIUM | `skip_validation` parameter undocumented |
| `evaluator.py:1414` | MEDIUM | Missing `enable_cache` param in docs |
| `measure.py:66,128,200` | LOW | None input validation |
| `validate.py:285-291` | LOW | Inconsistent error handling for regex_test |

---

## Verification

```bash
python3 -m pytest tests/
```

All 350 tests must pass.

---

## Summary

| Wave | Items | Priority |
|------|-------|----------|
| 1 | 5 (3 bugs + 2 investigations) | Critical Bugs |
| 2 | 9 | Documentation Corrections |
| 3 | 8 | Missing Documentation |
| 4 | 15 | Code Quality |
| 5 | 22 | Low Priority |
| **Total** | **59** | |