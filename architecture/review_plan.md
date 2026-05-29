# Architecture Review Plan

## Overview

This plan orchestrates a systematic review of all architecture documentation modules in the `architecture/` directory. Each module document will be reviewed by a dedicated subagent who will:

1. Read the architecture document
2. Verify all claims against the actual code
3. Interrogate the code for bugs, improvements, and inconsistencies
4. Write findings to `plans/<module>_review.md` at the repository root

## Architecture Modules to Review

The following architecture documents (15 total) will be reviewed, excluding `review_plan.md`:

| Module | Document | Code Location |
|--------|----------|---------------|
| API | `api.md` | `nl_calc/__init__.py`, `nl_calc/evaluator.py` |
| CLI | `cli.md` | `nl_calc/__main__.py` |
| Confusables | `confusables.md` | `nl_calc/exact/confusables.py` |
| Diff | `diff.md` | `nl_calc/exact/diff.py` |
| Evaluator | `evaluator.md` | `nl_calc/evaluator.py` |
| Exact | `exact.md` | `nl_calc/exact/` (overview) |
| MCP | `mcp.md` | `nl_calc/mcp/` |
| Measure | `measure.md` | `nl_calc/exact/measure.py` |
| Normalize | `normalize.md` | `nl_calc/normalize.py` |
| Overview | `overview.md` | Entire codebase |
| Primitives | `primitives.md` | `nl_calc/exact/primitives.py` |
| Synthesis | `synthesis.md` | `nl_calc/exact/synthesis.py` |
| Unicode Tools | `unicode_tools.md` | `nl_calc/exact/unicode_tools.py` |
| Units | `units.md` | `nl_calc/units.py` |
| Validate | `validate.md` | `nl_calc/exact/validate.py` |

## Subagent Tasks

Each subagent will perform the following steps for their assigned module:

### Step 1: Read Architecture Document
- Read the corresponding `.md` file in `architecture/`
- Note all claims about code structure, functions, constants, and behaviors

### Step 2: Locate Source Code
- Map document claims to actual source files
- Identify the relevant code module(s) to verify

### Step 3: Verify Claims Against Code
For each claim in the document:
- Find the corresponding code
- Verify accuracy (MATCHES / MISMATCH / MISSING)
- Document any discrepancies

### Step 4: Interrogate for Bugs
- Check for edge cases not handled
- Look for potential IndexError, KeyError, TypeError sources
- Verify error handling is complete
- Check for race conditions or thread-safety issues

### Step 5: Identify Improvements
- Look for code that could be simplified
- Identify missing validation
- Note performance concerns
- Check for consistency issues

### Step 6: Write Review Output
Write a `<module>_review.md` file to `plans/` at repository root with:
- Verified claims (with MATCHES/MISMATCH status)
- Discrepancies found
- Bugs identified
- Improvements suggested
- Priority classification for each item

## Review Output Format

Each subagent should output a file named `plans/<module>_review.md`:

```markdown
# <Module> Architecture Review

## Verified Claims
1. [Claim description] - MATCHES/MISMATCH
   - Evidence: [file:line]

## Discrepancies
1. [Description of mismatch]
   - Doc says: [what doc claims]
   - Code has: [what code actually does]

## Bugs Found
1. [Bug description]
   - Location: [file:line]
   - Severity: [High/Medium/Low]

## Improvements
1. [Improvement suggestion]
   - Priority: [High/Medium/Low]

## Priority Summary
- High: [list]
- Medium: [list]
- Low: [list]
```

## Dispatch Order

Subagents will be dispatched in the following order (grouped for parallel execution):

**Group 1 (Independent modules):**
- `api` → Review api.md
- `cli` → Review cli.md
- `validate` → Review validate.md

**Group 2 (Exact/ submodules):**
- `primitives` → Review primitives.md
- `confusables` → Review confusables.md
- `unicode_tools` → Review unicode_tools.md
- `measure` → Review measure.md
- `diff` → Review diff.md
- `synthesis` → Review synthesis.md

**Group 3 (Core modules):**
- `normalize` → Review normalize.md
- `evaluator` → Review evaluator.md
- `units` → Review units.md

**Group 4 (Meta modules):**
- `mcp` → Review mcp.md
- `overview` → Review overview.md
- `exact` → Review exact.md

## Stale Item Detection

After all reviews complete, the orchestrator will:

1. Compare `architecture/plans/` contents against the new `plans/` directory
2. Identify stale review files (those in `architecture/plans/` that are older or superseded)
3. Remove `architecture/plans/` stale items (these are outdated review artifacts)

Files to evaluate for removal:
- `architecture/plans/api_review.md`
- `architecture/plans/cli_review.md`
- `architecture/plans/confusables_review.md`
- `architecture/plans/diff_review.md`
- `architecture/plans/evaluator_review.md`
- `architecture/plans/exact_review.md`
- `architecture/plans/mcp_server_review.md`
- `architecture/plans/measure_review.md`
- `architecture/plans/normalize_review.md`
- `architecture/plans/overview_review.md`
- `architecture/plans/primitives_review.md`
- `architecture/plans/synthesis_review.md`
- `architecture/plans/unicode_tools_review.md`
- `architecture/plans/units_review.md`
- `architecture/plans/validate_review.md`

## Execution

After writing this plan:
1. Dispatch all Group 1 subagents in parallel
2. Wait for completion, then dispatch Group 2 (6 agents)
3. Wait for completion, then dispatch Group 3 (3 agents)
4. Wait for completion, then dispatch Group 4 (3 agents)
5. Detect and remove stale items from `architecture/plans/`
6. Commit this plan and all review outputs to main

## Verification

After all reviews complete, run:
```bash
python3 -m pytest tests/ -v
```

Ensure all tests pass after any code changes identified in reviews.