# exact/ - Unicode Text Inspection Tools

## Purpose

Low-level Unicode text primitives for detecting hidden characters, confusables, and text metrics. These primitives are deterministic, independently testable, and do not perform semantic interpretation.

## Module Structure

```
exact/
├── __init__.py          # Re-exports all public functions
├── primitives.py         # UTF-8 encoding, codepoint iteration
├── unicode_tools.py      # Script detection, confusable detection
├── confusables.py        # Homoglyph identification
├── validate.py          # JSON/bracket/regex validation
├── diff.py              # String diffing algorithms
├── measure.py           # Text metrics (words, lines, categories)
└── synthesis.py         # Higher-level text analysis tools
```

## Core Primitives (primitives.py)

### `utf8_bytes(text: str) -> int`

Returns number of UTF-8 bytes in text.

### `codepoints(text: str) -> list[CodepointInfo]`

Returns list of codepoint information:

```python
@dataclass
class CodepointInfo:
    char: str
    codepoint: int
    hex: str
    name: str
    category: str
```

### `normalize_unicode(text: str, form: str = "NFKC") -> str`

Apply Unicode normalization (default NFKC).

### `casefold_text(text: str) -> str`

Apply case folding for comparison.

### `raw_equal(a: str, b: str) -> bool`

Byte-level equality check.

### `normalized_equal(a: str, b: str) -> bool`

Normalized equality check.

### `measure_basic(text: str) -> MeasureBasic`

Basic text metrics.

### `find_invisibles(text: str) -> list[InvisibleCharInfo]`

Find invisible characters (zero-width, control chars, etc.).

### `visible_repr(text: str) -> str`

Visual representation with escapes.

## Unicode Tools (unicode_tools.py)

### `unicode_script(char: str) -> ScriptInfo`

Get script information for a character.

```python
@dataclass
class ScriptInfo:
    script: str          # e.g., "Latin", "Cyrillic"
    script_name: str     # Full name
    is_latin: bool
    is_cyrillic: bool
    is_common: bool
```

### `detect_mixed_scripts(text: str) -> list[ScriptInfo]`

Detect mixed scripts in text.

### `detect_confusables(text: str) -> list[ConfusableInfo]`

Find confusable characters (homoglyphs).

```python
@dataclass
class ConfusableInfo:
    char: str
    confusable_with: str
    index: int
    codepoint: int
    script: str
```

## Validation (validate.py)

### `check_brackets(text: str) -> CheckBracketsResult`

Verify matching bracket pairs (parentheses, braces, brackets).

### `validate_json(text: str) -> ValidateJsonResult`

Validate JSON syntax.

### `regex_test(pattern: str, texts: list[str]) -> RegexTestResult`

Test regex pattern against texts.

## Diff Algorithms (diff.py)

### `levenshtein_distance(a: str, b: str) -> int`

Calculate edit distance between strings.

### `first_diff(a: str, b: str) -> FirstDiff | None`

Find first difference between two strings.

```python
@dataclass
class FirstDiff:
    position: int
    a_char: str
    b_char: str
    a_context: str
    b_context: str
```

### `common_prefix_suffix(a: str, b: str) -> tuple[str, str]`

Find common prefix and suffix.

### `diff_spans(a: str, b: str) -> list[DiffSpan]`

Generate list of diff spans.

```python
@dataclass
class DiffSpan:
    span_type: str  # "equal", "insert", "delete", "replace"
    a_start: int
    a_end: int
    b_start: int
    b_end: int
```

## Measurement (measure.py)

### `line_metrics(text: str) -> LineMetrics`

```python
@dataclass
class LineMetrics:
    count: int
    max_length: int
    avg_length: float
```

### `word_metrics(text: str) -> WordMetrics`

```python
@dataclass
class WordMetrics:
    count: int
    max_length: int
    avg_length: float
    unique: int
```

### `char_category_metrics(text: str) -> CharCategoryMetrics`

Character category breakdown (Lu, Ll, Nd, Po, etc.).

## Synthesis (synthesis.py)

Higher-level tools combining primitives:

### `measure_text(text: str) -> MeasureTextResult`

Comprehensive text metrics.

### `text_equal(a: str, b: str, normalize: bool = True) -> TextEqualResult`

String comparison with normalization options.

### `explain_diff(a: str, b: str) -> ExplainDiffResult`

Human-readable diff explanation.

### `inspect_text(text: str) -> InspectTextResult`

Check for hidden characters, confusables, mixed scripts.

### `count_chars(text: str, target: str | None = None) -> CountCharsResult`

Character counting and frequency.

### `list_compare(a: list, b: list) -> dict`

Compare two lists element by element.