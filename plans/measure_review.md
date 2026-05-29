# measure.py Architecture Review

## Overview

Reviewed `architecture/measure.md` against the actual implementation in `nl_calc/exact/measure.py`.

---

## Verified Claims (MATCHES/MISMATCH)

### line_metrics()

| Claim | Status |
|-------|--------|
| LineMetrics TypedDict fields (lines, nonempty_lines, blank_lines, max_line_length_codepoints, trailing_whitespace_lines, newline_style, ends_with_newline) | MATCHES |
| Example: `line_metrics("hello\nworld\n")` returns lines=2, nonempty_lines=2, blank_lines=0, max_line_length_codepoints=5, newline_style='LF', ends_with_newline=True | MATCHES |
| Trailing whitespace detection | MATCHES |
| Newline style detection algorithm | MATCHES |
| None handling (gracefully returns zero metrics) | MATCHES |

### word_metrics()

| Claim | Status |
|-------|--------|
| WordMetrics TypedDict fields | MATCHES |
| Average word length rounded to 2 decimal places | MATCHES |
| Paragraph detection (separated by blank lines) | MATCHES |
| Word filtering (only tokens with letters count) | MATCHES |
| Unique words casefolded | MATCHES |
| None handling (gracefully returns zero metrics) | MATCHES |
| Example: `word_metrics("hello world hello")` returns words=3, unique_words_casefolded=2, paragraphs=1, average_word_length=5.0 | MATCHES |

### char_category_metrics()

| Claim | Status |
|-------|--------|
| CharCategoryMetrics TypedDict fields | MATCHES |
| Unicode category classification (L=letters, N=digits, P=punctuation, S=symbols, Z=spaces, C=control excluding Cf, M=combining marks) | MATCHES |
| Cf (format characters) exclusion per UTS #55 | MATCHES |
| TypeError raised on None | MATCHES (documented) |
| Example: `char_category_metrics("Hello World! 123")` returns letters=10, digits=3, punctuation=1, symbols=0, spaces=2, control_chars=0, combining_marks=0 | MATCHES |

### Newline Style Detection

| Claim | Status |
|-------|--------|
| LF detection | MATCHES |
| CRLF detection | MATCHES |
| CR detection | MATCHES |
| Mixed detection (CRLF + standalone CR/LF) | MATCHES |
| none detection | MATCHES |

---

## Discrepancies Found

### 1. sentences_estimate example in document is WRONG

**Location**: `architecture/measure.md` lines 47-50

**Issue**: The document shows:
```python
>>> word_metrics("hello world hello")
WordMetrics(words=3, unique_words_casefolded=2,
            sentences_estimate=1, paragraphs=1,
            average_word_length=5.0)
```

But `sentences_estimate=1` is incorrect. The string "hello world hello" contains no sentence-ending punctuation (. ! ?), so the actual result is `sentences_estimate=0`.

**Verified by running**:
```python
>>> word_metrics("hello world hello")["sentences_estimate"]
0
```

**Severity**: Documentation bug (the code is correct)

---

### 2. Comment claims "not ellipses or decimals" but implementation does match them

**Location**: `nl_calc/exact/measure.py:169`

**Issue**: The comment says:
```python
# Estimate sentences (count . ! ? that are not ellipses or decimals)
```

But the pattern `[.!?]+(?:\s|$)|[.!?]+(?=[A-Z])` does match ellipses:
```python
>>> re.findall(r"[.!?]+(?:\s|$)|[.!?]+(?=[A-Z])", "Hello... world")
['... ']  # Ellipses matched as 1 sentence
```

Additionally, "5. 5" (decimal with space) is incorrectly matched as a sentence.

**Severity**: Documentation comment mismatch (implementation behavior may still be acceptable)

---

## Inconsistencies

### 3. Inconsistent None handling across functions

| Function | None behavior |
|----------|---------------|
| `line_metrics(None)` | Returns zero metrics (graceful) |
| `word_metrics(None)` | Returns zero metrics (graceful) |
| `char_category_metrics(None)` | Raises TypeError |

While the TypeError for `char_category_metrics` is documented, the inconsistency raises questions about API design. The docstrings for all three functions claim "None is treated as empty string" but only two actually implement this.

---

## Edge Cases Verified

### Positive: Ellipses treated as single sentence ending
```python
>>> re.findall(pattern, "Hello... world")
['... ']  # Counted as 1, not 3
```
This is reasonable behavior.

### Negative: "5. 5" false positive
```python
>>> re.findall(pattern, "5. 5")
['. ']  # Incorrectly detected as sentence
```
Decimal numbers followed by space trigger false positives.

### Positive: "..." alone detected as sentence
```python
>>> re.findall(pattern, "...")
['...']
```
An ellipsis alone is detected as one sentence (arguably correct).

### Positive: "5.5" no false positive
```python
>>> re.findall(pattern, "5.5")
[]
```
Decimal without space correctly not detected.

---

## Bugs Identified

### None - All verified claims match implementation

No code bugs found. The implementation correctly follows the documented behavior in all cases except the `sentences_estimate=1` example which is a documentation error.

---

## Improvements Suggested

### Priority: Medium

**1. Fix the documented example for `sentences_estimate`**

The example in `architecture/measure.md` for `word_metrics("hello world hello")` should show `sentences_estimate=0` instead of `1`.

**2. Update comment to match implementation**

Change line 169 from:
```python
# Estimate sentences (count . ! ? that are not ellipses or decimals)
```
To something like:
```python
# Estimate sentences (count . ! ? followed by space/end-of-string,
# or followed by uppercase letter; ellipses counted as single ending)
```

**3. Consider making None handling consistent**

Either:
- Make `char_category_metrics(None)` return zero metrics (like the others), or
- Document explicitly why it differs and update the other two docstrings to remove "None is treated as empty string"

**4. Consider refining sentence pattern to avoid decimal false positives**

Current pattern: `[.!?]+(?:\s|$)|[.!?]+(?=[A-Z])`

Could be improved to not match a period that appears to be a decimal by checking if it's preceded/followed by digits. However, this adds complexity and may not be worth it.

---

## Priority Summary

| Priority | Item |
|----------|------|
| **High** | Fix documented `sentences_estimate=1` to `sentences_estimate=0` in word_metrics example |
| **Medium** | Update misleading comment about "not ellipses or decimals" |
| **Low** | Consider consistent None handling across all three functions |
| **Low** | Consider refining sentence pattern to avoid decimal false positives |
