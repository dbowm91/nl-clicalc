# AGENTS.override.md

## Session-Specific Overrides and Extensions

This file contains overrides and additions specific to this codebase. Items here take precedence over AGENTS.md.

### Verified/Corrected Information

The following items have been verified against the codebase and should be considered accurate:

1. **`evaluate_cached` in `__all__`** - Already present at `evaluator.py:34`
2. **`get_default_evaluator` in `__all__`** - Already present at `__init__.py:96`
3. **`mps` is in UNIT_CATEGORIES** - Already present at `units.py:1206` as `"m/s": "speed"` and aliases map `"mps"` to `"m/s"` at line 953

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
- `difflib.SequenceMatcher` used for diff (not pure Levenshtein)
- Temperature-to-non-temperature conversions silently fall through (no warning)
- Redundant double length check in mcp/tools.py (lines 77-80)
- DEBUG flag in validate.py causes side effects (prints to stderr)

(End of file - 67 lines)