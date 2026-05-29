# synthesis.py - Higher-Level Text Analysis

## Purpose

Combines primitives from `primitives.py`, `unicode_tools.py`, `diff.py`, `measure.py`, and `validate.py` to provide higher-level text inspection, comparison, and measurement operations.

## Core Functions

### Text Measurement

### `measure_text(text: str) -> MeasureTextResult`

Comprehensive text measurement combining multiple primitives.

```python
class MeasureTextResult(TypedDict):
    bytes_utf8: int
    codepoints: int
    graphemes: int
    words: int
    unique_words_casefolded: int
    lines: int
    nonempty_lines: int
    blank_lines: int
    max_line_length_codepoints: int
    chars_no_whitespace: int
    ascii: int
    non_ascii: int
    letters: int
    digits: int
    punctuation: int
    symbols: int
    spaces: int
    control_chars: int
    combining_marks: int
    invisible_chars: int
    newline_style: str
    ends_with_newline: bool
    normalization: NormalizationState
    unicode_risks: UnicodeRisks

class NormalizationState(TypedDict):
    """Unicode normalization state for a string."""
    is_nfc: bool
    is_nfd: bool
    is_nfkc: bool
    is_nfkd: bool

class UnicodeRisks(TypedDict):
    """Unicode risk signals detected in a string."""
    contains_invisibles: bool
    contains_bidi_controls: bool
    mixed_scripts: bool
    scripts: list[str]
```

### Text Comparison

### `text_equal(a: str, b: str, normalization: str = "raw", casefold: bool = False, trim: bool = False) -> TextEqualResult`

Compare two strings under various equality modes.

```python
class TextEqualResult(TypedDict):
    equal: bool
    mode: dict[str, Any]
    raw_equal: bool
    nfc_equal: bool
    nfd_equal: bool
    nfkc_equal: bool
    nfkd_equal: bool
    casefold_equal: bool
    byte_equal: bool
    lengths: dict[str, int]
    first_difference: dict[str, Any] | None
    classification: str  # "exact_match", "accent_or_diacritic_difference", etc.
```

### Diff Explanation

### `explain_diff(a: str, b: str, max_diffs: int = 20, include_codepoints: bool = True, include_context: bool = True) -> ExplainDiffResult`

Explain why two strings differ with detailed evidence.

```python
class ExplainDiffResult(TypedDict):
    equal: bool
    classification: str
    summary: dict[str, Any]
    a_metrics: dict[str, int]
    b_metrics: dict[str, int]
    diffs: list[DiffInfo]
    security_findings: list[dict]
    agent_instruction: str
```

### Text Inspection

### `inspect_text(text: str, include_codepoints: bool = True, include_confusables: bool = True) -> InspectTextResult`

Inspect text for hidden characters, confusables, and Unicode signals.

```python
class InspectTextResult(TypedDict):
    safe_repr: str
    metrics: dict[str, Any]
    normalization: dict[str, bool]
    invisibles: list[dict]
    scripts: dict[str, Any]
    confusables: list[dict]
    bidi_controls: list[dict]
    normalization_findings: list[NormalizationFinding]
    warnings: list[dict]

class InspectTextNormalized(TypedDict):
    """Normalized text analysis result."""
    form: str                    # NFC, NFD, NFKC, or NFKD
    text: str                    # Normalized text
    safe_repr: str               # Safe representation of normalized text
    changed: bool                # Whether normalization changed the text
    diff: list[dict]             # Differences found during normalization

class NormalizationFinding(TypedDict):
    """A finding from normalization analysis."""
    kind: str                    # Type of finding (e.g., "unsafe_chars", "mixed_script")
    message: str                # Human-readable description
```

### Character Counting

### `count_chars(text: str, target: str | None = None, normalization: str = "raw") -> CountCharsResult | dict[str, int]`

Count character occurrences or return frequency table. Returns `CountCharsResult` when `target` is specified, otherwise returns a frequency dictionary.

```python
class CountCharsResult(TypedDict):
    target: str                      # The character being counted
    normalization: str              # Normalization mode used
    count: int                       # Number of occurrences
    positions: list[int]             # All positions where target appears
    text_length_codepoints: int       # Total text length in codepoints
```

When `target` is `None`, returns a frequency dictionary mapping each character to its count.

### List Comparison

### `list_compare(a: list[str], b: list[str], ignore_order: bool = True, casefold: bool = False, normalization: str = "NFC", treat_as_multiset: bool = True, include_near_matches: bool = False, near_match_threshold: int = 2) -> ListCompareResult`

Compare two lists with optional transformations.

```python
class ListCompareResult(TypedDict):
    same_ordered: bool
    same_unordered: bool
    only_in_a: list[str]
    only_in_b: list[str]
    duplicates_a: list[str]
    duplicates_b: list[str]
    near_matches: list[ListCompareNearMatch]

class ListCompareOrderedResult(TypedDict):
    equal: bool
    first_diff_index: int | None
    equal_prefix_length: int
    aligned: list[dict]

class ListCompareSetResult(TypedDict):
    equal: bool
    only_in_a: list[str]
    only_in_b: list[str]

class ListCompareMultisetResult(TypedDict):
    equal: bool
    count_deltas: dict[str, int]
    only_in_a: list[str]
    only_in_b: list[str]

class ListCompareNearMatch(TypedDict):
    a: str
    b: str
    distance: int
    classification: str
```

### Text Window

### `text_window(text: str, position: dict, context_lines: int = 2, include_visible_repr: bool = True) -> TextWindowResult`

Get a window around a position in text with context lines. Shows the line at the given position with surrounding context lines.

```python
class TextWindowPosition(TypedDict):
    byte_offset: int
    codepoint_index: int
    grapheme_index: int
    line: int
    column: int

class TextWindowResult(TypedDict):
    position: TextWindowPosition
    line_text: str
    line_visible_repr: str
    before: list[dict]
    after: list[dict]
    newline_style: str
    at_codepoint: dict | None
    warnings: list[str]
```

## Internal Helper Functions

### `_classify_difference(...) -> str`

Classifies the type of difference between two strings:
- `"exact_match"` - Strings are identical
- `"accent_or_diacritic_difference"` - NFC equal but casefold differs
- `"unicode_normalization_only"` - NFC equal
- `"length_only"` - Different lengths
- `"invisible_character"` - Invisible characters detected
- `"ordinary_text_difference"` - Regular text difference

### `_generate_agent_instruction(...) -> str`

Generates agent-facing instruction based on classification.

### `_codepoint_details(s: str, start: int, end: int) -> list[dict]`

Gets codepoint details for a span.

## Dependencies

`synthesis.py` combines functions from:
- `primitives` - Basic text operations
- `unicode_tools` - Script and confusable detection
- `diff` - Diff algorithms
- `measure` - Text metrics
- `validate` - Validation utilities

## Index

See [overview.md](overview.md) for the module index.