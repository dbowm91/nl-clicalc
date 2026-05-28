# units Module Review — Improvement Plan

**Reviewed:** architecture/units.md against nl_calc/units.py
**Date:** 2026-05-28

## Verified Claims (with line references)

### Key Exports (lines 15-26)
- `UnitValue` - **Verified** at units.py:24
- `normalize_unit` - **Verified** at units.py:1056
- `get_conversion_factor` - **Verified** at units.py:1100
- `get_all_units` - **Verified** at units.py:1293
- `is_unit` - **Verified** at units.py:1115
- `are_units_compatible` - **Verified** at units.py:1269
- `convert_temperature` - **Verified** at units.py:1079
- `FLOAT_EPSILON` - **Verified** at units.py:20

### UnitValue Class
- Constructor `UnitValue(value: float, unit: str | None = None)` - **Verified** at units.py:31
- Properties (value, unit) - **Verified** at units.py:32-33
- Methods: `convert_to(target_unit)` - **Verified** at units.py:134
- Arithmetic: `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__pow__` - **Verified** at units.py:58-111

### Temperature Conversions
All formulas in TEMPERATURE_CONVERSIONS verified correct:
- `convert_temperature(0, "C", "F")` → 32.0 ✓ (units.py:1068)
- `convert_temperature(100, "C", "F")` → 212.0 ✓
- `convert_temperature(0, "K", "C")` → -273.15 ✓ (units.py:1064)

### Unit Categories Table (lines 71-93)
- Most categories match code: Length, Time, Mass, Data, Volume, Pressure, Energy, Power, Speed, Temperature, Frequency, Force, Voltage, Current, Area, Data Rate
- Canonical forms: `kn` (not `knot`), `R` (not `Ra`)

### Functions
- `normalize_unit()` - **Verified** at units.py:1056
- `get_conversion_factor("km", "m")` → 1000.0 ✓
- `get_conversion_factor("ft", "m")` → 0.3048 ✓
- `is_unit()`, `are_units_compatible()`, `get_unit_category()`, `get_all_units()` - **Verified**

### Prefixed Units
- kN (kilonewton), mV (millivolt), mA (milliampere) - **All verified working**

## Discrepancies Between Documentation and Code

### HIGH Priority

- [HIGH] **Bug: Same-unit multiplication produces wrong unit**
  - Documentation says: `UnitValue * UnitValue` → "Compound (e.g., `m*m`)"
  - Code actually does: When units are the same (e.g., `m * m`), returns just `m` instead of `m*m` (units.py:89-90)
  - Impact: Mathematically incorrect - `2m * 2m` should equal `4 m²`, not `4 m`
  - Example: `UnitValue(2, "m") * UnitValue(2, "m")` returns `4 m` instead of `4 m*m`

- [HIGH] **Bug: Dead code in `convert_to()` - negative Kelvin warning unreachable**
  - Code location: units.py:146-162
  - The `elif self.value < 0 and self.unit in ("K", "kelvin", "kelvins") and self.value < 0:` branch (line 157) can never execute
  - Reason: When converting temperature to temperature (e.g., K to F), the function returns early at line 148 before reaching line 157
  - Impact: Code for negative Kelvin warning is dead code
  - Additionally: `self.value < 0` is checked twice (redundant)

### MEDIUM Priority

- [MEDIUM] **Conversion factor documentation has wrong value and direction**
  - Documentation says: `get_conversion_factor("kg", "lb") → 0.453592`
  - Code actually returns: `2.2046226218487757`
  - Reason: Docs show lb→kg factor but label it as kg→lb
  - Impact: User calling `get_conversion_factor("kg", "lb")` gets wrong value
  - Fix: Change to `get_conversion_factor("lb", "kg") → 0.453592` OR `get_conversion_factor("kg", "lb") → 2.20462`

- [MEDIUM] **Temperature-to-non-temperature warning is misleading**
  - Code location: units.py:149-156
  - Warning says "This may give physically meaningless results"
  - Code then calls `get_conversion_factor()` which raises `ValueError`
  - Impact: Warning suggests a bad result will be returned, but actually an exception is raised

- [MEDIUM] **Unit Categories table (lines 71-93) is incomplete**
  - Missing from Force: `dyne`, `lbf` (code has them at units.py:485-487)
  - Missing from Voltage: `μV`, `uV` variants (code has them at units.py:498-500)
  - Missing from Current: `μA`, `uA` variants (code has them at units.py:509-513)
  - Missing from Frequency: `THz` (code has at units.py:597)
  - Missing area variants: `m^2`, `km^2`, `sqft`, `sqin`, `sqmi`, `sqyd`, `sqm`
  - Missing data units: `EB`, `ZB`, `YB`, `bit`
  - Missing volume: `uL`, `μL`, `floz`, `fl oz`, `tbsp`, `tsp`
  - Missing time: `ps`, `fortnight`, `decade`, `century`, `millennium`

