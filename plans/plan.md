# nl-clicalc Consolidated Implementation Plan

This is the single consolidated plan consolidating all review items from the plans directory.

## Status: ALL WAVES COMPLETED

All waves have been implemented and verified. See commit history for details.

## Wave 1: Critical Bugs (FIXED)
### 1.1 Force/Voltage/Current UNIT_ALIASES - FIXED
### 1.2 Temperature F→C Offset Precision - FIXED
### 1.3 Newline Detection Bug - FIXED
### 1.4 RegexTestResult Missing error Field - FIXED
### 1.5 CLI --mcp Flag Missing - FIXED

## Wave 2: High Priority Bugs (FIXED)
### 2.1 MCP Double-Wrapped Response - FIXED
### 2.2 MCP math_eval Missing MAX_TEXT_LENGTH - FIXED
### 2.3 utf8_bytes Return Type Clarification - DOCUMENTED
### 2.4 invisibles_detected Always False - FIXED
### 2.5 Unit Conversion Space-Separated Bug - DOCUMENTED (pre-existing limitation with 'in' keyword)

## Wave 3: Exact Module Bug Fixes (FIXED)
### 3.1 visible_repr() Variation Selector - FIXED
### 3.2 visible_repr() Missing WORD JOINER - FIXED
### 3.3 Add lru_cache to _get_script_heuristic - FIXED
### 3.4 mps Missing from UNIT_CATEGORIES - FIXED

## Wave 4: Documentation Fixes (FIXED)
### 4.1-4.18: All documentation fixes completed

## Wave 5: Medium Priority Items (FIXED)
### 5.1-5.27: All medium priority items completed

## Wave 6: Testing (FIXED)
### 6.1-6.10: All testing items completed

## Wave 7: Future Items (DEFERRED)
### 7.1-7.6: All marked as future/consider items

## Wave 1: Critical Bugs (Fix First - Sequential)

These bugs cause incorrect calculations or broken functionality and must be fixed before other work.

### 1.1 Force/Voltage/Current UNIT_ALIASES Bug
**File:** `nl_calc/units.py` lines 900-931

**Problem:** Prefixed units like `kN`, `mV`, `mA` are incorrectly aliased to base units:
- `"kN": "N"` should be `"kN": "kN"`
- `"kV": "V"` should be `"kV": "kV"`
- `"mV": "V"` should be `"mV": "mV"`
- `"mA": "A"` should be `"mA": "mA"`

This causes `get_conversion_factor("kN", "N")` to return `1.0` instead of `1000.0`.

**Fix:** Change each prefixed unit alias to map to itself, not the base unit:
```python
# Force (lines 900-908)
"kN": "kN",  # was "N"
"dyne": "dyne",  # was "N"
"lbf": "lbf",  # was "N"

# Voltage (lines 910-919)
"kV": "kV",  # was "V"
"mV": "mV",  # was "V"
"uV": "μV",  # was "V"

# Current (lines 921-931)
"mA": "mA",  # was "A"
"uA": "μA",  # was "A"
```

**Verification:**
```python
from nl_calc.units import get_conversion_factor
assert get_conversion_factor("kN", "N") == 1000.0
assert get_conversion_factor("mV", "V") == 1000.0
assert get_conversion_factor("mA", "A") == 1000.0
```

### 1.2 Temperature F→C Offset Precision
**File:** `nl_calc/units.py` line 1038

**Problem:** The offset `-17.777778` has rounding error. The exact value is `-32/1.8`.

**Fix:** Change line 1038 from:
```python
("F", "C"): (1.0 / 1.8, -17.777778),
```
to:
```python
("F", "C"): (1.0 / 1.8, -32.0 / 1.8),
```

**Verification:**
```python
from nl_calc.units import convert_temperature
assert convert_temperature(32, "F", "C") == 0.0  # freezing point
```

### 1.3 Newline Detection Bug
**File:** `nl_calc/exact/measure.py` lines 45-62

