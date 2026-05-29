# nl-clicalc Implementation Plan

## Status: IN PROGRESS (2026-05-29)

Consolidated from architecture review of all modules. Previous plan (2026-05-28) completed 56 items. New review identified 40+ actionable items across 5 waves.

---

## Overview

| Category | Count |
|----------|-------|
| High Priority Bugs | 4 |
| Medium Priority Bugs | 5 |
| Low Priority Bugs | 8 |
| Documentation Updates | 15 |
| Improvements | 8 |

**Total: 40+ actionable items**

---

## Wave 1: High Priority Bugs (Parallelizable - 4 items)

### 1. units.py - `__add__` Scalar + Dimensional Bug
**Severity:** HIGH
**Location:** `nl_calc/units.py:66`

`UnitValue(3, "m") + 5` returns `UnitValue(8, "m")` - should raise `ValueError` for dimensionless + dimensional mixing.

**Reproduction:**
```python
from nl_calc import run
result = run("3m + 5", NORMALIZE, PATTERNS)  # Returns 8 m - WRONG
```

**Fix:** Add dimensional analysis check in `__add__` to raise ValueError when adding scalar to dimensional value:
```python
def __add__(self, other):
    if isinstance(other, (int, float)):
        if self.unit is not None:
            raise ValueError(f"Cannot add scalar {other} to dimensional value {self}")
        return UnitValue(self.value + other, None)
    # ... existing UnitValue logic
```

### 2. units.py - `__rsub__` Scalar + Dimensional Bug
**Severity:** HIGH
**Location:** `nl_calc/units.py:81-84`

`5 - UnitValue(3, "m")` returns `UnitValue(2, "m")` - physically incorrect, should raise `ValueError`.

**Reproduction:**
```python
from nl_calc import run
result = run("5 - 3m", NORMALIZE, PATTERNS)  # Returns 2 m - WRONG
```

**Fix:** Add dimensional analysis check in `__rsub__`:
```python
def __rsub__(self, other):
    if isinstance(other, (int, float)):
        if self.unit is not None:
            raise ValueError(f"Cannot subtract dimensional value {self} from scalar {other}")
        return UnitValue(other - self.value, None)
    return NotImplemented
```

### 3. normalize.py - Double Minus Concatenation Bug
**Severity:** HIGH
**Location:** `nl_calc/normalize.py:762-763` in `split_at_operators`

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
# Before accessing tokens[i-1], check i > 0
if i > 0 and tokens[i-1] == '-':
    # Handle double minus case
```

### 4. mcp/tools.py - `unit_info()` Calls Non-existent Function
**Severity:** HIGH
**Location:** `nl_calc/mcp/tools.py:324`

`unit_info()` calls `list_units()` from `..units` but this function is not exported from units.py. Will fail with NameError at runtime.

**Reproduction:**
```bash
python -m nl_calc mcp
# Then call unit_info tool
# NameError: name 'list_units' is not defined
```

**Fix:** Either export `list_units` from units.py, or fix the function logic to use `get_all_units()` instead.

---

## Wave 2: Medium Priority Bugs (Parallelizable - 5 items)

### 5. validate.py - `toml_shape()` Wrong Exception Type
**Severity:** MEDIUM
**Location:** `nl_calc/exact/validate.py:413`

Catches `json.JSONDecodeError` but `tomllib` uses different exception types; TOML parse errors won't be caught.

**Fix:** Catch appropriate exception type(s) for tomllib (Python 3.11+):
```python
try:
    import tomllib
except ImportError:
    import tomli as tomllib

try:
    data = tomllib.loads(text)
except (tomllib.TOMLDecodeError, ValueError) as e:
    raise ValueError(f"Invalid TOML: {e}")
