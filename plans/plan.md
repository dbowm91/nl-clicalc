# nl-clicalc Implementation Plan

## Status: IN PROGRESS (2026-05-29)

Consolidated from architecture review of all modules. Previous plan (2026-05-28) was completed with 56 items. New review has identified additional issues requiring attention.

---

## Overview

| Category | Count |
|----------|-------|
| High Priority Bugs | 4 |
| Medium Priority Bugs | 5 |
| Low Priority Bugs | 8 |
| Documentation Updates | 15+ |
| Improvements | 8 |
| Deferred Items | 8 |

---

## Wave 1: High Priority Bugs (Parallel - 4 items)

### 1. units.py - `__add__` Scalar + Dimensional Bug
**Severity:** HIGH
**Location:** `units.py:66`

`UnitValue(3, "m") + 5` returns `UnitValue(8, "m")` - should raise `ValueError` for dimensionless + dimensional mixing.

**Fix:** Add dimensional analysis check in `__add__` to raise ValueError when adding scalar to dimensional value.

### 2. units.py - `__rsub__` Scalar + Dimensional Bug
**Severity:** HIGH
**Location:** `units.py:81-84`

`5 - UnitValue(3, "m")` returns `UnitValue(2, "m")` - physically incorrect, should raise `ValueError`.

**Fix:** Add dimensional analysis check in `__rsub__` to raise ValueError.

### 3. normalize.py - Double Minus Concatenation Bug
**Severity:** HIGH
**Location:** `normalize.py:762-763` in `split_at_operators`

"5 minus -2" becomes "52" instead of being properly tokenized as "5-(-2)".

**Root Cause:**
1. Bounds check at line 762 uses Python negative indexing when `i=0`, wrapping to last element
2. Pattern `^\d+-\d+$` at line 753 only matches single hyphen

**Failing Test Cases:**
- "5 minus -2" → "52" (should be 7)
- "5 minus negative 2" → "52" (should be 7)
- "5 -- 3" → "53" (should be 8)
- "5 - - 3" → "53" (should be 8)

**Fix:** Add bounds checking before accessing `tokens[i-1]` and handle multi-hyphen patterns.

### 4. mcp/tools.py - `unit_info()` Calls Non-existent Function
**Severity:** HIGH
**Location:** `nl_calc/mcp/tools.py:324`

`unit_info()` calls `list_units()` from `..units` but this function is not exported from units.py. Will fail with NameError at runtime.

**Fix:** Either export `list_units` from units.py, or fix the function logic.

---

## Wave 2: Medium Priority Bugs (Parallel - 5 items)

### 5. validate.py - `toml_shape()` Wrong Exception Type
**Severity:** MEDIUM
**Location:** `validate.py:413`

Catches `json.JSONDecodeError` but `tomllib` uses different exception types; TOML parse errors won't be caught.

**Fix:** Catch appropriate exception type(s) for tomllib.

### 6. normalize.py - `--verbose` Flag Logic Bug
**Severity:** MEDIUM
**Location:** `normalize.py:1517`

When `-e` is used (`quiet_by_default=True`), `--verbose` cannot enable expression output.

**Suggested Fix:**
```python
show_expression = args.verbose or args.show or (not args.quiet and not quiet_by_default and not args.single_expr)
```

### 7. mcp/tools.py - Duplicate `_VALID_TRANSFORM_OPERATIONS`
**Severity:** MEDIUM
**Location:** `nl_calc/mcp/tools.py:839-853` and `tools.py:1337-1351`

Same constant defined twice in same file. Second definition shadows the first.

**Fix:** Remove the duplicate at lines 1337-1351.

### 8. units.py - `__eq__` Returns NotImplemented
**Severity:** MEDIUM
**Location:** `units.py:48-53`

`UnitValue(5, "m") == UnitValue(5, "ft")` returns `NotImplemented` instead of `False`.

**Fix:** Compare values when units differ, return False for same-value different-unit.

### 9. normalize.py - Int Regex Pattern Contains Erroneous Characters
**Severity:** MEDIUM
**Location:** `normalize.py:367, 369`

Int patterns use `[-|+]?` and `[-|+|*]?` allowing `|` and `*` as sign characters.

**Fix:** Change to `[-+]?` and `[-+*]?`.

---

## Wave 3: Low Priority Bugs (Parallel - 8 items)

### 10. synthesis.py - `text_window` Undefined `n` Variable
**Severity:** LOW
**Location:** `synthesis.py:1223,1234`

Variable `n` used but not defined; should be `len(text)`.

### 11. synthesis.py - `list_compare` Operator Precedence
**Severity:** LOW
**Location:** `synthesis.py:1072`

Missing parentheses around `or` condition; `treat_as_multiset=False` case could return incorrect results.

### 12. synthesis.py - `count_chars` Field Inconsistency
**Severity:** LOW
**Location:** `synthesis.py:932,948`

Field is set to `len(text_bytes)` (byte count) or grapheme count instead of actual codepoint count.

### 13. primitives.py - ZWSP Not Treated as Extend
**Severity:** LOW
**Location:** `primitives.py:351-369`

ZWSP (U+200B) fails `_is_extend_char()` check; `count_graphemes("a\u200bb")` returns 3 instead of 2.

### 14. mcp/schemas.py - ErrorEnvelope Missing Runtime Fields
**Severity:** LOW
**Location:** `schemas.py:13-18`, `tools.py:222-252`