- [MEDIUM] **Key Exports missing `MAX_RESULT_VALUE`**
  - Documentation (lines 236-239) documents `MAX_RESULT_VALUE = 1e308`
  - But it's not listed in Key Exports section (lines 15-26)
  - Impact: Users don't know this constant is available

### LOW Priority

- [LOW] **Prefixed Units table (lines 219-232) is incomplete**
  - Only lists: milli, centi, deci, kilo, mega, giga, tera
  - Missing: micro (μ), nano (n), pico (p)
  - Example uses kN, mV, mA which are correct but not comprehensive

- [LOW] **Case sensitivity in normalize_unit**
  - `normalize_unit("kelvin")` → `"K"` (works)
  - `normalize_unit("Kelvin")` → `"Kelvin"` (case-sensitive, doesn't normalize)
  - `normalize_unit("KELVIN")` → `"KELVIN"` (case-sensitive)
  - Impact: Users must use exact case for proper normalization

- [LOW] **Rankine shown as "R" in docs but "Ra" alias not explained**
  - Code has `"Ra": "R"` in UNIT_ALIASES (line 980)
  - Docs only show "R" in table (line 86)
  - Impact: Minor confusion about canonical form

## Potential Bugs

### BUG 1: Same-unit multiplication produces mathematically incorrect result
- **Location**: units.py:89-90
- **Code**: `if self.unit == other.unit: return UnitValue(self.value * other.value, self.unit)`
- **Problem**: When multiplying `m * m`, should return `m*m` (or `m²`), not `m`
- **Fix**: Change to `return UnitValue(self.value * other.value, f"{self.unit}*{other.unit}")` when same unit

### BUG 2: Dead code - unreachable elif branch
- **Location**: units.py:157
- **Problem**: `elif self.value < 0 and self.unit in ("K", "kelvin", "kelvins") and self.value < 0:` is unreachable
- **Reason**: Early return at line 148 for temperature-to-temperature conversion
- **Fix**: Remove dead code, or restructure to handle this case

### BUG 3: Redundant condition
- **Location**: units.py:157
- **Problem**: `self.value < 0` checked twice in the same condition
- **Fix**: Remove duplicate check

## Improvement Suggestions

### HIGH Priority

1. **Fix same-unit multiplication bug** (units.py:89-90)
   - Change: `if self.unit == other.unit: return UnitValue(self.value * other.value, self.unit)`
   - To: `if self.unit == other.unit: return UnitValue(self.value * other.value, f"{self.unit}*{other.unit}")`
   - This ensures `m * m = m*m` (m squared) instead of just `m`

2. **Remove dead code in convert_to()** (units.py:157)
   - The negative Kelvin warning code is unreachable due to early return at line 148
   - Either remove it or restructure the logic to handle K→non-K temperature conversions with the warning

3. **Fix documentation for kg/lb conversion** (architecture/units.md:124)
   - Change: `get_conversion_factor("kg", "lb") → 0.453592`
   - To: `get_conversion_factor("kg", "lb") → 2.20462` OR `get_conversion_factor("lb", "kg") → 0.453592`

### MEDIUM Priority

4. **Update Unit Categories table with complete unit list**
   - Add missing Force units: dyne, lbf
   - Add missing Voltage units: μV, uV
   - Add missing Current units: μA, uA
   - Add THz to Frequency
   - Add area variants, data variants, volume variants, time variants

5. **Add `MAX_RESULT_VALUE` to Key Exports** (architecture/units.md:16-26)
   - Add `MAX_RESULT_VALUE` to the list of exported names

6. **Clarify temperature-to-non-temperature behavior** (units.py:149-156)
   - Either: Issue warning AND return a meaningless result (continue with factor-based conversion)
   - Or: Remove the misleading warning since ValueError is raised anyway

### LOW Priority

7. **Add micro, nano, pico to Prefixed Units table** (architecture/units.md:219-232)

8. **Consider case-insensitive normalization** (units.py:1056-1058)
   - Or document the case sensitivity behavior

9. **Update Prefixed Units examples** to include more prefix+unit combinations

## Summary

The units module is well-implemented with accurate temperature conversions and comprehensive unit coverage. Key issues found:

1. **Critical bug**: Same-unit multiplication (`m * m`) returns `m` instead of `m*m` (m squared)
2. **Critical bug**: Dead code in `convert_to()` - negative Kelvin warning unreachable
3. **Documentation error**: kg→lb conversion factor is wrong direction (shows 0.453592 which is lb→kg)
4. **Documentation gaps**: Many unit variants not listed in Unit Categories table
5. **Minor issues**: Case sensitivity, dead code, incomplete exports list

All temperature conversion formulas verified correct against code. The module is production-ready aside from the multiplication bug which should be fixed for mathematical correctness.
