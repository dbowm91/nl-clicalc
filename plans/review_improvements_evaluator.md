# evaluator Module Review — Improvement Plan

**Reviewed:** architecture/evaluator.md against nl_calc/evaluator.py
**Date:** 2026-05-28

## Verified Claims (with line references)
- Security architecture using AST (not eval) — VERIFIED at code line 1283 (docs line 45)
- Forbidden node types (Compare, BoolOp, Subscript, etc.) — VERIFIED at code lines 1252-1272 (docs lines 69-75)
- `evaluate()` signature — VERIFIED at code line 1305 (docs line 217)
- `evaluate_raw()` applies NL normalization — VERIFIED at code line 1332 (docs line 227)
- `evaluate_cached()` uses LRU cache — VERIFIED at code lines 125-150 (docs line 234)
- `evaluate_async()` uses thread executor — VERIFIED at code lines 153-165 (docs line 237)
- `evaluate_with_timeout()` timeout parameter — VERIFIED at code line 1346 (docs line 240)
- TimeoutError exception class — VERIFIED at code line 1340 (docs line 23)
- Memory functions (store/recall/add/subtract/clear/list) — VERIFIED at code lines 745-772 (docs lines 172-189)
- Variable functions (setvar/getvar/delvar/listvars/clearvars) — VERIFIED at code lines 781-824 (docs lines 191-203)
- MAX_EXPONENT=10000, MAX_FACTORIAL=1000, MAX_NESTING_DEPTH=100, MAX_RESULT_VALUE=1e308 — VERIFIED at code lines 60-63 (docs lines 207-213)
- `_complex_aware()` wrapper for complex number handling — VERIFIED at code lines 623-671 (docs lines 244-255)
- UnitValue handling in evaluate — VERIFIED at code lines 1294-1295, 1100-1118 (docs lines 268-280)

## Discrepancies Between Documentation and Code

### HIGH Priority

1. **Constants `g` and `standardgravity` missing from code**
   - Documentation says: `g` / `standardgravity` = 9.80665 exists (docs line 154-155)
   - Code actually does: NOT in CONSTANTS dict (code lines 836-902)
   - Impact: Users cannot use `g` or `standardgravity` in expressions

2. **Constants `wien` and `wienconstant` missing from code**
   - Documentation says: `wien` / `wienconstant` = 2.897771955e-3 exists (docs lines 169-170)
   - Code actually does: NOT in CONSTANTS dict (code lines 836-902)
   - Impact: Users cannot use `wien` or `wienconstant` in expressions

### MEDIUM Priority

3. **`load_user_config_extended()` not documented**
   - Documentation says: Only `load_user_config()` exists (docs line 28)
   - Code actually does: `load_user_config_extended()` exists at code lines 168-187 for custom number/operator words
   - Impact: Feature is hidden from users

4. **`evaluate_with_timeout` docstring example uses forbidden syntax**
   - Documentation says: Example uses `sum(i**2 for i in range(10000))` (docs line 1368)
   - Code actually does: Generator expressions (`ast.GeneratorExp`) are explicitly forbidden (code line 1261)
   - Impact: Documentation example would fail if executed

5. **PyCalcApp constructor docs mismatch**
   - Documentation says: `cache_size=1024` (docs line 264)
   - Code actually does: `DEFAULT_CACHE_SIZE = 1024` is default, but `enable_cache` parameter also exists (code lines 1412-1427)
   - Impact: Minor — docs don't mention `enable_cache` parameter

### LOW Priority

6. **Duplicate `G` entry in constants table**
   - Documentation says: `G` / `gravitationalconstant` appears at both line 155 and line 161
   - Code actually does: Only one entry in CONSTANTS (code line 878)
   - Impact: No functional impact, just documentation clutter

7. **`Evaluator` class not in Key Exports**
   - Documentation says: Lists all exports but omits `Evaluator` (docs lines 15-35)
   - Code actually does: `Evaluator` is in `__all__` (code line 31) and imported by `PyCalcApp`
   - Impact: Class is public but undocumented

