"""
User-defined configuration for nl-calc.

This file allows you to add custom units, constants, and functions.
Edit this file to extend nl-calc's functionality.

Example:
    # nl_calc_config.py
    CUSTOM_CONSTANTS = {
        "myconst": 42.0,
    }
    
    CUSTOM_FUNCTIONS = {
        "myfunc": lambda x: x * 2,
    }
"""

CUSTOM_CONSTANTS: dict[str, float] = {}

CUSTOM_FUNCTIONS: dict[str, callable] = {}

CUSTOM_UNITS: dict[str, dict[str, float]] = {}

CUSTOM_ALIASES: dict[str, str] = {}

CUSTOM_TEMP_CONVERSIONS: dict[tuple[str, str], tuple[float, float]] = {}

CUSTOM_NUMBER_WORDS: dict[str, list[str]] = {}

CUSTOM_OPERATOR_WORDS: dict[str, str] = {}
