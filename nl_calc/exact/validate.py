"""
Text validation primitives.

Provides validation for JSON, brackets, and regex patterns.
"""

from __future__ import annotations

import json
import re
from typing import TypedDict


MAX_PATTERN_LENGTH = 1000
MAX_PATTERN_NESTING = 5


class BracketError(TypedDict):
    """Information about an unmatched bracket."""
    char: str
    index: int
    line: int
    column: int


class CheckBracketsResult(TypedDict):
    """Result of bracket checking."""
    balanced: bool
    unmatched_openers: list[BracketError]
    unmatched_closers: list[BracketError]


class ValidateJsonResult(TypedDict):
    """Result of JSON validation."""
    valid: bool
    error: str | None
    line: int | None
    column: int | None
    position: int | None
    type: str | None
    top_level_keys: list[str] | None


class RegexMatch(TypedDict):
    """Result of a single regex match."""
    sample: str
    matches: bool
    fullmatch: bool
    span: list[int] | None
    groups: list[str]
    groupdict: dict[str, str]


class RegexTestResult(TypedDict):
    """Result of regex testing."""
    valid_pattern: bool
    results: list[RegexMatch]
    error: str | None


# Default bracket pairs
DEFAULT_BRACKET_PAIRS: dict[str, str] = {
    "(": ")",
    "[": "]",
    "{": "}",
    "<": ">",
}


def _get_line_column(s: str, index: int) -> tuple[int, int]:
    """Get 1-based line and column for a string index.

    Args:
        s: Input string.
        index: Character index.

    Returns:
        Tuple of (line, column), both 1-based.
    """
    line = 1
    column = 1
    for i in range(index):
        if s[i] == "\n":
            line += 1
            column = 1
        else:
            column += 1
    return line, column


def check_brackets(
    s: str,
    pairs: dict[str, str] | None = None,
) -> CheckBracketsResult:
    """Check if brackets are balanced in the string.

    Tracks unmatched openers and closers with positions.

    Args:
        s: Input string.
        pairs: Bracket pair mapping (default: () [] {} <>).

    Returns:
        Dictionary with balanced (bool), unmatched_openers (list),
        and unmatched_closers (list).
    """
    if pairs is None:
        pairs = DEFAULT_BRACKET_PAIRS

    openers = set(pairs.keys())
    closers = set(pairs.values())
    opener_to_closer = pairs.copy()

    stack: list[tuple[str, int]] = []  # (char, index)
    unmatched_openers: list[BracketError] = []
    unmatched_closers: list[BracketError] = []

    for index, char in enumerate(s):
        if char in openers:
            stack.append((char, index))
        elif char in closers:
            if stack:
                opener, opener_index = stack.pop()
                if opener_to_closer.get(opener) != char:
                    # Mismatch - treat as both unmatched
                    unmatched_openers.append(BracketError(
                        char=opener,
                        index=opener_index,
                        line=_get_line_column(s, opener_index)[0],
                        column=_get_line_column(s, opener_index)[1],
                    ))
                    unmatched_closers.append(BracketError(
                        char=char,
                        index=index,
                        line=_get_line_column(s, index)[0],
                        column=_get_line_column(s, index)[1],
                    ))
            else:
                # No matching opener
                unmatched_closers.append(BracketError(
                    char=char,
                    index=index,
                    line=_get_line_column(s, index)[0],
                    column=_get_line_column(s, index)[1],
                ))

    # Remaining openers are unmatched
    for opener, opener_index in stack:
        unmatched_openers.append(BracketError(
            char=opener,
            index=opener_index,
            line=_get_line_column(s, opener_index)[0],
            column=_get_line_column(s, opener_index)[1],
        ))

    return CheckBracketsResult(
        balanced=len(unmatched_openers) == 0 and len(unmatched_closers) == 0,
        unmatched_openers=unmatched_openers,
        unmatched_closers=unmatched_closers,
    )


