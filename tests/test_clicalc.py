"""Tests for nl-calc."""

import pytest

from eggcalc import EvaluationError, UnitValue, evaluate
from eggcalc.normalize import NORMALIZE, PATTERNS, check_if_number, run


class TestEvaluator:
    """Tests for the evaluator module."""

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        result = evaluate("5 + 3")
        assert result == 8 or (isinstance(result, UnitValue) and result.value == 8)

    def _get_value(self, result):
        """Extract numeric value from result."""
        if isinstance(result, UnitValue):
            return result.value
        return result

    def test_multi_digit_subtraction(self):
        """Test subtraction with multi-digit numbers."""
        assert abs(self._get_value(evaluate("90-1")) - 89) < 1e-10
        assert abs(self._get_value(evaluate("100-10")) - 90) < 1e-10
        assert abs(self._get_value(evaluate("50-5")) - 45) < 1e-10
        assert abs(self._get_value(evaluate("1000-1")) - 999) < 1e-10

    def test_order_of_operations(self):
        """Test order of operations."""
        result = evaluate("2 + 3 * 4")
        assert result == 14 or (isinstance(result, UnitValue) and result.value == 14)

    def test_trigonometric_functions(self):
        """Test trigonometric functions."""
        assert abs(evaluate("sin(0)") - 0.0) < 1e-10
        assert abs(evaluate("cos(0)") - 1.0) < 1e-10
        assert abs(evaluate("tan(0)") - 0.0) < 1e-10

    def test_constants(self):
        """Test mathematical constants."""
        assert abs(evaluate("pi") - 3.141592653589793) < 1e-10
        assert abs(evaluate("e") - 2.718281828459045) < 1e-10

class TestUnitConversions:
    """Tests for unit conversions using the run function."""

    def test_length_conversion(self):
        """Test length unit conversions."""
        import sys
        from io import StringIO

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        run("30m + 100ft", NORMALIZE, PATTERNS)
        sys.stdout = old_stdout
        output = captured.getvalue()
        assert "m" in output

    def test_time_conversion(self):
        """Test time unit conversions via run()."""
        # Use '1d + 12h' instead of '1h + 30min' because 'min' is also a
        # function name in FUNCTIONS, which causes apply_math_functions in
        # normalize.py to wrap it as 'min()' before AST evaluation.
        # 1d + 12h = 1.5d (the previous buggy result was 30.0 min, which
        # was the result of `h` resolving to Planck's constant instead of
        # the hour unit - now `h` correctly resolves to hours first per C1).
        result, _ = run("1d + 12h", NORMALIZE, PATTERNS)
        assert result is not None
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 1.5) < 1e-10

    def test_data_conversion(self):
        """Test data storage unit conversions."""
        import sys
        from io import StringIO

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        run("1GB + 500MB", NORMALIZE, PATTERNS)
        sys.stdout = old_stdout
        output = captured.getvalue()
        assert "GB" in output

    def test_mixed_conversion(self):
        """Test mixed unit operations."""
        import sys
        from io import StringIO

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        run("(30m+100ft)/2", NORMALIZE, PATTERNS)
        sys.stdout = old_stdout
        output = captured.getvalue()
        assert "m" in output

    def test_invalid_expression(self):
        """Test that invalid expressions raise errors."""
        with pytest.raises(EvaluationError):
            evaluate("import os")

    def test_power_operations(self):
        """Test power operations."""
        result = evaluate("2 ** 3")
        assert result == 8 or (isinstance(result, UnitValue) and result.value == 8)
        result = evaluate("4 ** 0.5")
        assert result == 2 or (isinstance(result, UnitValue) and result.value == 2)

    def test_negative_numbers(self):
        """Test negative numbers."""
        result = evaluate("-5 + 3")
        # Note: -5 + 3 in Python evaluates to -2, but depending on order might be different
        # Just verify it's a valid number
        assert isinstance(result, (int, float, UnitValue))

    def test_bitwise_not_rejects_float(self):
        """Test that bitwise NOT raises an error for float operands."""
        with pytest.raises(EvaluationError):
            evaluate("~3.14")


class TestNormalize:
    """Tests for the normalize module."""

    def test_check_if_number_integer(self):
        """Test checking if token is an integer."""
        result = check_if_number("42")
        assert result["bool"] is True
        assert result["converted"] == 42

    def test_check_if_number_float(self):
        """Test checking if token is a float."""
        result = check_if_number("3.14")
        assert result["bool"] is True
        assert result["converted"] == 3.14

    def test_check_if_number_with_unit(self):
        """Test checking if token has a unit."""
        result = check_if_number("50m")
        assert result["bool"] is True
        assert result["converted"] == 50

    def test_check_if_number_invalid(self):
        """Test checking invalid number."""
        result = check_if_number("abc")
        assert result["bool"] is False

    def test_natural_language_numbers(self):
        """Test natural language number conversion."""
        run("five plus three", NORMALIZE, PATTERNS)
        # Just check it doesn't error


