# API Review: architecture/api.md vs Implementation

## Summary

`nl_calc` is a natural language math expression calculator that converts English phrases like "five plus three" into numeric results. It supports unit conversions, memory registers, user-defined variables, and various mathematical functions. The core evaluation uses Python AST parsing for security.

---

## Verified Claims (Match Between Doc and Code)

### Package Entry Point
| Claim | Status | Location |
|-------|--------|----------|
| `__init__.py` re-exports all public functionality | ✅ Verified | `__init__.py:23-55` |

### Core Evaluation Functions
| Function | Doc Claim | Status | Implementation |
|----------|-----------|--------|-----------------|
| `evaluate(expression)` | Pre-normalized input | ✅ | `evaluator.py:1262-1268` |
| `evaluate_raw(expression)` | NL/spaces support | ✅ | `evaluator.py:1271-1294` |
| `evaluate_cached(expression)` | LRU caching (1024 entries) | ✅ | `evaluator.py:127-139` |
| `evaluate_async(expression)` | Async for web frameworks | ✅ | `evaluator.py:142-154` |
| `evaluate_with_timeout(expression, timeout)` | Timeout for untrusted input | ✅ | `evaluator.py:1303-1334` |

### Webapp Wrapper
| Claim | Status | Location |
|-------|--------|----------|
| `PyCalcApp` class exists | ✅ | `evaluator.py:1349-1469` |
| Thread-safe with caching | ✅ | Uses `threading.Lock` and `OrderedDict` |
| `cache_size` parameter | ✅ | `evaluator.py:1367` (default `DEFAULT_CACHE_SIZE`) |
| Async support via `calculate_async()` | ✅ | `evaluator.py:1410-1425` |

### Configuration Functions
| Function | Status | Location |
|----------|--------|----------|
| `register_constant()` | ✅ | `evaluator.py:56-59` |
| `register_function()` | ✅ | `evaluator.py:62-65` |
| `load_user_config()` | ✅ | `evaluator.py:68-104` |

### Memory Functions
| Function | Status | Location |
|----------|--------|----------|
| `memory_store()` | ✅ | `evaluator.py:729-731` |
| `memory_recall()` | ✅ | `evaluator.py:734-736` |
| `memory_add()` | ✅ | `evaluator.py:739-741` |
| `memory_subtract()` | ✅ | `evaluator.py:744-746` |
| `memory_clear()` | ✅ | `evaluator.py:749-751` |
| `memory_list()` | ✅ | `evaluator.py:754-756` |

### Variable Functions
| Function | Status | Location |
|----------|--------|----------|
| `setvar()` | ✅ | `evaluator.py:765-777` |
| `getvar()` | ✅ | `evaluator.py:780-790` (returns 0 if not found) |
| `delvar()` | ✅ | `evaluator.py:793-796` |
| `listvars()` | ✅ | `evaluator.py:799-802` |
| `clearvars()` | ✅ | `evaluator.py:805-808` |

### Utility Functions
| Function | Status | Location |
|----------|--------|----------|
| `normalize_unit()` | ✅ | `units.py:1025-1027` |
| `get_conversion_factor()` | ✅ | `units.py:1069-1081` |
| `get_all_units()` | ✅ | `units.py:1257-1259` |
| `is_unit()` | ✅ | `units.py:1084-1086` |

### Types
| Type | Status | Location |
|------|--------|----------|
| `UnitValue` | ✅ | `units.py:24-142` |
| `EvaluationError` | ✅ | `evaluator.py:658-661` |
| `TimeoutError` | ✅ | `evaluator.py:1297-1300` |
| `Memory` class | ✅ | `evaluator.py:664-722` |

### Security Constants
| Constant | Doc Value | Actual Value | Location |
|----------|-----------|--------------|----------|
| `MAX_EXPONENT` | 10000 | 10000 | `evaluator.py:49` |
| `MAX_FACTORIAL` | 1000 | 1000 | `evaluator.py:50` |
| `MAX_NESTING_DEPTH` | 100 | 100 | `evaluator.py:51` |
| `MAX_RESULT_VALUE` | 1e308 | 1e308 | `evaluator.py:52` |
| `DEFAULT_CACHE_SIZE` | 1024 | 1024 | `evaluator.py:53` |

---

## Issues Found

### 1. Cache Size Default Mismatch (PyCalcApp)

**Severity:** Minor (documentation inaccuracy)

**Issue:** The API doc claims `cache_size=1000` for `PyCalcApp`, but the actual default is `DEFAULT_CACHE_SIZE` which equals 1024.