**Problem:** The condition `"\r" not in "\n"` is malformed - it checks if literal `\n` is in string `\r`, which always returns True since they're different single characters. Any text with CRLF is incorrectly reported as "mixed".

**Fix:** Rewrite `_detect_newline_style()` to properly detect standalone CR/LF outside CRLF sequences:
```python
def _detect_newline_style(s: str) -> str:
    """Detect the newline style used in the string."""
    has_crlf = "\r\n" in s
    # Count standalone CR not followed by LF, and standalone LF not preceded by CR
    standalone_cr = s.count("\r") - s.count("\r\n")
    standalone_lf = s.count("\n") - s.count("\r\n")

    # If we have both standalone CR and standalone LF, it's mixed
    if standalone_cr > 0 and standalone_lf > 0:
        return "mixed"
    if has_crlf:
        return "CRLF"
    elif standalone_cr > 0:
        return "CR"
    elif standalone_lf > 0:
        return "LF"
    else:
        return "none"
```

**Verification:**
```python
from nl_calc.exact.measure import line_metrics
# CRLF should be "CRLF", not "mixed"
result = line_metrics("line1\r\nline2")
assert result.newline_style == "CRLF"
```

### 1.4 RegexTestResult Missing error Field
**File:** `nl_calc/exact/validate.py` lines 50-53, 237-241

**Problem:** The `RegexTestResult` TypedDict is missing `error: str | None` field. When invalid regex is provided, callers cannot get error details.

**Fix:** 
1. Add `error` field to `RegexTestResult` at line 53:
```python
class RegexTestResult(TypedDict):
    """Result of regex testing."""
    valid_pattern: bool
    results: list[RegexMatch]
    error: str | None  # Add this
```

2. Capture and return the error message at line 237:
```python
    except re.error as e:
        return RegexTestResult(
            valid_pattern=False,
            results=[],
            error=str(e),  # Add this
        )
```

### 1.5 CLI --mcp Flag Missing
**File:** `nl_calc/normalize.py` lines 1215-1268

**Problem:** The `--mcp` argument only exists in the built single-file version. When running via `python -m nl_calc`, argparse does not include `--mcp`.

**Fix:** Add `--mcp` argument to the argparse section (around line 1251) and handle it:
```python
parser.add_argument(
    "--mcp", action="store_true", help="Run as MCP server for exact text tools"
)
```

And add the handler after parsing (around line 1269):
```python
if args.mcp:
    from nl_calc.mcp.server import mcp_main
    return mcp_main()
```

## Wave 2: High Priority Bugs (Can Run Parallel with Wave 1)

### 2.1 MCP Double-Wrapped Response
**File:** `nl_calc/mcp/server.py` lines 114-130

**Problem:** Success responses are double-wrapped, nested with JSON string inside text content block.

**Fix:** Simplify `_success_response()` or `_handle_call_tool()` to avoid double-wrapping. The response structure should be:
```python
{
    "content": [{"type": "text", "text": json.dumps(result)}]
}
```
without an outer `ok=True` wrapper.

### 2.2 MCP math_eval Missing MAX_TEXT_LENGTH
**File:** `nl_calc/mcp/tools.py` lines 62-81

**Problem:** `math_eval` tool does not enforce `MAX_TEXT_LENGTH` like other tools do.

**Fix:** Add input length check at start of `math_eval`:
```python
if len(text) > MAX_TEXT_LENGTH:
    return {"error": f"Input exceeds maximum length of {MAX_TEXT_LENGTH}"}
```

### 2.3 utf8_bytes Return Type Clarification
**File:** `nl_calc/exact/primitives.py` lines 75-84

**Problem:** Documentation says "number of bytes" but implementation returns `bytes` object.

**Fix:** The implementation is correct (returns `bytes`). Update architecture documentation to clarify: `utf8_bytes()` returns actual UTF-8 encoded bytes, not a count.

### 2.4 invisibles_detected Always False
**File:** `nl_calc/exact/synthesis.py` line 280

