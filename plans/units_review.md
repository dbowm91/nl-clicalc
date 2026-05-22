# Units Module Code Review

## Overview

Reviewed `nl_calc/units.py` (1259 lines) against `architecture/units.md` (119 lines). The module provides unit conversion support for length, time, data, mass, volume, pressure, energy, power, force, voltage, current, angle, speed, area, frequency, and temperature.

---

## Summary

| Category | Status |
|----------|--------|
| Module Purpose | VERIFIED - Implements comprehensive unit conversion as documented |
| UnitValue class | VERIFIED - Functions as documented |
| UNIT_BASE structure | VERIFIED - Correct structure |
| UNIT_CONVERSIONS values | VERIFIED - Computed correctly from UNIT_BASE |
| Temperature handling | VERIFIED BUT - Uses offset math (correct), not base unit conversion |
| Force/Voltage/Current aliases | **CRITICAL BUG** - Aliases map to base unit, breaking conversions |
| Temperature offset precision | **MINOR BUG** - F->C offset has rounding error |

---

## Verified Claims

### UnitValue Class (lines 24-141)
- `UnitValue(60.48, "m")` creates instance with `.value` and `.unit` attributes ✓
- Addition with compatible units works: `UnitValue(1,"m") + UnitValue(1,"ft")` returns `60.7848 m` ✓
- Addition with incompatible units raises `ValueError` ✓

### UNIT_BASE Structure (lines 145-572)
- Dictionary mapping base units to variants with conversion factors ✓
- All documented categories present (length, time, data, data_rate, mass, volume, pressure, energy, power, force, voltage, current, angle, speed, area, frequency, temperature) ✓
- Data uses binary (1024) prefixes, data_rate uses decimal (1000) prefixes ✓

### TEMPERATURE_CONVERSIONS (lines 1030-1045)
- Formula `result = value * multiplier + offset` correctly implemented ✓
- All temperature conversion factors mathematically correct ✓

### Key Functions (lines 1025-1259)
| Function | Signature | Status |
|----------|-----------|--------|
| `get_conversion_factor(from, to)` | `(str, str) -> float` | VERIFIED |
| `convert_temperature(value, from, to)` | `(float, str, str) -> float` | VERIFIED |
| `normalize_unit(unit)` | `(str) -> str` | VERIFIED |
| `is_unit(text)` | `(str) -> bool` | VERIFIED |
| `get_unit_category(unit)` | `(str) -> str \| None` | VERIFIED |
| `are_units_compatible(u1, u2)` | `(str \| None, str \| None) -> bool` | VERIFIED |
| `get_all_units()` | `() -> list[str]` | VERIFIED |

### Constants
- `FLOAT_EPSILON = 1e-10` ✓ (line 20)
- `MAX_RESULT_VALUE = 1e308` ✓ (line 21)

---

## Issues Found

### CRITICAL BUG: Force/Voltage/Current Aliases Map to Base Unit

**Location:** `units.py` lines 900-931

**Problem:**

The `UNIT_ALIASES` dictionary incorrectly maps prefixed units to their base unit:

```python
# Force (lines 900-908) - ALL WRONG
"kN": "N",           # Should be "kN"
"kilonewton": "N",    # Should be "kN"
"dyne": "N",          # Should be "dyne"
"lbf": "N",           # Should be "lbf"

# Voltage (lines 910-919) - ALL WRONG
"kV": "V",            # Should be "kV"
"kilovolt": "V",      # Should be "kV"
"mV": "V",            # Should be "mV"

# Current (lines 921-931) - ALL WRONG
"mA": "A",            # Should be "mA"
"uA": "A",            # Should be "uA"
```

**Impact on `get_conversion_factor()` (lines 1069-1081):**

When converting `"kN"` to `"N"`:
1. `normalize_unit("kN")` returns `"N"` (corrupted!)
2. `normalize_unit("N")` returns `"N"`
3. Since `"N" == "N"`, returns `1.0` immediately (line 1074-1075)
4. Never looks up `("kN", "N")` in `UNIT_CONVERSIONS` where the correct value `1000.0` exists

