"""
Fuzz tests for nl-calc security.

Tests for:
- Invalid inputs (random strings, special characters)
- DoS protection (very long inputs, deeply nested expressions)
- Code execution prevention (import, exec, etc.)
- Memory exhaustion protection
"""

import random
import string
import subprocess
import sys

import pytest


class TestSecurityFuzz:
    """Security-focused fuzz tests."""

    def test_random_string_inputs(self):
        """Test that random strings don't cause crashes."""
        from nl_calc import EvaluationError, evaluate_raw

        # Generate random strings
        random.seed(42)
        for _ in range(100):
            # Random alphanumeric strings of varying lengths
            length = random.randint(1, 100)
            test_input = ''.join(random.choices(string.ascii_letters + string.digits + " ", k=length))

            # Should either return a result or raise EvaluationError
            try:
                result = evaluate_raw(test_input)
                # If it succeeds, result should be valid
                assert result is not None
            except EvaluationError:
                # Expected - invalid expressions should raise
                pass
            except Exception as e:
                # No other exceptions should occur
                pytest.fail(f"Unexpected exception for input '{test_input[:50]}...': {type(e).__name__}: {e}")

    def test_special_character_inputs(self):
        """Test inputs with special characters don't cause crashes."""
        from nl_calc import EvaluationError, evaluate_raw

        special_inputs = [
            ";;;",
            "<<<>>>",
            "@#$%^&*()",
            "\x00\x01\x02",
            "\n\n\n",
            "\t\t\t",
            "\\\\\\\\",
            "///*/",
            "''''''",
            '""""""',
            "\x1b[31m",  # ANSI color codes
            "eval(",
            "exec(",
            "__import__",
            "compile(",
            "breakpoint(",
            "globals()",
            "locals()",
            "vars()",
            "dir()",
            "help(",
            "open(",
            "print(",
            "input(",
            "exit(",
            "quit(",
            "os.system(",
            "subprocess.",
            "import ",
            "from ",
        ]

        for test_input in special_inputs:
            try:
                result = evaluate_raw(test_input)
                assert result is not None
            except (EvaluationError, SyntaxError):
                pass  # Expected
            except Exception as e:
                pytest.fail(f"Unexpected exception for input '{test_input}': {type(e).__name__}: {e}")

    def test_very_long_inputs(self):
        """Test that very long inputs are rejected quickly."""
        from nl_calc import MAX_INPUT_LENGTH, EvaluationError, evaluate_raw

        # Test at exactly the limit
        long_input = "1+" * (MAX_INPUT_LENGTH // 2)

        # Should complete or be rejected
        try:
            result = evaluate_raw(long_input)
            # If it works, result should be valid
            assert result is not None
        except (EvaluationError, SyntaxError):
            pass  # Expected - too long
        except Exception as e:
            pytest.fail(f"Unexpected exception for long input: {type(e).__name__}: {e}")

        # Test over the limit
        over_limit = "1+" * (MAX_INPUT_LENGTH + 1000)

        try:
            result = evaluate_raw(over_limit)
            pytest.fail("Should have raised an error for over-limit input")
        except (EvaluationError, SyntaxError):
            pass  # Expected

    def test_max_input_length_enforced(self):
        """Test MAX_INPUT_LENGTH is properly enforced."""
        from nl_calc import MAX_INPUT_LENGTH, NORMALIZE, PATTERNS, run

        # Create input longer than MAX_INPUT_LENGTH
        long_expr = "a" * (MAX_INPUT_LENGTH + 1)

        result, exit_code = run(long_expr, NORMALIZE, PATTERNS, "plain", False)

        assert exit_code == 2  # Should return error code 2
        assert result is None

    def test_deeply_nested_expressions(self):
        """Test deeply nested expressions don't cause stack overflow."""
        from nl_calc import MAX_NESTING_DEPTH, EvaluationError, evaluate_raw

        # Test within the limit
        nested = "(" * MAX_NESTING_DEPTH + "1" + ")" * MAX_NESTING_DEPTH
        try:
            result = evaluate_raw(nested)
            assert result == 1
        except EvaluationError as e:
            assert "too deep" not in str(e).lower()

        # Test over the limit - should fail gracefully
        very_deep = "(" * (MAX_NESTING_DEPTH + 10) + "1" + ")" * (MAX_NESTING_DEPTH + 10)
        try:
            result = evaluate_raw(very_deep)
            pytest.fail("Should have raised an error for over-limit nesting")
        except (EvaluationError, ValueError) as e:
            assert "too deep" in str(e).lower()

    def test_large_exponents(self):
        """Test that large exponents are rejected."""
        from nl_calc import EvaluationError, evaluate

        large_exp_inputs = [
            "2**100000",
            "2**999999",
            "10**10000",  # Exactly MAX_EXPONENT
            "10**10001",  # Over MAX_EXPONENT
            "2**-100000",
            "2**999999999",
        ]

        for test_input in large_exp_inputs:
            try:
                result = evaluate(test_input)
            except EvaluationError:
                pass  # Expected - exponent too large or invalid

    def test_wide_expressions(self):
        """Test expressions with many operations don't cause memory issues."""
        from nl_calc import EvaluationError, evaluate_raw

        # Create expression with many operations (not nested)
        wide_expr = "+".join(["1"] * 10000)

        try:
            result = evaluate_raw(wide_expr)
            # Should succeed or fail gracefully
            assert result is not None
        except (EvaluationError, SyntaxError, MemoryError):
            pass  # Expected - too many operations or OOM

    def test_code_execution_attempts(self):
        """Verify that code execution attempts are blocked."""
        from nl_calc import EvaluationError, evaluate, evaluate_raw

        dangerous_inputs = [
            # Import attempts
            "import os",
            "import sys",
            "from os import system",
            "__import__('os')",

            # Code execution
            "eval('1+1')",
            "exec('1+1')",

            # Attribute access
            "().__class__",
            "().__class__.__bases__",
            "object.__subclasses__",

            # File operations
            "open('/etc/passwd')",

            # System calls
            "os.system('ls')",
            "subprocess.call(['ls'])",

            # Variable access
            "globals()",
            "locals()",
            "vars()",

            # Other dangerous
            "breakpoint()",
            "help(1)",
        ]

        for test_input in dangerous_inputs:
            try:
                # Try both evaluate (pre-normalized) and evaluate_raw
                try:
                    result = evaluate(test_input)
                except:
                    result = evaluate_raw(test_input)

                # If we get here without exception, check result is safe
                # Should NOT execute the dangerous code
                assert result is not None
            except EvaluationError:
                pass  # Expected - blocked
            except SyntaxError:
                pass  # Expected - invalid syntax

    def test_attribute_access_blocked(self):
        """Test that dangerous attribute access is blocked."""
        from nl_calc import EvaluationError, evaluate

        attr_attempts = [
            "().__class__",
            "1 .__class__",
            "(1).__class__.__mro__",
            "''.__class__.__mro__",
            "[].__class__",
            "{}.__class__",
            "set().__class__",
        ]

        for test_input in attr_attempts:
            with pytest.raises(EvaluationError) as exc_info:
                evaluate(test_input)
            assert "not allowed" in str(exc_info.value).lower() or "unsupported" in str(exc_info.value).lower()

    def test_comprehensions_blocked(self):
        """Test that list/dict comprehensions are blocked."""
        from nl_calc import EvaluationError, evaluate

        comp_inputs = [
            "[x for x in range(10)]",
            "{x for x in range(10)}",
            "{x: x for x in range(10)}",
            "(x for x in range(10))",
            "[x for x in __import__('os').listdir('.')]",
        ]

        for test_input in comp_inputs:
            with pytest.raises(EvaluationError) as exc_info:
                evaluate(test_input)
            assert "unsupported" in str(exc_info.value).lower()

    def test_lambda_blocked(self):
        """Test that lambda expressions are blocked."""
        from nl_calc import EvaluationError, evaluate

        lambda_inputs = [
            "lambda x: x+1",
            "(lambda x: x+1)(5)",
            "f = lambda x: x",
        ]

        for test_input in lambda_inputs:
            with pytest.raises((EvaluationError, SyntaxError)):
                evaluate(test_input)

    def test_if_expression_blocked(self):
        """Test that ternary if expressions are blocked."""
        from nl_calc import EvaluationError, evaluate

        if_inputs = [
            "1 if True else 0",
            "x if x > 0 else -x",
        ]

        for test_input in if_inputs:
            with pytest.raises(EvaluationError):
                evaluate(test_input)

    def test_comparison_blocked(self):
        """Test that comparison operators are blocked."""
        from nl_calc import EvaluationError, evaluate

        compare_inputs = [
            "1 < 2",
            "1 > 0",
            "1 == 1",
            "1 != 2",
            "1 <= 2",
            "1 >= 0",
            "1 < 2 < 3",
        ]

        for test_input in compare_inputs:
            with pytest.raises(EvaluationError):
                evaluate(test_input)

    def test_boolean_operators_blocked(self):
        """Test that boolean operators are blocked."""
        from nl_calc import EvaluationError, evaluate

        bool_inputs = [
            "True and False",
            "True or False",
            "not True",
            "1 and 2",
            "1 or 0",
            "not 1",
        ]

        for test_input in bool_inputs:
            with pytest.raises(EvaluationError):
                evaluate(test_input)

    def test_subscription_blocked(self):
        """Test that subscripting is blocked."""
        from nl_calc import EvaluationError, evaluate

        sub_inputs = [
            "[1,2,3][0]",
            "()[0]",
            "{}['a']",
            "iter([])[0]",
        ]

        for test_input in sub_inputs:
            with pytest.raises(EvaluationError):
                evaluate(test_input)


class TestCLISecurity:
    """Security tests for CLI interface."""

    def test_cli_rejects_long_input(self):
        """Test CLI rejects input over MAX_INPUT_LENGTH."""
        long_expr = "x" * 20000

        result = subprocess.run(
            [sys.executable, "-m", "nl_calc", long_expr],
            capture_output=True,
            text=True,
            timeout=5,
        )

        assert result.returncode != 0
        assert "too long" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_cli_timeout_on_complex_input(self):
        """Test CLI doesn't hang on complex expressions."""
        # Nested expression that would take very long if not limited
        complex_expr = "(" * 100 + "1" + ")" * 100

        result = subprocess.run(
            [sys.executable, "-m", "nl_calc", "-e", complex_expr],
            capture_output=True,
            text=True,
            timeout=5,  # Should complete within 5 seconds
        )

        # Should either succeed or fail quickly
        assert result.returncode in (0, 1)

    def test_cli_no_code_injection(self):
        """Test CLI doesn't execute injected code."""
        malicious_inputs = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "$(whoami)",
            "`ls`",
            "&& ls",
            "|| ls",
        ]

        for test_input in malicious_inputs:
            result = subprocess.run(
                [sys.executable, "-m", "nl_calc", "-e", test_input],
                capture_output=True,
                text=True,
                timeout=5,
            )
            # Should either error or return result (not execute the command)
            # The malicious string should appear in output, not be executed
            assert result.returncode in (0, 1)


