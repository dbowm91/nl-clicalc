# measure.py Module Review — Improvement Plan

**Reviewed:** architecture/measure.md against nl_calc/exact/measure.py
**Date:** 2026-05-28

## Verified Claims (with line references)

- `line_metrics(text: str) -> LineMetrics` — VERIFIED at code line 66
- `word_metrics(text: str) -> WordMetrics` — VERIFIED at code line 128
- `char_category_metrics(text: str) -> CharCategoryMetrics` — VERIFIED at code line 200
- TypedDict classes `LineMetrics`, `WordMetrics`, `CharCategoryMetrics` — VERIFIED at code lines 15, 26, 35
- `LineMetrics` fields (lines, nonempty_lines, blank_lines, max_line_length_codepoints, trailing_whitespace_lines, newline_style, ends_with_newline) — VERIFIED at code lines 17-23
- `WordMetrics` fields (words, unique_words_casefolded, sentences_estimate, paragraphs, average_word_length) — VERIFIED at code lines 28-32
- `CharCategoryMetrics` fields (letters, digits, punctuation, symbols, spaces, control_chars, combining_marks) — VERIFIED at code lines 37-43
- Cf (format) characters intentionally excluded from control_chars count per UTS #55 — VERIFIED at code lines 234-235
- `average_word_length` rounded to 2 decimal places — VERIFIED at code line 196 (uses `round(avg_word_length, 2)`)
- Word definition as sequences of non-whitespace characters — VERIFIED at code line 151 (`s.split()`) and 154 (filters tokens without letters)
- Newline style values ("LF", "CRLF", "CR", "mixed", "none") — VERIFIED at code lines 52-63 and doc comment at line 22

## Discrepancies Between Documentation and Code

- [MEDIUM] **Newline detection algorithm does not match documented steps**
  - Documentation says: Steps 1-4 at docs lines 99-102 describe a simple sequential check if \r\n → "CRLF", else if \r → "CR", else if \n → "LF", else "none"
  - Code actually does: Lines 52-55 FIRST check for "mixed" when CRLF coexists with standalone CR or LF, which is missing from reported algorithm
  - Impact: Documentation underreports "mixed" detection complexity. For a string like "hello\r\nworld\n", docs would say "CRLF" but code returns "mixed" at line 52 because has_crlf AND standalone_lf > 0

## Potential Bugs

- [LOW] **`max_line_length_codepoints` names suggest codepoint count but uses `len(line)`**
  - Location: `nl_calc/exact/measure.py:104`
  - Issue: `len(line)` in Python returns character count (Unicodescalar values), not necessarily codepoints for strings containing supplementary characters (characters outside BMP). For example, emoji like "😀" (U+1F600) is 2 code units (surrogate pair) but 1 codepoint. However, in Python 3, `len()` on a str returns the number of characters (Unicode scalar values), not UTF-16 code units. So technically `len()` returns codepoint-like behavior for most cases, but "character" would be more accurate terminology
  - The documentation calls it `max_line_length_codepoints` which is technically correct for Python 3 str semantics, but could be misleading

- [LOW] **No validation or error handling for None input**
  - Location: `nl_calc/exact/measure.py:66, 128, 200`
  - Issue: Functions pass type annotation `s: str` but don't validate `s is not None`. Passing `None` would cause `AttributeError` at runtime rather than a clear error message
  - Suggested investigation: Consider adding `if s is None: raise TypeError("text must be a string")` or similar guard

## Improvement Suggestions

### MEDIUM Priority
- **Fix newline style detection algorithm documentation** (architecture/measure.md lines 98-102)
  - Add explicit "mixed" detection step showing that CRLF + standalone CR or LF → "mixed"
  - Restructure algorithm description to match code logic at measure.py lines 46-63

### LOW Priority
- **Add type validation** at measure.py lines 66, 128, 200 for None input
  - Consider raising a clear TypeError if None is passed

## Summary

The measure.py module documentation accurately describes the public API structure (TypedDict schemas, function signatures, return types) and correctly notes the Cf exclusion per UTS #55. The main discrepancy is that the newline detection algorithm description in architecture/measure.md does not capture the "mixed" detection logic that runs before the simple "CRLF/CR/LF/none" checks at code lines 56-63. There are no functional bugs in the code, but the documentation should be updated to reflect the actual detection priority. Minor improvement would be adding None input validation.
