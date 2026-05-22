# measure.py - Text Metrics

## Purpose

Provides functions for measuring text properties including line metrics, word metrics, and character category metrics.

## Core Functions

### `line_metrics(text: str) -> LineMetrics`

Analyze line structure in text.

```python
class LineMetrics(TypedDict):
    lines: int
    nonempty_lines: int
    blank_lines: int
    max_line_length_codepoints: int
    trailing_whitespace_lines: list[int]
    newline_style: str
    ends_with_newline: bool
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
class WordMetrics(TypedDict):
    words: int
    unique_words_casefolded: int
    sentences_estimate: int
    paragraphs: int
    average_word_length: float
```

**Word Definition**: Sequences of non-whitespace characters.

```python
>>> word_metrics("hello world hello")
WordMetrics(words=3, unique_words_casefolded=2,
            sentences_estimate=1, paragraphs=1,
            average_word_length=5.0)
```

### `char_category_metrics(text: str) -> CharCategoryMetrics`

Break down characters by Unicode category.

```python
class CharCategoryMetrics(TypedDict):
    letters: int
    digits: int
    punctuation: int
    symbols: int
    spaces: int
    control_chars: int
    combining_marks: int
```

Uses Unicode category ranges for classification:
- Letters: unicodedata.category starts with "L"
- Digits: category starts with "N" (includes Nd, Nl, No)
- Punctuation: category starts with "P"
- Symbols: category starts with "S"
- Spaces: category starts with "Z"
- Control chars: category starts with "C" (excluding Cf per UTS #55)
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