"""
nl-calc - Natural language math expression calculator.

A calculator that accepts natural language expressions and converts them
to mathematical expressions that can be evaluated.

Usage:
    python -m nl_calc "five plus two"
    python -m nl_calc "30m + 100ft"
    python -m nl_calc --help
    python -m nl_calc -i  # Interactive REPL mode

Library usage:
    from nl_calc import evaluate, EvaluationError, UnitValue
    result = evaluate("5 + 3")

    # For webapps with caching:
    from nl_calc import PyCalcApp
    app = PyCalcApp(cache_size=1024)
    result = app.calculate("five plus two")

Note: load_user_config_extended() is not exported as custom number/operator
words via external config are not officially supported.
"""

from .evaluator import (
    EvaluationError,
    evaluate,
    evaluate_raw,
    evaluate_cached,
    evaluate_async,
    evaluate_with_timeout,
    load_user_config,
    get_default_evaluator,
    register_constant,
    register_function,
    PyCalcApp,
    TimeoutError,
    Memory,
    memory_store,
    memory_recall,
    memory_add,
    memory_subtract,
    memory_clear,
    memory_list,
    setvar,
    getvar,
    delvar,
    listvars,
    clearvars,
    MAX_EXPONENT,
    MAX_FACTORIAL,
    MAX_NESTING_DEPTH,
    MAX_RESULT_VALUE,
    DEFAULT_CACHE_SIZE,
)
from .normalize import main, run, normalize, normalize_expression, print_help, NORMALIZE, PATTERNS, MAX_INPUT_LENGTH, MAX_NESTING_DEPTH
from .units import UnitValue, normalize_unit, get_conversion_factor, get_all_units, is_unit, get_unit_category, are_units_compatible, FLOAT_EPSILON

__version__ = "1.1.0"
__author__ = "nl-calc Contributors"

__all__ = [
    # Core evaluation
    "evaluate",
    "evaluate_raw",
    "evaluate_cached",
    "evaluate_async",
    "evaluate_with_timeout",
    # Exceptions
    "EvaluationError", 
    "TimeoutError",
    # Types
    "UnitValue",
    "Memory",
    # CLI
    "main",
    "run",
    "normalize",
    "normalize_expression",
    "print_help",
    # Constants
    "NORMALIZE",
    "PATTERNS",
    "MAX_INPUT_LENGTH",
    "MAX_NESTING_DEPTH",
    "MAX_EXPONENT",
    "MAX_FACTORIAL",
    "MAX_RESULT_VALUE",
    "DEFAULT_CACHE_SIZE",
    # Unit utilities
    "normalize_unit",
    "get_conversion_factor",
    "get_all_units",
    "is_unit",
    "get_unit_category",
    "are_units_compatible",
    "FLOAT_EPSILON",
    # Configuration
    "load_user_config",
    "get_default_evaluator",
    "register_constant",
    "register_function",
    # Webapp
    "PyCalcApp",
    # Memory functions
    "memory_store",
    "memory_recall",
    "memory_add",
    "memory_subtract",
    "memory_clear",
    "memory_list",
    # Variable functions
    "setvar",
    "getvar",
    "delvar",
    "listvars",
    "clearvars",
]

load_user_config()
