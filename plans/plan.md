# nl-clicalc Consolidated Implementation Plan

## Status: Implementation Planned

This plan consolidates action items from module architecture reviews. Items are organized by priority and dependencies for efficient parallel implementation.

---

## Wave 1: Critical Bugs (Fix First - Sequential)

### 1.1 REPL History Bug (CLI)
**Files:** `nl_calc/__main__.py:1029`
**Issue:** Line 1029 stores `None` when evaluation fails but `exit_code == 0`; should check if result is not None before appending to history.
**Fix:**
```python
# Before (line ~1029)
if exit_code == 0 and _ is not None:
    history.append((line, _))
```
**Verification:** `python3 -c "from nl_calc import run; run('x', True, True)"` - should not store None

### 1.2 TypedDict `__slots__` Removal (measure.py)
**Files:** `nl_calc/exact/measure.py:26, 38, 52`
**Issue:** `__slots__` has no effect on TypedDict and indicates type confusion.
**Fix:** Remove `__slots__ = [...]` from `WordMetrics`, `LineMetrics`, `CharCategoryMetrics` TypedDict classes.
**Note:** The `__slots__ = [...]` at validate.py:26 and :36 are VALID because those are actual classes (BracketError, CheckBracketsResult) with real implementations - only measure.py TypedDict classes are invalid.

### 1.3 Control Characters Fix (measure.py)
**Files:** `nl_calc/exact/measure.py:242-247`
**Issue:** `control_chars` only counts `Cc` category but should also count `Co` and `Cn`.
**Fix:** Modify counting logic to include all C* categories except Cf.
**Verification:** Test with strings containing various control character types.

### 1.4 Missing `__init__.py` Exports (exact)
**Files:** `nl_calc/exact/__init__.py`
**Issue:** `__all__` lists `unicode_scripts`, `confusables_count`, `longest_common_subsequence` but actual re-export statements don't include them.
**Fix:** Already verified as PRESENT in code (lines 50-52 for unicode_tools exports, lines 70-73 for diff exports). The plan review was incorrect - exports ARE present. No action needed.

### 1.5 Extended Pictographic Range Fix
**Files:** `nl_calc/exact/primitives.py:382`
**Issue:** `_is_extended_pictographic()` uses `0x1FFFF` but max valid Unicode is `0x10FFFF`.
**Fix:** Change `0x1FFFF` to `0x10FFFF` at line 382.
**Verification:** `python3 -c "from nl_calc.exact.primitives import _is_extended_pictographic; print(_is_extended_pictographic(chr(0x1FFFF)))"` should not error.

### 1.6 UnitValue `__rsub__` Bug
**Files:** `nl_calc/units.py:81-84`
**Issue:** `UnitValue(3, "ft") - 5` returns `-2 ft` instead of proper unit-converted result.
**Current code:**
```python
def __rsub__(self, other: Any) -> UnitValue:
    if isinstance(other, UnitValue):
        return other.__sub__(self)
    return UnitValue(other - self.value, self.unit)
```
**Fix:** When `other` is a scalar (not UnitValue), need to handle unit conversion properly. The result should be `UnitValue(other - self.value, self.unit)` but this only works if user intended scalar in feet units. Consider adding warning or converting `other` to same unit first.
**Verification:** `python3 -c "from nl_calc.units import UnitValue; print(UnitValue(3, 'ft') - 5)"` should give meaningful result.

### 1.7 `combine_number_parts()` Logic Error
**Files:** `nl_calc/normalize.py:493-537`
**Issue:** Produces incorrect results for inputs like "ten six" (10-19 range).
**Fix:** Fix boundary handling for single digits, digit sequences, and "ten" special cases.
**Verification:** Write tests for edge cases: "ten six", "five minus ten", "one hundred ten", nested parentheses.

---

## Wave 2: Medium Priority Bugs (Can Parallelize with Wave 1)

### 2.1 MCP `mcp_main` Alias
**Files:** `nl_calc/mcp/server.py:234`
**Issue:** Architecture doc claims `mcp_main` exists but it doesn't in source (only in built file).
**Status:** ALREADY PRESENT at line 234: `mcp_main = main`. No action needed.

### 2.2 `evaluate_cached` Cache Invalidation
**Files:** `nl_calc/evaluator.py`
**Issue:** Variable changes via `setvar` don't affect cached expressions.
**Fix Options:**
1. Add `use_cache: bool = True` parameter
2. Document the behavior clearly
3. Implement cache invalidation on variable changes
**Decision needed:** Document-only vs parameter addition.

### 2.3 `_handle_negative_token()` Bounds Checking
**Files:** `nl_calc/normalize.py`
**Issue:** Potential out-of-bounds access on `tokens[index-2]` and `tokens[index-1]` without sufficient bounds checking.
**Fix:** Add boundary assertions before accessing those indices.
**Verification:** Test cases that exercise negative number handling near start of expression.

