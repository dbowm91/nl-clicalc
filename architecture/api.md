# api.md - Public API Surface

## Package Entry Point

`__init__.py` re-exports all public functionality from the nl_calc package.

## Core Evaluation Functions

### `evaluate(expression: str) -> Any`

Evaluate a **pre-normalized expression** (no spaces, no natural language).

```python
result = evaluate("5+3")  # 8
```

For maximum performance when input format is controlled.

### `evaluate_raw(expression: str) -> Any`

Evaluate a raw expression with **spaces and/or natural language**.

```python
result = evaluate_raw("five plus three")  # 8
result = evaluate_raw("30m + 100ft")      # 60.48 m
```

Full normalization pipeline.

### `evaluate_cached(expression: str) -> Any`

Like `evaluate_raw()` but with **LRU caching** (1024 entries).

```python
result = evaluate_cached("five plus three")  # Cached
```

### `evaluate_async(expression: str) -> Awaitable[Any]`

Async version of `evaluate_raw()` for async web frameworks.

```python
result = await evaluate_async("5 + 3")
```

### `evaluate_with_timeout(expression: str, timeout: float = 5.0) -> Any`

Timeout-protected evaluation for **untrusted input**.

```python
result = evaluate_with_timeout("2 ** 1000000", timeout=1.0)
# Raises TimeoutError
```

## Webapp Wrapper

### `PyCalcApp`

Thread-safe wrapper with caching, optimized for long-running applications.

```python
app = PyCalcApp(cache_size=1000)
result = app.calculate("5 + 3")
result = await app.calculate_async("five plus two")
```

Features:
- Instance-isolated constants/functions
- LRU cache with configurable size
- Async support

## Configuration Functions

### `register_constant(name: str, value: float) -> None`

Register a custom constant globally (thread-safe).

```python
register_constant("earth_radius", 6371)
```

### `register_function(name: str, func: Callable) -> None`

Register a custom function globally (thread-safe, call during init only).

```python
register_function("square", lambda x: x ** 2)
```

### `load_user_config() -> None`

Load configuration from `nl_calc_config.py` in working directory.

## Memory Functions

Calculator-style memory operations:

| Function | Description |
|----------|-------------|
| `memory_store(value, register="M")` | Store value |
| `memory_recall(register="M")` | Recall value |
| `memory_add(value, register="M")` | Add to memory (M+) |
| `memory_subtract(value, register="M")` | Subtract from memory (M-) |
| `memory_clear(register=None)` | Clear memory |
| `memory_list()` | List all registers |

## Variable Functions

User-defined variables:

| Function | Description |
|----------|-------------|
| `setvar(name, value)` | Set variable |
| `getvar(name)` | Get variable (returns 0 if not found) |
| `delvar(name)` | Delete variable |
| `listvars()` | List all variables |
| `clearvars()` | Clear all variables |

## Utility Functions

```python
normalize_unit("meters")          # "m"
get_conversion_factor("ft", "m")   # 0.3048
get_all_units()                    # ['A', 'B', 'BTU', ...]
is_unit("m")                       # True
```

## Types

### `UnitValue`

```python
uv = UnitValue(5, "m")
print(f"{uv}")        # "5 m"
print(uv.value)      # 5.0
print(uv.unit)       # "m"
```

### `EvaluationError`

Raised for invalid expressions or unsupported operations.

### `TimeoutError`

Raised when `evaluate_with_timeout()` exceeds timeout.

### `Memory`

Memory register class (returned by `memory_*` functions return floats, but `Memory` class available for type hints).

## Security Constants

```python
MAX_EXPONENT = 10000
MAX_FACTORIAL = 1000
MAX_NESTING_DEPTH = 100
MAX_RESULT_VALUE = 1e308
DEFAULT_CACHE_SIZE = 1024
```

## Performance Characteristics

| Method | Input Type | Typical Speed |
|--------|------------|---------------|
| `evaluate()` | Pre-normalized | ~10 μs/eval |
| `evaluate_raw()` | Natural language | ~155 μs/eval |
| `evaluate_cached()` | Repeated NL | ~0.1 μs/eval (after first) |
| `PyCalcApp.calculate()` | NL with caching | ~0.3 μs/eval (after first) |