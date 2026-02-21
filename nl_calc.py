#!/usr/bin/env python3
from __future__ import annotations

"""
nl_calc - Natural language math expression calculator

Single-file version. Run: python3 nl_calc.py "five plus two"
Or make executable: chmod +x nl_calc.py && ./nl_calc.py "five plus two"
"""

import sys
import os

# Prevent pip from auto-installing dependencies
os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"

__version__ = "1.1.0"
# === units.py ===
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
        if self.unit == target_unit:
            return UnitValue(self.value, target_unit)

        if self.unit is None:
            raise ValueError("Cannot convert dimensionless value")

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
    "kN": "N",
    "kilonewton": "N",
    "dyne": "N",
    "dynes": "N",
    "lbf": "N",
    "poundforce": "N",
    # Voltage
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
    # Current
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
    ("F", "C"): (1.0 / 1.8, -17.777778),
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

# === evaluator.py ===
import ast
import cmath
import math
import random
import threading
from collections import OrderedDict
from functools import lru_cache
from typing import Any


__all__ = [
    "EvaluationError",
    "Evaluator",
    "evaluate",
    "evaluate_raw",
    "evaluate_cached",
    "evaluate_async",
    "evaluate_with_timeout",
    "get_default_evaluator",
    "register_constant",
    "register_function",
    "load_user_config",
    "PyCalcApp",
    "TimeoutError",
]


_lock = threading.Lock()
_config_loaded = False

MAX_EXPONENT = 10000
MAX_FACTORIAL = 1000
MAX_NESTING_DEPTH = 100
MAX_RESULT_VALUE = 1e308
DEFAULT_CACHE_SIZE = 1024


def register_constant(name: str, value: float) -> None:
    """Register a user-defined constant (thread-safe)."""
    with _lock:
        _default_evaluator.CONSTANTS[name] = value


def register_function(name: str, func: Any) -> None:
    """Register a user-defined function (thread-safe)."""
    with _lock:
        _default_evaluator.FUNCTIONS[name] = func


def load_user_config() -> None:
    """Load user-defined configuration from nl_calc_config.py (thread-safe)."""
    global _config_loaded

    with _lock:
        if _config_loaded:
            return

        try:
            import nl_calc_config as config

            for name, value in getattr(config, "CUSTOM_CONSTANTS", {}).items():
                _default_evaluator.CONSTANTS[name] = value

            for name, func in getattr(config, "CUSTOM_FUNCTIONS", {}).items():
                _default_evaluator.FUNCTIONS[name] = func


            for base, unit_dict in getattr(config, "CUSTOM_UNITS", {}).items():
                if base in UNIT_BASE:
                    UNIT_BASE[base].update(unit_dict)
                else:
                    UNIT_BASE[base] = unit_dict

            for unit, canonical in getattr(config, "CUSTOM_ALIASES", {}).items():
                UNIT_ALIASES[unit] = canonical

            for key, (mult, offset) in getattr(config, "CUSTOM_TEMP_CONVERSIONS", {}).items():
                TEMPERATURE_CONVERSIONS[key] = (mult, offset)

            _rebuild_conversions()

        except ImportError:
            pass

        _config_loaded = True


def _ensure_config_loaded() -> None:
    """Ensure user config is loaded (lazy loading)."""
    global _config_loaded
    if not _config_loaded:
        load_user_config()


@lru_cache(maxsize=DEFAULT_CACHE_SIZE)
def _cached_normalize_and_evaluate(expression: str) -> Any:
    """Cache for normalized and evaluated expressions."""
    _ensure_config_loaded()

    normalized, exit_code = normalize_expression(expression, NORMALIZE, PATTERNS)
    if exit_code != 0:
        raise EvaluationError(f"Invalid expression: {expression}")

    return _default_evaluator.evaluate(normalized)


def evaluate_cached(expression: str) -> Any:
    """Evaluate an expression with caching (for repeated identical expressions).

    Handles natural language input and caching. Uses LRU cache with 1024 entries.
    Best for webapps with repeated queries.
    """
    try:
        return _cached_normalize_and_evaluate(expression)
    except EvaluationError:
        raise
    except (ValueError, SyntaxError, RecursionError):
        _cached_normalize_and_evaluate.cache_clear()
        raise


async def evaluate_async(expression: str) -> Any:
    """Evaluate an expression asynchronously (for use with async web frameworks).

    Handles natural language input. Runs evaluation in a thread pool to avoid
    blocking the event loop.
    """
    import asyncio

    def _eval():
        return evaluate_raw(expression)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _eval)


def load_user_config_extended() -> None:
    """Load user-defined configuration including normalize (call after normalize is loaded)."""
    try:
        import nl_calc_config as config
        import nl_calc.normalize as normalize_mod

        for word, num in getattr(config, "CUSTOM_NUMBER_WORDS", {}).items():
            normalize_mod.NUMBER_WORDS[num] = normalize_mod.NUMBER_WORDS.get(num, [])
            normalize_mod.NUMBER_WORDS[num].append(word)

        for word, op in getattr(config, "CUSTOM_OPERATOR_WORDS", {}).items():
            if op not in normalize_mod.OPERATOR_CONVERSIONS:
                normalize_mod.OPERATOR_CONVERSIONS[op] = []
            normalize_mod.OPERATOR_CONVERSIONS[op].append(word)

        if hasattr(normalize_mod, "_rebuild_config"):
            normalize_mod._rebuild_config()

    except ImportError:
        pass


def _safe_pow(base: float, exp: float) -> float:
    """Safe power function with exponent limits to prevent DoS."""
    if abs(exp) > MAX_EXPONENT:
        raise EvaluationError(f"Exponent too large (max {MAX_EXPONENT})")
    if base < 0 and exp != int(exp):
        raise EvaluationError("Cannot raise negative number to non-integer power")
    result = pow(base, exp)
    if abs(result) > MAX_RESULT_VALUE:
        raise EvaluationError("Result too large")
    return result


def _safe_factorial(n: int) -> int:
    """Safe factorial with input bounds checking to prevent DoS."""
    if isinstance(n, float):
        if not n.is_integer():
            raise EvaluationError("factorial requires integer input")
        if abs(n) > MAX_FACTORIAL * 10:
            raise EvaluationError(f"factorial input too large (max {MAX_FACTORIAL})")
    n = int(n)
    if n < 0:
        raise EvaluationError("factorial requires non-negative input")
    if n > MAX_FACTORIAL:
        raise EvaluationError(f"factorial input too large (max {MAX_FACTORIAL})")
    return math.factorial(n)


def _cbrt(x: float) -> float:
    """Cube root that correctly handles negative numbers."""
    if x >= 0:
        return x ** (1 / 3)
    return -((-x) ** (1 / 3))


def _mean(*args: float) -> float:
    """Calculate arithmetic mean."""
    if not args:
        raise EvaluationError("mean requires at least one argument")
    return sum(args) / len(args)


def _std(*args: float) -> float:
    """Calculate standard deviation."""
    if len(args) < 2:
        raise EvaluationError("std requires at least two arguments")
    m = sum(args) / len(args)
    variance = sum((x - m) ** 2 for x in args) / len(args)
    return math.sqrt(variance)


def _sum(*args: float) -> float:
    """Sum all arguments."""
    return sum(args)


def _max(*args: float) -> float:
    """Return maximum of arguments."""
    if not args:
        raise EvaluationError("max requires at least one argument")
    return max(args)


def _min(*args: float) -> float:
    """Return minimum of arguments."""
    if not args:
        raise EvaluationError("min requires at least one argument")
    return min(args)


def _to_bin(x: int) -> str:
    """Convert integer to binary string."""
    return bin(x)


def _to_hex(x: int) -> str:
    """Convert integer to hexadecimal string."""
    return hex(x)


def _to_oct(x: int) -> str:
    """Convert integer to octal string."""
    return oct(x)


def _temp(value: float, from_unit: float | str, to_unit: float | str) -> float:
    """Convert temperature between units."""
    if isinstance(from_unit, float):
        from_unit = {1.0: "K", 0.017453292519943295: "deg"}.get(from_unit, "K")
    if isinstance(to_unit, float):
        to_unit = {1.0: "K", 0.017453292519943295: "deg"}.get(to_unit, "K")
    return convert_temperature(value, str(from_unit), str(to_unit))


def _convert(value: Any, to_unit: str) -> Any:
    """Convert a value with units to a different unit.

    Args:
        value: A number or UnitValue to convert
        to_unit: The target unit to convert to (can be str or UnitValue)

    Returns:
        UnitValue with the converted value and unit
    """
    # Handle case where to_unit is passed as a UnitValue (unit name like 'ft')
    if isinstance(to_unit, UnitValue):
        to_unit = to_unit.unit if to_unit.unit else str(to_unit.value)

    if isinstance(value, UnitValue):
        # Check for temperature conversions (special handling needed)

        cat = get_unit_category(value.unit) if value.unit else None
        if cat == "temperature" and value.unit:
            try:
                converted_val = convert_temperature(value.value, value.unit, to_unit)
                return UnitValue(converted_val, to_unit)
            except ValueError:
                pass  # Fall through to regular conversion
        return value.convert_to(to_unit)
    # If it's just a number without units, assume it's a dimensionless value
    # and try to convert (will fail if not a valid unit)
    return UnitValue(float(value), None).convert_to(to_unit)


# === Complex number functions ===


def _real(z: complex) -> float:
    """Return the real part of a complex number."""
    if isinstance(z, complex):
        return z.real
    return float(z)


