"""
MCP tool schemas for nl-calc exact tools.

Defines input/output schemas for each MCP tool following the
consistency requirements in the plan.
"""

from __future__ import annotations

from typing import Any, TypedDict


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


TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "math_eval": {
        "description": "Deterministically evaluate arithmetic, unit conversions, constants, and simple scientific expressions. Use for math and unit tasks instead of asking the model to calculate.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate (e.g., '5 + 3', '30m + 100ft', 'five plus three')",
                },
            },
            "required": ["expression"],
        },
    },
    "text_measure": {
        "description": "Measure exact text properties: UTF-8 byte length, codepoint count, words, lines, whitespace, newline style, Unicode normalization state, invisibles, and mixed-script signals.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Input string to measure",
                },
                "include_codepoints": {
                    "type": "boolean",
                    "description": "Include codepoint details (not yet implemented)",
                    "default": False,
                },
            },
            "required": ["text"],
        },
    },
    "text_equal": {
        "description": "Compare two strings under raw, Unicode-normalized, casefolded, or trimmed modes and report exact equality evidence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "string", "description": "First string"},
                "b": {"type": "string", "description": "Second string"},
                "normalization": {
                    "type": "string",
                    "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"],
                    "default": "raw",
                    "description": "Unicode normalization form",
                },
                "casefold": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use casefolded comparison",
                },
                "trim": {
                    "type": "boolean",
                    "default": False,
                    "description": "Trim whitespace",
                },
            },
            "required": ["a", "b"],
        },
    },
    "text_diff_explain": {
        "description": "Explain why two strings differ, including spans, codepoints, Unicode names, normalization equivalence, confusables, invisibles, and agent-facing classification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "string", "description": "First string"},
                "b": {"type": "string", "description": "Second string"},
                "max_diffs": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum diff spans to return",
                },
                "include_codepoints": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include codepoint details",
                },
                "include_context": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include context notes",
                },
            },
            "required": ["a", "b"],
        },
    },
    "text_inspect": {
        "description": "Inspect a string for hidden characters, Unicode confusables, mixed scripts, normalization state, and display-safe representation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input string to inspect"},
                "include_codepoints": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include codepoint details in invisibles",
                },
                "include_confusables": {
                    "type": "boolean",
                    "default": True,
                    "description": "Check for confusables",
                },
            },
            "required": ["text"],
        },
    },
    "text_count": {
        "description": "Count exact characters or produce a character frequency table with codepoint positions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input string"},
                "target": {
                    "type": "string",
                    "description": "Single character to count (None for frequency table)",
                },
                "normalization": {
                    "type": "string",
                    "enum": ["raw", "NFC", "NFKC"],
                    "default": "raw",
                    "description": "Unicode normalization form",
                },
            },
            "required": ["text"],
        },
    },
    "text_truncate": {
        "description": "Truncate a string to a specified number of grapheme clusters (user-perceived characters). Preserves emoji, combining sequences, and flag sequences intact. Useful for AI agent prompts where visual length matters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input string to truncate"},
                "max_graphemes": {
                    "type": "integer",
                    "description": "Maximum number of grapheme clusters to return",
                    "minimum": 0,
                },
            },
            "required": ["text", "max_graphemes"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Result string (truncated if truncation occurred)"},
                "original_graphemes": {"type": "integer", "description": "Original grapheme count"},
                "truncated_graphemes": {"type": "integer", "description": "Grapheme count in result"},
                "truncated": {"type": "boolean", "description": "True if text was truncated"},
            },
        },
    },
    "validate_brackets": {
        "description": "Check whether delimiters are structurally balanced and report unmatched delimiters with line/column positions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input string"},
                "pairs": {
                    "type": "object",
                    "description": "Bracket pair mapping (default: () [] {} <>)",
                },
            },
            "required": ["text"],
        },
    },
    "validate_json": {
        "description": "Validate JSON and report precise parse errors or top-level structure information.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input string to validate as JSON"},
            },
            "required": ["text"],
        },
    },
    "validate_regex": {
        "description": "Test a Python regular expression against sample strings and report match/fullmatch status, spans, groups, and errors.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regular expression pattern"},
                "samples": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of strings to test against",
                },
                "flags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Flag names (IGNORECASE, MULTILINE, etc.)",
                },
            },
            "required": ["pattern", "samples"],
        },
    },
    "list_compare": {
        "description": "Compare two lists exactly, optionally ignoring order, casefolding, or Unicode-normalizing elements. Report missing, duplicate, and near-match items.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "First list",
                },
                "b": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Second list",
                },
                "ignore_order": {
                    "type": "boolean",
                    "default": True,
                    "description": "Compare as sets",
                },
                "casefold": {
                    "type": "boolean",
                    "default": False,
                    "description": "Casefold elements before comparison",
                },
                "normalization": {
                    "type": "string",
                    "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"],
                    "default": "NFC",
                    "description": "Unicode normalization form",
                },
            },
            "required": ["a", "b"],
        },
    },
}
