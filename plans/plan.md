# nl-clicalc Consolidated Implementation Plan

## Status: Completed

Consolidated from all module review files. Contains all actionable items from:
- normalize_review.md, primitives_review.md, units_review.md
- synthesis_review.md, cli_review.md, measure_review.md
- evaluator_review.md, confusables_review.md, validate_review.md
- diff_review.md, unicode_tools_review.md, mcp_server_review.md

Wave 1: Critical bugs (4 items)
Wave 2: CLI/REPL fixes (3 items)
Wave 3: Documentation consistency (7 items)
Wave 4: Security and robustness (5 items)
Wave 5: Code quality (10 items)
Wave 6: Feature completeness (9 items)
Wave 7: Deferred future items
Wave 8: Low priority improvements

---

## Wave 1: Critical Bugs (Parallelizable - 4 items, run 4 subagents)

### 1.1 Fix Temperature Conversion in UnitValue.convert_to()
**File:** `nl_calc/units.py`

**Problem:** `UnitValue.convert_to()` warns about temperature conversions but uses multiplicative approach instead of offset-based formula. Temperature units (K, C, F, R) are not in UNIT_CONVERSIONS and `convert_temperature()` is not called.

**Action:** Modify `convert_to()` to detect when both source and target are temperature units and call `convert_temperature()` directly instead of doing `value * factor`.

**Verification:**
```python
python3 -c "from nl_calc.units import UnitValue; u = UnitValue(32, 'F'); print(u.convert_to('C'))"  # Should work
```

---

### 1.2 Fix kilonewton Alias
**File:** `nl_calc/units.py` (line ~923)

**Problem:** `kilonewton` alias maps to `N` instead of `kN`.

**Action:** Update alias to map to `kN`.

**Verification:**
```python
python3 -c "from nl_calc.units import get_conversion_factor; print(get_conversion_factor('kN', 'N'))"  # Should be 1000.0
```

---

### 1.3 Fix _cbrt() for Complex Number Support
**File:** `nl_calc/evaluator.py`

**Problem:** `_cbrt()` doesn't support complex numbers; negative cube roots fail with TypeError when compared with `>=`.

**Action:** Apply `_complex_aware` decorator pattern (similar to `_sqrt`) to `_cbrt()`.

**Verification:**
```python
python3 -c "from nl_calc.evaluator import evaluate; print(evaluate('cbrt(-8)')}"  # Should return (-2+0j) or similar
```

---

### 1.4 Add Complex-Aware Hyperbolic Functions
**File:** `nl_calc/evaluator.py`

**Problem:** `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` in FUNCTIONS use `math.*` directly instead of `_complex_aware` wrappers. Documentation claims these work with complex numbers but they fail.

**Action:** Change FUNCTIONS entries to use `_complex_aware` wrappers:
```python
_sinh = _complex_aware(math.sinh, cmath.sinh)
_cosh = _complex_aware(math.cosh, cmath.cosh)
_tanh = _complex_aware(math.tanh, cmath.tanh)
_asinh = _complex_aware(math.asinh, cmath.asinh)
_acosh = _complex_aware(math.acosh, cmath.acosh)
_atanh = _complex_aware(math.atanh, cmath.atanh)
```

**Verification:**
```python
python3 -c "from nl_calc.evaluator import evaluate; print(evaluate('sinh(1+2j)')}"  # Should work
```

---

## Wave 2: CLI and REPL Fixes (Parallelizable)

### 2.1 Fix Verbose Mode Flag
**File:** `nl_calc/__main__.py`

**Problem:** `-v` is `--version`, not verbose; no `--verbose` flag exists.

**Action:** Add proper `--verbose` flag or rename `-v` handling.

**Verification:**
```bash
python3 -m nl_calc --verbose "5 + 3"  # Should show expression
```

---

### 2.2 Fix REPL Default show_expression
**File:** `nl_calc/__main__.py`

**Problem:** Interactive mode should show expressions by default but doesn't.

**Action:** Set default `show_expression=True` for REPL mode.