def _imag(z: complex) -> float:
    """Return the imaginary part of a complex number."""
    if isinstance(z, complex):
        return z.imag
    return 0.0


def _conj(z: complex) -> complex:
    """Return the complex conjugate."""
    if isinstance(z, complex):
        return z.conjugate()
    return complex(z, 0)


def _phase(z: complex) -> float:
    """Return the phase (argument) of a complex number in radians."""
    return cmath.phase(z)


def _polar(z: complex) -> tuple:
    """Return polar coordinates (r, phi) of a complex number."""
    return cmath.polar(z)


def _rect(r: float, phi: float) -> complex:
    """Return complex number from polar coordinates."""
    return cmath.rect(r, phi)


# === Statistical functions ===


def _median(*args: float) -> float:
    """Calculate median of arguments."""
    if not args:
        raise EvaluationError("median requires at least one argument")
    sorted_args = sorted(args)
    n = len(sorted_args)
    mid = n // 2
    if n % 2 == 0:
        return (sorted_args[mid - 1] + sorted_args[mid]) / 2
    return sorted_args[mid]


def _mode(*args: float) -> float:
    """Calculate mode of arguments."""
    if not args:
        raise EvaluationError("mode requires at least one argument")
    from collections import Counter

    counts = Counter(args)
    max_count = max(counts.values())
    modes = [x for x, c in counts.items() if c == max_count]
    if len(modes) > 1:
        raise EvaluationError("Multiple modes found")
    return modes[0]


def _variance(*args: float) -> float:
    """Calculate population variance."""
    if len(args) < 2:
        raise EvaluationError("variance requires at least two arguments")
    m = sum(args) / len(args)
    return sum((x - m) ** 2 for x in args) / len(args)


def _variance_sample(*args: float) -> float:
    """Calculate sample variance (n-1 denominator)."""
    if len(args) < 2:
        raise EvaluationError("variance_sample requires at least two arguments")
    m = sum(args) / len(args)
    return sum((x - m) ** 2 for x in args) / (len(args) - 1)


# === Bitwise operations ===


def _bitand(a: int, b: int) -> int:
    """Bitwise AND."""
    return int(a) & int(b)


def _bitor(a: int, b: int) -> int:
    """Bitwise OR."""
    return int(a) | int(b)


def _bitxor(a: int, b: int) -> int:
    """Bitwise XOR."""
    return int(a) ^ int(b)


def _bitnot(a: int) -> int:
    """Bitwise NOT (inverts all bits)."""
    return ~int(a)


def _bitlshift(a: int, b: int) -> int:
    """Left shift."""
    return int(a) << int(b)


def _bitrshift(a: int, b: int) -> int:
    """Right shift."""
    return int(a) >> int(b)


# === Combinatorics ===


def _perm(n: int, r: int | None = None) -> int:
    """Calculate permutations P(n,r) = n!/(n-r)!."""
    n = int(n)
    if r is None:
        return math.factorial(n)
    r = int(r)
    if r > n:
        return 0
    return math.perm(n, r)


def _comb(n: int, r: int) -> int:
    """Calculate combinations C(n,r) = n!/(r!(n-r)!)."""
    n, r = int(n), int(r)
    if r > n:
        return 0
    return math.comb(n, r)


# === LCM ===


def _lcm(*args: int) -> int:
    """Calculate least common multiple."""
    if not args:
        raise EvaluationError("lcm requires at least one argument")
    result = int(abs(args[0]))
    for arg in args[1:]:
        result = abs(result * int(arg)) // math.gcd(result, int(arg))
    return result


# === Prime functions ===


def _is_prime(n: int) -> bool:
    """Check if a number is prime."""
    n = int(n)
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def _prime_factors(n: int) -> str:
    """Return prime factorization as a string."""
    n = int(n)
    if n < 2:
        return str(n)

    factors = {}
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors[d] = factors.get(d, 0) + 1
            temp //= d
        d += 1
    if temp > 1:
        factors[temp] = factors.get(temp, 0) + 1

    parts = []
    for prime in sorted(factors.keys()):
        exp = factors[prime]
        if exp == 1:
            parts.append(str(prime))
        else:
            parts.append(f"{prime}^{exp}")
    return " × ".join(parts)


def _next_prime(n: int) -> int:
    """Return the next prime after n."""
    n = int(n)
    candidate = n + 1
    while not _is_prime(candidate):
        candidate += 1
    return candidate


def _prev_prime(n: int) -> int:
    """Return the previous prime before n."""
    n = int(n)
    if n <= 2:
        raise EvaluationError("No prime less than 2")
    candidate = n - 1
    while candidate > 1 and not _is_prime(candidate):
        candidate -= 1
    if candidate < 2:
        raise EvaluationError("No prime less than 2")
    return candidate


# === Random functions ===

_random_generator = random.Random()


def _random() -> float:
    """Return random float in [0, 1)."""
    return _random_generator.random()


def _randint(a: int, b: int) -> int:
    """Return random integer in [a, b]."""
    return _random_generator.randint(int(a), int(b))


def _randrange(a: int, b: int | None = None) -> int:
    """Return random integer in [a, b) or [0, a) if b is None."""
    if b is None:
        return _random_generator.randrange(int(a))
    return _random_generator.randrange(int(a), int(b))


def _uniform(a: float, b: float) -> float:
    """Return random float in [a, b]."""
    return _random_generator.uniform(float(a), float(b))


def _randn() -> float:
    """Return random float from standard normal distribution."""
    return _random_generator.gauss(0, 1)


def _gauss(mu: float, sigma: float) -> float:
    """Return random float from normal distribution with mean mu and std sigma."""
    return _random_generator.gauss(float(mu), float(sigma))


def _seed(s: int | None = None) -> None:
    """Seed the random number generator."""
    _random_generator.seed(s)
    return None


# === Percentage functions ===


def _percent_of(p: float, x: float) -> float:
    """Calculate p percent of x."""
    return (p / 100) * x


def _as_percent(x: float, total: float) -> float:
    """Calculate what percent x is of total."""
    if total == 0:
        raise EvaluationError("Cannot divide by zero")
    return (x / total) * 100


# === Rounding ===


def _round(x: float, ndigits: int = 0) -> float:
    """Round to ndigits decimal places."""
    return round(float(x), int(ndigits))


def _sign(x: float) -> int:
    """Return sign of x: -1, 0, or 1."""
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0


# === Clamping ===


def _clamp(x: float, lo: float, hi: float) -> float:
    """Clamp x to range [lo, hi]."""
    return max(lo, min(hi, x))


# === Hypot ===


def _hypot(*args: float) -> float:
    """Calculate hypotenuse: sqrt(sum(x**2))."""
    return math.hypot(*[float(x) for x in args])


def _complex_aware(
    real_func, cmplx_func=None, *, use_complex_for_negative=False, use_complex_for_abs_gt_one=False
):
    """Create a function that handles both real and complex inputs.

    Args:
        real_func: Function for real numbers (from math module)
        cmplx_func: Function for complex numbers (from cmath module). Defaults to real_func.
        use_complex_for_negative: If True, use complex function for negative real inputs
        use_complex_for_abs_gt_one: If True, use complex function when abs(x) > 1

    Returns:
        A function that handles both real and complex inputs appropriately.
    """
    if cmplx_func is None:
        cmplx_func = getattr(cmath, real_func.__name__, real_func)

    def wrapper(x):
        if isinstance(x, complex):
            return cmplx_func(x)
        if use_complex_for_negative and x < 0:
            return cmplx_func(x)
        if use_complex_for_abs_gt_one and abs(x) > 1:
            return cmplx_func(x)
        return real_func(x)

    wrapper.__name__ = real_func.__name__
    wrapper.__doc__ = f"{real_func.__name__} that handles complex numbers."
    return wrapper


_sqrt = _complex_aware(math.sqrt, cmath.sqrt, use_complex_for_negative=True)
_log = _complex_aware(math.log, cmath.log, use_complex_for_negative=True)
_log10 = _complex_aware(math.log10, cmath.log10, use_complex_for_negative=True)
_log2 = _complex_aware(math.log2, lambda x: cmath.log(x, 2), use_complex_for_negative=True)
_exp = _complex_aware(math.exp, cmath.exp)
_sin = _complex_aware(math.sin, cmath.sin)
_cos = _complex_aware(math.cos, cmath.cos)
_tan = _complex_aware(math.tan, cmath.tan)
_asin = _complex_aware(math.asin, cmath.asin, use_complex_for_abs_gt_one=True)
_acos = _complex_aware(math.acos, cmath.acos, use_complex_for_abs_gt_one=True)
_atan = _complex_aware(math.atan, cmath.atan)


class EvaluationError(Exception):
    """Raised when an expression contains unsafe or unsupported operations."""

    pass


