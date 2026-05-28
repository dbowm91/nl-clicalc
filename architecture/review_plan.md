# Architecture Review Plan

**Created:** 2026-05-28  
**Status:** READY FOR EXECUTION

Systematic review of all architecture documentation against the nl-clicalc codebase. Uses subagents to review discrete modules in parallel, with each producing an improvement plan.

---

## Purpose

This plan orchestrates a deep, evidence-based review of every architecture document in `architecture/`. The goal is NOT to make direct code changes, but to produce a prioritized improvement plan for each module that a future agent can execute. Each subagent is assigned a discrete module, verifies documentation claims against source code, interrogates for bugs and improvements, and writes findings to `plans/review_improvements_<module>.md`.

---

## Review Process

### Phase 1: Parallel Module Reviews (Subagents)

Each subagent receives:
- Architecture document(s) to review (from `architecture/`)
- Corresponding source file(s) to verify claims against
- A checklist of things to verify
- Output file path in `plans/` directory

**Subagent Instructions:**
1. Read the assigned architecture document(s) completely
2. Read the corresponding source code file(s) in `nl_calc/`
3. For each claim in the documentation:
   - Verify the claim matches the code (function names, signatures, line numbers, behavior)
   - Note discrepancies where documentation says X but code does Y
   - Note undocumented features where code has X but docs don't mention it
4. Interrogate the code:
   - Look for potential bugs (edge cases, error handling, type issues, unsafe patterns)
   - Look for inconsistencies (naming, patterns, return types across modules)
   - Look for missing tests or documentation gaps
5. Write improvement plan to `plans/review_improvements_<module>.md`

### Phase 2: Stale Item Identification

After all module reviews complete, a designated subagent performs a stale item scan:
- Architecture documents that reference removed/renamed functions
- Documentation for features not implemented in code
- Module files that have been superseded or are no longer relevant
- Duplicate documentation across files
- Line number references that are stale due to code changes
- Outdated examples in docs that wouldn't work with current API

Findings written to `plans/review_stale_items.md`.

### Phase 3: Consolidation

After all reviews complete, this file is updated with:
- Summary of findings across all modules
- Final status for each module review
- Top-priority items across the entire codebase

---

## Discrete Architecture Modules

Each row defines a review unit: the doc(s), the source files, and the output plan.

| # | Module | Documentation | Source Files | Output Plan |
|---|--------|--------------|--------------|-------------|
| 1 | overview | `architecture/overview.md` | (cross-cutting) | `plans/review_improvements_overview.md` |
| 2 | normalize | `architecture/normalize.md` | `nl_calc/normalize.py` | `plans/review_improvements_normalize.md` |
| 3 | evaluator | `architecture/evaluator.md` | `nl_calc/evaluator.py` | `plans/review_improvements_evaluator.md` |
| 4 | units | `architecture/units.md` | `nl_calc/units.py` | `plans/review_improvements_units.md` |
| 5 | primitives | `architecture/primitives.md` | `nl_calc/exact/primitives.py` | `plans/review_improvements_primitives.md` |
| 6 | unicode_tools | `architecture/unicode_tools.md` | `nl_calc/exact/unicode_tools.py` | `plans/review_improvements_unicode_tools.md` |
| 7 | confusables | `architecture/confusables.md` | `nl_calc/exact/confusables.py` | `plans/review_improvements_confusables.md` |
| 8 | validate | `architecture/validate.md` | `nl_calc/exact/validate.py` | `plans/review_improvements_validate.md` |
| 9 | diff | `architecture/diff.md` | `nl_calc/exact/diff.py` | `plans/review_improvements_diff.md` |
| 10 | measure | `architecture/measure.md` | `nl_calc/exact/measure.py` | `plans/review_improvements_measure.md` |
| 11 | synthesis | `architecture/synthesis.md` | `nl_calc/exact/synthesis.py` | `plans/review_improvements_synthesis.md` |
| 12 | cli | `architecture/cli.md` | `nl_calc/__main__.py` | `plans/review_improvements_cli.md` |
| 13 | mcp | `architecture/mcp.md` | `nl_calc/mcp/server.py`, `tools.py`, `schemas.py` | `plans/review_improvements_mcp.md` |
| 14 | api | `architecture/api.md` | (various — cross-cutting) | `plans/review_improvements_api.md` |
| 15 | exact | `architecture/exact.md` | `nl_calc/exact/__init__.py`, `nl_calc/exact/*.py` | `plans/review_improvements_exact.md` |