### 2.4 BIDI Control Character Handling
**Files:** `nl_calc/exact/unicode_tools.py`
**Issue:** No explicit handling for BIDI control characters (U+202A-U+202E, U+2066-U+2069) - security concern for homograph attacks.
**Fix:** Consider adding explicit detection or warning in `_get_script_heuristic()`.
**Note:** This is a security enhancement, may be low priority.

### 2.5 Variation Selector Detection Inconsistency
**Files:** `nl_calc/exact/primitives.py`
**Issue:** VS Detection inconsistent between `find_invisibles()` (set membership) vs `visible_repr()` (range check).
**Fix:** Standardize to use consistent approach in both functions.
**Note:** `visible_repr()` uses range check `0xFE00 <= cp <= 0xFE0F` which is correct; `find_invisibles()` uses set membership in `_INVISIBLE_CHARS` which also works.

### 2.6 Dead Code Removal
**Files:** `nl_calc/exact/primitives.py:398-446`
**Issue:** `_advance_past_sequence()` never called; duplicates functionality inline in `count_graphemes()`.
**Fix Options:**
1. Remove `_advance_past_sequence()` entirely
2. Integrate into `count_graphemes()` replacing inline code
**Decision needed:** Remove or refactor to use the function.

### 2.7 Remove Redundant Import
**Files:** `nl_calc/evaluator.py:282`
**Issue:** Local import of `convert_temperature` duplicates module-level import.
**Fix:** Remove redundant local import at line ~282.
**Verification:** Ensure all calls to `convert_temperature` still work.

---

## Wave 3: Documentation Corrections (Independent - Can Parallelize)

### 3.1 TypedDict vs NamedTuple Corrections (Multiple Files)
**Files:** `architecture/*.md`
**Issue:** Documentation uses `@dataclass class Xxx(NamedTuple)` but code uses `TypedDict`.
**Fix:** Change all instances to `class Xxx(TypedDict)`.
**Files requiring updates:**
- `architecture/evaluator.md`
- `architecture/measure.md`
- `architecture/diff.md`
- `architecture/validate.md`
- `architecture/unicode_tools.md`
- `architecture/synthesis.md`

### 3.2 `SuccessEnvelope` Usage Decision
**Files:** `nl_calc/mcp/tools.py`, `nl_calc/mcp/schemas.py`, `architecture/mcp.md`
**Issue:** `SuccessEnvelope` defined but never used; `_success_response()` returns plain dict.
**Decision needed:** Either use it consistently OR remove from schemas.py.

### 3.3 Document Missing Functions
**Files:** `architecture/*.md`
**Issue:** Functions exist but undocumented.
**Add documentation for:**
- `unicode_scripts()` (in `unicode_tools.md`, `confusables.md`)
- `confusables_count()` (in `confusables.md`)
- `longest_common_subsequence()` (in `diff.md`)

### 3.4 `text_truncate` Schema Fix
**Files:** `nl_calc/mcp/schemas.py:152-166`
**Issue:** Schema missing output fields.
**Fix:** Update schema to document: `text`, `original_graphemes`, `truncated_graphemes`, `truncated`.

### 3.5 Fix Architecture Doc Cross-References
**Files:** `architecture/*.md`
**Issue:** Various field name mismatches.
**Fix:** Update to match:
- `DiffSpan` fields: doc says `a_start/a_end/b_start/b_end` but actual is `a_span/b_span`
- `RegexTestResult` → `RegexMatch` naming
- `check_brackets` examples show wrong field names
- Add `top_level_keys` to `ValidateJsonResult` documentation

---

## Wave 4: Feature Completeness (Parallel with Wave 3)

### 4.1 Export Memory and Variable Functions
**Files:** `nl_calc/evaluator.py:29-54`
**Status:** ALREADY EXPORTED in `__all__`. Verified present at lines 43-53. No action needed.

### 4.2 Add Missing Public Math Functions
**Files:** `nl_calc/evaluator.py`
**Issue:** Functions documented but not in public API.
**Fix:** Add public wrappers or expose:
- `sign` → add `SIGN` wrapper
- `hypot` → add to FUNCTIONS dict
- `fact` → add as alias for `factorial`
- `lshift`, `rshift` → add public names for bitwise ops
- `prevprime`, `nextprime` → add public names

### 4.3 Add Micro-Unit Categories
**Files:** `nl_calc/units.py`
**Issue:** Missing micro-unit categories.
**Fix:** Add to `UNIT_CATEGORIES`: `uA`, `μA`, `microamp`, `microampere`, `uV`, `μV`, `microvolt`

### 4.4 Add Type Hints to TypedDict Fields
**Files:** `nl_calc/exact/*.py`
**Issue:** TypedDict fields only have names, no type annotations.
**Fix:** Add proper type annotations to all TypedDict definitions.

### 4.5 Document Rankine Temperature Scale
**Files:** `architecture/units.md`
**Issue:** Rankine exists in `UNIT_ALIASES` but not documented.
**Fix:** Add documentation for Rankine temperature scale.

