# Architecture Overview Review

## Executive Summary

This review compares the documented architecture in `architecture/overview.md` against the actual implementation in `nl_calc/` to identify discrepancies, bugs, and improvement opportunities.

**Overall Assessment**: The architecture documentation is largely accurate and well-structured. Core module purposes are correctly documented, the security model is accurately described, and the build process exists as documented. However, several discrepancies exist between documented and implemented behavior, plus some documentation gaps and code quality issues.

---

## Summary of What the Overview Describes

The `architecture/overview.md` documents:

1. **System Architecture**: Top-level `nl_calc.__init__` re-exports, with core modules `normalize.py`, `evaluator.py`, `units.py` and supporting modules `exact/` (text inspection tools) and `mcp/` (MCP server)

2. **Processing Pipelines**: Two paths - Full Pipeline (normalize → evaluate) and Direct Evaluation (evaluate only)

3. **Core Modules**: normalize.py (NL processing), evaluator.py (AST evaluation), units.py (unit definitions), __main__.py (CLI), __init__.py (public API)

4. **Supporting Modules**: exact/ with primitives, unicode_tools, confusables, validate, diff, measure, synthesis; mcp/ with server, tools, schemas

5. **Data Structures**: NUMBER_WORDS, OPERATOR_CONVERSIONS, UNIT_BASE, UNIT_CONVERSIONS, UNIT_ALIASES, FUNCTION_MAPPINGS

6. **Types**: UnitValue, EvaluationError, TimeoutError

7. **Security Model**: AST-based parsing (not eval()), controlled function whitelist, DoS protection (max nesting, exponent, factorial limits), timeout support

8. **Build Process**: build_single.py combines into nl_calc.py, install.py installs to ~/.local/bin/calc

---

## Verified Claims (Matching Doc and Code)

### ✓ Core Module Structure
All four core modules exist with correctly documented purposes:
- `nl_calc/normalize.py` - NL tokenization, number word conversion, expression normalization (1319 lines)
- `nl_calc/evaluator.py` - AST parsing and evaluation, mathematical operations (1469 lines)
- `nl_calc/units.py` - Unit definitions, conversion factors, temperature conversions (1259 lines)
- `nl_calc/__main__.py` - CLI entry point (19 lines)

### ✓ Public API Surface
`__init__.py` correctly exports the documented API surface including evaluate, run, normalize, UnitValue, EvaluationError, TimeoutError, and various configuration constants.

### ✓ Security Model
- AST-based evaluation via `ast.parse()` and NodeVisitor pattern (evaluator.py:1237-1259)
- Whitelist of safe functions in `Evaluator.FUNCTIONS` dict (lines 876-994)
- DoS protection: MAX_EXPONENT=10000 (line 49), MAX_FACTORIAL=1000 (line 50), MAX_NESTING_DEPTH=100 (line 51)
- Timeout support via `evaluate_with_timeout()` (lines 1303-1334)

### ✓ UnitValue Type
Correctly implemented in units.py:24-141 with arithmetic operations, conversion methods, and proper unit handling.

### ✓ Build Process
- `build_single.py` exists and correctly combines all modules
- `install.py` calls build_single.py and installs
- All code in core modules for assembly to work

### ✓ exact/ Supporting Modules
All submodules exist and are properly structured:
- `exact/__init__.py` re-exports all primitives (134 lines)
- `exact/primitives.py`, `exact/diff.py`, `exact/validate.py`, `exact/measure.py`, `exact/unicode_tools.py`, `exact/synthesis.py`, `exact/confusables.py` all exist

### ✓ mcp/ Supporting Modules
All submodules exist:
- `mcp/__init__.py` (13 lines)
- `mcp/server.py` - stdio-based MCP request handling (420 lines)
- `mcp/tools.py` - MCP tool definitions
- `mcp/schemas.py` - JSON schemas

### ✓ Data Structure Constants
- NUMBER_WORDS (normalize.py:220-261) - correctly maps number words to values
- OPERATOR_CONVERSIONS (normalize.py:101-119) - correctly maps operator words to symbols
- UNIT_BASE (units.py:145-572) - correctly defines base units and conversion factors
- UNIT_CONVERSIONS (units.py:592) - pre-computed pairwise conversion factors
- UNIT_ALIASES (units.py:605-1022) - maps unit variants to canonical forms
- FUNCTION_MAPPINGS (normalize.py:123-217) - maps function name variants to canonical names

---

## Issues Found

### 1. Documentation Index Links to Non-Existent Files

**Location**: `architecture/overview.md` lines 143-156

**Issue**: The index references individual module docs that don't exist:
```
- [primitives.md](primitives.md)
- [unicode_tools.md](unicode_tools.md)
- [confusables.md](confusables.md)
- [validate.md](validate.md)
- [diff.md](diff.md)
- [measure.md](measure.md)
- [synthesis.md](synthesis.md)
```

