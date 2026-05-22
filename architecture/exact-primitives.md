# exact/primitives.py — Core Unicode Primitives

Core text primitives built on Python's `unicodedata` module. These are the **building blocks** for all other exact/ modules.

## File: `nl_calc/exact/primitives.py`

## Overview

Provides low-level deterministic operations for:
- UTF-8 encoding
- Codepoint iteration
- Unicode normalization
- Case folding
- Invisible character detection
- Grapheme counting

**Key principle:** No semantic interpretation, no LLM calls, deterministic results.

## Type Definitions

### CodepointInfo (NamedTuple)

```python
class CodepointInfo(NamedTuple):
    index: int      # Position in string (0-indexed)
    char: str       # The character itself
    codepoint: str  # "U+XXXX" hex format
    name: str       # Unicode name (e.g., "LATIN SMALL LETTER A")
    category: str   # Unicode category (e.g., "Ll", "Lu", "Nd")
```

### MeasureBasic (TypedDict)

```python
class MeasureBasic(TypedDict):
    bytes_utf8: int              # Length in UTF-8 bytes
    codepoints: int              # Number of codepoints
    graphemes_estimate: int      # Estimated grapheme clusters
    chars_no_whitespace: int     # Non-whitespace characters
    ascii: int                   # ASCII characters
    non_ascii: int               # Non-ASCII characters
```

### InvisibleCharInfo (TypedDict)

```python
class InvisibleCharInfo(TypedDict):
    index: int           # Position in string
    char: str            # The invisible character
    codepoint: str       # "U+XXXX" format
    name: str            # Unicode name
    category: str        # Unicode category
    display: str         # Short display name (e.g., "ZWSP")
```

## Invisible Characters

The module maintains a dictionary of invisible characters:

```python
_INVISIBLE_CHARS: dict[str, tuple[str, str]] = {
    "\u200b": ("ZERO WIDTH SPACE", "ZWSP"),
    "\u200c": ("ZERO WIDTH NON-JOINER", "ZWNJ"),
    "\u200d": ("ZERO WIDTH JOINER", "ZWJ"),
    "\u200e": ("LEFT-TO-RIGHT MARK", "LRM"),
    "\u200f": ("RIGHT-TO-LEFT MARK", "RLM"),
    "\ufeff": ("ZERO WIDTH NO-BREAK SPACE", "BOM"),
    "\u00a0": ("NO-BREAK SPACE", "NBSP"),
    "\u2028": ("LINE SEPARATOR", "LINE SEP"),
    "\u2029": ("PARAGRAPH SEPARATOR", "PARA SEP"),
    # ... more
    "\u2060": ("WORD JOINER", "WORD JOINER"),
    "\u00ad": ("SOFT HYPHEN", "SHY"),
}
```

Also detects variation selectors (U+FE00 to U+FE0F).

## Functions

### `utf8_bytes(s: str) -> bytes`

Returns raw UTF-8 encoded bytes.

```python
utf8_bytes("hello")        # → b'hello'
utf8_bytes("こんにちは")   # → b'\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf'
utf8_bytes("")             # → b''
```

**Returns:** Actual `bytes` object, not a count.

### `codepoints(s: str) -> list[CodepointInfo]`

Returns detailed information about each codepoint.

```python
codepoints("Hi")
# → [
#     CodepointInfo(index=0, char='H', codepoint='U+0048', name='LATIN CAPITAL LETTER H', category='Lu'),
#     CodepointInfo(index=1, char='i', codepoint='U+0069', name='LATIN SMALL LETTER I', category='Ll')
# ]
```

### `normalize_unicode(s: str, form: str) -> str`

Normalizes Unicode string to specified form.

```python
normalize_unicode("café", "NFC")   # → "café" (composed)
normalize_unicode("cafe\u0301", "NFC")  # → "café" (same as above)
normalize_unicode("café", "NFD")   # → "cafe\u0301" (decomposed)
```

**Valid forms:** NFC, NFD, NFKC, NFKD

**Raises:** `ValueError` if form is invalid

### `casefold_text(s: str) -> str`

Returns casefolded version for case-insensitive comparison.

```python
casefold_text("HELLO")  # → "hello"
casefold_text("Straße")  # → "strasse" (German ß -> ss)
```

### `raw_equal(a: str, b: str) -> bool`

Checks exact byte equality.

```python
raw_equal("abc", "abc")     # → True
raw_equal("abc", "ABC")     # → False
raw_equal("café", "cafe\u0301")  # → False (different bytes)
```

### `normalized_equal(a: str, b: str) -> bool`

Checks equality after NFC normalization.

```python
normalized_equal("café", "cafe\u0301")  # → True
normalized_equal("ABC", "abc")           # → False (case-sensitive)
```