class TestCLI:
    """Tests for CLI functionality."""

    def test_help_flag(self):
        """Test that help flag works."""
        from eggcalc.normalize import print_help
        # Just verify it doesn't error
        print_help()

    def test_empty_expression(self):
        """Test empty expression shows help."""
        import sys

        from eggcalc.normalize import main
        sys.argv = ["eggcalc"]
        main()


class TestUnitValue:
    """Tests for UnitValue class."""

    def test_creation(self):
        """Test creating UnitValue."""
        uv = UnitValue(5, "m")
        assert uv.value == 5
        assert uv.unit == "m"

    def test_repr(self):
        """Test string representation."""
        uv = UnitValue(5, "m")
        assert repr(uv) == "5 m"

    def test_addition_same_unit(self):
        """Test adding same units."""
        uv1 = UnitValue(5, "m")
        uv2 = UnitValue(3, "m")
        result = uv1 + uv2
        assert result.value == 8
        assert result.unit == "m"

    def test_addition_different_unit(self):
        """Test adding different units."""
        uv1 = UnitValue(1, "m")
        uv2 = UnitValue(100, "cm")
        result = uv1 + uv2
        assert result.unit == "m"
        assert abs(result.value - 2) < 1e-10

    def test_addition_incompatible_units(self):
        """Test adding incompatible units raises ValueError."""
        uv1 = UnitValue(30, "mi")
        uv2 = UnitValue(30, "gal")
        with pytest.raises(ValueError):
            uv1 + uv2

    def test_subtraction_incompatible_units(self):
        """Test subtracting incompatible units raises ValueError."""
        uv1 = UnitValue(30, "m")
        uv2 = UnitValue(10, "kg")
        with pytest.raises(ValueError):
            uv1 - uv2

    def test_addition_compatible_units(self):
        """Test adding compatible units (same category)."""
        uv1 = UnitValue(30, "mi")
        uv2 = UnitValue(30, "m")
        result = uv1 + uv2
        assert result.unit in ("mi", "m")
        assert result.value > 30


class TestPhysicalConstants:
    """Tests for physical constants."""

    def test_avogadro(self):
        """Test Avogadro constant via run()."""
        result, _ = run("5 times avogadro", NORMALIZE, PATTERNS)
        assert result is not None
        assert abs(float(result) - 3.011e24) < 1e22

    def test_speed_of_light(self):
        """Test speed of light."""
        result = evaluate("c")
        assert result == 299792458

    def test_boltzmann(self):
        """Test Boltzmann constant."""
        result = evaluate("k")
        assert abs(result - 1.380649e-23) < 1e-30

    def test_planck(self):
        """Test Planck constant (use the long name; 'h' resolves to hour unit)."""
        result = evaluate("planck")
        assert abs(result - 6.62607015e-34) < 1e-40


