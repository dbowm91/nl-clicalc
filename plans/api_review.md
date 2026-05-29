# API Documentation Review

## Overview

This document reviews the claims made in `architecture/api.md` against the actual implementation in the nl-calc codebase. The review identifies verified claims, discrepancies, bugs, and suggested improvements.

---

## Verified Claims

### Core Evaluation Functions

| Function | Status | Location |
|----------|--------|----------|
| `evaluate(expression: str) -> Any` | **MATCHES** | evaluator.py:1305-1311 |
| `evaluate_raw(expression: str) -> Any` | **MATCHES** | evaluator.py:1314-1337 |
| `evaluate_cached(expression: str) -> Any` | **MATCHES** | evaluator.py:138-150, uses LRU_CACHE_SIZE=1024 |
| `evaluate_async(expression: str) -> Awaitable[Any]` | **MATCHES** | evaluator.py:153-165 |
| `evaluate_with_timeout(expression: str, timeout: float = 5.0) -> Any` | **MATCHES** | evaluator.py:1346-1381 |

### Webapp Wrapper

| Component | Status | Location |
|-----------|--------|----------|
| `PyCalcApp` (thread-safe, caching, async) | **MATCHES** | evaluator.py:1396-1516 |
| `Evaluator` (low-level AST) | **MATCHES** | evaluator.py:827-1302 |

### Configuration Functions

| Function | Status | Location |
|----------|--------|----------|
| `register_constant(name: str, value: float) -> None` | **MATCHES** | evaluator.py:67-70 |
| `register_function(name: str, func: Callable) -> None` | **MATCHES** | evaluator.py:73-76 |
| `get_default_evaluator() -> Evaluator` | **MATCHES** | evaluator.py:1387-1393 |
| `load_user_config() -> None` | **MATCHES** | evaluator.py:79-115 |

### Memory Functions

| Function | Status | Location |
|----------|--------|----------|
| `memory_store(value, register="M")` | **MATCHES** | evaluator.py:745-747 |
| `memory_recall(register="M")` | **MATCHES** | evaluator.py:750-752 |
| `memory_add(value, register="M")` | **MATCHES** | evaluator.py:755-757 |
| `memory_subtract(value, register="M")` | **MATCHES** | evaluator.py:760-762 |
| `memory_clear(register=None)` | **MATCHES** | evaluator.py:765-767 |
| `memory_list()` | **MATCHES** | evaluator.py:770-772 |

### Variable Functions

| Function | Status | Location |
|----------|--------|----------|
| `setvar(name, value)` | **MATCHES** | evaluator.py:781-793 |
| `getvar(name)` | **MATCHES** | evaluator.py:796-806 (returns 0 if not found) |
| `delvar(name)` | **MATCHES** | evaluator.py:809-812 |
| `listvars()` | **MATCHES** | evaluator.py:815-818 |
| `clearvars()` | **MATCHES** | evaluator.py:821-824 |

### Utility Functions

| Function | Status | Location |
|----------|--------|----------|
| `normalize_unit("kilometers")` -> "km" | **MATCHES** | units.py:1047-1049 |
| `get_conversion_factor("ft", "m")` -> 0.3048 | **MATCHES** | units.py:1091-1103 |
| `get_all_units()` | **MATCHES** | units.py:1284-1286 |
| `is_unit("m")` | **MATCHES** | units.py:1106-1108 |
| `get_unit_category("m")` -> "length" | **MATCHES** | units.py:1254-1257 |
| `are_units_compatible("m", "ft")` | **MATCHES** | units.py:1260-1281 |
| `FLOAT_EPSILON` = 1e-10 | **MATCHES** | units.py:20 |

### Security Constants

| Constant | Doc Value | Actual Value | Location | Status |
|----------|-----------|--------------|----------|--------|
| `MAX_EXPONENT` | 10000 | 10000 | evaluator.py:60 | **MATCHES** |
| `MAX_FACTORIAL` | 1000 | 1000 | evaluator.py:61 | **MATCHES** |
| `MAX_NESTING_DEPTH` | 100 | 100 | evaluator.py:62 | **MATCHES** |
| `MAX_RESULT_VALUE` | 1e308 | 1e308 | evaluator.py:63 | **MATCHES** |
| `DEFAULT_CACHE_SIZE` | 1024 | 1024 | evaluator.py:64 | **MATCHES** |

### Input Limits

| Constant | Doc Value | Actual Value | Location | Status |
|----------|-----------|--------------|----------|--------|
| `MAX_INPUT_LENGTH` | 10000 | 10000 | normalize.py:42 | **MATCHES** |
| `MAX_NESTING_DEPTH` | 100 | 100 | normalize.py:43, evaluator.py:62 | **MATCHES** |

### Types

| Type | Status | Location |
|------|--------|----------|
| `UnitValue` class | **MATCHES** | units.py:24-156 |
| `EvaluationError` | **MATCHES** | evaluator.py:674-677 |
| `TimeoutError` | **MATCHES** | evaluator.py:1340-1343 |
| `Memory` class | **MATCHES** | evaluator.py:680-738 |

