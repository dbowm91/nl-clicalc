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
- Data structure field mismatches (CheckBracketsResult, WordMetrics) - most fixed
- Classification labels in synthesis.py now match documentation (`accent_or_diacritic_difference` implemented)

## Architecture Review Findings (2026-05-22)

During comprehensive architecture review of all 15 modules, the following issues were identified and fixed:

**Critical Bugs Fixed:**
1. `units.py.__rsub__` - operand reversal behavior intentional; `5 - UnitValue(3, 'ft')` returns `2 ft`
2. `exact/__init__.py` - missing exports for `unicode_scripts`, `confusables_count`, `longest_common_subsequence`
3. `measure.py` - invalid `__slots__` on TypedDict classes removed
4. `primitives.py` - BIDI control chars (U+202A-202E, U+2066-2069) already in `_INVISIBLE_CHARS`
5. `normalize.py` - REPL history condition already checks `_ is not None`
6. `build_single.py` - `mcp_main = main` alias fix when main is renamed to mcp_main during build

**Medium Priority Fixed:**
- `synthesis.py._generate_agent_instruction` - missing case for `accent_or_diacritic_difference` classification
- `validate.py` - unused `signal` import removed
- `primitives.py` - dead `_advance_past_sequence()` function removed
- `evaluator.py` - redundant local import of `convert_temperature` removed
- `measure.py` - control_chars now counts Co and Cn per UTS #55
- `normalize.py` - `combine_number_parts()` fixed for "ten six" case
- `normalize.py` - `_handle_negative_token()` bounds checking added

**Design Decisions (Not Bugs):**
- `are_units_compatible()` returns `True` for unknown categories by design (allows custom units)
- `evaluate_cached` caching doesn't invalidate on variable changes (stable expressions expected)
- `__rsub__` behavior for scalar minus UnitValue is intentional

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