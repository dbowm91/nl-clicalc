# Architecture Review Plan

## Overview

This plan coordinates a comprehensive review of all architecture documents in this directory, excluding this file itself. Each module will be reviewed by a dedicated subagent that will:

1. Read the architecture document for the module
2. Verify claims against the actual source code
3. Identify potential bugs, improvements, and inconsistencies
4. Write an improvement plan to `plans/<module>_review.md`

## Modules to Review

| # | Module | Architecture Doc | Source Location | Review Output |
|---|--------|-----------------|-----------------|---------------|
| 1 | overview | [overview.md](overview.md) | N/A (overview only) | `plans/overview_review.md` |
| 2 | normalize | [normalize.md](normalize.md) | `nl_calc/normalize.py` | `plans/normalize_review.md` |
| 3 | evaluator | [evaluator.md](evaluator.md) | `nl_calc/evaluator.py` | `plans/evaluator_review.md` |
| 4 | units | [units.md](units.md) | `nl_calc/units.py` | `plans/units_review.md` |
| 5 | cli | [cli.md](cli.md) | `nl_calc/__main__.py` | `plans/cli_review.md` |
| 6 | primitives | [primitives.md](primitives.md) | `nl_calc/exact/primitives.py` | `plans/primitives_review.md` |
| 7 | unicode_tools | [unicode_tools.md](unicode_tools.md) | `nl_calc/exact/unicode_tools.py` | `plans/unicode_tools_review.md` |
| 8 | confusables | [confusables.md](confusables.md) | `nl_calc/exact/confusables.py` | `plans/confusables_review.md` |
| 9 | validate | [validate.md](validate.md) | `nl_calc/exact/validate.py` | `plans/validate_review.md` |
| 10 | diff | [diff.md](diff.md) | `nl_calc/exact/diff.py` | `plans/diff_review.md` |
| 11 | measure | [measure.md](measure.md) | `nl_calc/exact/measure.py` | `plans/measure_review.md` |
| 12 | synthesis | [synthesis.md](synthesis.md) | `nl_calc/exact/synthesis.py` | `plans/synthesis_review.md` |
| 13 | exact | [exact.md](exact.md) | `nl_calc/exact/` | `plans/exact_review.md` |
| 14 | mcp | [mcp.md](mcp.md) | `nl_calc/mcp/` | `plans/mcp_review.md` |
| 15 | mcp_server | [mcp_server.md](mcp_server.md) | `nl_calc/mcp/server.py` | `plans/mcp_server_review.md` |

## Subagent Instructions

Each subagent should perform the following for their designated module:

### Phase 1: Document Analysis
- Read the architecture document thoroughly
- Extract all claims about functionality, behavior, and implementation details
- Note any specific algorithms, data structures, or edge cases mentioned

### Phase 2: Code Verification
- Read the corresponding source code file(s)
- Cross-reference each claim in the architecture doc with the actual implementation
- Identify any discrepancies between documentation and code
- Verify that all documented features are actually implemented

### Phase 3: Bug and Improvement Identification
- Look for potential bugs (off-by-one errors, missing error handling, etc.)
- Identify improvement opportunities (performance, code clarity, edge cases)
- Check for security concerns (AST evaluation safety, input validation)
- Verify API consistency with other modules

### Phase 4: Write Improvement Plan
- Create a markdown file in `plans/` with the naming convention `plans/<module>_review.md`
- Structure the plan with sections:
  - **Verified Claims**: What the documentation correctly states
  - **Discrepancies**: Where documentation differs from implementation
  - **Bugs Found**: Actual bugs or issues in the code
  - **Improvements**: Suggested enhancements with rationale
  - **Priority**: High/Medium/Low for each item

## Execution

Launch subagents in parallel for all modules, then aggregate results.

## Verification Commands

After all reviews complete, run:
```bash
python3 -m pytest tests/
```