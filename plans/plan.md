# nl-clicalc Implementation Plan

## Status: COMPLETED (2026-05-29)

All 35 items implemented and verified. All 631 tests pass.

Consolidated from architecture review of all modules. This plan has been verified against the codebase to remove items that were already fixed or incorrectly described.

---

## Overview

| Category | Count |
|----------|-------|
| High Priority Bugs | 2 |
| Medium Priority Bugs | 4 |
| Low Priority Bugs | 6 |
| Documentation Updates | 15 |
| Improvements | 8 |

**Total: 35 actionable items**

---

## Wave 1: High Priority Bugs

### 1. normalize.py - Double Minus Concatenation Bug
**Severity:** HIGH
**Location:** `nl_calc/normalize.py:762` in `split_at_operators`

"5 minus -2" becomes "52" instead of being properly tokenized as "5-(-2)".

**Root Cause:**
1. Bounds check at line 762 uses Python negative indexing when `i=0`, wrapping to last element
2. Pattern `^\d+-\d+$` at line 753 only matches single hyphen

**Failing Test Cases:**
| Input | Expected | Actual |
|-------|----------|--------|
| "5 minus -2" | 7 | 52 |
| "5 minus negative 2" | 7 | 52 |
| "5 -- 3" | 8 | 53 |
| "5 - - 3" | 8 | 53 |

**Fix:** Add bounds checking before accessing `tokens[i-1]`:
```python
# At line 762, before accessing tokens[i-1]:
if i > 0 and tokens[i-1] == '-':
    # Handle double minus case by inserting empty token
    # or properly merging tokens
```

**Implementation:**
- Read `split_at_operators` function (lines 720-800)
- The bug is at line 762: `tokens[i-1]` wraps to last element when i=0
- Need to add `i > 0 and` check before the negative index access
- After fixing bounds, ensure double-minus sequences are properly handled

### 2. mcp/tools.py - `unit_info()` Calls Non-existent Function
**Severity:** HIGH
**Location:** `nl_calc/mcp/tools.py:324`

`unit_info()` imports `list_units` from `..units` but this function does not exist in units.py. Will fail with NameError at runtime.

**Reproduction:**
```bash
python -m nl_calc mcp
# Then call unit_info tool
# NameError: name 'list_units' is not defined
```

**Fix:** Change the import and function call to use `get_all_units()` instead:
```python
# At line 324, change:
from ..units import UNIT_ALIASES, UNIT_CATEGORIES, UNIT_BASE, list_units
# to:
from ..units import UNIT_ALIASES, UNIT_CATEGORIES, UNIT_BASE, get_all_units

# In unit_info() function, change:
list_units()
# to:
get_all_units()
```

---

## Wave 2: Medium Priority Bugs

### 3. normalize.py - Int Regex Pattern Contains Erroneous Characters
**Severity:** MEDIUM
**Location:** `nl_calc/normalize.py:367, 369`

Int patterns use `[-|+]?` and `[-|+|*]?` allowing `|` and `*` as sign characters. Inside `[]`, these are treated as literals, not operators.

**Current (buggy):**
```python
"int": re.compile(r"^[-|+]?[0-9]\d*$"),           # Line 367 - allows | as sign
"int_number_combine": re.compile(r"^[-|+|*]?[0-9]\d*$"),  # Line 369 - allows | and * as signs
```

**Fix:**
```python
"int": re.compile(r"^[-+]?[0-9]\d*$"),            # Remove | from character class
"int_number_combine": re.compile(r"^[-+*]?[0-9]\d*$"),  # Remove | from character class
```

**Implementation:**
- Find lines 367 and 369 in normalize.py
- Replace `[-|+]` with `[-+]`
- Replace `[-|+|*]` with `[-+*]`
- Add tests to verify pattern works correctly

### 4. mcp/tools.py - Duplicate `_VALID_TRANSFORM_OPERATIONS`
**Severity:** MEDIUM
**Location:** `nl_calc/mcp/tools.py:839-853` and `tools.py:1337-1351`

Same constant defined twice in same file. Second definition at lines 1337-1351 shadows the first.

