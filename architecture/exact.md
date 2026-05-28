# exact/ — Unicode Text Primitives

Low-level deterministic Unicode text analysis tools. These modules are **independent** and **testable** without semantic interpretation or LLM calls.

## Module Structure

```
exact/
├── __init__.py       # Public API re-exports
├── primitives.py     # UTF-8, codepoints, normalization, invisibles
├── unicode_tools.py  # Script detection, confusables
├── measure.py        # Text metrics (words, lines, categories)
├── diff.py           # String diffing algorithms
├── validate.py       # JSON/bracket/regex validation
├── synthesis.py     # Higher-level text analysis
└── confusables.py   # Homoglyph identification (auto-generated)
```

## exact/__init__.py — Public API

Re-exports all public functions from submodules:

```python
from nl_calc.exact import (
    # Primitives
    utf8_bytes, codepoints, normalize_unicode, casefold_text,
    raw_equal, normalized_equal, measure_basic, count_graphemes,
    truncate_to_grapheme, find_invisibles, visible_repr,

    # Unicode tools
    unicode_script, unicode_scripts, detect_mixed_scripts,
    detect_confusables, confusables_count, reverse_confusables,

    # Diff
    first_diff, common_prefix_suffix, levenshtein_distance,
    diff_spans, longest_common_subsequence,

    # Validate
    check_brackets, validate_json, regex_test,

    # Measure
    line_metrics, word_metrics, char_category_metrics,

    # Synthesis
    measure_text, text_equal, inspect_text, explain_diff,
    count_chars, list_compare,
)
```

---

## primitives.py — Core Text Primitives

Low-level operations built on Python's `unicodedata` module.

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `utf8_bytes(s)` | bytes | Raw UTF-8 encoded bytes |
| `codepoints(s)` | list[CodepointInfo] | Detailed codepoint information |
| `normalize_unicode(s, form)` | str | NFC/NFD/NFKC/NFKD normalization |
| `casefold_text(s)` | str | Case-insensitive comparison |
| `raw_equal(a, b)` | bool | Exact string equality |
| `normalized_equal(a, b)` | bool | Equality after NFC normalization |
| `measure_basic(s)` | MeasureBasic | Basic text metrics |
| `count_graphemes(s)` | int | Grapheme cluster count |
| `truncate_to_grapheme(s, max_graphemes)` | str | Truncate to grapheme boundary |
| `find_invisibles(s)` | list[InvisibleCharInfo] | Detect hidden characters |
| `visible_repr(s)` | str | Display-safe representation |

### Invisible Characters Detected

```python
{
    "\u200b": "ZERO WIDTH SPACE (ZWSP)",
    "\u200c": "ZERO WIDTH NON-JOINER (ZWNJ)",
    "\u200d": "ZERO WIDTH JOINER (ZWJ)",
    "\u200e": "LEFT-TO-RIGHT MARK (LRM)",
    "\u200f": "RIGHT-TO-LEFT MARK (RLM)",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE (BOM)",
    "\u00a0": "NO-BREAK SPACE (NBSP)",
    "\u2028": "LINE SEPARATOR",
    "\u2029": "PARAGRAPH SEPARATOR",
    "\u202a": "LEFT-TO-RIGHT EMBEDDING (LRE)",
    "\u202b": "RIGHT-TO-LEFT EMBEDDING (RLE)",
    "\u202c": "POP DIRECTIONAL FORMATTING (PDF)",
    "\u202d": "LEFT-TO-RIGHT OVERRIDE (LRO)",
    "\u202e": "RIGHT-TO-LEFT OVERRIDE (RLO)",
    "\u2060": "WORD JOINER",
    "\u2066": "LEFT-TO-RIGHT ISOLATE (LRI)",
    "\u2067": "RIGHT-TO-LEFT ISOLATE (RLI)",
    "\u2068": "FIRST STRONG ISOLATE (FSI)",
    "\u2069": "POP DIRECTIONAL ISOLATE (PDI)",
    "\u00ad": "SOFT HYPHEN (SHY)",
    "\u180e": "MONGOLIAN VOWEL SEPARATOR (MVS)",
    "\u034f": "COMBINING GRAPHEME JOINER (CGJ)",
    ...
}
```

### CodepointInfo NamedTuple

```python
CodepointInfo(
    index=int,      # Position in string
    char=str,       # The character
    codepoint=str,  # "U+XXXX" format
    name=str,       # Unicode name
    category=str    # Unicode category (Lu, Nd, Po, etc.)
)
```

### MeasureBasic TypedDict