**Problem:** `invisibles_detected=False` is hardcoded instead of detecting actual invisibles state.

**Fix:** Detect invisibles before calling `_classify_difference()`:
```python
# At line 273, detect invisibles
invisibles_a = find_invisibles(a_work)
invisibles_b = find_invisibles(b_work)
invisibles_detected = invisibles_a or invisibles_b

# At line 280, pass actual value
classification = _classify_difference(
    raw_equal, nfc_equal, casefold_equal, byte_equal,
    len(a_work) != len(b_work), first_difference,
    invisibles_detected=invisibles_detected  # was False
)
```

### 2.5 Unit Conversion Space-Separated Bug
**File:** `nl_calc/normalize.py` lines 842-898

**Problem:** `_handle_unit_conversion_from_tokens()` only detects patterns when "from" unit is attached (e.g., `2meters`). Space-separated `2 meters in feet` doesn't work after splitting.

**Fix:** Modify token handling to combine number and unit when they are separate tokens:
- When tokens are `["2", "meters", "in", "feet"]`, combine `"2"` + `"meters"` → `"2meters"`
- Similar to how `combine_number_parts()` handles number words

## Wave 3: Exact Module Bug Fixes (Parallel with Wave 2)

### 3.1 visible_repr() Variation Selector Display Order
**File:** `nl_calc/exact/primitives.py` lines 272-275

**Problem:** Variation selectors (U+FE00 to U+FE0F) should display as `⟦VS⟧` but display as `◌︀` because combining mark check (`M` category) fires first.

**Fix:** Move VS check BEFORE combining mark check:
```python
elif 0xfe00 <= ord(char) <= 0xfe0f:
    result.append("⟦VS⟧")
elif unicodedata.category(char).startswith("M"):
    result.append(f"◌{char}")
```

### 3.2 visible_repr() Missing WORD JOINER
**File:** `nl_calc/exact/primitives.py` lines 269-285

**Problem:** U+2060 (WORD JOINER) is detected by `find_invisibles()` but `visible_repr()` has no case for it.

**Fix:** Add handling after line 271:
```python
elif char == "\u2060":
    result.append("⟦WORD JOINER⟧")
```

### 3.3 Add lru_cache to _get_script_heuristic
**File:** `nl_calc/exact/unicode_tools.py` lines 61-95

**Problem:** `_get_script_heuristic()` is called for every character in `detect_mixed_scripts` without memoization.

**Fix:** Add `@functools.lru_cache` decorator:
```python
@functools.lru_cache(maxsize=128)
def _get_script_heuristic(char: str) -> str:
    # ... existing implementation
```

### 3.4 mps Missing from UNIT_CATEGORIES
**File:** `nl_calc/units.py` lines 1089-1226

**Problem:** `get_unit_category("mps")` returns None, causing `are_units_compatible("mps", "km/h")` incorrectly return True.

**Fix:** Add `"mps": "speed"` to `UNIT_CATEGORIES` dict (around line 1206, after `"m/s"`).

## Wave 4: Documentation Fixes (Parallel Work)

### 4.1 Index Links to Non-Existent Files
**File:** `architecture/*.md`

**Problem:** References docs like `primitives.md`, `unicode_tools.md` that don't exist - actual docs are `exact.md` and `mcp_server.md`.

**Fix:** Update all index links to use correct file names.

### 4.2 Confusables Documentation Return Format
**File:** `docs/exact.md` lines 146-153

**Problem:** Documentation shows `confusable_with='U+0041'` (codepoint format) but actual implementation returns character `'A'`.

**Fix:** Update documentation to show actual return format (character not codepoint string).

### 4.3 Confusables Table Size
**File:** `docs/exact.md` line 138

**Problem:** Documentation says "~1800 entries" but actual table has 6564 entries.

**Fix:** Update to "~6500 entries".

### 4.4 detect_confusables Example Wrong
**File:** `architecture/unicode_tools.md` lines 75-84