**Fix:** Remove the duplicate definition at lines 1337-1351.

**Implementation:**
- Search for `_VALID_TRANSFORM_OPERATIONS` in tools.py
- Keep the first definition (around line 839)
- Delete the second definition (around line 1337)
- Verify no other code depends on the specific line number

### 5. units.py - `__eq__` Returns NotImplemented
**Severity:** MEDIUM
**Location:** `nl_calc/units.py:48-53`

`UnitValue(5, "m") == UnitValue(5, "ft")` returns `NotImplemented` instead of `False`. When units differ but values are equal, it should return `False` directly.

**Current code:**
```python
def __eq__(self, other: object) -> bool:
    if not isinstance(other, UnitValue):
        return NotImplemented
    if self.unit != other.unit:
        return NotImplemented  # BUG: should return False
    return abs(self.value - other.value) < FLOAT_EPSILON
```

**Fix:**
```python
def __eq__(self, other: object) -> bool:
    if not isinstance(other, UnitValue):
        return NotImplemented
    if self.unit != other.unit:
        return False  # Different units means not equal
    return abs(self.value - other.value) < FLOAT_EPSILON
```

**Implementation:**
- Read lines 48-53 of units.py
- Change line 52 from `return NotImplemented` to `return False`
- Add test: `assert UnitValue(5, "m") != UnitValue(5, "ft")`

---

## Wave 3: Low Priority Bugs

### 6. synthesis.py - `text_window` Undefined `n` Variable
**Severity:** LOW
**Location:** `nl_calc/exact/synthesis.py:1223, 1234`

Variable `n` is used in the codepoint-to-byte conversion loop but only defined inside the `grapheme_index` branch at line 1166. When `text_window()` is called with `kind="codepoint_index"`, `kind="byte_offset"`, or `kind="line_column"`, `n` is undefined.

**Current code structure:**
```python
# Line 1166: n defined only for grapheme_index
if position.kind == "grapheme_index":
    n = len(text)

# Lines 1223, 1234: n used but undefined for other kinds
for offset, char_index in enumerate(range(...)):
    ...convert grapheme to codepoint...
    if n == 0:  # Line 1223 - n undefined here for non-grapheme_index
        break
```

**Fix:** Define `n = len(text)` before the conditional branch so it's available for all position kinds.

**Implementation:**
- Read the `text_window` function (around lines 1106-1240)
- Move `n = len(text)` outside the grapheme_index branch (before line 1166)
- Test with different position kinds to verify fix

### 7. synthesis.py - `count_chars` Field Inconsistency
**Severity:** LOW
**Location:** `nl_calc/exact/synthesis.py:932, 948`

Field `text_length_codepoints` is set to byte count or grapheme count instead of actual codepoint count.

**Current code:**
```python
# Line 932 (byte mode):
text_length_codepoints=len(text_bytes)  # Returns byte count, NOT codepoint count

# Line 948 (grapheme mode):
text_length_codepoints=_count_graphemes(text)  # Returns grapheme count
```

**Fix:** Use `len(text)` (codepoint count) for `text_length_codepoints` in all modes. Consider renaming the field to `text_length_codepoints` to match actual content, or ensure it contains actual codepoint count.

**Implementation:**
- Read lines 920-960 in synthesis.py
- Change `text_length_codepoints=len(text_bytes)` to `text_length_codepoints=len(text)`
- Consider if field should be renamed for accuracy

### 8. mcp/schemas.py - ErrorEnvelope Missing Runtime Fields
**Severity:** LOW
**Location:** `nl_calc/mcp/schemas.py:13-18`, `tools.py:222-252`

`ErrorEnvelope` TypedDict defines only 4 fields but `_error_response()` and `_success_response()` add `tool`, `warnings`, and `limits_applied` fields at runtime.

**Fix:** Update `ErrorEnvelope` TypedDict to include all fields:

```python
class ErrorEnvelope(TypedDict):
    ok: bool
    error_type: str
    error: str
    hints: list[str]
    tool: str | None  # Add this
    warnings: list[str]  # Add this
    limits_applied: list[str]  # Add this
```

