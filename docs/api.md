# Python API

## Core Functions

### `evaluate(expression: str) -> Any`

Evaluate a pre-normalized expression (no spaces, no natural language).

```python
from nl_clicalc import evaluate

result = evaluate("5+3")
print(result)  # 8
```

### `evaluate_raw(expression: str) -> Any`

Evaluate a raw expression with spaces and/or natural language. Main function for user input.

```python
from nl_clicalc import evaluate_raw

result = evaluate_raw("5 + 3")        # 8
result = evaluate_raw("five plus 3")  # 8
result = evaluate_raw("30m + 100ft")  # UnitValue
```

### `evaluate_cached(expression: str) -> Any`

Like `evaluate_raw()` but with LRU caching for repeated expressions.

```python
from nl_clicalc import evaluate_cached

# First call computes
result = evaluate_cached("5 + 3")

# Second call uses cache
result = evaluate_cached("5 + 3")
```

### `evaluate_async(expression: str) -> Awaitable[Any]`

Async version for async web frameworks.

```python
import asyncio
from nl_clicalc import evaluate_async

async def main():
    result = await evaluate_async("5 + 3")
    print(result)

asyncio.run(main())
```

### `evaluate_with_timeout(expression: str, timeout: float = 5.0) -> Any`

Evaluate with timeout protection. Recommended for untrusted input.

```python
from nl_clicalc import evaluate_with_timeout, TimeoutError

try:
    result = evaluate_with_timeout("2 ** 1000000", timeout=1.0)
except TimeoutError:
    print("Evaluation timed out")
```

## PyCalcApp Class

Thread-safe wrapper for web applications with caching and instance isolation.

```python
from nl_clicalc import PyCalcApp

app = PyCalcApp(cache_size=1000)

# Basic usage
result = app.calculate("5 + 3")

# Natural language
result = app.calculate("five plus three")

# Units
result = app.calculate("30m + 100ft")

# Async
result = await app.calculate_async("5 + 3")

# Custom constants
app.register_constant("myconst", 42)
result = app.calculate("myconst")

# Custom functions
app.register_function("double", lambda x: x * 2)
result = app.calculate("double(5)")

# Cache management
print(app.cache_size)
app.clear_cache()
```

## Configuration

### `register_constant(name: str, value: float) -> None`

Register a custom constant globally (thread-safe).

```python
from nl_clicalc import register_constant, evaluate_raw

register_constant("earth_radius", 6371)
result = evaluate_raw("earth_radius")  # 6371
```

### `register_function(name: str, func: Callable) -> None`

Register a custom function globally. Only call during initialization.

```python
from nl_clicalc import register_function, evaluate_raw

def my_square(x, y):
    return x**2 + y**2

register_function("mysquare", my_square)
result = evaluate_raw("mysquare(3, 4)")  # 25
```

### `load_user_config() -> None`

Load configuration from `clicalc_config.py` in working directory.

```python
from nl_clicalc import load_user_config

load_user_config()
```

## Types

### `UnitValue`

Represents a numeric value with units.

```python
from nl_clicalc import UnitValue

uv = UnitValue(5, "m")
print(uv)        # "5 m"
print(uv.value)  # 5.0
print(uv.unit)   # "m"

# Operations
uv2 = UnitValue(100, "cm")
result = uv + uv2  # 6 m
```

### `EvaluationError`

Raised for invalid expressions.

```python
from nl_clicalc import evaluate_raw, EvaluationError

try:
    result = evaluate_raw("import os")
except EvaluationError as e:
    print(f"Error: {e}")
```

### `TimeoutError`

Raised when evaluation exceeds timeout.

```python
from nl_clicalc import evaluate_with_timeout, TimeoutError

try:
    result = evaluate_with_timeout("slow_expr", timeout=1.0)
except TimeoutError:
    print("Timed out")
```

## Utility Functions

### Unit Utilities

```python
from nl_clicalc import (
    normalize_unit,
    get_conversion_factor,
    get_all_units,
    is_unit,
)

# Normalize unit name
normalize_unit("meters")  # "m"

# Get conversion factor
get_conversion_factor("ft", "m")  # 0.3048

# List all units
units = get_all_units()

# Check if unit
is_unit("m")    # True
is_unit("xyz")  # False
```

## Memory Functions

```python
from nl_clicalc import (
    memory_store,
    memory_recall,
    memory_add,
    memory_subtract,
    memory_clear,
    memory_list,
)

memory_store(42)
memory_recall()     # 42
memory_add(8)       # Now 50
memory_subtract(5)  # Now 45
memory_clear()
```

## Variable Functions

```python
from nl_clicalc import (
    setvar,
    getvar,
    delvar,
    listvars,
    clearvars,
)

setvar("x", 10)
getvar("x")    # 10
listvars()     # {"x": 10}
delvar("x")
clearvars()
```

## Security Constants

```python
from nl_clicalc import (
    MAX_INPUT_LENGTH,
    MAX_NESTING_DEPTH,
    MAX_EXPONENT,
    MAX_FACTORIAL,
    MAX_RESULT_VALUE,
    DEFAULT_CACHE_SIZE,
)

print(MAX_INPUT_LENGTH)   # 10000
print(MAX_NESTING_DEPTH)  # 100
```