**Problem:** Example shows TWO confusables in "pаypal" but only ONE is actually detected (Cyrillic 'а' at index 1).

**Fix:** Fix example to show correct detection result with only one confusable.

### 4.5 detect_mixed_scripts Example Incomplete
**File:** `architecture/unicode_tools.md` lines 50-55

**Problem:** Example shows only Cyrillic positions but function returns ALL non-Common/Inherited positions.

**Fix:** Update example to show complete return value including all mixed-script positions.

### 4.6 Missing Cyrillic Range in Docs
**File:** `architecture/unicode_tools.md` lines 93-109

**Problem:** Missing `(0x0500, 0x052f, "Cyrillic")` that's present in implementation.

**Fix:** Add missing Cyrillic range documentation.

### 4.7 first_diff Documentation Wrong Field Names
**File:** `architecture/diff.md`

**Problem:** Docs claim `a_context` and `b_context` fields but implementation has `a_codepoint` and `b_codepoint`.

**Fix:** Update to `a_codepoint`/`b_codepoint`.

### 4.8 common_prefix_suffix Example Incorrect
**File:** `architecture/diff.md` lines 55-57

**Problem:** Example `("testing", "ing")` → suffix=2 is incorrect. No suffix overlap exists.

**Fix:** Fix or remove the incorrect example.

### 4.9 diff Algorithm Documentation
**File:** `architecture/diff.md` line 76

**Problem:** Says "Levenshtein" but implementation uses `difflib.SequenceMatcher`.

**Fix:** Update to say "Uses difflib.SequenceMatcher to compute opcodes".

### 4.10 ValidateJsonResult Field Names
**File:** `architecture/validate.md`

**Problem:** Doc says `error_position`, `error_line`, `error_column`, `structure` but code has `position`, `line`, `column`, `type`.

**Fix:** Unify field names (update docs to match code).

### 4.11 spans vs span Mismatch
**File:** `nl_calc/exact/validate.py` line 45

**Problem:** Document says `spans: list[tuple[int, int]]` but code has `span: list[int] | None` (singular, different type).

**Fix:** Update documentation to reflect singular `span` with `[start, end]` format.

### 4.12 Duplicate Line in confusables Architecture
**File:** `architecture/confusables.md` line 29

**Problem:** Line 29 duplicates line 28.

**Fix:** Remove duplicate line.

### 4.13 Undocumented Memory Type
**File:** `nl_calc/__init__.py`

**Problem:** `Memory` type exported but not documented in Types documentation.

**Fix:** Document the `Memory` type.

### 4.14 Temperature Base Unit Misleading
**File:** `architecture/units.md` line 41

**Problem:** Table shows `K` for temperature but conversions use offset math, not multiplicative factors.

**Fix:** Change to show `(offset-based)` instead of `K`.

### 4.15 Pipeline Diagram Inaccurate
**File:** `architecture/overview.md` lines 52-61

**Problem:** Shows `normalize() → normalize_expression() → evaluate()` but actual flow is `run() → normalize_expression() → normalize()` then `evaluate()`.

**Fix:** Update diagram to reflect actual flow.

### 4.16 Entry Point Description Misleading
**File:** `architecture/cli.md` lines 5-8

**Problem:** Docs say `__main__.py` provides entry point but it's just a bootstrap.

**Fix:** Update description to clarify bootstrap behavior.

### 4.17 Build Function Renaming Undocumented
**File:** `architecture/*.md`

**Problem:** `normalize.main()` → `normalize_main()`, MCP `main()` → `mcp_main()` not documented.

**Fix:** Document the renaming behavior.

### 4.18 Duplicate MAX_NESTING_DEPTH
**File:** `normalize.py:43` and `evaluator.py:51`

**Problem:** Defined in two places.

**Fix:** Consolidate to single definition.

## Wave 5: Medium Priority Items (Parallel Work)

### 5.1 include_codepoints Parameter Ignored
**File:** `nl_calc/exact/synthesis.py` line 173

**Problem:** Parameter accepted but silently ignored in `measure_text()`.