```

### 6. normalize.py - `--verbose` Flag Logic Bug
**Severity:** MEDIUM
**Location:** `nl_calc/normalize.py:1517`

When `-e` is used (`quiet_by_default=True`), `--verbose` cannot enable expression output.

**Current (buggy):**
```python
show_expression = not args.quiet and not quiet_by_default and not args.single_expr
```

**Fix:**
```python
show_expression = args.verbose or args.show or (not args.quiet and not quiet_by_default and not args.single_expr)
```

### 7. mcp/tools.py - Duplicate `_VALID_TRANSFORM_OPERATIONS`
**Severity:** MEDIUM
**Location:** `nl_calc/mcp/tools.py:839-853` and `tools.py:1337-1351`

Same constant defined twice in same file. Second definition at lines 1337-1351 shadows the first.

**Fix:** Remove the duplicate at lines 1337-1351.

### 8. units.py - `__eq__` Returns NotImplemented
**Severity:** MEDIUM
**Location:** `nl_calc/units.py:48-53`

`UnitValue(5, "m") == UnitValue(5, "ft")` returns `NotImplemented` instead of `False`.

**Reproduction:**
```python
from nl_calc import evaluate
result = evaluate("5m == 5ft")  # Returns NotImplemented (evaluates to False in Python)
```

**Fix:** Compare values when units differ, return False:
```python
def __eq__(self, other):
    if isinstance(other, UnitValue):
        if self.unit != other.unit:
            return False
        return self.value == other.value
    return NotImplemented
```

### 9. normalize.py - Int Regex Pattern Contains Erroneous Characters
**Severity:** MEDIUM
**Location:** `nl_calc/normalize.py:367, 369`

Int patterns use `[-|+]?` and `[-|+|*]?` allowing `|` and `*` as sign characters.

**Current (buggy):**
```python
INTEGER_PATTERN_1 = r'[-|+]?\d+'  # Wrong - allows | as sign
INTEGER_PATTERN_2 = r'[-|+|*]?\d+'  # Wrong - allows | and * as signs
```

**Fix:**
```python
INTEGER_PATTERN_1 = r'[-+]?\d+'
INTEGER_PATTERN_2 = r'[-+*]?\d+'
```

---

## Wave 3: Low Priority Bugs (Parallelizable - 8 items)

### 10. synthesis.py - `text_window` Undefined `n` Variable
**Severity:** LOW
**Location:** `nl_calc/exact/synthesis.py:1223, 1234`

Variable `n` used but not defined; should be `len(text)`.

**Fix:** Change `n` to `len(text)` in lines 1223 and 1234.

### 11. synthesis.py - `list_compare` Operator Precedence
**Severity:** LOW
**Location:** `nl_calc/exact/synthesis.py:1072`

Missing parentheses around `or` condition; `treat_as_multiset=False` case could return incorrect results.

**Current (buggy):**
```python
same_unordered = treat_as_multiset and a_set == b_set or not treat_as_multiset and a_counter == b_counter
```

**Fix:**
```python
same_unordered = (treat_as_multiset and a_set == b_set) or (not treat_as_multiset and a_counter == b_counter)
```

### 12. synthesis.py - `count_chars` Field Inconsistency
**Severity:** LOW
**Location:** `nl_calc/exact/synthesis.py:932, 948`

Field is set to `len(text_bytes)` (byte count) or grapheme count instead of actual codepoint count.

**Fix:** Use `len(text)` (codepoint count) instead of byte/grapheme count.

### 13. primitives.py - ZWSP Not Treated as Extend
**Severity:** LOW
**Location:** `nl_calc/exact/primitives.py:351-369`

ZWSP (U+200B) fails `_is_extend_char()` check; `count_graphemes("a\u200bb")` returns 3 instead of 2.

**Reproduction:**
```python
from nl_calc.exact import count_graphemes
count_graphemes("a\u200bb")  # Returns 3, should be 2
```

**Fix:** Add ZWSP to `_is_extend_char()` check alongside ZWNJ:
```python
if cp == 0x200B:  # ZWSP
    return True