| Location | Value |
|----------|-------|
| `architecture/api.md:62` | `cache_size=1000` |
| `evaluator.py:1367` | `cache_size: int = DEFAULT_CACHE_SIZE` |
| `evaluator.py:53` | `DEFAULT_CACHE_SIZE = 1024` |

**Recommendation:** Update the doc to say `cache_size=1024` or change the code to use `1000`.

---

### 2. `get_default_evaluator()` Missing from `__all__`

**Severity:** Minor (export list omission)

**Issue:** `get_default_evaluator()` is exported from `__init__.py` (line 31) but not listed in `__all__` (line 60-114).

**Location:** `__init__.py:96` exports it but `__all__` omits it.

**Recommendation:** Add `get_default_evaluator` to `__all__` at `__init__.py:96`.

---

### 3. `evaluate_with_timeout` Example is Misleading

**Severity:** Documentation bug

**Issue:** The doc shows `evaluate_with_timeout("2 ** 1000000", timeout=1.0)` as an example that raises TimeoutError, but `MAX_EXPONENT = 10000` means this expression would fail with `EvaluationError` ("Exponent too large") before the timeout could take effect.

**Locations:**
- `architecture/api.md:51-52` 
- `evaluator.py:179-188` (`_safe_pow` enforces `MAX_EXPONENT = 10000`)

**Recommendation:** Change the example to one that would actually timeout, such as:
```python
result = evaluate_with_timeout("sum(range(10**7))", timeout=0.001)
# May raise TimeoutError (depends on system speed)
```
Or add a note that expressions exceeding MAX_EXPONENT will fail before timeout.

---

### 4. `load_user_config_extended()` Not Exported

**Severity:** Feature visibility

**Issue:** The function `load_user_config_extended()` exists at `evaluator.py:157-176` but is not exported from `__init__.py`. This function loads custom number words and operator words from config, which `load_user_config()` does not handle.

**Recommendation:** Either:
1. Export `load_user_config_extended` from `__init__.py` if it's intended for public use, or
2. Document that custom number/operator words are not supported via user config

---

### 5. `Memory` Class Doc Mismatch

**Severity:** Minor

**Issue:** The doc says "returned by `memory_*` functions return floats, but `Memory` class available for type hints" at `architecture/api.md:149`. This is technically correct but confusing. The `memory_*` functions return `float`, not `Memory` objects.

**Recommendation:** Rewrite for clarity:
```markdown
## Memory Functions

Memory functions store and retrieve calculator values:

| Function | Description | Returns |
|----------|-------------|---------|
| `memory_store(value, register="M")` | Store value | `float` |
| `memory_recall(register="M")` | Recall value | `float` |
| `memory_add(value, register="M")` | Add to memory (M+) | `float` |
| `memory_subtract(value, register="M")` | Subtract from memory (M-) | `float` |
| `memory_clear(register=None)` | Clear memory | `None` |
| `memory_list()` | List all registers | `dict[str, float]` |

The `Memory` class is available for type hints.
```

---

### 6. Performance Characteristics Not Verified

**Severity:** Info/Not verified

**Issue:** The API doc lists performance characteristics (e.g., "~10 μs/eval" for `evaluate()`) but these were not verified against actual benchmarks. These values may become stale or inaccurate over time.

**Recommendation:** Either:
1. Remove specific timing numbers and use relative comparisons only
2. Add a note that these are typical values and may vary by system

---

## Improvement Recommendations

| Priority | File:Line | Issue | Recommendation |
|----------|-----------|-------|----------------|
| Low | `__init__.py:96` | `get_default_evaluator` not in `__all__` | Add to `__all__` list |
| Low | `architecture/api.md:62` | Cache size doc says 1000, actual is 1024 | Update doc to 1024 |
| Medium | `architecture/api.md:51-52` | Timeout example won't timeout due to MAX_EXPONENT | Use different example or add note |
| Low | `__init__.py` | `load_user_config_extended` not exported | Export or document limitation |
| Low | `architecture/api.md:98-105` | Memory functions table could be clearer | Add return types column |

---

## Conclusion

The API documentation is generally accurate and well-structured. The core functionality documented is correctly implemented. The main issues are:

1. **Cache size mismatch** - documentation says 1000, code uses 1024
2. **Missing exports** - `get_default_evaluator` exported but not in `__all__`
3. **Misleading example** - timeout example would fail before timeout due to exponent limit
4. **Feature visibility** - `load_user_config_extended()` exists but isn't exposed

These are mostly documentation accuracy issues rather than bugs in the implementation.