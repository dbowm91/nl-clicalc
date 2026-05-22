# measure.py - Text Metrics

## Purpose

Provides functions for measuring text properties including line metrics, word metrics, and character category metrics.

## Core Functions

### `line_metrics(text: str) -> LineMetrics`

Analyze line structure in text.

```python
@dataclass
class LineMetrics(NamedTuple):
    lines: int                       # Total line count
    nonempty_lines: int              # Lines with content
    blank_lines: int                 # Empty lines
    max_line_length_codepoints: int  # Longest line length
    trailing_whitespace_lines: list[int]  # 1-based line numbers with trailing whitespace
    newline_style: str               # "LF", "CRLF", "CR", "mixed", "none"
    ends_with_newline: bool          # Does text end with newline?
```

```python
>>> line_metrics("hello\nworld\n")
LineMetrics(lines=2, nonempty_lines=2, blank_lines=0,
            max_line_length_codepoints=5, newline_style='LF',
            ends_with_newline=True)
```

### `word_metrics(text: str) -> WordMetrics`

Analyze word structure in text.

```python
@dataclass
class WordMetrics(NamedTuple):
    words: int                       # Total word count
    unique_words_casefolded: int     # Unique words (casefolded)
    sentences_estimate: int           # Estimated sentence count
    paragraphs: int                  # Number of paragraphs (separated by blank lines)
    average_word_length: float       # Average word length in characters
```

**Word Definition**: Sequences of non-whitespace characters.

```python
>>> word_metrics("hello world hello")
WordMetrics(words=3, unique_words_casefolded=2,
            max_word_length=5, avg_word_length=5.0)
```

### `char_category_metrics(text: str) -> CharCategoryMetrics`

Break down characters by Unicode category.

```python
@dataclass
class CharCategoryMetrics(NamedTuple):
    letters: int          # Category L* (Lu, Ll, Lt, Lm, Lo)
    digits: int           # Category Nd
    punctuation: int     # Category P* (Pc, Pd, Ps, Pe, Pi, Pf, Po)
    symbols: int          # Category S* (Sm, Sc, Sk, So)
    spaces: int           # Category Zs (and other Z*)
    control_chars: int    # Category C* (Cc, Cf, Cs, Co, Cn)
    combining_marks: int # Category M* (Mn, Mc, Me)
```

Uses Unicode category ranges for classification:
- Letters: unicodedata.category starts with "L"
- Digits: category "Nd"
- Punctuation: category starts with "P"
- Symbols: category starts with "S"
- Spaces: category starts with "Z"
- Control chars: category starts with "C" (excluding newlines/tabs)
- Combining marks: category starts with "M"

```python
>>> char_category_metrics("Hello World! 123")
CharCategoryMetrics(letters=10, digits=3, punctuation=1,
                   symbols=0, spaces=3, control_chars=0,
                   combining_marks=0)
```

## Newline Style Detection

The `newline_style` field detects the type of line endings:

| Style | Description |
|-------|-------------|
| `"LF"` | Unix-style \n |
| `"CRLF"` | Windows-style \r\n |
| `"CR"` | Old Mac-style \r |
| `"mixed"` | Multiple types present |
| `"none"` | No newlines |

Detection algorithm:
1. If text contains \r\n → "CRLF"
2. If text contains \r (not followed by \n) → "CR"
3. If text contains \n → "LF"
4. Otherwise → "none"

## Index

See [overview.md](overview.md) for the module index.