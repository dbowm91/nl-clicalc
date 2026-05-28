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

### Known Limitations

These are documented limitations that agents should be aware of:
- `notifications/cancel` and `notifications/progress` not implemented in MCP server
- `confusable_codepoint` field not in ConfusableInfo (only `confusable_with` character)
- `_is_extended_pictographic` range (0x1F300-0x10FFFF) is broad and includes private use areas
- Script detection uses heuristic range-based approach, not `unicodedata.script()`
- Temperature-to-non-temperature conversion (`units.py:146-164`) crashes after issuing warning

### Critical Bugs to Avoid

The following bugs exist in the codebase and should NOT be introduced in new code:
1. **synthesis.py:337-338** - Dead code branch in `_classify_difference()`: `"accent_or_diacritic_difference"` case is unreachable when `nfc_equal=True`
2. **synthesis.py:704-714** - Dead code in `list_compare()`: `"unicode_normalization_only"` near_match classification is unreachable through normal usage
3. **units.py:146-164** - Temperature-to-non-temperature conversion crashes after warning

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
- Returns dict with keys `mixed_scripts`, `scripts`, `positions` (not list[ScriptInfo])

**CommonPrefixSuffix fields:**
- Use `common_prefix_len`, `common_suffix_len` (not `prefix`, `suffix`)

**visible_repr() Check Order:**
- Variation selector check (0xfe00-0xfe0f) comes BEFORE combining mark check
- This is correct per Unicode display recommendations

**validate.py Input Limits:**
- `MAX_INPUT_LENGTH = 100_000` enforced in `check_brackets()` and `validate_json()`
- Functions raise `ValueError` when input exceeds the limit
- Consistent with MCP layer's `MAX_TEXT_LENGTH` constant