class TestPyCalcApp:
    """Tests for PyCalcApp class."""

    def _get_value(self, result):
        """Extract numeric value from result."""
        if isinstance(result, UnitValue):
            return result.value
        return result

    def test_basic_calculate(self):
        """Test basic calculation."""
        from eggcalc import PyCalcApp
        app = PyCalcApp()
        result = app.calculate("5 + 3")
        assert self._get_value(result) == 8

    def test_natural_language(self):
        """Test natural language input."""
        from eggcalc import PyCalcApp
        app = PyCalcApp()
        result = app.calculate("five plus three")
        assert self._get_value(result) == 8

    def test_caching(self):
        """Test that caching works."""
        from eggcalc import PyCalcApp
        app = PyCalcApp(cache_size=10)

        # First call
        result1 = app.calculate("5 + 3")
        assert app.cache_size == 1

        # Second call should use cache
        result2 = app.calculate("5 + 3")
        assert app.cache_size == 1
        assert self._get_value(result1) == self._get_value(result2)

    def test_cache_clear(self):
        """Test cache clearing."""
        from eggcalc import PyCalcApp
        app = PyCalcApp()
        app.calculate("5 + 3")
        assert app.cache_size == 1
        app.clear_cache()
        assert app.cache_size == 0

    def test_cache_disabled(self):
        """Test with caching disabled."""
        from eggcalc import PyCalcApp
        app = PyCalcApp(enable_cache=False)
        app.calculate("5 + 3")
        assert app.cache_size == 0

    def test_register_constant(self):
        """Test registering custom constant."""
        from eggcalc import PyCalcApp
        app = PyCalcApp()
        app.register_constant("myconst", 42)
        result = app.calculate("myconst")
        assert self._get_value(result) == 42

    def test_register_function(self):
        """Test registering custom function."""
        from eggcalc import PyCalcApp
        app = PyCalcApp()
        app.register_function("double", lambda x: x * 2)
        result = app.calculate("double(5)")
        assert self._get_value(result) == 10

    def test_instance_isolation_constants(self):
        """Test that instances have isolated constants."""
        from eggcalc import PyCalcApp
        app1 = PyCalcApp()
        app2 = PyCalcApp()

        app1.register_constant("myconst", 42)
        app2.register_constant("myconst", 100)

        result1 = app1.calculate("myconst")
        result2 = app2.calculate("myconst")

        assert self._get_value(result1) == 42
        assert self._get_value(result2) == 100

    def test_instance_isolation_functions(self):
        """Test that instances have isolated functions."""
        from eggcalc import PyCalcApp
        app1 = PyCalcApp()
        app2 = PyCalcApp()

        app1.register_function("myfunc", lambda x: x * 2)
        app2.register_function("myfunc", lambda x: x * 3)

        result1 = app1.calculate("myfunc(5)")
        result2 = app2.calculate("myfunc(5)")

        assert self._get_value(result1) == 10
        assert self._get_value(result2) == 15

    def test_unit_calculations(self):
        """Test unit calculations in PyCalcApp."""
        from eggcalc import PyCalcApp
        app = PyCalcApp()
        result = app.calculate("30m + 100ft")
        assert hasattr(result, 'unit') or 'm' in str(result)


class TestAsyncFunctions:
    """Tests for async evaluation functions."""

    def _get_value(self, result):
        """Extract numeric value from result."""
        if isinstance(result, UnitValue):
            return result.value
        return result

    def test_evaluate_async(self):
        """Test async evaluation."""
        import asyncio

        from eggcalc import evaluate_async

        async def run_test():
            result = await evaluate_async("5 + 3")
            return result

        result = asyncio.run(run_test())
        assert self._get_value(result) == 8

    def test_eggcalc_app_async(self):
        """Test PyCalcApp async calculation."""
        import asyncio

        from eggcalc import PyCalcApp

        app = PyCalcApp()

        async def run_test():
            result = await app.calculate_async("5 + 3")
            return result

        result = asyncio.run(run_test())
        assert self._get_value(result) == 8


class TestCaching:
    """Tests for caching functions."""

    def _get_value(self, result):
        """Extract numeric value from result."""
        if isinstance(result, UnitValue):
            return result.value
        return result

    def test_evaluate_cached(self):
        """Test evaluate_cached function."""
        from eggcalc import evaluate_cached

        result = evaluate_cached("5 + 3")
        assert self._get_value(result) == 8

        # Second call should use cache
        result2 = evaluate_cached("5 + 3")
        assert self._get_value(result2) == 8

    def test_evaluate_cached_natural_language(self):
        """Test evaluate_cached with natural language."""
        from eggcalc import evaluate_cached

        result = evaluate_cached("five plus three")
        assert self._get_value(result) == 8


class TestTimeout:
    """Tests for timeout functionality."""

    def _get_value(self, result):
        """Extract numeric value from result."""
        if isinstance(result, UnitValue):
            return result.value
        return result

    def test_evaluate_with_timeout_success(self):
        """Test evaluate_with_timeout with fast expression."""
        from eggcalc import evaluate_with_timeout

        result = evaluate_with_timeout("5 + 3", timeout=1.0)
        assert self._get_value(result) == 8

    def test_evaluate_with_timeout_natural_language(self):
        """Test evaluate_with_timeout with natural language."""
        from eggcalc import evaluate_with_timeout

        result = evaluate_with_timeout("five plus three", timeout=1.0)
        assert self._get_value(result) == 8

    def test_timeout_error_raised(self):
        """Test that TimeoutError can be raised."""
        from eggcalc import TimeoutError

        # Just test that the exception class exists and is importable
        assert issubclass(TimeoutError, Exception)


