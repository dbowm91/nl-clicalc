# Units Module Review - Improvement Plan

## Verified Claims (with code references)

### UnitValue Class
- Constructor `UnitValue(value: float, unit: str | None = None)` - **Verified** at `units.py:31`
- Arithmetic operations (+, -, *, /, **) - **Verified** at `units.py:58-111`
- `convert_to(target_unit)` method - **Verified** at `units.py:134-164`
- Automatic unit conversion on add/subtract - **Verified** at `units.py:58-79`

### Temperature Conversions
All formulas in TEMPERATURE_CONVERSIONS verified against documentation:
| From/To | Formula | Code Location |
|---------|---------|---------------|
| C → F | C × 9/5 + 32 | `units.py:1063` (1.8, 32.0) |
| F → C | (F - 32) × 5/9 | `units.py:1064` (1/1.8, -32/1.8) |
| K → C | K - 273.15 | `units.py:1059` (1.0, -273.15) |
| K → F | K × 9/5 - 459.67 | `units.py:1061` (1.8, -459.67) |
| K → R | K × 9/5 | `units.py:1065` (1.8, 0.0) |
| R → K | R × 5/9 | `units.py:1066` (1/1.8, 0.0) |
| C → R | (C + 273.15) × 9/5 | `units.py:1067` (1.8, 491.67) |
| R → C | R × 5/9 - 273.15 | `units.py:1068` (1/1.8, -273.15) |
| F → R | F + 459.67 | `units.py:1069` (1.0, 459.67) |
| R → F | R - 459.67 | `units.py:1070` (1.0, -459.67) |

### Key Functions
- `normalize_unit()` - **Verified** at `units.py:1051-1053`
- `get_conversion_factor()` - **Verified** at `units.py:1095-1107`
- `is_unit()` - **Verified** at `units.py:1110-1112`
- `are_units_compatible()` - **Verified** at `units.py:1264-1285`
- `get_unit_category()` - **Verified** at `units.py:1258-1261`
- `get_all_units()` - **Verified** at `units.py:1288-1289`
- `convert_temperature()` - **Verified** at `units.py:1074-1092`

### Unit Definitions
- Binary prefixes (1024) for data storage - **Verified** at `units.py:276` comment
- Decimal prefixes (1000) for data rate - **Verified** at `units.py:308` comment
- SI prefixes correctly applied across Voltage, Current, Power, Energy, Pressure, Frequency

## Discrepancies Between Documentation and Code

### HIGH PRIORITY

**1. Force Category Missing "dyne" and "lbf" (Documentation)**
- Documentation says: `Force | N | kN, mN`
- Code has at `units.py:477-487`: `N`, `kN`, `kilonewton`, `dyne`, `dynes`, `lbf`, `poundforce`
- **Issue**: "mN" (millinewton) missing from UNIT_BASE, "dyne" and "lbf" missing from docs

**2. Voltage Category Missing "uV" and "μV" (Documentation)**
- Documentation says: `Voltage | V | mV, kV`
- Code has at `units.py:488-499`: `V`, `kV`, `mV`, `uV`, `μV`, `microvolt`
- **Issue**: Microvolt variants missing from docs

**3. Current Category Missing "uA" and "μA" (Documentation)**
- Documentation says: `Current | A | mA, kA`
- Code has at `units.py:500-512`: `A`, `mA`, `uA`, `μA`, `microamp`, `microampere`
- **Issue**: Microamp variants missing from docs

**4. "acre" Missing from UNIT_ALIASES (Bug)**
- Code has `acre: 4046.8564224` in UNIT_BASE at `units.py:562`
- But `acre` and `acres` are NOT in UNIT_ALIASES at `units.py:995-1016`
- **Bug**: `normalize_unit("acre")` returns `"acre"` which may not find conversion

### MEDIUM PRIORITY

