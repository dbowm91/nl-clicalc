# evaluator.py Architecture Review

## Overview
Reviewed `architecture/evaluator.md` against `nl_calc/evaluator.py` (1516 lines).

---

## Verified Claims

### MATCHES - Key Exports
| Document | Code (`__all__` lines 29-54) |
|----------|------------------------------|
| All listed functions exported | Confirmed |

### MATCHES - Security Architecture
- Uses `ast.parse()` for parsing (line 1283)
- Whitelist approach for allowed operations
- `NOT eval()` - confirmed

### MATCHES - AST Node Handlers
| Node Type | Handler | Line |
|-----------|---------|------|
| `ast.Constant` | visit_Constant | 1100 |
| `ast.BinOp` | visit_BinOp | 1135 |
| `ast.UnaryOp` | visit_UnaryOp | 1182 |
| `ast.Call` | visit_Call | 1199 |
| `ast.Name` | visit_Name | 1121 |

### MATCHES - Forbidden Node Types
All listed types are rejected in `_validate_node()` (lines 1244-1278):
- ast.Compare, ast.BoolOp, ast.Subscript, ast.List, ast.Dict, ast.Set
- ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp, ast.Lambda, ast.IfExp

### MATCHES - Safe Math Functions
All documented functions are present in `FUNCTIONS` dict (lines 905-1026).

### MATCHES - Constants
All 30+ documented constants are defined in `CONSTANTS` (lines 836-902) with correct values:
- Physical constants (c, h, k, G, etc.) match CODATA 2018 values
- Mathematical constants (pi, e, tau) use `math.*` values

### MATCHES - Memory System
All documented functions present (lines 745-772):
- memory_store, memory_recall, memory_add, memory_subtract, memory_clear, memory_list

### MATCHES - Variable Storage
All documented functions present (lines 781-824):
- setvar, getvar, delvar, listvars, clearvars

### MATCHES - Limits and Safeguards
| Limit | Document | Code (lines 60-64) |
|-------|----------|-------------------|
| MAX_EXPONENT | 10000 | 10000 |
| MAX_FACTORIAL | 1000 | 1000 |
| MAX_NESTING_DEPTH | 100 | 100 |
| MAX_RESULT_VALUE | 1e308 | 1e308 |
| DEFAULT_CACHE_SIZE | 1024 | 1024 |

### MATCHES - Complex Number Support
`_complex_aware()` wrapper implemented correctly (lines 623-671).

### MATCHES - PyCalcApp
Implementation matches documentation (lines 1396-1516).

### MATCHES - Unit Handling
Returns `UnitValue` objects as documented.

---

## Discrepancies Found

### 1. `evaluate_async` and `evaluate_cached` not documented
**Severity:** Documentation gap
**Location:** `evaluator.md` lines 217-243

The document describes `evaluate()`, `evaluate_raw()`, `evaluate_with_timeout()` but not:
- `evaluate_cached()` (line 138) - LRU cached evaluation
- `evaluate_async()` (line 153) - Async evaluation for web frameworks

Both are exported in `__all__` but not documented.

### 2. `ln(x)` alias missing
**Severity:** Documentation mismatch
**Location:** `evaluator.md` line 95

Document claims:
```
log(x) / ln(x) — natural log
```

Only `log` is implemented in `FUNCTIONS`. No `ln` alias exists.

### 3. Return type inconsistency (minor)
**Severity:** Low
**Location:** `visit_BinOp` line 1180

Document shows examples like `evaluate("5 + 3")  # → 8` suggesting plain numeric return.

Reality:
```python
evaluate("5 + 3")  → UnitValue(8, None)  # wrapped
evaluate("pi")     → 3.14159...          # plain float
```

Binary operations always wrap results in `UnitValue`, even without units.

---

## Bugs Identified

### CRITICAL - `get_unit_category` not imported (NameError)

**Severity:** Critical (breaks temperature conversion)

**Location:** `evaluator.py:292`

```python
# Line 292 in _convert():
cat = get_unit_category(value.unit) if value.unit else None
```

**Problem:** `get_unit_category` is used but never imported from `units.py`.

**Imports at lines 20-27:**
```python
from .units import (
    UnitValue,
    UNIT_ALIASES,
    UNIT_CONVERSIONS,
    normalize_unit,
    convert_temperature,
    are_units_compatible,
)
# NOTE: get_unit_category is MISSING
```

**Verified:**
```python
>>> from nl_calc.evaluator import _convert, UnitValue
>>> _convert(UnitValue(100, 'degC'), 'degF')
NameError: name 'get_unit_category' is not defined
```

**Impact:** All temperature conversions through the `_convert` function fail with `NameError`. This affects:
- CLI: `calc "100F to C"` → crashes
- `evaluate_raw("100degC to degF")` → crashes
- Direct `_convert()` calls with temperature units

**Fix:** Add `get_unit_category` to imports from `.units`.

---

## Improvements Suggested

### Priority 1 - Fix Critical Bug
**File:** `evaluator.py` line 20-27

Add `get_unit_category` to imports:
```python
from .units import (
    UnitValue,
    UNIT_ALIASES,
    UNIT_CONVERSIONS,
    normalize_unit,
    convert_temperature,
    are_units_compatible,
    get_unit_category,  # ADD THIS
)
```

### Priority 2 - Document Missing Functions
**File:** `architecture/evaluator.md`

Add documentation for:
- `evaluate_cached(expression: str) -> Any` - LRU cached evaluation
- `evaluate_async(expression: str) -> Any` - Async evaluation

### Priority 3 - Add `ln` Alias
**File:** `evaluator.py` line 905-1026

Add to `FUNCTIONS` dict:
```python
"ln": _log,  # alias for natural log
```

Or document that only `log` is available for natural logarithm.

---

## Priority Summary

| Priority | Issue | Severity | Effort |
|----------|-------|----------|--------|
| 1 | Fix missing `get_unit_category` import | Critical | Low |
| 2 | Document `evaluate_async`/`evaluate_cached` | Documentation | Low |
| 3 | Add `ln` alias or fix documentation | Low | Low |
| 4 | Consider consistent return types | Low | Medium |

---

## Test Coverage

All 629 tests pass. However, temperature conversion tests only test `convert_temperature()` directly (units.py), not through the evaluator pipeline, which is why the `NameError` bug was not caught.

**Recommendation:** Add integration test for temperature conversion through `evaluate_raw()` or CLI.
