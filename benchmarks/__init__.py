"""Benchmark suite for eggcalc performance measurement."""

from .run import (
    benchmark_evaluate,
    benchmark_evaluate_raw,
    benchmark_evaluate_cached,
    benchmark_normalize,
    benchmark_all,
)

from .results import BASELINE, format_benchmark_result

__all__ = [
    "benchmark_evaluate",
    "benchmark_evaluate_raw",
    "benchmark_evaluate_cached",
    "benchmark_normalize",
    "benchmark_all",
    "BASELINE",
    "format_benchmark_result",
]