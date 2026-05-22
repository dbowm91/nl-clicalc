# AGENTS.override.md

## Session-Specific Overrides and Extensions

This file contains overrides and additions specific to this codebase. Items here take precedence over AGENTS.md.

### Important Implementation Notes

**Build Single File Convention:**
The codebase must work when assembled by `build_single.py` into a single file. All code must be in one of the four core modules: `normalize.py`, `evaluator.py`, `units.py`, or `__main__.py`.

**Key Architectural Distinctions:**
- `run()` handles natural language AND unit conversions (normalizes first)
- `evaluate()` handles only valid Python syntax (no normalization)
- When testing NL or unit features, use `run()` or CLI, NOT `evaluate()`

**Unit Aliases Behavior:**
Prefixed units like `kN`, `mV`, `mA` map to themselves in `UNIT_ALIASES`. Word forms like `kilonewton` alias to the prefixed form (e.g., `"kilonewton": "kN"`). This is correct behavior - the word form converts to the symbol form which then properly converts.

**exact/ Module File Organization:**
- `confusables.py` is an auto-generated data file (~180KB, 6581 lines) containing only the CONFUSABLES dict
- TypedDict classes are in their logical modules (validate.py, measure.py, unicode_tools.py, etc.), NOT in confusables.py
- Helper functions like `confusables_count()` should go in `unicode_tools.py`, not `confusables.py`

**visible_repr() Check Order is Correct:**
The variation selector check (0xfe00-0xfe0f) comes BEFORE the combining mark check in `visible_repr()`. This is the correct order per AGENTS.md conventions. The code at primitives.py:273-276 is correct.

### Critical Issues (Require Fix Before Release)

1. **`split_at_operators` whitespace handling** - `nl_calc/normalize.py:703-742`
   - Symptom: `run("what's five plus three hundred twenty two?")` returns `(3100207, 0)` instead of `(327, 0)`
   - Multi-word numbers like "three hundred twenty two" are not properly combined

2. **`combine_number_parts()` logic** - `nl_calc/normalize.py:493-530`
   - Symptom: `combine_number_parts([20, 2])` returns `['20', '+2']` instead of `['22']`
   - Does not properly combine number parts into single values

3. **TypedDict `__slots__` in validate.py** - `nl_calc/exact/validate.py:26, 36, 60`
   - `CheckBracketsResult`, `RegexTestResult` are TypedDicts and should NOT have `__slots__`
   - `BracketError` is a regular class and CAN have `__slots__`

4. **`math_eval` response format inconsistency** - `nl_calc/mcp/tools.py:89`
   - Returns raw dict `{"result": ..., "type": ...}` instead of using `_success_response()` wrapper

### Verified Correct Information

The following items have been verified against the codebase and should be considered accurate:

1. **`evaluate_cached` in `__all__`** - Already present at `evaluator.py:34`
2. **`get_default_evaluator` in `__all__`** - Already present at `__init__.py:96`
3. **`mps` is in UNIT_CATEGORIES** - Already present at `units.py:1206` as `"m/s": "speed"` and aliases map `"mps"` to `"m/s"` at line 953
4. **`mcp_main` alias in server.py** - Already present at `server.py:234`
5. **Memory and variable functions exported** - All present in `evaluator.py.__all__`
6. **exact/__init__.py exports** - `unicode_scripts`, `confusables_count`, `longest_common_subsequence` all correctly exported
7. **acre in UNIT_ALIASES** - "acre" and "acres" are present at `units.py:1015-1016`

### Known Issues (Low Priority - Deferred)

These items are documented but not critical:
- `notifications/cancel` and `notifications/progress` not implemented in MCP server
- `confusable_codepoint` field not in ConfusableInfo (only `confusable_with` character)
- Bidirectional confusable detection not implemented
- `_is_extended_pictographic` range (0x1F300-0x10FFFF) is broad and includes private use areas
- Script detection uses heuristic range-based approach, not `unicodedata.script()`

### Documentation Notes

1. **TypedDict vs NamedTuple** - All architecture docs use `class Xxx(TypedDict)` correctly
2. **ConfusableInfo fields** - Use `confusable_with` and `confusable_name`, not `confusable_for` or `confusable_codepoint`
3. **ScriptInfo fields** - Use `index`, `char`, `script`, `codepoint` (not `count`, `start`, `end`)
4. **detect_mixed_scripts return** - Returns dict with keys `mixed_scripts`, `scripts`, `positions` (not list[ScriptInfo])
5. **CommonPrefixSuffix fields** - Use `common_prefix_len`, `common_suffix_len` (not `prefix`, `suffix`)