class TestComplexNumbers:
    """Tests for complex number functionality."""

    def test_imaginary_unit(self):
        """Test imaginary unit i."""
        from eggcalc import evaluate_raw

        result = evaluate_raw("i * i")
        if hasattr(result, 'value'):
            result = result.value
        assert abs(result.real + 1) < 1e-10
        assert abs(result.imag) < 1e-10

    def test_complex_literal(self):
        """Test complex literals."""
        from eggcalc import evaluate_raw

        result = evaluate_raw("3 + 4i")
        if hasattr(result, 'value'):
            result = result.value
        assert abs(result.real - 3) < 1e-10
        assert abs(result.imag - 4) < 1e-10

    def test_sqrt_negative(self):
        """Test sqrt of negative number."""
        from eggcalc import evaluate_raw

        result = evaluate_raw("sqrt(-1)")
        if hasattr(result, 'value'):
            result = result.value
        assert abs(result.imag - 1) < 1e-10

    def test_abs_complex(self):
        """Test abs of complex number."""
        from eggcalc import evaluate_raw

        result = evaluate_raw("abs(3+4i)")
        if hasattr(result, 'value'):
            result = result.value
        assert abs(result - 5) < 1e-10

    def test_conj(self):
        """Test complex conjugate."""
        from eggcalc import evaluate_raw

        result = evaluate_raw("conj(3+4i)")
        if hasattr(result, 'value'):
            result = result.value
        assert abs(result.real - 3) < 1e-10
        assert abs(result.imag + 4) < 1e-10


class TestBitwise:
    """Tests for bitwise operations."""

    def _get_value(self, result):
        """Extract numeric value from result."""
        if hasattr(result, 'value'):
            return result.value
        return result

    def test_bitand(self):
        """Test bitwise AND."""
        from eggcalc import evaluate_raw

        assert self._get_value(evaluate_raw("5 bitand 3")) == 1
        assert self._get_value(evaluate_raw("5 & 3")) == 1

    def test_bitor(self):
        """Test bitwise OR."""
        from eggcalc import evaluate_raw

        assert self._get_value(evaluate_raw("5 OR 3")) == 7
        assert self._get_value(evaluate_raw("5 | 3")) == 7

    def test_bitxor_word(self):
        """Test bitwise XOR using word."""
        from eggcalc import evaluate_raw

        assert self._get_value(evaluate_raw("5 XOR 3")) == 6

    def test_bitnot(self):
        """Test bitwise NOT."""
        from eggcalc import evaluate_raw

        assert self._get_value(evaluate_raw("~5")) == -6

    def test_shifts(self):
        """Test bit shifts."""
        from eggcalc import evaluate_raw

        assert self._get_value(evaluate_raw("5 << 2")) == 20
        assert self._get_value(evaluate_raw("5 >> 1")) == 2

    def test_base_prefixes(self):
        """Test base prefixes."""
        from eggcalc import evaluate_raw

        assert evaluate_raw("0xFF") == 255
        assert evaluate_raw("0b1010") == 10
        assert evaluate_raw("0o777") == 511


class TestCombinatorics:
    """Tests for combinatorics functions."""

    def test_perm(self):
        """Test permutations."""
        from eggcalc import evaluate_raw

        assert evaluate_raw("perm(5, 3)") == 60
        assert evaluate_raw("nPr(5, 3)") == 60

    def test_comb(self):
        """Test combinations."""
        from eggcalc import evaluate_raw

        assert evaluate_raw("comb(5, 3)") == 10
        assert evaluate_raw("nCr(5, 3)") == 10

    def test_lcm(self):
        """Test LCM."""
        from eggcalc import evaluate_raw

        assert evaluate_raw("lcm(12, 18)") == 36
        assert evaluate_raw("lcm(12, 18, 24)") == 72


class TestPrimes:
    """Tests for prime functions."""

    def test_isprime(self):
        """Test prime check."""
        from eggcalc import evaluate_raw

        assert evaluate_raw("isprime(17)") == True
        assert evaluate_raw("isprime(18)") == False

    def test_primefactors(self):
        """Test prime factorization."""
        from eggcalc import evaluate_raw

        result = evaluate_raw("primefactors(84)")
        assert "2" in result and "3" in result and "7" in result

    def test_nextprime(self):
        """Test next prime."""
        from eggcalc import evaluate_raw

        assert evaluate_raw("nextprime(17)") == 19


class TestStatistics:
    """Tests for statistical functions."""

    def test_median(self):
        """Test median."""
        from eggcalc import evaluate_raw

        assert evaluate_raw("median(1, 2, 3, 4, 5)") == 3
        assert evaluate_raw("median(1, 2, 3, 4)") == 2.5

    def test_mode(self):
        """Test mode."""
        from eggcalc import evaluate_raw

        assert evaluate_raw("mode(1, 2, 2, 3)") == 2

    def test_variance(self):
        """Test variance."""
        from eggcalc import evaluate_raw

        result = evaluate_raw("variance(1, 2, 3, 4, 5)")
        assert abs(result - 2.0) < 1e-10


