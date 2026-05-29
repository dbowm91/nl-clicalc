# confusables.py Architecture Review

## Verified Claims (with MATCHES/MISMATCH status)

| Claim | Status | Notes |
|-------|--------|-------|
| **Purpose**: Contains confusables table derived from Unicode Standard Annex #39 | MATCHES | Code is auto-generated from Unicode confusables.txt (UTS #39) |
| **Data Source**: Official Unicode `confusables.txt` from unicode.org | MATCHES | `generate_confusables.py` fetches from `https://www.unicode.org/Public/security/latest/confusables.txt` |
| **Data Structure**: `CONFUSABLES: dict[str, str]` with "U+XXXX" keys and space-separated codepoint values | MATCHES | Actual structure matches exactly |
| **How Confusables Work**: `detect_confusables()` scans text using table | MATCHES | `unicode_tools.detect_confusables()` at line 197-240 |
| **Generating the Table**: `scripts/generate_confusables.py` handles download/parsing/output | MATCHES | Script exists and is functional |
| **Security Applications**: Homoglyph attacks, IDN homograph attacks, social engineering | MATCHES | Implementation supports these use cases |
| **Index Reference**: References overview.md | MATCHES | Reference exists in architecture |

## Discrepancies Found

### 1. Documentation Examples Are Illustrative Only
**Severity**: Minor

The architecture document (lines 19-22) shows example entries:
```python
"U+0430": "U+0061",            # Cyrillic 'а' → Latin 'a'
"U+0022": "U+0027 U+0027",    # quotation mark → two apostrophes
"U+0025": "U+00BA U+002F U+2080",  # percent sign → 'º/₀'
```

These are valid confusables but **not** the actual first entries in the sorted file. The file is sorted by codepoint, so `U+0022` would appear before `U+0430`. The document's examples appear to be illustrative, not exact excerpts. This is not a bug but could mislead readers expecting to find these entries at the top.

### 2. File Line Count Discrepancy
**Severity**: Minor

The architecture document states the file is "~180KB, 6580 lines". The actual file is 6581 lines (including `__all__`). This is a minor mismatch - the size estimate (~180KB) is approximately correct.

## Bugs Identified

### None Found

The confusables implementation is a straightforward data file and generation script. No bugs were identified:

- Data structure is consistent (dict of string→string)
- Generation script handles multi-codepoint substitutions correctly
- Parser properly handles comments and header lines
- Sort order is deterministic (by codepoint)
- Import verification is performed after generation

## Edge Cases Handled Correctly

1. **Multi-codepoint substitutions**: Handled by `parse_line()` splitting on whitespace and joining characters
2. **Comments/headers**: `data_started` flag correctly skips non-data lines
3. **Invalid codepoints**: `parse_code_point()` validates with regex before conversion
4. **Empty substitutions**: Checked with `if not sub_parts` before processing
5. **Python 3.14+ compatibility**: `unicode_tools.py` tries `unicodedata.script()` first with fallback

## Potential Improvements

### Priority: Low

1. **Document illustrative examples**: The architecture document could clarify that the example entries are illustrative, not actual file excerpts.

2. **Add test for regeneration**: Consider adding a test that verifies the confusables table can be regenerated and produces identical output (reproducibility test).

3. **Add regeneration date comment**: The generated file could include a comment with the date of generation or the version of confusables.txt used.

## Code Quality Assessment

| Aspect | Rating | Notes |
|--------|--------|-------|
| Data correctness | Good | Auto-generated from official Unicode source |
| Type safety | Good | TypedDict classes used appropriately |
| Performance | Good | `lru_cache` used for `_get_script_heuristic()` and `_build_reverse_index()` |
| Error handling | Good | Validation in `parse_code_point()` and try/except in generators |
| Documentation | Adequate | Module docstring explains origin; in-code comments clarify structure |

## Priority Summary

| Priority | Item | Description |
|----------|------|-------------|
| Low | Documentation clarity | Clarify that example entries are illustrative |
| Low | Reproducibility test | Add test to verify regeneration produces identical output |
| Low | Regeneration metadata | Add date/version comment to generated file |

## Conclusion

The `confusables.py` architecture is **correct and well-implemented**. The document accurately describes the purpose, data source, structure, and generation process. No bugs were found in the actual code - it's a straightforward auto-generated data file. The potential improvements are minor documentation and testing enhancements rather than bug fixes.