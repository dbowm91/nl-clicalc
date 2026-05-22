# measure.py Architecture Review

## Summary

The `measure.py` module (`nl_calc/exact/measure.py`) provides text measurement primitives for analyzing line structure, word structure, and Unicode character categories. It is exported via `nl_calc/exact/__init__.py` and forms part of the low-level Unicode text primitives layer.

## Verified Claims

The following claims from `architecture/measure.md` match the implementation:

1. **line_metrics function** - Returns correct structure with `lines`, `nonempty_lines`, `blank_lines`, `max_line_length_codepoints`, `newline_style`, and `ends_with_newline`.

2. **word_metrics function** - Returns `words`, `unique_words_casefolded`, and `average_word_length` (field named `average_word_length` vs doc's `avg_word_length`).

3. **char_category_metrics function** - Correctly categorizes characters by Unicode general categories (L*, N*, P*, S*, Z*, C*, M*).

4. **Line counting logic** - Correctly uses `splitlines()` and counts nonempty vs blank lines.

5. **Empty string handling** - All three functions properly handle empty strings.

6. **Codepoint counting** - `len(line)` correctly returns Unicode codepoints in Python 3.

## Issues Found

### Issue 1: CRITICAL - Newline Detection Bug (line 52)

**Location**: `nl_calc/exact/measure.py:52`

**Problem**: The `mixed` newline detection condition is malformed:

```python
if has_crlf and ((has_cr and "\r" not in "\n") or (has_lf and "\n" not in "\r")):
```

This checks if literal string `"\n"` is not in string `"\r"`, which is always `True` since they are different single characters. The intended logic was to detect if LF exists *outside* of a CRLF sequence.

**Impact**:
- Any text with CRLF (`\r\n`) is incorrectly reported as `"mixed"` even when no other newline types exist
- `"hello\r\nworld"` returns `newline_style="mixed"` instead of `"CRLF"`
- This contradicts the documented detection algorithm which says: "If text contains \r\n → 'CRLF'"

**Evidence**:
```python
>>> line_metrics("hello\r\nworld\r\n")["newline_style"]
'mixed'  # Should be "CRLF"
```

### Issue 2: MAJOR - `mixed` Newline Style Not Documented

**Location**: `architecture/measure.md` and `nl_calc/exact/measure.py:52-53`

**Problem**: The `newline_style` field can return `"mixed"` but this value is not documented in `architecture/measure.md`. The documented detection algorithm (lines 96-100) only mentions LF, CRLF, CR, and none - no `mixed`.

### Issue 3: MINOR - WordMetrics Field Name Mismatch

**Location**: `nl_calc/exact/measure.py:31` vs `architecture/measure.md:41`

**Problem**: Document specifies `avg_word_length` but code has `average_word_length`.

```python
# Doc: avg_word_length
# Code: average_word_length
```

### Issue 4: MINOR - `max_word_length` Missing from Implementation

**Location**: `nl_calc/exact/measure.py:25-32` vs `architecture/measure.md:40`

**Problem**: Document specifies `max_word_length: int` in `WordMetrics` but the implementation does not include this field. The code computes `average_word_length` but not the maximum word length.

### Issue 5: MINOR - Word Definition Not Enforced

**Location**: `nl_calc/exact/measure.py:153` vs `architecture/measure.md:44`

**Problem**: Document says word definition is "Sequences of non-whitespace characters", but code filters out tokens without letters:

```python
words = [t for t in tokens if any(c.isalpha() for c in t)]
```

This means `"123"` and `"!!!"` would not be counted as words, contradicting the documented definition.

### Issue 6: MINOR - `trailing_whitespace_lines` Not Documented

**Location**: `nl_calc/exact/measure.py:20` vs `architecture/measure.md:19`

**Problem**: `LineMetrics` includes `trailing_whitespace_lines: list[int]` but this field is not documented in `architecture/measure.md`.

### Issue 7: MINOR - `sentences_estimate` and `paragraphs` Not Documented

**Location**: `nl_calc/exact/measure.py:29-30` vs `architecture/measure.md:31-49`

**Problem**: `WordMetrics` includes `sentences_estimate` and `paragraphs` fields but these are not documented in `architecture/measure.md`.

## Improvement Recommendations

### Recommendation 1: Fix Newline Detection Bug

**File**: `nl_calc/exact/measure.py:45-62`

Replace the broken condition at line 52 with correct logic:

```python
# Current (broken):
if has_crlf and ((has_cr and "\r" not in "\n") or (has_lf and "\n" not in "\r")):
    return "mixed"

# Fixed approach - detect standalone LF or CR outside CRLF:
# A standalone LF is one that's not preceded by \r
# A standalone CR is one that's not followed by \n
```

The detection algorithm should follow the documented rules:
1. If `\r\n` exists → "CRLF" (unless mixed with other types)
2. If standalone `\r` exists (not followed by `\n`) → "CR"
3. If standalone `\n` exists → "LF"
4. If multiple types exist → "mixed"
5. Otherwise → "none"

### Recommendation 2: Update Documentation

**File**: `architecture/measure.md`

Add the undocumented fields and clarify the detection algorithm:
- Add `trailing_whitespace_lines` to LineMetrics
- Add `sentences_estimate` and `paragraphs` to WordMetrics
- Document the `mixed` newline style
- Clarify the word definition vs implementation behavior

### Recommendation 3: Add `max_word_length` Field

**File**: `nl_calc/exact/measure.py:157-166`

Compute and return `max_word_length` to match documented interface:

```python
# After line 158, compute max_word_length:
max_word_length = max(len(w) for w in words) if words else 0
```

### Recommendation 4: Align Word Definition with Documentation

**File**: `nl_calc/exact/measure.py:153`

Either update the documentation to match the implementation (count only word-like tokens with letters), or update the implementation to count all whitespace-separated tokens as words.

### Recommendation 5: Align Field Names with Documentation

**File**: `nl_calc/exact/measure.py:31`

Rename `average_word_length` to `avg_word_length` to match the documented interface.

## Test Coverage Assessment

The test suite in `tests/test_exact.py:465-524` covers the measure functions but:
- `test_line_metrics_crlf` (line 476-478) accepts both "CRLF" and "mixed" due to the bug
- No tests verify the documented behavior that CRLF alone should return "CRLF"
- No tests for `trailing_whitespace_lines` field
- No tests for `sentences_estimate` or `paragraphs` fields

## Conclusion

The measure module has a critical bug in newline detection that causes all CRLF text to be misclassified as "mixed". Additionally, there are several documentation/implementation mismatches regarding field names, missing fields, and undocumented features. The implementation is functionally correct for the core metrics but the API surface does not match the documentation.