**Verification:**
```bash
echo "5 + 3" | python3 -m nl_calc -i  # Should show expression
```

---

### 2.3 Clarify -e Flag Description
**File:** `nl_calc/__main__.py` and architecture docs

**Problem:** Architecture says "(quiet mode)" but behavior differs.

**Action:** Update documentation to match actual `-e` behavior.

---

## Wave 3: Documentation vs Implementation Consistency (Parallelizable)

### 3.1 Fix measure.py max_word_length Documentation
**File:** `nl_calc/exact/measure.py`

**Problem:** Documentation shows `max_word_length` in example but not in implementation.

**Action:** Either implement `max_word_length` feature or remove from documentation.

**Verification:**
```python
python3 -c "from nl_calc.exact.measure import measure_text; print(measure_text('hello world', max_word_length=5))"
```

---

### 3.2 Add missing check_brackets Return Type Documentation
**File:** `nl_calc/exact/validate.py`

**Problem:** The `CheckBracketsResult` TypedDict and documentation could be more clear about return structure.

**Action:** Ensure documentation clearly shows all three fields returned: `balanced`, `unmatched_openers`, `unmatched_closers`.

**Verification:**
```python
python3 -c "from nl_calc.exact.validate import check_brackets; print(check_brackets('(())'))"
```

---

### 3.3 Document TEMPERATURE_CONVERSIONS
**File:** `nl_calc/units.py` and architecture docs

**Problem:** Architecture omits separate temperature handling mechanism.

**Action:** Document `TEMPERATURE_CONVERSIONS` constant and temperature conversion flow.

---

### 3.4 Add CGJ/MVS/SHY to Primitives Documentation
**File:** `nl_calc/exact/primitives.py` and architecture docs

**Problem:** U+034F (CGJ) and U+180E (MVS) in `_INVISIBLE_CHARS` but missing from architecture doc.

**Action:** Update architecture documentation to include these characters.

---

### 3.5 Fix diff_spans Algorithm Documentation
**File:** `nl_calc/exact/diff.py`

**Problem:** Documentation claims Levenshtein but uses SequenceMatcher.

**Action:** Update documentation to accurately describe difflib-based approach.

---

### 3.6 Add longest_common_subsequence() Function
**File:** `nl_calc/exact/diff.py`

**Problem:** Documented but missing from implementation.

**Action:** Implement `longest_common_subsequence()` function.

---

### 3.7 Fix unicode_script() Documentation
**File:** `nl_calc/exact/unicode_tools.py`

**Problem:** Documentation claims Unicode script property with fallback but only uses heuristic.

**Action:** Update documentation to accurately describe heuristic-based approach.

---

## Wave 4: Security and Robustness Fixes (Parallelizable)

### 4.1 Include Cf Characters in control_chars Count
**File:** `nl_calc/exact/measure.py`

**Problem:** Cf (format) characters not included in `control_chars` for invisible character detection.

**Action:** Consider including Cf characters for proper invisible character detection.

**Verification:**
```python
python3 -c "from nl_calc.exact.measure import measure_text; print(measure_text('\ufeff'))"  # Cf test
```

---

### 4.2 Add Type Check for Bitwise Operations
**File:** `nl_calc/evaluator.py`

**Problem:** Bitwise operations silently truncate floats.

**Action:** Add type check that prevents float-to-int silent truncation.

**Verification:**
```python
python3 -c "from nl_calc.evaluator import evaluate; print(evaluate('5.5 & 3'))"  # Should error
```

---

### 4.3 Add Near-Zero Check in _as_percent()
**File:** `nl_calc/evaluator.py`

**Problem:** Near-zero division could cause overflow.

**Action:** Add near-zero check for overflow prevention.

---

### 4.4 Fix Negative Nesting Depth in Pattern Complexity
**File:** `nl_calc/exact/validate.py`

**Problem:** Negative nesting depth in `_check_pattern_complexity` could bypass ReDoS protection.

**Action:** Ensure depth never goes negative.

---

### 4.5 Fix Header Detection in Confusables Generator
**File:** `scripts/generate_confusables.py`