---

## Wave 5: Improvements (Lower Priority - Parallel)

### 5.1 Remove Unused Imports
**Files:** `nl_calc/exact/validate.py`, `nl_calc/exact/synthesis.py`
**Issue:** `signal` import in validate.py unused; `_normalize_unicode` import in synthesis.py unused.
**Fix:** Remove unused imports.

### 5.2 Improve Error Messages in `_validate_node`
**Files:** `nl_calc/evaluator.py`
**Issue:** "Unsupported node type: 'Compare'" is unclear.
**Fix:** Change to "Comparison operators are not supported".

### 5.3 Add `get_unit_category()` to Overview
**Files:** `architecture/overview.md`
**Issue:** Missing from Key Data Structures table.
**Fix:** Add to table around line 262.

### 5.4 Update `SuccessEnvelope` Type Hints
**Files:** `nl_calc/mcp/schemas.py`
**Issue:** Using bare `list[str]` instead of proper type hints.
**Fix:** Use proper type hints for `SuccessEnvelope` and `ErrorEnvelope` fields.

### 5.5 Fix `are_units_compatible()` Unknown Category Handling
**Files:** `nl_calc/units.py`
**Issue:** Returns `True` when one category is known but the other is unknown, allowing invalid unit mixing.
**Fix:** Reconsider handling when one category is known but the other is unknown.

### 5.6 Fix `sentence_pattern` Punctuation Handling
**Files:** `nl_calc/exact/measure.py`
**Issue:** Pattern doesn't handle punctuation followed by non-whitespace (e.g., `"Is it you?You're"`).
**Fix:** Consider pattern like `[.!?]+(?:\s|$)|[.!?]+(?=[A-Z])`.

### 5.7 Add `accent_or_diacritic_difference` to `explain_diff`
**Files:** `nl_calc/exact/synthesis.py`
**Issue:** `explain_diff` sets `"compatibility_normalization_only"` but should also handle accent/diacritic classification.
**Fix:** Add handling for `"accent_or_diacritic_difference"` case.

### 5.8 `_classify_difference` Logic Fix
**Files:** `nl_calc/exact/synthesis.py`
**Issue:** `"unicode_normalization_only"` classification is unreachable via normal flow.
**Fix:** Restructure logic so we return on `casefold_equal` before checking `nfc_equal`.

### 5.9 `list_compare` Duplicate Near Matches
**Files:** `nl_calc/exact/synthesis.py`
**Issue:** Items can appear in `near_matches` twice with different classifications.
**Fix:** Deduplicate near_matches by codepoint position.

### 5.10 Remove Redundant Assignment in `explain_diff`
**Files:** `nl_calc/exact/synthesis.py:414`
**Issue:** Duplicate `same_length_codepoints = len(a) == len(b)`.
**Fix:** Remove duplicate assignment.

---

## Deferred Items (Future Enhancement)

| Item | Description | Reason |
|------|-------------|--------|
| D1 | Include Cf in control_chars | Intentional per UTS #55 - format chars are silently ignored |
| D2 | Full TypedDict `__slots__` | Only validate.py and measure.py needed; other files have few instances |
| D3 | Grapheme counting | Requires complex Unicode grapheme cluster implementation |
| D4 | max_word_length feature | `average_word_length` available; max is rarely needed |
| D5 | Statistical functions (mean, median, std, variance) | Low priority - external libraries available |
| D6 | Compound unit parsing | Complex to implement correctly |
| D7 | Cancel notification support for MCP | Currently not supported |
| D8 | Bidirectional confusable detection | Complex Unicode security area |

---

## Parallelization Strategy

**Wave 1 (Critical Bugs):** Execute sequentially - fixes may depend on each other
**Wave 2 (Medium Bugs):** Can start once Wave 1 is 50% complete
**Wave 3 (Documentation):** Can run in parallel with Wave 2 - no code dependencies
**Wave 4 (Features):** Can run in parallel with Wave 3 - no code dependencies
**Wave 5 (Improvements):** Can run in parallel with Wave 4 - no code dependencies

**Suggested Agent Assignment:**
- Agent A: Wave 1 + Wave 2 (critical bugs)
- Agent B: Wave 3 (documentation fixes)
- Agent C: Wave 4 (feature completeness)
- Agent D: Wave 5 (improvements)

---

## Verification Commands

```bash
# Run all tests
python3 -m pytest tests/

# Verify specific functionality
python3 -c "from nl_calc.exact import unicode_scripts, confusables_count, longest_common_subsequence; print('Exports OK')"
python3 -c "from nl_calc.evaluator import evaluate, memory_store; memory_store('x', 5); print(evaluate('x * 2'))"
```

---

## Notes

- All changes must work with `build_single.py` assembling modules into `nl_calc.py`
- Standard library only - no external packages
- Use type annotations for function signatures
- All code must pass lint/typecheck if configured