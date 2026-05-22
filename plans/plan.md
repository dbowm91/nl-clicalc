# nl-clicalc Consolidated Implementation Plan

## Status: Pending Implementation

New action items from module architecture reviews (2026-05-22). Previous plan items marked as complete.

---

## Wave 1: Critical Bugs

### 1. Fix `split_at_operators` whitespace-separated number words
**File:** `nl_calc/normalize.py:703-742`  
**Symptom:** `run("what's five plus three hundred twenty two?")` returns `(3100207, 0)` instead of `(327, 0)`  
**Root cause:** Multi-word numbers like "three hundred twenty two" are not properly combined - normalization produces `'5+3100202'` instead of `'5+322'`  
**Action:** Review tokenization logic for whitespace-separated number words; ensure proper combination of multi-word number expressions  
**Verification:** `python -c "from nl_calc import run, NORMALIZE, PATTERNS; print(run('five plus three hundred twenty two', NORMALIZE, PATTERNS))"`

### 2. Fix `combine_number_parts` logic
**File:** `nl_calc/normalize.py:493-530`  
**Symptom:** `combine_number_parts([20, 2])` returns `['20', '+2']` instead of `['22']`  
**Action:** Simplify logic to properly combine number parts into single values  
**Verification:** `python -c "from nl_calc.normalize import combine_number_parts; print(combine_number_parts([20, 2]))"`

---

## Wave 2: TypedDict and Validation Fixes

### 3. Remove `__slots__` from TypedDict classes
**File:** `nl_calc/exact/validate.py:26, 36, 60`  
**Issue:** TypedDict classes incorrectly have `__slots__` defined (Python typing semantics do not support `__slots__` on TypedDict)  
**Action:** Remove `__slots__` from `BracketError`, `CheckBracketsResult`, `RegexTestResult`  
**Note:** `BracketError` is a regular class (supports `__slots__`), but `CheckBracketsResult` and `RegexTestResult` are TypedDicts (do NOT support `__slots__`)  
**Verification:** `python -c "from nl_calc.exact.validate import CheckBracketsResult; print('Has __slots__:', hasattr(CheckBracketsResult, '__slots__'))"`

### 4. Fix flag name discrepancy in validate.py
**File:** `nl_calc/exact/validate.py:288-298`  
**Issue:** Documentation lists `ASCII` flag but code uses `UNICODE`, `DEBUG`  
**Action:** Ensure flag constants are consistently named or documented

---

## Wave 3: Documentation Corrections