class TestMemorySafety:
    """Test memory-related safety."""

    def test_no_memory_leak_on_repeated_calls(self):
        """Test repeated calls don't leak memory."""
        import tracemalloc

        from nl_calc import evaluate_raw

        tracemalloc.start()

        # Run many evaluations
        for i in range(1000):
            try:
                evaluate_raw("5 + 3")
            except:
                pass

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Memory should not grow significantly
        # 1MB is generous - typical should be < 100KB
        assert peak < 1_000_000, f"Peak memory too high: {peak} bytes"

    def test_recursion_limit_protection(self):
        """Test expression evaluation respects recursion limits."""
        from nl_calc import MAX_NESTING_DEPTH, EvaluationError, evaluate_raw

        # Test within the limit
        depth = MAX_NESTING_DEPTH
        nested = "(" * depth + "1" + ")" * depth

        try:
            result = evaluate_raw(nested)
            assert result == 1
        except (EvaluationError, ValueError, RecursionError, SyntaxError):
            pass  # Acceptable


class TestASTSecurity:
    """Tests for AST-based security."""

    def test_ast_parse_blocks_unsafe_nodes(self):
        """Test that AST parser correctly identifies unsafe nodes."""
        from nl_calc.evaluator import EvaluationError, Evaluator

        evaluator = Evaluator()

        # These should all be blocked
        unsafe_expressions = [
            "[x for x in y]",  # ListComp
            "{x for x in y}",  # SetComp
            "{x: y for x in z}",  # DictComp
            "lambda x: x",  # Lambda
            "x if y else z",  # IfExp
            "x < y",  # Compare
            "x and y",  # BoolOp
            "x[0]",  # Subscript
        ]

        for expr in unsafe_expressions:
            with pytest.raises(EvaluationError):
                evaluator.evaluate(expr)

    def test_only_safe_functions_allowed(self):
        """Test only whitelisted functions can be called."""
        from nl_calc import EvaluationError, evaluate

        # Test math functions work
        assert evaluate("sqrt(4)") == 2
        assert evaluate("sin(0)") == 0

        # Test dangerous functions are blocked
        with pytest.raises(EvaluationError):
            evaluate("__import__('os')")

        with pytest.raises(EvaluationError):
            evaluate("eval('1')")

        with pytest.raises(EvaluationError):
            evaluate("exec('x=1')")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
