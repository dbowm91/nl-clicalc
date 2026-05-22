# Architecture Review Skill

## Purpose
Guide agents through systematic architecture document review against implementation code.

## When to Use
- Reviewing architecture documents (`.md` files in `architecture/`)
- Verifying implementation matches documentation
- Identifying bugs, inconsistencies, or missing features
- Adding new features to the codebase

## Review Process

### 1. Gather Information
```bash
# Read architecture document
cat architecture/<module>.md

# Read corresponding implementation
cat nl_calc/<module>.py

# List all architecture docs
ls architecture/
```

### 2. Focus Areas Checklist
For each module, examine:
1. **Completeness** - All documented features implemented?
2. **Correctness** - Implementation matches behavior?
3. **Consistency** - Doc and code contradict?
4. **Edge Cases** - Unhandled cases?
5. **Performance** - Efficiency concerns?
6. **Security** - Potential issues?
7. **Maintainability** - Code quality?
8. **Test Coverage** - Adequate tests?

### 3. Verification Steps
- Use `grep` to find specific function definitions
- Use `python3 -c "from module import function"` to verify exports
- Check `__all__` lists for public API consistency
- Run tests to verify functionality

### 4. Important Notes
- Use specific `file:line` references when reporting issues
- Distinguish between bugs (code wrong) vs doc issues (doc wrong)
- For bugs, verify the issue actually causes failure before documenting

## Common Issues Found in This Codebase

- Functions in `__all__` but not exported correctly
- Documentation claims features not in code
- Code has features not documented
- Alias mappings that break functionality (e.g., prefixed units aliased to base)
- Precision errors in constants
- Missing CLI flags between built vs source versions
- TypedDict vs NamedTuple mismatches (documentation shows one, code uses other)
- Missing function aliases (documentation shows `normalize_main`, `mcp_main` but they don't exist)
- ErrorEnvelope class documented but doesn't exist in code
- Data structure field mismatches (CheckBracketsResult, WordMetrics) - all fixed
- Classification labels in synthesis.py (`accent_or_diacritic_difference`, `unicode_normalization_only`) now properly reachable

## Architecture Review Findings (2026-05-22)

During comprehensive architecture review of all modules, the following issues were identified and fixed:

**Critical Bugs Fixed:**
1. `normalize.py.combine_number_parts()` - Added skip_next flag to prevent duplicate processing of merged number parts
2. `synthesis.py._classify_difference()` - Reordered checks so NFC equality is checked before casefold equality
3. `exact/__init__.py` - missing exports for `unicode_scripts`, `confusables_count`, `longest_common_subsequence`
4. `measure.py` - invalid `__slots__` on TypedDict classes removed
5. `primitives.py` - BIDI control chars (U+202A-202E, U+2066-2069) already in `_INVISIBLE_CHARS`
6. `normalize.py` - REPL history condition already checks `_ is not None`

**Medium Priority Fixed:**
- `synthesis.py._generate_agent_instruction` - missing case for `accent_or_diacritic_difference` classification now handled
- `primitives.py` - dead `_advance_past_sequence()` function removed
- `measure.py` - control_chars now counts Co and Cn per UTS #55
- `normalize.py` - `_handle_negative_token()` bounds checking added
- `schemas.py` - removed unused `SuccessEnvelope` TypedDict
- `validate.md` - fixed check_brackets examples and RegexMatch naming
- `unicode_tools.md` - added `unicode_scripts()` and `confusables_count()` to index
- `overview.md` - added `get_unit_category()` to Key Data Structures table

**Wave 3 Documentation Fixes (2026-05-22):**
- exact.md: CheckBracketsResult now correctly documented with `unmatched_openers`/`unmatched_closers` (not message/position/expected/found)
- exact.md: RegexTestResult now correctly documented with `valid_pattern` and `results: list[RegexMatch]` (not match_count/matches/non_matches)
- exact.md: Added RegexMatch TypedDict definition (sample, matches, fullmatch, span, groups, groupdict)
- exact.md: LineMetrics now correctly documented with full field list (lines, nonempty_lines, blank_lines, max_line_length_codepoints, trailing_whitespace_lines, newline_style, ends_with_newline)
- api.md: Added `get_unit_category()` to utility functions
- api.md: Clarified that `normalize_unit()` exists in units.py but is not part of public API

**Design Decisions (Not Bugs):**
- `are_units_compatible()` returns `False` when one category is known but other is unknown (safe behavior)
- `evaluate_cached` caching doesn't invalidate on variable changes (stable expressions expected)
- `__rsub__` behavior for scalar minus UnitValue is intentional (result in unit's unit)
- TypedDict classes in this codebase have `__slots__` defined but they are ignored (dict-based access is used). While unusual, this doesn't cause errors but provides no memory benefit.

## Architecture Files Location
- `architecture/` - Module-level documentation
- `docs/exact.md` - exact/ module documentation
- `plans/` - Implementation plans and reviews

## Documentation Maintenance
When updating code:
1. Check if corresponding architecture doc needs update
2. Ensure `build_single.py` still works (code must be in core modules)
3. Run all tests to verify no regressions
4. Update AGENTS.md if new conventions are introduced