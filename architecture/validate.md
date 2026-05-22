# validate.py - Validation Utilities

## Purpose

Provides validation utilities for checking brackets, JSON syntax, and testing regex patterns against sample strings.

## Core Functions

### `check_brackets(text: str, pairs: dict[str, str] | None = None) -> CheckBracketsResult`

Check whether delimiters are structurally balanced.

```python
class BracketError(TypedDict):
    char: str
    index: int
    line: int
    column: int


class CheckBracketsResult(TypedDict):
    balanced: bool
    unmatched_openers: list[BracketError]
    unmatched_closers: list[BracketError]
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
class ValidateJsonResult(TypedDict):
    valid: bool
    error: str | None
    line: int | None
    column: int | None
    position: int | None
    type: str | None
    top_level_keys: list[str] | None
```

```python
>>> validate_json('{"hello": "world"}')
ValidateJsonResult(valid=True, error=None, position=None,
                   line=None, column=None, type='object')
>>> validate_json('{"hello": }')
ValidateJsonResult(valid=False, error='Expecting property name',
                   position=10, line=1,
                   column=10, type=None)
```

### `regex_test(pattern: str, samples: list[str], flags: list[str] | None = None) -> RegexTestResult`

Test a Python regular expression against sample strings.

```python
class RegexMatch(TypedDict):
    sample: str
    matches: bool
    fullmatch: bool
    span: list[int] | None
    groups: list[str]
    groupdict: dict[str, str]


class RegexTestResult(TypedDict):
    valid_pattern: bool
    results: list[RegexMatch]
    error: str | None
```

Example:
```python
>>> regex_test(r"^\d+$", ["123", "abc", "12a"])
RegexTestResult(
    valid_pattern=True,
    error=None,
    results=[
        RegexSampleResult(sample='123', matches=True, fullmatch=True,
                          span=[0, 3], groups=[], groupdict={}),
        RegexSampleResult(sample='abc', matches=False, fullmatch=False,
                          span=None, groups=[], groupdict={}),
        RegexSampleResult(sample='12a', matches=True, fullmatch=False,
                          span=[0, 2], groups=[], groupdict={})
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