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

### Critical Issues (Resolved)

The following issues have been fixed:
1. **`split_at_operators` whitespace handling** - Fixed by adding `_combine_consecutive_numbers()` in normalize.py
2. **`combine_number_parts()` logic** - Already working correctly (verification shows `['22']` for `[20, 2]`)
3. **TypedDict `__slots__` in validate.py** - Already removed from CheckBracketsResult, RegexTestResult
4. **`math_eval` response format inconsistency** - Already using `_success_response()` wrapper

### Low Priority Known Issues

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