### 5. Fix `control_chars` documentation
**File:** `architecture/measure.md:74`  
**Action:** Clarify that control_chars includes category 'C' (excluding 'Cf' per UTS #55); newlines and tabs ARE counted

### 6. Fix `CommonPrefixSuffix` return type documentation
**File:** `architecture/exact.md:186-193`  
**Action:** Change "Named tuple" to "TypedDict"; fix field names to `common_prefix_len`, `common_suffix_len`

### 7. Fix digits category documentation
**File:** `architecture/measure.md:70`  
**Action:** Change `"Nd"` to category starts with 'N' (includes Nd, Nl, No)

### 8. Fix `graphemes: None` documentation error
**File:** `architecture/synthesis.md:19`  
**Action:** Change `graphemes: None` to `graphemes: int`

### 9. Fix `ScriptInfo` TypedDict structure documentation
**File:** `architecture/exact-unicode_tools.md:19-24`  
**Action:** Update to match actual structure: `index`, `char`, `script`, `codepoint`

### 10. Fix `ConfusableInfo` TypedDict structure documentation
**File:** `architecture/exact-unicode_tools.md:29-36`  
**Action:** Fix field names: `confusable_with` (not `confusable_for`), `confusable_name` (not `confusable_codepoint`), add `index`

### 11. Fix `detect_mixed_scripts` return type documentation
**File:** `architecture/exact-unicode_tools.md:65-74`  
**Action:** Update to reflect actual return type: dict with keys `mixed_scripts`, `scripts`, `positions`

### 12. Fix docstring example mismatch
**File:** `architecture/exact-unicode_tools.md:72-73`  
**Action:** Fix ScriptInfo example to match actual structure

### 13. Update architecture/diff.md TypedDict documentation
**File:** `architecture/diff.md:98-119`  
**Action:** Change "Named tuple" to "TypedDict" for `FirstDiff`, `DiffSpan`, `CommonPrefixSuffix`

### 14. Fix common_prefix_suffix examples
**File:** `architecture/diff.md:54-59`  
**Action:** Ensure examples match actual code behavior

### 15. Update confusables.py header comment
**File:** `nl_calc/exact/confusables.py:11-12`  
**Action:** Clarify multi-codepoint nature of substitutions

### 16. Fix stale comment referencing removed function
**File:** `nl_calc/exact/primitives.py:355`  
**Action:** Update comment that references `_advance_past_sequence` (removed)

### 17. Fix `--verbose` flag documentation
**File:** `cli.md:20-29`  
**Action:** Document `--verbose` flag in CLI options table

### 18. Add `exit()` to REPL documentation
**File:** `cli.md:79`  
**Action:** Document that `exit()` is accepted in REPL

---

## Wave 4: Feature Completeness

### 19. Add `fact` factorial alias
**File:** `nl_calc/evaluator.py:920`  
**Issue:** Only `"factorial": _safe_factorial` exists; `"fact"` alias is missing  
**Action:** Add `"fact": _safe_factorial` alongside existing alias  
**Verification:** `python -c "from nl_calc import evaluate; print(evaluate('fact(5)'))"`

### 20. Add missing physical constants to CONSTANTS dict
**File:** `nl_calc/evaluator.py:830-883`  
**Issue:** Constants `me`, `mp`, `mn`, `re`, `alpha`, `wien` are mapped in `CONSTANT_WORDS` (normalize.py) but not defined in `CONSTANTS` dict  
**Action:** Add actual numeric values for: electron mass (`me`=9.1093837015e-31), proton mass (`mp`=1.67262192369e-27), neutron mass (`mn`=1.67493e-27), classical electron radius (`re`=2.817952326e-15), fine structure constant (`alpha`=7.2973525693e-3), Wien displacement (`wien`=2.897771955e-3)  
**Verification:** `python -c "from nl_calc import evaluate; print(evaluate('me'))"`

### 21. Add `get_unit_category()` and `are_units_compatible()` to API docs
**File:** `architecture/api.md`  
**Action:** Document these utility functions in "Unit Utilities" section

### 22. Document `get_default_evaluator()` function
**File:** `architecture/api.md`  
**Action:** Add to "Core Evaluation Functions" section

### 23. Document `FLOAT_EPSILON` constant
**File:** `architecture/api.md`  
**Action:** Document in "Security Constants" or "Tolerance Constants" section

### 24. Document `MAX_INPUT_LENGTH` and `MAX_NESTING_DEPTH`
**File:** `architecture/api.md`  
**Action:** Document these limit constants

### 25. Update evaluator.py Key Exports
**File:** `architecture/overview.md` or `evaluator.py:117`  
**Action:** Ensure complete list: `evaluate_async()`, `evaluate_with_timeout()`, `Memory`, `memory_store()`, `memory_recall()`, `memory_add()`, `memory_subtract()`, `memory_clear()`, `memory_list()`, `setvar()`, `getvar()`, `delvar()`, `listvars()`, `clearvars()`

### 26. Update normalize.py Key Exports
**File:** `architecture/overview.md` or `normalize.py:94`  
**Action:** Ensure complete list: `NORMALIZE`, `PATTERNS`, `print_help`, `MAX_INPUT_LENGTH`, `MAX_NESTING_DEPTH`

### 27. Add `normalize_unit` to Key Data Structures
**File:** `architecture/overview.md`  
**Action:** Add to units row in table

### 28. Add `Memory` to Key Data Structures
**File:** `architecture/overview.md`  
**Action:** Document Memory class in table

### 29. Add `ExplainDiffResult` structure details
**File:** `architecture/exact.md` or `architecture/diff.md`  
**Action:** Document TypedDict fields with working examples

### 30. Add `InspectTextResult` structure details
**File:** `architecture/synthesis.md`  
**Action:** Document TypedDict fields

### 31. Add `CountCharsResult` structure
**File:** `architecture/measure.md`  
**Action:** Document structure

---

## Wave 5: MCP Server Updates

### 32. Fix `math_eval` response format inconsistency
**File:** `nl_calc/mcp/tools.py:89`  
**Issue:** `math_eval` returns raw dict `{"result": ..., "type": ...}` while other tools use `_success_response()` wrapper `{"ok": True, "result": ...}`  
**Action:** Change to use `_success_response()` for consistency

### 33. Add type validation to multiple tools
**File:** `nl_calc/mcp/tools.py`  
**Action:** Add validation for: `expression` (str), `include_codepoints` (bool), `casefold` (bool), `trim` (bool), `flags` items

### 34. Add minimum constraint for max_graphemes
**File:** `nl_calc/mcp/schemas.py:155`  
**Action:** Add `"minimum": 0` to `max_graphemes` property

### 35. Add outputSchema to remaining tools
**File:** `nl_calc/mcp/schemas.py`  
**Action:** Complete outputSchema definitions beyond `text_truncate`

### 36. Validate pairs parameter in validate_brackets
**File:** `nl_calc/mcp/tools.py:260-281`  
**Action:** Add validation for pairs parameter

### 37. Document SuccessEnvelope removal
**File:** `mcp.md:38-44`  
**Action:** Document that SuccessEnvelope was removed from API

### 38. Complete error code table
**File:** `mcp_server.md:226-231`  
**Action:** Add missing `-32601 MethodNotFound` error code

### 39. Separate `_handle_initialize` function
**File:** `nl_calc/mcp/server.py:160-174`  
**Action:** Extract inline handling to separate function

### 40. Add first-call performance note for PyCalcApp
**File:** `nl_calc/mcp/server.py`  
**Action:** Document first-call initialization overhead

---

## Wave 6: Code Quality

### 41. Refine `_is_extended_pictographic` range
**File:** `nl_calc/exact/primitives.py:382`  
**Action:** Consider refining range (0x1F300-0x10FFFF is broad; includes private use areas)

### 42. Document count_graphemes/truncate functions
**File:** `nl_calc/exact/primitives.py:291-463`  
**Action:** Document `count_graphemes()`, `truncate_to_grapheme()`, `_is_extend_char()`, `_is_extended_pictographic()`

### 43. Update graphemes_estimate documentation
**File:** `architecture/primitives.md:102`  
**Action:** Change `None # Not implemented` to `int` (feature is implemented)

### 44. Fix `word_metrics` docstring
**File:** `nl_calc/exact/measure.py:44`  
**Action:** Clarify word definition

### 45. Add defensive else clause
**File:** `nl_calc/exact/measure.py:239`  
**Action:** Add else clause for completeness

### 46. Document normalized_equal default form
**File:** `nl_calc/exact/primitives.py:151`  
**Action:** Emphasize NFC default in docstring

### 47. Complete invisible chars list in docs
**File:** `architecture/primitives.md`  
**Action:** Document all entries: LRE, RLE, LRO, RLO, LRI, RLI, FSI, PDI, MVS, CGJ

### 48. Add rounding info for average_word_length
**File:** `architecture/measure.md`  
**Action:** Document that average_word_length is rounded to 2 decimal places

### 49. Improve combining_marks example
**File:** `nl_calc/exact/measure.py`  
**Action:** Use NFD text or add second example showing combining marks

### 50. Rename REPL result variable from `_`
**File:** `nl_calc/__main__.py` or `nl_calc/normalize.py:1039`  
**Action:** Rename to avoid shadowing Python's last-expression-value built-in

### 51. Add type annotations where missing
**Files:** Multiple modules  
**Action:** Ensure all functions have complete type annotations

### 52. Add docstring to `validate_for_eval`
**File:** `nl_calc/normalize.py:475`  
**Action:** Add missing docstring

### 53. Add line counts to module listings
**File:** `architecture/overview.md`  
**Action:** Update with accurate line counts (confusables.py ~6580 lines)

---

## Wave 7: Units/Validation Updates

### 54. Update unit categories documentation sync
**File:** `architecture/units.md`  
**Action:** Sync Force (missing dyne, lbf), Voltage (missing uV, μV), Current (missing uA, μA), THz, area variants

### 55. Clean up UNIT_ALIASES self-mappings
**File:** `nl_calc/units.py`  
**Action:** Remove redundant self-mapping entries unless intentional

### 56. Add missing area units to UNIT_ALIASES
**File:** `nl_calc/units.py`  
**Action:** Add: `sqft`, `sqin`, `sqmi`, `sqyd`, `sqm`

### 57. Update Error Handling documentation
**File:** `architecture/validate.md:106-109`  
**Action:** Clarify functions return error info in result dicts, not raise exceptions

### 58. Add nesting underflow detection
**File:** `nl_calc/exact/validate.py:251-252`  
**Action:** Report error for malformed patterns like `')'`

### 59. Refine temperature offset precision
**File:** `nl_calc/units.py`  
**Action:** Consider using Fraction for exact temperature offsets

---

## Deferred Items

| Item | Description | Reason |
|------|-------------|--------|
| D1 | Add reverse lookup function for confusables | Requires design decision |
| D2 | Fix or remove unreachable `unicode_normalization_only` | Requires investigation |
| D3 | Add `include_codepoints` to `measure_text()` or remove from docs | Design decision |
| D4 | Add `normalize_text` parameter to `inspect_text()` | May overlap with existing |
| D5 | Performance review for confusables_count | Defer until profiling needed |
| D6 | Reorganize documentation structure | Low priority, structural |
| D7 | Add docstrings to ConfusableInfo fields | Low priority |
| D8 | Clarify `normalize()` vs `normalize_expression()` distinction | Low priority |
| D9 | Add input size limits for `check_brackets()` and `validate_json()` | Low priority |
| D10 | Update CLI entry description | Low priority |
| D11 | Clarify normalize.py dependencies | Low priority |
| D12 | Add `__all__` export list for diff.py | Low priority |

---

## Parallelization by Wave

All items within a wave are parallelizable:

- **Wave 1 (Critical):** Items 1-2 can run in parallel
- **Wave 2 (TypedDict):** Items 3-4 can run in parallel  
- **Wave 3 (Documentation):** Items 5-18 can all run in parallel
- **Wave 4 (Features):** Items 19-31 can all run in parallel
- **Wave 5 (MCP):** Items 32-40 can all run in parallel
- **Wave 6 (Quality):** Items 41-53 can all run in parallel
- **Wave 7 (Units):** Items 54-59 can all run in parallel

---

## Verification Commands

```bash
# Run all tests
python -m pytest tests/

# Verify critical fixes
python -c "from nl_calc import run, NORMALIZE, PATTERNS; print(run('five plus three hundred twenty two', NORMALIZE, PATTERNS))"
python -c "from nl_calc.normalize import combine_number_parts; print(combine_number_parts([20, 2]))"
python -c "from nl_calc.exact.validate import CheckBracketsResult; print('Has __slots__:', hasattr(CheckBracketsResult, '__slots__'))"

# Verify feature additions
python -c "from nl_calc import evaluate; print(evaluate('fact(5)'))"
python -c "from nl_calc import evaluate; print(evaluate('me'))"

# Verify MCP fix
python -c "from nl_calc.mcp.tools import math_eval; print(math_eval('5+3'))"
```

---

## Notes

- All changes must work with `build_single.py` assembling modules into `nl_calc.py`
- Standard library only - no external packages
- Use type annotations for function signatures
- TypedDict classes do NOT support `__slots__`
- `BracketError` is a regular class (supports `__slots__`); TypedDicts do NOT
- Wave 1 items produce incorrect results and should be prioritized