### UnitValue Behavior

The documentation shows:
```python
uv = UnitValue(5, "m")
print(f"{uv}")        # "5.0 m"
print(uv.value)       # 5.0
print(uv.unit)        # "m"
```

This **MATCHES** the implementation at units.py:35-46 (`__repr__`, `value`, `unit`).

---

## Discrepancies Found

### 1. `normalize_expression` Return Type (MEDIUM)

**Doc says:**
```python
def normalize_expression(expression: str) -> str
```

**Actual:**
```python
def normalize_expression(expression: str, operators: dict, patterns: Mapping[str, Pattern[str]], skip_validation: bool = False) -> tuple[str, int]
```

**Returns:** `tuple[str, int]` - (normalized_expression, exit_code)

**Impact:** Code using the documented signature will fail to unpack the tuple correctly. Example in doc shows only string being returned:
```python
normalize_expression("five plus three")  # "5+3"
```

Actual result: `("5+3", 0)`

**Recommendation:** Update documentation to show correct return type.

---

### 2. `evaluate()` Handles Spaces (LOW)

**Doc says:**
```python
def evaluate(expression: str) -> Any
Evaluate a pre-normalized expression (no spaces, no natural language).
```

**Actual:** The function calls `ast.parse(expression, mode="eval")` which accepts spaces. The docstring could be clearer that this function is intended for pre-normalized input but technically accepts any valid Python expression syntax.

**Example:**
```python
evaluate("5 + 3")  # Works, returns 8
```

**Impact:** Minor confusion about intended use case. The function works but the docstring is guidance, not a restriction.

---

### 3. Performance Characteristics Not Verified (INFO)

The document lists performance timings:
- `evaluate()`: ~10 μs/eval
- `evaluate_raw()`: ~155 μs/eval
- `evaluate_cached()`: ~0.1 μs/eval
- `PyCalcApp.calculate()`: ~0.3 μs/eval

These are documented but not verified against actual benchmarks. No timing tests exist in the codebase. These should be treated as estimates.

---

## Bugs Identified

### 1. No Bugs Found in Core Implementation

The architecture review from `plans/plan.md` previously identified and fixed these critical bugs:
- Temperature-to-non-temperature conversion (units.py:146-164) - **FIXED**
- Dead code in `list_compare()` near_matches (synthesis.py:704-714) - **FIXED**
- Float regex pattern `[-|+]?` to `[-+]?` (normalize.py:368) - **FIXED**

### 2. Potential Edge Cases (LOW)

#### Edge Case: `evaluate_raw` uses `skip_validation=True`
At evaluator.py:1332-1336, `evaluate_raw` calls `normalize_expression` with `skip_validation=True`, which may skip token validation in some paths.

#### Edge Case: `_handle_negative_token` bounds checking
At normalize.py:691, the bounds check:
```python
if index < 2 or index >= len(tokens) or (index - 1) >= len(tokens) or (index - 2) >= len(tokens):
    return tokens, []
```
This appears correct but the logic is complex and could be simplified.

#### Edge Case: Complex number `1j` vs `i` suffix
The normalization converts `i` suffix to `j` for complex numbers (normalize.py:907-911), but there may be edge cases with expressions like `i` alone (which becomes `1j`).

---

## Improvements Suggested

### Priority: LOW

#### 1. Document the `normalize_expression` signature correctly
The function takes 4 arguments but documentation shows 1. The actual signature should be documented:
```python
def normalize_expression(
    expression: str,
    operators: dict,
    patterns: Mapping[str, Pattern[str]],
    skip_validation: bool = False,
) -> tuple[str, int]:
```

#### 2. Add performance benchmark tests
The documented performance characteristics (~10 μs, ~155 μs, etc.) should be verified with actual benchmark tests to ensure they remain accurate as code evolves.

#### 3. Consider adding type stubs
The codebase uses Python typing but some functions like `evaluate_async` use `Awaitable[Any]` which is appropriate for Python 3.7+ but could be more specific.

#### 4. Document `load_user_config_extended` behavior
The function `load_user_config_extended` exists (evaluator.py:168-187) but is not exported. The comment at `__init__.py:22-23` explains this is intentional because custom number/operator words via external config are not officially supported. This design decision could be more prominently documented.

---

## Priority Summary

| Priority | Item | Description |
|----------|------|-------------|
| **MEDIUM** | `normalize_expression` return type | Documentation shows `str` but actual return is `tuple[str, int]` |
| **LOW** | `evaluate()` docstring | Mentions "no spaces" but function accepts spaces |
| **INFO** | Performance timings | Listed but not verified with benchmarks |
| **LOW** | Edge case complexity | Some bounds-checking logic in `_handle_negative_token` is complex |

---

## Conclusion

The API documentation is largely accurate with one significant discrepancy: `normalize_expression` returns a tuple but documentation shows a string. Most other claims match the implementation. The code appears well-tested and the architecture review has already addressed previous critical bugs.

The most important fix needed is updating the `normalize_expression` documentation to show the correct return type of `tuple[str, int]`.