"""
Unit definitions and conversions for nl-calc.

Provides comprehensive unit conversion support including:
- Length (meters, feet, inches, miles, lightyears, etc.)
- Time (seconds, hours, days, weeks, years, etc.)
- Data storage (bytes, KB, MB, GB, TB, etc.)
- Data transfer rate (bps, Kbps, Mbps, Gbps)
- Mass (kg, grams, pounds, ounces, etc.)
- Volume (liters, gallons, cups, etc.)
- Pressure (Pa, bar, psi, atm, etc.)
- Energy (J, kJ, cal, kWh, BTU, eV, etc.)
- Power (W, kW, MW, hp, etc.)
"""

from __future__ import annotations

from typing import Any

FLOAT_EPSILON = 1e-10
MAX_RESULT_VALUE = 1e308


class UnitValue:
    """Represents a numeric value with optional units.

    Supports arithmetic operations with automatic unit conversion
    when adding or subtracting values with compatible units.
    """

    def __init__(self, value: float, unit: str | None = None) -> None:
        self.value = value
        self.unit = unit

    def __repr__(self) -> str:
        if self.unit:
            return f"{self.value} {self.unit}"
        return str(self.value)

    def __str__(self) -> str:
        return self.__repr__()

    def __format__(self, format_spec: str) -> str:
        if self.unit:
            return f"{self.value:{format_spec}} {self.unit}"
        return f"{self.value:{format_spec}}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnitValue):
            return NotImplemented
        if self.unit != other.unit:
            return NotImplemented
        return abs(self.value - other.value) < FLOAT_EPSILON

    def __hash__(self) -> int:
        return hash((self.value, self.unit))

    def __add__(self, other: Any) -> UnitValue:
        if isinstance(other, UnitValue):
            if not are_units_compatible(self.unit, other.unit):
                raise ValueError(f"Cannot add incompatible units: {self.unit} + {other.unit}")
            if self.unit == other.unit or other.unit is None or self.unit is None:
                return UnitValue(self.value + other.value, self.unit or other.unit)
            converted = other.convert_to(self.unit)
            return UnitValue(self.value + converted.value, self.unit)
        return UnitValue(self.value + other, self.unit)

    def __radd__(self, other: Any) -> UnitValue:
        return self.__add__(other)

    def __sub__(self, other: Any) -> UnitValue:
        if isinstance(other, UnitValue):
            if not are_units_compatible(self.unit, other.unit):
                raise ValueError(f"Cannot subtract incompatible units: {self.unit} - {other.unit}")
            if self.unit == other.unit or other.unit is None or self.unit is None:
                return UnitValue(self.value - other.value, self.unit or other.unit)
            converted = other.convert_to(self.unit)
            return UnitValue(self.value - converted.value, self.unit)
        return UnitValue(self.value - other, self.unit)

    def __rsub__(self, other: Any) -> UnitValue:
        return UnitValue(other - self.value, self.unit)

    def __mul__(self, other: Any) -> UnitValue:
        if isinstance(other, UnitValue):
            if self.unit and other.unit:
                if self.unit == other.unit:
                    return UnitValue(self.value * other.value, self.unit)
                return UnitValue(self.value * other.value, f"{self.unit}*{other.unit}")
            return UnitValue(self.value * other.value, self.unit or other.unit)
        return UnitValue(self.value * other, self.unit)

    def __rmul__(self, other: Any) -> UnitValue:
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> UnitValue:
        if isinstance(other, UnitValue):
            if self.unit and other.unit:
                if self.unit == other.unit:
                    return UnitValue(self.value / other.value, None)
                return UnitValue(self.value / other.value, f"{self.unit}/{other.unit}")
            return UnitValue(self.value / other.value, self.unit)
        return UnitValue(self.value / other, self.unit)

    def __rtruediv__(self, other: Any) -> UnitValue:
        return UnitValue(other / self.value, self.unit)

    def __pow__(self, other: Any) -> UnitValue:
        return UnitValue(self.value**other, self.unit)

    def __neg__(self) -> UnitValue:
        return UnitValue(-self.value, self.unit)

    def __pos__(self) -> UnitValue:
        return UnitValue(self.value, self.unit)

    def __abs__(self) -> UnitValue:
        return UnitValue(abs(self.value), self.unit)

    def __round__(self, ndigits: int = 0) -> UnitValue:
        return UnitValue(round(self.value, ndigits), self.unit)

    def __complex__(self) -> complex:
        return complex(self.value)

    def __int__(self) -> int:
        return int(self.value)

    def __float__(self) -> float:
        return float(self.value)

    def convert_to(self, target_unit: str) -> UnitValue:
        """Convert to a different unit of the same type."""
        import warnings

        if self.unit == target_unit:
            return UnitValue(self.value, target_unit)

        if self.unit is None:
            raise ValueError("Cannot convert dimensionless value")

        cat = get_unit_category(self.unit)
        target_cat = get_unit_category(target_unit)
        if cat == "temperature" and target_cat == "temperature":
            converted = convert_temperature(self.value, self.unit, target_unit)
            return UnitValue(converted, target_unit)
        if cat == "temperature":
            if target_cat != "temperature":
                warnings.warn(
                    f"Converting temperature ({self.unit}={self.value}) to non-temperature unit ({target_unit}). "
                    f"This may give physically meaningless results.",
                    UserWarning,
                    stacklevel=2,
                )
            elif self.value < 0 and self.unit in ("K", "kelvin", "kelvins") and self.value < 0:
                warnings.warn(
                    f"Absolute zero is 0 K. Converting negative Kelvin value {self.value} K will give incorrect results.",
                    UserWarning,
                    stacklevel=2,
                )
        factor = get_conversion_factor(self.unit, target_unit)
        return UnitValue(self.value * factor, target_unit)


