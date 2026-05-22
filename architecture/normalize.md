# normalize.py - Natural Language Processing Pipeline

## Purpose

Converts mathematical expressions written in natural language (e.g., "sixteen plus five hundred twenty two") into executable mathematical expressions.

## Key Responsibilities

1. **Word-to-Number Conversion**: Translates number words ("twenty", "five", "hundred") to digits
2. **Operator Mapping**: Converts operator words ("plus", "minus", "times") to symbols
3. **Tokenization**: Splits expressions at operator boundaries
4. **Unit Preprocessing**: Inserts multiplication operators before units (e.g., `30m` → `30*m`)
5. **Unit Conversion Detection**: Identifies and handles unit conversion expressions

## Main Functions

### `normalize(expression, operators, patterns)`

Applies all normalization transformations to an expression string:
- Word replacement using combined dictionaries
- Percentage conversion
- Complex number suffix handling (`3i` → `3j`)
- Whitespace handling (removes outside parentheses, preserves inside)

### `normalize_expression(expression, operators, patterns)`

Full normalization pipeline without evaluation:
1. `normalize()` - Apply word replacements
2. `split_at_operators()` - Tokenize at operators
3. `convert_from_human_handler()` - Convert number words
4. `apply_math_functions()` - Handle function syntax
5. `_handle_unit_conversion_from_tokens()` - Detect unit conversions
6. `_preprocess_units()` - Add multiplication before units

### `run(expression, operators, patterns)`

Full pipeline: normalize + evaluate + return result.

## Build Compatibility

For single-file builds, `main()` is also available as `normalize_main()`:

```python
from normalize import main, normalize_main  # Both refer to same function
```

### `check_if_number(token)`

Checks if a token represents a number (int, float, hex, binary, octal, complex, unit-suffixed).

## Data Structures

```python
OPERATOR_CONVERSIONS = {
    "+": ["plus", "positive"],
    "-": ["minus", "negative"],
    "*": ["times", "multiplied by", "of"],
    "/": ["divided by", "over", "per"],
    "**": ["^", "raised to", "to the power of"],
    ...
}

NUMBER_WORDS = {
    "0": ["zero"],
    "1": ["one"],
    ...
    "100": ["hundred"],
    "1000": ["thousand"],
    ...
}
```

## Performance Optimizations

- Pre-sorted unit list `_UNITS_BY_LENGTH` for longest-match unit detection
- Unit prefix set `_UNIT_PREFIXES` for O(1) quick rejection
- LRU cache on `check_if_number()` (1024 entries)
- Combined regex patterns for single-pass word replacement

## Constants

- `MAX_INPUT_LENGTH = 10000` - Maximum input character length
- `MAX_NESTING_DEPTH = 100` - Maximum parentheses nesting depth

## Dependencies

- Imports from `evaluator.py`: `EvaluationError`, `evaluate`
- Imports from `units.py`: `UnitValue`, `UNIT_ALIASES`, `is_unit`, `UNIT_CATEGORIES`
- Imports from `exact`: `inspect_text`, `count_chars`, `regex_test`