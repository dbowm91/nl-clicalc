# Architecture Review Plan

## Status: Incomplete - Implementation Phase

The review phase is complete. All 15 module reviews have been completed and saved to `plans/<module>_review.md`. This document now tracks the implementation phase to address findings from the reviews.

---

## Implementation Waves

### Wave 1: Critical Bugs (Code Fixes)

| # | Module | Issue | Priority |
|---|--------|-------|----------|
| 1.1 | units | `__rsub__` operand reversal bug (line 81-82) | HIGH |
| 1.2 | exact | Missing exports in `__init__.py` (unicode_scripts, confusables_count, longest_common_subsequence) | HIGH |
| 1.3 | measure | Invalid `__slots__` on TypedDict classes (lines 26, 38, 52) | HIGH |
| 1.4 | primitives | Invalid emoji range 0x1FFFF → 0x10FFFF (line 382) | HIGH |
| 1.5 | cli | REPL history stores None on eval failure (line 1029) | HIGH |
| 1.6 | mcp | Missing `mcp_main` alias in server.py | HIGH |

### Wave 2: Medium Priority Fixes

| # | Module | Issue | Priority |
|---|--------|-------|----------|
| 2.1 | units | Missing micro-unit categories (uA, μA, uV, μV) | MEDIUM |
| 2.2 | synthesis | Missing accent_or_diacritic_difference case in `_generate_agent_instruction` | MEDIUM |
| 2.3 | exact | Remove unused imports (signal in validate.py, normalize_unicode in synthesis.py) | MEDIUM |
| 2.4 | evaluator | Cache invalidation issue with user variables | MEDIUM |
| 2.5 | units | `are_units_compatible()` treats unknown categories as compatible | MEDIUM |

### Wave 3: Documentation & Low Priority

| # | Module | Issue | Priority |
|---|--------|-------|----------|
| 3.1 | All | Update architecture docs to reflect TypedDict usage (not NamedTuple/@dataclass) | LOW |
| 3.2 | All | Add missing function documentation (longest_common_subsequence, unicode_scripts, confusables_count) | LOW |
| 3.3 | evaluate | Export memory/variable functions via `__all__` | LOW |
| 3.4 | mcp | Update SuccessEnvelope usage or remove dead code | LOW |

---

## Modules Reviewed

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

## Verification Commands

After all reviews complete, run:
```bash
python3 -m pytest tests/
```