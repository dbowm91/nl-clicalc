# api.md Module Review — Improvement Plan

**Reviewed:** architecture/api.md against nl_calc/__init__.py, evaluator.py, units.py  
**Date:** 2026-05-28

## Verified Claims (with line references)

- `evaluate()` function exists and evaluates pre-normalized expressions — VERIFIED at evaluator.py:1305
- `evaluate_raw()` function exists for raw expressions — VERIFIED at evaluator.py:1314
- `evaluate_cached()` uses LRU cache with 1024 entries — VERIFIED at evaluator.py:64 (DEFAULT_CACHE_SIZE=1024) and evaluator.py:125-150
- `evaluate_async()` async version exists — VERIFIED at evaluator.py:153
- `evaluate_with_timeout()` with default timeout 5.0 — VERIFIED at evaluator.py:1346
- `PyCalcApp` class with cache_size parameter (default 1024) — VERIFIED at evaluator.py:1396, 1414
- `register_constant()` thread-safe function — VERIFIED at evaluator.py:67
- `register_function()` thread-safe function — VERIFIED at evaluator.py:73
- `get_default_evaluator()` returns Evaluator instance — VERIFIED at evaluator.py:1387
- `load_user_config()` loads from nl_calc_config.py — VERIFIED at evaluator.py:79
- Memory functions (memory_store, memory_recall, etc.) — VERIFIED at evaluator.py:745-772
- Variable functions (setvar, getvar, delvar, listvars, clearvars) — VERIFIED at evaluator.py:781-824
- `normalize_unit("kilometers")` returns "km" — VERIFIED at units.py:636 (maps "kilometers" to "km")
- `get_conversion_factor("ft", "m")` returns 0.3048 — VERIFIED at units.py:1100
- `is_unit("m")` returns True — VERIFIED at units.py:1115
- `get_unit_category("m")` returns "length" — VERIFIED at units.py:1263
- Security constants (MAX_EXPONENT=10000, MAX_FACTORIAL=1000, etc.) — VERIFIED at evaluator.py:60-64
- MAX_INPUT_LENGTH=10000 — VERIFIED at normalize.py:42
- MAX_NESTING_DEPTH=100 — VERIFIED at normalize.py:43 and evaluator.py:62
- `UnitValue` class with value and unit attributes — VERIFIED at units.py:24
- `EvaluationError` exception — VERIFIED at evaluator.py:674
- `TimeoutError` exception — VERIFIED at evaluator.py:1340
- `Memory` class — VERIFIED at evaluator.py:680

## Discrepancies Between Documentation and Code

- [HIGH] `normalize_expression` signature and return type incorrect
  - Documentation says: `normalize_expression(expression: str) -> str` (api.md:130)
  - Code actually does: `normalize_expression(expression: str, operators: dict, patterns: Mapping[str, Pattern[str]], skip_validation: bool = False) -> tuple[str, int]` at normalize.py:1105
  - Impact: API consumers will fail if they call it as documented; the function requires NORMALIZE and PATTERNS arguments and returns a tuple

- [HIGH] `PyCalcApp.calculate_async` example uses wrong syntax
  - Documentation says: `result = await app.calculate_async("five plus two")` (api.md:65)
  - Code actually does: `calculate_async` is an async method (evaluator.py:1457-1472), so the example is syntactically correct, but it should be noted that `calculate_async` is an instance method, not a class method
  - Impact: The example `app.calculate_async(...)` is correct but `PyCalcApp.calculate_async(...)` would be wrong

- [MEDIUM] `UnitValue` string representation includes decimal even for integers
  - Documentation shows: `print(f"{uv}")  # "5 m"` (api.md:174)
  - Code actually does: `__repr__` at units.py:35-38 returns `f"{self.value} {self.unit}"` which would produce `"5.0 m"` because float formatting
  - Impact: Documentation example shows `"5 m"` but actual output is `"5.0 m"`

- [MEDIUM] `evaluate_raw` documented but signature incomplete
  - Documentation says: `evaluate_raw(expression: str) -> Any` (api.md:19)
  - Code actually does: `_ensure_config_loaded()` then normalizes and evaluates (evaluator.py:1314-1337)
  - The example `evaluate_raw("five plus three")  # 8` is correct but simplified; actual call works
  - Impact: Minor - the function works as documented but the documentation doesn't mention it calls `normalize_expression` internally

- [MEDIUM] `load_user_config_extended` not exported but mentioned in __init__.py docstring
  - Documentation doesn't mention `load_user_config_extended()` at all
  - Code: `__init__.py:22-23` mentions "Note: load_user_config_extended() is not exported as custom number/operator words via external config are not officially supported"
  - The function exists at evaluator.py:168-187 but is not exported
  - Impact: No functional impact but could confuse users who see it in the codebase

- [LOW] Performance characteristics are estimates, not verified
  - Documentation shows specific timings: ~10 μs/eval, ~155 μs/eval, ~0.1 μs/eval (api.md:195-197)
  - Code: No benchmark code exists to verify these timings
  - Impact: Timings may be inaccurate; they appear to be documented expectations rather than measurements

- [LOW] `register_function` documentation says "call during init only"
  - Documentation says: "Register a custom function globally (thread-safe, call during init only)" (api.md:84)
  - Code actually does: No such restriction exists in evaluator.py:73-76
  - Impact: Misleading - the function can be called anytime, not just during init

## Potential Bugs

- [LOW] No bugs found in the API surface itself. The code is well-structured with proper exception handling and thread-safety mechanisms.

## Improvement Suggestions

### HIGH Priority

- Fix `normalize_expression` documentation:
  - Either document the full signature with required arguments, or
  - Document a simplified version that shows the typical calling pattern: `normalize_expression(expression, NORMALIZE, PATTERNS) -> tuple[str, int]`
  - Current documentation showing `normalize_expression("five plus three")  # "5+3"` is misleading

- Fix `UnitValue` example to show actual output:
  - Change `print(f"{uv}")  # "5 m"` to `print(f"{uv}")  # "5.0 m"`
  - Or add example showing `uv.value` returns `5.0`

### MEDIUM Priority

- Remove or correct the "call during init only" restriction from `register_function` documentation since the code doesn't enforce this
- Consider adding a note that performance timings in api.md:191-198 are estimates, or add actual benchmarks
- Document that `load_user_config_extended()` exists but is intentionally not exported

### LOW Priority

- Clarify that `evaluate_async` and `calculate_async` are instance methods, not class methods
- Add `are_units_compatible` to the utility functions table if it's intended to be part of the public API

## Summary

The api.md documentation provides a good overview of the public API surface, but has several inaccuracies: the `normalize_expression` function signature is documented incorrectly (returns tuple, not string, and requires arguments), the `UnitValue` string representation example shows incorrect output format, and some performance claims are undocumented estimates. The core evaluation functions (`evaluate`, `evaluate_raw`, `evaluate_cached`, `evaluate_async`, `evaluate_with_timeout`), memory functions, variable functions, and utility functions are all accurately documented and match the code implementation.