`_error_response()` and `_success_response()` add `tool`, `warnings`, and `limits_applied` fields not declared in `ErrorEnvelope` TypedDict.

### 15. api - `normalize_expression` Return Type Mismatch
**Severity:** LOW
**Location:** Documentation vs actual

Doc says `-> str`, actual is `-> tuple[str, int]`.

### 16. evaluator.py - Missing `ln` Alias
**Severity:** LOW

Document claims `ln(x)` exists but only `log` is implemented.

### 17. evaluator.py - Missing Documentation for `evaluate_async`/`evaluate_cached`
**Severity:** LOW

LRU cached evaluation functions not documented.

---

## Wave 4: Documentation Updates (Parallel - 15 items)

### 18. exact/ Module Structure Documentation
**Priority:** MEDIUM
**Location:** `architecture/exact.md`

Document shows 7 modules, actual has 12+ (path_tools, glob, transform, identifier, identifier_inspect, position are missing).

### 19. MCP Tools Documentation
**Priority:** HIGH
**Location:** `architecture/mcp.md`

Document shows 11 tools, actual has 39. Update to reflect all 50+ tools.

### 20. Test Count Update
**Priority:** LOW
**Location:** `architecture/overview.md`

Document says "350 tests pass", actual is 629.

### 21. exact/ Public API Re-exports
**Priority:** MEDIUM

Missing: `path_analyze`, `glob_match`, `escape_text`, `text_hash`, `text_transform`, `json_extract`, `json_compare`, `json_shape`, `regex_finditer`, `regex_safety_check`, `validate_toml_text`, `version_compare`, `list_dedupe`, `list_sort`, `text_position`, `identifier_analyze`, `identifier_analyze`, `path_normalize`

### 22. measure.py - `sentences_estimate` Example Wrong
**Priority:** LOW
**Location:** `architecture/measure.md:47-50`

Example shows `sentences_estimate=1` for "hello world hello" but actual result is `0`. Code is correct; docs are wrong.

### 23. measure.py - Misleading Comment
**Priority:** LOW
**Location:** `measure.py:169`

Comment says "not ellipses or decimals" but implementation does match ellipses.

### 24. synthesis.py - `text_window` Function Undocumented
**Priority:** MEDIUM
**Location:** `architecture/synthesis.md`

Function at line 1106 not documented.

### 25. synthesis.py - Extra TypedDict Classes Not Documented
**Priority:** LOW

Missing: `TextWindowPosition`, `TextWindowResult`, `ListCompareOrderedResult`, `ListCompareSetResult`, `ListCompareMultisetResult`, `ListCompareNearMatch`

### 26. unicode_tools.py - `check_domain_safety()` Example Wrong
**Priority:** MEDIUM
**Location:** `architecture/unicode_tools.md:182-187`

Example calls `len(mixed)` on dict (returns 3 keys, not script count). Bug is in documentation, not code.

### 27. unicode_tools.py - `reverse_confusables()` Not Documented
**Priority:** LOW

Listed in index but not in Functions section.

### 28. unicode_tools.py - Dependencies Section Wrong
**Priority:** LOW

Claims `primitives.py` is used (only standard library + confusables.py).

### 29. validate.py - Document Severely Incomplete
**Priority:** HIGH

Only 3 of 25+ functions documented. Missing 22 functions, 14 TypedDicts, 6 constants.

### 30. units.py - Angle Category Missing from Table
**Priority:** LOW

Unit Categories table missing Angle category (rad, deg).

### 31. confusables.py - Data Format Documentation
**Priority:** LOW

Doc shows `dict[str, list[str]]`, actual is `dict[str, str]` with space-separated codepoints.

### 32. diff.py - Documentation Examples Wrong
**Priority:** LOW

- `diff_spans` example shows wrong index and wrong text
- `common_prefix_suffix("hello", "yo")` doc shows `0,0` but actual is `0,1`

---

## Wave 5: Improvements (Parallel - 8 items)

### 33. exact/ - Add TomlShapeResult, VersionCompareResult Exports
**Priority:** LOW
**Location:** `nl_calc/exact/validate.py` / `__init__.py`

`TomlShapeResult` and `VersionCompareResult` defined but not exported.

### 34. mcp/ - Define MAX_REGEX_SAMPLES Constant
**Priority:** LOW

Referenced in docstring but not defined.

### 35. mcp/ - Document Tier/Tag Filtering in Tools
**Priority:** LOW

### 36. measure.py - Consider Consistent None Handling
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
- `get_unit_category` is correctly imported in evaluator.py
- All 629 tests pass
- Memory, variable, constant functions all match documentation
- CLI options correctly route to implementations
- Text commands (`inspect`, `count`, `regex`) delegate correctly to `exact` module

---

## Implementation Order

1. **Wave 1**: Fix high priority bugs (4 items) - can parallelize
2. **Wave 2**: Fix medium priority bugs (5 items) - can parallelize
3. **Wave 3**: Fix low priority bugs (8 items) - can parallelize
4. **Wave 4**: Update documentation (15 items) - can parallelize
5. **Wave 5**: Improvements (8 items) - can parallelize

**Total: 40 actionable items across 5 waves**

---

## Verification

```bash
python3 -m pytest tests/
```

All 629 tests must pass after changes.