**Implementation:**
- Read schemas.py lines 13-18 for ErrorEnvelope definition
- Read tools.py lines 222-252 for how fields are added at runtime
- Update TypedDict to include all fields
- Or remove the extra fields from the response functions if they shouldn't be there

### 9. api - `normalize_expression` Return Type Mismatch
**Severity:** LOW
**Location:** Documentation vs actual `nl_calc/normalize.py:1105-1110`

Documentation says `normalize_expression` returns `-> str` but actual signature returns `-> tuple[str, int]`.

**Actual signature:**
```python
def normalize_expression(
    expression: str,
    operators: dict,
    patterns: Mapping[str, Pattern[str]],
    skip_validation: bool = False,
) -> tuple[str, int]:  # Returns (normalized_expression, exit_code)
```

**Fix:** Update documentation to reflect actual return type `tuple[str, int]`.

**Implementation:**
- Find architecture documentation that shows this function
- Update return type from `-> str` to `-> tuple[str, int]`
- Document what each tuple element represents

### 10. evaluator.py - Missing `ln` Alias
**Severity:** LOW

Documentation claims `ln(x)` exists but only `log` is in the evaluator's FUNCTIONS dict. `normalize.py` handles `ln -> log` mapping at line 144 for `run()`, but `evaluate("ln(5)")` fails.

**Fix:** Add `"ln"` as direct alias in evaluator's FUNCTIONS dict:

```python
# In evaluator.py, FUNCTIONS dict around line 923
"log": _log,
"ln": _log,  # Add this alias
```

**Implementation:**
- Read evaluator.py FUNCTIONS dict (around line 906-1027)
- Add `"ln": _log` entry
- Verify both `run("ln(5)")` and `evaluate("ln(5)")` work

### 11. evaluator.py - Missing Documentation for `evaluate_async`/`evaluate_cached`
**Severity:** LOW

LRU cached evaluation functions exist but are not documented.

**Fix:** Add documentation for these functions in architecture/evaluator.md.

**Implementation:**
- Read evaluator.py lines 138 (evaluate_cached) and 153 (evaluate_async)
- Add documentation to architecture/evaluator.md explaining:
  - `evaluate_cached`: LRU cached version of evaluate
  - `evaluate_async`: async wrapper with caching

---

## Wave 4: Documentation Updates

### 12. architecture/exact.md - Module Structure
**Priority:** MEDIUM

Document shows 7 modules, actual has 12+ (path_tools, glob, transform, identifier, identifier_inspect, position are missing).

**Fix:** Update module list to include all actual modules in nl_calc/exact/

### 13. architecture/mcp.md - MCP Tools Documentation
**Priority:** HIGH

Document shows 11 tools, actual has 39. Update to reflect all 39+ tools.

**Fix:** Document all MCP tools defined in tools.py

### 14. architecture/overview.md - Test Count
**Priority:** LOW

Document says "350 tests pass", actual is 629.

**Fix:** Update test count to 629

### 15. architecture/exact.md - Public API Re-exports
**Priority:** MEDIUM

Missing exports: `path_analyze`, `glob_match`, `escape_text`, `text_hash`, `text_transform`, `json_extract`, `json_compare`, `json_shape`, `regex_finditer`, `regex_safety_check`, `validate_toml_text`, `version_compare`, `list_dedupe`, `list_sort`, `text_position`, `identifier_analyze`, `identifier_analyze`, `path_normalize`

**Fix:** Review exact/__init__.py exports and update documentation

### 16. architecture/measure.md - `sentences_estimate` Example
**Priority:** LOW
**Location:** `architecture/measure.md:47-50`

Example shows `sentences_estimate=1` for "hello world hello" but actual result is `0`. Code is correct; docs are wrong.

**Fix:** Update example to show correct result

### 17. measure.py - Misleading Comment
**Priority:** LOW
**Location:** `nl_calc/exact/measure.py:169`

Comment says "not ellipses or decimals" but implementation does match ellipses.

**Fix:** Update comment to match actual behavior, or fix behavior if comment intent is correct

### 18. architecture/synthesis.md - `text_window` Function
**Priority:** MEDIUM

