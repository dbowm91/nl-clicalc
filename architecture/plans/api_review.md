# api.md Architecture Review

## Verified Claims

1. **evaluate()**: Function exists (evaluator.py line 811) - MATCHES
2. **evaluate_raw()**: Function exists (evaluator.py line 1219) - MATCHES
3. **evaluate_cached()**: Function exists (evaluator.py line 1296) - MATCHES
4. **evaluate_async()**: Function exists (evaluator.py line 1339) - MATCHES
5. **evaluate_with_timeout()**: Function exists (evaluator.py line 1255) - MATCHES
6. **PyCalcApp**: Class exists (evaluator.py line 1353) - MATCHES
7. **register_constant()**: Function exists (evaluator.py line 1159) - MATCHES
8. **register_function()**: Function exists (evaluator.py line 1176) - MATCHES
9. **load_user_config()**: Function exists (evaluator.py line 1134) - MATCHES
10. **memory_* functions**: All exist (evaluator.py lines 698-756) - MATCHES
11. **Variable functions**: setvar, getvar, delvar, listvars, clearvars - MATCHES
12. **UnitValue class**: Exists (units.py line 24) - MATCHES
13. **EvaluationError**: Exception class exists (evaluator.py line 76) - MATCHES
14. **TimeoutError**: Exception class exists (evaluator.py line 1297) - MATCHES
15. **Security constants**: MAX_EXPONENT=10000, MAX_FACTORIAL=1000, MAX_NESTING_DEPTH=100, MAX_RESULT_VALUE=1e308, DEFAULT_CACHE_SIZE=1024 - MATCHES

## Discrepancies

1. **normalize_unit() not in api.md**: 
   - Document says `normalize_unit("meters")  # "m"` is a utility function
   - But normalize_unit is NOT exported from nl_calc/__init__.py
   - The function exists (units.py:1051) but is not part of the public API

2. **get_unit_category() not in api.md**:
   - api.md shows `is_unit("m")  # True` but doesn't mention `get_unit_category()`
   - `get_unit_category()` exists (units.py:1276) and is exported but not documented

3. **normalize_expression() not in api.md**:
   - Not documented but is exported from __init__.py
   - This is the lower-level normalization function used by evaluate_raw internally

## Bugs Found

No bugs. API is internally consistent.

## Improvements

1. **Medium Priority**: Add `get_unit_category()` to the Utility Functions section
2. **Low Priority**: Note that `normalize_unit()` exists in units.py but is not part of the public API
3. **Low Priority**: Consider documenting `normalize_expression()` if it's intended for external use

## Priority

- **Medium**: Add get_unit_category() to documentation
- **Low**: Clarify which utility functions are part of public API vs internal