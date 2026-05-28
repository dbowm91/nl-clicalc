# confusables Module Review — Improvement Plan

**Reviewed:** architecture/confusables.md against nl_calc/exact/confusables.py
**Date:** 2026-05-28

## Verified Claims (with line references)
- Purpose: Contains confusables table derived from Unicode Standard Annex #39 — VERIFIED (confusables.py:1-6)
- Data Source: https://www.unicode.org/Public/security/latest/confusables.txt — VERIFIED at scripts/generate_confusables.py:15
- Data Structure: `CONFUSABLES: dict[str, str]` mapping codepoint strings to substitution strings — VERIFIED at confusables.py:14
- Generating the Table: scripts/generate_confusables.py exists and parses confusables.txt — VERIFIED at scripts/generate_confusables.py:1-168
- Security Applications: Homoglyph/IDN homograph/social engineering detection described — VERIFIED via `detect_confusables()` in unicode_tools.py:187
- `CONFUSABLES` is auto-generated data (~180KB) — VERIFIED at generate_confusables.py:1, confusables.py is ~176KB
- Example mappings (`U+0430` → `U+0061`, `U+00C6` → `U+0041 U+0045`) — VERIFIED at confusables.py:348, 30

## Discrepancies Between Documentation and Code
- [LOW] File line count in docs says "6581 lines" but actual file is 6580 lines
  - Documentation says: "~6581 lines" (confusables.md line 12, general description)
  - Code actually is: 6580 lines (verified via `wc -l`)
  - Impact: Trivial — size description is approximate by design

- [LOW] Documentation mentions `unicode_tools.detect_confusables()` as how the table is used, but doesn't document
  - `confusables_count()` function exists in unicode_tools.py:233-247
  - `reverse_confusables()` function exists in unicode_tools.py:268-293
  - `__all__ = ["CONFUSABLES"]` exists at confusables.py:6580 but is not documented
  - These functions are exported in `__init__.py` and used by other modules but documentation only mentions `detect_confusables()`

- [LOW] The example in architecture/confusables.md shows `U+0022: "U+0027 U+0027"` (quotation mark → two apostrophes) but in actual confusables.py line 15 we have `"U+0022": "U+0027 U+0027"` — VERIFIED correct

## Potential Bugs
- [LOW] No actual bugs found — code is straightforward data with well-tested consumption functions
- The confusables table is auto-generated and the generator script has basic assertions (lines 162-163 in generate_confusables.py)
- All consumption functions (`detect_confusables`, `confusables_count`, `reverse_confusables`) have proper type annotations, error handling, and tests

## Improvement Suggestions

### MEDIUM Priority
1. **Document undocumented public exports**: The `__all__ = ["CONFUSABLES"]` at confusables.py:6580 is not documented, and neither are `confusables_count`/`reverse_confusables` in the architecture docs. Consider adding:
   - `confusables_count()` signature and purpose (thin wrapper, O(n) lookup per char)
   - `reverse_confusables()` signature and purpose (builds inverted index for "what looks like X")
   - `__all__` is present in confusables.py but documentation doesn't mention it

2. **Add `build_single.py` compatibility note**: Since `confusables.py` is 6580 lines of data (~176KB), including it inline in `nl_calc.py` via `build_single.py` significantly increases file size. Documentation should note this is a data-only module that gets inlined verbatim.

### LOW Priority
1. **Clarify relationship between docs and data**: The documentation uses example `U+0430` which maps to `U+0061`. The actual file at line 348 confirms this entry. Documentation examples are accurate.

2. **Consider adding test for `reverse_confusables()`**: While `detect_confusables` has tests in test_exact.py:250-276, `reverse_confusables()` has no direct test coverage (only used indirectly via synthesis.py). The function at unicode_tools.py:268 has proper error handling for non-single-char input but lacks a dedicated unit test.

3. **Data freshness**: Documentation doesn't mention when the confusables table was last regenerated or how to check data freshness. The generator script downloads from Unicode on each run, but `confusables.py` in the repo is a snapshot. Consider adding a comment or metadata about data version.

## Summary
The confusables architecture documentation is accurate and matches the code well. The module is essentially auto-generated data (~176KB, 6580 lines) that is consumed by well-tested utility functions (`detect_confusables`, `confusables_count`, `reverse_confusables`) in unicode_tools.py. The main gap is that the architecture document only mentions `detect_confusables()` but the `confusables_count()` and `reverse_confusables()` functions are also public exports with significant functionality. No bugs were found — the data generation, consumption, and error handling are all implemented correctly.
