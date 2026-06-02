"""
Safe AST-based expression evaluator for eggcalc.

Provides a secure way to evaluate mathematical expressions without
using the unsafe eval() function. Supports arithmetic operations,
trigonometric functions, logarithms, constants, and unit conversions.
"""

from __future__ import annotations

import ast
import cmath
import math
import random
import threading
from collections import OrderedDict
from functools import lru_cache
from typing import Any

from .units import (
    UNIT_ALIASES,
    UNIT_CONVERSIONS,
    UnitValue,
    are_units_compatible,
    convert_temperature,
    get_unit_category,
    normalize_unit,
)

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
    "memory_store",
    "memory_recall",
    "memory_add",
    "memory_subtract",
    "memory_clear",
    "memory_list",
    "setvar",
    "getvar",
    "delvar",
    "listvars",
    "clearvars",
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
    """Load user-defined configuration from eggcalc_config.py (thread-safe)."""
    global _config_loaded
    try:
        import eggcalc.normalize as normalize_mod
        import eggcalc_config as config

        for name, value in getattr(config, "CUSTOM_CONSTANTS", {}).items():
            _default_evaluator.CONSTANTS[name] = value

        for name, func in getattr(config, "CUSTOM_FUNCTIONS", {}).items():
            _default_evaluator.FUNCTIONS[name] = func

        from . import units

        for base, unit_dict in getattr(config, "CUSTOM_UNITS", {}).items():
            if base in units.UNIT_BASE:
                units.UNIT_BASE[base].update(unit_dict)
            else:
                units.UNIT_BASE[base] = unit_dict

        for unit, canonical in getattr(config, "CUSTOM_ALIASES", {}).items():
            units.UNIT_ALIASES[unit] = canonical

        for key, (mult, offset) in getattr(config, "CUSTOM_TEMP_CONVERSIONS", {}).items():
            units.TEMPERATURE_CONVERSIONS[key] = (mult, offset)

        units._rebuild_conversions()

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
    from .normalize import NORMALIZE, PATTERNS, normalize_expression

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

    def _eval() -> float:
        return evaluate_raw(expression)

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _eval)


def load_user_config_extended() -> None:
    """Load user-defined configuration including normalize (call after normalize is loaded)."""
    try:
        import eggcalc.normalize as normalize_mod
        import eggcalc_config as config

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
    if isinstance(x, float):
        if not x.is_integer():
            raise EvaluationError("bin() requires integer input")
        x = int(x)
    return bin(x)


def _to_hex(x: int) -> str:
    """Convert integer to hexadecimal string."""
    if isinstance(x, float):
        if not x.is_integer():
            raise EvaluationError("hex() requires integer input")
        x = int(x)
    return hex(x)


def _to_oct(x: int) -> str:
    """Convert integer to octal string."""
    if isinstance(x, float):
        if not x.is_integer():
            raise EvaluationError("oct() requires integer input")
        x = int(x)
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


