# Architecture Review Plan

This document outlines the review plan for architecture modules in this directory.

## Modules to Review

| Module | Reviewer Agent | Output File |
|--------|---------------|-------------|
| overview.md | overview-reviewer | plans/overview_review.md |
| normalize.md | normalize-reviewer | plans/normalize_review.md |
| evaluator.md | evaluator-reviewer | plans/evaluator_review.md |
| units.md | units-reviewer | plans/units_review.md |
| cli.md | cli-reviewer | plans/cli_review.md |
| api.md | api-reviewer | plans/api_review.md |
| exact.md | exact-reviewer | plans/exact_review.md |
| mcp_server.md | mcp_server-reviewer | plans/mcp_server_review.md |

## Review Instructions for Each Subagent

Each subagent must:

1. **Read the architecture document** assigned to them
2. **Verify claims** in the document against the actual codebase:
   - Cross-reference function names, class definitions, and modules
   - Check that documented behaviors match implementation
   - Identify any discrepancies or outdated information
3. **Interrogate the code** for:
   - **Improvements**: Code patterns, optimizations, better error handling, cleaner abstractions
   - **Bugs**: Edge cases, potential exceptions, race conditions, logic errors
   - **Security issues**: Input validation, injection vulnerabilities, data exposure
4. **Write an improvement plan** to the designated output file in `plans/` directory

## Review Focus Areas

- **Correctness**: Does the implementation match the documentation?
- **Completeness**: Are all documented features implemented?
- **Robustness**: Error handling, edge cases, boundary conditions
- **Maintainability**: Code clarity, documentation quality, test coverage
- **Performance**: Algorithmic efficiency, resource usage

## Execution

Subagents will be launched to review modules in parallel. Each will write findings to `plans/<module>_review.md`.