def validate_json(s: str) -> ValidateJsonResult:
    """Validate JSON string and return detailed error information.

    Args:
        s: Input string.

    Returns:
        Dictionary with valid (bool), error message (if invalid),
        line, column, position (if invalid), and type/top_level_keys (if valid).
    """
    try:
        parsed = json.loads(s)

        # Determine the type
        if isinstance(parsed, dict):
            type_str = "object"
            keys = list(parsed.keys())
        elif isinstance(parsed, list):
            type_str = "array"
            keys = None
        else:
            type_str = type(parsed).__name__
            keys = None

        return ValidateJsonResult(
            valid=True,
            error=None,
            line=None,
            column=None,
            position=None,
            type=type_str,
            top_level_keys=keys,
        )

    except json.JSONDecodeError as e:
        return ValidateJsonResult(
            valid=False,
            error=e.msg,
            line=e.lineno,
            column=e.colno,
            position=e.pos,
            type=None,
            top_level_keys=None,
        )


def _check_pattern_complexity(pattern: str) -> tuple[bool, str | None]:
    """Check if regex pattern is too complex (ReDoS prevention).

    Args:
        pattern: Regular expression pattern.

    Returns:
        Tuple of (is_safe, error_message).
    """
    if len(pattern) > MAX_PATTERN_LENGTH:
        return False, f"Pattern length {len(pattern)} exceeds maximum {MAX_PATTERN_LENGTH}"

    nesting_depth = 0
    max_nesting = 0
    in_char_class = False
    i = 0

    while i < len(pattern):
        char = pattern[i]

        if char == '\\' and i + 1 < len(pattern):
            i += 2
            continue

        if char == '[':
            nesting_depth += 1
            max_nesting = max(max_nesting, nesting_depth)
            in_char_class = True
        elif char == ']':
            nesting_depth -= 1
            in_char_class = False
        elif char == '(' and not in_char_class:
            nesting_depth += 1
            max_nesting = max(max_nesting, nesting_depth)
        elif char == ')' and not in_char_class:
            nesting_depth -= 1
            if nesting_depth < 0:
                nesting_depth = 0

        i += 1

    if max_nesting > MAX_PATTERN_NESTING:
        return False, f"Pattern nesting depth {max_nesting} exceeds maximum {MAX_PATTERN_NESTING}"

    return True, None


def regex_test(
    pattern: str,
    samples: list[str],
    flags: list[str] | None = None,
) -> RegexTestResult:
    """Test a Python regular expression against sample strings.

    Args:
        pattern: Regular expression pattern.
        samples: List of strings to test against.
        flags: List of flag names (e.g., ["IGNORECASE", "MULTILINE"]).

    Returns:
        Dictionary with valid_pattern (bool) and results (list of
        RegexMatch dicts with matches, fullmatch, span, groups, groupdict).
    """
    is_safe, error_msg = _check_pattern_complexity(pattern)
    if not is_safe:
        return RegexTestResult(
            valid_pattern=False,
            results=[],
            error=error_msg,
        )

    flag_values = 0
    if flags:
        flag_map = {
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
            "UNICODE": re.UNICODE,
            "DEBUG": re.DEBUG,
            "VERBOSE": re.VERBOSE,
        }
        for flag_name in flags:
            if flag_name in flag_map:
                flag_values |= flag_map[flag_name]

    try:
        compiled = re.compile(pattern, flag_values)
    except re.error as e:
        return RegexTestResult(
            valid_pattern=False,
            results=[],
            error=str(e),
        )

    results: list[RegexMatch] = []

    for sample in samples:
        match = compiled.search(sample)
        if match is None:
            results.append(RegexMatch(
                sample=sample,
                matches=False,
                fullmatch=False,
                span=None,
                groups=[],
                groupdict={},
            ))
        else:
            full_match = compiled.fullmatch(sample)
            span = list(match.span()) if match else None
            groups = list(match.groups())
            groupdict = match.groupdict() if match else {}

            results.append(RegexMatch(
                sample=sample,
                matches=True,
                fullmatch=full_match is not None,
                span=span,
                groups=groups,
                groupdict=groupdict,
            ))

    return RegexTestResult(
        valid_pattern=True,
        results=results,
    )
