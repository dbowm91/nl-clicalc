# confusables.py Architecture Review

## Document: architecture/confusables.md

## Verified Claims
| Claim | Status | Evidence |
|-------|--------|----------|
| Data source URL: https://www.unicode.org/Public/security/latest/confusables.txt | VERIFIED | generate_confusables.py:16, confusables.py header |
| Data structure: dict[str, str] with U+XXXX format | VERIFIED | confusables.py:20, actual keys/values match format |
| Generator script: scripts/generate_confusables.py | VERIFIED | script exists at correct path, functional |
| Regenerate command: `python scripts/generate_confusables.py` | VERIFIED | script runs successfully with cache |
| Source version: 17.0.0 | VERIFIED | confusables.py:6, data/confusables.txt header |
| Source date: 2025-07-22 | VERIFIED | confusables.py:7, data/confusables.txt header |
| Generated date in header | VERIFIED | confusables.py:8 (2026-05-29) |
| Entry count: 6565 | VERIFIED | confusables.py:9, actual len(CONFUSABLES) = 6565 |
| File size ~176KB (~6580 lines) | VERIFIED | confusables.py: 6587 lines, ~176KB |
| No TypedDict classes in confusables.py | VERIFIED | confusables.py contains only CONFUSABLES dict and __all__ |
| CONFUSABLES exported via __all__ = ["CONFUSABLES"] | VERIFIED | confusables.py:6590 |
| Cyrillic U+0430 → U+0061 mapping | VERIFIED | CONFUSABLES["U+0430"] = "U+0061" |
| Cyrillic U+0410 → U+0041 mapping | VERIFIED | CONFUSABLES["U+0410"] = "U+0041" |
| Multi-codepoint example U+00C6 → U+0041 U+0045 | VERIFIED | CONFUSABLES["U+00C6"] = "U+0041 U+0045" |
| Multi-codepoint example U+0022 → U+0027 U+0027 | VERIFIED | CONFUSABLES["U+0022"] = "U+0027 U+0027" |
| Multi-codepoint example U+00D8 → U+004F U+0338 | VERIFIED | CONFUSABLES["U+00D8"] = "U+004F U+0338" |
| detect_confusables() function | VERIFIED | unicode_tools.py:197-240 |
| confusables_count() function | VERIFIED | unicode_tools.py:243-257 |
| reverse_confusables() function | VERIFIED | unicode_tools.py:278-302 |
| _build_reverse_index() with @lru_cache | VERIFIED | unicode_tools.py:260-275 |
| ConfusableInfo TypedDict | VERIFIED | unicode_tools.py:29-42 |
| detect_confusables returns list[ConfusableInfo] | VERIFIED | unicode_tools.py:197 |
| reverse_confusables returns list[str] | VERIFIED | unicode_tools.py:278 |
| detect_confusables example: 'pаypal' detection | VERIFIED | Correctly identifies U+0430 as confusable |
| reverse_confusables example: "0" in reverse_confusables("O") | VERIFIED | Returns True |
| Cached data at data/confusables.txt | VERIFIED | data/confusables.txt exists (745683 bytes) |
| Functions exported from exact module | VERIFIED | __init__.py:193-196, 293-295 |
| Scans text by codepoint string lookup | VERIFIED | unicode_tools.py:213-214 |

## Discrepancies

No major discrepancies found. The architecture document accurately describes the confusables.py implementation.

**Minor documentation note:** The architecture doc (line 21) shows example `"U+0430": "U+0061"` with comment `Cyrillic 'а' → Latin 'a'`. The U+0430 is indeed Cyrillic small letter A (а, not to be confused with Latin a). This is correct.

## Bugs Identified

| Bug | Location | Severity | Description |
|-----|----------|----------|-------------|
| Multi-codepoint confusables in reverse index | unicode_tools.py:260-275 | Low | The `_build_reverse_index()` function adds source characters to each target codepoint individually. For multi-codepoint substitutions like U+00C6 (Æ) → U+0041 U+0045 (AE), 'Æ' appears in both reverse_confusables('A') and reverse_confusables('E'). This is technically correct (Æ decomposes to A+E) but may cause confusion when 'Æ' is treated as confusable with a single 'A' or 'E' rather than the 'AE' sequence. This is a design trade-off, not a bug per se. |

## Improvements Surface

| Area | Priority | Description |
|------|----------|-------------|
| Reverse index design | Low | The current reverse_confusables() implementation returns source characters that map to ANY of the target codepoints in a multi-codepoint substitution. For true "what looks like this character" semantics, this works fine. However, if the use case requires knowing whether a character is confusable with a specific single character vs a multi-character sequence, additional logic would be needed. Consider documenting this behavior explicitly in the docstring. |
| Performance | Low | The reverse_confusables() function builds the full reverse index on first call. For large confusables tables, this is a one-time cost. The @lru_cache(maxsize=1) ensures subsequent calls are cached. This is already optimal. |
| Memory | Low | The reverse index stores lists of characters for each target codepoint. With 6565 entries and many potential duplicates across multi-codepoint targets, memory usage is O(n) where n is the total number of target codepoint entries. Currently acceptable. |

## Notes

- All 23 documented constants, structures, and functions match between architecture/confusables.md and the implementation.
- The confusables table is correctly auto-generated from Unicode confusables.txt (UTS #39).
- The confusables.py file is properly structured as a data-only file with no business logic.
- The ConfusableInfo TypedDict is correctly defined in unicode_tools.py, not confusables.py.
- The detect_confusables() function correctly identifies homoglyph attacks (e.g., Cyrillic 'а' in "pаypal").
- The reverse_confusables() function correctly returns all characters that map to a given target.
- The generator script supports caching for reproducible builds.
- The generator script supports version-pinned downloads via get_confusables_url(version).
- No security issues identified - the implementation is a straightforward lookup table.
- Overall the documentation is highly accurate and comprehensive. No major discrepancies between architecture/confusables.md and eggcalc/exact/confusables.py, eggcalc/exact/unicode_tools.py.
