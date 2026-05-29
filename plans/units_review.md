# units.py Architecture Review

## Overview

This document reviews `architecture/units.md` against the actual implementation in `nl_calc/units.py` (1286 lines).

---

## Verified Claims

### Key Exports
| Claim | Status | Notes |
|-------|--------|-------|
| `UnitValue` | MATCHES | Class defined at line 24 |
| `normalize_unit` | MATCHES | Function at line 1047 |
| `get_conversion_factor` | MATCHES | Function at line 1091 |
| `get_all_units` | MATCHES | Function at line 1284 |
| `is_unit` | MATCHES | Function at line 1106 |
| `are_units_compatible` | MATCHES | Function at line 1260 |
| `convert_temperature` | MATCHES | Function at line 1070 |
| `FLOAT_EPSILON` | MATCHES | Constant at line 20 (value 1e-10) |

### UnitValue Class Properties
| Property | Status |
|----------|--------|
| `value` (float) | MATCHES |
| `unit` (str \| None) | MATCHES |

### UnitValue Methods
| Method | Status |
|--------|--------|
| `convert_to(target_unit)` | MATCHES |
| `__repr__()` | MATCHES |
| `__str__()` | MATCHES |
| `__format__(format_spec)` | MATCHES |
| `__eq__(other)` | MATCHES |
| `__hash__()` | MATCHES |
| `__add__ / __radd__` | MATCHES |
| `__sub__ / __rsub__` | MATCHES |
| `__mul__ / __rmul__` | MATCHES |
| `__truediv__` | MATCHES |

### UnitValue Arithmetic (lines 67-76)
| Operation | Result Unit | Notes |
|-----------|-------------|-------|
| `UnitValue + UnitValue` | Common unit | MATCHES - converts if compatible |
| `UnitValue - UnitValue` | Common unit | MATCHES - converts if compatible |
| `UnitValue * UnitValue` | Compound (e.g., `m*m`) | MATCHES |
| `UnitValue / UnitValue` | Compound (e.g., `m/s`) | MATCHES |
| `UnitValue ** n` | Same unit | MATCHES - power of value, keeps unit |

### Unit Categories Table
| Category | Base Unit | Status |
|----------|-----------|--------|
| Length | m | MATCHES |
| Time | s | MATCHES |
| Mass | kg | MATCHES |
| Data | B | MATCHES |
| Volume | L | MATCHES |
| Pressure | Pa | MATCHES |
| Energy | J | MATCHES |
| Power | W | MATCHES |
| Speed | m/s | MATCHES |
| Temperature | K | MATCHES |
| Frequency | Hz | MATCHES |
| Force | N | MATCHES |
| Voltage | V | MATCHES |
| Current | A | MATCHES |
| Area | m2 | MATCHES |
| Data Rate | bps | MATCHES |

### Temperature Scale Formulas
The table in the doc (lines 147-157) accurately describes the conversion formulas. Each formula is encoded in `TEMPERATURE_CONVERSIONS` (lines 1052-1067).

### Prefixed Units
The document lists 7 SI prefixes (lines 230-238). The actual implementation handles these but through explicit definitions in `UNIT_BASE` and `UNIT_ALIASES`, not a separate prefix system. **MATCHES** in spirit.

### Constants
| Constant | Documented | Actual | Status |
|----------|------------|--------|--------|
| `FLOAT_EPSILON` | 1e-10 | 1e-10 | MATCHES |
| `MAX_RESULT_VALUE` | 1e308 | 1e308 | MATCHES |

---

## Discrepancies Found

### 1. Unit Categories Table - Missing Categories
**Severity: LOW** (documentation issue)

The document's Unit Categories table (lines 79-101) lists 16 categories but is missing:
- **Angle** (rad, deg)
- **Anglular** is not listed as a category

The actual code includes radians/degrees in `UNIT_BASE` (lines 506-513) and `UNIT_CATEGORIES` (lines 1224-1225).

### 2. Document Lists `FLOAT_EPSILON` and `MAX_RESULT_VALUE` as Exports
**Severity: LOW** (documentation completeness)

The Key Exports section doesn't list these constants, though they are important constants defined in the module.

