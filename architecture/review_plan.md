# Architecture Review Plan

This document outlines a comprehensive review plan for the architecture documents in this directory. Each module will be reviewed by a dedicated subagent that will verify claims against the implementation code, identify bugs, and propose improvements.

## Modules to Review

1. **api.md** - API design and interfaces
2. **cli.md** - Command-line interface architecture
3. **confusables.md** - Confusable character handling
4. **diff.md** - Diff calculation and display
5. **evaluator.md** - Expression evaluation engine
6. **exact.md** - Exact arithmetic and fractions
7. **mcp_server.md** - MCP server implementation
8. **measure.md** - Measurement and unit handling
9. **normalize.md** - Text normalization
10. **overview.md** - Architecture overview
11. **primitives.md** - Primitive operations
12. **synthesis.md** - Synthesis engine
13. **unicode_tools.md** - Unicode utilities
14. **units.md** - Unit definitions and conversions
15. **validate.md** - Validation logic

## Review Process

Each subagent will:
1. Read the architecture document for their assigned module
2. Examine the corresponding source code in `nl_calc/`
3. Verify claims made in the document against actual implementation
4. Identify bugs, inconsistencies, or potential issues
5. Propose specific improvements with code references
6. Write the improvement plan to `plans/<module>_review.md`

## Subagent Assignments

### 1. API Module Reviewer
Task: Review `architecture/api.md` against implementation
Target: `nl_calc/` API interfaces
Output: `plans/api_review.md`

### 2. CLI Module Reviewer
Task: Review `architecture/cli.md` against implementation
Target: `nl_calc/__main__.py` and CLI handling
Output: `plans/cli_review.md`

### 3. Confusables Module Reviewer
Task: Review `architecture/confusables.md` against implementation
Target: Confusable character detection code
Output: `plans/confusables_review.md`

### 4. Diff Module Reviewer
Task: Review `architecture/diff.md` against implementation
Target: Diff calculation implementation
Output: `plans/diff_review.md`

### 5. Evaluator Module Reviewer
Task: Review `architecture/evaluator.md` against implementation
Target: `nl_calc/evaluator.py`
Output: `plans/evaluator_review.md`

### 6. Exact Module Reviewer
Task: Review `architecture/exact.md` against implementation
Target: Exact arithmetic implementation
Output: `plans/exact_review.md`

### 7. MCP Server Module Reviewer
Task: Review `architecture/mcp_server.md` against implementation
Target: MCP server implementation
Output: `plans/mcp_server_review.md`

### 8. Measure Module Reviewer
Task: Review `architecture/measure.md` against implementation
Target: Measurement handling code
Output: `plans/measure_review.md`

### 9. Normalize Module Reviewer
Task: Review `architecture/normalize.md` against implementation
Target: `nl_calc/normalize.py`
Output: `plans/normalize_review.md`

### 10. Overview Module Reviewer
Task: Review `architecture/overview.md` against implementation
Target: Cross-cutting architecture concerns
Output: `plans/overview_review.md`

### 11. Primitives Module Reviewer
Task: Review `architecture/primitives.md` against implementation
Target: Primitive operations implementation
Output: `plans/primitives_review.md`

### 12. Synthesis Module Reviewer
Task: Review `architecture/synthesis.md` against implementation
Target: Synthesis engine implementation
Output: `plans/synthesis_review.md`

### 13. Unicode Tools Module Reviewer
Task: Review `architecture/unicode_tools.md` against implementation
Target: Unicode utility functions
Output: `plans/unicode_tools_review.md`

### 14. Units Module Reviewer
Task: Review `architecture/units.md` against implementation
Target: `nl_calc/units.py`
Output: `plans/units_review.md`

### 15. Validate Module Reviewer
Task: Review `architecture/validate.md` against implementation
Target: Validation logic implementation
Output: `plans/validate_review.md`

## Review Focus Areas

For each module, reviewers should examine:

1. **Completeness**: Are all features described in the doc actually implemented?
2. **Correctness**: Do the implementation match the documented behavior?
3. **Consistency**: Are there contradictions between doc and code?
4. **Edge Cases**: Are there unhandled edge cases?
5. **Performance**: Any efficiency concerns?
6. **Security**: Potential security issues?
7. **Maintainability**: Code quality and organization issues?
8. **Test Coverage**: Are there adequate tests?

## Execution

Reviewers will be launched concurrently to maximize efficiency. Each reviewer will receive detailed instructions to:
- Read the architecture document fully
- Locate and examine relevant source code
- Cross-reference claims with actual implementation
- Document findings with specific file:line references
- Provide actionable improvement recommendations