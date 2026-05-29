# Architecture Overview Review

**Document:** `architecture/overview.md`
**Review date:** 2026-05-29
**Reviewer:** Code review
**Test status:** 629 tests passing

---

## Summary

The architecture document is largely accurate but has several discrepancies due to being outdated. The codebase has evolved significantly since the document was written, adding new modules, tools, and functionality not reflected in the documentation.

---

## Verified Claims

### System Architecture
| Claim | Status | Notes |
|-------|--------|-------|
| CLI delegates to normalize.main() | ✓ MATCHES | `__main__.py:17` calls `normalize.main()` |
| normalize.py converts NL to Python | ✓ MATCHES | Full pipeline implemented in `normalize.py` |
| evaluator.py uses AST (not eval) | ✓ MATCHES | `evaluator.py` uses `ast.parse` and `NodeVisitor` |
| units.py handles conversions | ✓ MATCHES | `UnitValue`, `UNIT_CONVERSIONS`, etc. fully implemented |

### Core Module Exports

#### normalize.py (MOSTLY ACCURATE)
| Claim | Status | Notes |
|-------|--------|-------|
| Exports: `run()` | ✓ MATCHES | Line 31 |
| Exports: `normalize()` | ✓ MATCHES | Line 32 |
| Exports: `normalize_expression()` | ✓ MATCHES | Line 33 |
| Exports: `main()` | ✓ MATCHES | Line 34 |
| Exports: `print_help()` | ✓ MATCHES | Line 35 |
| Exports: `NORMALIZE`, `PATTERNS` | ✓ MATCHES | Lines 36-37 |

**Discrepancy:** Document doesn't mention the re-exports from evaluator (`evaluate`, `EvaluationError`, `UnitValue`) which appear in `__all__` at lines 28-30.

#### evaluator.py (OUTDATED)
| Claim | Status | Notes |
|-------|--------|-------|
| Exports: `evaluate()` | ✓ MATCHES | Line 32 |
| Exports: `evaluate_raw()` | ✓ MATCHES | Line 33 |
| Exports: `evaluate_cached()` | ✓ MATCHES | Line 34 |
| Exports: `evaluate_async()` | ✓ MATCHES | Line 35 |
| Exports: `evaluate_with_timeout()` | ✓ MATCHES | Line 36 |
| Exports: `PyCalcApp`, `Evaluator` | ✓ MATCHES | Lines 40-41 |
| Exports: `EvaluationError`, `TimeoutError` | ✓ MATCHES | Lines 31, 42 |

**Discrepancy:** Document doesn't mention the many additional exports in `__all__` (lines 43-54): memory functions (`memory_store`, `memory_recall`, etc.) and variable functions (`setvar`, `getvar`, etc.).

#### units.py (OUTDATED)
| Claim | Status | Notes |
|-------|--------|-------|
| Exports: `UnitValue` | ✓ MATCHES | Line 24 |
| Exports: `get_conversion_factor()` | ✓ MATCHES | Line 1091 |
| Exports: `is_unit()` | ✓ MATCHES | Line 1106 |
| Exports: `get_unit_category()` | ✓ MATCHES | Line 1254 |
| Exports: `get_all_units()` | ✓ MATCHES | Line 1284 |

**Discrepancy:** Document doesn't list many additional exports: `normalize_unit()`, `are_units_compatible()`, `convert_temperature()`, `UNIT_BASE`, `UNIT_CONVERSIONS`, `UNIT_ALIASES`, `UNIT_CATEGORIES`, `TEMPERATURE_CONVERSIONS`, `_rebuild_conversions()`, `list_units()` (referenced in tools.py:324 but not exported).

---

## Discrepancies Found

### 1. Test Count Outdated
**Severity:** Low (documentation)
- **Document says:** "All 350 tests pass" (line 5)
- **Actual:** 629 tests pass
- **Impact:** Users may think something is wrong if they run tests and see more passing than documented

### 2. exact/ Module Structure Incomplete
**Severity:** Medium (documentation)
- **Document shows:** 7 modules in exact/ (primitives, unicode_tools, measure, diff, validate, synthesis, confusables)
- **Actual:** 15+ modules (also: path_tools, identifier_inspect, transform, glob, identifier, position, and potentially others)
- **Impact:** Document severely under-represents the scope of the exact/ package
- **Files present but undocumented:**
  - `nl_calc/exact/path_tools.py`
  - `nl_calc/exact/identifier_inspect.py`
  - `nl_calc/exact/transform.py`
  - `nl_calc/exact/glob.py`
  - `nl_calc/exact/identifier.py`
  - `nl_calc/exact/position.py`

### 3. MCP Tool Schema Count
**Severity:** Medium (documentation)
- **Document shows:** 11 tools in the schemas.py table (lines 327-339)
- **Actual:** ~50+ tools defined in `TOOL_SCHEMAS` (lines 21-959)
- **Impact:** Document massively under-represents MCP server capabilities
- **Notable tools missing from doc table:** `json_canonicalize`, `json_query`, `text_window`, `text_fingerprint`, `identifier_analyze`, `identifier_inspect`, `glob_match`, `list_dedupe`, `list_sort`, `version_compare`, `path_normalize`, `path_analyze`, `json_shape`, `json_extract`, `json_compare`, `regex_finditer`, `regex_safety_check`, `validate_schema_light`, `validate_toml`, `escape_text`, `unescape_text`, `text_hash`, `text_position`, `unit_convert`, `unit_info`, `constant_lookup`

