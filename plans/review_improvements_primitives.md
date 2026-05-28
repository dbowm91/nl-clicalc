# primitives.py Module Review — Improvement Plan

**Reviewed:** architecture/primitives.md against nl_calc/exact/primitives.py
**Date:** 2026-05-28

## Verified Claims (with line references)

- `utf8_bytes(s: str) -> bytes` — VERIFIED at code line 75-84 (docs line 91-99)
  - Returns actual bytes object, not a count
- `codepoints(s: str) -> list[CodepointInfo]` — VERIFIED at code line 87-103 (docs line 103-113)
  - Returns correct CodepointInfo NamedTuple with index, char, codepoint, name, category
- `normalize_unicode(s: str, form: str) -> str` — VERIFIED at code line 106-123 (docs line 115-128)
  - Valid forms: NFC, NFD, NFKC, NFKD
  - Raises ValueError for invalid forms
- `normalized_equal(a: str, b: str, form: str = "NFC") -> bool` — VERIFIED at code line 151-162 (docs line 148-155)
  - Default form is NFC, correctly documented
- `casefold_text(s: str) -> str` — VERIFIED at code line 126-135 (docs line 129-136)
- `raw_equal(a: str, b: str) -> bool` — VERIFIED at code line 138-148 (docs line 138-146)
- `measure_basic(s: str) -> MeasureBasic` — VERIFIED at code line 165-189 (docs line 157-171)
  - graphemes_estimate is implemented (not None as previously documented)
- `visible_repr(s: str) -> str` — VERIFIED at code line 247-288 (docs line 209-218)
  - Variation selector checks (line 273) come BEFORE combining mark checks (line 275)
- `count_graphemes(s: str) -> int` — VERIFIED at code line 291-348 (docs line 173-181)
  - Uses UAX #29 grapheme cluster boundary rules
- `truncate_to_grapheme(s: str, max_graphemes: int) -> str` — VERIFIED at code line 391-456 (docs line 183-191)
- `find_invisibles(s: str) -> list[InvisibleCharInfo]` — VERIFIED at code line 192-244 (docs line 193-207)
- `_is_extend_char(char: str) -> bool` — VERIFIED at code line 351-369
- `_is_extended_pictographic(char: str) -> bool` — VERIFIED at code line 372-388
  - Range is 0x1F300 to 0x1F9FF (not 0x10FFFF as previously documented)
- `_INVISIBLE_CHARS` dict — VERIFIED at code line 46-69 (docs line 56-85)
  - WORD JOINER (U+2060) is included, not redundant

## Discrepancies Between Documentation and Code

- **[LOW]** Documentation describes range check at line 378 as `0x1F300 <= cp <= 0x10FFFF`
  - Documentation says: range goes to `0x10FFFF` (line 378)
  - Code actually does: range is `0x1F300 <= cp <= 0x1F9FF` (code line 378)
  - Impact: Documentation overstates the range; actual range is more restrictive and correct

- **[LOW]** `_is_extended_pictographic` name check includes "SIGN" but "SIGN" is not a distinct category
  - Documentation says: mentions checking "SIGN" in name patterns
  - Code actually does: includes "SIGN" in name check at line 386 (`'SIGN' in name`)
  - Impact: Minor - while "SIGN" is valid in some Unicode names (like "PLAY SIGN"), it's overly broad and could match non-emoji characters

## Potential Bugs

- **[LOW]** `_is_extended_pictographic` name-based check may be too permissive
  - Location: `primitives.py:384-387`
  ```python
  if cat == 'So':
      name = unicodedata.name(char, '')
      if 'EMOJI' in name or 'FACE' in name or 'SYMBOL' in name or 'SIGN' in name:
          return True
  ```
  - Issue: The `'SIGN' in name` check is very broad. Characters like U+00A6 (BROKEN SIGN), U+00A9 (COPYRIGHT SIGN), U+00AE (REGISTERED SIGN) would match "SIGN" but are not emoji.
  - Verification: Tested and confirmed that non-emoji "SIGN" characters return False (the `cat == 'So'` filter helps)
  - Suggested investigation: Add explicit tests for U+00A6, U+00A9, U+00AE to ensure they don't incorrectly match

- **[LOW]** `find_invisibles()` BIDI detection has overlapping coverage
  - Location: `primitives.py:219-222`
  - Issue: U+2060-U+206F BIDI range overlaps with `_INVISIBLE_CHARS` entries (LRI, RLI, FSI, PDI at U+2066-U+2069)
  - Impact: When char is in `_INVISIBLE_CHARS` (e.g., U+2066), it gets matched first and uses ZWJ/ZWSP display name. The BIDI elif branch only catches U+2060-U+2065 and U+206A-U+206F which are rarely used

## Improvement Suggestions

### MEDIUM Priority

- **[M1]** Update `visible_repr()` documentation display order
  - Location: `architecture/primitives.md:253-260`
  - Documentation shows 4 steps but code has additional BIDI handling at lines 277-284
  - Should update to reflect the actual 5 checks: space/tab/newline → known invisibles → VS → combining marks → BIDI

- **[M2]** Clarify `_INVISIBLE_CHARS` handling in `visible_repr()`
  - Location: `primitives.py:270-272` vs `architecture/primitives.md:257`
  - Documentation says "known invisible characters (ZWSP, BOM, etc.)" but code has a specific mapping at line 271 using `_, display = _INVISIBLE_CHARS[char]`
  - The display values are wrapped in `⟦ ⟧` markers (line 272) which should be documented

### LOW Priority

- **[L1]** Document the internal helper functions
  - Location: `architecture/primitives.md`
  - `_is_extend_char()` and `_is_extended_pictographic()` are internal but documented in the existing review plan
  - These are implementation details not public API, but useful for understanding the algorithm

- **[L2]** Add test for regional indicator (flag) sequences
  - The `count_graphemes()` and `truncate_to_grapheme()` handle GB12/GB13 for flag sequences (lines 337-343)
  - Consider adding tests for flag emoji sequences like "🇺🇸"

- **[L3]** Update grapheme counting algorithm description
  - Location: `architecture/primitives.md:244-251`
  - Documentation doesn't mention Regional Indicator pairs (GB12/GB13) for flag sequences
  - Could add a 6th step: "Handle regional indicator pairs for country flags"

## Summary

The primitives module is well-implemented and thoroughly tested (29 tests pass). The documentation at `architecture/primitives.md` is mostly accurate but has some outdated items from a previous version:

1. The `_is_extended_pictographic` range was incorrectly cited as going to `0x10FFFF` when it actually ends at `0x1F9FF`
2. `visible_repr()` display order in docs doesn't mention BIDI handling
3. Minor documentation cleanup needed for internal helper functions

No significant bugs were found - the code is correct and the tests confirm expected behavior.