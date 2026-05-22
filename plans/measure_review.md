# measure.py Architecture Review

## Verified Claims

| Claim | Status |
|-------|--------|
| `line_metrics()` returns `LineMetrics` with fields: lines, nonempty_lines, blank_lines, max_line_length_codepoints, trailing_whitespace_lines (list[int]), newline_style, ends_with_newline | Verified |
| `word_metrics()` returns `WordMetrics` with fields: words, unique_words_casefolded, sentences_estimate, paragraphs, average_word_length | Verified |
| `char_category_metrics()` returns `CharCategoryMetrics` with fields: letters, digits, punctuation, symbols, spaces, control_chars, combining_marks | Verified |
| Newline style detection algorithm (CRLF → LF → CR → none) | Verified |
| `control_chars` excludes `Cf` (format characters) per UTS #55 | Verified |
| Word definition: sequences of non-whitespace characters (actual: filters tokens with at least one letter) | Verified |

## Discrepancies

### 1. Dataclass vs TypedDict
**Architecture doc says:** `@dataclass class LineMetrics(NamedTuple)`
**Actual code:** `class LineMetrics(TypedDict)`

The documentation shows NamedTuple with @dataclass decorator, but the implementation uses TypedDict. This is a significant inconsistency in the architecture docs.

### 2. `average_word_length` Precision
**Architecture doc:** Shows `5.0` (full precision)
**Actual code:** `round(avg_word_length, 2)` - rounds to 2 decimal places

```python
# measure.py:205
average_word_length=round(avg_word_length, 2),
```

### 3. `sentences_estimate` Returns 0 for No Matches
**Architecture doc:** Shows example with simple case
**Actual code:** Returns 0 when no sentence-ending punctuation found, but pattern `[.!?]+(?:\s|$)` requires whitespace or end-of-string after punctuation.

```python
# measure.py:180-182
sentence_pattern = r"[.!?]+(?:\s|$)"
sentences = re.findall(sentence_pattern, s)
sentences_estimate = len(sentences) if sentences else 0
```

The pattern requires whitespace or end-of-string after punctuation, which may not match sentences at end of input without trailing space/newline.

### 4. Paragraph Detection with Empty Lines
**Architecture doc:** Describes paragraphs as "separated by blank lines"
**Actual code:** Correctly implements blank line detection, but a single blank line between paragraphs is counted as one blank line, not creating a new paragraph.

### 5. TypedDict with `__slots__`
The code defines `__slots__` on TypedDict classes (lines 26, 38, 52), but TypedDict doesn't support `__slots__` - this has no effect but indicates confusion about type system.

## Bugs Found

### Bug 1: `char_category_metrics` - Control Character Count Excludes `Co` and `Cn`
**Severity:** Medium

The code only counts `Cc` (control characters):
```python
# measure.py:243-244
if cat == "Cc":  # Control characters
    control_chars += 1
```

But the architecture doc says "Category C* (Cc, Cs, Co, Cn) - Cf excluded per UTS #55". The implementation only counts `Cc`, not `Co` (other) or `Cn` (unassigned).

**Impact:** Control character count is incomplete.

### Bug 2: `word_metrics` Sentence Pattern Doesn't Match All Cases
**Severity:** Medium

```python
sentence_pattern = r"[.!?]+(?:\s|$)"
```

This pattern requires whitespace or end-of-string after sentence terminators. It won't count a sentence ending with `!` or `?` followed by another character like:
- `"Hello! World"` - The `!` won't be counted because it's followed by space but the space is followed by `W`, not at end or before new sentence marker
- `"Is it you?Really"` - The `?` won't be counted

Actually, `(?:\s|$)` should match before `W` in `"Hello! World"` since space is whitespace. Let me re-analyze...

Wait, the pattern `[.!?]+(?:\s|$)` matches `.!` followed by space, which matches. So `"Hello! World"` should work. But `"Really?You're"` - the `?` is followed by `Y`, not whitespace or end. So this would not be counted as a sentence ending.

### Bug 3: `_detect_newline_style` - False Positive for "mixed"
**Severity:** Low

```python
# measure.py:61-62
if has_crlf and (standalone_cr > 0 or standalone_lf > 0):
    return "mixed"
```

This returns "mixed" if CRLF exists AND there are standalone CR or LF. But this is overly broad - having CRLF and one standalone CR elsewhere does indicate mixing. However, the count logic is correct.

Actually, let me trace through a case: `\r\n\r` has CRLF and standalone CR.
- `has_crlf = True`
- `standalone_cr = 1 - 0 = 1` (one `\r` not part of CRLF)
- `standalone_lf = 0 - 0 = 0`
- Result: `mixed` - correct, there is mixing.

The logic seems correct for detecting mixed line endings.

## Improvements

### High Priority

1. **Fix `control_chars` to count all C* categories except Cf**
   - Currently only counts `Cc`, should also count `Co` and `Cn`
   - Location: `measure.py:242-247`

2. **Remove invalid `__slots__` from TypedDict classes**
   - `__slots__` has no effect on TypedDict and indicates type confusion
   - Location: `measure.py:26, 38, 52`

### Medium Priority

3. **Update architecture doc to reflect TypedDict usage**
   - Change `@dataclass class LineMetrics(NamedTuple)` to `class LineMetrics(TypedDict)`
   - Same for `WordMetrics` and `CharCategoryMetrics`

4. **Fix `sentence_pattern` to handle punctuation followed by non-whitespace**
   - Consider pattern like `[.!?]+(?:\s|$)|[.!?]+(?=[A-Z])`
   - This would catch `"Is it you?You're"` type cases

5. **Round `average_word_length` consistently**
   - Either document the 2 decimal place rounding or use full precision

### Low Priority

6. **Add type hints to TypedDict fields**
   - Currently only field names, no type annotations

7. **Consider adding docstring examples matching architecture doc**
   - The docstrings show examples in the arch doc but not in code

8. **Consider caching for repeated calls on same strings**
   - Could add `@functools.lru_cache` to metric functions if needed

## Summary

| Category | Count |
|----------|-------|
| Verified claims | 6 |
| Discrepancies | 5 |
| Bugs | 3 |
| Improvements | 8 |

The module is generally well-implemented and matches the architecture closely. The main issues are:
1. `control_chars` undercounts (missing Co, Cn)
2. Documentation uses NamedTuple/@dataclass but code uses TypedDict
3. `__slots__` on TypedDict classes is meaningless