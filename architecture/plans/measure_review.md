# measure.py Architecture Review

## Verified Claims

1. **Purpose**: Text metrics (line, word, character) - MATCHES (lines 1-6)
2. **`line_metrics()`**: Function exists (line 65), returns line count, nonempty/blank, max line length, trailing whitespace, newline style, ends_with_newline - MATCHES
3. **`word_metrics()`**: Function exists (line 127), returns word count, unique words, sentences estimate, paragraphs, average word length - MATCHES
4. **`char_category_metrics()`**: Function exists (line 200), breaks down by Unicode categories - MATCHES
5. **LineMetrics**: lines, nonempty_lines, blank_lines, max_line_length_codepoints, trailing_whitespace_lines, newline_style, ends_with_newline - MATCHES (lines 14-22)
6. **WordMetrics**: words, unique_words_casefolded, sentences_estimate, paragraphs, average_word_length - MATCHES (lines 25-31)
7. **CharCategoryMetrics**: letters, digits, punctuation, symbols, spaces, control_chars, combining_marks - MATCHES (lines 34-42)
8. **Unicode category classification**: Letters (L*), Digits (Nd), Punctuation (P*), Symbols (S*), Spaces (Z*), Control (C*), Combining marks (M*) - MATCHES (lines 223-240)
9. **Newline style detection algorithm**: LF, CRLF, CR, mixed, none - MATCHES (lines 45-62)

## Discrepancies

1. **Doc example error**:
   - Lines 49-52 show `WordMetrics(words=3, unique_words_casefolded=2, max_word_length=5, avg_word_length=5.0)`
   - But actual `WordMetrics` does NOT have `max_word_length` field, only `average_word_length`
   - This is a documentation bug - max_word_length doesn't exist in the code

2. **Data structure types**:
   - Architecture doc uses `@dataclass class XxxMetrics(NamedTuple)`
   - Code uses `class XxxMetrics(TypedDict)`
   - Functionally similar but documentation is inconsistent with implementation

3. **Average word length rounding**:
   - Code rounds average to 2 decimal places (line 196)
   - Doc shows `5.0` which is fine but doesn't mention rounding behavior

## Bugs Found

No bugs in code. Documentation error only.

## Improvements

1. **High Priority**: Fix architecture doc example - remove `max_word_length=5` from word_metrics example since this field doesn't exist
2. **Low Priority**: Update architecture doc to use TypedDict instead of NamedTuple for data structures
3. **Low Priority**: Document that average_word_length is rounded to 2 decimal places

## Priority

- **High**: Fix WordMetrics example in documentation
- **Low**: Documentation style improvements (TypedDict vs NamedTuple)