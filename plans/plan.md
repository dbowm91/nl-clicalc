# nl-clicalc Consolidated Implementation Plan

## Status: Implementation Planned

This plan consolidates action items from module architecture reviews. Items are organized by priority and dependencies for efficient parallel implementation.

---

## Wave 1: Critical Bugs (Sequential - Fix First)

These items must be fixed before dependent work begins. They involve potential runtime errors or incorrect behavior.

### 1.1 REPL History Bug (CLI)
**Files:** `nl_calc/normalize.py:1028-1029`
**Issue:** Line 1029 stores `None` when evaluation fails but `exit_code == 0`; should check if result is not None before appending to history.
**Current code:**
```python
if exit_code == 0 and _ is not None:
    history.append((line, _))
```
**Fix:** No code change needed - verification shows condition already checks `_ is not None`. Verify behavior with: `python3 -c "from nl_calc import run; run('x', True, True)"` - should not store None.

### 1.2 TypedDict `__slots__` Removal (measure.py)
**Files:** `nl_calc/exact/measure.py:26, 38, 52`
**Issue:** `__slots__` has no effect on TypedDict and indicates type confusion.
**Fix:** Remove `__slots__ = [...]` from `WordMetrics`, `LineMetrics`, `CharCategoryMetrics` TypedDict classes.
**Important:** The `__slots__ = [...]` at `validate.py:26` and `:36` on `BracketError` and `CheckBracketsResult` are VALID because those are actual classes (with implementations), not TypedDicts. Only measure.py TypedDicts need fixing.