**Problem:** Valid codepoints starting with "0" could be skipped.

**Action:** Fix header detection logic to handle zero-prefixed codepoints.

---

## Wave 5: Code Quality and Polish (Parallelizable)

### 5.1 Remove Redundant WORD JOINER Code
**File:** `nl_calc/exact/primitives.py` (lines 277-278)

**Problem:** Lines 277-278 never reached; WORD JOINER already handled by dict lookup.

**Action:** Refactor to let dict handle all BIDI chars, remove redundant code.

**Verification:**
```python
python3 -c "from nl_calc.exact.primitives import visible_repr; print(visible_repr('\u2060'))"  # Should work
```

---

### 5.2 Move import re to Module Level
**File:** `nl_calc/exact/measure.py`

**Problem:** `import re` inside function instead of module level.

**Action:** Move import to top of file.

---

### 5.3 Remove or Document DEBUG Flag
**File:** `nl_calc/exact/validate.py`

**Problem:** DEBUG flag causes side effects.

**Action:** Remove flag or document its behavior.

---

### 5.4 Add confusables_count() Helper
**File:** `nl_calc/exact/unicode_tools.py`

**Problem:** No fast helper for counting confusables without building full list. NOTE: confusables.py is auto-generated data, not the place for this helper.

**Action:** Add `confusables_count()` function to `unicode_tools.py`.

---

### 5.6 Document max_len and max_diffs Parameters
**File:** `nl_calc/exact/diff.py`

**Problem:** `max_len=10000` and `max_diffs=50` parameters not documented.

**Action:** Add parameter documentation.

---

### 5.7 Add SuccessEnvelope Consistency
**File:** `nl_calc/mcp/schemas.py` and `nl_calc/mcp/tools.py`

**Problem:** `SuccessEnvelope` TypedDict inconsistent usage.

**Action:** Use consistently or remove.

---

### 5.8 Remove Redundant Double Length Check
**File:** `nl_calc/mcp/tools.py` (lines 77-80)

**Problem:** Redundant check of MAX_TEXT_LENGTH vs MAX_EXPRESSION_LENGTH.

**Action:** Remove redundant check.

---

### 5.9 Add TypedDict __slots__ to Correct Files
**Files:** `nl_calc/exact/validate.py`, `nl_calc/exact/measure.py`, `nl_calc/exact/unicode_tools.py`, `nl_calc/exact/diff.py`, `nl_calc/exact/synthesis.py`

**Problem:** TypedDict classes could benefit from __slots__ for memory efficiency. NOTE: confusables.py is a data file with no TypedDict classes - the TypedDicts are in other files.

**Action:** Add __slots__ for memory efficiency to TypedDict classes in correct files.

---

### 5.10 Add Type Guard for Self-Mapping Confusables
**File:** `nl_calc/exact/unicode_tools.py`

**Problem:** No type guard for self-mapping confusables (character maps to itself).

**Action:** Add type guard function to filter out self-mappings in `detect_confusables()`.

---

## Wave 6: Feature Completeness (Parallelizable)

### 6.1 Implement accent_or_diacritic_difference Classification
**File:** `nl_calc/exact/synthesis.py`

**Problem:** Documented but not implemented; code uses `case_only` instead.

**Action:** Implement proper `accent_or_diacritic_difference` classification.

---

### 6.2 Implement graphemes Counting
**File:** `nl_calc/exact/synthesis.py`

**Problem:** `graphemes: None` always hardcoded.

**Action:** Implement actual grapheme count or remove from TypedDict.

---

### 6.3 Add Batch unicode_scripts() Function
**File:** `nl_calc/exact/unicode_tools.py`

**Problem:** Only single script detection exists.

**Action:** Add `unicode_scripts()` for batch processing.

---

### 6.4 Expand Script Range Coverage
**File:** `nl_calc/exact/unicode_tools.py`

**Problem:** Missing Thai, Korean Hangul, Georgian, Armenian, Cherokee, Canadian Aboriginal.

**Action:** Add script support for these scripts.

---

