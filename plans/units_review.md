# Units Module Review

## Summary

The units module is well-structured and mostly accurate in its documentation. Two bugs require attention: temperature conversions via `UnitValue.convert_to()` fail due to missing temperature entries in `UNIT_CONVERSIONS`, and `kilonewton` incorrectly maps to `N` instead of `kN`. The architecture document is largely correct but omits the separate `TEMPERATURE_CONVERSIONS` table.

---

## Verified Claims

| Claim | Status |
|-------|--------|
| `UnitValue` represents value + optional unit | Correct |
| `UNIT_BASE` maps base units to variants and factors | Correct |
| `UNIT_ALIASES` maps all variants to canonical forms | Correct |
| `UNIT_CONVERSIONS` pre-computed pairwise factors | Correct (but temperature entries missing) |
| Temperature uses offset-based calculations | Correct - `TEMPERATURE_CONVERSIONS` uses `(multiplier, offset)` formula |
| `are_units_compatible()` enables same-category operations | Correct |
| `FLOAT_EPSILON = 1e-10` | Correct |
| `MAX_RESULT_VALUE = 1e308` | Correct |

---

## Discrepancies

### 1. Temperature Not in `UNIT_CONVERSIONS`
**Documentation states:** `UNIT_CONVERSIONS` contains "Pre-computed pairwise conversion factors"

**Reality:** Temperature units (K, C, F, R) are NOT in `UNIT_CONVERSIONS`. Temperature conversion uses a separate `TEMPERATURE_CONVERSIONS` dict with `(multiplier, offset)` tuples.

**Impact:** Low - this is an implementation detail that doesn't affect users.

### 2. Missing Temperature Entry in Table
**Documentation shows:** A table of unit categories but doesn't list temperature conversions separately.

**Reality:** Temperature uses a special formula `result = value * multiplier + offset` with `TEMPERATURE_CONVERSIONS` dict.

---

## Bugs Found

### Bug 1: Temperature Conversion via `UnitValue.convert_to()` Fails - HIGH Priority

**Location:** `units.py:132-160` and `UNIT_CONVERSIONS`

**Problem:** `UnitValue.convert_to()` uses `get_conversion_factor()` which relies on `UNIT_CONVERSIONS`. Temperature units (K, C, F, R) are not in `UNIT_CONVERSIONS`, so temperature conversions fail:

```python
>>> uv = UnitValue(100, 'C')
>>> uv.convert_to('F')
ValueError: Cannot convert from C to F
```

**Correct behavior:** `convert_temperature(100, 'C', 'F')` correctly returns `212.0`.

**Fix:** `convert_to()` must check if the unit category is "temperature" and call `convert_temperature()` instead of using the multiplicative factor approach.

---

### Bug 2: `kilonewton` Alias Maps to `N` Instead of `kN` - MEDIUM Priority

**Location:** `units.py:922-923`

**Problem:**
```python
"kilonewton": "N",  # WRONG - should be "kN"
```

**Impact:** `normalize_unit("kilonewton")` returns `"N"` instead of `"kN"`. While both represent newtons, this is inconsistent - all other prefixed units (kPa, kV, kW, kJ) map to their prefixed canonical form.

**Fix:** Change line 923 to `"kilonewton": "kN",`

---

## Improvements

### Improvement 1: Add Temperature-Specific Path in `convert_to()` - MEDIUM Priority

**Rationale:** The current design conflates multiplicative conversions (m → ft) with offset-based temperature conversions (C → F). The `convert_to()` method should detect temperature conversions and route them through `convert_temperature()`.

**Current workaround:** Users must call `convert_temperature()` directly, which is not discoverable.

---

### Improvement 2: Document `TEMPERATURE_CONVERSIONS` in Architecture - LOW Priority

**Rationale:** The architecture doc shows a table of categories but doesn't explain that temperature conversions have a separate handling mechanism with offset math.

**Suggested addition:** Document that temperature conversions use `TEMPERATURE_CONVERSIONS` with formula `result = value * multiplier + offset`.

---

### Improvement 3: Consistent Prefix Handling - LOW Priority

**Rationale:** The `kilonewton` → `N` mapping is inconsistent with the pattern used by all other prefixed units. While not technically wrong (both resolve to the same base unit), it creates confusion.

---

## Priority Summary

| Item | Priority | Type |
|------|----------|------|
| Fix temperature `convert_to()` | HIGH | Bug |
| Fix `kilonewton` alias | MEDIUM | Bug |
| Add temperature path in `convert_to()` | MEDIUM | Improvement |
| Document `TEMPERATURE_CONVERSIONS` | LOW | Improvement |
| Consistency pass on aliases | LOW | Improvement |