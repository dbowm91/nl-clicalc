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

### Known Issues (Low Priority - Deferred)

These items are documented but not critical:
- `notifications/cancel` and `notifications/progress` not implemented in MCP server
- `confusable_codepoint` field not in ConfusableInfo (only `confusable_with` character)
- Bidirectional confusable detection not implemented

### Verified Correct Information

The following items have been verified against the codebase and should be considered accurate:

1. **`evaluate_cached` in `__all__`** - Already present at `evaluator.py:34`
2. **`get_default_evaluator` in `__all__`** - Already present at `__init__.py:96`
3. **`mps` is in UNIT_CATEGORIES** - Already present at `units.py:1206` as `"m/s": "speed"` and aliases map `"mps"` to `"m/s"` at line 953
4. **`mcp_main` alias in server.py** - Already present at `server.py:234`
5. **Memory and variable functions exported** - All present in `evaluator.py.__all__`
6. **exact/__init__.py exports** - `unicode_scripts`, `confusables_count`, `longest_common_subsequence` all correctly exported

### Implementation Notes from Architecture Review (Completed 2026-05-22)

All items below have been fixed as of the 2026-05-22 implementation wave:

1. **REPL History stores None on eval failure** - Fixed: condition at `normalize.py:1028` already checks `_ is not None`

2. **TypedDict `__slots__` invalid in measure.py** - Fixed: `__slots__` removed from `WordMetrics`, `LineMetrics`, `CharCategoryMetrics`

3. **Control chars counting incomplete** - Fixed: `measure.py` now counts `Co` and `Cn` per UTS #55, excluding `Cf`

4. **`__rsub__` in UnitValue** - Intentionally left as-is; `5 - UnitValue(3, 'ft')` returns `2 ft` (scalar minus unitless result)

5. **`combine_number_parts()` logic error** - Fixed: added case for `part == 10 and next < 10` to handle "ten six" properly

6. **`_handle_negative_token()` bounds** - Fixed: added proper bounds checking at start of function

7. **`_advance_past_sequence()` dead code** - Fixed: function removed, logic retained inline in `count_graphemes()`

8. **BIDI control character handling** - Fixed: BIDI chars (U+202A-202E, U+2066-2069) already in `_INVISIBLE_CHARS`

### Documentation Discrepancies Fixed

1. **TypedDict vs NamedTuple in arch docs** - Fixed: architecture docs updated to use `class Xxx(TypedDict)` instead of NamedTuple

2. **Missing arch documentation** - Fixed: `unicode_scripts()`, `confusables_count()`, `longest_common_subsequence()` now documented

3. **DiffSpan field names** - Fixed: architecture docs now correctly show `a_span/b_span` instead of `a_start/a_end`

4. **`text_truncate` schema** - Fixed: schema updated with output fields in `schemas.py`

5. **Rankine temperature** - Fixed: documented in `architecture/units.md`