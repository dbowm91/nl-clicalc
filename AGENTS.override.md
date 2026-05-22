# AGENTS.override.md

## Session-Specific Overrides and Extensions

This file contains overrides and additions specific to this planning/consolidation session. Items here take precedence over AGENTS.md for this codebase.

### Corrected/Resolved Items

The following items from AGENTS.md Known Issues are now **RESOLVED** and should not be worked on:

- ~~**evaluate_cached not in __all__**~~ - Already present in `__all__` at `evaluator.py:34`

### Key Fixes Needed (from Consolidated Plan)

See `plans/plan.md` for the full consolidated implementation plan. Critical items:

1. **Wave 1 (Critical Bugs)** - Fix these first sequentially:
   - UNIT_ALIASES bug (kN, mV, mA mapping to base units)
   - Temperature F→C offset precision
   - Newline detection bug in measure.py
   - RegexTestResult missing `error` field
   - CLI --mcp flag missing from normalize.py
   - visible_repr() variation selector display order
   - visible_repr() missing WORD JOINER (U+2060)
   - mps missing from UNIT_CATEGORIES

2. **Wave 2 (High Priority)** - Can parallelize with Wave 1:
   - MCP double-wrapped response structure
   - MCP math_eval missing MAX_TEXT_LENGTH
   - utf8_bytes return type ambiguity
   - invisibles_detected always False in synthesis.py
   - Unit conversion space-separated detection bug

### Architecture Notes for exact/ Module

When working on exact/ module fixes:

- `primitives.py:utf8_bytes()` - Returns `bytes` object, not int
- `primitives.py:visible_repr()` - VS checks must come BEFORE combining mark checks
- `unicode_tools.py:_get_script_heuristic()` - Needs `@lru_cache` decorator
- `measure.py:newline_style()` - `mixed` detection logic at lines 45-62 is broken

### MCP Server Issues

When working on MCP server:

- `server.py` uses non-prefixed tool names (e.g., `math_eval`)
- `schemas.py` has prefixed names (`nl_calculate`) but TOOL_SCHEMAS is **dead code**
- `tools.py:math_eval` lacks `MAX_TEXT_LENGTH` enforcement
- Error messages not sanitized for non-ASCII characters

### Documentation Bugs to Fix

Many documentation files reference wrong field names or outdated info:

- `architecture/diff.md`: `a_context`/`b_context` should be `a_codepoint`/`b_codepoint`
- `docs/exact.md`: confusables return format shows codepoint instead of character
- `docs/exact.md`: "~1800 entries" should be "~6500 entries"
- `architecture/unicode_tools.md`: detect_confusables example shows 2 confusables, only 1 exists
- `architecture/unicode_tools.md`: detect_mixed_scripts example incomplete

### API Usage Reminder

For testing NL/unit features:
- Use `run()` or CLI, NOT `evaluate()`
- `evaluate()` only works with valid Python syntax

For pure math:
- Use `evaluate()`
- Results may be `UnitValue` - extract with `.value`