```python
MeasureBasic(
    bytes_utf8=int,          # UTF-8 byte count
    codepoints=int,          # Codepoint count
    graphemes_estimate=int,  # Grapheme cluster estimate
    chars_no_whitespace=int, # Non-whitespace characters
    ascii=int,               # ASCII character count
    non_ascii=int            # Non-ASCII character count
)
```

---

## unicode_tools.py — Script and Confusable Detection

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `unicode_script(char)` | str | Script of a character |
| `unicode_scripts(s)` | list[str] | Scripts for all characters |
| `detect_mixed_scripts(s)` | list[ScriptInfo] | Find mixed-script runs |
| `detect_confusables(s)` | list[ConfusableInfo] | Find confusable homoglyphs |
| `confusables_count(s)` | int | Fast confusable count |
| `reverse_confusables(char)` | list[str] | Find chars that confusable-map TO this char |

### Script Detection

Scripts include: Latin, Greek, Cyrillic, Arabic, Hebrew, Han (Chinese), Japanese (Hiragana/Katakana), Korean (Hangul), Thai, etc.

### Confusable Detection

Identifies characters that appear identical but have different Unicode code points:

```python
# Latin 'a' vs Cyrillic 'а'
detect_confusables("access")  # Returns confusables in Latin 'a' → Cyrillic 'а'
```

### reverse_confusables

```python
reverse_confusables(char: str) -> list[str]
```

Given a character, returns all characters from the confusables table that confusable-map TO this character (i.e., characters that look like the given character).

```python
# Digit 0 looks like letter O
"0" in reverse_confusables("O")  # True
```

Returns an empty list if no characters confusable-map to the input.

---

## measure.py — Text Metrics

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `measure_basic(s)` | MeasureBasic | Basic metrics |
| `char_category_metrics(s)` | CharCategoryMetrics | Metrics by Unicode category |
| `line_metrics(s)` | LineMetrics | Line count and newline style |
| `word_metrics(s)` | WordMetrics | Word count and boundaries |

### CharCategoryMetrics

Groups characters by Unicode category:

| Category | Description | Example |
|----------|-------------|---------|
| Lu | Letter, uppercase | A-Z (Latin) |
| Ll | Letter, lowercase | a-z (Latin) |
| Nd | Number, decimal digit | 0-9 |
| Po | Punctuation, other | . , ! ? |
|Zs | Separator, space | Space, NBSP |
| ... | | |

### LineMetrics

```python
LineMetrics(
    lines=int,                      # Total number of lines
    nonempty_lines=int,             # Lines with content
    blank_lines=int,                # Empty lines
    max_line_length_codepoints=int, # Longest line length
    trailing_whitespace_lines=list[int],  # Indices of lines with trailing whitespace
    newline_style=str,              # "LF", "CRLF", "CR", "mixed", "none"
    ends_with_newline=bool          # Whether string ends with newline
)
```

---

## diff.py — String Comparison Algorithms

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `first_diff(a, b)` | FirstDiff | Position of first difference |
| `common_prefix_suffix(a, b)` | CommonPrefixSuffix | Longest common prefix/suffix lengths |
| `levenshtein_distance(a, b)` | int | Edit distance |
| `diff_spans(a, b)` | list[DiffSpan] | Spans that differ |
| `longest_common_subsequence(a, b)` | str | LCS via dynamic programming |

### DiffSpan

```python
DiffSpan(
    kind=str,            # "equal", "insert", "delete", "replace"
    a_span=list[int],    # [start, end) in string a
    b_span=list[int],    # [start, end) in string b
    a_text=str,
    b_text=str,
)
```

### FirstDiff

```python
FirstDiff(
    a_index=int,         # Position of first difference in string a
    b_index=int,         # Position of first difference in string b
    a_char=str,          # Character at position in string a
    b_char=str,          # Character at position in string b
    a_codepoint=str,     # "U+XXXX" format
    b_codepoint=str,     # "U+XXXX" format
)
```

### CommonPrefixSuffix

```python
CommonPrefixSuffix(
    common_prefix_len=int,   # Length of common prefix
    common_suffix_len=int,   # Length of common suffix (non-overlapping)
)
```

### Examples

```python
first_diff("hello", "hallo")
# → FirstDiff(a_index=1, b_index=1, a_char='e', b_char='a', ...)

common_prefix_suffix("abc123", "abc456")
# → CommonPrefixSuffix(common_prefix_len=3, common_suffix_len=0)
```

---

## validate.py — Format Validation

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `check_brackets(s)` | CheckBracketsResult | Balanced bracket check |
| `validate_json(s)` | ValidateJsonResult | JSON syntax validation |
| `regex_test(pattern, samples)` | RegexTestResult | Test regex against samples |

### CheckBracketsResult

