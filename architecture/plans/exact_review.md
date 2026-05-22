# exact.md Architecture Review

## Verified Claims

1. **exact/__init__.py re-exports**: All documented re-exports exist in nl_calc/exact/__init__.py - MATCHES
2. **primitives.py functions**: All documented (utf8_bytes, codepoints, normalize_unicode, casefold_text, raw_equal, normalized_equal, measure_basic, count_graphemes, truncate_to_grapheme, find_invisibles, visible_repr) - MATCHES
3. **unicode_tools functions**: unicode_script, unicode_scripts, detect_mixed_scripts, detect_confusables, confusables_count - MATCHES
4. **diff functions**: first_diff, common_prefix_suffix, levenshtein_distance, diff_spans, longest_common_subsequence - MATCHES
5. **validate functions**: check_brackets, validate_json, regex_test - MATCHES
6. **measure functions**: line_metrics, word_metrics, char_category_metrics - MATCHES
7. **synthesis functions**: measure_text, text_equal, inspect_text, explain_diff, count_chars, list_compare - MATCHES
8. **Module structure**: All files present (primitives.py, unicode_tools.py, measure.py, diff.py, validate.py, synthesis.py, confusables.py) - MATCHES
9. **Architecture diagram**: Shows correct dependencies - MATCHES
10. **TypedDict convention**: Code uses TypedDict throughout - MATCHES

## Discrepancies

1. **CheckBracketsResult structure - MAJOR DISCREPANCY**:
   - **Doc shows** (lines 234-241): balanced, message, position, expected, found
   - **Code uses** (validate.py lines 29-33): balanced, unmatched_openers, unmatched_closers
   - These are completely different structures

2. **RegexTestResult structure - MAJOR DISCREPANCY**:
   - **Doc shows** (lines 247-255): valid, error, match_count, matches, non_matches
   - **Code uses** (validate.py lines 60-64): valid_pattern, results (list[RegexMatch]), error
   - Code returns array of RegexMatch objects, not separate match/nonmatch lists

3. **RegexMatch in doc vs code**:
   - Doc doesn't define RegexMatch but code does (validate.py lines 50-57)
   - RegexMatch has: sample, matches, fullmatch, span, groups, groupdict

4. **LineMetrics structure mismatch**:
   - **Doc shows** (lines 173-178): count, newline_style, has_trailing_newline, blank_lines
   - **Code uses** (measure.py lines 15-23): lines, nonempty_lines, blank_lines, max_line_length_codepoints, trailing_whitespace_lines, newline_style, ends_with_newline
   - Completely different fields

5. **MeasureBasic fields - minor**:
   - Doc shows (lines 107-114): bytes_utf8, codepoints, graphemes_estimate, chars_no_whitespace, ascii, non_ascii
   - Code matches exactly (primitives.py lines 307-314)

6. **Synthesis classification labels**:
   - Doc shows "accent_or_diacritic_difference" but code uses "case_only" (see synthesis_review.md)

## Bugs Found

1. **BUG in validate.py line 36**: `CheckBracketsResult.__slots__ = ['balanced', 'unmatched_openers', 'unmatched_closers']`
   - TypedDict classes do NOT support `__slots__`
   - This will raise an error at runtime if accessed

## Improvements

1. **High Priority**: Fix CheckBracketsResult documentation to match actual structure (unmatched_openers/closers)
2. **High Priority**: Fix RegexTestResult documentation to reflect actual structure (valid_pattern, results list)
3. **High Priority**: Fix LineMetrics documentation - completely wrong structure
4. **High Priority**: Remove invalid `__slots__` from CheckBracketsResult (validate.py line 36)
5. **Low Priority**: Document RegexMatch structure since code uses it

## Priority

- **High**: Fix all data structure documentation errors in exact.md
- **High**: Remove invalid __slots__ from CheckBracketsResult
- **Low**: Minor documentation clarifications