**Fix:** Either implement the parameter or remove it.

### 5.2 Unify text_equal() and explain_diff() Classification
**File:** `nl_calc/exact/synthesis.py` lines 313-337, 397-408

**Problem:** Two functions use different classification schemes for the same comparisons.

**Fix:** Unify classification logic between the two functions.

### 5.3 Optimize list_compare() near_matches
**File:** `nl_calc/exact/synthesis.py` lines 656-673

**Problem:** Current O(n²) nested loops can be improved with set-based matching.

**Fix:** Implement set-based matching for near_matches detection.

### 5.4 Case-Insensitive MCP Tool Matching
**File:** `nl_calc/mcp/server.py` line 46

**Problem:** Tool names are case-sensitive with no suggestion for close matches.

**Fix:** Add case-insensitive tool name matching or document case-sensitivity.

### 5.5 MCP Error Message Sanitization
**File:** `nl_calc/mcp/tools.py`

**Problem:** Unicode characters in error messages not sanitized.

**Fix:** Add error message sanitization to prevent control characters in JSON-RPC error messages.

### 5.6 TOOL_SCHEMAS Dead Code
**File:** `nl_calc/mcp/schemas.py` and `nl_calc/mcp/server.py`

**Problem:** Tool names in `schemas.py` use `nl_` prefix but `server.py` uses non-prefixed names - TOOL_SCHEMAS is dead code.

**Fix:** Refactor to use TOOL_SCHEMAS as single source of truth, or remove dead code.

### 5.7 Missing Functions in Registry
**File:** `nl_calc/evaluator.py`

**Problem:** `abs`, `floor`, `ceil`, `trunc` not documented in Functions Registry.

**Fix:** Add missing functions to documentation.

### 5.8 Missing Percentage Functions Documentation
**File:** `nl_calc/evaluator.py`

**Problem:** `percentof`, `percent_of`, `aspercent`, `as_percent` not documented.

**Fix:** Document percentage functions.

### 5.9 Missing Base Conversion Documentation
**File:** `nl_calc/evaluator.py`

**Problem:** `bin`, `hex`, `oct` not documented.

**Fix:** Document base conversion functions.

### 5.10 load_user_config_extended Not Exported
**File:** `nl_calc/__init__.py`

**Problem:** `load_user_config_extended()` exists in `evaluator.py` (line 157) but is NOT exported from `__init__.py`.

**Fix:** Either export `load_user_config_extended` from `__init__.py` or document that custom number/operator words via external config are not officially supported.

### 5.11 Timeout Example Fails Before Timeout
**File:** `nl_calc/__init__.py` or docs

**Problem:** Example uses expression that fails with `EvaluationError` ("Exponent too large") before timeout due to `MAX_EXPONENT = 10000`.

**Fix:** Change example to one that would actually timeout or add note about limitation.

### 5.12 Memory Functions Return Type Documentation
**File:** `nl_calc/evaluator.py` or docs

**Problem:** Documentation claims functions return `Memory` objects but they actually return `float`.

**Fix:** Rewrite documentation to clarify return types are `float`.

### 5.13 evaluate_raw skip_validation Scope
**File:** `nl_calc/evaluator.py`

**Problem:** Docstring says "skip_validation=True" but it only skips normalization validation, not AST security validation.

**Fix:** Clarify docstring to indicate scope of skip_validation.

### 5.14 _cached_normalize_and_evaluate Visibility
**File:** `nl_calc/evaluator.py`

**Problem:** Not exported and not clearly marked as internal.

**Fix:** Either add to `__all__` if public, or rename with underscore prefix.

### 5.15 Cache Size Documentation Mismatch
**File:** `nl_calc/__init__.py` or docs

**Problem:** Documentation says `cache_size=1000` but actual default is `1024`.

**Fix:** Update documentation to say `cache_size=1024`.

### 5.16 Missing Functions in Documentation
**File:** `architecture/evaluator.md`

