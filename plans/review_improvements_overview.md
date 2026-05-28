# normalize.py + overview.md Module Review — Improvement Plan

**Reviewed:** architecture/overview.md against nl_calc/normalize.py, evaluator.py, units.py  
**Date:** 2026-05-28

## Verified Claims (with line references)

- `run()`, `normalize()`, `normalize_expression()`, `main()`, `print_help()`, `NORMALIZE`, `PATTERNS` exported from normalize.py — VERIFIED at `__init__.py:57`
- `NUMBER_WORDS` dict in normalize.py — VERIFIED at normalize.py:220
- `OPERATOR_CONVERSIONS` dict in normalize.py — VERIFIED at normalize.py:101
- `FUNCTION_MAPPINGS` dict in normalize.py — VERIFIED at normalize.py:123
- `CONSTANT_WORDS` dict in normalize.py — VERIFIED at normalize.py:279
- `UNIT_BASE` dict in units.py — VERIFIED at units.py:168
- `UNIT_CONVERSIONS` dict in units.py — VERIFIED at units.py:620
- `UNIT_ALIASES` dict in units.py — VERIFIED at units.py:636
- `normalize_unit()` function in units.py — VERIFIED at units.py:1056
- `get_unit_category()` function in units.py — VERIFIED at units.py:1263
- `are_units_compatible()` function in units.py — VERIFIED at units.py:1269
- `UnitValue` class in units.py — VERIFIED at units.py:24
- `Memory` class in evaluator.py — VERIFIED at evaluator.py:680
- `TOOL_SCHEMAS` in mcp/schemas.py — VERIFIED at schemas.py:21
- Module dependency diagram in overview.md — VERIFIED by code inspection

## Discrepancies Between Documentation and Code

- [MEDIUM] `normalize_expression` return type documented incorrectly
  - Documentation says: `normalize_expression(expression: str) -> str` (api.md:130)
  - Code actually does: Returns `tuple[str, int]` (normalize_expression is a 2-tuple of (normalized_string, exit_code))
  - Impact: API consumers may incorrectly handle the return value, expecting just a string

- [LOW] `are_units_compatible` missing from Key exports for units.py
  - Documentation lists Key exports for units.py as: `UnitValue`, `get_conversion_factor()`, `is_unit()`, `get_unit_category()`, `get_all_units()` (overview.md:144)
  - Code actually has: `are_units_compatible` is also exported from units.py and used internally
  - Impact: Minor - the function is documented in the Key Data Structures table (overview.md:464) but not in Key exports

- [LOW] Performance timings in api.md are estimates, not measured values
  - Documentation claims: `evaluate()` ~10 μs/eval, `evaluate_cached()` ~0.1 μs/eval (api.md:195-197)
  - Code: No performance benchmarks exist in codebase
  - Impact: Timings may become outdated; suggests need for actual benchmark tests

## Potential Bugs

- [MEDIUM] Potential race condition in `Memory` class
  - Location: `evaluator.py:680-738`
  - Issue: The `Memory` class uses `threading.Lock()` for thread-safety, but `Evaluator.visit_Call()` at line 1199 uses `self.FUNCTIONS[name](*args)` which calls memory functions that also use locks. If the same `Evaluator` instance is shared across threads, nested calls could deadlock. However, the design of `PyCalcApp` uses isolated evaluator instances per app, mitigating this.
  - Suggested investigation: Review thread-safety guarantees when using `get_default_evaluator()` with memory functions from multiple threads

- [MEDIUM] `normalize_expression` not validated in `run()` for some exit codes
  - Location: `normalize.py:1153-1193`
  - Issue: `run()` calls `normalize_expression()` which returns `(normalized, exit_code)`. When `exit_code == 2`, it prints `joined` (which is actually the error message, not normalized expression) to stderr and returns `(None, 2)`. This is confusing naming but not a bug.
  - Suggested investigation: The `exit_code == 2` case prints the raw input expression, not the normalized form - could be confusing for debugging

## Improvement Suggestions

### HIGH Priority

- Update `normalize_expression` signature in api.md to reflect actual return type `tuple[str, int]`
  - Current: `normalize_expression(expression: str) -> str`
  - Should be: `normalize_expression(expression: str, operators: dict, patterns: Mapping[str, Pattern[str]], skip_validation: bool = False) -> tuple[str, int]`
  - Or document a simplified wrapper for basic usage

### MEDIUM Priority

- Add `are_units_compatible` to units.py Key exports list in overview.md
- Consider adding actual performance benchmarks to verify the ~10μs, ~155μs, ~0.1μs claims in api.md
- Clarify the `normalize_expression` function signature across documentation - it requires `operators` and `patterns` arguments which aren't documented

### LOW Priority

- The api.md example `normalize_expression("five plus three")  # "5+3"` doesn't show the required arguments
- Performance characteristics table (api.md:191-198) lists timings but these appear to be theoretical/hypothetical, not measured

## Summary

The overview.md architecture documentation is generally accurate and well-structured. The main issues are: (1) `normalize_expression` return type is documented as `str` but actually returns `tuple[str, int]`, and (2) `are_units_compatible` is missing from the units.py Key exports list despite being in the Key Data Structures table. The codebase structure, module dependencies, and data flow diagrams match the actual implementation.