Actual architecture docs are: `exact.md` (combined for all exact modules) and `mcp_server.md`. The 1:1 mapping of modules to docs doesn't match reality.

**Fix**: Update index to reference actual doc files or create missing docs.

---

### 2. Processing Pipeline Description Partially Incorrect

**Location**: `architecture/overview.md` lines 52-61

**Documentation says**:
```
Input → normalize() → normalize_expression() → evaluate() → Result
```

**Actual flow** (`normalize.py:948-989`):
```python
def run(expression, operators, patterns, ...):
    joined, exit_code = normalize_expression(expression, operators, patterns)
    # normalize_expression() internally calls normalize()
    result = evaluate(joined)  # Direct call, not shown in diagram
    return result, 0
```

**Issue**: The diagram shows `normalize() → normalize_expression() → evaluate()` but the actual flow is `run() → normalize_expression() → normalize()` then `evaluate()`. The normalize() call is internal to normalize_expression().

**Fix**: Update diagram to show accurate calling hierarchy:
```
Input → run() → normalize_expression() → normalize() → split_at_operators() → evaluate() → Result
```

---

### 3. Direct Evaluation Path Description Misleading

**Location**: `architecture/overview.md` lines 62-68

**Documentation says**: "Skips normalization, directly parses via Python AST."

**Actual** (`evaluator.py:1262-1268`):
```python
def evaluate(expression: str) -> Any:
    _ensure_config_loaded()
    return _default_evaluator.evaluate(expression)
```

The `Evaluator.evaluate()` (lines 1237-1259) uses `ast.parse()` then visits nodes - it's the same AST-based evaluation as the full pipeline, just without NL normalization.

**Fix**: Clarify that `evaluate()` uses AST parsing via the `Evaluator` class, but skips the NL normalization step.

---

### 4. Missing Unit Category for `mps`

**Location**: `units.py` lines 496-513 and 1089-1226

**Issue**: The `mps` speed unit is defined in UNIT_BASE:
```python
"m/s": {
    "mps": 1.0,  # line 498
    ...
}
```

But in UNIT_CATEGORIES (lines 1089-1226), `mps` is not listed. Only these speed units are categorized:
```python
"m/s": "speed",   # line 1206
"km/h": "speed",
"mph": "speed",
"kn": "speed",
"mach": "speed",
```

**Impact**: `get_unit_category("mps")` returns `None`, causing `are_units_compatible("mps", "km/h")` to incorrectly return `True` (since None is compatible with everything per line 1251-1252).

**Fix**: Add `"mps": "speed"` to `UNIT_CATEGORIES`.

---

### 5. `Memory` Type Not Documented

**Location**: `architecture/overview.md` lines 120-125

**Documentation lists**:
- `UnitValue` - Represents a numeric value with optional units
- `EvaluationError` - Raised when expression is invalid
- `TimeoutError` - Raised when evaluation exceeds timeout

**Actual** (`evaluator.py:664-723`): The `Memory` class exists and is exported via `__init__.py` (line 36, 72). It's used for calculator memory functions (M+, M-, MR, MC).

**Fix**: Add `Memory` to the Types documentation.

---

### 6. `normalize_expression` Not Documented in API

**Location**: `architecture/overview.md` lines 70-78 and `architecture/api.md`

**Issue**: `normalize_expression()` is exported from `__init__.py` (line 54) and is useful for custom evaluators, but it's not documented in the API section.

**Fix**: Add `normalize_expression` to the Utility Functions section in api.md.

---

### 7. `CONSTANT_WORDS` and `STRIPPED_PHRASES` Not Documented

**Location**: `normalize.py` lines 264-300

**Issue**: `CONSTANT_WORDS` (physical constant word mappings) and `STRIPPED_PHRASES` (phrases removed from input) are undocumented but affect natural language processing behavior.

**Fix**: Document these in normalize.md.

---

### 8. Build Process Documentation Incomplete

**Location**: `architecture/overview.md` lines 131-141

**Documentation says**: "All code must be in one of the core modules for assembly to work."

**Actual** (`build_single.py:21-43`): The build actually includes ALL modules:
```python
MODULES_CALC = ["units", "evaluator", "normalize"]
MODULES_EXACT = ["exact/primitives", "exact/diff", ...]
MODULES_MCP = ["mcp/schemas", "mcp/tools", "mcp/server"]
```

Also, `build_single.py` renames functions to avoid conflicts (`normalize.main()` → `normalize_main()`, MCP `main()` → `mcp_main()`), which is undocumented.

**Fix**: Update documentation to state that ALL modules (calc, exact, mcp) are assembled, and document function renaming behavior.

---