### 6.5 Document "Other" Script Exclusion Behavior
**File:** `nl_calc/exact/unicode_tools.py`

**Problem:** Mixed script detection "Other" behavior undocumented.

**Action:** Document in `detect_mixed_scripts()` docstring.

---

### 6.6 Fix common_prefix_suffix Doc Examples
**File:** `nl_calc/exact/diff.py`

**Problem:** Doc examples have wrong values (prefix=3→4, suffix=0→3).

**Action:** Fix docstring examples.

---

### 6.7 Add Docstring Example for common_prefix_suffix
**File:** `nl_calc/exact/diff.py`

**Problem:** Missing example for overlap prevention.

**Action:** Add docstring example showing overlap handling.

---

### 6.8 Add max_word_length Feature
**File:** `nl_calc/exact/measure.py`

**Problem:** Parameter documented but not implemented.

**Action:** Implement feature if needed, or clarify limitation.

---

### 6.9 Align control_chars with Documentation
**File:** `nl_calc/exact/measure.py`

**Problem:** Cf exclusion inconsistent with documentation.

**Action:** Clarify Cf handling in documentation.

---

## Wave 7: Deferred Future Items (Low Priority)

### 7.1 Rust Reimplementation Candidates
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

**Action:** Add cancel notification support for long-running operations.

---

### 7.3 Consider Adding confusable_codepoint Field
**File:** `nl_calc/exact/unicode_tools.py` (ConfusableInfo TypedDict is here, not in confusables.py)

**Problem:** Consumers may need both character and codepoint representations.

**Action:** Consider adding `confusable_codepoint` field to ConfusableInfo TypedDict.

---

### 7.4 Consider Bidirectional Confusable Detection
**File:** `nl_calc/exact/unicode_tools.py`

**Problem:** Currently only catches confusable characters, not Latin characters being used deceptively.

**Action:** Consider adding bidirectional confusable detection.

---

### 7.5 Levenshtein vs difflib Refactor
**File:** `nl_calc/exact/diff.py`

**Problem:** Current difflib behavior may be insufficient for some use cases.

**Action:** Optionally refactor to use true Levenshtein-based LCS diff.

---

### 7.6 Performance Timing Numbers
**File:** `nl_calc/__init__.py` or docs

**Problem:** Unverified performance timing numbers in documentation.

**Action:** Remove or qualify since they cannot be verified.

---

## Wave 8: Additional Low Priority Improvements

### 8.1 Refactor visible_repr() for Clarity
**File:** `nl_calc/exact/primitives.py`

**Problem:** Overlapping checks in visible_repr().

**Action:** Consolidate checks for clarity.

---

### 8.2 Add typing.Literal for Normalization Forms
**File:** `nl_calc/exact/primitives.py`

**Problem:** Could use better type safety for `normalize_unicode()`.

**Action:** Add `typing.Literal` for normalization forms.

---

### 8.3 Fix kilonewton Prefix Handling
**File:** `nl_calc/units.py`

**Problem:** Should follow pattern of other prefixed units.

**Action:** Ensure consistent prefix handling.

---

### 8.4 Remove Redundant --usage Flag
**File:** `nl_calc/__main__.py`

**Problem:** Same as `-h`/`--help`.

**Action:** Remove redundant flag or consolidate.

---

### 8.5 Shell Glob Detection Improvement
**File:** `nl_calc/__main__.py`

**Problem:** Only checks first arg for glob patterns.

**Action:** Improve glob detection for multi-file scenarios.

---

### 8.6 Add Edge Case Tests for Primitives
**File:** `tests/`

**Problem:** No tests for empty strings, only-invisible strings, all VS, all BIDI chars.

**Action:** Add comprehensive edge case tests.

---

### 8.7 Document degrees/radians Complex Limitation
**File:** `nl_calc/evaluator.py`

**Problem:** `degrees`/`radians` not complex-aware not documented.

**Action:** Add documentation noting complex number limitation.

---

### 8.8 Add Mixed-Script Threshold Option
**File:** `nl_calc/exact/unicode_tools.py`

