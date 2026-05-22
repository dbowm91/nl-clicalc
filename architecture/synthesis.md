# synthesis.py - Higher-Level Text Analysis

## Purpose

Combines primitives from `primitives.py`, `unicode_tools.py`, `diff.py`, `measure.py`, and `validate.py` to provide higher-level text inspection, comparison, and measurement operations.

## Core Functions

### Text Measurement

### `measure_text(text: str, include_codepoints: bool = False) -> MeasureTextResult`

Comprehensive text measurement combining multiple primitives.

```python
class MeasureTextResult(TypedDict):
    bytes_utf8: int
    codepoints: int
    graphemes: None
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
    warnings: list[dict]
```

### Character Counting

### `count_chars(text: str, target: str | None = None, normalization: str = "raw") -> CountCharsResult | dict[str, int]`

Count character occurrences or return frequency table.

```python
class CountCharsResult(TypedDict):
    target: str
    normalization: str
    count: int
    positions: list[int]
    text_length_codepoints: int
```

When `target` is `None`, returns a frequency dictionary instead.

### List Comparison

### `list_compare(a: list[str], b: list[str], ignore_order: bool = True, casefold: bool = False, normalization: str = "NFC") -> dict`

Compare two lists with optional transformations.

```python
{
    "same_ordered": bool,
    "same_unordered": bool,
    "only_in_a": list[str],
    "only_in_b": list[str],
    "duplicates_a": list[str],
    "duplicates_b": list[str],
    "near_matches": list[dict]  # Items that differ only by case or normalization
}
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