```

### 14. mcp/schemas.py - ErrorEnvelope Missing Runtime Fields
**Severity:** LOW
**Location:** `nl_calc/mcp/schemas.py:13-18`, `tools.py:222-252`

`_error_response()` and `_success_response()` add `tool`, `warnings`, and `limits_applied` fields not declared in `ErrorEnvelope` TypedDict.

**Fix:** Add missing fields to TypedDict definition, or remove runtime additions.

### 15. api - `normalize_expression` Return Type Mismatch
**Severity:** LOW
**Location:** Documentation vs actual

Doc says `-> str`, actual is `-> tuple[str, int]`.

**Fix:** Update documentation to reflect actual return type.

### 16. evaluator.py - Missing `ln` Alias
**Severity:** LOW

Document claims `ln(x)` exists but only `log` is implemented.

**Fix:** Either add `ln` as alias in `FUNCTION_MAPPINGS`, or update documentation.

### 17. evaluator.py - Missing Documentation for `evaluate_async`/`evaluate_cached`
**Severity:** LOW

LRU cached evaluation functions not documented.

**Fix:** Add documentation for `evaluate_async` and `evaluate_cached`.

---

## Wave 4: Documentation Updates (Parallelizable - 15 items)

### 18. architecture/exact.md - Module Structure
**Priority:** MEDIUM

Document shows 7 modules, actual has 12+ (path_tools, glob, transform, identifier, identifier_inspect, position are missing).

### 19. architecture/mcp.md - MCP Tools Documentation
**Priority:** HIGH

Document shows 11 tools, actual has 39. Update to reflect all 39+ tools.

### 20. architecture/overview.md - Test Count
**Priority:** LOW

Document says "350 tests pass", actual is 629.

### 21. architecture/exact.md - Public API Re-exports
**Priority:** MEDIUM

Missing exports: `path_analyze`, `glob_match`, `escape_text`, `text_hash`, `text_transform`, `json_extract`, `json_compare`, `json_shape`, `regex_finditer`, `regex_safety_check`, `validate_toml_text`, `version_compare`, `list_dedupe`, `list_sort`, `text_position`, `identifier_analyze`, `identifier_analyze`, `path_normalize`

### 22. architecture/measure.md - `sentences_estimate` Example
**Priority:** LOW
**Location:** `architecture/measure.md:47-50`

Example shows `sentences_estimate=1` for "hello world hello" but actual result is `0`. Code is correct; docs are wrong.

### 23. measure.py - Misleading Comment
**Priority:** LOW
**Location:** `nl_calc/exact/measure.py:169`

Comment says "not ellipses or decimals" but implementation does match ellipses.

### 24. architecture/synthesis.md - `text_window` Function
**Priority:** MEDIUM

Function at line 1106 not documented.

### 25. architecture/synthesis.md - TypedDict Classes
**Priority:** LOW

Missing: `TextWindowPosition`, `TextWindowResult`, `ListCompareOrderedResult`, `ListCompareSetResult`, `ListCompareMultisetResult`, `ListCompareNearMatch`

### 26. architecture/unicode_tools.md - `check_domain_safety()` Example
**Priority:** MEDIUM
**Location:** `architecture/unicode_tools.md:182-187`

Example calls `len(mixed)` on dict (returns 3 keys, not script count). Bug is in documentation, not code.

### 27. architecture/unicode_tools.md - `reverse_confusables()` Not Documented
**Priority:** LOW

Listed in index but not in Functions section.

### 28. architecture/unicode_tools.md - Dependencies Section
**Priority:** LOW

Claims `primitives.py` is used (only standard library + confusables.py).

### 29. architecture/validate.md - Documentation Severely Incomplete
**Priority:** HIGH

Only 3 of 25+ functions documented. Missing 22 functions, 14 TypedDicts, 6 constants.

### 30. architecture/units.md - Angle Category Missing
**Priority:** LOW

Unit Categories table missing Angle category (rad, deg).

### 31. architecture/confusables.md - Data Format Documentation
**Priority:** LOW

Doc shows `dict[str, list[str]]`, actual is `dict[str, str]` with space-separated codepoints.

### 32. architecture/diff.md - Documentation Examples Wrong
**Priority:** LOW

- `diff_spans` example shows wrong index and wrong text
- `common_prefix_suffix("hello", "yo")` doc shows `0,0` but actual is `0,1`

---

## Wave 5: Improvements (Parallelizable - 8 items)

### 33. exact/ - Add TomlShapeResult, VersionCompareResult Exports
**Priority:** LOW
**Location:** `nl_calc/exact/validate.py` / `__init__.py`

`TomlShapeResult` and `VersionCompareResult` defined but not exported.

### 34. mcp/ - Define MAX_REGEX_SAMPLES Constant
**Priority:** LOW

Referenced in docstring but not defined.

### 35. mcp/ - Document Tier/Tag Filtering in Tools
**Priority:** LOW

### 36. measure.py - Consistent None Handling
**Priority:** LOW

`char_category_metrics(None)` raises TypeError while others return zero.

### 37. primitives.py - Add ZWSP Extend Behavior Tests
**Priority:** LOW

### 38. unicode_tools.py - Add MixedScriptsResult to Type Definitions
**Priority:** LOW

### 39. units.py - Document Scalar + UnitValue Behavior
**Priority:** LOW

Or decide to fix (see Wave 1 items 1-2).

### 40. validate.py - DEBUG Flag Never Applied
**Priority:** LOW

Remove or implement.

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

- confusables.py implementation is correct - no bugs found
- All evaluator security architecture (AST parsing, whitelist approach) verified
- `get_unit_category` is correctly imported in evaluator.py (line 27)
- All 629 tests pass
- Memory, variable, constant functions all match documentation
- CLI options correctly route to implementations
- Text commands (`inspect`, `count`, `regex`) delegate correctly to `exact` module

---

## Implementation Order & Parallelization

### Phase 1 (Wave 1): High Priority Bugs
**Can parallelize:** All 4 items are independent
- Agent 1: units.py __add__ + __rsub__ bugs (items 1-2)
- Agent 2: normalize.py double-minus bug (item 3)
- Agent 3: mcp/tools.py list_units issue (item 4)

### Phase 2 (Wave 2): Medium Priority Bugs
**Can parallelize:** All 5 items are independent
- Agent 1: validate.py toml_shape exception (item 5)
- Agent 2: normalize.py --verbose + int regex (items 6, 9)
- Agent 3: mcp/tools.py duplicate constant (item 7)
- Agent 4: units.py __eq__ issue (item 8)

### Phase 3 (Wave 3): Low Priority Bugs
**Can parallelize:** Items are mostly independent
- Agent 1: synthesis.py bugs (items 10, 11, 12)
- Agent 2: primitives.py ZWSP (item 13)
- Agent 3: mcp/schemas.py ErrorEnvelope (item 14)
- Agent 4: evaluator docs + ln alias (items 16, 17)

### Phase 4 (Wave 4): Documentation Updates
**Can parallelize:** All items are independent documentation work
- Each doc file can be updated by separate agent

### Phase 5 (Wave 5): Improvements
**Can parallelize:** All items are independent
- Each improvement can be implemented by separate agent

---

## Verification

After any changes, run:
```bash
python3 -m pytest tests/
```

All 629 tests must pass.

---

## Plan Source Files

This plan was consolidated from the following architecture review files:
- `plans/overview_review.md` - General architecture discrepancies
- `plans/exact_review.md` - exact/ module review
- `plans/mcp_review.md` - MCP server review
- `plans/normalize_review.md` - normalize.py review
- `plans/evaluator_review.md` - evaluator.py review (note: claimed bug re: get_unit_category import is INCORRECT - import is present at line 27)
- `plans/units_review.md` - units.py review
- `plans/measure_review.md` - measure.py review
- `plans/synthesis_review.md` - synthesis.py review
- `plans/diff_review.md` - diff.py review
- `plans/unicode_tools_review.md` - unicode_tools.py review
- `plans/primitives_review.md` - primitives.py review
- `plans/confusables_review.md` - confusables.py review
- `plans/cli_review.md` - CLI review
- `plans/validate_review.md` - validate.py review
- `plans/api_review.md` - API review
