# Testing Guidelines

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=nl_calc --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_tokenization.py -v

# Run specific test class
python -m pytest tests/test_tokenization.py::TestMultiDigitSubtraction -v
```

## Test Files

| File | Purpose |
|------|---------|
| `test_clicalc.py` | Original functional tests (95 tests) |
| `test_security_fuzz.py` | Security and fuzz tests (22 tests) |
| `test_tokenization.py` | Tokenization edge cases (54 tests) |
| `test_math_identities.py` | Mathematical laws (28 tests) |
| `conftest.py` | Shared fixtures |

## API Usage

### Use `evaluate()` for:
- Pure math expressions (`"5 + 3"`, `"2**10"`)
- Function calls (`"sin(0)"`, `"sqrt(16)"`)
- Constants (`"pi"`, `"e"`)

### Use `run()` or CLI for:
- Natural language (`"five plus three"`)
- Unit expressions (`"30m + 100ft"`)
- Complex expressions with units

## Helper Functions

```python
def get_value(result):
    """Extract numeric value from result, handling UnitValue."""
    if isinstance(result, UnitValue):
        return result.value
    return result

def val(expr):
    """Evaluate and extract value, handling UnitValue."""
    result = evaluate(expr)
    if isinstance(result, UnitValue):
        return result.value
    return result
```

## Testing Patterns

### Parametric Tests
```python
@pytest.mark.parametrize("expr,expected", [
    ("90-1", 89),
    ("100-10", 90),
    ("1000-1", 999),
])
def test_multi_digit_subtraction(self, expr, expected):
    result = evaluate(expr)
    assert abs(get_value(result) - expected) < 1e-10
```

### Class-Based Organization
```python
class TestMultiDigitSubtraction:
    """Test subtraction with multi-digit numbers."""

    def test_simple_subtraction(self):
        result = evaluate("90-1")
        assert abs(get_value(result) - 89) < 1e-10
```

## Common Issues

### UnitValue Return Type
Many operations return `UnitValue` instead of plain numbers:
```python
result = evaluate("5 + 3")
# May return UnitValue(8, None) instead of 8
```

Always use `get_value()` or `val()` to extract the numeric value.

### API Mismatch
Using `evaluate()` for NL or unit expressions will fail:
```python
evaluate("five plus three")  # SyntaxError - not valid Python
evaluate("30m + 100ft")      # SyntaxError - m, ft not valid
```

Use `run()` for these cases.
