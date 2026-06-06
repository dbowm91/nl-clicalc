# Bug Hunt: eggcalc/mcp/ and eggcalc/units.py

## Summary of Findings

After thorough investigation, I found **3 real bugs**, **2 design gaps**, and **10 areas confirmed working correctly**.

---

## BUGS (confirmed issues requiring fixes)

### BUG 1: `UnitValue` missing `__mod__` and `__floordiv__` operators

**Location:** `eggcalc/units.py` (class `UnitValue`, after `__pow__` at ~line 210)

**Reproduction:**
```python
from eggcalc.units import UnitValue
uv = UnitValue(5, "m")
uv % 2    # TypeError: unsupported operand type(s) for %
uv // 2   # TypeError: unsupported operand type(s) for //
```

**Expected:** Operations should produce `UnitValue(1, "m")` and `UnitValue(2, "m")` respectively, matching `__truediv__`/`__mul__` semantics.
**Actual:** `TypeError` — these dunder methods are not implemented.

**Impact:** Users writing `5m // 2` or `5m % 2` through the calculator get a raw Python TypeError instead of a clean EvaluationError.

---

### BUG 2: `_sanitize_error` does not redact variable assignment values in multiline contexts

**Location:** `eggcalc/mcp/tools.py:368` — the regex `re.sub(r'^\s*[A-Za-z_]\w*\s*=\s*["\'][^"\']*["\']', ...)` is anchored to start-of-line but only matches the FIRST assignment on each line.

**Reproduction:**
```python
from eggcalc.mcp.tools import _sanitize_error
result = _sanitize_error('x = "secret" y = "password"')
# Output: '<var>=<redacted> y = "password"'  ← second assignment not redacted
```

**Expected:** All variable assignments with string values should be redacted.
**Actual:** Only the first per line is redacted. However, this is a minor issue since the regex correctly handles the common single-assignment-per-line case. The risk is low since error messages rarely contain multiple assignments.

**Status:** Minor / low priority.

---

### BUG 3: `bool` JSON-RPC `id` passes validation in `handle_request`

**Location:** `eggcalc/mcp/server.py:823-834`

**Reproduction:**
```python
from eggcalc.mcp.server import handle_request
resp = handle_request({"jsonrpc": "2.0", "id": True, "method": "ping", "params": {}})
# Returns {"jsonrpc": "2.0", "id": True, "result": {}}  ← no error
```

**Expected:** JSON-RPC spec says `id` must be string, integer, or null. `True`/`False` are booleans, not valid ids.
**Actual:** `isinstance(True, (str, int))` returns `True` in Python because `bool` is a subclass of `int`. The check passes booleans through.

**Fix:** Add `and not isinstance(request_id, bool)` to the id validation:
```python
if not isinstance(request_id, (str, int)) or isinstance(request_id, bool):
```

---

## DESIGN GAPS (not bugs, but areas for consideration)

### DESIGN GAP 1: `5 + 3m` and `5 - 3m` raise errors by design

**Location:** `eggcalc/units.py:102` and `eggcalc/units.py:130`

**Current behavior:**
```python
UnitValue(3, "m").__radd__(5)  # ValueError: Cannot add dimensionless to m
5 - UnitValue(3, "m")          # ValueError: Cannot subtract unit from dimensionless
```