class Memory:
    """Memory registers for storing values (like scientific calculator memory)."""

    def __init__(self) -> None:
        self._registers: dict[str, float] = {}
        self._default_register: float = 0.0
        self._lock = threading.Lock()

    def _get_and_set(self, register: str, new_value: float) -> float:
        """Set a register value and return it (internal, assumes lock held)."""
        if register == "M":
            self._default_register = new_value
            return new_value
        self._registers[register] = new_value
        return new_value

    def _get(self, register: str) -> float:
        """Get a register value (internal, assumes lock held)."""
        if register == "M":
            return self._default_register
        return self._registers.get(register, 0.0)

    def store(self, value: float, register: str = "M") -> float:
        """Store value in register (default: M)."""
        with self._lock:
            return self._get_and_set(register, float(value))

    def recall(self, register: str = "M") -> float:
        """Recall value from register (default: M)."""
        with self._lock:
            return self._get(register)

    def add(self, value: float, register: str = "M") -> float:
        """Add value to register (M+)."""
        with self._lock:
            return self._get_and_set(register, self._get(register) + float(value))

    def subtract(self, value: float, register: str = "M") -> float:
        """Subtract value from register (M-)."""
        with self._lock:
            return self._get_and_set(register, self._get(register) - float(value))

    def clear(self, register: str | None = None) -> None:
        """Clear register (or all if register is None)."""
        with self._lock:
            if register is None:
                self._default_register = 0.0
                self._registers.clear()
            elif register == "M":
                self._default_register = 0.0
            else:
                self._registers.pop(register, None)

    def list_registers(self) -> dict[str, float]:
        """List all registers and their values."""
        with self._lock:
            result = {"M": self._default_register}
            result.update(self._registers.copy())
            return result


# Global memory instance
_memory = Memory()


def memory_store(value: float, register: str = "M") -> float:
    """Store value in memory register."""
    return _memory.store(value, register)


def memory_recall(register: str = "M") -> float:
    """Recall value from memory register."""
    return _memory.recall(register)


def memory_add(value: float, register: str = "M") -> float:
    """Add value to memory register (M+)."""
    return _memory.add(value, register)


def memory_subtract(value: float, register: str = "M") -> float:
    """Subtract value from memory register (M-)."""
    return _memory.subtract(value, register)


def memory_clear(register: str | None = None) -> None:
    """Clear memory register(s)."""
    _memory.clear(register)


def memory_list() -> dict[str, float]:
    """List all memory registers."""
    return _memory.list_registers()


# === Variable storage ===

_user_variables: dict[str, Any] = {}
_variables_lock = threading.Lock()


def setvar(name: str, value: Any) -> Any:
    """Set a user variable.

    Args:
        name: Variable name
        value: Variable value

    Returns:
        The value that was set
    """
    with _variables_lock:
        _user_variables[name] = value
        return value


def getvar(name: str) -> Any:
    """Get a user variable.

    Args:
        name: Variable name

    Returns:
        The variable value or 0 if not found
    """
    with _variables_lock:
        return _user_variables.get(name, 0)


def delvar(name: str) -> None:
    """Delete a user variable."""
    with _variables_lock:
        _user_variables.pop(name, None)


def listvars() -> dict[str, Any]:
    """List all user variables."""
    with _variables_lock:
        return _user_variables.copy()


def clearvars() -> None:
    """Clear all user variables."""
    with _variables_lock:
        _user_variables.clear()


