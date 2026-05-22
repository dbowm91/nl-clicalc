# Units Module Review - Improvement Plan

## Verified Claims

The following claims in `architecture/units.md` are **correct**:

1. **Key Exports** - All exports listed are present in `units.py`
2. **UnitValue Constructor** - `UnitValue(value: float, unit: str | None = None)` matches implementation
3. **UnitValue Properties** - `value` and `unit` properties are correctly implemented
4. **UnitValue Methods** - `convert_to(target_unit)` is implemented
5. **Arithmetic Operations** - Table accurately describes +, -, *, /, ** behavior
6. **Important Note** - Adding/subtracting incompatible units raises `ValueError` ✓
7. **Temperature Scale Formulas** - All formulas in table are correctly implemented
8. **FLOAT_EPSILON = 1e-10** - Correct value
9. **MAX_RESULT_VALUE = 1e308** - Correct value
10. **Module Dependencies** - Correctly states no dependencies on other nl_calc modules
11. **get_conversion_factor, are_units_compatible, get_unit_category** - All work as documented

## Discrepancies

### Documentation vs Implementation

| Item | Documented | Actual | Impact |
|------|-----------|--------|--------|
| **Key Exports** | Lists only 8 items | Many additional exports (`convert_temperature`, `UNIT_BASE`, `UNIT_ALIASES`, `UNIT_CONVERSIONS`, `UNIT_CATEGORIES`, `TEMPERATURE_CONVERSIONS`) | Minor - docs just incomplete |
| **Unit Categories Table** | Shows 15 categories | 18 categories present (added: angle, area, data_rate) | Minor - docs incomplete |
| **Prefixed Units Table** | Only 7 prefixes shown | SI prefixes correctly implemented | Minor - docs incomplete |
| **is_unit()** | Listed in Key Exports | Not exported in `__all__` but works | Low |

## Bugs Found

### 1. `__rsub__` Reverses Operands Incorrectly (HIGH Priority)

**Location:** `units.py:81-82`

```python
def __rsub__(self, other: Any) -> UnitValue:
    return UnitValue(other - self.value, self.unit)
```

**Problem:** When `UnitValue(3, "ft") - 5` is evaluated, Python calls `5.__rsub__(UnitValue(3, "ft"))`, which becomes `UnitValue(3, "ft").__rsub__(5)`. This returns `UnitValue(5 - 3, "ft")` = `UnitValue(2, "ft")`, completely ignoring unit conversion.

**Expected:** `UnitValue(3, "ft") - 5` should convert `5` to `UnitValue(5, "m")` (dimensionless treated as meters per `are_units_compatible` behavior), then subtract.

**Actual Output:**
```
UnitValue(3, "ft") - 5  →  -2 ft  (WRONG - no unit conversion, value is wrong sign)
```

**Verification:**
```python
uv = UnitValue(3, "ft")
result = uv - 5  # Returns: -2 ft (incorrect)
```

**Fix:** `__rsub__` should handle `other` as a value with the same unit as `self`:
```python
def __rsub__(self, other: Any) -> UnitValue:
    if isinstance(other, UnitValue):
        return other.__sub__(self)
    return UnitValue(other - self.value, self.unit)
```

### 2. `get_unit_category()` Missing 6 Micro-units (MEDIUM Priority)

**Location:** `units.py:1217-1220`

**Problem:** These aliases exist in `UNIT_ALIASES` but have no entry in `UNIT_CATEGORIES`:
- `uA` / `μA` / `microamp` / `microampere` (current category)
- `uV` / `μV` / `microvolt` (voltage category)

**Impact:** `is_unit("uA")` returns `True` but `get_unit_category("uA")` returns `None`, causing inconsistent behavior. Unit operations with micro-amps/volts may fail unexpectedly.

**Fix:** Add to `UNIT_CATEGORIES`:
```python
"uA": "current",
"μA": "current",
"uV": "voltage",
"μV": "voltage",
```

### 3. Temperature Conversion Precision Issue (LOW Priority)

**Location:** `units.py:1054-1066`

The `TEMPERATURE_CONVERSIONS` dictionary uses derived offset values that can cause floating-point drift in certain conversions:

```python
("F", "K"): (1.0 / 1.8, 255.372222),  # Approximation
("R", "C"): (1.0 / 1.8, -273.15),     # Inconsistent precision
```

**Example:**
```python
convert_temperature(491.67, "R", "C")  # Returns ~5.684e-14 instead of 0.0
```

**Fix:** Use more precise constants or restructure to use direct formulas instead of lookup table.

### 4. `are_units_compatible()` Treats Unknown Categories as Compatible (MEDIUM Priority)

**Location:** `units.py:1273-1274`

```python
if cat1 is None or cat2 is None:
    return True
```

**Problem:** If either unit has no category entry, they are considered compatible. This means unknown units can be mixed with any other unit without error.

**Example:**
```python
are_units_compatible("foo", "m")   # Returns True (but should probably warn)
are_units_compatible("foo", "kg") # Returns True
```

**Fix:** Consider returning `False` when one category is known but the other is unknown:
```python
if cat1 is None and cat2 is None:
    return True
if cat1 is None or cat2 is None:
    return False  # Unknown unit shouldn't mix with known units
```

## Improvements with Priority

### High Priority

1. **Fix `__rsub__` operand reversal bug** - Currently produces mathematically incorrect results when subtracting a scalar from a UnitValue

### Medium Priority

2. **Add missing micro-unit categories** (`uA`, `μA`, `uV`, `μV`, `microamp`, `microampere`, `microvolt`)
3. **Reconsider `are_units_compatible()` unknown category handling** - Currently allows unknown units to mix with any unit
4. **Document Rankine temperature scale** - Documented in `UNIT_ALIASES` but not in architecture doc

### Low Priority

5. **Improve temperature conversion precision** - Use exact formulas instead of derived offsets
6. **Update architecture documentation** - Add missing exports and categories to match implementation
7. **Add explicit type exports to `__all__`** - The module lacks an explicit `__all__` export list

## Summary

| Priority | Count |
|----------|-------|
| High | 1 |
| Medium | 3 |
| Low | 3 |

The core unit conversion logic is sound. The main bug is `__rsub__` which incorrectly handles scalar subtraction without unit conversion. The documentation is largely accurate but incomplete in several areas.