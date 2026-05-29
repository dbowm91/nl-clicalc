# Unit Testing Patterns for nl-clicalc

## Purpose
Guide agents on writing and running tests for this codebase.

## Critical API Distinction

**ALWAYS use the correct API or tests will fail:**

| Test Type | Use This API | Why |
|-----------|--------------|-----|
| Mathematical operations (`5+3`, `2**10`) | `evaluate()` | Direct AST parsing |
| Natural language (`"five plus three"`) | CLI or `run()` | Requires normalization |
| Unit conversions with operators | CLI or `run()` | Requires normalization |
| NL input with units (`"30m + 100ft"`) | CLI or `run()` | Requires normalization |

## Wrong Usage (Will Fail)
```python
# WRONG - evaluate() doesn't handle NL
evaluate("five plus three")
evaluate("1km in m")
evaluate("30m + 100ft")
```

## Correct Usage
```python
# For pure math - use evaluate()
from nl_calc import evaluate
result = evaluate("5 + 3")  # Works

# For NL or units - use run() or CLI
from nl_calc import run, NORMALIZE, PATTERNS
result = run("five plus three", NORMALIZE, PATTERNS)

# From CLI
import subprocess
result = subprocess.run(["python", "-m", "nl_calc", "5+3"], capture_output=True)
```

## Testing Helper Patterns

### Extracting Values from UnitValue
```python
from nl_calc import evaluate, UnitValue

def get_value(result):
    """Extract numeric value from result, handling UnitValue."""
    if isinstance(result, UnitValue):
        return result.value
    return result

def val(expr):
    """Evaluate and extract value, handling UnitValue."""
    result = evaluate(expr)
    return get_value(result)
```

### Verifying Unit Conversions
```python
from nl_calc.units import get_conversion_factor, UnitValue

# Direct conversion factor check
factor = get_conversion_factor("km", "m")
assert factor == 1000.0

# UnitValue operations
uv1 = UnitValue(1, "kN")
uv2 = UnitValue(1000, "N")
result = uv1 + uv2
# Should be 2000 N or 2 kN (not 1001 kN!)
```

### Testing Error Cases
```python
import pytest
from nl_calc import evaluate

def test_invalid_expression():
    with pytest.raises(EvaluationError):
        evaluate("5 +")  # Incomplete expression

def test_overflow():
    with pytest.raises(EvaluationError):
        evaluate("10 ** 10000")  # Exponent too large
```

## Running Tests
```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_clicalc.py

# Specific test
python -m pytest tests/test_clicalc.py::test_function_name

# With verbose output
python -m pytest tests/ -v
```

## Test File Structure
```
tests/
├── conftest.py              # Shared fixtures
├── README.md                # Test documentation
├── test_clicalc.py          # Core functional tests
├── test_security_fuzz.py   # Security/fuzz tests
├── test_tokenization.py    # Tokenization edge cases
├── test_math_identities.py  # Mathematical laws verification
├── test_mcp_server.py       # MCP server integration tests
├── test_exact.py            # Exact module tests
└── test_cli_text.py        # CLI text tools tests
```

## Current Test Count
- 352 tests pass (as of latest run)
- All must continue to pass

## Common Issues When Testing
1. Using `evaluate()` for NL input → KeyError or parse errors
2. Using `evaluate()` for unit expressions → fails to recognize units
3. Forgetting to extract `.value` from `UnitValue` for numeric comparisons
4. Not accounting for floating-point precision in comparisons (use `pytest.approx`)