class Evaluator(ast.NodeVisitor):
    """Safe AST-based expression evaluator.

    Evaluates mathematical expressions without using eval().
    Supports arithmetic operators, trig functions, constants,
    logarithms, and unit conversions.
    """

    # Safe mathematical constants
    CONSTANTS: dict[str, Any] = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "inf": math.inf,
        "nan": math.nan,
        # Imaginary unit
        "i": 1j,
        "j": 1j,
        # Physical constants
        "na": 6.02214076e23,
        "avogadro": 6.02214076e23,
        "avogadros": 6.02214076e23,
        "r": 8.314462618,
        "gasconstant": 8.314462618,
        "idealgasconstant": 8.314462618,
        "h": 6.62607015e-34,
        "planck": 6.62607015e-34,
        "planckconstant": 6.62607015e-34,
        "k": 1.380649e-23,
        "boltzmann": 1.380649e-23,
        "boltzmannconstant": 1.380649e-23,
        "c": 299792458,
        "c0": 299792458,
        "speedoflight": 299792458,
        "speedoflightvacuum": 299792458,
        "elementarycharge": 1.602176634e-19,
        "echarge": 1.602176634e-19,
        "f": 96485.33212,
        "faraday": 96485.33212,
        "faradayconstant": 96485.33212,
        "u": 1.66053906660e-27,
        "amu": 1.66053906660e-27,
        "atomicmassunit": 1.66053906660e-27,
        "epsilon0": 8.8541878128e-12,
        "vacuumpermittivity": 8.8541878128e-12,
        # Electromagnetism
        "mu0": 1.25663706212e-6,
        "vacuumpermeability": 1.25663706212e-6,
        "g": 9.80665,
        "standardgravity": 9.80665,
        # Gravitation
        "G": 6.67430e-11,
        "gravitationalconstant": 6.67430e-11,
        # Spectroscopy
        "rydberg": 10973731.568160,
        "rydbergconstant": 10973731.568160,
        # Thermodynamics
        "stefan": 5.670374419e-8,
        "stefanboltzmann": 5.670374419e-8,
        "planckbar": 1.054571817e-34,
        "hbar": 1.054571817e-34,
        "reducedplanck": 1.054571817e-34,
    }

    # Safe mathematical functions
    FUNCTIONS: dict[str, Any] = {
        # Trigonometric (complex-aware)
        "sin": _sin,
        "cos": _cos,
        "tan": _tan,
        "asin": _asin,
        "acos": _acos,
        "atan": _atan,
        "atan2": math.atan2,
        # Hyperbolic
        "sinh": math.sinh,
        "cosh": math.cosh,
        "tanh": math.tanh,
        "asinh": math.asinh,
        "acosh": math.acosh,
        "atanh": math.atanh,
        # Logarithmic (complex-aware)
        "log": _log,
        "log10": _log10,
        "log2": _log2,
        "log1p": math.log1p,
        "exp": _exp,
        "expm1": math.expm1,
        # Power and root (complex-aware)
        "sqrt": _sqrt,
        "pow": _safe_pow,
        # Rounding and absolute
        "abs": abs,
        "floor": math.floor,
        "ceil": math.ceil,
        "trunc": math.trunc,
        "round": _round,
        "sign": _sign,
        # Factorial and combinatorics
        "factorial": _safe_factorial,
        "gcd": math.gcd,
        "lcm": _lcm,
        "perm": _perm,
        "comb": _comb,
        "nPr": _perm,
        "nCr": _comb,
        "cbrt": lambda x: _cbrt(x),
        # Angle conversion
        "degrees": math.degrees,
        "radians": math.radians,
        # Statistical functions
        "mean": _mean,
        "median": _median,
        "mode": _mode,
        "std": _std,
        "variance": _variance,
        "var": _variance,
        "variance_sample": _variance_sample,
        "sum": _sum,
        "max": _max,
        "min": _min,
        # Complex number functions
        "real": _real,
        "imag": _imag,
        "conj": _conj,
        "conjugate": _conj,
        "phase": _phase,
        "polar": _polar,
        "rect": _rect,
        # Base conversion
        "bin": _to_bin,
        "hex": _to_hex,
        "oct": _to_oct,
        # Bitwise operations
        "bitand": _bitand,
        "bitor": _bitor,
        "bitxor": _bitxor,
        "bitnot": _bitnot,
        "bitlshift": _bitlshift,
        "bitrshift": _bitrshift,
        # Prime functions
        "isprime": _is_prime,
        "is_prime": _is_prime,
        "primefactors": _prime_factors,
        "prime_factors": _prime_factors,
        "nextprime": _next_prime,
        "next_prime": _next_prime,
        "prevprime": _prev_prime,
        "prev_prime": _prev_prime,
        # Random functions
        "random": _random,
        "randint": _randint,
        "randrange": _randrange,
        "uniform": _uniform,
        "randn": _randn,
        "gauss": _gauss,
        "seed": _seed,
        # Percentage
        "percentof": _percent_of,
        "percent_of": _percent_of,
        "aspercent": _as_percent,
        "as_percent": _as_percent,
        # Utility
        "clamp": _clamp,
        "hypot": _hypot,
        # Temperature conversion
        "temp": _temp,
        # Unit conversion
        "convert": _convert,
        # Memory functions
        "store": memory_store,
        "recall": memory_recall,
        "M": lambda: memory_recall("M"),
        "Mplus": lambda x: memory_add(x, "M"),
        "Mminus": lambda x: memory_subtract(x, "M"),
        "MC": lambda: memory_clear("M"),
        "MR": lambda: memory_recall("M"),
        # Variable functions
        "setvar": setvar,
        "getvar": getvar,
        "delvar": delvar,
        "listvars": listvars,
        "clearvars": clearvars,
    }

    # Safe binary operators
    BINOPS: dict[type[ast.operator], Any] = {
        ast.Add: (lambda a, b: a + b),
        ast.Sub: (lambda a, b: a - b),
        ast.Mult: (lambda a, b: a * b),
        ast.Div: (lambda a, b: a / b),
        ast.FloorDiv: (lambda a, b: a // b),
        ast.Mod: (lambda a, b: a % b),
        ast.Pow: (lambda a, b: a**b),
        # Bitwise operators
        ast.LShift: (lambda a, b: int(a) << int(b)),
        ast.RShift: (lambda a, b: int(a) >> int(b)),
        ast.BitOr: (lambda a, b: int(a) | int(b)),
        ast.BitXor: (lambda a, b: int(a) ^ int(b)),
        ast.BitAnd: (lambda a, b: int(a) & int(b)),
    }

    # Safe unary operators
    UNARYOPS: dict[type[ast.unaryop], Any] = {
        ast.UAdd: (lambda x: x),
        ast.USub: (lambda x: -x),
        ast.Invert: (lambda x: ~int(x)),
    }

    def __init__(self) -> None:
        """Initialize evaluator with instance-level constants and functions.

        Each evaluator instance has its own copy of constants and functions,
        allowing for instance isolation in PyCalcApp.
        """
        self.CONSTANTS = self.__class__.CONSTANTS.copy()
        self.FUNCTIONS = self.__class__.FUNCTIONS.copy()

    def _parse_unit(self, text: str) -> tuple[float, str | None]:
        """Parse a string that may contain a number and unit."""
        text = text.strip()

        # Check for unit suffix
        for unit in sorted(UNIT_ALIASES.keys(), key=len, reverse=True):
            if text.endswith(unit):
                num_str = text[: -len(unit)].strip()
                if num_str:
                    try:
                        num = float(num_str)
                        return num, UNIT_ALIASES[unit]
                    except ValueError:
                        pass

        # Check if it's just a unit
        if text in UNIT_ALIASES:
            return 1.0, UNIT_ALIASES[text]

        # Try to parse as plain number
        try:
            return float(text), None
        except ValueError:
            raise EvaluationError(f"Cannot parse: '{text}'")

    def _get_conversion_factor(self, from_unit: str, to_unit: str) -> float:
        """Get conversion factor from one unit to another."""
        from_unit = normalize_unit(from_unit)
        to_unit = normalize_unit(to_unit)

        if from_unit == to_unit:
            return 1.0

        key = (from_unit, to_unit)
        if key in UNIT_CONVERSIONS:
            return UNIT_CONVERSIONS[key]

        raise EvaluationError(f"Cannot convert from '{from_unit}' to '{to_unit}'")

    def visit_Constant(self, node: ast.Constant) -> Any:
        """Visit a constant node."""
        if isinstance(node.value, (int, float, complex)):
            return node.value
        if isinstance(node.value, str):
            if node.value in self.CONSTANTS:
                return self.CONSTANTS[node.value]
            # Check if it looks like a number with unit
            for unit in sorted(UNIT_ALIASES.keys(), key=len, reverse=True):
                if node.value.endswith(unit) and len(node.value) > len(unit):
                    num_part = node.value[: -len(unit)].strip()
                    if num_part:
                        try:
                            num = float(num_part)
                            return UnitValue(num, UNIT_ALIASES[unit])
                        except ValueError:
                            pass
            # Return plain string as-is (for function arguments like setvar("x", 10))
            return node.value
        raise EvaluationError(f"Unsupported constant: '{node.value}'")

    def visit_Name(self, node: ast.Name) -> Any:
        """Visit a name node."""
        if node.id in self.CONSTANTS:
            return self.CONSTANTS[node.id]
        if node.id in UNIT_ALIASES:
            return UnitValue(1.0, UNIT_ALIASES[node.id])
        if node.id in self.FUNCTIONS:
            raise EvaluationError(f"Function '{node.id}' used without arguments")
        # Check user variables (thread-safe access)
        with _variables_lock:
            if node.id in _user_variables:
                return _user_variables[node.id]
        raise EvaluationError(f"Unknown name: '{node.id}'")

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        """Visit a binary operation node."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_class = type(node.op)

        # Extract values and units
        left_val = left.value if isinstance(left, UnitValue) else left
        left_unit = normalize_unit(left.unit) if isinstance(left, UnitValue) and left.unit else None
        right_val = right.value if isinstance(right, UnitValue) else right
        right_unit = (
            normalize_unit(right.unit) if isinstance(right, UnitValue) and right.unit else None
        )

        # Check if operation is addition/subtraction with incompatible units
        is_add_sub = op_class in (ast.Add, ast.Sub)
        if is_add_sub and not are_units_compatible(left_unit, right_unit):
            raise EvaluationError(
                f"Cannot add/subtract incompatible units: '{left_unit}' and '{right_unit}'"
            )

        # Handle unit conversion
        if left_unit and right_unit and left_unit != right_unit:
            try:
                factor = self._get_conversion_factor(right_unit, left_unit)
                right_val = right_val * factor
                right_unit = left_unit
            except EvaluationError:
                try:
                    factor = self._get_conversion_factor(left_unit, right_unit)
                    left_val = left_val * factor
                    left_unit = right_unit
                except EvaluationError:
                    pass

        result_unit = left_unit or right_unit

        if op_class not in self.BINOPS:
            raise EvaluationError(f"Unsupported binary operator: '{node.op.__class__.__name__}'")

        result = self.BINOPS[op_class](left_val, right_val)
        return UnitValue(result, result_unit)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        """Visit a unary operation node."""
        operand = self.visit(node.operand)
        op_class = type(node.op)

        if op_class not in self.UNARYOPS:
            raise EvaluationError(f"Unsupported unary operator: '{node.op.__class__.__name__}'")

        result = self.UNARYOPS[op_class](operand)

        if isinstance(operand, UnitValue):
            return UnitValue(result, operand.unit)
        return result

    def visit_Call(self, node: ast.Call) -> Any:
        """Visit a function call node."""
        func_name = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "math":
                func_name = node.func.attr

        if func_name is None or func_name not in self.FUNCTIONS:
            raise EvaluationError(f"Function '{func_name}' is not allowed")

        # Special handling for temp function to preserve unit names
        if func_name == "temp":
            args = []
            for i, arg in enumerate(node.args):
                result = self.visit(arg)
                if i > 0 and isinstance(result, UnitValue):
                    args.append(result.unit or "K")
                elif isinstance(result, str):
                    args.append(result)
                else:
                    args.append(result)
            return self.FUNCTIONS[func_name](*args)

        # Special handling for convert function to preserve UnitValue arguments
        if func_name == "convert":
            args = []
            for i, arg in enumerate(node.args):
                result = self.visit(arg)
                # Pass the full UnitValue, not just the value
                args.append(result)
            return self.FUNCTIONS[func_name](*args)

        # Extract values from arguments, handling UnitValues
        args = []
        for arg in node.args:
            result = self.visit(arg)
            if isinstance(result, UnitValue):
                args.append(result.value)
            else:
                args.append(result)

        return self.FUNCTIONS[func_name](*args)

    def _validate_node(self, node: ast.AST) -> None:
        """Validate that a node is safe to evaluate."""
        node_type = type(node)

        # Allowed node types
        if node_type in (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Call):
            return

        # Forbidden node types
        forbidden = (
            ast.Subscript,
            ast.List,
            ast.Dict,
            ast.Set,
            ast.ListComp,
            ast.DictComp,
            ast.SetComp,
            ast.GeneratorExp,
            ast.Lambda,
            ast.IfExp,
            ast.Compare,
            ast.BoolOp,
        )
        if node_type in forbidden:
            raise EvaluationError(f"Unsupported node type: '{node_type.__name__}'")

        # Attribute access (for math.*)
        if isinstance(node, ast.Attribute):
            if not (isinstance(node.value, ast.Name) and node.value.id == "math"):
                if node.attr not in ("real", "imag", "conjugate"):
                    raise EvaluationError(f"Attribute access '{node.attr}' is not allowed")

    def evaluate(self, expression: str) -> Any:
        """Evaluate an expression and return the result."""
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise EvaluationError(f"Invalid syntax: '{expression}'") from e

        # Validate all nodes
        for node in ast.walk(tree):
            self._validate_node(node)

        result = self.visit(tree.body)

        # Handle result
        if isinstance(result, UnitValue):
            return result
        if isinstance(result, str):
            return result
        if result is None:
            return None  # Functions like seed() and clearvars() return None
        if not isinstance(result, (int, float, complex)):
            raise EvaluationError(f"Result must be a number, got '{type(result)}'")
        return result


def evaluate(expression: str) -> Any:
    """Evaluate a pre-normalized expression (no spaces, no natural language).

    For raw input with spaces or natural language, use evaluate_raw() instead.
    """
    _ensure_config_loaded()
    return _default_evaluator.evaluate(expression)


def evaluate_raw(expression: str) -> Any:
    """Evaluate a raw expression with spaces and/or natural language.

    This function processes the expression through the full normalization
    pipeline, handling spaces inside parentheses and natural language conversion.

    Args:
        expression: A raw expression string (e.g., "(2 * 3)" or "five plus three")

    Returns:
        The result of the evaluation (int, float, str, or UnitValue).

    Raises:
        EvaluationError: If the expression is invalid or contains unsupported operations.
    """
    _ensure_config_loaded()

    normalized, exit_code = normalize_expression(
        expression, NORMALIZE, PATTERNS, skip_validation=True
    )
    if exit_code != 0:
        raise EvaluationError(f"Invalid expression: {expression}")
    return _default_evaluator.evaluate(normalized)


class TimeoutError(Exception):
    """Raised when expression evaluation times out."""

    pass


def evaluate_with_timeout(expression: str, timeout: float = 5.0) -> Any:
    """Evaluate an expression with a timeout for untrusted input.

    This is the recommended function for evaluating expressions from
    untrusted sources (web requests, user input, etc.).

    Args:
        expression: A raw expression string (with spaces, natural language, etc.)
        timeout: Maximum time in seconds (default: 5.0)

    Returns:
        The result of the evaluation (int, float, str, or UnitValue).

    Raises:
        TimeoutError: If evaluation exceeds the timeout.
        EvaluationError: If the expression is invalid or contains unsupported operations.

    Example:
        >>> result = evaluate_with_timeout("2 ** 1000000", timeout=1.0)
        # Raises TimeoutError
    """
    import concurrent.futures

    _ensure_config_loaded()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(evaluate_raw, expression)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            future.cancel()
            raise TimeoutError(f"Evaluation timed out after {timeout} seconds")


_default_evaluator = Evaluator()


def get_default_evaluator() -> Evaluator:
    """Get the default evaluator instance.

    Returns:
        The default Evaluator instance used by module-level functions.
    """
    return _default_evaluator


class PyCalcApp:
    """Thread-safe wrapper for clicalc, optimized for webapp usage.

    Provides caching, instance isolation, and async support for
    long-running applications like web servers.

    Each PyCalcApp instance has its own isolated evaluator with its own
    constants and functions. Registering constants/functions on one instance
    does not affect other instances.

    Usage:
        app = PyCalcApp()
        result = app.calculate("5 + 3")
        result = app.calculate("30m + 100ft")  # with units
    """

    def __init__(
        self,
        cache_size: int = DEFAULT_CACHE_SIZE,
        enable_cache: bool = True,
    ) -> None:
        """Initialize PyCalcApp.

        Args:
            cache_size: LRU cache size (default 1000)
            enable_cache: Whether to enable caching (default True)
        """
        self._evaluator = Evaluator()
        self._enable_cache = enable_cache
        self._cache: OrderedDict[str, Any] | None = OrderedDict() if enable_cache else None
        self._lock = threading.Lock()
        self._cache_max_size = cache_size

    def calculate(self, expression: str) -> Any:
        """Evaluate an expression (thread-safe).

        Args:
            expression: Math expression (e.g., "5 + 3" or "five plus two")

        Returns:
            Result (int, float, str, or UnitValue)

        Raises:
            EvaluationError: If expression is invalid
        """
        if self._cache is not None:
            with self._lock:
                if expression in self._cache:
                    self._cache.move_to_end(expression)
                    return self._cache[expression]

        result = self._evaluate_internal(expression)

        if self._cache is not None:
            with self._lock:
                if len(self._cache) >= self._cache_max_size:
                    self._cache.popitem(last=False)
                self._cache[expression] = result

        return result

    async def calculate_async(self, expression: str) -> Any:
        """Evaluate an expression asynchronously (thread-safe).

        Args:
            expression: Math expression

        Returns:
            Result (int, float, str, or UnitValue)
        """
        import asyncio

        def _eval():
            return self.calculate(expression)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _eval)

    def _evaluate_internal(self, expression: str) -> Any:
        """Internal evaluation that uses the instance's evaluator."""

        normalized, exit_code = normalize_expression(
            expression, NORMALIZE, PATTERNS, skip_validation=True
        )
        if exit_code != 0:
            raise EvaluationError(f"Invalid expression: {expression}")

        return self._evaluator.evaluate(normalized)

    def register_constant(self, name: str, value: float) -> None:
        """Register a custom constant on this instance (thread-safe).

        Unlike the global register_constant function, this only affects
        this PyCalcApp instance.
        """
        with self._lock:
            self._evaluator.CONSTANTS[name] = value

    def register_function(self, name: str, func: Any) -> None:
        """Register a custom function on this instance (thread-safe).

        Unlike the global register_function function, this only affects
        this PyCalcApp instance.
        """
        with self._lock:
            self._evaluator.FUNCTIONS[name] = func

    def clear_cache(self) -> None:
        """Clear the evaluation cache."""
        if self._cache is not None:
            with self._lock:
                self._cache.clear()

    @property
    def cache_size(self) -> int:
        """Return current cache size."""
        if self._cache is None:
            return 0
        with self._lock:
            return len(self._cache)

# === normalize.py ===
import argparse
import re
import sys
import traceback
from functools import lru_cache
from typing import Any, Mapping, Pattern


__all__ = [
    "evaluate",
    "EvaluationError",
    "UnitValue",
    "run",
    "normalize",
    "normalize_expression",
    "main",
    "print_help",
    "NORMALIZE",
    "PATTERNS",
    "MAX_INPUT_LENGTH",
    "MAX_NESTING_DEPTH",
]

MAX_INPUT_LENGTH = 10000
MAX_NESTING_DEPTH = 100

# Pre-computed sorted units list for performance (avoid re-sorting each call)
_UNITS_BY_LENGTH: list[str] = sorted(UNIT_ALIASES.keys(), key=len, reverse=True)

# Common unit prefixes for faster lookup (most frequently used units first)
_COMMON_UNITS: list[str] = [
    "m",
    "km",
    "cm",
    "mm",
    "s",
    "ms",
    "us",
    "ns",
    "min",
    "h",
    "d",
    "g",
    "kg",
    "mg",
    "lb",
    "oz",
    "L",
    "mL",
    "gal",
    "J",
    "kJ",
    "W",
    "kW",
    "Pa",
    "atm",
    "N",
    "V",
    "A",
    "Hz",
    "B",
    "KB",
    "MB",
    "GB",
    "in",
    "ft",
    "yd",
    "mi",
    "yr",
    "K",
    "C",
    "F",
]

# Build a prefix set for O(1) lookup of common unit starts
_UNIT_PREFIXES: set[str] = set()
for unit in _COMMON_UNITS:
    for i in range(1, len(unit) + 1):
        _UNIT_PREFIXES.add(unit[:i])


# Operator conversions: operator -> list of word representations
OPERATOR_CONVERSIONS: dict[str, list[str]] = {
    "+": ["plus", "positive"],
    "-": ["minus", "negative"],
    "*": ["times", "multiplied by"],
    "/": ["divided by", "over", "per", "divide"],
    "**": ["^", "raised to", "raised to the power", "to the power of"],
    ".": ["point"],
    ",": [],
    "&": ["AND", "and", "bitand", "bit and"],
    "|": ["OR", "or", "bitor", "bit or"],
    "^": ["XOR", "xor", "bitxor", "bit xor"],
    "<<": ["left shift", "shift left", "lshift"],
    ">>": ["right shift", "shift right", "rshift"],
    "~": ["NOT", "not", "bitnot", "bit not"],
    "%": ["mod", "modulo", "percent", "remainder"],
    # Unit conversion words - these get split out as tokens
    "IN": ["in", "into"],
    "TO": ["to", "as"],
}

# Function name mappings (for function name normalization)
# Maps common names/aliases to canonical function names
FUNCTION_MAPPINGS: dict[str, str] = {
    "square root": "sqrt",
    "sqrt": "sqrt",
    "sine": "sin",
    "sin": "sin",
    "cosine": "cos",
    "cos": "cos",
    "tangent": "tan",
    "tan": "tan",
    "arcsine": "asin",
    "asin": "asin",
    "inverse sine": "asin",
    "arccos": "acos",
    "acos": "acos",
    "inverse cosine": "acos",
    "arctan": "atan",
    "atan": "atan",
    "inverse tangent": "atan",
    "absolute": "abs",
    "abs": "abs",
    "magnitude": "abs",
    "ln": "log",
    "log": "log",
    "log10": "log10",
    "log2": "log2",
    "exp": "exp",
    "temp": "temp",
    "bin": "bin",
    "hex": "hex",
    "oct": "oct",
    "mean": "mean",
    "average": "mean",
    "median": "median",
    "mode": "mode",
    "std": "std",
    "stdev": "std",
    "variance": "variance",
    "var": "var",
    "sum": "sum",
    "max": "max",
    "min": "min",
    "gcd": "gcd",
    "lcm": "lcm",
    "perm": "perm",
    "comb": "comb",
    "nPr": "nPr",
    "nCr": "nCr",
    "factorial": "factorial",
    "fact": "factorial",
    "real": "real",
    "imag": "imag",
    "conj": "conj",
    "conjugate": "conj",
    "phase": "phase",
    "polar": "polar",
    "rect": "rect",
    "bitand": "bitand",
    "bitor": "bitor",
    "bitxor": "bitxor",
    "bitnot": "bitnot",
    "isprime": "isprime",
    "primefactors": "primefactors",
    "prime_factors": "primefactors",
    "nextprime": "nextprime",
    "prevprime": "prevprime",
    "random": "random",
    "randint": "randint",
    "randn": "randn",
    "gauss": "gauss",
    "seed": "seed",
    "percentof": "percentof",
    "percent_of": "percentof",
    "aspercent": "aspercent",
    "as_percent": "aspercent",
    "clamp": "clamp",
    "hypot": "hypot",
    "round": "round",
    "sign": "sign",
    "cbrt": "cbrt",
    "cube root": "cbrt",
    "ceil": "ceil",
    "ceiling": "ceil",
    "floor": "floor",
    "store": "store",
    "recall": "recall",
    "Mplus": "Mplus",
    "Mminus": "Mminus",
    "MC": "MC",
    "MR": "MR",
    "setvar": "setvar",
    "getvar": "getvar",
    "delvar": "delvar",
    "listvars": "listvars",
    "clearvars": "clearvars",
}

# Number words
NUMBER_WORDS: dict[str, list[str]] = {
    "0": ["zero"],
    "1": ["one"],
    "2": ["two"],
    "3": ["three"],
    "4": ["four"],
    "5": ["five"],
    "6": ["six"],
    "7": ["seven"],
    "8": ["eight"],
    "9": ["nine"],
    "10": ["teen", "ten"],
    "11": ["eleven"],
    "12": ["twelve"],
    "13": ["thirteen"],
    "14": ["fourteen"],
    "15": ["fifteen"],
    "16": ["sixteen"],
    "17": ["seventeen"],
    "18": ["eighteen"],
    "19": ["nineteen"],
    "20": ["twenty"],
    "30": ["thirty"],
    "40": ["forty"],
    "50": ["fifty"],
    "60": ["sixty"],
    "70": ["seventy"],
    "80": ["eighty"],
    "90": ["ninety"],
    "100": ["hundred"],
    "1000": ["thousand"],
    "1000000": ["million"],
    "1000000000": ["billion"],
    "1000000000000": ["trillion"],
    "1000000000000000": ["quadrillion"],
    "1000000000000000000": ["quintillion"],
    "0.5": ["half"],
    "0.25": ["quarter"],
    "0.001": ["thousandth"],
    "0.000001": ["millionth"],
    "0.000000001": ["billionth"],
}

# Phrases to strip from input
STRIPPED_PHRASES: list[str] = [
    "what's",
    "what is",
    "a ",
    "\\bof\\b",
    "?",
    "calculate",
    "compute",
    "convert",
    "tell me",
    "give me",
    "the ",
]

# Physical constants word mappings
CONSTANT_WORDS: dict[str, list[str]] = {
    "na": ["avogadro", "avogadros", "avogadro number"],
    "r": ["gas constant", "ideal gas constant", "molar gas constant"],
    "h": ["planck", "planck constant"],
    "k": ["boltzmann", "boltzmann constant"],
    "c": ["speed of light", "speed of light in vacuum", "c zero"],
    "elementarycharge": ["elementary charge", "e charge"],
    "f": ["faraday", "faraday constant"],
    "u": ["atomic mass", "atomic mass unit", "amu"],
    "epsilon0": ["vacuum permittivity", "permittivity of free space"],
    "mu0": ["vacuum permeability", "permeability of free space", "magnetic constant"],
    "g": ["gravity", "standard gravity", "earth gravity"],
    "G": ["gravitational constant", "newton constant", "big g"],
    "me": ["electron mass"],
    "mp": ["proton mass"],
    "mn": ["neutron mass"],
    "re": ["electron radius", "classical electron radius"],
    "alpha": ["fine structure constant", "sommerfeld"],
    "rydberg": ["rydberg constant"],
    "stefan": ["stefan boltzmann", "stefan-boltzmann constant"],
    "wien": ["wien constant", "wien displacement"],
}


def _build_config() -> tuple[dict, dict]:
    """Build normalization configuration."""
    # Sort numbers by key descending for matching
    sorted_numbers = {k: NUMBER_WORDS[k] for k in sorted(NUMBER_WORDS.keys(), reverse=True)}

    # Build symbols list
    symbols = ["(", ")"] + list(OPERATOR_CONVERSIONS.keys())

    # Build word to operator mapping
    word_to_operator: dict[str, str] = {}
    for operator, words in OPERATOR_CONVERSIONS.items():
        for word in words:
            word_to_operator[word] = operator

    # Build word to number mapping (sorted by length for correct replacement)
    word_to_number: dict[str, str] = {}
    for num_val, words in NUMBER_WORDS.items():
        for word in words:
            word_to_number[word] = num_val
    sorted_word_to_number = dict(
        sorted(word_to_number.items(), key=lambda x: len(x[0]), reverse=True)
    )

    # Build word to constant mapping
    word_to_constant: dict[str, str] = {}
    for const_key, words in CONSTANT_WORDS.items():
        for word in words:
            word_to_constant[word] = const_key
    sorted_word_to_constant = dict(
        sorted(word_to_constant.items(), key=lambda x: len(x[0]), reverse=True)
    )

    # Build combined word replacement regex for performance (constants + operators)
    all_words = {}
    all_words.update(sorted_word_to_constant)
    all_words.update(sorted_word_to_number)
    all_words.update(word_to_operator)

    # Sort by length descending for correct matching
    sorted_all_words = dict(sorted(all_words.items(), key=lambda x: len(x[0]), reverse=True))

    # Build normalize config
    normalize_config = {
        "symbols": symbols,
        "convert": OPERATOR_CONVERSIONS,
        "word_to_operator": word_to_operator,
        "word_to_number": sorted_word_to_number,
        "word_to_constant": sorted_word_to_constant,
        "word_to_all": sorted_all_words,
        "numbers": sorted_numbers,
        "functions": FUNCTION_MAPPINGS,
    }

    # Compile regex patterns
    compiled_patterns: dict[str, re.Pattern[str]] = {
        "space": re.compile(r"\s+"),
        "point": re.compile(r"\."),
        "negative": re.compile(r"\-"),
        "thousands_separator": re.compile(r","),
        "inline_negative": re.compile(r"^[a-zA-Z]+-[a-zA-Z]+$"),
        "parenthesis": re.compile(r"\(|\)"),
        "operators": re.compile(f"^({'|'.join([re.escape(s) for s in symbols])}){{1}}$"),
        "stripped_chars": re.compile(f"({'|'.join([re.escape(p) for p in STRIPPED_PHRASES])})"),
        "int": re.compile(r"^[-|+]?[0-9]\d*$"),
        "float": re.compile(r"^[-|+]?[0-9]\d*\.\d+?$"),
        "int_number_combine": re.compile(r"^[-|+|*]?[0-9]\d*$"),
        "valid_operations": re.compile(
            f"^({'|'.join([re.escape(s) for s in symbols] + [re.escape(f) for f in FUNCTION_MAPPINGS.values()] + [re.escape(c) for c in CONSTANT_WORDS.keys()])}){{1}}$"
        ),
    }

    return normalize_config, compiled_patterns


# Module-level config (computed once)
NORMALIZE, PATTERNS = _build_config()


def _rebuild_config() -> None:
    """Rebuild NORMALIZE and PATTERNS after adding custom words."""
    global NORMALIZE, PATTERNS
    NORMALIZE, PATTERNS = _build_config()


@lru_cache(maxsize=1024)
def check_if_number(token: str) -> dict:
    """Check if a token represents a number.

    Returns a dict with:
        bool: whether the token is a number
        converted: the parsed number or original string
        type: the original input type
    """
    patterns = PATTERNS
    if len(token) == 0:
        return {"bool": False, "converted": token, "type": type(token)}

    # Remove thousands separator
    cleaned = patterns["thousands_separator"].sub("", token)

    # Check for percentage (e.g., "50%")
    if cleaned.endswith("%"):
        num_part = cleaned[:-1]
        try:
            val = float(num_part) / 100
            return {"bool": True, "converted": val, "type": type(token)}
        except ValueError:
            pass

    # Check for complex number suffix (e.g., "3i", "4j")
    if cleaned.endswith(("i", "j")) and len(cleaned) > 1:
        num_part = cleaned[:-1]
        if num_part in ("+", "-"):
            # Just "+i" or "-i"
            return {
                "bool": True,
                "converted": complex(0, 1 if num_part == "+" else -1),
                "type": type(token),
            }
        try:
            val = float(num_part)
            return {"bool": True, "converted": complex(0, val), "type": type(token)}
        except ValueError:
            pass

    # Check for hex prefix (0x)
    if cleaned.lower().startswith("0x"):
        try:
            val = int(cleaned, 16)
            return {"bool": True, "converted": val, "type": type(token)}
        except ValueError:
            pass

    # Check for binary prefix (0b)
    if cleaned.lower().startswith("0b"):
        try:
            val = int(cleaned, 2)
            return {"bool": True, "converted": val, "type": type(token)}
        except ValueError:
            pass

    # Check for octal prefix (0o)
    if cleaned.lower().startswith("0o"):
        try:
            val = int(cleaned, 8)
            return {"bool": True, "converted": val, "type": type(token)}
        except ValueError:
            pass

    # Check if it's a plain number
    if patterns["int"].match(cleaned):
        return {"bool": True, "converted": int(cleaned), "type": type(token)}
    if patterns["float"].match(cleaned):
        return {"bool": True, "converted": float(cleaned), "type": type(token)}
    if patterns["int_number_combine"].match(cleaned):
        return {"bool": True, "converted": cleaned, "type": type(token)}

    # Check if it's a number with unit (use pre-computed sorted list)
    for unit in _UNITS_BY_LENGTH:
        if cleaned.endswith(unit):
            num_part = cleaned[: -len(unit)]
            if num_part:
                try:
                    val = float(num_part)
                    return {"bool": True, "converted": val, "type": type(token)}
                except ValueError:
                    pass

    return {"bool": False, "converted": token, "type": type(token)}


def validate_for_eval(tokens: list, patterns: Mapping[str, Pattern[str]]) -> bool:
    """Validate that all tokens are either numbers, valid operations, units, or known constants."""

    known_constants = set(_default_evaluator.CONSTANTS.keys())

    for token in tokens:
        # Skip tokens that look like function calls (contain parentheses)
        if "(" in token or ")" in token:
            continue
        if not check_if_number(token)["bool"]:
            if not patterns["valid_operations"].match(token):
                if not is_unit(token):
                    if token not in known_constants:
                        raise ValueError(f"Invalid token: {token}")
    return True


def combine_number_parts(
    number_parts: list, patterns: Mapping[str, Pattern[str]], split_tokens: list
) -> list:
    """Combine number parts into a single mathematical expression."""
    result = []
    for i, part in enumerate(number_parts):
        if i == 0:
            if i != len(number_parts) - 1 and part < 10 and number_parts[i + 1] == 10:
                result.append(f"{part + number_parts[i + 1]}")
            elif part != 10:
                result.append(str(part))
        else:
            if i != len(number_parts) - 1 and part < 10 and number_parts[i + 1] == 10:
                result.append(f"{part + number_parts[i + 1]}")
            elif part == 10 and number_parts[i - 1] < 10:
                pass
            elif part < 10:
                result.append(f"+{part}")
            elif number_parts[i - 1] < 10 and part < 100:
                result.append(f"+{part}")
            elif number_parts[i - 1] < 100:
                result.append(f"*{part}")
            else:
                result.append(f"+{part}")

    if patterns["negative"].match(split_tokens[0]):
        result.insert(0, "-")

    return result


def convert_numbers(number_info: list, patterns: Mapping[str, Pattern[str]]) -> str:
    """Convert a token that may contain number words to a numeric expression."""
    if number_info[1]["bool"]:
        return number_info[0]

    split_tokens = number_info[0].split("@")
    number_parts = []

    for token in split_tokens:
        check_result = check_if_number(token)
        if check_result["bool"]:
            number_parts.append(check_result["converted"])

    combined = combine_number_parts(number_parts, patterns, split_tokens)

    if validate_for_eval(combined, patterns):
        joined = "".join(combined)
        if joined:
            try:
                result = evaluate(joined)
                if isinstance(result, UnitValue):
                    return str(result.value)
                return str(result)
            except EvaluationError:
                return number_info[0]
        return number_info[0]

    return ""


def apply_math_functions(
    tokens: list, operators: dict, patterns: Mapping[str, Pattern[str]]
) -> list:
    """Convert function names to math function calls.

    Rules:
    - sin40 + 2 -> math.sin(40) + 2 (no paren means only first number is args)
    - sin(40+2) -> math.sin(40+2) (user's parens preserved)
    - sin of 40 -> math.sin(40)
    """
    output_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token in operators["functions"]:
            output_tokens.append(operators["functions"][token])
            next_token = tokens[i + 1] if i + 1 < len(tokens) else None

            if next_token is not None and next_token == "(":
                pass
            else:
                output_tokens.append("(")

                while i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    is_operator = patterns["operators"].match(next_token) is not None

                    if is_operator and next_token != ".":
                        break
                    if next_token == ")":
                        break

                    output_tokens.append(next_token)
                    i += 1

                    if next_token == ".":
                        continue

                output_tokens.append(")")
        else:
            output_tokens.append(token)

        i += 1

    return output_tokens


def error_message(original: str, exception: BaseException, verbose: bool = False) -> None:
    """Print an error message based on the exception type."""
    exc_type = type(exception)
    if exc_type is ValueError:
        print(f"Unrecognized command: '{original}'", file=sys.stderr)
    elif exc_type is ZeroDivisionError:
        print(f"Can't divide by 0: '{original}'", file=sys.stderr)
    elif exc_type is EvaluationError:
        print(f"Evaluation error: {exception}", file=sys.stderr)
    else:
        if verbose:
            traceback.print_exc()
        else:
            print(f"Error: {exception}", file=sys.stderr)


def convert_from_human_handler(
    tokens: list,
    operators: dict,
    patterns: Mapping[str, Pattern[str]],
    original: str,
) -> tuple[list, bool]:
    """Convert human-readable number words to numeric values."""
    is_valid = False

    for i in range(len(tokens)):
        is_number = check_if_number(tokens[i])

        if not is_number["bool"]:
            replaced = tokens[i]
            word_to_number = operators.get("word_to_number", {})
            for word, num_val in word_to_number.items():
                replaced = replaced.replace(word, f"@{num_val}")
            tokens[i] = {0: replaced, 1: is_number}
        else:
            tokens[i] = {0: tokens[i], 1: is_number}

        try:
            tokens[i] = convert_numbers(tokens[i], patterns)
            is_valid = True
        except ValueError:
            tokens[i] = tokens[i][0] if isinstance(tokens[i], dict) else tokens[i]
            error_message(original, ValueError())
            break

    return tokens, is_valid


def _handle_negative_token(
    tokens: list,
    index: int,
    patterns: Mapping[str, Pattern[str]],
) -> tuple[list, list]:
    """Handle negative token patterns like 'five-six' or '5.-2'."""
    temp = tokens[index].split("-")
    tokens[index - 2] = f"{tokens[index - 2]}.{temp[0]}"
    tokens[index - 1] = ""
    tokens[index] = f"-{temp[1]}"
    return tokens, [index - 1]


def _should_handle_inline_negative(
    tokens: list, index: int, patterns: Mapping[str, Pattern[str]]
) -> bool:
    """Check if token should be handled as inline negative."""
    return bool(
        index >= 2
        and patterns["inline_negative"].match(tokens[index])
        and patterns["point"].match(tokens[index - 1])
        and not check_if_number(tokens[index - 2])["bool"]
    )


def _should_handle_decimal_negative(
    tokens: list, index: int, patterns: Mapping[str, Pattern[str]]
) -> bool:
    """Check if token should be handled as decimal negative."""
    return bool(
        index >= 2
        and patterns["negative"].search(tokens[index])
        and patterns["point"].match(tokens[index - 1])
        and check_if_number(tokens[index - 2])["bool"]
    )


def split_at_operators(
    expression: str, operators: dict, patterns: Mapping[str, Pattern[str]]
) -> list:
    """Split an expression string at operator boundaries."""
    # Escape operators for splitting
    for symbol in operators["symbols"]:
        if symbol != "-":
            expression = expression.replace(symbol, f"\\{symbol}\\")

    tokens = [t.strip() for t in expression.split("\\") if t.strip()]

    indices_to_remove = []

    for i in range(len(tokens)):
        is_num = check_if_number(tokens[i])["bool"]
        is_op = patterns["operators"].match(tokens[i]) is not None

        if not is_num and not is_op:
            if _should_handle_inline_negative(tokens, i, patterns):
                tokens, removed = _handle_negative_token(tokens, i, patterns)
                indices_to_remove.extend(removed)
            elif _should_handle_decimal_negative(tokens, i, patterns):
                tokens, removed = _handle_negative_token(tokens, i, patterns)
                indices_to_remove.extend(removed)
            elif tokens[i][:1] != "-" and tokens[i - 1] != ".":
                tokens[i] = tokens[i].replace("-", "")
            elif patterns["negative"].match(tokens[i][:1]):
                tokens[i] = f"-{tokens[i][1:].replace('-', '')}"

    if indices_to_remove:
        for idx in reversed(indices_to_remove):
            tokens.pop(idx)

    return tokens


def normalize(expression: str, operators: dict, patterns: Mapping[str, Pattern[str]]) -> str:
    """Normalize an expression by removing filler words and applying conversions."""
    # Use combined word replacement for efficiency (single pass)
    # Use word boundaries to avoid replacing parts of words
    word_to_all = operators.get("word_to_all", {})
    for word, replacement in sorted(word_to_all.items(), key=lambda x: len(x[0]), reverse=True):
        # Use regex with word boundaries to only match whole words
        expression = re.sub(r"\b" + re.escape(word) + r"\b", replacement, expression)

    # Strip phrases
    expression = patterns["stripped_chars"].sub("", expression)

    # Convert percentages (e.g., 50% -> 0.5)
    expression = re.sub(r"(\d+(?:\.\d+)?)%", lambda m: str(float(m.group(1)) / 100), expression)

    # Convert 'i' suffix to 'j' for complex numbers (e.g., 3+4i -> 3+4j)
    # Match: number followed by 'i' (not preceded by another letter)
    expression = re.sub(r"(\d)i\b", r"\1j", expression)
    # Handle standalone 'i' preceded by operators or at start
    expression = re.sub(r"(^|[+\-*/(])i\b", r"\g<1>1j", expression)

    # Replace whitespace outside parentheses with nothing
    # Preserve whitespace inside parentheses to separate function args
    result = []
    depth = 0
    for char in expression:
        if char == "(":
            depth += 1
            if depth > MAX_NESTING_DEPTH:
                raise ValueError(f"Expression nesting too deep (max {MAX_NESTING_DEPTH})")
            result.append(char)
        elif char == ")":
            depth -= 1
            result.append(char)
        elif char.isspace():
            if depth > 0:
                result.append(char)  # Keep space inside parentheses
            # Skip space outside parentheses
        else:
            result.append(char)

    expression = "".join(result)

    return expression


def _preprocess_units(expression: str) -> str:
    """Preprocess expression to add multiplication before units."""
    result = []
    i = 0
    depth = 0
    units = _UNITS_BY_LENGTH  # Use pre-computed list
    prefixes = _UNIT_PREFIXES  # Use pre-computed prefix set

    while i < len(expression):
        char = expression[i]

        if char == "(":
            depth += 1
            result.append(char)
            i += 1
        elif char == ")":
            depth -= 1
            result.append(char)
            i += 1
        elif char.isdigit():
            # Look for number followed by optional whitespace and unit
            num_start = i
            while i < len(expression) and (expression[i].isdigit() or expression[i] == "."):
                i += 1
            num = expression[num_start:i]

            # Skip whitespace between number and unit
            while i < len(expression) and expression[i].isspace():
                i += 1

            if i < len(expression):
                # Quick check: does the remaining start with a potential unit prefix?
                remaining = expression[i:]
                if remaining and remaining[0] not in prefixes:
                    # No unit possible, skip unit search
                    result.append(num)
                else:
                    # Check for unit using pre-computed sorted list
                    found_unit = False
                    for unit in units:
                        if remaining.startswith(unit):
                            result.append(num)
                            result.append("*")
                            result.append(unit)
                            i += len(unit)
                            found_unit = True
                            break
                    if not found_unit:
                        result.append(num)
            else:
                result.append(num)
        else:
            result.append(char)
            i += 1

    return "".join(result)


def _handle_unit_conversion_from_tokens(tokens: list) -> list:
    """Handle unit conversion patterns from tokens like ['2meters', 'in', 'feet'].

    Detects patterns like: [number+unit, 'in'/'to'/'into'/'as', target_unit]
    Converts to: ['convert(number*unit,target_unit)']
    """
    if len(tokens) < 3:
        return tokens

    # Look for pattern: token with number+unit followed by conversion word followed by unit
    conversion_words = {"in", "to", "into", "as"}

    for i in range(len(tokens) - 2):
        # Check if tokens[i] ends with a unit (has number prefix)
        token = tokens[i]
        for unit in _UNITS_BY_LENGTH:
            if token.endswith(unit):
                num_part = token[: -len(unit)]
                if num_part and num_part[-1].isdigit():
                    # Found number+unit pattern
                    from_unit = unit
                    from_unit_normalized = UNIT_ALIASES.get(from_unit, from_unit)

                    # Check conversion word (uppercase from operator split)
                    conv_word = tokens[i + 1].upper()
                    if conv_word in {"IN", "TO"}:
                        # Check target unit
                        to_token = tokens[i + 2]
                        to_unit_normalized = None

                        for unit2 in _UNITS_BY_LENGTH:
                            if to_token == unit2 or to_token.endswith(unit2):
                                to_unit_normalized = UNIT_ALIASES.get(unit2, unit2)
                                break

                        if to_unit_normalized and from_unit_normalized in UNIT_ALIASES:

                            cat1 = get_unit_category(from_unit_normalized)
                            cat2 = get_unit_category(to_unit_normalized)

                            if (
                                cat1
                                and cat2
                                and are_units_compatible(from_unit_normalized, to_unit_normalized)
                            ):
                                # Replace the three tokens with the convert function
                                new_tokens = (
                                    tokens[:i]
                                    + [
                                        f"convert({num_part}*{from_unit_normalized},{to_unit_normalized})"
                                    ]
                                    + tokens[i + 3 :]
                                )
                                return new_tokens

    return tokens


def normalize_expression(
    expression: str,
    operators: dict,
    patterns: Mapping[str, Pattern[str]],
    skip_validation: bool = False,
) -> tuple[str, int]:
    """Normalize an expression without evaluating it.

    This is useful when you want to use a custom evaluator.

    Args:
        expression: The raw expression to normalize
        operators: The operators configuration dict
        patterns: The compiled regex patterns dict
        skip_validation: If True, skip token validation (for custom evaluators)

    Returns:
        tuple: (normalized_expression, exit_code) - normalized_expression is the
               normalized string, exit_code is 0 on success, non-zero on error
    """
    if len(expression) > MAX_INPUT_LENGTH:
        return f"Error: Input too long (max {MAX_INPUT_LENGTH} characters)", 2

    expression = normalize(expression, operators, patterns)
    tokens = split_at_operators(expression, operators, patterns)
    tokens, is_valid = convert_from_human_handler(tokens, operators, patterns, expression)

    if not is_valid:
        return "", 1

    tokens = apply_math_functions(tokens, operators, patterns)

    # Handle unit conversion patterns from tokens (e.g., "2m in feet" -> tokens ['2m', 'in', 'feet'])
    tokens = _handle_unit_conversion_from_tokens(tokens)
    joined = "".join(tokens)

    joined = _preprocess_units(joined)

    if not skip_validation:
        try:
            validate_for_eval(tokens, patterns)
        except ValueError:
            return "", 1

    return joined, 0


def run(
    expression: str,
    operators: dict,
    patterns: Mapping[str, Pattern[str]],
    output_format: str = "plain",
    show_expression: bool = True,
) -> tuple[Any, int]:
    """Process a single expression: normalize, convert, evaluate, and print result.

    Returns:
        tuple: (result, exit_code) - result is the evaluated value or None on error
    """
    original = expression
    joined, exit_code = normalize_expression(expression, operators, patterns)

    if exit_code != 0:
        if exit_code == 2:
            print(joined, file=sys.stderr)
        return None, exit_code

    try:
        result = evaluate(joined)
        if output_format == "json":
            import json

            if show_expression:
                print(json.dumps({"expression": joined, "result": str(result)}))
            else:
                print(json.dumps({"result": str(result)}))
        else:
            if show_expression:
                print(f"{joined} -> {result}")
            else:
                print(result)
        return result, 0
    except ZeroDivisionError as e:
        error_message(original, e)
        return None, 1
    except EvaluationError as e:
        error_message(original, e)
        return None, 1


def _run_repl(show_expression: bool = True) -> int:
    """Run interactive REPL mode."""
    import sys

    print("nl-calc interactive mode. Type 'help' for available commands, 'quit' or 'exit' to exit.")
    print()

    history: list[tuple[str, Any]] = []

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        if line.lower() in ("quit", "exit", "exit()"):
            break

        if line.lower() == "help":
            print_help()
            continue

        if line.lower() == "history":
            for expr, result in history:
                print(f"{expr} -> {result}")
            continue

        if line.lower() == "clear":
            history.clear()
            continue

        _, exit_code = run(line, NORMALIZE, PATTERNS, "plain", show_expression)

        if exit_code == 0:
            history.append((line, _))

    return 0


def print_help() -> None:
    """Print available operators and functions."""
    lines = [
        "Available operators:",
        "  Arithmetic: +, -, *, /, **",
        "  Words: plus, minus, times, divided by, over, raised to, to the power of",
        "  Negative: negative, minus",
        "",
        "Available functions:",
        "  sin, cos, tan, asin, acos, atan, atan2",
        "  sinh, cosh, tanh, asinh, acosh, atanh",
        "  sqrt, log, log10, log2, log1p",
        "  abs, floor, ceil, trunc, factorial, gcd, pow",
        "",
        "Available constants:",
        "  pi, e, tau, inf, nan",
        "  avogadro, gas constant, planck, boltzmann",
        "  c (speed of light), elementary charge, faraday, amu",
        "",
        "Available units:",
        "  Length: m, km, cm, mm, um, nm, pm, in, ft, yd, mi, ly, au, pc",
        "  Time: s, ms, us, ns, ps, min, h, d, wk, yr",
        "  Data: B, KB, MB, GB, TB, PB",
        "  Mass: kg, g, mg, ug, ng, lb, oz, ton",
        "  Volume: L, mL, gal, qt, pt, cup",
        "  Pressure: Pa, kPa, MPa, GPa, bar, atm, psi",
        "  Energy: J, kJ, MJ, GJ, cal, kcal, Wh, kWh, BTU, eV",
        "  Power: W, kW, MW, GW, mW, hp",
        "",
        "Examples:",
        "  calc five plus two",
        '  calc "twenty plus five"',
        '  calc "sin of 3.14159"',
        "  calc 30m + 100ft",
        "  calc (30m+100ft)/2",
    ]
    for line in lines:
        print(line)


def main() -> int:
    """Main entry point for CLI."""
    import os
    # __version__ is defined at module level

    parser = argparse.ArgumentParser(
        description="Natural language math expression calculator",
        add_help=False,
    )
    parser.add_argument(
        "expression", nargs="*", help="Expression to evaluate (e.g., 'five plus two')"
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show help and available operators"
    )
    parser.add_argument("-v", "--version", action="store_true", help="Show version information")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress expression in output")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    parser.add_argument(
        "-e",
        "--expression",
        dest="single_expr",
        help="Evaluate a single expression (useful for piping)",
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Start interactive REPL mode"
    )
    parser.add_argument(
        "-s",
        "--show",
        action="store_true",
        help="Show expression in output (default for interactive)",
    )

    args = parser.parse_args()

    if args.version:
        print(f"nl-calc {__version__}")
        return 0

    if args.help or (not args.expression and not args.single_expr and not args.interactive):
        print_help()
        return 0

    if args.interactive:
        return _run_repl(show_expression=args.show)

    if args.single_expr:
        expression = args.single_expr
        quiet_by_default = True
    else:
        expression = " ".join(args.expression)
        quiet_by_default = False

    # Detect shell glob expansion (e.g., "python nl_calc.py 30 * 3" expands "*" to files)
    if args.expression and len(args.expression) > 1:
        # Check if any argument is a file or directory that exists (likely from glob expansion)
        cwd = os.getcwd()
        glob_indicators = []
        for arg in args.expression:
            path = os.path.join(cwd, arg)
            if os.path.exists(path) and arg not in (".", ".."):
                glob_indicators.append(arg)

        if glob_indicators:
            print("Error: Possible shell glob expansion detected.", file=sys.stderr)
            print(
                f"The '*' character was expanded to file(s): {glob_indicators[:5]}{'...' if len(glob_indicators) > 5 else ''}",
                file=sys.stderr,
            )
            print("Please quote your expression:", file=sys.stderr)
            print(f'  calc "{" ".join(args.expression)}"', file=sys.stderr)
            print("Or use -e flag:", file=sys.stderr)
            print(f'  calc -e "{" ".join(args.expression)}"', file=sys.stderr)
            return 1

    output_format = "json" if args.json else "plain"
    if args.quiet:
        show_expression = False
    elif args.show:
        show_expression = True
    elif quiet_by_default:
        show_expression = False
    else:
        show_expression = False

    _, exit_code = run(expression, NORMALIZE, PATTERNS, output_format, show_expression)
    return exit_code



# === Entry point ===
if __name__ == "__main__":
    sys.exit(main())
