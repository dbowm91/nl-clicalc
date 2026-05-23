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
- **visible_repr() check order is critical** - Variation selector (U+FE00-U+FE0F) must be checked BEFORE category 'M' checks

### 5. Known Code Patterns
- TypedDict classes don't support `__slots__` (ignored by Python)
- `_get_script_heuristic()` is cached with `@lru_cache`
- CONFUSABLES dict is unidirectional (Latin → confusable chars)
- `unicode_normalization_only` classification is valid and reachable

## Common Issues Found in This Codebase

**These issues have been identified and resolved:**

1. **Combine consecutive numbers** - `split_at_operators` now properly handles whitespace-separated number words
2. **TypedDict `__slots__`** - Removed from all TypedDict classes (they don't support `__slots__`)
3. **Missing exports in exact/__init__.py** - `unicode_scripts`, `confusables_count`, `longest_common_subsequence` now exported
4. **Text classification order** - `_classify_difference()` checks NFC equality before casefold equality
5. **MCP response consistency** - `math_eval` returns direct result dict

**Documentation/Code inconsistencies to watch for:**

- TypedDict vs NamedTuple mismatches (code uses TypedDict throughout)
- Missing function aliases (check `mcp_main = main` at server.py:234)
- Data structure field mismatches (verify against actual code)

**Note:** Many of these issues were identified and fixed during the 2026-05-22 architecture review. See the findings section below for details.

## Architecture Review Findings (Historical)

This section records issues found during the 2026-05-22 architecture review. All critical issues were fixed.

**Critical Bugs Fixed (2026-05-22):**
- `normalize.py.combine_number_parts()` - Added skip_next flag to prevent duplicate processing
- `synthesis.py._classify_difference()` - Reordered checks for NFC before casefold
- `exact/__init__.py` - Added missing exports
- `measure.py` - Removed invalid `__slots__` from TypedDict classes
- `primitives.py` - BIDI control chars confirmed in `_INVISIBLE_CHARS`
- `schemas.py` - Removed unused `SuccessEnvelope` TypedDict

**Design Decisions Documented:**
- `are_units_compatible()` returns `False` when one category is unknown
- `evaluate_cached` caching is intentional (stable expressions)
- TypedDict `__slots__` are ignored (dict-based access used)

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