### 1.3 Control Characters Fix (measure.py)
**Files:** `nl_calc/exact/measure.py:233-238`
**Issue:** `control_chars` only counts `Cc` category but documentation says it should count all C* categories except Cf (per UTS #55).
**Current code:**
```python
elif cat.startswith("C"):  # Other (control, format, etc.)
    if cat == "Cc":  # Control characters
        control_chars += 1
    elif cat == "Cf":  # Format characters (e.g., U+FEFF BOM)
        pass  # Cf excluded from control_chars count per UTS #55
    # Other C* (like surrogate) skip
```
**Fix:** Change to count Co (奇昇字符 - chars with no assigned category) and Cn (surrogates) as control_chars as well, while maintaining Cf exclusion.
**Verification:** Test with strings containing various control character types.

### 1.4 Extended Pictographic Range Fix
**Files:** `nl_calc/exact/primitives.py:382`
**Issue:** `_is_extended_pictographic()` uses `0x1FFFF` but max valid Unicode is `0x10FFFF`.
**Fix:** Change `0x1FFFF` to `0x10FFFF` at line 382.
**Verification:** `python3 -c "from nl_calc.exact.primitives import _is_extended_pictographic; print(_is_extended_pictographic(chr(0x1FFFF)))"` should not error.

### 1.5 UnitValue `__rsub__` Bug
**Files:** `nl_calc/units.py:81-84`
**Issue:** `UnitValue(3, "ft") - 5` returns `-2 ft` instead of proper unit-converted result.
**Current code:**
```python
def __rsub__(self, other: Any) -> UnitValue:
    if isinstance(other, UnitValue):
        return other.__sub__(self)
    return UnitValue(other - self.value, self.unit)
```
**Fix:** When `other` is a scalar (not UnitValue), need to handle unit conversion properly. Consider converting `other` to match self's unit first, then subtracting. The result should be `UnitValue(other - self.value, self.unit)` but this only works if user intended scalar in feet units.
**Verification:** `python3 -c "from nl_calc.units import UnitValue; print(UnitValue(3, 'ft') - 5)"` should give meaningful result.

### 1.6 `combine_number_parts()` Logic Error
**Files:** `nl_calc/normalize.py:493-537`
**Issue:** Produces incorrect results for inputs like "ten six" (10-19 range).
**Fix:** Fix boundary handling for single digits, digit sequences, and "ten" special cases.
**Verification:** Write tests for edge cases: "ten six", "five minus ten", "one hundred ten", nested parentheses.

### 1.7 `_handle_negative_token()` Bounds Checking
**Files:** `nl_calc/normalize.py:650-660`
**Issue:** Potential out-of-bounds access on `tokens[index-2]` and `tokens[index-1]` without sufficient bounds checking.
**Current code:**
```python
def _handle_negative_token(tokens: list, index: int, patterns: Mapping[str, Pattern[str]]) -> tuple[list, list]:
    temp = tokens[index].split("-")
    tokens[index - 2] = f"{tokens[index - 2]}.{temp[0]}"
    tokens[index - 1] = ""
    tokens[index] = f"-{temp[1]}"
    return tokens, [index - 1]
```
**Fix:** Add boundary assertions or guards before accessing `tokens[index-2]` and `tokens[index-1]`. The function is only called when `index >= 2`, but we should still verify `tokens[index-2]` and `tokens[index-1]` exist.
**Verification:** Test cases that exercise negative number handling near start of expression.

---

## Wave 2: Medium Priority Bugs (Parallel with Wave 1, can start when Wave 1 is 50% complete)

### 2.1 BIDI Control Character Handling
**Files:** `nl_calc/exact/unicode_tools.py`
**Issue:** No explicit handling for BIDI control characters (U+202A-U+202E, U+2066-U+2069) - security concern for homograph attacks.
**Fix:** Consider adding explicit detection or warning in `_get_script_heuristic()` or add to invisible character tracking.
**Note:** This is a security enhancement, may be low priority.

### 2.2 Variation Selector Detection Inconsistency
**Files:** `nl_calc/exact/primitives.py`
**Issue:** VS Detection inconsistent between `find_invisibles()` (set membership) vs `visible_repr()` (range check).
**Fix:** Standardize to use consistent approach in both functions.
**Note:** `visible_repr()` uses range check `0xFE00 <= cp <= 0xFE0F` which is correct; `find_invisibles()` uses set membership in `_INVISIBLE_CHARS` which also works. Verify both approaches are correct and document why they differ.

### 2.3 `_advance_past_sequence()` Dead Code
**Files:** `nl_calc/exact/primitives.py:398-446`
**Issue:** `_advance_past_sequence()` function defined but never called directly (only referenced in comment). Its functionality is duplicated inline in `count_graphemes()`.
**Fix Options:**
1. Remove `_advance_past_sequence()` entirely
2. Integrate into `count_graphemes()` replacing inline code
**Decision needed:** Remove or refactor to use the function. The inline code in `count_graphemes()` (lines 473-505) handles the same logic.

### 2.4 Redundant Local Import in `_convert`
**Files:** `nl_calc/evaluator.py:293`
**Issue:** Local import of `convert_temperature` at line 293 duplicates module-level import at line 25.
**Fix:** Remove redundant local import at line ~293.
**Verification:** Ensure all calls to `convert_temperature` still work (the module-level import handles most cases; the local import is for a specific code path).

### 2.5 `evaluate_cached` Cache Invalidation
**Files:** `nl_calc/evaluator.py:138`
**Issue:** Variable changes via `setvar` don't affect cached expressions.
**Fix Options:**
1. Add `use_cache: bool = True` parameter to `evaluate_cached`
2. Document the behavior clearly
3. Implement cache invalidation on variable changes
**Decision needed:** Document-only vs parameter addition.

---

## Wave 3: Documentation Corrections (Independent - Can Parallelize with Wave 2)

### 3.1 TypedDict vs NamedTuple Corrections (Multiple Files)
**Files:** `architecture/*.md`
**Issue:** Documentation uses `@dataclass class Xxx(NamedTuple)` but code uses `class Xxx(TypedDict)`.
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
- `DiffSpan` fields: doc says `a_start/a_end/b_start/b_end` but actual is `a_span/b_span` (list of 2 ints)
- `RegexTestResult` → `RegexMatch` naming
- `check_brackets` examples show wrong field names
- Add `top_level_keys` to `ValidateJsonResult` documentation

---

## Wave 4: Feature Completeness (Parallel with Wave 3)

### 4.1 Add Missing Public Math Functions
**Files:** `nl_calc/evaluator.py`
**Issue:** Functions documented but not in public API.
**Fix:** Add public wrappers or expose:
- `sign` → add `SIGN` wrapper
- `hypot` → add to FUNCTIONS dict
- `fact` → add as alias for `factorial`
- `lshift`, `rshift` → add public names for bitwise ops
- `prevprime`, `nextprime` → add public names

### 4.2 Add Micro-Unit Categories
**Files:** `nl_calc/units.py`
**Issue:** Missing micro-unit categories.
**Fix:** Add to `UNIT_CATEGORIES`: `uA`, `μA`, `microamp`, `microampere`, `uV`, `μV`, `microvolt`, `microampere`

### 4.3 Add Type Hints to TypedDict Fields
**Files:** `nl_calc/exact/*.py`
**Issue:** TypedDict fields only have names, no type annotations.
**Fix:** Add proper type annotations to all TypedDict definitions.

### 4.4 Document Rankine Temperature Scale
**Files:** `architecture/units.md`
**Issue:** Rankine exists in `UNIT_ALIASES` but not documented.
**Fix:** Add documentation for Rankine temperature scale.

### 4.5 `get_unit_category()` in Overview
**Files:** `architecture/overview.md`
**Issue:** Missing from Key Data Structures table.
**Fix:** Add to table around line 262.

---

## Wave 5: Improvements (Lower Priority - Parallel)

### 5.1 Remove Unused Imports
**Files:** `nl_calc/exact/validate.py`, `nl_calc/exact/synthesis.py`
**Issue:** `signal` import in validate.py unused (the `signal` in synthesis.py is from the docstring "Unicode risk signals", not the Python module). Actually `signal` module is not imported anywhere in validate.py based on current code.
**Fix:** Verify and remove any truly unused imports.

### 5.2 Improve Error Messages in `_validate_node`
**Files:** `nl_calc/evaluator.py`
**Issue:** "Unsupported node type: 'Compare'" is unclear.
**Fix:** Change to "Comparison operators are not supported".

### 5.3 Update `SuccessEnvelope` Type Hints
**Files:** `nl_calc/mcp/schemas.py`
**Issue:** Using bare `list[str]` instead of proper type hints.
**Fix:** Use proper type hints for `SuccessEnvelope` and `ErrorEnvelope` fields.

### 5.4 Fix `are_units_compatible()` Unknown Category Handling
**Files:** `nl_calc/units.py`
**Issue:** Returns `True` when one category is known but the other is unknown, allowing invalid unit mixing.
**Fix:** Reconsider handling when one category is known but the other is unknown.

### 5.5 Fix `sentence_pattern` Punctuation Handling
**Files:** `nl_calc/exact/measure.py`
**Issue:** Pattern doesn't handle punctuation followed by non-whitespace (e.g., `"Is it you?You're"`).
**Fix:** Consider pattern like `[.!?]+(?:\s|$)|[.!?]+(?=[A-Z])`.

### 5.6 Add `accent_or_diacritic_difference` to `explain_diff`
**Files:** `nl_calc/exact/synthesis.py`
**Issue:** `explain_diff` sets `"compatibility_normalization_only"` but should also handle accent/diacritic classification via `_classify_difference`.
**Fix:** Verify handling for `"accent_or_diacritic_difference"` case - code at line 506 shows it IS handled. Verify explain_diff uses it properly.

### 5.7 `_classify_difference` Logic Fix
**Files:** `nl_calc/exact/synthesis.py`
**Issue:** `"unicode_normalization_only"` classification at line 340 may be unreachable via normal flow because casefold_equal check (line 334) comes first and returns "case_only".
**Fix:** Restructure logic so we return on `casefold_equal` before checking `nfc_equal`. Actually the code at lines 337-340 already checks `nfc_equal` inside a block that follows the `casefold_equal` block - verify this is correct.

### 5.8 `list_compare` Duplicate Near Matches
**Files:** `nl_calc/exact/synthesis.py`
**Issue:** Items can appear in `near_matches` twice with different classifications.
**Fix:** Deduplicate near_matches by codepoint position.

### 5.9 Remove Redundant Assignment in `explain_diff`
**Files:** `nl_calc/exact/synthesis.py:414`
**Issue:** Duplicate `same_length_codepoints = len(a) == len(b)` at lines 392 and 414.
**Fix:** Remove duplicate assignment or use one consistent location.

### 5.10 `visible_repr()` vs `find_invisibles()` VS Handling
**Files:** `nl_calc/exact/primitives.py`
**Issue:** Variation selector (VS) detection differs between `visible_repr()` (lines 273-274) and `find_invisibles()` (set membership).
**Fix:** Verify both approaches are semantically equivalent and document why they differ, OR standardize to use a common helper function.

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
- Agent A: Wave 1 (critical bugs) - sequential
- Agent B: Wave 2 (medium bugs) - parallel with A
- Agent C: Wave 3 (documentation fixes) - parallel with B
- Agent D: Wave 4 (feature completeness) - parallel with C
- Agent E: Wave 5 (improvements) - parallel with D

---

## Verification Commands

```bash
# Run all tests
python3 -m pytest tests/

# Verify specific functionality
python3 -c "from nl_calc.exact import unicode_scripts, confusables_count, longest_common_subsequence; print('Exports OK')"
python3 -c "from nl_calc.evaluator import evaluate, memory_store; memory_store('x', 5); print(evaluate('x * 2'))"
python3 -c "from nl_calc import run; run('x', True, True)"  # REPL history test
python3 -c "from nl_calc.units import UnitValue; print(UnitValue(3, 'ft') - 5)"  # __rsub__ test
```

---

## Notes

- All changes must work with `build_single.py` assembling modules into `nl_calc.py`
- Standard library only - no external packages
- Use type annotations for function signatures
- All code must pass lint/typecheck if configured
- TypedDict classes do NOT support `__slots__` - only regular classes (with actual implementations) do
- `BracketError` and `CheckBracketsResult` in validate.py ARE regular classes (not TypedDict) and DO support `__slots__`

---

## Detailed Implementation Guidance

### For Wave 1 (Critical Bugs)

**1.2 TypedDict `__slots__` Removal:**
When removing `__slots__` from TypedDict classes in measure.py, note that these classes inherit from `TypedDict`. TypedDict is a special type construct that doesn't support `__slots__` - the attribute access would fail at runtime if you tried to use instances with `__slots__`. The correct pattern is to simply not include `__slots__` on TypedDict definitions.

**1.3 Control Characters Fix:**
The comment at line 233 says "Other (control, format, etc.)" but the code only handles "Cc". Per UTS #55, the intent is to count control characters (Cc) and orphan code points (Co, Cn) but NOT format characters (Cf). So the fix should be:
```python
elif cat.startswith("C"):
    if cat == "Cf":
        pass  # Cf excluded from control_chars count per UTS #55
    else:
        control_chars += 1  # Cc, Co, Cn all count
```

**1.6 UnitValue `__rsub__`:**
When fixing `__rsub__`, consider that `5 - UnitValue(3, 'ft')` should convert 5 to feet units first, then subtract. The current implementation gives `-2 ft` which is mathematically wrong. The fix should convert the scalar `other` to the same unit as `self` before subtracting, when units are involved.

**1.7 `_handle_negative_token()`:**
This function is only called when `index >= 2` based on call sites at lines 711 and 714. But we should verify the tokens at `index-2` and `index-1` exist and are valid before accessing them. The function modifies tokens in-place which is risky.

### For Wave 2 (Medium Bugs)

**2.3 `_advance_past_sequence()` Dead Code:**
The function at primitives.py:398-446 is defined but never called. Its logic is duplicated inline in `count_graphemes()` at lines 488-497 (ZWJ handling) and 500-505 (regional indicators). When deciding whether to remove or refactor, note that the inline code is more readable but the function provides a cleaner abstraction. For now, recommend removing the dead function and keeping the inline code in `count_graphemes()`.

### For Wave 3 (Documentation)

**3.1 TypedDict vs NamedTuple:**
The architecture docs incorrectly show patterns like `@dataclass class Xxx(NamedTuple)` which is invalid syntax. The correct pattern for TypedDict is:
```python
class Xxx(TypedDict):
    field1: str
    field2: int
```
Not `@dataclass class Xxx(TypedDict)` which would be a dataclass inheriting from TypedDict (also invalid).

### For Wave 4 (Feature Completeness)

**4.1 Adding Math Functions:**
Functions like `sign`, `hypot`, `fact`, `lshift`, `rshift`, `prevprime`, `nextprime` exist in the evaluator but may not be exposed in the public API. Check `FUNCTION_MAPPINGS` in normalize.py and the FUNCTIONS dict in evaluator.py to see what's currently available and what needs to be added.

### For Wave 5 (Improvements)

**5.8 `list_compare` Deduplication:**
When deduplicating near_matches, use the `a_span` or `b_span` start position as a unique key. The issue is that the same codepoint position might appear twice with different classification reasons.

(End of file - total 470 lines)