---

## Subagent Dispatch Plan

Subagents are dispatched in batches. Each subagent operates independently and writes its own output file.

### Batch 1: Core Modules (3 subagents)

- **Subagent A**: overview + api
  - `architecture/overview.md`, `architecture/api.md`
  - Cross-cutting review: verify overview claims against all modules, verify API doc against actual exports
  - Output: `plans/review_improvements_overview.md`, `plans/review_improvements_api.md`

- **Subagent B**: normalize + evaluator
  - `architecture/normalize.md`, `architecture/evaluator.md`
  - Verify NL processing pipeline claims, AST evaluation claims, function signatures
  - Output: `plans/review_improvements_normalize.md`, `plans/review_improvements_evaluator.md`

- **Subagent C**: units
  - `architecture/units.md`
  - Verify unit definitions, conversion factors, temperature handling, UnitValue class
  - Output: `plans/review_improvements_units.md`

### Batch 2: exact/ Primitives (3 subagents)

- **Subagent D**: primitives
  - `architecture/primitives.md`
  - Verify UTF-8, codepoint, normalization, invisible detection claims
  - Output: `plans/review_improvements_primitives.md`

- **Subagent E**: unicode_tools
  - `architecture/unicode_tools.md`
  - Verify script detection, confusable detection claims
  - Output: `plans/review_improvements_unicode_tools.md`

- **Subagent F**: confusables
  - `architecture/confusables.md`
  - Verify data file structure, generation claims, integration points
  - Output: `plans/review_improvements_confusables.md`

### Batch 3: exact/ Analysis (4 subagents)

- **Subagent G**: validate
  - `architecture/validate.md`
  - Verify bracket, JSON, regex validation claims
  - Output: `plans/review_improvements_validate.md`

- **Subagent H**: diff
  - `architecture/diff.md`
  - Verify diff algorithms, LCS implementation, Levenshtein claims
  - Output: `plans/review_improvements_diff.md`

- **Subagent I**: measure
  - `architecture/measure.md`
  - Verify text metrics, line metrics, word metrics claims
  - Output: `plans/review_improvements_measure.md`

- **Subagent J**: synthesis
  - `architecture/synthesis.md`
  - Verify higher-level analysis claims, integration with other exact/ modules
  - Output: `plans/review_improvements_synthesis.md`

### Batch 4: Interface & Integration (3 subagents)

- **Subagent K**: cli
  - `architecture/cli.md`
  - Verify CLI argument handling, interactive mode, output formatting
  - Output: `plans/review_improvements_cli.md`

- **Subagent L**: mcp
  - `architecture/mcp.md`
  - Verify MCP server protocol, tool definitions, error handling
  - Output: `plans/review_improvements_mcp.md`

- **Subagent M**: exact (subpackage overview)
  - `architecture/exact.md`
  - Verify __init__.py exports, module interconnections, public API surface
  - Output: `plans/review_improvements_exact.md`

### Phase 2 Subagent: Stale Item Scanner

- **Subagent N**: Stale item identification
  - Scans all architecture docs against current codebase
  - Checks for dead references, unimplemented features, superseded docs
  - Output: `plans/review_stale_items.md`

---

## Review Checklist (Per Module)

Each subagent must address every item in this checklist:

### Documentation Accuracy
- [ ] Documentation exists for all public functions/classes
- [ ] Function signatures match between docs and code (parameter names, types, defaults)
- [ ] Line number references in docs are accurate against current code
- [ ] Return type documentation matches actual return types
- [ ] All constants and values are documented correctly
- [ ] No undocumented public API surface (functions/classes exported but not in docs)
- [ ] Error handling behavior is documented
- [ ] Edge cases are documented where relevant

### Code Quality Interrogation
- [ ] No potential bugs in edge cases (empty input, zero division, overflow)
- [ ] Error handling is consistent and robust
- [ ] Type annotations are present and accurate
- [ ] No unsafe patterns (eval, exec, injection risks)
- [ ] Caching behavior is correct and documented
- [ ] No resource leaks (file handles, connections, memory)
- [ ] Concurrency safety if applicable