```python
CheckBracketsResult(
    balanced=bool,
    unmatched_openers=list[BracketError],  # Opening brackets without matching close
    unmatched_closers=list[BracketError]    # Closing brackets without matching open
)
```

Where `BracketError` contains: `char` (the bracket character), `position` (index in string).

Handles bracket types: `()`, `[]`, `{}`, `<>`

### RegexTestResult

```python
RegexTestResult(
    valid_pattern=bool,      # Whether regex pattern is valid
    results=list[RegexMatch],  # List of per-sample match results
    error=str | None         # Error message if pattern invalid
)
```

### RegexMatch

```python
RegexMatch(
    sample=str,              # The input sample string
    matches=bool,            # Whether pattern matched (anywhere)
    fullmatch=bool,          # Whether entire string matched
    span=list[int] | None,   # (start, end) of match if any
    groups=list[str],        # Captured groups
    groupdict=dict[str, str] # Named groups dict
)
```

---

## synthesis.py — Higher-Level Analysis

Combines primitives into higher-level tools.

### Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `measure_text(s)` | MeasureTextResult | Comprehensive text metrics |
| `text_equal(a, b, ...)` | TextEqualResult | String equality modes |
| `inspect_text(s, ...)` | InspectTextResult | Hidden char inspection |
| `explain_diff(a, b, ...)` | ExplainDiffResult | Detailed diff explanation |
| `count_chars(s, ...)` | CountCharsResult | Character counting |
| `list_compare(a, b)` | dict | Compare two lists |

### MeasureTextResult

Combines: basic metrics + category metrics + line metrics + word metrics + invisible detection + mixed script detection

```python
MeasureTextResult(
    basic=MeasureBasic,
    categories=CharCategoryMetrics,
    lines=LineMetrics,
    words=WordMetrics,
    invisibles=list[InvisibleCharInfo],
    mixed_scripts=list[ScriptInfo],
    ...
)
```

### TextEqualResult

```python
TextEqualResult(
    raw_equal=bool,
    nfc_equal=bool,
    nfd_equal=bool,
    nfkc_equal=bool,
    nfkd_equal=bool,
    casefold_equal=bool,
    trim_equal=bool,
    ...
)
```

### InspectTextResult

```python
InspectTextResult(
    codepoints=list[CodepointInfo],
    invisibles=list[InvisibleCharInfo],
    confusables=list[ConfusableInfo],
    mixed_scripts=list[ScriptInfo],
    visible_repr=str,
    normalization=str,  # Current normalization form
    ...
)
```

---

## confusables.py — Homoglyph Data

**Auto-generated data file** (~180KB, ~6500 lines).

Contains mapping of confusable character pairs:
- Latin/Cyrillic confusables
- Latin/Greek confusables
- Latin/Arabic confusables
- etc.

Data format:
```python
CONFUSABLES: dict[str, list[str]] = {
    "A": ["А", "Α", "А", "𝒜"],  # Latin A vs Cyrillic А, Greek Α, etc.
    "a": ["а", "ɑ", "α", "а"],
    ...
}
```

---

## Architecture Notes

```
┌─────────────────────────────────────────────────────────────┐
│                        synthesis.py                         │
│         (High-level tools combining primitives)            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌────────────┐ ┌──────┐ ┌──────────┐     │
│  │diff.py   │ │measure.py   │ │validate│ │unicode_ │     │
│  │          │ │            │ │      │ │tools.py │     │
│  └────┬─────┘ └──────┬─────┘ └───┬──┘ └────┬─────┘     │
│       │               │           │          │            │
├───────┴───────────────┴───────────┴──────────┴────────────┤
│                      primitives.py                           │
│         (UTF-8, codepoints, normalization, invisibles)      │
└─────────────────────────────────────────────────────────────┘
```

### Key Conventions

1. **`utf8_bytes()` returns `bytes`** — Not an int count, returns actual UTF-8 encoded bytes
2. **`visible_repr()` display order matters** — Variation selector checks must come BEFORE combining mark checks
3. **`_get_script_heuristic()` benefits from caching** — Now has `@functools.lru_cache` decorator
4. **Cf (format) characters excluded from `control_chars`** — Format characters are silently ignored per UTS #55
5. **`confusables_count()` helper** — Fast function to count confusables without building full list

### TypedDict vs NamedTuple

Architecture docs may show `@dataclass class Xxx(NamedTuple)` but code uses `class Xxx(TypedDict)` for consistency with Python 3.14+ typing patterns.

---

## Testing

All exact/ modules have deterministic behavior:
- No random operations
- No external dependencies (network, filesystem)
- No LLM calls
- Repeatable results for same input

See `tests/test_exact.py` for comprehensive tests.