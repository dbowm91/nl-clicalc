# Architecture Review Plan

This document outlines the review plan for architecture documentation in this directory.

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

## Subagent Assignments

Each subagent will review one module and write improvement plans to `plans/review_improvements_<modulename>.md`.

### Module Review Tasks

1. **normalize**: Review architecture/normalize.md against nl_calc/normalize.py. Verify all documented functions, data structures, and behaviors exist and work as documented.

2. **evaluator**: Review architecture/evaluator.md against nl_calc/evaluator.py. Verify AST-based evaluation logic, operator handling, and function implementations.

3. **units**: Review architecture/units.md against nl_calc/units.py. Verify unit definitions, conversion factors, and temperature conversion logic.

4. **primitives**: Review architecture/primitives.md and architecture/exact-primitives.md against nl_calc/exact/primitives.py. Verify UTF-8 handling, codepoint iteration, and Unicode normalization.

5. **unicode_tools**: Review architecture/unicode_tools.md and architecture/exact-unicode_tools.md against nl_calc/exact/unicode_tools.py. Verify script detection and confusable detection functions.

6. **confusables**: Review architecture/confusables.md against nl_calc/exact/confusables.py. Verify confusable character identification logic.

7. **validate**: Review architecture/validate.md against nl_calc/exact/validate.py. Verify JSON/bracket/regex validation implementations.

8. **diff**: Review architecture/diff.md against nl_calc/exact/diff.py. Verify string diffing algorithms and longest common subsequence implementation.

9. **measure**: Review architecture/measure.md against nl_calc/exact/measure.py. Verify text metrics (words, lines, categories) implementations.

10. **synthesis**: Review architecture/synthesis.md against nl_calc/exact/synthesis.py. Verify higher-level text analysis tools.

11. **cli**: Review architecture/cli.md against nl_calc/__main__.py. Verify CLI interface implementation.

12. **mcp**: Review architecture/mcp.md and architecture/mcp_server.md against nl_calc/mcp/. Verify MCP server implementation, tool definitions, and JSON schemas.

13. **api**: Review architecture/api.md. Verify documented API surface matches actual exports from modules.

14. **exact**: Review architecture/exact.md as overview of nl_calc/exact/ subpackage.

15. **overview**: Review architecture/overview.md as top-level architecture documentation.

## Output Files

Each subagent will write their improvement plan to:
- `plans/review_improvements_<modulename>.md`

Plans should include:
- Verified claims (with code references)
- Discrepancies between documentation and code
- Potential bugs identified
- Improvement suggestions with priority