Function at line 1106 not documented.

**Fix:** Add documentation for text_window function

### 19. architecture/synthesis.md - TypedDict Classes
**Priority:** LOW

Missing: `TextWindowPosition`, `TextWindowResult`, `ListCompareOrderedResult`, `ListCompareSetResult`, `ListCompareMultisetResult`, `ListCompareNearMatch`

**Fix:** Document all TypedDict classes in synthesis module

### 20. architecture/unicode_tools.md - `check_domain_safety()` Example
**Priority:** MEDIUM
**Location:** `architecture/unicode_tools.md:182-187`

Example calls `len(mixed)` on dict (returns 3 keys, not script count). Bug is in documentation, not code.

**Fix:** Fix example to show correct usage

### 21. architecture/unicode_tools.md - `reverse_confusables()` Not Documented
**Priority:** LOW

Listed in index but not in Functions section.

**Fix:** Add function documentation

### 22. architecture/unicode_tools.md - Dependencies Section
**Priority:** LOW

Claims `primitives.py` is used (only standard library + confusables.py).

**Fix:** Update dependencies section

### 23. architecture/validate.md - Documentation Severely Incomplete
**Priority:** HIGH

Only 3 of 25+ functions documented. Missing 22 functions, 14 TypedDicts, 6 constants.

**Fix:** Document all functions, TypedDicts, and constants in validate.py

### 24. architecture/units.md - Angle Category Missing
**Priority:** LOW

Unit Categories table missing Angle category (rad, deg).

**Fix:** Add Angle category to unit categories table

### 25. architecture/confusables.md - Data Format Documentation
**Priority:** LOW

Doc shows `dict[str, list[str]]`, actual is `dict[str, str]` with space-separated codepoints.

**Fix:** Update data format documentation to match actual structure

### 26. architecture/diff.md - Documentation Examples Wrong
**Priority:** LOW

- `diff_spans` example shows wrong index and wrong text
- `common_prefix_suffix("hello", "yo")` doc shows `0,0` but actual is `0,1`

**Fix:** Fix examples to match actual behavior

---

## Wave 5: Improvements

### 27. exact/ - Add TomlShapeResult, VersionCompareResult Exports
**Priority:** LOW
**Location:** `nl_calc/exact/validate.py` / `__init__.py`

`TomlShapeResult` and `VersionCompareResult` defined but not exported.

**Fix:** Add to __init__.py exports

### 28. mcp/ - Define MAX_REGEX_SAMPLES Constant
**Priority:** LOW

Referenced in docstring but not defined.

**Fix:** Define the constant in tools.py

### 29. mcp/ - Document Tier/Tag Filtering in Tools
**Priority:** LOW

**Fix:** Add documentation about tier and tag filtering mechanism

### 30. measure.py - Consistent None Handling
**Priority:** LOW

`char_category_metrics(None)` raises TypeError while others return zero.

**Fix:** Make None handling consistent across all functions

### 31. primitives.py - Add ZWSP Extend Behavior Tests
**Priority:** LOW

**Fix:** Add tests to verify ZWSP is properly handled as extend character

### 32. unicode_tools.py - Add MixedScriptsResult to Type Definitions
**Priority:** LOW

**Fix:** Add TypedDict for MixedScriptsResult if missing

### 33. units.py - Document Scalar + UnitValue Behavior
**Priority:** LOW

Document the behavior when adding scalars to UnitValues, or decide to fix.

### 34. validate.py - DEBUG Flag Never Applied
**Priority:** LOW

**Fix:** Either implement DEBUG functionality or remove the flag

---

## Deferred Items (Design Review Needed)

| Item | Description | Reason |
|------|-------------|--------|
| D1 | Return type consistency | Binary operations return `UnitValue` even without units |
| D2 | Type stubs | Could add more specific type annotations |
| D3 | `load_user_config_extended` | Not exported by design |
| D4 | Confusables regeneration metadata | Could add date/version comment |
| D5 | Confusables reproducibility test | Could verify regeneration produces identical output |
| D6 | Performance benchmarking | Documented timings not verified |
| D7 | Complete TypedDict documentation for synthesis | All return types need docs |
| D8 | Reorganize documentation | Low priority, current structure functional |

