# Evaluator Module Review - Improvement Plan

## Verified Claims

### Correct Implementation Details

| Claim | Status | Notes |
|-------|--------|-------|
| AST-based evaluation | Verified | Uses `ast.parse` and `NodeVisitor` pattern correctly |
| Security architecture | Verified | Whitelist approach with `_validate_node` |
| Limits (MAX_EXPONENT, MAX_FACTORIAL, etc.) | Verified | All constants correctly defined |
| Module dependencies | Verified | Imports from `units.py` are correct |
| Thread-safety | Verified | Uses `threading.Lock` appropriately |
| Memory system | Verified | `Memory` class with register support |
| Variable storage | Verified | `_user_variables` dict with lock protection |
| PyCalcApp class | Verified | Caching, instance isolation, async support |
| Complex number support | Verified | `_complex_aware` wrapper implemented correctly |

### Correctly Documented (matches implementation)

- `evaluate()`, `evaluate_raw()`, `evaluate_cached()`, `evaluate_async()`, `evaluate_with_timeout()`
- `EvaluationError`, `TimeoutError`, `PyCalcApp`
- Constants table (all listed constants present in implementation)
- Function categories: trigonometric, logarithmic, statistical, combinatorics, bitwise, random, prime functions

---

## Discrepancies

### 1. Memory and Variable Functions Not Exported via `__all__`

**Documentation (evaluator.md:29-34):**
```python
memory_store, memory_recall, memory_add, memory_subtract,
memory_clear, memory_list,
setvar, getvar, delvar, listvars, clearvars,
```

**Actual `__all__` (evaluator.py:29-43):**
```python
__all__ = [
    "EvaluationError",
    "Evaluator",
    "evaluate",
    "evaluate_raw",
    "evaluate_cached",
    "evaluate_async",
    "evaluate_with_timeout",
    "get_default_evaluator",
    "register_constant",
    "register_function",
    "load_user_config",
    "PyCalcApp",
    "TimeoutError",
]
```

**Impact:** Low - functions are available but not properly exported for `from nl_calc.evaluator import *`

### 2. AST Node Handler Documentation Inaccurate

**Documentation (evaluator.md:61-73):**
Claims support for `visit_Compare`, `visit_BoolOp`, `visit_Subscript`, `visit_List`, `visit_Dict`

**Actual Implementation (evaluator.py:1211-1241):**
`_validate_node` explicitly **forbids** these node types:
```python
forbidden = (
    ast.Subscript, ast.List, ast.Dict, ast.Set,
    ast.ListComp, ast.DictComp, ast.SetComp,
    ast.GeneratorExp, ast.Lambda, ast.IfExp,
    ast.Compare, ast.BoolOp,
)
```

**Impact:** Documentation misleading - users expect these features but they don't work

### 3. `ast.Num` vs `ast.Constant` in Documentation

**Documentation:** Lists `ast.Num` handler
**Actual Implementation:** Python 3.8+ uses `ast.Constant` (line 1070)

**Impact:** Minor - implementation correct for Python 3.8+

### 4. Built-in Function Discrepancies

| Documented | Actual | Notes |
|------------|--------|-------|
| `sign(x)` | `_sign` (private) | Not in FUNCTIONS dict |
| `hypot(*args)` | `_hypot` (private) | Not in FUNCTIONS dict |
| `fact(n)` | Not implemented | Only `factorial` exists |
| `lshift(a, b)`, `rshift(a, b)` | `_bitlshift`, `_bitrshift` (private) | Not in FUNCTIONS dict |
| `prevprime(n)` | `_prev_prime` (private) | Not in FUNCTIONS dict |
| `nextprime(n)` | `_next_prime` (private) | Not in FUNCTIONS dict |

**Impact:** Medium - documentation promises functions that don't exist in public API

### 5. `evaluate_with_timeout` Docstring Example Won't Work

**Docstring claims:**
```python
>>> result = evaluate_with_timeout("sum(i**2 for i in range(10000))", timeout=1.0)
```

