# Measure Module Review - Improvement Plan

## Summary

The `nl_calc/exact/measure.py` module provides text measurement primitives for line metrics, word metrics, and character category metrics. The implementation is well-tested (13 tests pass) and functionally correct. However, several discrepancies between documentation and code were identified.

---

## Verified Claims (with Code References)

### Line Metrics

| Claim | Status | Code Reference |
|-------|--------|----------------|
| `lines` count via `splitlines()` | Verified | `measure.py:88` |
| `nonempty_lines` and `blank_lines` tracking | Verified | `measure.py:106-115` |
| `trailing_whitespace_lines` as 1-based indices | Verified | `measure.py:103` (`enumerate(lines, start=1)`) |
| `max_line_length_codepoints` using `len(line)` | Verified | `measure.py:104` |
| `newline_style` detection (LF/CRLF/CR/mixed/none) | Verified | `measure.py:46-63` |
| `ends_with_newline` detection | Verified | `measure.py:92` |
| Empty string returns zeros | Verified | `measure.py:77-86` |

**Code Reference**: `measure.py:66-125`

### Word Metrics

| Claim | Status | Code Reference |
|-------|--------|----------------|
| Word filtering: only tokens containing letters | Verified | `measure.py:154` (`any(c.isalpha() for c in t)`) |
| Casefolded unique word counting | Verified | `measure.py:159` (`w.casefold()`) |
| `average_word_length` rounded to 2 decimals | Verified | `measure.py:196` (`round(avg_word_length, 2)`) |
| Sentence estimation via regex | Verified | `measure.py:171-173` |
| Paragraph counting (blank line separated) | Verified | `measure.py:176-185` |
| Minimum 1 paragraph if content exists | Verified | `measure.py:188-189` |

**Code Reference**: `measure.py:128-197`

### Char Category Metrics

| Claim | Status | Code Reference |
|-------|--------|----------------|
| Letters: category starts with "L" | Verified | `measure.py:223` |
| Digits: category starts with "N" | Verified | `measure.py:225-226` |
| Punctuation: category starts with "P" | Verified | `measure.py:227-228` |
| Symbols: category starts with "S" | Verified | `measure.py:229-230` |
| Spaces: category starts with "Z" | Verified | `measure.py:231-232` |
| Control chars: Cc, Co, Cn count; Cf excluded | Verified | `measure.py:233-237` |
| Combining marks: category starts with "M" | Verified | `measure.py:238-239` |

**Code Reference**: `measure.py:200-249`

---

## Discrepancies Between Documentation and Code

### 1. **control_chars Documentation Error** (High Priority)

**Location**: `architecture/measure.md:74`

**Documentation states**:
```
Control chars: category starts with "C" (excluding newlines/tabs)
```

**Actual behavior**: Newlines (`\n`, `\r`) and tabs (`\t`) ARE counted as control characters. They have Unicode category `Cc` (Control).

**Code at `measure.py:233-237`**:
```python
elif cat.startswith("C"):  # Other (control, format, etc.)
    if cat == "Cf":  # Format characters (e.g., U+FEFF BOM)
        pass  # Cf excluded from control_chars count per UTS #55
    else:
        control_chars += 1  # Cc, Co, Cn all count
```

**Verification**:
```python
>>> char_category_metrics('\n\t\r')['control_chars']
3  # All counted
```

**Fix**: Update documentation to remove "excluding newlines/tabs" and clarify that Cf (format characters) are the only exclusion per UTS #55.

---

### 2. **Digits Category Documentation** (Medium Priority)

**Location**: `architecture/measure.md:70`

**Documentation states**:
```
Digits: category "Nd"
```

**Actual behavior**: Code uses `cat.startswith("N")` which includes:
- `Nd` (Decimal Number)
- `Nl` (Letter Number)
- `No` (Other Number)

**Code at `measure.py:225-226`**:
```python
elif cat.startswith("N"):  # Numbers
    digits += 1
```

**Fix**: Update documentation to say "category starts with 'N'" or clarify that Nl and No are included.

---

### 3. **Combining Marks Example Mismatch** (Low Priority)

**Location**: `architecture/measure.md:77-82`

**Example**: `char_category_metrics("Hello World! 123")` shows `combining_marks=0`

**Issue**: The example uses NFC-normalized text where "é" is a single codepoint. To demonstrate combining marks, one should use NFD-normalized text like `"café"` with decomposed é (e + combining acute accent).

**Note**: This is not a code bug; it's a documentation example issue.

---

### 4. **average_word_length Rounding Not Documented** (Low Priority)

**Location**: `architecture/measure.md:41`