# Unit definitions: base unit -> {unit: factor to base}
UNIT_BASE: dict[str, dict[str, float]] = {
    # Length (base: meters)
    "m": {
        "m": 1.0,
        "meter": 1.0,
        "meters": 1.0,
        "km": 1000.0,
        "kilometer": 1000.0,
        "kilometers": 1000.0,
        "cm": 0.01,
        "centimeter": 0.01,
        "centimeters": 0.01,
        "mm": 0.001,
        "millimeter": 0.001,
        "millimeters": 0.001,
        "um": 1e-6,
        "μm": 1e-6,
        "micrometer": 1e-6,
        "micrometers": 1e-6,
        "nm": 1e-9,
        "nanometer": 1e-9,
        "nanometers": 1e-9,
        "pm": 1e-12,
        "picometer": 1e-12,
        "picometers": 1e-12,
        "in": 0.0254,
        "inch": 0.0254,
        "inches": 0.0254,
        "ft": 0.3048,
        "foot": 0.3048,
        "feet": 0.3048,
        "yd": 0.9144,
        "yard": 0.9144,
        "yards": 0.9144,
        "mi": 1609.344,
        "mile": 1609.344,
        "miles": 1609.344,
        "ly": 9.4607e15,
        "lightyear": 9.4607e15,
        "lightyears": 9.4607e15,
        "au": 1.496e11,
        "astronomicalunit": 1.496e11,
        "astronomicalunits": 1.496e11,
        "pc": 3.086e16,
        "parsec": 3.086e16,
        "parsecs": 3.086e16,
        "angstrom": 1e-10,
        "angstroms": 1e-10,
        "fermi": 1e-15,
        "nmi": 1852.0,
        "nauticalmile": 1852.0,
        "nauticalmiles": 1852.0,
        "furlong": 201.168,
        "furlongs": 201.168,
        "chain": 20.1168,
        "chains": 20.1168,
        "rd": 5.0292,
        "rod": 5.0292,
        "rods": 5.0292,
        "fathom": 1.8288,
        "fathoms": 1.8288,
        "smoot": 1.7018,
        "smoots": 1.7018,
    },
    # Time (base: seconds)
    "s": {
        "s": 1.0,
        "second": 1.0,
        "seconds": 1.0,
        "ms": 0.001,
        "millisecond": 0.001,
        "milliseconds": 0.001,
        "us": 1e-6,
        "μs": 1e-6,
        "microsecond": 1e-6,
        "microseconds": 1e-6,
        "ns": 1e-9,
        "nanosecond": 1e-9,
        "nanoseconds": 1e-9,
        "ps": 1e-12,
        "picosecond": 1e-12,
        "picoseconds": 1e-12,
        "min": 60.0,
        "minute": 60.0,
        "minutes": 60.0,
        "h": 3600.0,
        "hr": 3600.0,
        "hour": 3600.0,
        "hours": 3600.0,
        "d": 86400.0,
        "day": 86400.0,
        "days": 86400.0,
        "wk": 604800.0,
        "week": 604800.0,
        "weeks": 604800.0,
        "fortnight": 1209600.0,
        "fortnights": 1209600.0,
        "yr": 31536000.0,
        "year": 31536000.0,
        "years": 31536000.0,
        "decade": 315360000.0,
        "decades": 315360000.0,
        "century": 3153600000.0,
        "centuries": 3153600000.0,
        "millennium": 31536000000.0,
        "millennia": 31536000000.0,
    },
    # Note: Year is defined as 365 days (31536000 seconds), ignoring leap years.
    # Data storage (base: bytes) - uses binary (1024) prefixes per IEEE/ASTM standard
    "B": {
        "B": 1.0,
        "byte": 1.0,
        "bytes": 1.0,
        "bit": 0.125,
        "bits": 0.125,
        "KB": 1024.0,
        "kilobyte": 1024.0,
        "kilobytes": 1024.0,
        "MB": 1048576.0,
        "megabyte": 1048576.0,
        "megabytes": 1048576.0,
        "GB": 1073741824.0,
        "gigabyte": 1073741824.0,
        "gigabytes": 1073741824.0,
        "TB": 1099511627776.0,
        "terabyte": 1099511627776.0,
        "terabytes": 1099511627776.0,
        "PB": 1125899906842624.0,
        "petabyte": 1125899906842624.0,
        "petabytes": 1125899906842624.0,
        "EB": 1152921504606846976.0,
        "exabyte": 1152921504606846976.0,
        "exabytes": 1152921504606846976.0,
        "ZB": 1.1805916207174113e21,
        "zettabyte": 1.1805916207174113e21,
        "zettabytes": 1.1805916207174113e21,
        "YB": 1.2089258196146292e24,
        "yottabyte": 1.2089258196146292e24,
        "yottabytes": 1.2089258196146292e24,
    },
    # Data transfer rate (base: bits per second) - uses decimal (1000) prefixes per SI standard
    "bps": {
        "bps": 1.0,
        "bit/s": 1.0,
        "bits/s": 1.0,
        "Kbps": 1000.0,
        "kilobps": 1000.0,
        "kilobit/s": 1000.0,
        "kilobits/s": 1000.0,
        "Mbps": 1000000.0,
        "megabps": 1000000.0,
        "megabit/s": 1000000.0,
        "megabits/s": 1000000.0,
        "Gbps": 1000000000.0,
        "gigabps": 1000000000.0,
        "gigabit/s": 1000000000.0,
        "gigabits/s": 1000000000.0,
    },
    # Mass (base: kilograms)
    "kg": {
        "kg": 1.0,
        "kilogram": 1.0,
        "kilograms": 1.0,
        "g": 0.001,
        "gram": 0.001,
        "grams": 0.001,
        "mg": 1e-6,
        "milligram": 1e-6,
        "milligrams": 1e-6,
        "ug": 1e-9,
        "μg": 1e-9,
        "microgram": 1e-9,
        "micrograms": 1e-9,
        "ng": 1e-12,
        "nanogram": 1e-12,
        "nanograms": 1e-12,
        "lb": 0.45359237,
        "lbs": 0.45359237,
        "pound": 0.45359237,
        "pounds": 0.45359237,
        "oz": 0.0283495231,
        "ounce": 0.0283495231,
        "ounces": 0.0283495231,
        "ton": 907.18474,
        "tons": 907.18474,
        "tonne": 1000.0,
        "tonnes": 1000.0,
        "stone": 6.35029318,
        "stones": 6.35029318,
        "slug": 14.593903,
        "slugs": 14.593903,
        "ct": 0.0002,
        "carat": 0.0002,
        "carats": 0.0002,
        "gr": 6.479891e-5,
        "grain": 6.479891e-5,
        "grains": 6.479891e-5,
        "dr": 0.0017718452,
        "dram": 0.0017718452,
        "drams": 0.0017718452,
    },
    # Volume (base: liters)
    "L": {
        "L": 1.0,
        "liter": 1.0,
        "liters": 1.0,
        "l": 1.0,
        "mL": 0.001,
        "milliliter": 0.001,
        "milliliters": 0.001,
        "uL": 1e-6,
        "μL": 1e-6,
        "microliter": 1e-6,
        "microliters": 1e-6,
        "gal": 3.785411784,
        "gallon": 3.785411784,
        "gallons": 3.785411784,
        "qt": 0.946352946,
        "quart": 0.946352946,
        "quarts": 0.946352946,
        "pt": 0.473176473,
        "pint": 0.473176473,
        "pints": 0.473176473,
        "cup": 0.2365882365,
        "cups": 0.2365882365,
        "floz": 0.0295735296,
        "fl oz": 0.0295735296,
        "fluidounce": 0.0295735296,
        "fluidounces": 0.0295735296,
        "tbsp": 0.0147867678,
        "tablespoon": 0.0147867678,
        "tablespoons": 0.0147867678,
        "tsp": 0.00492892159,
        "teaspoon": 0.00492892159,
        "teaspoons": 0.00492892159,
    },
    # Pressure (base: Pascal)
    "Pa": {
        "Pa": 1.0,
        "pascal": 1.0,
        "pascals": 1.0,
        "kPa": 1000.0,
        "kilopascal": 1000.0,
        "kilopascals": 1000.0,
        "MPa": 1000000.0,
        "megapascal": 1000000.0,
        "megapascals": 1000000.0,
        "GPa": 1e9,
        "gigapascal": 1e9,
        "gigapascals": 1e9,
        "bar": 100000.0,
        "bars": 100000.0,
        "mbar": 100.0,
        "millibar": 100.0,
        "atm": 101325.0,
        "atmosphere": 101325.0,
        "atmospheres": 101325.0,
        "psi": 6894.757293168,
    },
    # Energy (base: Joules)
    "J": {
        "J": 1.0,
        "joule": 1.0,
        "joules": 1.0,
        "kJ": 1000.0,
        "kilojoule": 1000.0,
        "kilojoules": 1000.0,
        "MJ": 1e6,
        "megajoule": 1e6,
        "megajoules": 1e6,
        "GJ": 1e9,
        "gigajoule": 1e9,
        "gigajoules": 1e9,
        "cal": 4.184,
        "calorie": 4.184,
        "calories": 4.184,
        "kcal": 4184.0,
        "kilocalorie": 4184.0,
        "kilocalories": 4184.0,
        "Wh": 3600.0,
        "watt-hour": 3600.0,
        "watt-hours": 3600.0,
        "kWh": 3600000.0,
        "kilowatt-hour": 3600000.0,
        "kilowatt-hours": 3600000.0,
        "BTU": 1055.06,
        "btu": 1055.06,
        "eV": 1.602176634e-19,
    },
    # Power (base: Watts)
    "W": {
        "W": 1.0,
        "watt": 1.0,
        "watts": 1.0,
        "kW": 1000.0,
        "kilowatt": 1000.0,
        "kilowatts": 1000.0,
        "MW": 1e6,
        "megawatt": 1e6,
        "megawatts": 1e6,
        "GW": 1e9,
        "gigawatt": 1e9,
        "gigawatts": 1e9,
        "mW": 0.001,
        "milliwatt": 0.001,
        "milliwatts": 0.001,
        "hp": 745.699872,
        "horsepower": 745.699872,
    },
    "N": {
        "N": 1.0,
        "newton": 1.0,
        "newtons": 1.0,
        "kN": 1000.0,
        "kilonewton": 1000.0,
        "dyne": 1e-5,
        "dynes": 1e-5,
        "lbf": 4.4482216152605,
        "poundforce": 4.4482216152605,
    },
    "V": {
        "V": 1.0,
        "volt": 1.0,
        "volts": 1.0,
        "kV": 1000.0,
        "kilovolt": 1000.0,
        "mV": 0.001,
        "millivolt": 0.001,
        "uV": 1e-6,
        "microvolt": 1e-6,
    },
    "A": {
        "A": 1.0,
        "amp": 1.0,
        "ampere": 1.0,
        "amperes": 1.0,
        "mA": 0.001,
        "milliamp": 0.001,
        "milliampere": 0.001,
        "uA": 1e-6,
        "microamp": 1e-6,
    },
    "rad": {
        "rad": 1.0,
        "radian": 1.0,
        "radians": 1.0,
        "deg": 0.017453292519943295,
        "degree": 0.017453292519943295,
        "degrees": 0.017453292519943295,
    },
    # Speed (base: meters per second)
    "m/s": {
        "m/s": 1.0,
        "mps": 1.0,
        "meterpersecond": 1.0,
        "meterspersecond": 1.0,
        "km/h": 0.277777778,
        "kph": 0.277777778,
        "kilometerperhour": 0.277777778,
        "kilometersperhour": 0.277777778,
        "mph": 0.44704,
        "mileperhour": 0.44704,
        "milesperhour": 0.44704,
        "kn": 0.514444,
        "knot": 0.514444,
        "knots": 0.514444,
        "kt": 0.514444,
        "mach": 340.29,
    },
    # Area (base: square meters)
    "m2": {
        "m2": 1.0,
        "m^2": 1.0,
        "sqm": 1.0,
        "squaremeter": 1.0,
        "squaremeters": 1.0,
        "km2": 1000000.0,
        "km^2": 1000000.0,
        "squarekilometer": 1000000.0,
        "squarekilometers": 1000000.0,
        "cm2": 0.0001,
        "cm^2": 0.0001,
        "squarecentimeter": 0.0001,
        "squarecentimeters": 0.0001,
        "mm2": 1e-6,
        "mm^2": 1e-6,
        "squaremillimeter": 1e-6,
        "squaremillimeters": 1e-6,
        "ha": 10000.0,
        "hectare": 10000.0,
        "hectares": 10000.0,
        "acre": 4046.8564224,
        "acres": 4046.8564224,
        "ft2": 0.09290304,
        "ft^2": 0.09290304,
        "sqft": 0.09290304,
        "squarefoot": 0.09290304,
        "squarefeet": 0.09290304,
        "in2": 0.00064516,
        "in^2": 0.00064516,
        "sqin": 0.00064516,
        "squareinch": 0.00064516,
        "squareinches": 0.00064516,
        "mi2": 2589988.110336,
        "mi^2": 2589988.110336,
        "sqmi": 2589988.110336,
        "squaremile": 2589988.110336,
        "squaremiles": 2589988.110336,
        "yd2": 0.83612736,
        "yd^2": 0.83612736,
        "sqyd": 0.83612736,
        "squareyard": 0.83612736,
        "squareyards": 0.83612736,
    },
    # Frequency (base: Hertz)
    "Hz": {
        "Hz": 1.0,
        "hertz": 1.0,
        "kHz": 1000.0,
        "kilohertz": 1000.0,
        "MHz": 1000000.0,
        "megahertz": 1000000.0,
        "GHz": 1000000000.0,
        "gigahertz": 1000000000.0,
        "THz": 1000000000000.0,
        "terahertz": 1000000000000.0,
    },
}