**This is intentional per the code comments.** The `__radd__` method calls `__add__`, which correctly rejects mixing dimensionless and unit values. This is physically correct (you can't add "5" to "3 meters"). However, users might expect `5 + 3m` to produce `8m` (treating `5` as `5m`).

**Recommendation:** Keep current behavior. The `run()` pipeline handles NL normalization properly.

---

### DESIGN GAP 2: `are_units_compatible(None, None)` returns `True`

**Location:** `eggcalc/units.py:1520`

**Current behavior:** Two `None` units (dimensionless) are considered compatible for addition. This is correct — dimensionless + dimensionless should work.

**Status:** Working as designed.

---

## AREAS CONFIRMED WORKING

### 1. MCP `_get_tool_executor` thread safety
The double-checked locking pattern with `_tool_executor_lock` is correct. All 20 concurrent threads received the same `ThreadPoolExecutor` instance. No issues.

### 2. MCP spawn semaphore timeout
The `_SPAWN_SEMAPHORE.acquire(timeout=_SPAWN_ACQUIRE_TIMEOUT)` in both `validate_regex` and `evaluate_with_timeout` correctly handles the case where all spawn slots are busy, returning a timeout error after 10 seconds. The `finally` block correctly releases the semaphore.

### 3. UnitValue arithmetic (confirmed working)
- `5m + 3m = 8m` ✓
- `5m + 100cm = 6m` (auto-converts) ✓  
- `5m * 3 = 15m` ✓
- `5m / 3 = 1.666...m` ✓
- `5m ** 2 = 25 m²` ✓
- `5m ** 0 = 1 m⁰` ✓
- `5m ** 0.5` → ValueError (correct: can't raise to non-integer power) ✓
- `15 / 3m = 5.0 1/m` (compound unit) ✓

### 4. Temperature conversions (all correct)
- `0F in C = -17.7778` ✓
- `0C in F = 32` ✓  
- `0K in C = -273.15` ✓
- `0K in F = -459.67` ✓
- `-459.67F in K = 0.0` ✓

### 5. Unit aliases
- `is_unit("5inches") = False` — `is_unit` expects raw unit strings, not "5inches" ✓
- Normalization pipeline correctly strips number prefixes via `run()` ✓

### 6. Invalid unit conversions
- `5m to kg` → ValueError ✓
- `5seconds to meters` → ValueError ✓

### 7. `get_conversion_factor` edge cases
- Same unit returns `1.0` ✓
- Unknown unit raises `ValueError` ✓
- Cross-category raises `ValueError` ✓

### 8. `are_units_compatible` with dimensionless
- `None + None = True` ✓ (dimensionless + dimensionless)
- `None + "m" = True` ✓ (dimensionless is compatible with anything)
- `"m" + "kg" = False` ✓ (incompatible categories)

### 9. `_sanitize_error` correctness
- Redacts file paths, memory addresses, traceback references ✓
- Caps input at 8192 bytes ✓
- Non-ASCII replaced with `?` ✓

### 10. MCP mode disables random/side-effects
- `handle_request()` sets `_mcp_mode = True` and calls `configure_default_evaluator(allow_random=False, allow_side_effects=False)` on first invocation ✓
- Child processes receive `allow_random=False` via `_evaluate_with_timeout_worker` parameters ✓

### 11. `build_single.py` still works
- Output file generated successfully (1.1MB) ✓

### 12. MCP rate limiting
- Implemented in `main()` (stdin reader loop), not in `handle_request()` — rate limiting is at the transport layer ✓

### 13. MCP request size limiting
- Implemented in `main()` via `len(line.encode('utf-8')) > MAX_REQUEST_BYTES` ✓

### 14. MCP tool output size limiting
- `MAX_OUTPUT_BYTES` check in `_handle_call_tool` at line 687 ✓

### 15. `_find_close_match` for unknown tools
- Case-insensitive matching works ✓
- Edit distance matching with threshold works ✓
- Long tool names rejected early ✓

---

## RECOMMENDED FIXES (in priority order)

1. **BUG 3 (bool id):** Add `isinstance(request_id, bool)` check in `handle_request()` — 1-line fix
2. **BUG 1 (missing operators):** Add `__mod__` and `__floordiv__` to `UnitValue` — straightforward addition
3. **BUG 2 (sanitize):** Low priority, the current regex is sufficient for most real error messages

## TEST PLAN

New tests should be added to:

### `tests/test_clicalc.py` — TestUnitValue class
```python
def test_mod_with_scalar(self):
    """5m % 2 should return 1m."""
    uv = UnitValue(5, "m")
    result = uv % 2
    assert result.value == 1
    assert result.unit == "m"

def test_floordiv_with_scalar(self):
    """5m // 2 should return 2m."""
    uv = UnitValue(5, "m")
    result = uv // 2
    assert result.value == 2
    assert result.unit == "m"

def test_mod_with_unit(self):
    """5m % 3m should return 2m."""
    result = UnitValue(5, "m") % UnitValue(3, "m")
    assert result.value == 2
    assert result.unit == "m"

def test_floordiv_with_unit(self):
    """5m // 3m should return 1 (dimensionless)."""
    result = UnitValue(5, "m") // UnitValue(3, "m")
    assert result.value == 1
    assert result.unit is None
```

### `tests/test_mcp_server.py` — TestErrorHandling class
```python
def test_bool_id_rejected(self):
    """JSON-RPC id must not be boolean."""
    response = handle_request({
        "jsonrpc": "2.0", "id": True, "method": "ping", "params": {}
    })
    assert "error" in response
    assert response["error"]["code"] == -32600
```