8. **Many constants in code not documented**
   - Code has undocumented constants: `u`/`amu`/`atomicmassunit`, `epsilon0`/`vacuumpermittivity`, `mu0`/`vacuumpermeability`, `rydberg`/`rydbergconstant`, `stefan`/`stefanboltzmann`, `planckbar`/`hbar`/`reducedplanck`, `me`/`electronmass`, `mp`/`protonmass`, `mn`/`neutronmass`, `re`/`electronradius`, `alpha`/`finestructure`
   - Impact: Users don't know these constants exist

9. **Many functions in code not documented**
   - Code has undocumented functions: `is_prime`, `conjugate` (alias of `conj`), `nPr` (alias of `perm`), `nCr` (alias of `comb`), `var`/`vars`/`var_sample` (aliases of variance functions), `log1p`, `expm1`, `degrees`, `radians`, `floor`, `ceil`, `trunc`, `randrange`, `uniform`, `M`, `Mplus`, `Mminus`, `MC`, `MR`
   - Impact: Users don't know these functions exist

## Potential Bugs

### MEDIUM Priority

1. **`_sqrt` with complex `cmath.sqrt` may produce unexpected results for floats**
   - Location: `evaluator.py:654`
   - Issue: `_sqrt = _complex_aware(math.sqrt, cmath.sqrt, use_complex_for_negative=True)` — When `use_complex_for_negative=True` and a negative float is passed, it delegates to `cmath.sqrt` which returns a complex number. This changes the return type from `float` to `complex`, which may cause issues in downstream operations.
   - Suggested investigation: Verify all callers of `_sqrt` can handle complex return types

2. **Generator expression example in docs contradicts validator**
   - Location: `evaluator.py:1261` (forbidden) vs `evaluator.py:1368` (doc example)
   - Issue: `ast.GeneratorExp` is explicitly forbidden, but the `evaluate_with_timeout` docstring shows `sum(i**2 for i in range(10000))` as an example. This example would raise `EvaluationError`.
   - Suggested investigation: Remove or fix the example in the docstring

### LOW Priority

3. **`_perm` function returns 0 for invalid input without error**
   - Location: `evaluator.py:425-433`
   - Issue: When `r > n`, `_perm` returns 0 silently rather than raising an error. This may be confusing since `math.perm` raises ValueError for invalid inputs.
   - Suggested investigation: Consider whether to raise an error for consistency with `math.perm`

4. **`memory_store` returns float but doesn't match docstring**
   - Location: `evaluator.py:745-747`
   - Issue: `memory_store` docstring says "Store value in memory register" but doesn't specify the return type. Code returns `float` from `_memory.store()`.
   - Suggested investigation: Add return type annotation and update docstring

## Improvement Suggestions

### HIGH Priority
- Add `g` / `standardgravity` (9.80665) to CONSTANTS dict
- Add `wien` / `wienconstant` (2.897771955e-3) to CONSTANTS dict
- Fix `evaluate_with_timeout` docstring example — remove or change generator expression example

### MEDIUM Priority
- Document `load_user_config_extended()` in Key Exports or remove from code if not intended for external use
- Add `enable_cache` parameter to PyCalcApp documentation
- Add `Evaluator` class to Key Exports section

### LOW Priority
- Remove duplicate `G` entry from constants table (docs line 161)
- Add undocumented constants to the constants table: `u`/`amu`, `epsilon0`, `mu0`, `rydberg`, `stefan`, `planckbar`/`hbar`, `me`, `mp`, `mn`, `re`, `alpha`
- Add undocumented functions to the functions tables: `is_prime`, `conjugate`, `nPr`, `nCr`, `var`, `vars`, `var_sample`, `log1p`, `expm1`, `degrees`, `radians`, `floor`, `ceil`, `trunc`, `randrange`, `uniform`, memory shortcuts (`M`, `Mplus`, etc.)
- Add return type annotations to module-level functions lacking them

## Summary
The evaluator.md documentation is mostly accurate for the core evaluation functions, AST security model, and memory/variable systems. However, there are two HIGH-priority discrepancies: `g`/`standardgravity` and `wien`/`wienconstant` are documented but missing from the actual code. Additionally, the `evaluate_with_timeout` docstring contains an example that uses forbidden syntax (generator expressions), which would fail if executed. Several constants and functions exist in code but are not documented, limiting user awareness of available features.