def _build_unit_conversions() -> dict[tuple[str, str], float]:
    """Build a complete unit conversion lookup table."""
    conversions: dict[tuple[str, str], float] = {}

    for base_unit, units in UNIT_BASE.items():
        unit_factors = {unit: factor for unit, factor in units.items()}

        for from_unit, from_factor in unit_factors.items():
            for to_unit, to_factor in unit_factors.items():
                if from_unit != to_unit:
                    key = (from_unit, to_unit)
                    conversions[key] = from_factor / to_factor

    return conversions


# Pre-computed conversion factors: (from_unit, to_unit) -> factor
UNIT_CONVERSIONS: dict[tuple[str, str], float] = {}


def _rebuild_conversions() -> None:
    """Rebuild UNIT_CONVERSIONS after adding custom units."""
    global UNIT_CONVERSIONS
    UNIT_CONVERSIONS = _build_unit_conversions()


_rebuild_conversions()


# Map all unit aliases to canonical forms
UNIT_ALIASES: dict[str, str] = {
    # Length
    "m": "m",
    "meter": "m",
    "meters": "m",
    "km": "km",
    "kilometer": "km",
    "kilometers": "km",
    "cm": "cm",
    "centimeter": "cm",
    "centimeters": "cm",
    "mm": "mm",
    "millimeter": "mm",
    "millimeters": "mm",
    "um": "um",
    "μm": "um",
    "micrometer": "um",
    "micrometers": "um",
    "nm": "nm",
    "nanometer": "nm",
    "nanometers": "nm",
    "pm": "pm",
    "picometer": "pm",
    "picometers": "pm",
    "in": "in",
    "inch": "in",
    "inches": "in",
    "ft": "ft",
    "foot": "ft",
    "feet": "ft",
    "yd": "yd",
    "yard": "yd",
    "yards": "yd",
    "mi": "mi",
    "mile": "mi",
    "miles": "mi",
    "ly": "ly",
    "lightyear": "ly",
    "lightyears": "ly",
    "au": "au",
    "astronomicalunit": "au",
    "astronomicalunits": "au",
    "pc": "pc",
    "parsec": "pc",
    "parsecs": "pc",
    "angstrom": "angstrom",
    "angstroms": "angstrom",
    "fermi": "fermi",
    "nmi": "nmi",
    "nauticalmile": "nmi",
    "nauticalmiles": "nmi",
    "furlong": "furlong",
    "furlongs": "furlong",
    "chain": "chain",
    "chains": "chain",
    "rd": "rd",
    "rod": "rd",
    "rods": "rd",
    "fathom": "fathom",
    "fathoms": "fathom",
    "smoot": "smoot",
    "smoots": "smoot",
    # Time
    "s": "s",
    "second": "s",
    "seconds": "s",
    "ms": "ms",
    "millisecond": "ms",
    "milliseconds": "ms",
    "us": "us",
    "μs": "us",
    "microsecond": "us",
    "microseconds": "us",
    "ns": "ns",
    "nanosecond": "ns",
    "nanoseconds": "ns",
    "ps": "ps",
    "picosecond": "ps",
    "picoseconds": "ps",
    "min": "min",
    "minute": "min",
    "minutes": "min",
    "h": "h",
    "hr": "h",
    "hour": "h",
    "hours": "h",
    "d": "d",
    "day": "d",
    "days": "d",
    "wk": "wk",
    "week": "wk",
    "weeks": "wk",
    "yr": "yr",
    "year": "yr",
    "years": "yr",
    "fortnight": "fortnight",
    "fortnights": "fortnight",
    "decade": "decade",
    "decades": "decade",
    "century": "century",
    "centuries": "century",
    "millennium": "millennium",
    "millennia": "millennium",
    # Data storage
    "B": "B",
    "byte": "B",
    "bytes": "B",
    "bit": "bit",
    "bits": "bit",
    "KB": "KB",
    "kilobyte": "KB",
    "kilobytes": "KB",
    "MB": "MB",
    "megabyte": "MB",
    "megabytes": "MB",
    "GB": "GB",
    "gigabyte": "GB",
    "gigabytes": "GB",
    "TB": "TB",
    "terabyte": "TB",
    "terabytes": "TB",
    "PB": "PB",
    "petabyte": "PB",
    "petabytes": "PB",
    "EB": "EB",
    "exabyte": "EB",
    "exabytes": "EB",
    "ZB": "ZB",
    "zettabyte": "ZB",
    "zettabytes": "ZB",
    "YB": "YB",
    "yottabyte": "YB",
    "yottabytes": "YB",
    # Data transfer
    "bps": "bps",
    "bit/s": "bps",
    "bits/s": "bps",
    "Kbps": "Kbps",
    "kilobps": "Kbps",
    "kilobit/s": "Kbps",
    "kilobits/s": "Kbps",
    "Mbps": "Mbps",
    "megabps": "Mbps",
    "megabit/s": "Mbps",
    "megabits/s": "Mbps",
    "Gbps": "Gbps",
    "gigabps": "Gbps",
    "gigabit/s": "Gbps",
    "gigabits/s": "Gbps",
    # Mass
    "kg": "kg",
    "kilogram": "kg",
    "kilograms": "kg",
    "g": "g",
    "gram": "g",
    "grams": "g",
    "mg": "mg",
    "milligram": "mg",
    "milligrams": "mg",
    "ug": "ug",
    "μg": "ug",
    "microgram": "ug",
    "micrograms": "ug",
    "ng": "ng",
    "nanogram": "ng",
    "nanograms": "ng",
    "lb": "lb",
    "lbs": "lb",
    "pound": "lb",
    "pounds": "lb",
    "oz": "oz",
    "ounce": "oz",
    "ounces": "oz",
    "ton": "ton",
    "tons": "ton",
    "tonne": "tonne",
    "tonnes": "tonne",
    "stone": "stone",
    "stones": "stone",
    "slug": "slug",
    "slugs": "slug",
    "ct": "ct",
    "carat": "ct",
    "carats": "ct",
    "gr": "gr",
    "grain": "gr",
    "grains": "gr",
    "dr": "dr",
    "dram": "dr",
    "drams": "dr",
    # Volume
    "L": "L",
    "l": "L",
    "liter": "L",
    "liters": "L",
    "mL": "mL",
    "milliliter": "mL",
    "milliliters": "mL",
    "uL": "uL",
    "μL": "uL",
    "microliter": "uL",
    "microliters": "uL",
    "gal": "gal",
    "gallon": "gal",
    "gallons": "gal",
    "qt": "qt",
    "quart": "qt",
    "quarts": "qt",
    "pt": "pt",
    "pint": "pt",
    "pints": "pt",
    "cup": "cup",
    "cups": "cup",
    "floz": "floz",
    "fl oz": "floz",
    "fluidounce": "floz",
    "fluidounces": "floz",
    "tbsp": "tbsp",
    "tablespoon": "tbsp",
    "tablespoons": "tbsp",
    "tsp": "tsp",
    "teaspoon": "tsp",
    "teaspoons": "tsp",
    # Pressure
    "Pa": "Pa",
    "pascal": "Pa",
    "pascals": "Pa",
    "kPa": "kPa",
    "kilopascal": "kPa",
    "kilopascals": "kPa",
    "MPa": "MPa",
    "megapascal": "MPa",
    "megapascals": "MPa",
    "GPa": "GPa",
    "gigapascal": "GPa",
    "gigapascals": "GPa",
    "bar": "bar",
    "bars": "bar",
    "mbar": "mbar",
    "millibar": "mbar",
    "atm": "atm",
    "atmosphere": "atm",
    "atmospheres": "atm",
    "psi": "psi",
    "psia": "psi",
    # Energy
    "J": "J",
    "joule": "J",
    "joules": "J",
    "kJ": "kJ",
    "kilojoule": "kJ",
    "kilojoules": "kJ",
    "MJ": "MJ",
    "megajoule": "MJ",
    "megajoules": "MJ",
    "GJ": "GJ",
    "gigajoule": "GJ",
    "gigajoules": "GJ",
    "cal": "cal",
    "calorie": "cal",
    "calories": "cal",
    "kcal": "kcal",
    "kilocalorie": "kcal",
    "kilocalories": "kcal",
    "Wh": "Wh",
    "watt-hour": "Wh",
    "watt-hours": "Wh",
    "kWh": "kWh",
    "kilowatt-hour": "kWh",
    "kilowatt-hours": "kWh",
    "BTU": "BTU",
    "btu": "BTU",
    "eV": "eV",
    "ev": "eV",
    "electronvolt": "eV",
    "electronvolts": "eV",
    # Power
    "W": "W",
    "watt": "W",
    "watts": "W",
    "kW": "kW",
    "kilowatt": "kW",
    "kilowatts": "kW",
    "MW": "MW",
    "megawatt": "MW",
    "megawatts": "MW",
    "GW": "GW",
    "gigawatt": "GW",
    "gigawatts": "GW",
    "mW": "mW",
    "milliwatt": "mW",
    "milliwatts": "mW",
    "hp": "hp",
    "horsepower": "hp",
    # Force
    "N": "N",
    "newton": "N",
    "newtons": "N",
    "kN": "kN",
    "kilonewton": "kN",
    "dyne": "dyne",
    "dynes": "dyne",
    "lbf": "lbf",
    "poundforce": "lbf",
    # Voltage
    "V": "V",
    "volt": "V",
    "volts": "V",
    "kV": "kV",
    "kilovolt": "kV",
    "mV": "mV",
    "millivolt": "mV",
    "uV": "μV",
    "μV": "μV",
    "microvolt": "μV",
    # Current
    "A": "A",
    "amp": "A",
    "ampere": "A",
    "amperes": "A",
    "mA": "mA",
    "milliamp": "mA",
    "milliampere": "mA",
    "uA": "μA",
    "μA": "μA",
    "microamp": "μA",
    "microampere": "μA",
    # Angles
    "rad": "rad",
    "radian": "rad",
    "radians": "rad",
    "deg": "deg",
    "degree": "deg",
    "degrees": "deg",
    # Temperature
    "K": "K",
    "kelvin": "K",
    "kelvins": "K",
    "C": "C",
    "celsius": "C",
    "centigrade": "C",
    "F": "F",
    "fahrenheit": "F",
    "R": "R",
    "Ra": "R",
    "rankine": "R",
    # Speed
    "m/s": "m/s",
    "mps": "m/s",
    "meterpersecond": "m/s",
    "meterspersecond": "m/s",
    "km/h": "km/h",
    "kph": "km/h",
    "kilometerperhour": "km/h",
    "kilometersperhour": "km/h",
    "mph": "mph",
    "mileperhour": "mph",
    "milesperhour": "mph",
    "kn": "kn",
    "knot": "kn",
    "knots": "kn",
    "kt": "kn",
    "mach": "mach",
    # Area
    "m2": "m2",
    "m^2": "m2",
    "sqm": "m2",
    "squaremeter": "m2",
    "squaremeters": "m2",
    "km2": "km2",
    "km^2": "km2",
    "squarekilometer": "km2",
    "squarekilometers": "km2",
    "cm2": "cm2",
    "cm^2": "cm2",
    "squarecentimeter": "cm2",
    "squarecentimeters": "cm2",
    "mm2": "mm2",
    "mm^2": "mm2",
    "squaremillimeter": "mm2",
    "squaremillimeters": "mm2",
    "ha": "ha",
    "hectare": "ha",
    "hectares": "ha",
    "acre": "acre",
    "acres": "acre",
    "ft2": "ft2",
    "ft^2": "ft2",
    "sqft": "ft2",
    "squarefoot": "ft2",
    "squarefeet": "ft2",
    "in2": "in2",
    "in^2": "in2",
    "sqin": "in2",
    "squareinch": "in2",
    "squareinches": "in2",
    "mi2": "mi2",
    "mi^2": "mi2",
    "sqmi": "mi2",
    "squaremile": "mi2",
    "squaremiles": "mi2",
    "yd2": "yd2",
    "yd^2": "yd2",
    "sqyd": "yd2",
    "squareyard": "yd2",
    "squareyards": "yd2",
    # Frequency
    "Hz": "Hz",
    "hertz": "Hz",
    "kHz": "kHz",
    "kilohertz": "kHz",
    "MHz": "MHz",
    "megahertz": "MHz",
    "GHz": "GHz",
    "gigahertz": "GHz",
    "THz": "THz",
    "terahertz": "THz",
}