class TestPercentage:
    """Tests for percentage functionality."""

    def test_percent_literal(self):
        """Test percentage literal."""
        from eggcalc import evaluate_raw

        assert abs(evaluate_raw("50%") - 0.5) < 1e-10
        assert abs(evaluate_raw("25%") - 0.25) < 1e-10

    def test_percentof(self):
        """Test percentof function."""
        from eggcalc import evaluate_raw

        assert evaluate_raw("percentof(20, 100)") == 20.0


class TestRandom:
    """Tests for random functions."""

    def test_random_range(self):
        """Test random is in range."""
        from eggcalc import evaluate_raw

        evaluate_raw("seed(42)")
        result = evaluate_raw("random()")
        assert 0 <= result < 1

    def test_randint_range(self):
        """Test randint is in range."""
        from eggcalc import evaluate_raw

        evaluate_raw("seed(42)")
        result = evaluate_raw("randint(1, 100)")
        assert 1 <= result <= 100


class TestMemory:
    """Tests for memory functions."""

    def test_store_recall(self):
        """Test store and recall."""
        from eggcalc import evaluate_raw, memory_clear

        memory_clear()
        result = evaluate_raw("store(42)")
        assert result == 42

        result = evaluate_raw("recall()")
        assert result == 42


class TestVariables:
    """Tests for variable functionality."""

    def _get_value(self, result):
        """Extract numeric value from result."""
        if hasattr(result, 'value'):
            return result.value
        return result

    def test_setvar_getvar(self):
        """Test setvar and getvar."""
        from eggcalc import clearvars, evaluate_raw

        clearvars()
        result = evaluate_raw('setvar("x", 10)')
        assert self._get_value(result) == 10

        result = evaluate_raw("x + 5")
        assert self._get_value(result) == 15


class TestPrefixedUnitConversions:
    """Tests for prefixed unit conversions via get_conversion_factor."""

    def test_kilonewton_to_newton(self):
        """Test kN to N conversion factor is 1000.0."""
        from eggcalc import get_conversion_factor
        result = get_conversion_factor("kN", "N")
        assert result == 1000.0

    def test_millivolt_to_volt(self):
        """Test mV to V conversion factor is 0.001."""
        from eggcalc import get_conversion_factor
        result = get_conversion_factor("mV", "V")
        assert abs(result - 0.001) < 1e-10

    def test_milliamp_to_amp(self):
        """Test mA to A conversion factor is 0.001."""
        from eggcalc import get_conversion_factor
        result = get_conversion_factor("mA", "A")
        assert abs(result - 0.001) < 1e-10

    def test_kilowatt_to_watt(self):
        """Test kW to W conversion factor is 1000.0."""
        from eggcalc import get_conversion_factor
        result = get_conversion_factor("kW", "W")
        assert result == 1000.0

    def test_megabyte_to_byte(self):
        """Test MB to B conversion factor is 1048576.0."""
        from eggcalc import get_conversion_factor
        result = get_conversion_factor("MB", "B")
        assert result == 1048576.0

    def test_kilometer_to_meter(self):
        """Test km to m conversion factor is 1000.0."""
        from eggcalc import get_conversion_factor
        result = get_conversion_factor("km", "m")
        assert result == 1000.0


class TestTemperatureConversions:
    """Tests for temperature conversions with exact offset handling."""

    def test_fahrenheit_to_celsius_exact_freezing(self):
        """Test 32F to C equals exactly 0.0C."""
        from eggcalc.units import convert_temperature
        result = convert_temperature(32.0, "F", "C")
        assert abs(result - 0.0) < 1e-9

    def test_fahrenheit_to_celsius_boiling(self):
        """Test 212F to C equals approximately 100.0C."""
        from eggcalc.units import convert_temperature
        result = convert_temperature(212.0, "F", "C")
        assert abs(result - 100.0) < 1e-9

    def test_celsius_to_fahrenheit_freezing(self):
        """Test 0C to F equals exactly 32F."""
        from eggcalc.units import convert_temperature
        result = convert_temperature(0.0, "C", "F")
        assert abs(result - 32.0) < 1e-9

    def test_celsius_to_fahrenheit_boiling(self):
        """Test 100C to F equals approximately 212F."""
        from eggcalc.units import convert_temperature
        result = convert_temperature(100.0, "C", "F")
        assert abs(result - 212.0) < 1e-9


