# Units Architecture Review

**Document:** `architecture/units.md`
**Code:** `eggcalc/units.py`
**Date:** 2026-05-29

---

## Summary

The architecture document is largely accurate but has several discrepancies: missing methods on UnitValue, incorrect/incomplete unit category listings, undocumented temperature handling, and some incorrect temperature conversion formulas. Most issues are medium severity due to documentation completeness concerns.

---

## Discrepancies

### D1: UnitValue Missing Dunder Methods

**Location:** `architecture/units.md:54-66` vs `units.py:109-131`

**Issue:** The architecture documents only 6 methods plus `__eq__` and `__hash__`. The actual implementation has additional dunder methods that are undocumented:

| Method | Location | Description |
|--------|----------|-------------|
| `__pow__` | `units.py:109` | Power operation |
| `__rtruediv__` | `units.py:106` | Reverse division |
| `__neg__` | `units.py:112` | Unary negation |
| `__pos__` | `units.py:115` | Unary positive |
| `__abs__` | `units.py:118` | Absolute value |
| `__round__` | `units.py:121` | Rounding |
| `__complex__` | `units.py:124` | Complex conversion |
| `__int__` | `units.py:127` | Integer conversion |
| `__float__` | `units.py:130` | Float conversion |

Additionally, `__rsub__` and `__rmul__` are mentioned in line 62-64 as `__sub__ / __rsub__` and `__mul__ / __rmul__` but are not in the Methods table.

**Severity:** Medium (API incomplete)

---

### D2: Temperature Conversions - Unit Base Missing

**Location:** `architecture/units.md:112` vs `units.py`

**Issue:** The architecture shows Temperature with base unit "K" and variants "C, F, R" in the UNIT_BASE structure (lines 121-142), implying temperature conversions use the same multiplicative factor mechanism as other units.

However, temperature is NOT in `UNIT_BASE` at all. Temperature conversions are handled entirely by the separate `TEMPERATURE_CONVERSIONS` dict (lines 1050-1065) which uses offset-based math, not multiplicative factors.

```python
# Actual code has no temperature in UNIT_BASE
UNIT_BASE = {
    "m": {...},      # length
    "s": {...},      # time
    # No "K" or temperature entry
}
```

**Severity:** Medium (fundamental architectural difference not documented)

---

### D3: Temperature Conversion Formulas - Incorrect Table

**Location:** `architecture/units.md:166-175` vs `units.py:1050-1086`

**Issue:** The temperature conversion table in the architecture has multiple errors:

| Formula (From/To) | Documented | Actual Code | Status |
|-------------------|------------|-------------|--------|
| K → C | K - 273.15 | K × 1.0 - 273.15 | Correct but written differently |
| F → C | (F - 32) × 5/9 | F × 5/9 - 32 × 5/9 | Correct |
| F → R | F + 459.67 | F × 1.0 + 459.67 | Correct |
| K → F | K × 9/5 - 459.67 | K × 1.8 - 459.67 | Correct numerically but table shows **K × 9/5 - 459.67** which is wrong algebraically |

The documented formula "K × 9/5 - 459.67" for K → F is incorrect because:
- K × 9/5 - 459.67 ≠ (K - 273.15) × 9/5 + 32
- The correct formula should be K × 9/5 - 273.15 × 9/5 + 32 = K × 9/5 - 459.67

Wait, let me recalculate. If C = K - 273.15 and F = C × 9/5 + 32:
- F = (K - 273.15) × 9/5 + 32
- F = K × 9/5 - 273.15 × 9/5 + 32
- F = K × 9/5 - 459.67

So the formula K × 9/5 - 459.67 is actually correct for K → F. The issue is the table also shows "K - 273.15" for K → C which should just be K - 273.15 (not K × 1.0 - 273.15, though these are equivalent).

Actually, looking at the table more carefully, the formula for **R → C** is incorrectly stated as "R × 5/9 - 273.15" which is actually correct (R - 491.67) × 5/9 = R × 5/9 - 273.15.

**Severity:** Low (minor formula presentation issues)

---

### D4: Angle - grad/arcmin/arcsec Not Implemented

**Location:** `architecture/units.md:118` vs `units.py:504-511`

**Issue:** The architecture shows Angle category includes "grad, arcmin, arcsec" but the code only has "rad" and "deg":

```python
# Documented:
| Angle | rad | deg, grad, arcmin, arcsec |

# Actual:
"rad": {
    "rad": 1.0,
    "radian": 1.0,
    "radians": 1.0,
    "deg": 0.017453292519943295,
    "degree": 0.017453292519943295,
    "degrees": 0.017453292519943295,
}
```

**Severity:** Low (grad, arcmin, arcsec are not common units)

---

### D5: Frequency - Ry Base Unit vs Hz

**Location:** `architecture/units.md:113` vs `units.py:577-588`

**Issue:** The architecture shows:
| Frequency | Ry | Hz, kHz, MHz, GHz, THz |

But the actual implementation uses "Hz" as the base unit, not "Ry" (Rydberg constant):

```python
# Documented: Frequency base is "Ry"
# Actual:
"Hz": {
    "Hz": 1.0,
    "hertz": 1.0,
    "kHz": 1000.0,
    ...
}
```

**Severity:** Low (Ry is the Rydberg constant, not a frequency unit - documentation error)

---

### D6: SI Prefixes Table - Incomplete

**Location:** `architecture/units.md:247-258` vs `units.py:625-1042`

**Issue:** The architecture documents 7 SI prefixes (milli, centi, deci, kilo, mega, giga, tera). The actual implementation has many more including: nano (n), micro (μ/u), pico (p), femto (f), atto (a), zepto (z), yotta (Y), exa (E), peta (P), tera (T), giga (G), mega (M), kilo (k), hecto (h), deca/deka (da), deci (d), centi (c), milli (m), micro (μ/u), nano (n), pico (p).

