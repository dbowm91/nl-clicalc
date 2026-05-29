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
- `confusables.py` is an auto-generated data file (~176KB, 6580 lines) containing only the CONFUSABLES dict
- TypedDict classes are in their logical modules (validate.py, measure.py, unicode_tools.py, etc.), NOT in confusables.py
- Helper functions like `confusables_count()` should go in `unicode_tools.py`, not `confusables.py`
- `reverse_confusables()` is implemented, exported, and documented in architecture docs

**visible_repr() Check Order is Correct:**
The variation selector check (0xfe00-0xfe0f) comes BEFORE the combining mark check in `visible_repr()`. This is the correct order per AGENTS.md conventions. The code at primitives.py:273-276 is correct.

**Verified NOT Bugs:**
- `synthesis.py:337-338` - `accent_or_diacritic_difference` IS reachable (NFC-equal strings can be byte-different after casefocus when precomposed vs decomposed)
- `normalize.py:693` - `_handle_negative_token` has bounds checking + regex guard, no IndexError possible

**build_single.py Convention:**
- `normalize_main` alias is created by `build_single.py:236` during assembly, does not exist in source `normalize.py`

### Known Limitations

These are documented limitations that agents should be aware of:
- `notifications/cancel` and `notifications/progress` not implemented in MCP server
- `confusable_codepoint` field not in ConfusableInfo (only `confusable_with` character)
- `_is_extended_pictographic` name-based fallback includes 'SIGN' keyword which over-matches non-pictographic symbols like © ® ™ (acceptable for text detection purposes)
- Script detection uses heuristic range-based approach, not `unicodedata.script()`
- Temperature-to-non-temperature conversion now raises clear ValueError
- `_INVISIBLE_CHARS` contains 22 characters - documentation updated to list all
- Double-minus concatenation bug: "5 minus -2" → "52" instead of 3 (normalize.py:762-763)
- `unit_info()` MCP tool fails with NameError - calls non-existent `list_units()` function
- Scalar + dimensional arithmetic does not raise ValueError (e.g., `UnitValue(3,"m") + 5` returns `8 m`)

### New Bugs Identified (2026-05-29)

These bugs are documented in `plans/plan.md` and await implementation:
1. `units.py:66` - `__add__` scalar + dimensional: `UnitValue(3,"m") + 5` → `8 m` (should raise ValueError)
2. `units.py:81-84` - `__rsub__` scalar + dimensional: `5 - UnitValue(3,"m")` → `2 m` (should raise ValueError)
3. `normalize.py:762-763` - Double minus: `"5 minus -2"` → `"52"` (should be `5-(-2)` → `7`)
4. `mcp/tools.py:324` - `unit_info()` calls non-existent `list_units()` from units.py
5. `mcp/tools.py:839 and 1337` - Duplicate `_VALID_TRANSFORM_OPERATIONS` constant

### Previously Reported Issues (Now Fixed)

The following bugs were fixed in the plan implementation:
1. ~~Dead code in `list_compare()` near_matches~~ - FIXED
2. ~~Temperature-to-non-temperature conversion crash~~ - FIXED
3. ~~Float regex pipe bug~~ - FIXED

### Additional Verified NOT Bugs (2026-05-29)

These were investigated and confirmed not to be bugs:
- `get_unit_category` IS correctly imported in evaluator.py (line 27) - not a bug
- `__eq__` returning `NotImplemented` for different units is intentional for Python's comparison protocol
- Int regex patterns `[-|+]?` at normalize.py:367,369 allow `|` and `*` but these don't appear in practice (low practical impact)

### Session Learnings (2026-05-29)

**Plan Consolidation:**
- Consolidated 15 architecture review files into single `plans/plan.md`
- 40+ actionable items organized into 5 waves for parallel implementation
- Each wave can be worked on independently by different agents

**Parallelization Opportunities:**
- Wave 1 (4 high priority bugs): 3 parallel agents possible
- Wave 2 (5 medium bugs): 4 parallel agents possible
- Wave 3 (8 low bugs): 4 parallel agents possible
- Wave 4 (15 doc updates): 15 parallel agents possible
- Wave 5 (8 improvements): 8 parallel agents possible

**Verified During Review:**
- `get_unit_category` IS correctly imported in evaluator.py:27 (NOT a bug as claimed in evaluator_review)
- `list_units` is NOT exported from units.py - confirmed bug in mcp/tools.py:324
- `__eq__` for UnitValue with different units returns NotImplemented (could be improved to return False)

### Architecture Conventions

**TypedDict vs NamedTuple:**
- All architecture docs use `class Xxx(TypedDict)` correctly
- TypedDict is used throughout for consistency with Python 3.14+ typing patterns
- TypedDict classes do NOT support `__slots__` - only regular classes do

**ConfusableInfo fields:**
- Use `confusable_with` and `confusable_name`, not `confusable_for` or `confusable_codepoint`

**ScriptInfo fields:**
- Use `index`, `char`, `script`, `codepoint` (not `count`, `start`, `end`)

**detect_mixed_scripts return:**
- Returns MixedScriptsResult TypedDict with keys `mixed_scripts`, `scripts`, `positions`

**CommonPrefixSuffix fields:**
- Use `common_prefix_len`, `common_suffix_len` (not `prefix`, `suffix`)

**visible_repr() Check Order:**
- Variation selector check (0xfe00-0xfe0f) comes BEFORE combining mark check
- This is correct per Unicode display recommendations

**validate.py Input Limits:**
- `MAX_INPUT_LENGTH = 100_000` enforced in `check_brackets()` and `validate_json()`
- `MAX_SAMPLE_LENGTH = 10_000` enforced in `regex_test()`
- Functions raise `ValueError` when input exceeds the limit
- Consistent with MCP layer's `MAX_TEXT_LENGTH` constant