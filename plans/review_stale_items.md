# Architecture Stale Item Report

**Date:** 2026-05-28

## Dead References (Functions/Classes/Variables in Docs but Not Code)

- **`normalize_main` alias does not exist** (cli.md:13,16)
  - Documentation claims `main()` is "aliased as `normalize_main()` for build compatibility" and shows import statement
  - Code: No such alias exists in `normalize.py` or `__init__.py`
  - The renaming only happens in `build_single.py` at line 234 during single-file build
  - Impact: Any code/documentation referencing `normalize_main` will fail

- **`evaluate_with_timeout` docstring uses forbidden syntax** (evaluator.py:1368)
  - The docstring example `sum(i**2 for i in range(10000))` uses a generator expression
  - Code: `ast.GeneratorExp` is explicitly forbidden at evaluator.py:1261
  - Impact: Example would raise `EvaluationError` if executed

## Unimplemented Features (In Docs but Not Code)

- **`normalize_main` alias** (documented in cli.md but not implemented in source)
  - The alias only exists during `build_single.py` build process, not in source
  - Source `normalize.py` only has `main()`, no alias

## Superseded/Conflicting Documentation

- **Duplicate `G` / `gravitationalconstant` entry** (evaluator.md:155 and 161)
  - The constants table lists `G` / `gravitationalconstant` twice with identical values
  - Code: Only one entry exists in CONSTANTS dict
  - Impact: Documentation clutter; no functional conflict but redundant

## Outdated Examples

- **ALL THREE `common_prefix_suffix` examples are wrong** (diff.md:53-59)
  - `"hello", "hell"` doc says `common_prefix_len: 3` → code returns `4`
  - `"hello", "yo"` doc says `common_prefix_len: 0` → code returns `0` but `common_suffix_len: 1` (doc says `0`)
  - `"testing", "ing"` doc says `common_suffix_len: 0` → code returns `3`
  - Code is correct; all three examples need updating

- **`FirstDiff` TypedDict declaration wrong** (diff.md:88-92)
  - Docs show 3 fields: `position`, `a_char`, `b_char`
  - Code has 6 fields: `a_index`, `b_index`, `a_char`, `b_char`, `a_codepoint`, `b_codepoint`

- **`diff_spans` example shows filtered `equal` spans** (diff.md:105-109)
  - Documentation shows output with `kind='equal'` spans
  - Code explicitly filters out equal spans: `if tag == "equal": continue`
  - Only non-equal spans are returned

- **`visible_repr()` display order incomplete** (primitives.md:253-260)
  - Docs describe 4 steps but code has 5 steps including BIDI handling (primitives.py:277-284)
  - Missing: BIDI character checks (U+2060-U+206F range)

- **`normalize_expression` return type wrong** (api.md:130, normalize.md:143-146)
  - Docs say: `normalize_expression(expression: str) -> str`
  - Code: Returns `tuple[str, int]` (normalized_string, exit_code) and requires `operators` and `patterns` arguments

## Orphaned Modules

- None confirmed. All documented modules exist in codebase.

## Stale Line Numbers

- None confirmed. Architecture docs generally avoid specific line number references.

## Duplicate Content Across Files

- **`common_prefix_suffix` overlap prevention behavior** documented in multiple places with inconsistent examples
  - diff.md (lines 53-59) shows wrong examples
  - synthesis.md references same examples but they are wrong
  - The actual function correctly prevents prefix/suffix overlap, but docs show wrong return values

- **`FirstDiff` structure** appears in both diff.md (lines 28-36, 85-92) with different field definitions (correct version at lines 28-36, wrong version at 88-92)

- **Confusables data description** appears in both confusables.md and unicode_tools.md
  - confusables.md describes data structure
  - unicode_tools.md describes usage functions
  - No conflict, but overlap in describing confusables table format

## Outdated Counts (Line counts, file sizes, etc.)

- **confusables.py line count** (confusables.md:12,297)
  - Docs say "~6581 lines" but actual is 6580 lines
  - Minor: description already says "approximately"

- **confusables.py file size** (confusables.md:12,297, exact.md:338)
  - Docs say "~180KB, ~6500 lines" and "~180KB, ~6580 lines"
  - Actual: ~176KB, 6580 lines
  - Slight size discrepancy (180KB vs 176KB)

## Missing Modules (Code has but no Doc)

- **`reverse_confusables()` function** - exported in `__init__.py:52` and `unicode_tools.py:268-292` but completely absent from unicode_tools.md architecture document
  - Fully implemented public API function with no documentation

- **`load_user_config_extended()`** - exists in evaluator.py:168-187 but not documented anywhere
  - Note: Intentionally not exported in `__init__.py` per docstring ("not officially supported")

- **Multiple UnitValue public methods undocumented** (units.md)
  - Missing: `__str__`, `__format__`, `__eq__`, `__hash__`, `__radd__`, `__rsub__`, `__rmul__`, `__rtruediv__`, `__neg__`, `__pos__`, `__abs__`, `__round__`, `__complex__`, `__int__`, `__float__`
  - Docs only mention `convert_to()` and `__repr__()`

- **`_handle_initialize` description imprecise** (mcp.md:203-208)
  - Doc says "called inline" but it's routed through `handle_request` conditional
  - Minor clarity issue

## Additional Findings from Review Plans (Verified as Valid)

The following were identified in review plans and confirmed as valid stale items:

1. **`--verbose` flag behavior mismatch** (cli.md:32 vs normalize.py:1441)
   - Docs say "Show detailed error information and tracebacks"
   - Code actually shows expression in output (equivalent to `--show`)

2. **`check_if_number` return type annotation wrong** (normalize.md:156-166)
   - Docs show `"type": type(token)` but code returns actual type string (e.g., `"int"`, `"float"`)

3. **`normalize_expression` `skip_validation` parameter undocumented** (normalize.md:143-146)
   - Code has parameter at normalize.py:1109 but docs omit it

4. **`evaluate_raw` incomplete signature** (api.md:19)
   - Doc shows `evaluate_raw(expression: str)` without mentioning it calls `normalize_expression` internally

5. **`visible_repr()` display order incomplete** - BIDI handling missing from docs (primitives.md)

6. **`normalize_expression` signature across docs** - multiple docs show simplified or wrong signatures

## Summary

The architecture documentation has several significant stale items requiring correction. The most impactful are: (1) `normalize_main` alias documented as existing but not present in source code, (2) all three `common_prefix_suffix` examples in diff.md showing incorrect return values, (3) `FirstDiff` TypedDict documentation showing 3 fields when code has 6, and (4) `normalize_expression` return type documented as `str` when it returns `tuple[str, int]`. Most issues stem from documentation not being updated after code changes, particularly around return types and function signatures. The codebase is generally well-documented but these discrepancies between docs and actual API surface should be addressed.
