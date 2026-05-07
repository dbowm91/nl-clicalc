"""
MCP tool schemas for nl-calc exact tools.

Defines input/output schemas for each MCP tool following the
consistency requirements in the plan.
"""

from __future__ import annotations

from typing import TypedDict


class ErrorEnvelope(TypedDict):
    """Standard error envelope for MCP tool responses."""
    ok: bool
    error_type: str
    error: str
    hints: list[str]


class SuccessEnvelope(TypedDict):
    """Standard success envelope for MCP tool responses."""
    ok: bool
    result: dict


# Input schemas

class CalculateInput(TypedDict):
    """Input for nl_calculate tool."""
    expression: str


class MeasureTextInput(TypedDict):
    """Input for nl_measure_text tool."""
    text: str
    include_codepoints: bool


class TextEqualInput(TypedDict):
    """Input for nl_text_equal tool."""
    a: str
    b: str
    normalization: str
    casefold: bool
    trim: bool


class ExplainDiffInput(TypedDict):
    """Input for nl_explain_diff tool."""
    a: str
    b: str
    max_diffs: int
    include_codepoints: bool
    include_context: bool


class InspectTextInput(TypedDict):
    """Input for nl_inspect_text tool."""
    text: str
    include_codepoints: bool
    include_confusables: bool


class CountCharsInput(TypedDict):
    """Input for nl_count_chars tool."""
    text: str
    target: str | None
    normalization: str


class CheckBracketsInput(TypedDict):
    """Input for nl_check_brackets tool."""
    text: str
    pairs: dict[str, str] | None


class ValidateJsonInput(TypedDict):
    """Input for nl_validate_json tool."""
    text: str


class RegexTestInput(TypedDict):
    """Input for nl_regex_test tool."""
    pattern: str
    samples: list[str]
    flags: list[str] | None


class ListCompareInput(TypedDict):
    """Input for nl_list_compare tool."""
    a: list[str]
    b: list[str]
    ignore_order: bool
    casefold: bool
    normalization: str


# Tool definitions (for schema documentation)

TOOL_SCHEMAS = {
    "nl_calculate": {
        "description": "Deterministically evaluate arithmetic, unit conversions, constants, and simple scientific expressions. Use for math and unit tasks instead of asking the model to calculate.",
        "input": CalculateInput,
    },
    "nl_measure_text": {
        "description": "Measure exact text properties: UTF-8 byte length, codepoint count, words, lines, whitespace, newline style, Unicode normalization state, invisibles, and mixed-script signals.",
        "input": MeasureTextInput,
    },
    "nl_text_equal": {
        "description": "Compare two strings under raw, Unicode-normalized, casefolded, or trimmed modes and report exact equality evidence.",
        "input": TextEqualInput,
    },
    "nl_explain_diff": {
        "description": "Explain why two strings differ, including spans, codepoints, Unicode names, normalization equivalence, confusables, invisibles, and agent-facing classification.",
        "input": ExplainDiffInput,
    },
    "nl_inspect_text": {
        "description": "Inspect a string for hidden characters, Unicode confusables, mixed scripts, normalization state, and display-safe representation.",
        "input": InspectTextInput,
    },
    "nl_count_chars": {
        "description": "Count exact characters or produce a character frequency table with codepoint positions.",
        "input": CountCharsInput,
    },
    "nl_check_brackets": {
        "description": "Check whether delimiters are structurally balanced and report unmatched delimiters with line/column positions.",
        "input": CheckBracketsInput,
    },
    "nl_validate_json": {
        "description": "Validate JSON and report precise parse errors or top-level structure information.",
        "input": ValidateJsonInput,
    },
    "nl_regex_test": {
        "description": "Test a Python regular expression against sample strings and report match/fullmatch status, spans, groups, and errors.",
        "input": RegexTestInput,
    },
    "nl_list_compare": {
        "description": "Compare two lists exactly, optionally ignoring order, casefolding, or Unicode-normalizing elements. Report missing, duplicate, and near-match items.",
        "input": ListCompareInput,
    },
}
