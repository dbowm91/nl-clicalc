"""
MCP tools implementation for nl-calc exact functions.

Maps MCP tool names to their corresponding synthesis functions
and handles input validation and error wrapping.
"""

from __future__ import annotations

from typing import Any

from .. import EvaluationError, evaluate_raw
from ..exact import (
    check_brackets as _check_brackets,
)
from ..exact import (
    regex_test as _regex_test,
)
from ..exact import (
    validate_json as _validate_json,
)
from ..exact.synthesis import (
    count_chars as _count_chars,
)
from ..exact.synthesis import (
    explain_diff as _explain_diff,
)
from ..exact.synthesis import (
    inspect_text as _inspect_text,
)
from ..exact.synthesis import (
    list_compare as _list_compare,
)
from ..exact.synthesis import (
    measure_text as _measure_text,
)
from ..exact.synthesis import (
    text_equal as _text_equal,
)
from .schemas import ErrorEnvelope

MAX_TEXT_LENGTH = 100_000
MAX_LIST_ITEMS = 10_000
MAX_REGEX_SAMPLES = 100


def _error_response(error_type: str, error: str, hints: list[str] | None = None) -> dict:
    """Create a standardized error envelope."""
    return ErrorEnvelope(
        ok=False,
        error_type=error_type,
        error=error,
        hints=hints or [],
    )


def _success_response(result: Any) -> dict:
    """Create a standardized success envelope."""
    return {"ok": True, "result": result}


def math_eval(expression: str) -> dict:
    """Evaluate a math expression.

    Args:
        expression: Math expression (e.g., "5 + 3", "30m + 100ft", "five plus three").

    Returns:
        Success response with result, or error envelope.
    """
    if len(expression) > MAX_TEXT_LENGTH:
        return _error_response("InputError", f"Input exceeds maximum length of {MAX_TEXT_LENGTH}")
    try:
        result = evaluate_raw(expression)
        if hasattr(result, 'value'):
            result_val = result.value
        else:
            result_val = result
        return {"result": str(result_val), "type": type(result_val).__name__}
    except EvaluationError as e:
        return _error_response("EvaluationError", str(e), ["Check expression syntax"])
    except Exception as e:
        return _error_response("UnexpectedError", str(e))


def text_measure(text: str, include_codepoints: bool = False) -> dict:
    """Measure text properties.

    Args:
        text: Input string.
        include_codepoints: Include codepoint details (not yet implemented).

    Returns:
        Success envelope with metrics, or error envelope.
    """
    if len(text) > MAX_TEXT_LENGTH:
        return _error_response(
            "InputTooLarge",
            f"Input length {len(text)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
            [f"Maximum input length is {MAX_TEXT_LENGTH} characters"],
        )

    try:
        result = _measure_text(text, include_codepoints)
        return _success_response(result)
    except ValueError as e:
        return _error_response("ValidationError", str(e))


def text_equal(
    a: str,
    b: str,
    normalization: str = "raw",
    casefold: bool = False,
    trim: bool = False,
) -> dict:
    """Compare two strings for equality.

    Args:
        a: First string.
        b: Second string.
        normalization: "raw", "NFC", "NFD", "NFKC", or "NFKD".
        casefold: Use casefolded comparison.
        trim: Trim whitespace.

    Returns:
        Success envelope with comparison result, or error envelope.
    """
    valid_normalizations = {"raw", "NFC", "NFD", "NFKC", "NFKD"}
    if normalization not in valid_normalizations:
        return _error_response(
            "ValidationError",
            f"Unsupported normalization form: {normalization}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
        )

    try:
        result = _text_equal(a, b, normalization, casefold, trim)
        return _success_response(result)
    except Exception as e:
        return _error_response("UnexpectedError", str(e))


def text_diff_explain(
    a: str,
    b: str,
    max_diffs: int = 20,
    include_codepoints: bool = True,
    include_context: bool = True,
) -> dict:
    """Explain differences between two strings.

    Args:
        a: First string.
        b: Second string.
        max_diffs: Maximum diff spans to return.
        include_codepoints: Include codepoint details.
        include_context: Include context notes.

    Returns:
        Success envelope with diff explanation, or error envelope.
    """
    if len(a) > MAX_TEXT_LENGTH or len(b) > MAX_TEXT_LENGTH:
        return _error_response(
            "InputTooLarge",
            f"Input exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
            [f"Maximum input length is {MAX_TEXT_LENGTH} characters"],
        )

    try:
        result = _explain_diff(a, b, max_diffs, include_codepoints, include_context)
        return _success_response(result)
    except ValueError as e:
        return _error_response("ValidationError", str(e))