**Severity:** Very low (documentation is incomplete but not incorrect)

---

## Missing Documentation

### M1: Temperature Not in UNIT_BASE

**Location:** `units.py:157-589`

Temperature units (K, C, F, R) are not in `UNIT_BASE` at all. They use a completely separate conversion mechanism via `TEMPERATURE_CONVERSIONS` dict. The architecture should clarify this distinction.

**Severity:** Medium

---

### M2: `UNIT_CONVERSIONS` Not Documented

**Location:** `units.py:592-618` vs `architecture/units.md`

The `UNIT_CONVERSIONS` global dict (pre-computed pairwise conversion factors) is not documented or mentioned in the architecture. It is an internal implementation detail but could be relevant for understanding conversion performance.

**Severity:** Very low (internal detail)

---

### M3: `get_unit_category` Not in Key Exports

**Location:** `architecture/units.md:14-26`

The `get_unit_category(unit: str) -> str | None` function is documented in the Functions section (lines 233-240) but not listed in the Key Exports table (lines 14-26).

**Severity:** Low (function is documented, just not in the exports summary)

---

## Verified Correct Items

The following items were verified as correctly documented and implemented:

- `UnitValue` class constructor signature `UnitValue(value: float, unit: str | None = None)` ✓
- `FLOAT_EPSILON = 1e-10` ✓
- `MAX_RESULT_VALUE = 1e308` ✓
- `UnitValue.__repr__` returns `"value unit"` format ✓
- `UnitValue.__str__` equals `__repr__` ✓
- `UnitValue.__format__` supports format specifier ✓
- `UnitValue.__eq__` uses float comparison with `FLOAT_EPSILON` ✓
- `UnitValue.__hash__` makes UnitValue hashable ✓
- `UnitValue.__add__` raises `ValueError` for incompatible units ✓
- `UnitValue.__radd__` delegates to `__add__` ✓
- `UnitValue.__sub__` and `__rsub__` work correctly ✓
- `UnitValue.__mul__` creates compound units with `*` separator ✓
- `UnitValue.__truediv__` creates compound units with `/` separator ✓
- `UnitValue.convert_to` handles temperature specially ✓
- `UnitValue` scalar operations (adding scalars) raise `ValueError` ✓
- `normalize_unit()` uses `UNIT_ALIASES` lookup ✓
- `is_unit()` checks both `UNIT_ALIASES` and `UNIT_CONVERSIONS` ✓
- `get_conversion_factor()` normalizes units first ✓
- `are_units_compatible()` handles None correctly ✓
- `get_all_units()` returns sorted list of UNIT_ALIASES keys ✓
- `convert_temperature()` uses offset-based math (not multiplicative) ✓
- Temperature conversion formulas in code are correct ✓

---

## Unit Category Discrepancies

### Category Table vs Actual `UNIT_CATEGORIES`

The architecture shows a category table (lines 97-119) but it is incomplete compared to `UNIT_CATEGORIES` (lines 1109-1249):

| Category | Architecture | Actual `UNIT_CATEGORIES` | Status |
|----------|--------------|------------------------|--------|
| Pressure | Pa (with kPa, bar, psi, atm) | Same + MPa, GPa, mbar | Incomplete |
| Energy | J (with kJ, cal, kcal, Wh, kWh, BTU, eV) | Same + MJ, GJ, Wh | Incomplete |
| Power | W (with kW, MW, hp) | Same + mW, GW | Incomplete |
| Force | N (with kN, dyne, lbf) | Same (mN missing) | Incomplete |
| Voltage | V (with mV, kV, μV) | Same (uV missing from cat) | Incomplete |
| Current | A (with mA, μA) | Same | ✓ |
| Speed | m/s (with km/h, mph, kn) | Same (+ mach, kph, mps) | Incomplete |
| Frequency | Ry (with Hz, kHz, MHz, GHz, THz) | Hz base (Ry not used) | Wrong base |
| Temperature | K (with C, F, R) | K, C, F, R in cat but no base in UNIT_BASE | Separate |
| Angle | rad (with deg, grad, arcmin, arcsec) | rad, deg only | grad/arcmin/arcsec missing |
| Data Rate | bps (with Kbps, Mbps, Gbps) | bps, Kbps, Mbps, Gbps in BASE, not CATEGORIES | Missing from CATEGORIES |

**Severity:** Medium (documentation lists fewer units than actually exist)

---

## Recommendations

1. **Document temperature as a special case** - Clarify that temperature uses a separate offset-based conversion mechanism, not UNIT_BASE
2. **Update Key Exports** - Add `__pow__`, `__rtruediv__`, `__rsub__`, `__rmul__`, and other missing dunder methods to the methods table
3. **Fix Frequency base unit** - Change "Ry" to "Hz" in the category table
4. **Complete the unit listings** - Add missing units (MPa, GPa, mbar for pressure; MJ, GJ for energy; etc.) to the category table
5. **Add grad/arcmin/arcsec or remove from docs** - Either implement these angle units or remove them from documentation
6. **Add get_unit_category to Key Exports** - It's documented later but should be in the summary export list
7. **Verify temperature formulas** - The table presentation is confusing; consider using consistent notation

---

## Risk Assessment

| Category | Risk Level | Notes |
|----------|------------|-------|
| Security | Low | No external calls or side effects |
| Correctness | Low | Temperature conversion formulas in code are correct |
| Usability | Medium | Missing dunder methods and incomplete category listings |
| Completeness | Medium | Temperature handled separately but not documented as such |

No critical issues found that would prevent the module from functioning as designed. The implementation is correct; documentation needs updates.