### 4. Module Dependencies Incomplete
**Severity:** Low (documentation)
- **Document says:** `normalize.py` → exact (only `inspect_text`)
- **Actual:** `normalize.py` also imports `count_chars` and `regex_test` from exact (line 25)
- **Impact:** Minor - doesn't reflect full dependency

### 5. normalize.py Imports Not Documented
**Severity:** Low (documentation)
- **Document shows:** No mention of exact/ imports in normalize.py section
- **Actual:** `normalize.py:25` imports `inspect_text`, `count_chars`, `regex_test` from exact

### 6. build_single.py Output Size
**Severity:** Low (documentation)
- **Document says:** "Output: Self-contained executable (~394KB)"
- **Actual:** Size may have changed with additions to exact/ and MCP modules

---

## Bugs Identified

### Bug 1: tools.py Imports Unused Function
**Severity:** Low
- **Location:** `nl_calc/mcp/tools.py:324`
- **Issue:** `unit_info()` function calls `list_units()` from `..units` but this function is not exported from `units.py`
- **Code:** `from ..units import UNIT_ALIASES, UNIT_CATEGORIES, UNIT_BASE, list_units`
- **Result:** If `unit_info` is called, it will fail with `NameError` when trying to use `list_units()`
- **Fix needed:** Either export `list_units` from units.py, or remove the import and fix the function logic

### Bug 2: tools.py Duplicate _VALID_TRANSFORM_OPERATIONS Definition
**Severity:** Low
- **Location:** `nl_calc/mcp/tools.py:839-853` and `nl_calc/mcp/tools.py:1337-1351`
- **Issue:** `_VALID_TRANSFORM_OPERATIONS` is defined twice in the same file
- **Note:** Second definition shadows first, but both are identical so no runtime issue occurs
- **Fix needed:** Remove duplicate definition

---

## Code Quality Issues

### Issue 1: tools.py Has Duplicate Constants
**Location:** `nl_calc/mcp/tools.py:839-853` and `nl_calc/mcp/tools.py:1337-1351`
**Issue:** `_VALID_TRANSFORM_OPERATIONS` defined twice
**Recommendation:** Remove first definition (lines 839-853)

### Issue 2: tools.py Imports Non-existent list_units
**Location:** `nl_calc/mcp/tools.py:324`
**Issue:** `unit_info()` tries to import and use `list_units()` which doesn't exist in units.py
**Recommendation:** Either add `list_units()` export to units.py, or fix the unit_info logic to not use it

---

## Improvements Suggested

### Priority: Medium

1. **Update test count in documentation**
   - Change "350 tests" to "629 tests" (or whatever current count is)
   - This ensures users aren't confused

2. **Update exact/ module listing**
   - Add all modules currently in exact/ package
   - Consider grouping modules by functionality

3. **Update MCP tools documentation**
   - Document all 50+ tools instead of just 11
   - Either expand the table or link to full schema

4. **Fix unit_info() function**
   - The function imports `list_units` which doesn't exist
   - Will cause NameError at runtime if called

5. **Remove duplicate _VALID_TRANSFORM_OPERATIONS definition**
   - Easy fix, just remove lines 839-853

### Priority: Low

6. **Add `list_units()` export to units.py**
   - Or remove its usage from tools.py
   - Currently inconsistent

7. **Document normalize.py exact/ dependencies**
   - Add `count_chars`, `regex_test` to module dependency diagram

---

## Priority Summary

| Priority | Item | Impact |
|----------|------|--------|
| **Medium** | Fix `unit_info()` - imports non-existent `list_units()` | Runtime error |
| **Medium** | Update exact/ module documentation | User confusion |
| **Medium** | Update MCP tools documentation | User confusion |
| **Medium** | Update test count | User confusion |
| **Low** | Remove duplicate `_VALID_TRANSFORM_OPERATIONS` | Code cleanliness |
| **Low** | Add `list_units` to units.py exports | API consistency |

---

## Verified as Correct

The following architectural claims have been verified as accurate:

1. **Data Flow (run pipeline):** Input → normalize() → normalize_expression() → evaluate() → Output ✓
2. **Data Flow (direct evaluate):** Input → AST parse → safe evaluation ✓
3. **Unit conversion handling:** Temperature conversions have special handling via offset math ✓
4. **CLI entry point:** __main__.py properly delegates to normalize.main() ✓
5. **AST-based evaluation:** No use of eval(), uses ast.parse + NodeVisitor pattern ✓
6. **Build system:** build_single.py correctly assembles all modules into single file ✓
7. **MCP server protocol:** Implements JSON-RPC 2.0 over stdio ✓
8. **Physical constants values:** Verified in evaluator.py match documented values

---

## Conclusion

The architecture document is outdated but the core architecture is sound. The main issues are:

1. **Missing modules** in exact/ and MCP documentation
2. **Runtime bug** in tools.py unit_info() function
3. **Duplicate code** in tools.py
4. **Stale test count** (350 vs 629 actual)

The code quality is generally good. The discrepancies appear to be from the codebase evolving without corresponding documentation updates.