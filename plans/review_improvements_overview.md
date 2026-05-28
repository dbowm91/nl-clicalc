# overview + api Module Review — Improvement Plan

**Reviewed:** architecture/overview.md, architecture/api.md against nl_calc/*.py
**Date:** 2026-05-28

## Verified Claims (with line references)

| Claim | File | Verified | Notes |
|-------|------|----------|-------|
| Core modules exist at correct paths | overview.md | ✓ | normalize.py (1527 lines), evaluator.py (1516 lines), units.py (1295 lines), __main__.py (19 lines) |
| exact/ module structure (7 files + __init__) | overview.md | ✓ | All present: primitives.py (456), unicode_tools.py (293), measure.py (251), diff.py (246), validate.py (347), synthesis.py (727), confusables.py (~6580 lines) |
| mcp/ module structure | overview.md | ✓ | schemas.py (332), tools.py (424), server.py (239), __init__.py (13) |
| Key Data Structures locations | overview.md | ✓ | NUMBER_WORDS, OPERATOR_CONVERSIONS, FUNCTION_MAPPINGS in normalize.py; UNIT_BASE, UNIT_CONVERSIONS, UNIT_ALIASES in units.py |
| TOOL_SCHEMAS in mcp/schemas.py | overview.md | ✓ | Line 21-332 in schemas.py |
| Memory class in evaluator.py | overview.md | ✓ | Lines 680-738 |
| Build system files exist | overview.md | ✓ | build_single.py, install.py present |
| evaluate() signature | api.md | ✓ | evaluator.py:1305 - takes expression: str, returns Any |
| evaluate_raw() exists | api.md | ✓ | evaluator.py:1314 |
| evaluate_cached() with 1024 entries | api.md | ✓ | evaluator.py:138, DEFAULT_CACHE_SIZE = 1024 |
| evaluate_async() exists | api.md | ✓ | evaluator.py:153-165 |
| evaluate_with_timeout() exists | api.md | ✓ | evaluator.py:1346-1381 |
| PyCalcApp class | api.md | ✓ | evaluator.py:1396-1516 |
| register_constant() thread-safe | api.md | ✓ | evaluator.py:67-70 uses _lock |
| Memory functions (store/recall/add/subtract/clear) | api.md | ✓ | evaluator.py:745-772 |
| Variable functions (setvar/getvar/delvar/listvars/clearvars) | api.md | ✓ | evaluator.py:781-824 |
| normalize_expression() exists | api.md | ✓ | normalize.py:1105-1150 |
| UnitValue class | api.md | ✓ | units.py:24-165 |
| Security constants (MAX_EXPONENT=10000, MAX_FACTORIAL=1000, MAX_NESTING_DEPTH=100, MAX_RESULT_VALUE=1e308) | api.md | ✓ | evaluator.py:60-63 |

---

## Discrepancies Between Documentation and Code

### [HIGH] normalize_expression() return type mismatch
- **Documentation says:** `normalize_expression(expression: str) -> str` (api.md line 130)
- **Code actually does:** `normalize_expression(...) -> tuple[str, int]` (normalize.py:1110)
- **Impact:** API consumers will get a tuple (normalized_expression, exit_code), not just a string. This is a significant API mismatch.

### [HIGH] load_user_config_extended() completely undocumented
- **Documentation says:** Nothing about this function
- **Code actually does:** `load_user_config_extended()` exists (evaluator.py:168-187) for loading custom number/operator words via config
- **Impact:** Users cannot discover this capability from docs; `__init__.py` exports it but api.md does not mention it

### [HIGH] register_function() undocumented
- **Documentation says:** Nothing about register_function()
- **Code actually does:** `register_function(name: str, func: Any)` exists (evaluator.py:73-76)
- **Impact:** Users cannot discover how to register custom functions

### [HIGH] get_default_evaluator() undocumented
- **Documentation says:** Nothing about get_default_evaluator()
- **Code actually does:** `get_default_evaluator() -> Evaluator` exists (evaluator.py:1387-1393)
- **Impact:** Users cannot access the default evaluator instance from docs

### [MEDIUM] MAX_INPUT_LENGTH inconsistency
- **Documentation says:** `MAX_INPUT_LENGTH = 10000` (api.md line 164)
- **Code actually does:** normalize.py:42 defines MAX_INPUT_LENGTH = 10000, but validate.py:14 defines MAX_INPUT_LENGTH = 100_000
- **Impact:** Different limits apply depending on which module validates; the "Input Limits" section implies a single consistent value

### [MEDIUM] Variable functions return types incorrect
- **Documentation says:** setvar, getvar, delvar all return `dict[str, Any]`
- **Code actually does:** 
  - setvar returns `Any` (the value set) - evaluator.py:781-793
  - getvar returns `Any` (the value, default 0) - evaluator.py:796-806
  - delvar returns `None` - evaluator.py:809-812
  - listvars returns `dict[str, Any]` - evaluator.py:815-818 (correct)
  - clearvars returns `None` - evaluator.py:821-824 (correct)
- **Impact:** API consumers will have wrong type expectations

### [MEDIUM] normalize.py Key Exports incomplete
- **Documentation says:** `run()`, `normalize()`, `normalize_expression()`, `main()` (overview.md line 96)
- **Code actually does:** Also exports `NORMALIZE`, `PATTERNS`, `print_help`, `MAX_INPUT_LENGTH`, `MAX_NESTING_DEPTH` (normalize.py:57)
- **Impact:** Users cannot discover pattern constants from docs

---

## Potential Bugs

### [MEDIUM] Conflicting MAX_INPUT_LENGTH definitions
- **Location:** normalize.py:42 vs validate.py:14
- **Issue:** Two different values (10000 vs 100000) for the same constant name in different modules
- **Risk:** If code paths converge or developers assume consistency, bugs could result
- **Recommendation:** Consider renaming to avoid confusion (e.g., MAX_NORMALIZE_INPUT, MAX_VALIDATE_INPUT)

---

## Improvement Suggestions

### HIGH Priority

1. **Fix normalize_expression() return type documentation** (api.md line 130)
   - Change from `-> str` to `-> tuple[str, int]`
   - Document that it returns (normalized_expression, exit_code)

2. **Document load_user_config_extended()** (evaluator.py:168)
   - Add to Configuration Functions section in api.md
   - Note: "For advanced use; allows custom number/operator words"

3. **Document register_function()** (evaluator.py:73)
   - Add to Configuration Functions section
   - Already has proper docstring, just needs API docs

4. **Document get_default_evaluator()** (evaluator.py:1387)
   - Add to Configuration Functions section
   - "Returns the default Evaluator instance for advanced use"

### MEDIUM Priority

5. **Fix MAX_INPUT_LENGTH consistency** (api.md line 164)
   - Either document both values, or clarify which applies where
   - Consider if normalize.py should use validate.py's more generous limit

6. **Fix variable functions return types** (api.md lines 120-126)
   - setvar: `-> Any` (not dict)
   - getvar: `-> Any` (not dict)  
   - delvar: `-> None` (not dict)
   - listvars: `-> dict[str, Any]` (correct)
   - clearvars: `-> None` (correct)

7. **Add NORMALIZE and PATTERNS to normalize.py exports** (overview.md line 96)
   - These are critical for advanced usage

### LOW Priority

8. **Add Memory class to Key Data Structures** (overview.md line ~466)
   - Add `| Memory | evaluator.py | Calculator memory registers |`

9. **Add normalize_unit to Key Data Structures** (overview.md line ~464)
   - Add `| normalize_unit | units.py | Convert unit name to canonical form |`

---

## Summary

The architecture documentation (overview.md) is generally well-structured and accurate for the high-level architecture. The main issues are:

1. **Incomplete exports documentation** - Many functions in evaluator.py and normalize.py are not documented in api.md (evaluate_with_timeout, memory functions, variable functions, NORMALIZE/PATTERNS, etc.)

2. **Return type errors in api.md** - normalize_expression returns tuple not str, variable functions have wrong return types documented

3. **MAX_INPUT_LENGTH inconsistency** - Two different values in normalize.py vs validate.py causes confusion

4. **Missing advanced APIs** - load_user_config_extended, register_function, get_default_evaluator are functional but undocumented

The code itself appears sound with good error handling and consistent patterns. The issues are purely documentation-related, and fixing them would make the API much clearer for users.