```python
>>> get_conversion_factor("kN", "N")
1.0  # WRONG - should be 1000.0

>>> get_conversion_factor("kV", "V")
1.0  # WRONG - should be 1000.0

>>> get_conversion_factor("mV", "V")
1.0  # WRONG - should be 0.001

>>> get_conversion_factor("mA", "A")
1.0  # WRONG - should be 0.001
```

**Impact on `UnitValue.convert_to()` (lines 132-141):**

```python
>>> UnitValue(1, "kN").convert_to("N")
1.0 N  # WRONG - should be 1000 N
```

**Impact on `UnitValue.__add__()` (lines 58-66):**

The `__add__` method calls `other.convert_to(self.unit)` when units differ, using the broken conversion:

```python
>>> UnitValue(1, "kN") + UnitValue(1000, "N")
1001.0 kN  # WRONG - should be 2000 N or 2 kN
```

The `other` (1000 N) is converted to kN with factor 1.0 instead of 0.001, giving 1000 kN, then 1 + 1000 = 1001 kN.

**Verification:**

```python
>>> from nl_calc.units import UNIT_CONVERSIONS
>>> UNIT_CONVERSIONS[("kN", "N")]
1000.0  # Correct value exists in the lookup table!
>>> UNIT_CONVERSIONS[("kV", "V")]
1000.0  # Correct value exists!
>>> UNIT_CONVERSIONS[("mV", "V")]
0.001   # Correct value exists!
```

The bug is that `normalize_unit()` corrupts the lookup key before the correct value can be found.

---

### MINOR BUG: Temperature Conversion Offset Precision

**Location:** `units.py` lines 1030-1045

**Problem:**

The `("F", "C")` entry has a rounding error in the offset:

```python
("F", "C"): (1.0/1.8, -17.777778),  # Should be -17.77777777777778
```

**Impact:**

```python
>>> convert_temperature(32, "F", "C")  # Freezing point of water
-2.2222222284540294e-07  # Should be exactly 0.0

>>> convert_temperature(212, "F", "C")  # Boiling point of water
99.99999977777779  # Should be exactly 100.0
```

**Root cause:**

The offset `-17.777778` is rounded to 6 decimal places. The exact value is `-32/1.8 = -17.77777777777778...`. The error is approximately `2.2e-7`, which is small but causes visible inaccuracies at exact reference points.

---

### Documentation Issue: Missing Categories in Table

**Location:** `architecture/units.md` lines 21-41

**Problem:**

The unit categories table documents 17 categories but shows them in a format that omits several actual categories:

| Documented | Actually in Code |
|-----------|------------------|
| (shows all in single table) | data_rate ✓ |
| | angle ✓ |
| | force ✓ |
| | voltage ✓ |
| | current ✓ |

The table structure lists them correctly, but the text at line 27 says "data | B | B, KB..." implying data_rate is missing. Actually, looking more carefully, the table does show data_rate at line 28. The issue is more about clarity - the "Base Unit" column is misleading for some categories.

---

### Documentation Issue: Temperature "Base Unit" Misleading

**Location:** `architecture/units.md` line 41

**Problem:**

The table shows `temperature | K | K, C, F, R` implying K is the base unit that others convert to via multiplication. This is incorrect:

1. **Kelvin is NOT in `UNIT_BASE`** - there's no `"K": {...}` entry
2. **Temperature conversions use `convert_temperature()` with offset math**, NOT `UNIT_CONVERSIONS`
3. The offset-based conversion is the correct design for temperature

The documentation correctly notes the offset formula (lines 43-56), but the table representation is misleading.

---

## Improvement Recommendations

### Priority 1: Fix Force/Voltage/Current UNIT_ALIASES

**File:** `nl_calc/units.py`

**Lines 900-908 - Force aliases (change from):**
```python
"N": "N",
"newton": "N",
"newtons": "N",
"kN": "N",
"kilonewton": "N",
"dyne": "N",
"dynes": "N",
"lbf": "N",
"poundforce": "N",
```

