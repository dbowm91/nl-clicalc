# overview.md Architecture Review

## Verified Claims

1. **Purpose**: Natural language math calculator - MATCHES
2. **normalize.py description**: Correctly describes NL processing (lines 79-96) - MATCHES
3. **evaluator.py description**: AST-based evaluation, all features listed (lines 100-119) - MATCHES
4. **units.py description**: All unit categories listed (lines 123-144) - MATCHES
5. **CLI entry point**: __main__.py delegates to normalize.main() (lines 148-154) - MATCHES
6. **exact/ module structure**: All files and functions documented correctly - MATCHES
7. **mcp/ module structure**: Correct (schemas, tools, server) - MATCHES
8. **Build system**: build_single.py and install.py described correctly - MATCHES
9. **Data flow diagrams**: Accurate for run() and evaluate() pipelines - MATCHES
10. **Key Data Structures table**: All structures present (lines 451-463) - MATCHES
11. **Module Dependencies**: Accurate dependency chart (lines 467-496) - MATCHES
12. **Deep Dive Reviews table**: All review plan files listed (lines 500-519) - MATCHES
13. **API Quick Reference**: Correct usage examples - MATCHES

## Discrepancies

1. **normalize.py Key exports (line 94)**:
   - Shows: `run()`, `normalize()`, `normalize_expression()`, `main()`
   - But `normalize()` is NOT exported from __init__.py - only `run()` is exported
   - `normalize_expression` is exported, `main` is exported

2. **normalize.py Key exports missing**:
   - NORMALIZE, PATTERNS are not mentioned but are key constants for the API

3. **evaluator.py Key exports (line 117)**:
   - Shows: `evaluate()`, `evaluate_raw()`, `evaluate_cached()`, `PyCalcApp`
   - This is correct

4. **units.py Key exports (line 142)**:
   - Shows: `UnitValue`, `get_conversion_factor()`, `is_unit()`, `get_unit_category()`, `get_all_units()`
   - All correct

5. **exact/ LineMetrics in overview (lines 171-178)**:
   - Shows `count`, `newline_style`, `has_trailing_newline`, `blank_lines`
   - But actual LineMetrics has: `lines`, `nonempty_lines`, `blank_lines`, `max_line_length_codepoints`, `trailing_whitespace_lines`, `newline_style`, `ends_with_newline`
   - This is a documentation bug in overview.md

6. **primitives.py count_graphemes and truncate_to_grapheme (lines 193-194)**:
   - These functions ARE documented in overview but NOT in the primitives.md detailed section
   - Wait, let me check - they ARE mentioned in exact.md (lines 67-68)

## Bugs Found

No bugs. Documentation is mostly accurate.

## Improvements

1. **Medium Priority**: Fix LineMetrics structure in overview.md (lines 171-178)
2. **Low Priority**: Add NORMALIZE and PATTERNS to normalize.py key exports section

## Priority

- **Medium**: Fix LineMetrics documentation in overview.md
- **Low**: Minor export list corrections