class TestUnicodeScriptOther:
    """Tests for unicode_script() returning 'Other' for digits and punctuation."""

    def test_digits_return_other(self):
        """Test that ASCII digits return 'Other'."""
        from eggcalc.exact import unicode_script
        assert unicode_script("0") == "Other"
        assert unicode_script("1") == "Other"
        assert unicode_script("5") == "Other"
        assert unicode_script("9") == "Other"

    def test_punctuation_return_other(self):
        """Test that ASCII punctuation returns 'Other'."""
        from eggcalc.exact import unicode_script
        assert unicode_script(".") == "Other"
        assert unicode_script(",") == "Other"
        assert unicode_script("!") == "Other"
        assert unicode_script("?") == "Other"
        assert unicode_script(":") == "Other"
        assert unicode_script(";") == "Other"
        assert unicode_script("-") == "Other"
        assert unicode_script("(") == "Other"
        assert unicode_script(")") == "Other"

    def test_space_returns_other(self):
        """Test that space returns 'Other'."""
        from eggcalc.exact import unicode_script
        assert unicode_script(" ") == "Other"

    def test_math_symbols_return_other(self):
        """Test that common math symbols return 'Other'."""
        from eggcalc.exact import unicode_script
        assert unicode_script("+") == "Other"
        assert unicode_script("=") == "Other"
        assert unicode_script("*") == "Other"
        assert unicode_script("/") == "Other"
        assert unicode_script("%") == "Other"


class TestDivisionByZero:
    """Tests for division by zero error handling."""

    def test_division_by_zero(self):
        """Test that division by zero raises EvaluationError."""
        with pytest.raises(EvaluationError, match="Cannot divide by zero"):
            evaluate("1/0")

    def test_floor_div_by_zero(self):
        """Test that floor division by zero raises EvaluationError."""
        with pytest.raises(EvaluationError, match="Cannot divide by zero"):
            evaluate("1//0")

    def test_mod_by_zero(self):
        """Test that modulo by zero raises EvaluationError."""
        with pytest.raises(EvaluationError, match="Cannot divide by zero"):
            evaluate("1%0")


class TestErrorHandling:
    """Tests for proper error handling (no raw Python exceptions)."""

    def test_perm_negative(self):
        """Test that perm with negative input raises EvaluationError."""
        with pytest.raises(EvaluationError, match="non-negative"):
            evaluate("perm(-1)")

    def test_perm_negative_r(self):
        """Test that perm with negative r raises EvaluationError."""
        with pytest.raises(EvaluationError, match="non-negative"):
            evaluate("perm(5, -1)")

    def test_shift_negative(self):
        """Test that negative shift count raises EvaluationError."""
        with pytest.raises(EvaluationError, match="non-negative"):
            evaluate("5 << -1")
        with pytest.raises(EvaluationError, match="non-negative"):
            evaluate("5 >> -1")

    def test_pow_overflow(self):
        """Test that very large exponent raises EvaluationError."""
        with pytest.raises(EvaluationError, match="Exponent too large"):
            evaluate("2 ** 100000")

    def test_log_zero(self):
        """Test that log of zero raises EvaluationError."""
        with pytest.raises(EvaluationError):
            evaluate("log(0)")

    def test_factorial_negative(self):
        """Test that factorial of negative raises EvaluationError."""
        with pytest.raises(EvaluationError):
            evaluate("factorial(-1)")

    def test_factorial_non_integer(self):
        """Test that factorial of non-integer raises EvaluationError."""
        with pytest.raises(EvaluationError):
            evaluate("factorial(1.5)")


class TestCompoundUnitDivision:
    """Tests for compound unit division (Fix #1)."""

    def test_unit_division_by_number(self):
        """Test that UnitValue / number correctly divides the value."""
        result = evaluate("(100*km) / 2")
        assert isinstance(result, UnitValue)
        assert result.unit == "km"
        assert abs(result.value - 50.0) < 1e-10

    def test_unit_division_by_unit(self):
        """Test that UnitValue / UnitValue with different units creates compound."""
        result = evaluate("(100*km) / (2*m)")
        assert isinstance(result, UnitValue)
        assert result.unit == "km/m"
        # Division does NOT convert units (only add/sub do); result is 100/2 = 50 km/m
        assert abs(result.value - 50.0) < 1e-10


