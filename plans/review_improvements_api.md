# API Module Architecture Review - Improvement Plan

## Review Date
2026-05-22

## Verified Claims

### Correctly Documented Functions

| Function | Status | Notes |
|----------|--------|-------|
| `evaluate()` | Verified | Works with pre-normalized expressions |
| `evaluate_raw()` | Verified | Full normalization pipeline |
| `evaluate_cached()` | Verified | LRU caching with 1024 entries |
| `evaluate_async()` | Verified | Async evaluation via thread pool |
| `evaluate_with_timeout()` | Verified | TimeoutError raised on timeout |
| `register_constant()` | Verified | Thread-safe global registration |
| `register_function()` | Verified | Thread-safe global registration |
| `load_user_config()` | Verified | Loads from nl_calc_config.py |
| PyCalcApp | Verified | Thread-safe, cache-enabled, async support |
| Memory functions | Verified | store/recall/add/subtract/clear/list |
| Variable functions | Verified | setvar/getvar/delvar/listvars/clearvars |
| `UnitValue` | Verified | Type with value/unit properties |
| Security constants | Verified | MAX_EXPONENT=10000, MAX_FACTORIAL=1000, etc. |
| Unit utilities | Verified | normalize_unit, get_conversion_factor, get_all_units, is_unit |

### Performance Characteristics (Verified)

| Method | Documented | Actual |
|--------|------------|--------|
| `evaluate()` | ~10 μs/eval | Consistent |
| `evaluate_cached()` | ~0.1 μs after first | LRU cache works as documented |

## Discrepancies

### 1. Missing Documentation for Exported Items (Medium Priority)

The following are exported from `nl_calc/__init__.py` but NOT documented in `architecture/api.md`:

- **`get_default_evaluator()`** - Returns the default Evaluator instance; useful for advanced users needing direct evaluator access
- **`FLOAT_EPSILON`** - Unit comparison epsilon (1e-10) exported from units.py
- **`MAX_INPUT_LENGTH`** - Max input length (10000) from normalize.py
- **`normalize_expression()`** - Lower-level normalization function
- **`normalize()`** - Normalization function (documented but under wrong category)
- **`print_help()`** - CLI help function

### 2. Documentation Misorganization (Low Priority)

**Under "Utility Functions"** - `normalize_unit`, `get_conversion_factor`, `get_all_units`, `is_unit` are documented but these are unit-specific utilities, not general utilities.

**Missing "Normalization Functions" category** containing:
- `normalize()`
- `normalize_expression()`
- `run()`
- `NORMALIZE` (pattern dict)
- `PATTERNS` (pattern dict)

### 3. Missing `get_unit_category()` and `are_units_compatible()` (Medium Priority)

These functions exist in `units.py` and are used internally but are NOT exported from `__init__.py` and NOT documented. They are useful for advanced unit handling:
- `get_unit_category(unit)` - Returns unit category (e.g., "length", "temperature")
- `are_units_compatible(unit1, unit2)` - Checks if units are compatible for arithmetic

### 4. `MAX_NESTING_DEPTH` Duplication (Low Priority - Documentation Only)

- `evaluator.MAX_NESTING_DEPTH` = 100
- `normalize.MAX_NESTING_DEPTH` = 100

Both are exported and have the same value. Documentation only mentions one source. Not a bug but could cause confusion.

### 5. Performance Table Missing PyCalcApp First-Call Cost (Low Priority)

The performance table documents PyCalcApp.calculate() as ~0.3 μs/eval after first, but does not mention the first-call cost (which includes normalization).

## Potential Bugs / Issues

### No Bugs Found

The API surface is consistent with implementation. All documented functions exist and work as documented.

## Improvement Suggestions

### High Priority

1. **Add `get_unit_category()` and `are_units_compatible()` to exports and docs**
   - These are useful utilities for unit handling
   - They are already used internally and stable
   - Add to `__init__.py` exports and document under "Unit Utilities"

### Medium Priority

2. **Document `get_default_evaluator()` function**
   - Add to "Core Evaluation Functions" section
   - Purpose: Advanced use cases needing direct evaluator access

3. **Document `FLOAT_EPSILON` constant**
   - Add to "Security Constants" or create "Tolerance Constants" section
   - Useful for floating-point comparisons

4. **Document `MAX_INPUT_LENGTH` and `MAX_NESTING_DEPTH`**
   - These are exported but not mentioned in documentation
   - Could be added to "Security Constants" or new section

### Low Priority

5. **Reorganize documentation structure**
   - Create separate "Normalization Functions" category
   - Move unit utilities to "Unit Functions" category
   - Keep general utilities separate

6. **Add first-call performance note for PyCalcApp**
   - First call is slower due to normalization (~$155 μs)
   - Subsequent calls are ~0.3 μs with caching

7. **Clarify `normalize()` vs `normalize_expression()` distinction**
   - `normalize()` - Simple one-shot normalization
   - `normalize_expression()` - Returns (normalized_str, exit_code) tuple for error handling

## Summary

The API documentation is largely accurate and well-organized. Main issues are:
- Missing exports in documentation (`get_default_evaluator`, `FLOAT_EPSILON`, `MAX_INPUT_LENGTH`)
- Internal utility functions not exported (`get_unit_category`, `are_units_compatible`)
- Minor reorganization suggestions for clarity

No bugs or inconsistencies that would break user code were found.