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
| `test_clicalc.py` | Core functional tests (87 tests) |
| `test_security_fuzz.py` | Security and fuzz tests (22 tests) |
| `test_tokenization.py` | Tokenization edge cases (54 tests) |
| `test_math_identities.py` | Mathematical laws (28 tests) |
| `test_exact.py` | Unicode text primitives (98 tests) |
| `test_cli_text.py` | CLI text tools (19 tests) |
| `test_mcp_server.py` | MCP server integration (16 tests) |
| `conftest.py` | Shared fixtures |

## New Test Classes (Wave 6)

| Class | File | Tests |
|-------|------|-------|
| `TestPrefixedUnitConversions` | test_clicalc.py | 6 tests for prefixed units (kN, mV, mA, kW, MB, km) |
| `TestTemperatureConversions` | test_clicalc.py | 4 tests for exact temperature offsets (32F=0C, etc.) |
| `TestUnicodeScriptOther` | test_clicalc.py | 4 tests for unicode_script() returning "Other" |

## API Usage

### Use `evaluate()` for:
- Pure math expressions (`"5 + 3"`, `"2**10"`)
- Function calls (`"sin(0)"`, `"sqrt(16)"`)
- Constants (`"pi"`, `"e"`)

### Use `run()` or CLI for:
- Natural language (`"five plus three"`)
- Unit expressions (`"30m + 100ft"`)
- Complex expressions with units

### Use `convert_temperature()` for:
- Direct temperature conversions with offset handling
- `convert_temperature(32.0, "F", "C")` returns `0.0`

### Use `get_conversion_factor()` for:
- Prefixed unit conversion factors
- `get_conversion_factor("kN", "N")` returns `1000.0`

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

### Testing Temperature Conversions
```python
def test_fahrenheit_to_celsius_exact_freezing(self):
    """Test 32F to C equals exactly 0.0C."""
    from nl_calc.units import convert_temperature
    result = convert_temperature(32.0, "F", "C")
    assert abs(result - 0.0) < 1e-9
```

### Testing Unit Conversion Factors
```python
def test_kilonewton_to_newton(self):
    """Test kN to N conversion factor is 1000.0."""
    from nl_calc import get_conversion_factor
    result = get_conversion_factor("kN", "N")
    assert result == 1000.0
```

### Testing Unicode Script Detection
```python
def test_digits_return_other(self):
    """Test that ASCII digits return 'Other'."""
    from nl_calc.exact import unicode_script
    assert unicode_script("0") == "Other"
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

### Temperature Conversion
Temperature conversions require `convert_temperature()` for proper offset handling:
```python
from nl_calc.units import convert_temperature
result = convert_temperature(32.0, "F", "C")  # Returns 0.0
```

### Prefixed Units
Some prefixed units (like "kg") have compound meanings. Use `get_conversion_factor()` for prefix conversions:
```python
from nl_calc import get_conversion_factor
factor = get_conversion_factor("kN", "N")  # Returns 1000.0
```