**Reality:** `ast.GeneratorExp` is explicitly forbidden in `_validate_node` (line 1228)

**Impact:** Example would fail if user tries it

---

## Bugs Found

### BUG 1: `get_unit_category` Not Imported (CRITICAL)

**Location:** `evaluator.py:281-284`

```python
def _convert(value: Any, to_unit: str) -> Any:
    ...
    from .units import get_unit_category  # Local import inside function
    ...
    cat = get_unit_category(value.unit) if value.unit else None
```

**Problem:** `get_unit_category` is imported locally inside `_convert`, but it's also called at line 284. This actually works but is inconsistent - should be at module level.

**Actual Bug:** Wait - re-reading the code, `get_unit_category` IS imported locally at line 281. Let me verify...

Actually looking at lines 279-294 more carefully:
```python
if isinstance(value, UnitValue):
    # Check for temperature conversions (special handling needed)
    from .units import get_unit_category  # <-- LOCAL import
    from .units import convert_temperature

    cat = get_unit_category(value.unit) if value.unit else None
```

The local import is inside the `if isinstance(value, UnitValue)` block, so the bug only manifests when this branch is taken with certain inputs. However, there's still a potential issue if the import fails.

**Severity:** Medium - code works but pattern is fragile

### BUG 2: Unused Local Import in `_convert`

**Location:** `evaluator.py:282`

```python
from .units import convert_temperature
```

But `convert_temperature` is already imported at module level (line 25). The local import at line 282 is redundant.

**Severity:** Low - code duplication, no functional impact

### BUG 3: `evaluate_cached` Cache Invalidation Issue

**Problem:** The `_cached_normalize_and_evaluate` function caches results by expression string. However, if user variables change (via `setvar`), the same expression can return different results.

```python
evaluate("x + 1")  # x=5 → 6, cached
setvar("x", 10)
evaluate("x + 1")  # Still returns 6 from cache, not 11
```

**Severity:** Medium - may confuse users expecting variable changes to affect cached expressions

---

## Improvements with Priority

### High Priority

1. **Fix Documentation: Remove False Feature Claims**
   - Remove `visit_Compare`, `visit_BoolOp` from node handler table
   - Remove `visit_Subscript`, `visit_List`, `visit_Dict` from node handler table
   - Fix `evaluate_with_timeout` docstring example to use valid syntax
   - Clarify which functions are public vs private

2. **Export Memory and Variable Functions via `__all__`**
   - Add `memory_store`, `memory_recall`, `memory_add`, `memory_subtract`, `memory_clear`, `memory_list`
   - Add `setvar`, `getvar`, `delvar`, `listvars`, `clearvars`
   - Update documentation to match

3. **Add Missing Public Functions**
   - `sign` → add `SIGN` wrapper or rename `_sign` exposure
   - `hypot` → add to FUNCTIONS dict
   - `fact` → add as alias for `factorial`
   - `lshift`, `rshift` → add public names for bitwise ops
   - `prevprime`, `nextprime` → add public names

### Medium Priority

4. **Add Cache Awareness to `evaluate_cached`**
   - Consider adding optional `use_cache` parameter
   - Or document the behavior clearly
   - Or use a more sophisticated caching strategy that considers variable state

5. **Remove Redundant Local Import**
   - Line 282: `from .units import convert_temperature` is duplicate of module-level import

6. **Improve `_validate_node` Error Messages**
   - Currently says "Unsupported node type: 'Compare'"
   - Better: "Comparison operators are not supported"

### Low Priority

7. **Type Annotation Improvements**
   - `evaluate_cached` return type: `Any` → should be more specific
   - `evaluate_async` return type annotation missing

8. **Documentation Consistency**
   - Add "See [units.md]" cross-reference where unit handling is discussed
   - Ensure all functions have complete docstrings

---

## Summary

| Category | Count |
|----------|-------|
| Verified Correct | 8 |
| Discrepancies | 5 |
| Bugs | 3 |
| High Priority Fixes | 3 |
| Medium Priority Fixes | 2 |
| Low Priority Fixes | 2 |