---

## Verified as Working (No Action Needed)

The following items were claimed as bugs but verified to already be fixed or working correctly:
- `units.py:66` __add__ scalar+dimensional - Already raises ValueError correctly
- `units.py:81-83` __rsub__ scalar+dimensional - Already raises ValueError correctly
- `normalize.py:1517` --verbose flag - Logic is actually correct
- `validate.py:413` toml_shape exception - Uses Exception which works
- `synthesis.py:1072` list_compare operator precedence - Parentheses already present
- `primitives.py:351-369` ZWSP extend - ZWSP (0x200B) already included in check
- `get_unit_category` import in evaluator.py - Import is present at line 27
- All 629 tests pass
- Memory, variable, constant functions all match documentation
- CLI options correctly route to implementations
- Text commands delegate correctly to exact/ module

---

## Implementation Order & Parallelization

### Phase 1 (Wave 1): High Priority Bugs
**Items: 1-2** (2 items, can parallelize 2 agents)
- Agent 1: normalize.py double-minus bug (item 1)
- Agent 2: mcp/tools.py list_units issue (item 2)

### Phase 2 (Wave 2): Medium Priority Bugs
**Items: 3-5** (3 items, can parallelize 3 agents)
- Agent 1: normalize.py int regex patterns (item 3)
- Agent 2: mcp/tools.py duplicate constant (item 4)
- Agent 3: units.py __eq__ issue (item 5)

### Phase 3 (Wave 3): Low Priority Bugs
**Items: 6-11** (6 items, can parallelize 3-4 agents)
- Agent 1: synthesis.py text_window n variable + count_chars field (items 6, 7)
- Agent 2: mcp/schemas.py ErrorEnvelope + api normalize_expression (items 8, 9)
- Agent 3: evaluator.py ln alias + docs for evaluate_async/cached (items 10, 11)

### Phase 4 (Wave 4): Documentation Updates
**Items: 12-26** (15 items, can parallelize 4-5 agents)
- Agent 1: exact.md updates (items 12, 15)
- Agent 2: mcp.md + validate.md (items 13, 23)
- Agent 3: synthesis.md docs (items 18, 19)
- Agent 4: unicode_tools.md docs (items 20, 21, 22)
- Agent 5: remaining docs (items 14, 16, 17, 24, 25, 26)

### Phase 5 (Wave 5): Improvements
**Items: 27-34** (8 items, can parallelize 3-4 agents)
- Agent 1: exports and constants (items 27, 28, 34)
- Agent 2: None handling consistency (item 30)
- Agent 3: type definitions (items 31, 32)
- Agent 4: documentation for scalar+UnitValue (item 33)

---

## Verification

After any changes, run:
```bash
python3 -m pytest tests/
```

All 629 tests must pass.

---

## Removed Items (Already Fixed or Incorrect)

The following items from the original plan have been removed because they were verified as already fixed or incorrectly described:

| Original # | Description | Reason Removed |
|-----------|-------------|----------------|
| 1 | units.py __add__ scalar+dimensional | Already raises ValueError (code verified) |
| 2 | units.py __rsub__ scalar+dimensional | Already raises ValueError (code verified) |
| 5 | validate.py toml_shape exception | Uses Exception, not JSONDecodeError (works) |
| 6 | normalize.py --verbose flag | Code is actually correct |
| 11 | synthesis.py list_compare operator precedence | Parentheses already present (code verified) |
| 13 | primitives.py ZWSP extend | ZWSP already included in check (code verified) |

---

## Notes for Future Agents

1. **Before fixing bugs:** Always read the actual code first. The plan.md was verified but some bugs may have been fixed after verification.

2. **For unit tests:** When adding tests for bug fixes, use:
   - `run()` for NL inputs like "five plus three"
   - `evaluate()` for pure math like "5 + 3"
   - CLI for integration tests

3. **For documentation fixes:** Always verify against the actual code before updating docs.

4. **Build compatibility:** All code changes must work when assembled by build_single.py into nl_calc.py

(End of file)