**5. Area Units in Documentation Incomplete**
- Documentation lists only: `m2`, `km2`, `cm2`, `mm2`, `ha`, `acre`, `ft2`, `in2`, `mi2`, `yd2`
- Code has at `units.py:540-584`: Also `m^2`, `km^2`, `cm^2`, `mm^2`, `ft^2`, `sqft`, `in^2`, `sqin`, `mi^2`, `sqmi`, `yd^2`, `sqyd`, `sqm`
- **Issue**: Many area variants not documented

**6. Speed "knot" vs "kn" Discrepancy**
- Documentation says: `Speed | m/s | km/h, mph, knot`
- Code uses `kn` as canonical (`units.py:534`), with `knot` and `knots` as aliases
- **Issue**: Documentation should reference "kn" as canonical

**7. Frequency "THz" Missing from Documentation**
- Documentation doesn't list THz in table or unit categories
- Code has `THz` at `units.py:595`

### LOW PRIORITY

**8. Unit Aliases Mapping Redundancy**
- Many entries like `"m": "m"`, `"km": "km"` map to themselves
- **Note**: These may be intentional for uniform lookups, not a bug

**9. MicroPrefix Inconsistency in Aliases**
- `"uV": "μV"` but `"μV": "μV"` - inconsistent direction
- `"uA": "μA"` but `"μA": "μA"` - inconsistent direction
- **Note**: Both directions normalized in practice

**10. Documentation Missing "Frequency" Base Unit**
- Table shows `"Frequency | Hz | kHz, MHz, GHz"` but doesn't mention THz

## Potential Bugs

### BUG 1: "acre" Not in UNIT_ALIASES (HIGH)
- **Location**: `units.py:631-1048`
- **Issue**: `acre` and `acres` defined in UNIT_BASE but not in UNIT_ALIASES
- **Impact**: `normalize_unit("acre")` returns `"acre"` which then fails conversion lookup
- **Fix**: Add `"acre": "acre"` and `"acres": "acre"` to UNIT_ALIASES

### BUG 2: Temperature Conversion Offset Precision (LOW)
- **Location**: `units.py:1056-1071`
- Some offsets like 255.372222 appear truncated (should be 255.372222...)
- **Impact**: Minor precision loss on reverse conversions
- **Fix**: Use more precise fractional representations where possible

## Improvement Suggestions

### HIGH PRIORITY

1. **Add "acre"/"acres" to UNIT_ALIASES** - Fixes conversion failure for acre units

2. **Update Documentation** - Sync Unit Categories table with actual code:
   - Force: `N | kN, dyne, lbf` (remove "mN", add "dyne", "lbf")
   - Voltage: `V | mV, kV, μV`
   - Current: `A | mA, kA, μA`
   - Add `THz` to Frequency
   - Add area variants (`m^2`, `sqft`, etc.)
   - Update Speed to show "kn" as canonical

### MEDIUM PRIORITY

3. **Add `mN` (millinewton) to Force category** if SI compliance desired
   - Currently missing from UNIT_BASE despite SI prefix support

4. **Clean up UNIT_ALIASES** - Consider removing self-mappings like `"m": "m"` for clarity
   - Though may be intentional for uniform dictionary behavior

5. **Add missing area units to UNIT_ALIASES**:
   - `sqft`, `sqin`, `sqmi`, `sqyd`, `sqm`

### LOW PRIORITY

6. **Refine Temperature Offset Precision** - Consider using Fraction for exact values:
   - `F → K`: Use `(value - 32) * 5/9 + 273.15` instead of pre-computed offset

7. **Consider Adding `acre` to UNIT_CATEGORIES** - Ensure `acre`/`acres` get correct category mapping

## Summary

The units module is generally well-implemented with accurate temperature conversions and comprehensive unit coverage. Main issues are:

1. **Critical bug**: `acre` missing from UNIT_ALIASES causes conversion failures
2. **Documentation gaps**: Many unit variants (μV, μA, THz, area variants) not documented
3. **Inconsistencies**: Some alias mappings are redundant or inconsistent in direction

All temperature conversion formulas verified correct against documentation.