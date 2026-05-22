# validate.py - Validation Utilities

## Purpose

Provides validation utilities for checking brackets, JSON syntax, and testing regex patterns against sample strings.

## Core Functions

### `check_brackets(text: str, pairs: dict[str, str] | None = None) -> CheckBracketsResult`

Check whether delimiters are structurally balanced.

```python
@dataclass
class CheckBracketsResult(NamedTuple):
    balanced: bool
    error: str | None          # Error message if unbalanced
    position: int | None      # Position of error
    expected: str | None      # What was expected
    unexpected: str | None    # What was unexpected
```

**Default bracket pairs**:
```python
{"(": ")", "[": "]", "{": "}", "<": ">"}
```

```python
>>> check_brackets("({[]})")
CheckBracketsResult(balanced=True, error=None, position=None,
                    expected=None, unexpected=None)
>>> check_brackets("({]})")
CheckBracketsResult(balanced=False, error='Mismatched bracket',
                    position=2, expected='}', unexpected=']')
```

### `validate_json(text: str) -> ValidateJsonResult`

Validate JSON syntax and report precise parse errors.

```python
@dataclass
class ValidateJsonResult(NamedTuple):
    valid: bool
    error: str | None          # Error message if invalid
    error_position: int | None # Character position of error
    error_line: int | None     # Line number of error
    error_column: int | None   # Column number of error
    structure: str | None      # "object", "array", "string", "number", etc.
```

```python
>>> validate_json('{"hello": "world"}')
ValidateJsonResult(valid=True, error=None, error_position=None,
                   error_line=None, error_column=None, structure='object')
>>> validate_json('{"hello": }')
ValidateJsonResult(valid=False, error='Expecting property name',
                   error_position=10, error_line=1,
                   error_column=10, structure=None)
```

### `regex_test(pattern: str, samples: list[str], flags: list[str] | None = None) -> RegexTestResult`

Test a Python regular expression against sample strings.

```python
@dataclass
class RegexTestResult(NamedTuple):
    valid_pattern: bool
    error: str | None
    results: list[RegexSampleResult]
```

Where `RegexSampleResult` contains:
```python
@dataclass
class RegexSampleResult(NamedTuple):
    sample: str
    matches: bool
    fullmatch: bool
    spans: list[tuple[int, int]]     # Match spans
    groups: list[str]                 # Captured groups
    groupdict: dict[str, str]         # Named groups
```

Example:
```python
>>> regex_test(r"^\d+$", ["123", "abc", "12a"])
RegexTestResult(
    valid_pattern=True,
    error=None,
    results=[
        RegexSampleResult(sample='123', matches=True, fullmatch=True,
                          spans=[(0, 3)], groups=[], groupdict={}),
        RegexSampleResult(sample='abc', matches=False, fullmatch=False,
                          spans=[], groups=[], groupdict={}),
        RegexSampleResult(sample='12a', matches=True, fullmatch=False,
                          spans=[(0, 2)], groups=[], groupdict={})
    ]
)
```

**Supported flags**: `IGNORECASE`, `MULTILINE`, `DOTALL`, `VERBOSE`, `ASCII`

## Error Handling

All functions raise `ValueError` for:
- Invalid regex patterns (handled gracefully in `regex_test`)
- Input exceeding size limits

## Index

See [overview.md](overview.md) for the module index.