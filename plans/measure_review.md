# measure.py Architecture Review

## Verified Claims

### LineMetrics
- `lines`, `nonempty_lines`, `blank_lines` - **Verified**: Correctly computed via `splitlines()` and iteration
- `max_line_length_codepoints` - **Verified**: Uses `len(line)` on codepoints (correct for Unicode)
- `trailing_whitespace_lines` - **Verified**: Uses `line != line.rstrip()` comparison
- `newline_style` detection - **Verified**: Algorithm correctly detects LF, CRLF, CR, mixed, none
- `ends_with_newline` - **Verified**: Checks for all newline types including edge cases

### WordMetrics
- `words` counting - **Verified**: Filters tokens to require at least one letter
- `unique_words_casefolded` - **Verified**: Uses `casefold()` for proper Unicode case-insensitive comparison
- `paragraphs` counting - **Verified**: Separated by blank lines, with fallback for content-only text
- `average_word_length` - **Verified**: Calculated correctly with rounding

### char_category_metrics
- Category classification logic - **Verified**: Uses `unicodedata.category()` with proper `startswith` checks
- Letters (L*), digits (Nd), punctuation (P*), symbols (S*), spaces (Z*), combining marks (M*) - **Verified**

## Discrepancies

### 1. WordMetrics Dataclass Definition vs Actual (HIGH)
**Location**: measure.md:38-52 vs measure.py:25-31

**Documentation claims**:
```python
@dataclass
class WordMetrics(NamedTuple):
    words: int
    unique_words_casefolded: int
    sentences_estimate: int
    paragraphs: int
    average_word_length: float  # Only this field exists
```

**But example shows**:
```python
WordMetrics(words=3, unique_words_casefolded=2,
            max_word_length=5, avg_word_length=5.0)  # max_word_length doesn't exist!
```

**Actual implementation** has only `average_word_length`, NOT `max_word_length`.

**Impact**: Documentation is self-contradictory and misleading.

---

### 2. Control Character Classification (MEDIUM)
**Location**: measure.md:63 vs measure.py:233-238

**Documentation states**: `control_chars: int    # Category C* (Cc, Cf, Cs, Co, Cn)`

**Implementation**:
```python
elif cat.startswith("C"):  # Other (control, format, etc.)
    if cat == "Cc":  # Control characters
        control_chars += 1
    elif cat == "Cf":  # Format characters
        pass  # Don't count as control
    # Other C* (like surrogate) skip
```

**Issue**: Documentation lists Cf as part of control_chars, but implementation explicitly skips Cf (format characters). This is a significant security-relevant discrepancy since Cf includes invisible characters like:
- U+200B (zero-width space)
- U+200E (left-to-right mark)
- U+2028 (line separator)
- U+2029 (paragraph separator)

These "invisible" Cf characters are exactly what `find_invisibles()` in primitives.py detects. Including them in `control_chars` would make the metric more useful for security analysis.

## Bugs Found

### 1. Cf Format Characters Excluded from Control Count (MEDIUM - Security Relevance)
**Location**: measure.py:236-237

**Problem**: Format characters (category Cf) are intentionally skipped, but these include invisible Unicode characters that are security-relevant (homoglyphs, hidden text, steganography).

**Current behavior**: Zero-width space (U+200B) is NOT counted in control_chars.

**Should behavior**: According to documentation, Cf should be counted.

**Workaround**: Users calling `char_category_metrics` would NOT detect zero-width spaces unless they also use `find_invisibles()` directly.

---

### 2. Inconsistent Import Style (LOW)
**Location**: measure.py:170

**Problem**:
```python
def word_metrics(s: str) -> WordMetrics:
    ...
    import re  # Local import inside function
```

All other imports in the module are at module level (line 10-11). This is inconsistent with codebase conventions.

---

## Improvements

### 1. Document max_word_length Absence (LOW)
If `max_word_length` was ever intended but not implemented, it should be either:
- Added to the implementation, OR
- Removed from documentation

### 2. Consider Adding max_word_length (MEDIUM - Feature Gap)
The documentation example shows `max_word_length` which doesn't exist. If there's a use case for max word length tracking, this could be a useful addition.

### 3. Align Control Chars with Documentation (MEDIUM)
Either:
- Update documentation to reflect that Cf is excluded, OR
- Update implementation to include Cf in control_chars count

### 4. Use Module-Level re Import (LOW)
Move `import re` to top of file alongside `unicodedata` import.

---

## Priority Summary

| Item | Type | Priority | Effort |
|------|------|----------|--------|
| Documentation contradiction (max_word_length) | Discrepancy | HIGH | Low (doc fix) |
| Cf exclusion from control_chars | Bug | MEDIUM | Low (code or doc fix) |
| Local import inconsistency | Code Style | LOW | Trivial |
| Add max_word_length feature | Improvement | MEDIUM | Medium |

---

## Recommendations

1. **Immediate**: Fix documentation to remove `max_word_length` from example to match actual implementation.

2. **Security-relevant**: Consider whether Cf characters should be included in control_chars count since they're exactly the "invisible" characters the module aims to detect. This would align behavior with documentation.

3. **Low priority**: Move `import re` to module level for consistency.