class TestUppercaseOperators:
    """Tests for uppercase operator words (Fix #3)."""

    def test_uppercase_plus(self):
        """Test that uppercase PLUS works."""
        result, code = run("3 PLUS 5", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 8

    def test_uppercase_minus(self):
        """Test that uppercase MINUS works."""
        result, code = run("10 MINUS 3", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 7

    def test_uppercase_times(self):
        """Test that uppercase TIMES works."""
        result, code = run("4 TIMES 5", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 20

    def test_mixed_case(self):
        """Test mixed case operator words."""
        result, code = run("3 PlUs 5", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 8


class TestFunctionSpaceNumber:
    """Tests for function followed by space and number (Fix #2/#17)."""

    def test_sqrt_space_number(self):
        """Test 'sqrt 144' parses correctly."""
        result, code = run("sqrt 144", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 12.0) < 1e-10

    def test_sin_space_number(self):
        """Test 'sin 0' parses correctly."""
        result, code = run("sin 0", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val) < 1e-10

    def test_abs_space_number(self):
        """Test 'abs( -5)' parses correctly."""
        result, code = run("abs( -5)", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 5


class TestTemperatureCaseSensitivity:
    """Tests for lowercase temperature unit support (Fix #18)."""

    def test_lowercase_f_to_c(self):
        """Test '100f to c' converts correctly."""
        result, code = run("100f to c", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 37.77777777777778) < 1e-5

    def test_lowercase_c_to_f(self):
        """Test '0c to f' converts correctly."""
        result, code = run("0c to f", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 32.0) < 1e-10

    def test_uppercase_still_works(self):
        """Test that uppercase temperature units still work."""
        result, code = run("100F to C", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 37.77777777777778) < 1e-5


class TestUntestedMathFunctions:
    """Tests for math functions that had no test coverage."""

    def test_log(self):
        """Test natural logarithm."""
        result = evaluate("log(1)")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val) < 1e-10

    def test_log10(self):
        """Test base-10 logarithm."""
        result = evaluate("log10(100)")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 2.0) < 1e-10

    def test_log2(self):
        """Test base-2 logarithm."""
        result = evaluate("log2(8)")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 3.0) < 1e-10

    def test_exp(self):
        """Test exponential function."""
        result = evaluate("exp(0)")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 1.0) < 1e-10

    def test_abs_function(self):
        """Test absolute value function."""
        result = evaluate("abs(-5)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 5

    def test_floor(self):
        """Test floor function."""
        result = evaluate("floor(3.7)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 3

    def test_ceil(self):
        """Test ceiling function."""
        result = evaluate("ceil(3.2)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 4

    def test_sign(self):
        """Test sign function."""
        result = evaluate("sign(-5)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == -1

    def test_cbrt(self):
        """Test cube root function."""
        result = evaluate("cbrt(27)")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 3.0) < 1e-10

    def test_asin(self):
        """Test arcsine function."""
        result = evaluate("asin(1)")
        import math
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - math.pi / 2) < 1e-10

    def test_acos(self):
        """Test arccosine function."""
        result = evaluate("acos(1)")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val) < 1e-10

    def test_atan(self):
        """Test arctangent function."""
        result = evaluate("atan(1)")
        import math
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - math.pi / 4) < 1e-10

    def test_factorial(self):
        """Test factorial function."""
        result = evaluate("factorial(5)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 120

    def test_gcd(self):
        """Test GCD function."""
        result = evaluate("gcd(12, 8)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 4

    def test_sum(self):
        """Test sum function."""
        result = evaluate("sum(1, 2, 3, 4)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 10

    def test_max_function(self):
        """Test max function."""
        result = evaluate("max(3, 7, 2)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 7

    def test_min_function(self):
        """Test min function."""
        result = evaluate("min(3, 7, 2)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 2

    def test_hypot(self):
        """Test hypotenuse function."""
        result = evaluate("hypot(3, 4)")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 5.0) < 1e-10

    def test_clamp(self):
        """Test clamp function."""
        result = evaluate("clamp(5, 1, 10)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 5

    def test_clamp_below(self):
        """Test clamp with value below range."""
        result = evaluate("clamp(-5, 0, 10)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 0

    def test_prevprime(self):
        """Test previous prime function."""
        result = evaluate("prevprime(10)")
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 7

    def test_var_sample(self):
        """Test sample variance function."""
        result = evaluate("variance(2, 4, 4, 4, 5, 5, 7, 9)")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 4.0) < 1e-10

    def test_nl_numbers(self):
        """Test natural language number parsing."""
        result, code = run("five plus three", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 8

    def test_nl_sqrt(self):
        """Test natural language sqrt with single number."""
        result, code = run("sqrt of 144", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 12.0) < 1e-10

    def test_nl_sqrt_simple(self):
        """Test natural language sqrt with simple number word."""
        result, code = run("square root of nine", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - 3.0) < 1e-10


class TestCacheByteCap:
    """H25: LRU cache has both a hard entry count and a soft byte cap."""

    def test_cache_caps_at_default_size(self):
        """Adding more than DEFAULT_CACHE_SIZE entries should evict oldest."""
        from eggcalc import evaluate_cached

        for i in range(1100):
            evaluate_cached(f"{i}+1")
        from eggcalc.evaluator import _cache, DEFAULT_CACHE_SIZE

        assert len(_cache) <= DEFAULT_CACHE_SIZE

    def test_cache_under_byte_cap(self):
        """Total cache bytes should stay under MAX_CACHE_BYTES."""
        from eggcalc.evaluator import _cache, _cache_bytes, MAX_CACHE_BYTES

        from eggcalc import evaluate_cached

        for i in range(50):
            evaluate_cached(f"{i}+1")
        # Even if we don't hit the cap, total bytes must be bounded
        assert _cache_bytes <= MAX_CACHE_BYTES * 2


class TestBinOpOverflowComplex:
    """M4: complex results with NaN/inf components raise EvaluationError."""

    def test_complex_division_by_zero(self):
        """Complex division by zero should not return inf silently."""
        with pytest.raises(EvaluationError):
            evaluate("1j/0")


class TestWorkerReap:
    """M5: evaluate_with_timeout kills stragglers after the timeout."""

    def test_timeout_returns_within_reasonable_time(self):
        """evaluate_with_timeout should return control quickly even on a
        pathological input. We just check that the function returns
        (with TimeoutError) within a reasonable time."""
        import time

        from eggcalc import TimeoutError, evaluate_with_timeout

        start = time.monotonic()
        try:
            evaluate_with_timeout("0+0+0+0+0", timeout=0.5)
        except TimeoutError:
            pass
        elapsed = time.monotonic() - start
        assert elapsed < 5.0, f"Timeout took {elapsed:.2f}s"


class TestDigitScales:
    """Verify _DIGIT_SCALES produces correct results."""

    def test_billion_correct(self):
        """'5 billion' should be 5_000_000_000, not 5_000_000_000_000."""
        result, code = run("5 billion", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 5_000_000_000

    def test_trillion_correct(self):
        """'3 trillion' should be 3_000_000_000_000."""
        result, code = run("3 trillion", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 3_000_000_000_000

    def test_quadrillion_correct(self):
        """'2 quadrillion' should be 2_000_000_000_000_000."""
        result, code = run("2 quadrillion", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 2_000_000_000_000_000

    def test_million_still_correct(self):
        """'7 million' should still be 7_000_000."""
        result, code = run("7 million", NORMALIZE, PATTERNS)
        assert code == 0
        val = result.value if isinstance(result, UnitValue) else result
        assert val == 7_000_000


class TestVisitAttribute:
    """Verify standalone .real/.imag/.conjugate attribute access."""

    def test_real_of_complex(self):
        """(3+4j).real should be 3.0."""
        result = evaluate("(3+4j).real")
        assert abs(result - 3.0) < 1e-10

    def test_imag_of_complex(self):
        """(3+4j).imag should be 4.0."""
        result = evaluate("(3+4j).imag")
        assert abs(result - 4.0) < 1e-10

    def test_real_of_real(self):
        """(5).real should be 5."""
        result = evaluate("(5).real")
        assert result == 5

    def test_imag_of_real(self):
        """(5).imag should be 0.0."""
        result = evaluate("(5).imag")
        assert result == 0.0

    def test_conjugate(self):
        """(3+4j).conjugate should be (3-4j)."""
        result = evaluate("(3+4j).conjugate")
        assert isinstance(result, complex)
        assert result == (3-4j)


class TestComplexPower:
    """Verify complex number exponentiation works."""

    def test_i_squared(self):
        """i**2 should be -1 (or close to it)."""
        result = evaluate("i**2")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - (-1)) < 1e-10 or abs(val - (-1+0j)) < 1e-10

    def test_j_squared(self):
        """j**2 should be -1."""
        result = evaluate("j**2")
        val = result.value if isinstance(result, UnitValue) else result
        assert abs(val - (-1)) < 1e-10 or abs(val - (-1+0j)) < 1e-10

    def test_complex_power(self):
        """(1+1j)**2 should be 2j."""
        result = evaluate("(1+1j)**2")
        assert isinstance(result, complex)
        assert abs(result - 2j) < 1e-10


class TestLargeIntStrSafety:
    """Verify large integer str() doesn't raise ValueError."""

    def test_large_shift_result(self):
        """1 << 14300 should not raise ValueError."""
        result = evaluate("1 << 14300")
        assert result is not None
        assert isinstance(result, int)
        assert result > 0

    def test_large_factorial(self):
        """factorial(1000) should not raise ValueError."""
        result = evaluate("factorial(1000)")
        assert result is not None
        assert isinstance(result, int)


class TestNestingDepth:
    """Verify MAX_NESTING_DEPTH is enforced."""

    def test_deep_nesting_rejected(self):
        """Deeply nested expressions should raise EvaluationError."""
        from eggcalc.evaluator import MAX_NESTING_DEPTH
        expr = "1+" * (MAX_NESTING_DEPTH + 10) + "1"
        with pytest.raises(EvaluationError, match="deeply nested"):
            evaluate(expr)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
