# Testing Plan

## Overview

This plan establishes a comprehensive test infrastructure to ensure the validity and reliability of nl-clicalc. The primary motivation was the bug where `90-1` returned `901` instead of `89` - a simple but obvious bug that slipped through due to insufficient test coverage in tokenization. This plan addresses that gap and builds a robust testing foundation for future development.

## Goals

1. **Rule out edge case bugs** - Particularly in tokenization, unit conversion, and natural language parsing
2. **Establish baseline validity** - Prove that the calculator produces reliable outputs
3. **Enable confident development** - A well-tested base allows adding features without fear of breaking existing functionality

## Critical Learning: API Mismatch

### The Two APIs

**`evaluate()` (direct AST)** - For pure math only:
```python
from nl_calc import evaluate
evaluate("5 + 3")        # ✓ Works
evaluate("90-1")         # ✓ Works (after fix)
evaluate("2**10")        # ✓ Works
evaluate("sin(0)")       # ✓ Works
```

**`run()` (full pipeline)** - For NL and units:
```python
from nl_calc.normalize import run, NORMALIZE, PATTERNS
run("five plus three", NORMALIZE, PATTERNS)  # ✓ Works
run("30m + 100ft", NORMALIZE, PATTERNS)      # ✓ Works
```

### Common Mistake

Using `evaluate()` for NL or unit expressions **will fail**:
```python
evaluate("five plus three")  # ✗ SyntaxError - not valid Python
evaluate("1km in m")         # ✗ SyntaxError - km not valid identifier
evaluate("30m + 100ft")       # ✗ SyntaxError - m not valid identifier
```

### Why This Matters for Tests

When writing tests, you MUST use the correct API:
- **Mathematical expressions** (`5+3`, `2**10`, `sin(0)`) → `evaluate()`
- **Natural language** (`"five plus three"`) → `run()` or CLI
- **Unit expressions** (`"30m + 100ft"`) → `run()` or CLI

## Current State

### Test Files
- `tests/test_clicalc.py` - Main functional tests (708 lines, 15+ classes)
- `tests/test_security_fuzz.py` - Security and fuzz tests (489 lines, 4 classes)
- `tests/conftest.py` - Shared fixtures
- `tests/test_tokenization.py` - Tokenization edge cases (54 tests)
- `tests/test_math_identities.py` - Mathematical laws (28 tests)

### Test Results Summary

| Test File | Status | Notes |
|-----------|--------|-------|
| test_clicalc.py | 95 tests | Original tests - all pass |
| test_security_fuzz.py | 22 tests | Original tests - all pass |
| test_tokenization.py | 54 tests | NEW - all pass (regression for 90-1 bug) |
| test_math_identities.py | 28 tests | NEW - all pass |

### Well-Covered Areas
- Arithmetic (basic operations)
- Trigonometric functions
- Physical constants
- UnitValue class
- Complex numbers, bitwise, combinatorics, primes
- PyCalcApp caching and async
- Security (AST injection blocking)
- Tokenization (multi-digit operations, negative numbers, decimals)
- Mathematical identities (associativity, distributivity, etc.)

### What We Learned

**Unit conversion tests failed because wrong API was used:**
- Tests assumed `evaluate("1km in m")` would work
- Reality: This requires normalization pipeline (`run()`)
- The functionality WORKS - just not through `evaluate()`

**Natural language tests failed same way:**
- Tests assumed `evaluate("five plus three")` would work
- Reality: NL parsing happens before AST evaluation
- The functionality WORKS - just not through `evaluate()`

## Plan

### Phase 1: Verify Existing Test Suite (COMPLETED)

**Goal:** Confirm current tests actually work and provide baseline coverage.

1. Run full test suite with coverage report:
   ```bash
   python -m pytest tests/ --cov=nl_calc --cov-report=term-missing
   ```

2. Identify which areas pass/fail and document what gaps exist

3. Fix any broken or flaky tests

### Phase 2: Create Organized Test Structure (COMPLETED)

**Goal:** Create a more maintainable and scalable test organization.

**Current Structure:**
```
tests/
├── conftest.py             # Shared fixtures
├── test_clicalc.py         # Core tests (keep existing)
├── test_security_fuzz.py  # Security tests (keep existing)
├── test_tokenization.py   # Tokenization and parsing (54 tests)
└── test_math_identities.py# Mathematical laws (28 tests)
```

### Phase 3: Tokenization Tests (COMPLETED)

**Completed tests include:**
1. **Multi-digit subtraction** (regression for 90-1 bug)
2. **Chained operations** (`100-10-20-30`)
3. **Operator precedence**
4. **Negative numbers**
5. **Decimal numbers**
6. **Edge cases**

### Phase 4: Mathematical Identity Tests (COMPLETED)

**Completed tests include:**
1. **Addition laws** - commutative, associative, identity, inverse
2. **Multiplication laws** - commutative, associative, identity, inverse, distributive
3. **Power laws** - a^0, a^1, power multiplication, power of power
4. **Trigonometric identities** - sin²+cos²=1, tan=sin/cos
5. **Order of operations**
6. **Division laws**
7. **Special cases** - double negative, 0^0, 1^a, a^0.5

### Phase 5: Unit Conversion Tests (DEFERRED)

**Note:** Unit conversion tests require `run()` API, not `evaluate()`.
Tests using `evaluate("1km in m")` will fail - this is an API mismatch, not a bug.

Unit conversion functionality WORKS via `run()` and CLI.

### Phase 6: Natural Language Tests (DEFERRED)

**Note:** NL parsing tests require `run()` API, not `evaluate()`.
Tests using `evaluate("five plus three")` will fail - this is an API mismatch, not a bug.

NL functionality WORKS via `run()` and CLI.

### Phase 7: Documentation (IN PROGRESS)

**Goal:** Document test coverage and patterns for future contributors.

1. ✓ `AGENTS.md` created with testing guidelines
2. `plans/testing_plan.md` updated with learnings
3. `tests/README.md` documenting test conventions (TODO)

## Testing Patterns That Work

### Helper Functions
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

## Success Criteria

1. ✓ All existing tests pass (177 total)
2. ✓ Tokenization tests cover multi-digit operations
3. ✓ Mathematical identity tests verify core laws
4. Unit conversion tests require `run()` API (functionality exists, tests need rewrite)
5. NL tests require `run()` API (functionality exists, tests need rewrite)

## Testing Conventions

1. **Use `evaluate()` for:** Pure math expressions, function calls, constants
2. **Use `run()` or CLI for:** Natural language, unit expressions
3. **Always extract values:** Results may be `UnitValue` - use `get_value()` or `val()`
4. **Use parametrize:** For testing multiple inputs/outputs
5. **Keep tests focused:** One concept per test class

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