def normalize_unit(unit: str) -> str:
    """Normalize a unit to its canonical form."""
    return UNIT_ALIASES.get(unit, unit)


TEMPERATURE_CONVERSIONS: dict[tuple[str, str], tuple[float, float]] = {
    # (from, to) -> (multiplier, offset)
    # Note: Offsets are derived values; floating-point precision may cause minor rounding differences
    ("K", "C"): (1.0, -273.15),
    ("C", "K"): (1.0, 273.15),
    ("K", "F"): (1.8, -459.67),
    ("F", "K"): (1.0 / 1.8, 255.372222),
    ("C", "F"): (1.8, 32.0),
    ("F", "C"): (1.0 / 1.8, -32.0 / 1.8),
    ("K", "R"): (1.8, 0.0),
    ("R", "K"): (1.0 / 1.8, 0.0),
    ("C", "R"): (1.8, 491.67),
    ("R", "C"): (1.0 / 1.8, -273.15),
    ("F", "R"): (1.0, 459.67),
    ("R", "F"): (1.0, -459.67),
}


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert temperature values with proper offset handling."""
    from_unit = normalize_unit(from_unit)
    to_unit = normalize_unit(to_unit)

    if from_unit == to_unit:
        return value

    key = (from_unit, to_unit)
    if key in TEMPERATURE_CONVERSIONS:
        multiplier, offset = TEMPERATURE_CONVERSIONS[key]
        return value * multiplier + offset

    reverse_key = (to_unit, from_unit)
    if reverse_key in TEMPERATURE_CONVERSIONS:
        multiplier, offset = TEMPERATURE_CONVERSIONS[reverse_key]
        return (value - offset) / multiplier

    raise ValueError(f"Cannot convert temperature from {from_unit} to {to_unit}")


def get_conversion_factor(from_unit: str, to_unit: str) -> float:
    """Get conversion factor from one unit to another."""
    from_unit = normalize_unit(from_unit)
    to_unit = normalize_unit(to_unit)

    if from_unit == to_unit:
        return 1.0

    key = (from_unit, to_unit)
    if key in UNIT_CONVERSIONS:
        return UNIT_CONVERSIONS[key]

    raise ValueError(f"Cannot convert from {from_unit} to {to_unit}")


def is_unit(text: str) -> bool:
    """Check if text represents a unit."""
    return text in UNIT_ALIASES or text in UNIT_CONVERSIONS


UNIT_CATEGORIES: dict[str, str] = {
    "m": "length",
    "km": "length",
    "cm": "length",
    "mm": "length",
    "um": "length",
    "nm": "length",
    "pm": "length",
    "in": "length",
    "ft": "length",
    "yd": "length",
    "mi": "length",
    "ly": "length",
    "au": "length",
    "pc": "length",
    "angstrom": "length",
    "fermi": "length",
    "nmi": "length",
    "furlong": "length",
    "chain": "length",
    "rd": "length",
    "fathom": "length",
    "smoot": "length",
    "s": "time",
    "ms": "time",
    "us": "time",
    "ns": "time",
    "ps": "time",
    "min": "time",
    "h": "time",
    "hr": "time",
    "d": "time",
    "wk": "time",
    "yr": "time",
    "fortnight": "time",
    "decade": "time",
    "century": "time",
    "millennium": "time",
    "B": "data",
    "bit": "data",
    "KB": "data",
    "MB": "data",
    "GB": "data",
    "TB": "data",
    "PB": "data",
    "EB": "data",
    "ZB": "data",
    "YB": "data",
    "bps": "data_rate",
    "Kbps": "data_rate",
    "Mbps": "data_rate",
    "Gbps": "data_rate",
    "kg": "mass",
    "g": "mass",
    "mg": "mass",
    "ug": "mass",
    "ng": "mass",
    "lb": "mass",
    "oz": "mass",
    "ton": "mass",
    "tonne": "mass",
    "stone": "mass",
    "slug": "mass",
    "ct": "mass",
    "gr": "mass",
    "dr": "mass",
    "L": "volume",
    "mL": "volume",
    "uL": "volume",
    "gal": "volume",
    "qt": "volume",
    "pt": "volume",
    "cup": "volume",
    "floz": "volume",
    "tbsp": "volume",
    "tsp": "volume",
    "Pa": "pressure",
    "kPa": "pressure",
    "MPa": "pressure",
    "GPa": "pressure",
    "bar": "pressure",
    "mbar": "pressure",
    "atm": "pressure",
    "psi": "pressure",
    "J": "energy",
    "kJ": "energy",
    "MJ": "energy",
    "GJ": "energy",
    "cal": "energy",
    "kcal": "energy",
    "Wh": "energy",
    "kWh": "energy",
    "BTU": "energy",
    "eV": "energy",
    "W": "power",
    "kW": "power",
    "MW": "power",
    "GW": "power",
    "mW": "power",
    "hp": "power",
    "N": "force",
    "kN": "force",
    "dyne": "force",
    "lbf": "force",
    "V": "voltage",
    "kV": "voltage",
    "mV": "voltage",
    "uV": "voltage",
    "A": "current",
    "mA": "current",
    "uA": "current",
    "rad": "angle",
    "deg": "angle",
    "K": "temperature",
    "C": "temperature",
    "F": "temperature",
    "R": "temperature",
    "m/s": "speed",
    "mps": "speed",
    "km/h": "speed",
    "mph": "speed",
    "kn": "speed",
    "mach": "speed",
    "m2": "area",
    "km2": "area",
    "cm2": "area",
    "mm2": "area",
    "ha": "area",
    "acre": "area",
    "ft2": "area",
    "in2": "area",
    "mi2": "area",
    "yd2": "area",
    "Hz": "frequency",
    "kHz": "frequency",
    "MHz": "frequency",
    "GHz": "frequency",
    "THz": "frequency",
}


def get_unit_category(unit: str) -> str | None:
    """Get the category for a unit (e.g., 'm' -> 'length', 'gal' -> 'volume')."""
    normalized = normalize_unit(unit)
    return UNIT_CATEGORIES.get(normalized)


def are_units_compatible(unit1: str | None, unit2: str | None) -> bool:
    """Check if two units are compatible for addition/subtraction.

    Returns True if:
    - Both units are None (dimensionless)
    - One unit is None and the other is not
    - Both units belong to the same category (e.g., both length)

    Returns False if units are from different categories.
    """
    if unit1 is None or unit2 is None:
        return True

    cat1 = get_unit_category(unit1)
    cat2 = get_unit_category(unit2)

    if cat1 is None or cat2 is None:
        return True

    return cat1 == cat2


def get_all_units() -> list[str]:
    """Get list of all supported units."""
    return sorted(UNIT_ALIASES.keys())