**Issue**: Documentation does not mention that `average_word_length` is rounded to 2 decimal places.

**Code at `measure.py:196`**:
```python
average_word_length=round(avg_word_length, 2),
```

---

### 5. **Missing Cf Exclusion Context** (Low Priority)

**Location**: `architecture/measure.md:74`

**Issue**: The architecture doc does not mention that Cf (format) characters are excluded from control_chars per UTS #55, though the Session Learnings in AGENTS.md do note this.

**Code at `measure.py:234-235`**:
```python
if cat == "Cf":  # Format characters (e.g., U+FEFF BOM)
    pass  # Cf excluded from control_chars count per UTS #55
```

---

## Potential Bugs Identified

### 1. **Missing Else Clause in char_category_metrics** (Low Priority - Defensive Coding)

**Location**: `measure.py:220-239`

**Issue**: The `elif` chain does not have a final `else` to handle unexpected Unicode categories. Characters with categories not starting with L, N, P, S, Z, C, or M are silently ignored.

**Code**:
```python
for char in s:
    cat = unicodedata.category(char)
    if cat.startswith("L"):
        letters += 1
    elif cat.startswith("N"):
        digits += 1
    # ... etc
    elif cat.startswith("M"):
        combining_marks += 1
    # No else clause!
```

**Impact**: Very low - Python's `unicodedata.category()` always returns a known general category. This would only matter if the Unicode standard adds new categories.

**Recommendation**: Add defensive `else: pass` with a comment explaining this case cannot occur with valid Unicode.

---

### 2. **word_metrics Ignores Non-Letter Tokens** (Documented Behavior, Not a Bug)

**Location**: `measure.py:153-154`

**Behavior**: Only tokens containing at least one letter are counted as words.

**Example**:
```python
>>> word_metrics("123 hello 456")
WordMetrics(words=1, ..., average_word_length=5.0)
```

**Documentation at `measure.py:44`**:
```
Word Definition: Sequences of non-whitespace characters.
```

This comment is incorrect as it doesn't match the actual behavior. The code explicitly filters out tokens without letters (lines 153-154).

**Impact**: The docstring at `measure.py:44` contradicts the actual implementation.

**Recommendation**: Update the docstring to match the actual behavior: "Words are whitespace-separated tokens that contain at least one alphabetic character."

---

## Improvement Suggestions

### High Priority

1. **Fix control_chars documentation** (`architecture/measure.md:74`)
   - Remove "(excluding newlines/tabs)"
   - Clarify: "Control chars: category starts with 'C' (excluding 'Cf' format characters per UTS #55)"
   - Add note that newlines and tabs ARE counted

### Medium Priority

2. **Fix digits category documentation** (`architecture/measure.md:70`)
   - Change `"Nd"` to `"N"` or clarify "category starts with 'N' (includes Nd, Nl, No)"

3. **Add Cf exclusion note to documentation** (`architecture/measure.md:74`)
   - Add "Cf (format characters) are excluded per UTS #55"

### Low Priority

4. **Fix word_metrics docstring** (`measure.py:44`)
   - Change "Word Definition: Sequences of non-whitespace characters"
   - To "Word Definition: Whitespace-separated tokens containing at least one alphabetic character"

5. **Add rounding info for average_word_length** (`architecture/measure.md`)
   - Document that `average_word_length` is rounded to 2 decimal places

6. **Improve combining_marks example** (`architecture/measure.md:77-82`)
   - Use NFD text or add a second example showing combining marks

7. **Add defensive else clause** (`measure.py:239`)
   - Add `else: pass  # All categories handled; cannot reach here with valid Unicode`

---

## Test Coverage

All 13 tests in `tests/test_exact.py::TestMeasure` pass:

| Test | Status |
|------|--------|
| `test_line_metrics_lf` | PASS |
| `test_line_metrics_crlf` | PASS |
| `test_line_metrics_mixed` | PASS |
| `test_line_metrics_trailing_whitespace` | PASS |
| `test_line_metrics_max_line_length` | PASS |
| `test_line_metrics_empty` | PASS |
| `test_word_metrics_basic` | PASS |
| `test_word_metrics_punctuation` | PASS |
| `test_word_metrics_sentences` | PASS |
| `test_word_metrics_paragraphs` | PASS |
| `test_word_metrics_empty` | PASS |
| `test_word_metrics_average_length` | PASS |
| `test_char_category_metrics` | PASS |

---

## Conclusion

The measure module implementation is correct and well-tested. The main issues are documentation inaccuracies rather than code bugs. The highest priority fix is correcting the `control_chars` documentation which incorrectly states newlines and tabs are excluded when they are actually counted.
