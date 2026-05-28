# primitives.py - Unicode Text Primitives

## Purpose

Low-level Unicode text primitives that are deterministic, independently testable, and do not perform semantic interpretation. All other modules in `exact/` build on these primitives.

## Core Functions

### Encoding and Codepoints

### `utf8_bytes(s: str) -> bytes`

Returns raw UTF-8 bytes of the string.

```python
>>> utf8_bytes("hello")
b'hello'
>>> utf8_bytes("こんにちは")
b'\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\xa1\x9f\xe3\x81\xa1'
```

### `codepoints(s: str) -> list[CodepointInfo]`

Returns detailed information about each codepoint in the string.

```python
@dataclass
class CodepointInfo(NamedTuple):
    index: int
    char: str
    codepoint: str      # "U+XXXX"
    name: str          # Unicode name
    category: str      # Unicode category (Lu, Ll, Nd, etc.)
```

Example:
```python
>>> codepoints("ABC")
[CodepointInfo(0, 'A', 'U+0041', 'LATIN CAPITAL LETTER A', 'Lu'),
 CodepointInfo(1, 'B', 'U+0042', 'LATIN CAPITAL LETTER B', 'Lu'),
 CodepointInfo(2, 'C', 'U+0043', 'LATIN CAPITAL LETTER C', 'Lu')]
```

### Normalization

### `normalize_unicode(s: str, form: str) -> str`

Normalize Unicode string to the specified form.

Valid forms: `NFC`, `NFD`, `NFKC`, `NFKD`

```python
>>> normalize_unicode("café", "NFC")
'café'
>>> normalize_unicode("café", "NFD")
'cafe\u0301'
```

### `casefold_text(s: str) -> str`

Return casefolded version of string for case-insensitive comparison.

```python
>>> casefold_text("HELLO")
'hello'
>>> casefold_text("Straße")
'strasse'
```

### Equality Checking

### `raw_equal(a: str, b: str) -> bool`

Check if two strings are exactly equal (byte identity).

```python
>>> raw_equal("hello", "hello")
True
>>> raw_equal("hello", "HELLO")
False
```

### `normalized_equal(a: str, b: str, form: str = "NFC") -> bool`

Check if two strings are equal after Unicode normalization.

```python
>>> normalized_equal("café", "cafe\u0301", "NFD")
True
```

### Measurement

### `measure_basic(s: str) -> MeasureBasic`

Return basic text measurements as a TypedDict:

```python
class MeasureBasic(TypedDict):
    bytes_utf8: int           # UTF-8 byte count
    codepoints: int          # Total codepoints
    graphemes_estimate: int  # Grapheme cluster count
    chars_no_whitespace: int # Non-whitespace characters
    ascii: int               # ASCII characters
    non_ascii: int           # Non-ASCII characters
```

### `find_invisibles(s: str) -> list[InvisibleCharInfo]`

Find all invisible or control characters in the string.

Detects:
- Zero-width spaces/joiners (ZWSP, ZWNJ, ZWJ)
- Directional marks (LRM, RLM, LRE, RLE, etc.)
- BOM (Byte Order Mark)
- No-break space (NBSP)
- Line/paragraph separators
- Soft hyphen
- Variation selectors
- Combining grapheme joiner

```python
class InvisibleCharInfo(TypedDict):
    index: int
    char: str
    codepoint: str  # "U+XXXX"
    name: str
    category: str
    display: str   # Short display name like "ZWSP"
```

### `visible_repr(s: str) -> str`

Return a display-safe representation, mapping invisible characters to visible markers:

| Character | Marker |
|-----------|--------|
| space | ␠ |
| tab | ␉ |
| newline | ␊ |
| carriage return | ␍ |
| ZWSP | ⟦ZWSP⟧ |
| VS | ⟦VS⟧ |
| combining marks | ◌ + char |
| bidi controls | ⟦LRI⟧, ⟦RLI⟧, etc. |

## Internal Constants

### `_INVISIBLE_CHARS`

Dictionary mapping invisible character codepoints to `(name, display)` tuples:

```python
_INVISIBLE_CHARS = {
    "\u200b": ("ZERO WIDTH SPACE", "ZWSP"),
    "\u200c": ("ZERO WIDTH NON-JOINER", "ZWNJ"),
    "\u200d": ("ZERO WIDTH JOINER", "ZWJ"),
    "\u200e": ("LEFT-TO-RIGHT MARK", "LRM"),
    "\u200f": ("RIGHT-TO-LEFT MARK", "RLM"),
    "\ufeff": ("ZERO WIDTH NO-BREAK SPACE", "BOM"),
    "\u00a0": ("NO-BREAK SPACE", "NBSP"),
    "\u2028": ("LINE SEPARATOR", "LINE SEP"),
    "\u2029": ("PARAGRAPH SEPARATOR", "PARA SEP"),
    "\u202a": ("LEFT-TO-RIGHT EMBEDDING", "LRE"),
    "\u202b": ("RIGHT-TO-LEFT EMBEDDING", "RLE"),
    "\u202c": ("POP DIRECTIONAL FORMATTING", "PDF"),
    "\u202d": ("LEFT-TO-RIGHT OVERRIDE", "LRO"),
    "\u202e": ("RIGHT-TO-LEFT OVERRIDE", "RLO"),
    "\u2066": ("LEFT-TO-RIGHT ISOLATE", "LRI"),
    "\u2067": ("RIGHT-TO-LEFT ISOLATE", "RLI"),
    "\u2068": ("FIRST STRONG ISOLATE", "FSI"),
    "\u2069": ("POP DIRECTIONAL ISOLATE", "PDI"),
    "\u2060": ("WORD JOINER", "WORD JOINER"),
    "\u00ad": ("SOFT HYPHEN", "SHY"),
    "\u180e": ("MONGOLIAN VOWEL SEPARATOR", "MVS"),
    "\u034f": ("COMBINING GRAPHEME JOINER", "CGJ"),
}
```

### `_VARIATION_SELECTORS`

Set of codepoint values for variation selectors (U+FE00 to U+FE0F).

## Dependencies

- `unicodedata` - Standard library for Unicode data
- `typing` - For type annotations and NamedTuple/TypedDict definitions

## Index

See [overview.md](overview.md) for the module index.