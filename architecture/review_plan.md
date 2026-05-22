# Architecture Review Plan

**Status: COMPLETE** (2026-05-22)

All architecture modules have been reviewed and documentation discrepancies fixed.

## Review Summary

| Module | Review File | Status |
|--------|-------------|--------|
| normalize | plans/normalize_review.md | Completed |
| evaluator | plans/evaluator_review.md | Completed |
| units | plans/units_review.md | Completed |
| primitives | plans/primitives_review.md | Completed |
| unicode_tools | plans/unicode_tools_review.md | Completed |
| confusables | plans/confusables_review.md | Completed |
| validate | plans/validate_review.md | Completed |
| diff | plans/diff_review.md | Completed |
| measure | plans/measure_review.md | Completed |
| synthesis | plans/synthesis_review.md | Completed |
| cli | plans/cli_review.md | Completed |
| mcp | plans/mcp_server_review.md | Completed |
| api | plans/api_review.md | Completed |
| exact | plans/exact_review.md | Completed |
| overview | plans/overview_review.md | Completed |

## Key Fixes Applied

1. **CheckBracketsResult** - Documentation now matches code structure (unmatched_openers/closers)
2. **RegexTestResult** - Now documented with valid_pattern and results list
3. **RegexMatch** - Added proper TypedDict definition
4. **LineMetrics** - Now fully documented with all fields
5. **get_unit_category()** - Added to API documentation
6. **normalize_unit()** - Clarified as internal (not public API)

## Review Strategy

For each discrete architecture module:
1. Read the architecture documentation for the module
2. Locate and read the corresponding source code
3. Verify claims made in the documentation against the code
4. Interrogate the code for improvements and potential bugs
5. Write an improvement plan to `plans/review_improvements_<modulename>.md`

## Discrete Architecture Modules

| Module | Documentation | Source Files |
|--------|--------------|--------------|
| overview | architecture/overview.md | (top-level) |
| normalize | architecture/normalize.md | nl_calc/normalize.py |
| evaluator | architecture/evaluator.md | nl_calc/evaluator.py |
| units | architecture/units.md | nl_calc/units.py |
| primitives | architecture/primitives.md, architecture/exact-primitives.md | nl_calc/exact/primitives.py |
| unicode_tools | architecture/unicode_tools.md, architecture/exact-unicode_tools.md | nl_calc/exact/unicode_tools.py |
| confusables | architecture/confusables.md | nl_calc/exact/confusables.py |
| validate | architecture/validate.md | nl_calc/exact/validate.py |
| diff | architecture/diff.md | nl_calc/exact/diff.py |
| measure | architecture/measure.md | nl_calc/exact/measure.py |
| synthesis | architecture/synthesis.md | nl_calc/exact/synthesis.py |
| cli | architecture/cli.md | nl_calc/__main__.py |
| mcp | architecture/mcp.md, architecture/mcp_server.md | nl_calc/mcp/server.py, tools.py, schemas.py |
| api | architecture/api.md | (various) |
| exact | architecture/exact.md | nl_calc/exact/*.py |

## Review Plan Files

Each module review produced a detailed plan in `plans/<module>_review.md`:

- `plans/normalize_review.md` - Number word conversion, operators, functions
- `plans/evaluator_review.md` - AST evaluation, constants, memory
- `plans/units_review.md` - Unit definitions, conversions, temperature
- `plans/primitives_review.md` - UTF-8, codepoints, normalization
- `plans/unicode_tools_review.md` - Script detection, confusables
- `plans/confusables_review.md` - Homoglyph data
- `plans/validate_review.md` - Brackets, JSON, regex validation
- `plans/diff_review.md` - String comparison algorithms
- `plans/measure_review.md` - Text metrics
- `plans/synthesis_review.md` - Higher-level analysis tools
- `plans/cli_review.md` - CLI interface
- `plans/mcp_server_review.md` - MCP server implementation
- `plans/api_review.md` - Public API surface
- `plans/exact_review.md` - exact/ subpackage overview
- `plans/overview_review.md` - Top-level documentation

Plans include verified claims, discrepancies, bugs found, and improvement suggestions with priority.