**Problem:** `variance_sample`, `conjugate`, `is_prime`, `prime_factors`, `next_prime`, `prev_prime`, `var` not documented.

**Fix:** Document all function aliases and missing functions.

### 5.17 Missing Architecture Items
**File:** `architecture/*.md`

**Problem:** `normalize_expression`, `CONSTANT_WORDS`, `STRIPPED_PHRASES`, `FUNCTION_MAPPINGS`, `TimeoutError`, `get_default_evaluator()`, memory functions not documented.

**Fix:** Add documentation for undocumented data structures and functions.

### 5.18 Variance Sample Not in Functions Dict
**File:** `nl_calc/evaluator.py` line 928

**Problem:** `variance_sample` defined but not exposed to users.

**Fix:** Add to FUNCTIONS dict or document why not exposed.

### 5.19 Undocumented Fields in measure
**File:** `nl_calc/exact/measure.py`

**Problem:** `trailing_whitespace_lines`, `sentences_estimate`, `paragraphs`, `mixed` newline style not documented.

**Fix:** Document all fields in architecture/measure.md.

### 5.20 avg_word_length vs average_word_length
**File:** `nl_calc/exact/measure.py` line 31

**Problem:** Document specifies `avg_word_length` but code has `average_word_length`.

**Fix:** Align field name between docs and code.

### 5.21 max_word_length Missing
**File:** `nl_calc/exact/measure.py`

**Problem:** Document specifies `max_word_length` in WordMetrics but implementation doesn't include it.

**Fix:** Either add to implementation or remove from docs.

### 5.22 Silent Fallthrough in Temperature Conversion
**File:** `nl_calc/units.py`

**Problem:** `100 K` to `ft` might silently give wrong result.

**Fix:** Add validation or warning for invalid temperature conversions.

### 5.23 Typo in Docstring
**File:** `nl_calc/normalize.py:843`

**Problem:** `2meters` → `2 meters`.

**Fix:** Fix typo.

### 5.24 NFKD Equal Not Documented
**File:** `architecture/synthesis.md`

**Problem:** `TextEqualResult` includes `nfkd_equal` but not mentioned in architecture.

**Fix:** Document `nfkd_equal` field.

### 5.25 count_chars Return Type Confusing
**File:** `nl_calc/exact/synthesis.py` lines 570-608

**Problem:** Union return type is confusing.

**Fix:** Consider splitting into two functions.

### 5.26 Graphemes Estimate Unimplemented
**File:** `nl_calc/exact/primitives.py` line 184

**Problem:** `graphemes_estimate` always returns `None`.

**Fix:** Either implement with `unicodedata` or label clearly as unavailable.

### 5.27 Remove Redundant Codepoint Entries
**File:** `nl_calc/exact/unicode_tools.py`

**Problem:** Duplicate entries like `(0x0401, 0x0401, "Cyrillic")` should be removed.

**Fix:** Remove redundant single-codepoint range entries.

## Wave 6: Testing (Parallel with Documentation)

### 6.1 Add Tests for Force/Voltage/Current Conversions
**File:** `tests/`

**Problem:** No tests exist for prefixed unit conversions after UNIT_ALIASES fix.

**Fix:** Add tests verifying `get_conversion_factor("kN", "N")` returns `1000.0`.

### 6.2 Add Test for Temperature Conversion Precision
**File:** `tests/`

**Problem:** No tests for exact temperature offset conversion.

**Fix:** Add test verifying freezing point conversion.

### 6.3 Add Test for "Other" Script Category
**File:** `tests/`

**Problem:** No tests for characters returning "Other" from `unicode_script` (digits, punctuation).

**Fix:** Add tests for `unicode_script()` with digits and punctuation.

### 6.4 Complete Phase 5: Unit Conversion Tests
**File:** `tests/`

**Problem:** Deferred from testing_plan.md.

**Fix:** Complete unit conversion tests using `run()` API (not `evaluate()`).

### 6.5 Complete Phase 6: Natural Language Tests
**File:** `tests/`