### `measure_basic(s: str) -> MeasureBasic`

Returns basic text metrics.

```python
measure_basic("Hello World")
# → MeasureBasic(
#     bytes_utf8=11,
#     codepoints=11,
#     graphemes_estimate=11,
#     chars_no_whitespace=10,
#     ascii=11,
#     non_ascii=0
# )
```

### `count_graphemes(s: str) -> int`

Counts grapheme clusters (what a user would consider a "character").

```python
count_graphemes("hello")        # → 5
count_graphemes("café")         # → 4 (é as single grapheme)
count_graphemes("👨‍👩‍👧‍👦")     # → 1 (family emoji is ZWJ sequence)
```

### `truncate_to_grapheme(s: str, max_graphemes: int) -> str`

Truncates string to max grapheme count, preserving grapheme integrity.

```python
truncate_to_grapheme("Hello World", 5)   # → "Hello"
truncate_to_grapheme("café", 3)          # → "caf"
truncate_to_grapheme("👋🌍", 1)           # → "👋"
```

### `find_invisibles(s: str) -> list[InvisibleCharInfo]`

Detects invisible characters in string.

```python
find_invisibles("hello\u200bworld")
# → [InvisibleCharInfo(
#     index=5,
#     char='\u200b',
#     codepoint='U+200B',
#     name='ZERO WIDTH SPACE',
#     category='Cf',
#     display='ZWSP'
# )]
```

### `visible_repr(s: str) -> str`

Returns display-safe representation with invisible characters marked.

```python
visible_repr("hello\u200bworld")  # → 'hello[ZWSP]world'
visible_repr("hi")                # → 'hi'
```

**Display order matters:** Variation selector checks come BEFORE combining mark checks (U+FE00-U+FE0F before category 'M').

## Unicode Categories

Categories used in codepoint info and metrics:

| Category | Name | Examples |
|----------|------|----------|
| Lu | Letter, uppercase | A-Z (Latin) |
| Ll | Letter, lowercase | a-z (Latin) |
| Lo | Letter, other | Chinese characters |
| Nd | Number, decimal digit | 0-9 |
| Nl | Number, letter | Roman numerals |
| No | Number, other | Superscripts |
| Po | Punctuation, other | . , ! ? |
| Pi | Punctuation, initial | « |
| Pf | Punctuation, final | » |
| Pd | Punctuation, dash | - |
| Zs | Separator, space | Space |
| Zl | Separator, line | Line separator |
| Zp | Separator, paragraph | Paragraph separator |
| Cf | Format | Word joiner, BOM |
| Cn | Not assigned | Unassigned |

## Implementation Notes

### Grapheme Counting Algorithm

Grapheme clusters are counted using Unicode segmentation:
1. Iterate through string by codepoint
2. Check for combining characters (category 'M' or 'Mn')
3. Check for variation selectors (U+FE00-U+FE0F)
4. Check for zero-width joiners (ZWJ U+200D)
5. Group connected codepoints into graphemes

### Visible Representation Display Order

The `visible_repr()` function has specific ordering for detecting invisible characters:

1. First check for known invisible characters (ZWSP, BOM, etc.)
2. Then check for variation selectors (U+FE00-U+FE0F)
3. Then check for combining marks (category 'Mn', 'Mc')
4. Then report character as-is

This ordering matters because some variation selectors can look like combining marks but should be handled differently.

## Dependencies

```
primitives.py
    └── (no external dependencies, uses only unicodedata and typing)
```

## Usage Example

```python
from nl_calc.exact import (
    utf8_bytes, codepoints, normalize_unicode,
    measure_basic, count_graphemes, find_invisibles
)

# Basic measurements
text = "Café naïve"
metrics = measure_basic(text)
print(f"UTF-8 bytes: {metrics['bytes_utf8']}")
print(f"Codepoints: {metrics['codepoints']}")
print(f"Graphemes: {count_graphemes(text)}")

# Normalization comparison
raw = "café"
decomposed = "cafe\u0301"
print(f"Raw equal: {raw == decomposed}")  # False
print(f"NFC equal: {normalize_unicode(raw, 'NFC') == normalize_unicode(decomposed, 'NFC')}")  # True

# Invisible detection
hidden = "password\u200b123"
invisibles = find_invisibles(hidden)
if invisibles:
    print(f"Found {len(invisibles)} invisible characters!")
```

## Testing Strategy

Since primitives are deterministic:
1. Test with known inputs for predictable outputs
2. Test Unicode edge cases (empty strings, surrogate pairs)
3. Test combining character sequences
4. Test ZWJ emoji sequences
5. Test all four normalization forms
6. Test invisible character detection for each known type