def _polar(z: complex) -> tuple[float, float]:
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
    """Return prime factorization as a formatted string.

    Returns a string of the form "2^2 × 3 × 5" where each prime factor
    is separated by " × ". Factors with exponent 1 appear as the prime
    itself (e.g. "3"), while factors with higher exponents include the
    exponent (e.g. "2^2"). For n < 2, returns the number as a string.
    """
    n = int(n)
    if n < 2:
        return str(n)

    factors: dict[int, int] = {}
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
    if abs(total) < 1e-100:
        raise EvaluationError("Near-zero divisor could cause overflow")
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

    def wrapper(x: float) -> complex | float:
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
_sinh = _complex_aware(math.sinh, cmath.sinh)
_cosh = _complex_aware(math.cosh, cmath.cosh)
_tanh = _complex_aware(math.tanh, cmath.tanh)
_asinh = _complex_aware(math.asinh, cmath.asinh)
_acosh = _complex_aware(math.acosh, cmath.acosh)
_atanh = _complex_aware(math.atanh, cmath.atanh)
_cbrt = _complex_aware(lambda x: x ** (1 / 3), lambda x: x ** (1 / 3), use_complex_for_negative=True)


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
        # Atomic/particle physics
        "me": 9.1093837015e-31,
        "electronmass": 9.1093837015e-31,
        "mp": 1.67262192369e-27,
        "protonmass": 1.67262192369e-27,
        "mn": 1.67493e-27,
        "neutronmass": 1.67493e-27,
        "re": 2.817952326e-15,
        "electronradius": 2.817952326e-15,
        "alpha": 7.2973525693e-3,
        "finestructure": 7.2973525693e-3,
        "wien": 2.897771955e-3,
        "wienconstant": 2.897771955e-3,
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
        # Hyperbolic (complex-aware)
        "sinh": _sinh,
        "cosh": _cosh,
        "tanh": _tanh,
        "asinh": _asinh,
        "acosh": _acosh,
        "atanh": _atanh,
        # Logarithmic (complex-aware)
        "log": _log,
        "ln": _log,
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
        "fact": _safe_factorial,
        "gcd": math.gcd,
        "lcm": _lcm,
        "perm": _perm,
        "comb": _comb,
        "nPr": _perm,
        "nCr": _comb,
        "cbrt": _cbrt,
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
        "vars": _variance_sample,
        "var_sample": _variance_sample,
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
        ast.BitOr: (lambda a, b: a | b),
        ast.BitXor: (lambda a, b: a ^ b),
        ast.BitAnd: (lambda a, b: a & b),
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

        # Get the name of the right operand if it's a Name node (for compound unit detection)
        right_name: str | None = None
        if isinstance(node.right, ast.Name):
            right_name = node.right.id

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

        is_bitwise = op_class in (ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift)
        if is_bitwise and (isinstance(left_val, float) or isinstance(right_val, float)):
            raise EvaluationError("Bitwise operations require integer operands, not floats")

        if op_class not in self.BINOPS:
            raise EvaluationError(f"Unsupported binary operator: '{node.op.__class__.__name__}'")

        result = self.BINOPS[op_class](left_val, right_val)

        # Compound unit detection for division:
        # 1. UnitValue / UnitValue with different units -> "left_unit/right_unit"
        # 2. UnitValue / number whose AST name is a unit -> "left_unit/name" (e.g., km/h, mi/h)
        if op_class is ast.Div and isinstance(left, UnitValue) and left.unit:
            if isinstance(right, UnitValue) and right.unit and left.unit != right.unit:
                compound = f"{left.unit}/{right.unit}"
                return UnitValue(left_val / right_val, compound)
            if not isinstance(right, UnitValue) and right_name and right_name in UNIT_ALIASES:
                unit_name = UNIT_ALIASES[right_name]
                compound = f"{left.unit}/{unit_name}"
                return UnitValue(left_val, compound)

        # Compound unit detection for multiplication:
        # UnitValue * UnitValue with different units -> "left_unit*right_unit"
        # UnitValue * number whose AST name is a unit -> "left_unit*name"
        if op_class is ast.Mult and isinstance(left, UnitValue) and left.unit:
            if isinstance(right, UnitValue) and right.unit and left.unit != right.unit:
                compound = f"{left.unit}*{right.unit}"
                return UnitValue(left_val * right_val, compound)
            if not isinstance(right, UnitValue) and right_name and right_name in UNIT_ALIASES:
                unit_name = UNIT_ALIASES[right_name]
                compound = f"{left.unit}*{unit_name}"
                return UnitValue(left_val * right_val, compound)

        if result_unit is None:
            return result
        return UnitValue(result, result_unit)

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        """Visit a unary operation node."""
        operand = self.visit(node.operand)
        op_class = type(node.op)

        if op_class not in self.UNARYOPS:
            raise EvaluationError(f"Unsupported unary operator: '{node.op.__class__.__name__}'")

        if op_class is ast.Invert and not isinstance(operand, int):
            raise EvaluationError("Bitwise NOT requires an integer operand")

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
            if node_type == ast.Compare:
                raise EvaluationError("Comparison operators are not supported")
            if node_type == ast.BoolOp:
                raise EvaluationError("Boolean operators are not supported")
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
    from .normalize import NORMALIZE, PATTERNS, normalize_expression

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

    Note:
        Expressions that exceed MAX_EXPONENT (10000) or MAX_FACTORIAL (1000)
        will fail with EvaluationError before the timeout is reached.

    Example:
        >>> result = evaluate_with_timeout("sum([i**2 for i in range(100)])", timeout=1.0)
        # May raise TimeoutError for slow expressions
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

        def _eval() -> float:
            return self.calculate(expression)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _eval)

    def _evaluate_internal(self, expression: str) -> Any:
        """Internal evaluation that uses the instance's evaluator."""
        from .normalize import NORMALIZE, PATTERNS, normalize_expression

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
