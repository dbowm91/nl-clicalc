"""Shared pytest fixtures for nl-calc tests."""

import pytest

from eggcalc import UnitValue, evaluate, evaluate_raw
from eggcalc.normalize import NORMALIZE, PATTERNS


@pytest.fixture
def eval_result():
    """Fixture that wraps evaluate result, extracting value from UnitValue if needed."""
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
def get_value():
    """Helper to extract numeric value from result (handles UnitValue)."""
    def _get_value(result):
        if isinstance(result, UnitValue):
            return result.value
        return result
    return _get_value


@pytest.fixture
def approx():
    """pytest.approx wrapper for floating point comparisons."""
    return lambda x, y, rel_tol=1e-10: abs(x - y) < rel_tol
