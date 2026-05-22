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

**SuccessEnvelope is Defined but Unused:**
The `SuccessEnvelope` TypedDict in `schemas.py` is never imported or used in `tools.py`. Only `ErrorEnvelope` is used. Consider using consistently or removing.

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

### Implementation Notes from Architecture Review

**Potential Bugs to Fix (from 2026-05-22 review):**

1. **REPL History stores None on eval failure** - `normalize.py:1028-1029` should check `result is not None` before appending to history

2. **TypedDict `__slots__` invalid in measure.py** - `WordMetrics`, `LineMetrics`, `CharCategoryMetrics` have `__slots__` which has no effect on TypedDict. Remove `__slots__ = [...]` from these classes. Note: `BracketError` and `CheckBracketsResult` in validate.py DO have valid `__slots__`.

3. **Control chars counting incomplete** - `measure.py:242-247` only counts `Cc` category, should also count `Co` and `Cn` (excluding `Cf`).

4. **`__rsub__` in UnitValue** - `units.py:81-84` - When doing scalar minus UnitValue (e.g., `5 - UnitValue(3, 'ft')`), returns wrong result. Currently delegates to `UnitValue(other - self.value, self.unit)` which doesn't properly convert.

5. **`combine_number_parts()` logic error** - `normalize.py:493-537` produces incorrect results for inputs like "ten six" (10-19 range).

6. **`_handle_negative_token()` bounds** - `normalize.py` has potential out-of-bounds access on `tokens[index-2]` and `tokens[index-1]` without sufficient bounds checking.

7. **`_advance_past_sequence()` dead code** - `primitives.py:398-446` function is never called; duplicates functionality inline in `count_graphemes()`.

8. **BIDI control character handling** - `unicode_tools.py` has no explicit handling for BIDI control characters (U+202A-U+202E, U+2066-U+2069) - security concern for homograph attacks.

### Documentation Discrepancies to Fix

1. **TypedDict vs NamedTuple in arch docs** - Multiple `architecture/*.md` files show `@dataclass class Xxx(NamedTuple)` but code uses `class Xxx(TypedDict)`. Update all to match.

2. **Missing arch documentation** - Functions exist but undocumented:
   - `unicode_scripts()` in `unicode_tools.md`, `confusables.md`
   - `confusables_count()` in `confusables.md`
   - `longest_common_subsequence()` in `diff.md`

3. **DiffSpan field names** - Arch doc says `a_start/a_end/b_start/b_end` but actual is `a_span/b_span` (list[int]).

4. **`text_truncate` schema** - Missing output fields in `schemas.py:152-166`.

5. **Rankine temperature** - Exists in `UNIT_ALIASES` but not documented in `architecture/units.md`.