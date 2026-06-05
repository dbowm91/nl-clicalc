"""Shared pytest fixtures for eggcalc tests."""

import pytest

from eggcalc import UnitValue, evaluate, evaluate_raw
from eggcalc.normalize import NORMALIZE, PATTERNS


@pytest.fixture
def eval_result():
    """Optional helper: wraps evaluate result, extracting value from UnitValue if needed.
    Not currently used by any tests — available for convenience if needed.
    """
    def _eval_result(expr):
        result = evaluate(expr)
        if isinstance(result, UnitValue):
            return result.value
        return result
    return _eval_result


@pytest.fixture
def evaluate_raw():
    """Direct access to evaluate_raw function."""
    from eggcalc import evaluate_raw
    return evaluate_raw


@pytest.fixture
def normalize_config():
    """Access to normalize config and patterns."""
    return (NORMALIZE, PATTERNS)


@pytest.fixture
def extract_value():
    """Extract the numeric value from a result, intentionally hiding the UnitValue wrapper.

    Use this when you only care about the numeric value and want convenience
    over verifying the UnitValue wrapper type.
    """
    def _extract_value(result):
        if isinstance(result, UnitValue):
            return result.value
        return result
    return _extract_value


@pytest.fixture
def approx():
    """Optional helper: pytest.approx wrapper for floating point comparisons.
    Most tests use pytest.approx directly — available for convenience if needed.
    """
    return lambda x, y, rel_tol=1e-10: abs(x - y) < rel_tol
