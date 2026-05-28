# units Module Review — Improvement Plan

**Reviewed:** architecture/units.md against nl_calc/units.py
**Date:** 2026-05-28

## Verified Claims (with line references)

- `UnitValue` class exported — VERIFIED at code line 24
- `normalize_unit(unit: str) -> str` — VERIFIED at code line 1056
- `get_conversion_factor(from_unit, to_unit) -> float` — VERIFIED at code line 1100
- `get_all_units() -> list[str]` — VERIFIED at code line 1293
- `is_unit(s: str) -> bool` — VERIFIED at code line 1115
- `are_units_compatible(unit1, unit2) -> bool` — VERIFIED at code line 1269
- `convert_temperature(value, from_unit, to_unit) -> float` — VERIFIED at code line 1079
- `FLOAT_EPSILON = 1e-10` — VERIFIED at code line 20
- `MAX_RESULT_VALUE = 1e308` — VERIFIED at code line 21
- UnitValue `__init__(value: float, unit: str | None = None)` — VERIFIED at code line 31
- UnitValue `convert_to(target_unit)` method — VERIFIED at code line 134
- UnitValue `__repr__()` method — VERIFIED at code line 35
- Arithmetic operations (+, -, *, /, **) — VERIFIED at lines 58-111
- Incompatible unit addition/subtraction raises ValueError — VERIFIED at lines 61, 74
- Temperature conversion formulas — VERIFIED at TEMPERATURE_CONVERSIONS lines 1061-1076
- Module has no dependencies on other nl_calc modules — VERIFIED at code line 1-14

## Discrepancies Between Documentation and Code

- [MEDIUM] **Documentation lists 18 unit categories but omits "angle" category**
  - Documentation says: Table shows 18 categories (lines 71-92)
  - Code actually does: 19 categories exist; "angle" (rad, deg) is present in UNIT_CATEGORIES at lines 1233-1234
  - Impact: Documentation incomplete; angle units are functional but undocumented

- [MEDIUM] **Documentation missing several public methods**
  - Documentation lists only `convert_to()` and `__repr__()` methods (lines 53-57)
  - Code actually has: `__str__()` (line 40), `__format__()` (line 43), `__eq__()` (line 48), `__hash__()` (line 55), `__radd__()` (line 68), `__rsub__()` (line 81), `__rmul__()` (line 95), `__rtruediv__()` (line 107), `__neg__()`, `__pos__()`, `__abs__()`, `__round__()`, `__complex__()`, `__int__()`, `__float__()` (lines 113-132)
  - Impact: Public API undocumented

- [LOW] **Documentation lists function signatures with simplified types**
  - Documentation shows `is_unit(s: str) -> bool` (line 183)
  - Code uses `is_unit(text: str) -> bool` (line 1115)
  - Impact: Parameter name mismatch (s vs text); cosmetic only

- [LOW] **Documentation mentions "Prefix" section but code handles prefixes differently**
  - Documentation says "The system handles SI prefixes" with a table showing deci (d), centi (c) (lines 220-232)
  - Code does not appear to dynamically apply prefixes; prefixed units like kN, mV, mA are explicitly listed in UNIT_ALIASES
  - Impact: Documentation may mislead readers about prefix handling mechanism

## Potential Bugs

- [HIGH] **Temperature to non-temperature conversion crashes after warning**
  - Location: `units.py:146-164`
  - Issue: When converting temperature to non-temperature (e.g., `UnitValue(100, 'K').convert_to('m')`), the code:
    1. Correctly warns that results may be physically meaningless (line 151-156)
    2. Then crashes with "Cannot convert from K to m" because K is not in UNIT_BASE
  - The warning implies the conversion will proceed, but it actually fails
  - Suggested investigation: Either remove the warning and let the error surface naturally, or implement a fallback that actually performs a meaningless multiplicative conversion

- [MEDIUM] **Unreachable negative Kelvin warning code**
  - Location: `units.py:157-162`
  - Issue: The warning about negative Kelvin values is never triggered because:
    1. Temperature-to-temperature conversions return early at line 146-148 before reaching line 157
    2. When target is non-temperature, line 150's `if` is True so the `elif` on line 157 never fires
  - Additionally, condition `self.value < 0 and ... and self.value < 0` has redundant check
  - Suggested investigation: Remove dead code or restructure to actually warn when appropriate

- [LOW] **Redundant condition in negative Kelvin check**
  - Location: `units.py:157`
  - Issue: `self.value < 0` appears twice in the condition
  - Suggested investigation: Clean up redundant condition

## Improvement Suggestions

### HIGH Priority

- **Fix temperature-to-non-temperature conversion behavior**
  - The warning on line 151-156 promises a conversion but then the code crashes
  - Options: (1) Remove the warning and let errors fail naturally, (2) Actually implement the multiplicative conversion with a warning, or (3) Raise a proper error about impossible conversion
  - This creates a poor user experience: warning followed by exception

- **Make unreachable code reachable or remove it**
  - The negative Kelvin warning (lines 157-162) can never trigger under current flow
  - Either remove it or restructure so it actually fires for the appropriate case (if there is one)

### MEDIUM Priority

- **Document the "angle" unit category**
  - Add "angle" to the Unit Categories table in documentation
  - Units: rad, deg

- **Document all public UnitValue methods**
  - Add documentation for `__str__`, `__format__`, `__eq__`, `__hash__`, `__radd__`, `__rsub__`, `__rmul__`, `__rtruediv__`, `__neg__`, `__pos__`, `__abs__`, `__round__`, `__complex__`, `__int__`, `__float__`

- **Add `get_unit_category` to the Key Exports section**
  - Function exists at line 1263 and is documented in Functions section but not in Key Exports

### LOW Priority

- **Fix parameter name in `is_unit` documentation**
  - Docs show `is_unit(s: str)` but code uses `is_unit(text: str)`

- **Clarify prefix handling in documentation**
  - The documentation's "Prefixed Units" section suggests dynamic prefix parsing
  - Clarify that prefixed units (kN, mV, mA) are pre-defined aliases, not dynamically generated

## Summary

The units.md documentation is largely accurate but has three significant issues: (1) A HIGH priority bug where temperature-to-non-temperature conversions issue a warning then crash instead of completing the conversion, (2) Dead code for a negative Kelvin warning that can never be reached due to early returns, and (3) Several public methods and one unit category (angle) are undocumented. The module's core functionality is sound, but these documentation gaps and the temperature conversion bug should be addressed.
