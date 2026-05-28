# Architecture Review Plan

**Status: IN PROGRESS** (2026-05-28)

Systematic review of all architecture documentation against codebase. Uses subagents to review discrete modules in parallel.

---

## Overview

This plan orchestrates a deep review of every architecture module. Each subagent is assigned a discrete module, reviews its documentation against code, verifies claims, interrogates for bugs/improvements, and writes an improvement plan to `plans/review_improvements_<module>.md`.

## Review Process

### Phase 1: Parallel Module Reviews (Subagents)

Each subagent receives:
- Architecture document(s) to review
- Corresponding source file(s) to verify against
- Output file path in `plans/` directory

**Subagent Instructions:**
1. Read the assigned architecture document(s) completely
2. Read the corresponding source code file(s)
3. For each claim in the documentation:
   - Verify the claim matches the code (function names, line numbers, behavior)
   - Note any discrepancies (documentation says X but code does Y)
   - Note any undocumented features (code has X but docs don't mention it)
4. Interrogate the code:
   - Look for potential bugs (edge cases, error handling, type issues)
   - Look for inconsistencies (naming, patterns, return types)
   - Look for missing tests or documentation gaps
5. Write improvement plan to `plans/review_improvements_<module>.md` with:
   - Verified claims (with line references)
   - Discrepancies found
   - Potential bugs
   - Improvement suggestions (prioritized: HIGH/MEDIUM/LOW)
   - Summary

### Phase 2: Stale Item Identification

After all module reviews complete, a final pass identifies:
- Architecture documents that reference removed/renamed functions
- Documentation for features not yet implemented (stale TODOs)
- Module files that have been superseded or are no longer relevant
- Duplicate documentation across files

### Phase 3: Consolidation

Consolidate findings into a summary section in this file.

---

## Discrete Architecture Modules

| # | Module | Documentation | Source Files | Output Plan |
|---|--------|--------------|--------------|-------------|
| 1 | overview | architecture/overview.md | (top-level) | plans/review_improvements_overview.md |
| 2 | normalize | architecture/normalize.md | nl_calc/normalize.py | plans/review_improvements_normalize.md |
| 3 | evaluator | architecture/evaluator.md | nl_calc/evaluator.py | plans/review_improvements_evaluator.md |
| 4 | units | architecture/units.md | nl_calc/units.py | plans/review_improvements_units.md |
| 5 | primitives | architecture/primitives.md, architecture/exact-primitives.md | nl_calc/exact/primitives.py | plans/review_improvements_primitives.md |
| 6 | unicode_tools | architecture/unicode_tools.md, architecture/exact-unicode_tools.md | nl_calc/exact/unicode_tools.py | plans/review_improvements_unicode_tools.md |
| 7 | confusables | architecture/confusables.md | nl_calc/exact/confusables.py | plans/review_improvements_confusables.md |
| 8 | validate | architecture/validate.md | nl_calc/exact/validate.py | plans/review_improvements_validate.md |
| 9 | diff | architecture/diff.md | nl_calc/exact/diff.py | plans/review_improvements_diff.md |
| 10 | measure | architecture/measure.md | nl_calc/exact/measure.py | plans/review_improvements_measure.md |
| 11 | synthesis | architecture/synthesis.md | nl_calc/exact/synthesis.py | plans/review_improvements_synthesis.md |
| 12 | cli | architecture/cli.md | nl_calc/__main__.py | plans/review_improvements_cli.md |
| 13 | mcp | architecture/mcp.md, architecture/mcp_server.md | nl_calc/mcp/server.py, tools.py, schemas.py | plans/review_improvements_mcp.md |
| 14 | api | architecture/api.md | (various) | plans/review_improvements_api.md |
| 15 | exact | architecture/exact.md | nl_calc/exact/__init__.py, nl_calc/exact/*.py | plans/review_improvements_exact.md |

---

## Subagent Dispatch Plan

Subagents will be dispatched in batches to manage parallel execution. Each subagent operates independently.

### Batch 1: Core Modules (3 subagents)
- **Subagent A**: overview + api (overview is top-level, api is cross-cutting)
- **Subagent B**: normalize + evaluator (NL processing pipeline)
- **Subagent C**: units (standalone unit system)

### Batch 2: exact/ Primitives (3 subagents)
- **Subagent D**: primitives + exact-primitives (UTF-8, codepoints)
- **Subagent E**: unicode_tools + exact-unicode_tools (script detection)
- **Subagent F**: confusables (homoglyph data)

### Batch 3: exact/ Analysis (4 subagents)
- **Subagent G**: validate (brackets, JSON, regex)
- **Subagent H**: diff (string comparison)
- **Subagent I**: measure (text metrics)
- **Subagent J**: synthesis (higher-level analysis)

### Batch 4: Interface & Integration (3 subagents)
- **Subagent K**: cli (command-line interface)
- **Subagent L**: mcp + mcp_server (MCP server)
- **Subagent M**: exact (subpackage overview)

---

## Review Checklist (Per Module)

Each subagent must address:

- [ ] Documentation exists for all public functions/classes
- [ ] Function signatures match between docs and code
- [ ] Line number references are accurate
- [ ] Return type documentation matches actual returns
- [ ] All constants/values documented correctly
- [ ] No undocumented public API surface
- [ ] Error handling behavior documented
- [ ] Edge cases documented where relevant
- [ ] No stale references to removed features
- [ ] No duplicate documentation across files

---

## Stale Item Detection Criteria

During Phase 2, flag for pruning:
1. **Dead references**: Documentation mentions functions/classes that no longer exist in code
2. **Unimplemented features**: Documentation describes features not in code (not deferred, just absent)
3. **Superseded docs**: Multiple documents covering same topic with conflicting info
4. **Outdated examples**: Code examples in docs that wouldn't work with current API
5. **Orphaned modules**: Architecture docs for modules that have been removed or renamed

---

## Output Format

Each subagent writes to `plans/review_improvements_<module>.md`:

```markdown
# <Module> Module Review - Improvement Plan

## Verified Claims (with line references)
- [list of verified claims with code line numbers]

## Discrepancies Between Documentation and Code
- [list of discrepancies with priority]

## Potential Bugs
- [list of bugs found with location]

## Improvement Suggestions
### HIGH Priority
- [critical improvements]
### MEDIUM Priority
- [important improvements]
### LOW Priority
- [nice-to-have improvements]

## Summary
[2-3 sentence summary of module health]
```

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
3. Stale items have been identified and documented
4. This file is updated with final status and summary