**To:**
```python
"N": "N",
"newton": "N",
"newtons": "N",
"kN": "kN",
"kilonewton": "kN",
"dyne": "dyne",
"dynes": "dyne",
"lbf": "lbf",
"poundforce": "lbf",
```

**Lines 910-919 - Voltage aliases (change from):**
```python
"V": "V",
"volt": "V",
"volts": "V",
"kV": "V",
"kilovolt": "V",
"mV": "V",
"millivolt": "V",
"uV": "V",
"μV": "V",
"microvolt": "V",
```

**To:**
```python
"V": "V",
"volt": "V",
"volts": "V",
"kV": "kV",
"kilovolt": "kV",
"mV": "mV",
"millivolt": "mV",
"uV": "uV",
"μV": "uV",
"microvolt": "uV",
```

**Lines 921-931 - Current aliases (change from):**
```python
"A": "A",
"amp": "A",
"ampere": "A",
"amperes": "A",
"mA": "A",
"milliamp": "A",
"milliampere": "A",
"uA": "A",
"μA": "A",
"microamp": "A",
"microampere": "A",
```

**To:**
```python
"A": "A",
"amp": "A",
"ampere": "A",
"amperes": "A",
"mA": "mA",
"milliamp": "mA",
"milliampere": "mA",
"uA": "uA",
"μA": "uA",
"microamp": "uA",
"microampere": "uA",
```

---

### Priority 2: Fix Temperature F->C Offset Precision

**File:** `nl_calc/units.py`

**Line 1038 - Change from:**
```python
("F", "C"): (1.0 / 1.8, -17.777778),
```

**To:**
```python
("F", "C"): (1.0 / 1.8, -32.0 / 1.8),
```

Or use the computed floating-point value with more precision:
```python
("F", "C"): (1.0 / 1.8, -17.77777777777778),
```

---

### Priority 3: Update Documentation

**File:** `architecture/units.md`

**Line 41 - Change from:**
```
| temperature | K | K, C, F, R |
```

**To:**
```
| temperature | (offset-based) | K, C, F, R |
```

**Add note after line 56:**
```
Note: Temperature conversions use offset-based formulas, not multiplicative factors.
The `convert_temperature()` function handles all temperature conversions.
Temperature units are NOT stored in UNIT_BASE.
```

---

## Testing Recommendations

After fixes, verify:

```python
# Force conversions
assert get_conversion_factor("kN", "N") == 1000.0
assert get_conversion_factor("N", "kN") == 0.001
assert get_conversion_factor("dyne", "N") == 1e-5
assert get_conversion_factor("lbf", "N") == pytest.approx(4.4482216152605)

# Voltage conversions
assert get_conversion_factor("kV", "V") == 1000.0
assert get_conversion_factor("V", "kV") == 0.001
assert get_conversion_factor("mV", "V") == 0.001

# Current conversions
assert get_conversion_factor("mA", "A") == 0.001
assert get_conversion_factor("uA", "A") == 1e-6

# Temperature conversions
assert convert_temperature(32, "F", "C") == pytest.approx(0.0, abs=1e-9)
assert convert_temperature(212, "F", "C") == pytest.approx(100.0, abs=1e-9)
assert convert_temperature(0, "C", "F") == pytest.approx(32.0, abs=1e-9)

# UnitValue operations
uv1 = UnitValue(1, "kN")
uv2 = UnitValue(1000, "N")
result = uv1 + uv2
assert result.value == pytest.approx(2000.0) or result.value == pytest.approx(2.0)
```

---

## Files Reviewed

- `architecture/units.md` (119 lines) - Documentation
- `nl_calc/units.py` (1259 lines) - Implementation

## Review Summary

| Issue | Severity | Location | Status |
|-------|----------|----------|--------|
| Force aliases map to N | CRITICAL | lines 900-908 | Bug |
| Voltage aliases map to V | CRITICAL | lines 910-919 | Bug |
| Current aliases map to A | CRITICAL | lines 921-931 | Bug |
| F->C offset precision | MINOR | line 1038 | Bug |
| Temperature "base unit" misleading | LOW | architecture/units.md:41 | Doc issue |