**Problem:** Deferred from testing_plan.md.

**Fix:** Complete NL tests using `run()` API (not `evaluate()`).

### 6.6 Complete Phase 7: Test Documentation
**File:** `tests/README.md`

**Problem:** Deferred from testing_plan.md.

**Fix:** Create `tests/README.md` documenting test conventions.

### 6.7 Add MCP Server Integration Tests
**File:** `tests/`

**Problem:** No MCP server tests exist.

**Fix:** Add tests covering protocol handshake, tools/list, tools/call, error handling.

### 6.8 Add Regex Pattern Complexity Limits
**File:** `nl_calc/exact/validate.py` or `nl_calc/mcp/`

**Problem:** ReDoS potential in regex tool.

**Fix:** Add pattern complexity limits or timeout to prevent ReDoS.

### 6.9 Add MAX_EXPRESSION_LENGTH to math_eval
**File:** `nl_calc/mcp/tools.py`

**Problem:** Resource exhaustion possible via math_eval with very long expressions.

**Fix:** Add `MAX_EXPRESSION_LENGTH` limit.

### 6.10 Ensure All Tests Pass
**File:** `tests/`

**Problem:** New tests must not break existing tests.

**Fix:** Run `python -m pytest tests/` and ensure all pass.

## Wave 7: Future Items (Low Priority)

### 7.1 Rust Reimplementation Items (Future)
Future Rust reimplementation may include:
- Statistical functions (mean, median, std, variance)
- Complex number support
- Remaining physical constants
- Unicode normalization
- Casefold comparison
- Mixed script detection
- Compound unit parsing
- Port remaining test suites
- Interactive REPL and extended CLI options

### 7.2 Add Cancel Notification Support
**File:** `nl_calc/mcp/`

**Problem:** `notifications/cancel` and `notifications/progress` not handled.

**Fix:** Add cancel notification support for long-running operations.

### 7.3 Consider Adding confusable_codepoint Field
**File:** `nl_calc/exact/confusables.py`

**Problem:** Consumers may need both character and codepoint representations.

**Fix:** Consider adding `confusable_codepoint` field to ConfusableInfo TypedDict.

### 7.4 Consider Bidirectional Confusable Detection
**File:** `nl_calc/exact/confusables.py`

**Problem:** Currently only catches confusable characters, not Latin characters being used deceptively.

**Fix:** Consider adding bidirectional confusable detection.

### 7.5 Levenshtein vs difflib
**File:** `nl_calc/exact/diff.py`

**Problem:** Current difflib behavior may be insufficient for some use cases.

**Fix:** Optionally refactor to use true Levenshtein-based LCS diff.

### 7.6 Performance Timing Numbers
**File:** `nl_calc/__init__.py` or docs

**Problem:** Unverified performance timing numbers in documentation.

**Fix:** Remove or qualify since they cannot be verified.

---

## Verification Commands

After implementing changes, verify with these commands:

```bash
# Run all tests
python -m pytest tests/

# Verify unit conversion fix (1.1)
python -c "from nl_calc.units import get_conversion_factor; print(get_conversion_factor('kN', 'N'))"  # Should be 1000.0

# Verify temperature fix (1.2)
python -c "from nl_calc.units import convert_temperature; print(convert_temperature(32, 'F', 'C'))"  # Should be 0.0

# Verify newline detection (1.3)
python -c "from nl_calc.exact.measure import line_metrics; print(line_metrics('a\r\nb').newline_style)"  # Should be CRLF

# Verify MCP flag exists (1.5)
python -m nl_calc --help | grep mcp

# Check for lru_cache on _get_script_heuristic (3.3)
python -c "from nl_calc.exact.unicode_tools import _get_script_heuristic; import functools; print(hasattr(_get_script_heuristic, 'cache_info'))"

# Verify mps in UNIT_CATEGORIES (3.4)
python -c "from nl_calc.units import get_unit_category; print(get_unit_category('mps'))"  # Should be 'speed'
```