---

## Bugs Identified

### BUG 1: `__rsub__` with scalar ignores dimensional analysis
**Severity: HIGH** | **Line: 81-84**

```python
def __rsub__(self, other: Any) -> UnitValue:
    if isinstance(other, UnitValue):
        return other.__sub__(self)
    return UnitValue(other - self.value, self.unit)  # BUG: scalar + dimensional = error
```

When `other` is a scalar (e.g., `5 - UnitValue(3, "m")`), the code returns `UnitValue(2, "m")`, treating the scalar as having the same unit. This is physically incorrect and should raise `ValueError`.

**Reproduction:**
```python
from nl_calc.units import UnitValue
result = 5 - UnitValue(3, "m")  # Returns UnitValue(2, "m") - INCORRECT
```

**Expected:** Should raise `ValueError` (incompatible units: dimensionless - length).

---

### BUG 2: `__add__` with scalar ignores dimensional analysis
**Severity: HIGH** | **Line: 66**

```python
def __add__(self, other: Any) -> UnitValue:
    if isinstance(other, UnitValue):
        ...
    return UnitValue(self.value + other, self.unit)  # BUG: scalar added to dimensional value
```

When `other` is a scalar (e.g., `UnitValue(3, "m") + 5`), the code returns `UnitValue(8, "m")`. This should raise an error since you cannot add a dimensionless quantity to a dimensional one.

**Reproduction:**
```python
from nl_calc.units import UnitValue
result = UnitValue(3, "m") + 5  # Returns UnitValue(8, "m") - INCORRECT
```

**Fix:** Check if `other` is a UnitValue AND if it's dimensionless (unit is None), converting that case correctly. But non-UnitValue scalars should raise `ValueError` since they're dimensionless.

---

### BUG 3: `__eq__` returns `NotImplemented` for same-value different-unit comparison
**Severity: MEDIUM** | **Line: 48-53**

```python
def __eq__(self, other: object) -> bool:
    if not isinstance(other, UnitValue):
        return NotImplemented
    if self.unit != other.unit:
        return NotImplemented  # Should return False
    return abs(self.value - other.value) < FLOAT_EPSILON
```

When comparing `UnitValue(5.0, "m") == UnitValue(5.0, "ft")`, the method returns `NotImplemented` instead of `False`. This violates equality contract expectations - comparisons should return `True`, `False`, or `NotImplemented`, but returning `NotImplemented` for same-value different-unit comparison is unexpected.

**Impact:** `UnitValue(5, "m") == UnitValue(5, "ft")` returns `NotImplemented` (a truthy value), making the objects appear equal in boolean context, but Python's comparison machinery will try reflected comparison which may yield inconsistent results.

**Fix:** Return `False` when units differ but values are same.

---

## Improvements Suggested

### IMPROVEMENT 1: Document `__rsub__` anomaly for scalar subtraction
**Priority: LOW**

The current behavior of `5 - UnitValue(3, "m")` returning `UnitValue(2, "m")` is mathematically questionable. Either:
1. Document this as intentional behavior
2. Raise `ValueError` for scalar + dimensional operations (recommended fix)

### IMPROVEMENT 2: Improve documentation completeness for Angle category
**Priority: LOW**

The architecture document should include the Angle category in the Unit Categories table.

### IMPROVEMENT 3: Add conversion factor cache warming note
**Priority: LOW**

The `UNIT_CONVERSIONS` cache is rebuilt at module load via `_rebuild_conversions()` (line 620). If new units are added to `UNIT_BASE` at runtime, the cache must be manually rebuilt via `_rebuild_conversions()`. This is mentioned in comment (line 615) but not documented.

---

## Priority Summary

| Priority | Item | Type |
|----------|------|------|
| HIGH | Fix `__rsub__` scalar + dimensional bug | Bug |
| HIGH | Fix `__add__` scalar + dimensional bug | Bug |
| MEDIUM | Fix `__eq__` NotImplemented for different units | Bug |
| LOW | Document Angle category in Unit Categories table | Improvement |
| LOW | Document scalar + UnitValue behavior (or fix it) | Improvement |