### 9. Duplicate MAX_NESTING_DEPTH Constants

**Location**: `normalize.py:43` and `evaluator.py:51`

**Issue**: `MAX_NESTING_DEPTH = 100` is defined in both modules. This is a maintenance issue - if one is changed without the other, behavior could diverge.

**Fix**: Move `MAX_NESTING_DEPTH` to a shared location (e.g., `__init__.py` or a constants module).

---

### 10. `variance_sample` Not Exposed in FUNCTIONS

**Location**: `evaluator.py:380-385`

**Code**:
```python
def _variance_sample(*args: float) -> float:
    """Calculate sample variance (n-1 denominator)."""
    ...
```

This function is defined but NOT in the FUNCTIONS dict (lines 876-994), so it's not accessible to users. Only `variance` (population variance) is exposed.

**Fix**: Either add `variance_sample` to FUNCTIONS dict or clarify that only population variance is supported.

---

### 11. Inconsistent Error Handling in `_convert`

**Location**: `evaluator.py:272-301`

**Issue**: When temperature conversion fails (line 182-183), it silently falls through to regular unit conversion:
```python
try:
    converted_val = convert_temperature(value.value, value.unit, to_unit)
    return UnitValue(converted_val, to_unit)
except ValueError:
    pass  # Fall through to regular conversion
```

This could mask errors - e.g., converting `100 K` to `ft` might silently give a wrong result via regular conversion.

**Fix**: Either raise an error when temperature conversion fails, or document this fallback behavior explicitly.

---

## Improvement Recommendations

### High Priority

1. **Fix index links** (`architecture/overview.md:143-156`): Update to reference existing `exact.md` and `mcp_server.md` instead of non-existent per-module docs.

2. **Add `mps` to UNIT_CATEGORIES** (`units.py:1089-1226`): Add `"mps": "speed"` to fix the unit compatibility check bug.

3. **Document `Memory` type** (`architecture/overview.md:120-125`): Add `Memory` to the Types section as it's exported and functional.

### Medium Priority

4. **Clarify processing pipeline** (`architecture/overview.md:52-61`): Update diagram to show `run() → normalize_expression() → normalize()` calling hierarchy.

5. **Document `normalize_expression`** (`architecture/api.md`): Add to Utility Functions since it's exported and useful for custom evaluators.

6. **Document `CONSTANT_WORDS` and `STRIPPED_PHRASES`** (`architecture/normalize.md`): Add documentation for these normalization constants.

7. **Document build function renaming** (`architecture/overview.md:131-141`): Explain that `normalize.main()` becomes `normalize_main()` and MCP `main()` becomes `mcp_main()` to avoid conflicts.

### Low Priority

8. **Fix typo in docstring** (`normalize.py:843`): `2meters` → `2 meters`.

9. **Consider adding `variance_sample`** to FUNCTIONS dict if sample variance support is desired.

10. **Consolidate duplicate MAX_NESTING_DEPTH** into a shared constants location.

---

## Bug Summary

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Medium | `architecture/overview.md:143-156` | Index links to non-existent docs |
| 2 | Low | `architecture/overview.md:52-61` | Pipeline diagram inaccurate |
| 3 | Low | `architecture/overview.md:62-68` | Direct evaluation description misleading |
| 4 | **High** | `units.py:1089-1226` | `mps` missing from UNIT_CATEGORIES (compatibility bug) |
| 5 | Low | `architecture/overview.md:120-125` | `Memory` type undocumented |
| 6 | Low | `architecture/api.md` | `normalize_expression` undocumented |
| 7 | Low | `architecture/normalize.md` | `CONSTANT_WORDS`, `STRIPPED_PHRASES` undocumented |
| 8 | Low | `architecture/overview.md:131-141` | Build process docs incomplete |
| 9 | Low | `normalize.py:43`, `evaluator.py:51` | Duplicate MAX_NESTING_DEPTH constant |
| 10 | Low | `evaluator.py:876-994` | `variance_sample` not in FUNCTIONS |
| 11 | Low | `evaluator.py:182-183` | Silent fallthrough in temperature conversion error |

---

## Appendix: Code Reference Index

| File | Lines | Description |
|------|-------|-------------|
| `nl_calc/__init__.py` | 1-116 | Public API surface |
| `nl_calc/normalize.py` | 1-1319 | NL processing pipeline |
| `nl_calc/evaluator.py` | 1-1469 | AST-based evaluation |
| `nl_calc/units.py` | 1-1259 | Unit definitions and conversions |
| `nl_calc/__main__.py` | 1-19 | CLI entry point |
| `nl_calc/exact/__init__.py` | 1-134 | Exact module exports |
| `nl_calc/mcp/__init__.py` | 1-13 | MCP module exports |
| `build_single.py` | 1-436 | Single-file assembly script |