**Problem:** Mixed script detection has fixed threshold.

**Action:** Add threshold configuration option.

---

### 8.9 Document BracketError and RegexMatch Types
**File:** `nl_calc/exact/validate.py`

**Problem:** Types not documented.

**Action:** Add type documentation.

---

### 8.10 Document normalize_main Alias Behavior
**File:** `nl_calc/__main__.py` or build docs

**Problem:** `normalize_main` alias only exists via build script, not at runtime.

**Action:** Document this build-time behavior.

---

### 8.11 Document mcp_main Build-Time Alias
**File:** `build_single.py` and docs

**Problem:** `mcp_main` is build-time alias, not native export.

**Action:** Document this build-time behavior clearly.

---

### 8.12 count_chars Documentation
**File:** `nl_calc/exact/synthesis.py`

**Problem:** Normalization behavior unclear.

**Action:** Improve docstring documentation.

---

### 8.13 Add Complex-Aware Hyperbolic Functions
**File:** `nl_calc/evaluator.py`

**Problem:** Hyperbolic functions not complex-aware.

**Action:** Add complex-aware wrappers for sinh, cosh, tanh, etc.

---

### 8.14 Consolidate Duplicate Data Structures Section
**File:** Architecture docs for normalize

**Problem:** Architecture doc has duplicate sections (38-76 and 82-102).

**Action:** Consolidate into single section.

---

## Verification Commands

```bash
# Run all tests
python3 -m pytest tests/

# Verify kilonewton fix (1.2)
python3 -c "from nl_calc.units import get_conversion_factor; print(get_conversion_factor('kN', 'N'))"

# Verify temperature fix (1.1)
python3 -c "from nl_calc.units import convert_temperature; print(convert_temperature(32, 'F', 'C'))"

# Verify newline detection
python3 -c "from nl_calc.exact.measure import line_metrics; print(line_metrics('a\r\nb').newline_style)"

# Verify MCP flag
python3 -m nl_calc --help | grep mcp

# Check for lru_cache on _get_script_heuristic
python3 -c "from nl_calc.exact.unicode_tools import _get_script_heuristic; import functools; print(hasattr(_get_script_heuristic, 'cache_info'))"

# Verify mps in UNIT_CATEGORIES
python3 -c "from nl_calc.units import get_unit_category; print(get_unit_category('mps'))"
```

---

## Parallelization Strategy

### Wave 1 (Critical Bugs - 4 items, run 4 subagents in parallel)
- Agent A: 1.1 Temperature conversion in UnitValue.convert_to()
- Agent B: 1.2 kilonewton alias fix
- Agent C: 1.3 _cbrt complex number support
- Agent D: 1.4 Complex-aware hyperbolic functions

### Wave 2 (CLI/REPL Fixes - 3 items)
Can run in parallel with 2-3 subagents:
- 2.1 Add --verbose flag or repurpose -v
- 2.2 Fix REPL default show_expression
- 2.3 Clarify -e flag description

### Wave 3 (Documentation vs Implementation - 7 items)
Mostly independent, can parallelize:
- 3.1 Fix measure.py max_word_length documentation
- 3.2 Add check_brackets return type documentation
- 3.3 Document TEMPERATURE_CONVERSIONS
- 3.4 Add CGJ/MVS/SHY to primitives documentation
- 3.5 Fix diff_spans algorithm documentation
- 3.6 Add longest_common_subsequence() function
- 3.7 Fix unicode_script() documentation

### Wave 4 (Security and Robustness - 5 items)
- 4.1 Include Cf characters in control_chars count
- 4.2 Add type check for bitwise operations
- 4.3 Add near-zero check in _as_percent()
- 4.4 Fix negative nesting depth in pattern complexity
- 4.5 Fix header detection in confusables generator

### Wave 5 (Code Quality - 10 items)
All independent, can run many in parallel. See individual items.

### Wave 6 (Feature Completeness - 9 items)
All independent, can run many in parallel. See individual items.

### Wave 7 (Deferred Future) and Wave 8 (Low Priority)
Can be worked on incrementally as time permits.