### Cross-Module Consistency
- [ ] Naming conventions are consistent across modules
- [ ] Return type patterns are consistent
- [ ] Import patterns follow established conventions
- [ ] No circular dependencies
- [ ] Module boundaries are clean

### Test Coverage Observations
- [ ] Note any functions that appear to lack test coverage
- [ ] Note any edge cases that should be tested
- [ ] Note any integration tests that are missing

---

## Output Format

Each subagent writes to `plans/review_improvements_<module>.md` using this structure:

```markdown
# <Module> Module Review — Improvement Plan

**Reviewed:** architecture/<doc>.md against nl_calc/<module>.py  
**Date:** <YYYY-MM-DD>

## Verified Claims (with line references)
- [claim from docs] — VERIFIED at code line <N> (docs line <M>)
- [claim from docs] — VERIFIED at code line <N> (docs line <M>)

## Discrepancies Between Documentation and Code
- [HIGH/MEDIUM/LOW] <description of discrepancy>
  - Documentation says: <X> (docs line <M>)
  - Code actually does: <Y> (code line <N>)
  - Impact: <what this means>

## Potential Bugs
- [HIGH/MEDIUM/LOW] <bug description>
  - Location: `<file>:<line>`
  - Issue: <what could go wrong>
  - Suggested investigation: <what to look at>

## Improvement Suggestions
### HIGH Priority
- [critical improvements that affect correctness or security]

### MEDIUM Priority
- [important improvements for robustness, performance, or maintainability]

### LOW Priority
- [nice-to-have improvements, style, clarity]

## Summary
[2-3 sentence summary of module health, overall documentation quality, 
and key areas needing attention]
```

---

## Stale Item Detection Criteria

During Phase 2, the stale item scanner flags items for pruning:

1. **Dead references**: Documentation mentions functions/classes/variables that no longer exist in code
2. **Unimplemented features**: Documentation describes features not in code (not deferred, just absent)
3. **Superseded docs**: Multiple documents covering same topic with conflicting info
4. **Outdated examples**: Code examples in docs that wouldn't work with current API
5. **Orphaned modules**: Architecture docs for modules that have been removed or renamed
6. **Stale line numbers**: Docs reference specific line numbers that no longer match
7. **Duplicate content**: Same information repeated across multiple architecture files
8. **Outdated counts**: Line counts, file sizes, test counts that are stale
9. **Missing modules**: Code modules that have no corresponding architecture doc

---

## Existing Review Plans (from prior review)

The following improvement plans already exist from a previous review. These may be refreshed or replaced based on the current review:

- `plans/review_improvements_api.md` — API documentation review
- `plans/review_improvements_cli.md` — CLI documentation review
- `plans/review_improvements_confusables.md` — confusables.py documentation review
- `plans/review_improvements_diff.md` — diff.py documentation review
- `plans/review_improvements_evaluator.md` — evaluator.py documentation review
- `plans/review_improvements_exact.md` — exact/ subpackage documentation review
- `plans/review_improvements_mcp.md` — MCP server documentation review
- `plans/review_improvements_measure.md` — measure.py documentation review
- `plans/review_improvements_normalize.md` — normalize.py documentation review
- `plans/review_improvements_overview.md` — overview documentation review
- `plans/review_improvements_primitives.md` — primitives.py documentation review
- `plans/review_improvements_synthesis.md` — synthesis.py documentation review
- `plans/review_improvements_unicode_tools.md` — unicode_tools.py documentation review
- `plans/review_improvements_units.md` — units.py documentation review
- `plans/review_improvements_validate.md` — validate.py documentation review

Subagents should overwrite these files with fresh analysis based on the current state of the codebase.

---

## Progress Tracking

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Batch 1 (overview, api, normalize, evaluator, units) | PENDING | |
| Phase 1: Batch 2 (primitives, unicode_tools, confusables) | PENDING | |
| Phase 1: Batch 3 (validate, diff, measure, synthesis) | PENDING | |
| Phase 1: Batch 4 (cli, mcp, exact) | PENDING | |
| Phase 2: Stale item identification | PENDING | |
| Phase 3: Consolidation | PENDING | |

---

## Completion Criteria

This review is complete when:
1. All 15 modules have corresponding `plans/review_improvements_<module>.md` files
2. Each file contains verified claims, discrepancies, bugs, and prioritized improvements
3. Stale items are documented in `plans/review_stale_items.md`
4. This file is updated with final status and consolidation summary