def text_inspect(
    text: str,
    include_codepoints: bool = True,
    include_confusables: bool = True,
) -> dict:
    """Inspect text for Unicode signals and hidden characters.

    Args:
        text: Input string.
        include_codepoints: Include codepoint details in invisibles.
        include_confusables: Check for confusables.

    Returns:
        Success envelope with inspection result, or error envelope.
    """
    if len(text) > MAX_TEXT_LENGTH:
        return _error_response(
            "InputTooLarge",
            f"Input length {len(text)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
            [f"Maximum input length is {MAX_TEXT_LENGTH} characters"],
        )

    try:
        result = _inspect_text(text, include_codepoints, include_confusables)
        return _success_response(result)
    except ValueError as e:
        return _error_response("ValidationError", str(e))


def text_count(
    text: str,
    target: str | None = None,
    normalization: str = "raw",
) -> dict:
    """Count character occurrences or return frequency table.

    Args:
        text: Input string.
        target: Single character to count (None for frequency table).
        normalization: "raw", "NFC", or "NFKC".

    Returns:
        Success envelope with count result, or error envelope.
    """
    if len(text) > MAX_TEXT_LENGTH:
        return _error_response(
            "InputTooLarge",
            f"Input length {len(text)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
            [f"Maximum input length is {MAX_TEXT_LENGTH} characters"],
        )

    if target is not None and len(target) != 1:
        return _error_response(
            "ValidationError",
            "target must be a single character",
            ["Provide a single character or None for frequency table"],
        )

    valid_normalizations = {"raw", "NFC", "NFKC"}
    if normalization not in valid_normalizations:
        return _error_response(
            "ValidationError",
            f"Unsupported normalization form: {normalization}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
        )

    try:
        result = _count_chars(text, target, normalization)
        return _success_response(result)
    except ValueError as e:
        return _error_response("ValidationError", str(e))


def validate_brackets(text: str, pairs: dict[str, str] | None = None) -> dict:
    """Check bracket balance.

    Args:
        text: Input string.
        pairs: Bracket pair mapping (default: () [] {} <>).

    Returns:
        Success envelope with bracket check result, or error envelope.
    """
    if len(text) > MAX_TEXT_LENGTH:
        return _error_response(
            "InputTooLarge",
            f"Input length {len(text)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
            [f"Maximum input length is {MAX_TEXT_LENGTH} characters"],
        )

    try:
        result = _check_brackets(text, pairs)
        return _success_response(result)
    except Exception as e:
        return _error_response("UnexpectedError", str(e))


def validate_json(text: str) -> dict:
    """Validate JSON string.

    Args:
        text: Input string.

    Returns:
        Success envelope with validation result, or error envelope.
    """
    if len(text) > MAX_TEXT_LENGTH:
        return _error_response(
            "InputTooLarge",
            f"Input length {len(text)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
            [f"Maximum input length is {MAX_TEXT_LENGTH} characters"],
        )

    try:
        result = _validate_json(text)
        return _success_response(result)
    except Exception as e:
        return _error_response("UnexpectedError", str(e))


def validate_regex(
    pattern: str,
    samples: list[str],
    flags: list[str] | None = None,
) -> dict:
    """Test regex pattern against samples.

    Args:
        pattern: Regular expression pattern.
        samples: List of strings to test.
        flags: List of flag names (IGNORECASE, MULTILINE, etc.).

    Returns:
        Success envelope with regex test results, or error envelope.
    """
    if len(samples) > MAX_REGEX_SAMPLES:
        return _error_response(
            "InputTooLarge",
            f"Number of samples {len(samples)} exceeds MAX_REGEX_SAMPLES {MAX_REGEX_SAMPLES}",
            [f"Maximum {MAX_REGEX_SAMPLES} samples allowed"],
        )

    try:
        result = _regex_test(pattern, samples, flags)
        return _success_response(result)
    except Exception as e:
        return _error_response("UnexpectedError", str(e))


def list_compare(
    a: list[str],
    b: list[str],
    ignore_order: bool = True,
    casefold: bool = False,
    normalization: str = "NFC",
) -> dict:
    """Compare two lists.

    Args:
        a: First list.
        b: Second list.
        ignore_order: Compare as sets.
        casefold: Casefold elements before comparison.
        normalization: Unicode normalization form.

    Returns:
        Success envelope with comparison result, or error envelope.
    """
    if len(a) > MAX_LIST_ITEMS or len(b) > MAX_LIST_ITEMS:
        return _error_response(
            "InputTooLarge",
            f"List length exceeds MAX_LIST_ITEMS {MAX_LIST_ITEMS}",
            [f"Maximum {MAX_LIST_ITEMS} items per list"],
        )

    valid_normalizations = {"raw", "NFC", "NFD", "NFKC", "NFKD"}
    if normalization not in valid_normalizations:
        return _error_response(
            "ValidationError",
            f"Unsupported normalization form: {normalization}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
        )

    try:
        result = _list_compare(a, b, ignore_order, casefold, normalization)
        return _success_response(result)
    except Exception as e:
        return _error_response("UnexpectedError", str(e))
