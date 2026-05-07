# units.py - Unit Definitions and Conversions

## Purpose

Comprehensive unit conversion support including length, time, mass, volume, pressure, energy, power, and more.

## Key Types

### `UnitValue`

Represents a numeric value with optional units.

```python
uv = UnitValue(60.48, "m")
uv.value  # 60.48
uv.unit  # "m"
```

Supports arithmetic operations with automatic unit conversion on add/subtract.

## Unit Categories

| Category | Base Unit | Examples |
|----------|-----------|----------|
| length | m | m, km, cm, mm, in, ft, yd, mi, ly, au, pc |
| time | s | s, ms, us, ns, min, h, d, wk, yr |
| data | B | B, KB, MB, GB, TB, PB (binary prefixes) |
| data_rate | bps | bps, Kbps, Mbps, Gbps (decimal prefixes) |
| mass | kg | kg, g, mg, lb, oz, ton |
| volume | L | L, mL, gal, qt, pt, cup, floz |
| pressure | Pa | Pa, kPa, MPa, bar, atm, psi |
| energy | J | J, kJ, cal, kcal, Wh, kWh, BTU, eV |
| power | W | W, kW, MW, GW, mW, hp |
| force | N | N, kN, dyne, lbf |
| voltage | V | V, kV, mV, uV |
| current | A | A, mA, uA |
| angle | rad | rad, deg |
| speed | m/s | m/s, km/h, mph, kn, mach |
| area | m2 | m2, km2, ft2, acre, ha |
| frequency | Hz | Hz, kHz, MHz, GHz, THz |
| temperature | K | K, C, F, R |

## Temperature Conversions

Temperature uses special handling with offset calculations:

```python
TEMPERATURE_CONVERSIONS = {
    ("C", "F"): (1.8, 32.0),   # Celsius to Fahrenheit
    ("F", "C"): (1.0/1.8, -17.777778),
    ("K", "C"): (1.0, -273.15),
    ...
}
```

Formula: `result = value * multiplier + offset`

## Data Structure

### `UNIT_BASE`

Dictionary mapping base units to their variants and conversion factors:

```python
"m": {
    "m": 1.0,
    "km": 1000.0,
    "cm": 0.01,
    "ft": 0.3048,
    ...
}
```

### `UNIT_ALIASES`

Maps all unit variant names to canonical forms:

```python
"meters": "m",
"kilometer": "km",
"foot": "ft",
...
```

### `UNIT_CONVERSIONS`

Pre-computed pairwise conversion factors: `(from_unit, to_unit) → factor`

Built by `_build_unit_conversions()` at module load time.

## Key Functions

| Function | Description |
|----------|-------------|
| `get_conversion_factor(from, to)` | Get conversion factor between units |
| `convert_temperature(value, from, to)` | Convert temperature values |
| `normalize_unit(unit)` | Get canonical unit name |
| `is_unit(text)` | Check if text is a unit |
| `get_unit_category(unit)` | Get category for unit |
| `are_units_compatible(u1, u2)` | Check if units can be added |
| `get_all_units()` | List all supported units |

## Compatibility Checking

`are_units_compatible()` enables adding/subtracting only units of the same category:

```python
# These work
UnitValue(1, "m") + UnitValue(1, "ft")  # Convert ft to m
UnitValue(1, "kg") + UnitValue(1, "lb")  # Convert lb to kg

# These raise ValueError
UnitValue(1, "m") + UnitValue(1, "kg")  # Incompatible units
```

## Constants

- `FLOAT_EPSILON = 1e-10` - For float equality comparison
- `MAX_RESULT_VALUE = 1e308` - Maximum result value