# exact/ Module Review — Improvement Plan

**Reviewed:** architecture/exact.md against nl_calc/exact/__init__.py and nl_calc/exact/*.py
**Date:** 2026-05-28

## Verified Claims (with line references)
- `utf8_bytes(s)` returns `bytes` — VERIFIED at primitives.py:75 (docs line 60)
- `codepoints(s)` returns `list[CodepointInfo]` — VERIFIED at primitives.py:87 (docs line 61)
- `normalize_unicode(s, form)` — VERIFIED at primitives.py:106 (docs line 62)
- `casefold_text(s)` — VERIFIED at primitives.py:126 (docs line 63)
- `raw_equal(a, b)` — VERIFIED at primitives.py:138 (docs line 64)
- `normalized_equal(a, b)` — VERIFIED at primitives.py:151 (docs line 65)
- `count_graphemes(s)` — VERIFIED at primitives.py:291 (docs line 67)
- `find_invisibles(s)` — VERIFIED at primitives.py:192 (docs line 69)
- `unicode_script(char)` — VERIFIED at unicode_tools.py:119 (docs line 125)
- `unicode_scripts(s)` — VERIFIED at unicode_tools.py:138 (docs line 126)
- `detect_mixed_scripts(s)` — VERIFIED at unicode_tools.py:150 (docs line 127)
- `detect_confusables(s)` — VERIFIED at unicode_tools.py:187 (docs line 128)
- `confusables_count(s)` — VERIFIED at unicode_tools.py:233 (docs line 129)
- `_get_script_heuristic()` has `@functools.lru_cache` — VERIFIED at unicode_tools.py:72 (docs line 379)
- Cf (format) characters excluded from control_chars — VERIFIED at measure.py:234 (docs line 380)
- `CodepointInfo` uses NamedTuple — VERIFIED at primitives.py:16 (docs line 384)
- `MeasureBasic` uses TypedDict — VERIFIED at primitives.py:25 (docs line 384)
- All diff functions match documented signatures — VERIFIED at diff.py
- All validate functions match documented signatures — VERIFIED at validate.py

## Discrepancies Between Documentation and Code

### [MEDIUM] `reverse_confusables` is undocumented in public API
- **Documentation says:** Not listed in public API exports (architecture/exact.md lines 24-47)
- **Code actually does:** Exported in `__init__.py:52` and documented in unicode_tools.py docstring
- **Impact:** Users of the exact/ module cannot discover this function from documentation

### [MEDIUM] `truncate_to_grapheme` parameter name mismatch
- **Documentation says:** `truncate_to_grapheme(s, max_len)` (architecture/exact.md line 68)
- **Code actually does:** `truncate_to_grapheme(s: str, max_graphemes: int)` at primitives.py:391
- **Impact:** Minor confusion; `max_len` in docs but `max_graphemes` in code

### [MEDIUM] Invisible characters list incomplete in documentation
- **Documentation says:** 10 characters shown (architecture/exact.md lines 75-89)
- **Code actually does:** 23 characters in `_INVISIBLE_CHARS` dict (primitives.py:46-69)
- **Missing from docs:** U+180e (MVS), U+034f (CGJ), U+202b-202e (RLE, PDF, LRO, RLO), U+2066-2069 (LRI, RLI, FSI, PDI)
- **Impact:** Users may not be aware of all detectable invisible characters

### [LOW] `visible_repr()` display order claim is incorrect
- **Documentation says:** "Variation selector checks must come BEFORE combining mark checks" (architecture/exact.md line 378)
- **Code actually does:** Lines 273-276 check VS first (line 273), then combining marks (line 275) — code is correct, but the doc framing implies this was a deliberate design choice
- **Impact:** Documentation doesn't match the actual implementation logic (though result is correct)

### [LOW] `first_diff` missing from architecture doc public API
- **Documentation says:** Not listed in public API table (architecture/exact.md lines 24-47)
- **Code actually does:** Exported at `__init__.py:71` and in public API `__all__` at line 117
- **Impact:** Function is not documented as part of the public API

### [LOW] `CommonPrefixSuffix` missing from architecture doc
- **Documentation says:** Not mentioned in docstring examples (architecture/exact.md lines 210-221)
- **Code actually does:** Defined at diff.py:38-41 and used in synthesis.py
- **Impact:** Return type not documented

### [LOW] TypedDict vs documented structure mismatches
- **Documentation says:** Various TypedDict structures shown in architecture/exact.md
- **Code actually does:** Some fields differ (e.g., `CheckBracketsResult.unmatched_openers` uses `BracketError` with line/column not position only; `RegexMatch` has `fullmatch`, `span`, `groupdict` not documented)
- **Impact:** Documentation is incomplete for some return type structures

## Potential Bugs

### [MEDIUM] `_is_extended_pictographic()` codepoint range may over-match
- **Location:** `primitives.py:372-388`
- **Issue:** Line 378 checks `0x1F300 <= cp <= 0x1F9FF` and returns True immediately if in range. The subsequent category (`cat == 'So'`) and name checks (lines 383-387) only run if the codepoint is NOT in range. This means any character in that range (including non-emoji symbols like ☀ U+2600) is classified as pictographic.
- **Suggested investigation:** Test with symbols like ☀ (BLACK SUN WITH RAYS) or �Ⅱ (MUSIC NOTE) to see if they're incorrectly treated as emoji. Consider whether this matters for nl-clicalc's use case.

### [LOW] `detect_mixed_scripts()` return type is `dict` not TypedDict
- **Location:** `unicode_tools.py:150`
- **Issue:** Function returns a `dict` directly rather than a typed structure. This is inconsistent with other functions that return TypedDict types like `ConfusableInfo`.
- **Suggested investigation:** Consider creating a `MixedScriptsResult` TypedDict for consistency.

### [LOW] `visible_repr()` combining mark check order issue
- **Location:** `primitives.py:273-276`
- **Issue:** VS check (line 273: `0xfe00 <= ord(char) <= 0xfe0f`) comes before combining mark check (line 275: `unicodedata.category(char).startswith("M")`). If a VS is followed by a combining mark, they would be processed separately rather than together.
- **Suggested investigation:** Verify this doesn't cause display issues with VS+combining mark sequences.

### [LOW] `list_compare()` returns plain dict
- **Location:** `synthesis.py:622-727`
- **Issue:** Returns `dict` instead of a TypedDict like other synthesis functions. Return type hint at line 625 says `-> dict` but could be more specific.
- **Suggested investigation:** Consider creating a `ListCompareResult` TypedDict for consistency and better type safety.

## Improvement Suggestions

### HIGH Priority
- Add `reverse_confusables` to the documented public API in architecture/exact.md (lines 24-47)
- Add `first_diff` and `CommonPrefixSuffix` to documented public API
- Update invisible characters list (lines 75-89) to include all 23 characters in `_INVISIBLE_CHARS`

### MEDIUM Priority
- Correct `truncate_to_grapheme` parameter name in docs: `max_len` → `max_graphemes`
- Clarify `visible_repr()` display order claim or verify the code has the documented behavior
- Document `CheckBracketsResult.unmatched_openers/closers` uses `BracketError` with `line` and `column` fields (not just `position`)
- Document `RegexMatch` fields: `fullmatch`, `span`, `groupdict`

### LOW Priority
- Consider adding TypedDict for `detect_mixed_scripts()` return value
- Consider adding TypedDict for `list_compare()` return value
- Add example for `common_prefix_suffix` showing non-overlapping prefix/suffix behavior

## Summary

The exact/ module documentation is generally accurate and well-structured. Most discrepancies are cases where the documentation is incomplete rather than incorrect. The primary issue is that `reverse_confusables` is exported in `__init__.py` but not documented in the architecture file. There are also several TypedDict structures whose fields are only partially documented. The most significant potential bug is in `_is_extended_pictographic()` where the codepoint range check returns early, potentially misclassifying non-emoji symbols as emoji.
