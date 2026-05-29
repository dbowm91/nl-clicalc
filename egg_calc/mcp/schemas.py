"""
MCP tool schemas for nl-calc exact tools.

Defines input/output schemas for each MCP tool following the
consistency requirements in the plan.
"""

from __future__ import annotations

from typing import Any, TypedDict


class FindingSpan(TypedDict, total=False):
    """Location span within a finding."""
    byte_start: int
    byte_end: int
    char_start: int
    char_end: int
    line: int
    column: int


class Finding(TypedDict, total=False):
    """Structured finding emitted by MCP tools."""
    code: str
    severity: str  # "info" | "warn" | "error"
    message: str
    span: FindingSpan
    details: dict[str, Any]


class ErrorEnvelope(TypedDict):
    """Standard error envelope for MCP tool responses."""
    ok: bool
    error_type: str
    error: str
    hints: list[str]
    tool: str | None
    warnings: list[str]


TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "math_eval": {
        "description": "Deterministically evaluate arithmetic, unit conversions, constants, and simple scientific expressions. Use for math and unit tasks instead of asking the model to calculate.",
        "tier": 0,
        "tags": ["math", "evaluation", "arithmetic", "units", "constants"],
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
        "outputSchema": {
            "type": "object",
            "properties": {
                "result": {"type": "string", "description": "Evaluation result as string"},
                "type": {"type": "string", "description": "Python type name of the result"},
            },
        },
    },
    "unit_convert": {
        "description": "Convert a numeric value from one unit to another using pre-defined conversion factors.",
        "tier": 2,
        "tags": ["math", "units", "conversion"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "Numeric value to convert"},
                "from_unit": {"type": "string", "description": "Source unit (e.g., 'km', 'ft', 'kg')"},
                "to_unit": {"type": "string", "description": "Target unit (e.g., 'm', 'in', 'lb')"},
            },
            "required": ["value", "from_unit", "to_unit"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "Converted value"},
                "from_unit": {"type": "string"},
                "to_unit": {"type": "string"},
                "factor": {"type": "number", "description": "Conversion factor used"},
            },
        },
    },
    "unit_info": {
        "description": "Get information about a unit including its canonical form and category.",
        "tier": 2,
        "tags": ["math", "units", "information"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "unit": {"type": "string", "description": "Unit name or alias (e.g., 'km', 'kilogram', '℃')"},
            },
            "required": ["unit"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "unit": {"type": "string"},
                "canonical": {"type": "string", "description": "Canonical unit name"},
                "category": {"type": "string", "description": "Unit category (e.g., 'length', 'mass', 'temperature')"},
                "is_valid": {"type": "boolean"},
            },
        },
    },
    "constant_lookup": {
        "description": "Look up physical constant values and symbols (Avogadro, Planck, speed of light, etc.).",
        "tier": 2,
        "tags": ["math", "constants", "physics", "lookup"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Constant name (e.g., 'avogadro', 'planck', 'c', 'G')"},
            },
            "required": ["name"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number", "description": "Constant value"},
                "symbol": {"type": "string", "description": " display symbol (e.g., 'N_A', 'h', 'c')"},
                "display_name": {"type": "string", "description": "Human-readable name"},
            },
        },
    },
    "text_measure": {
        "description": "Measure exact text properties: UTF-8 byte length, codepoint count, words, lines, whitespace, newline style, Unicode normalization state, invisibles, and mixed-script signals.",
        "tier": 0,
        "tags": ["text", "measurement", "unicode", "metrics"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Input string to measure",
                },
                "detail": {
                    "type": "string",
                    "enum": ["summary", "normal", "full"],
                    "default": "normal",
                    "description": "Detail level for output",
                },
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "bytes_utf8": {"type": "integer"},
                "codepoints": {"type": "integer"},
                "graphemes": {"type": "integer"},
                "words": {"type": "integer"},
                "lines": {"type": "integer"},
                "nonempty_lines": {"type": "integer"},
                "blank_lines": {"type": "integer"},
                "warnings": {"type": "array"},
            },
        },
    },
    "text_equal": {
        "description": "Compare two strings under raw, Unicode-normalized, casefolded, or trimmed modes and report exact equality evidence.",
        "tier": 0,
        "tags": ["text", "comparison", "equality", "unicode"],
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
                "ignore_newline_style": {
                    "type": "boolean",
                    "default": False,
                    "description": "Normalize different newline styles before comparison",
                },
                "ignore_trailing_whitespace": {
                    "type": "boolean",
                    "default": False,
                    "description": "Ignore trailing whitespace on each line",
                },
                "ignore_final_newline": {
                    "type": "boolean",
                    "default": False,
                    "description": "Ignore trailing newline at end of strings",
                },
            },
            "required": ["a", "b"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "equal": {"type": "boolean"},
                "classification": {"type": "string"},
            },
        },
    },
    "text_diff_explain": {
        "description": "Explain why two strings differ, including spans, codepoints, Unicode names, normalization equivalence, confusables, invisibles, and agent-facing classification.",
        "tier": 1,
        "tags": ["text", "diff", "comparison", "unicode"],
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
                "detail": {
                    "type": "string",
                    "enum": ["summary", "normal", "full"],
                    "default": "normal",
                    "description": "Detail level: summary (compact), normal, or full",
                },
            },
            "required": ["a", "b"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "classification": {"type": "string"},
                "truncated": {"type": "boolean"},
                "spans": {"type": "array"},
                "a_codepoints": {"type": "array"},
                "b_codepoints": {"type": "array"},
            },
        },
    },
    "text_inspect": {
        "description": "Inspect a string for hidden characters, Unicode confusables, mixed scripts, normalization state, and display-safe representation. Can report both original and normalized text analysis.",
        "tier": 1,
        "tags": ["text", "unicode", "inspection", "security"],
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
                "detail": {
                    "type": "string",
                    "enum": ["summary", "normal", "full"],
                    "default": "normal",
                    "description": "Detail level: summary (compact), normal, or full",
                },
                "normalize": {
                    "type": "string",
                    "enum": ["none", "NFC", "NFD", "NFKC", "NFKD"],
                    "default": "none",
                    "description": "Normalization form to analyze",
                },
                "compare_normalized": {
                    "type": "boolean",
                    "default": False,
                    "description": "Report both original and normalized analysis",
                },
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "invisibles": {"type": "array"},
                "confusables": {"type": "array"},
                "bidi_controls": {"type": "array"},
                "scripts": {"type": "array"},
                "normalization": {"type": "string"},
                "visible_repr": {"type": "string"},
                "warnings": {"type": "array"},
                "limits_applied": {"type": "array"},
                "normalize": {"type": "string"},
                "compare_normalized": {"type": "boolean"},
                "original": {"type": "object"},
                "normalized": {"type": "object"},
                "normalization_findings": {"type": "array"},
            },
        },
    },
    "text_count": {
        "description": "Count exact characters or produce a character frequency table with codepoint positions, grapheme clusters, bytes, or substring matches.",
        "tier": 0,
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
                "count_mode": {
                    "type": "string",
                    "enum": ["codepoint", "grapheme", "byte", "substring"],
                    "default": "codepoint",
                    "description": "Count mode: codepoint (Python str), grapheme (user-perceived), byte (UTF-8), substring",
                },
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "count": {"type": "integer"},
                "positions": {"type": "array"},
                "frequency": {"type": "object"},
                "text_length_codepoints": {"type": "integer"},
            },
        },
    },
    "text_truncate": {
        "description": "Truncate a string to a specified number of grapheme clusters (user-perceived characters). Preserves emoji, combining sequences, and flag sequences intact. Useful for AI agent prompts where visual length matters.",
        "tier": 3,
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
    "text_transform": {
        "description": "Apply deterministic text transformations: Unicode normalization (NFC/NFD/NFKC/NFKD), casefold, trim, newline normalization, zero-width removal, bidi control stripping, and visible representation.",
        "tier": 2,
        "tags": ["text", "unicode", "transform", "normalization", "sanitation"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input string to transform"},
                "operations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Operations to apply: normalize_nfc, normalize_nfd, normalize_nfkc, normalize_nfkd, casefold, trim, trim_trailing_whitespace, normalize_newlines_lf, ensure_final_newline, strip_final_newline, remove_zero_width, remove_bidi_controls, visible_repr",
                },
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["text", "operations"],
        },
    },
    "validate_brackets": {
        "description": "Check whether delimiters are structurally balanced and report unmatched delimiters with line/column positions.",
        "tier": 1,
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
        "outputSchema": {
            "type": "object",
            "properties": {
                "balanced": {"type": "boolean"},
                "unmatched_openers": {"type": "array"},
                "unmatched_closers": {"type": "array"},
            },
        },
    },
    "validate_json": {
        "description": "Validate JSON and report precise parse errors or top-level structure information.",
        "tier": 0,
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input string to validate as JSON"},
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "valid": {"type": "boolean"},
                "error": {"type": "string"},
                "line": {"type": "integer"},
                "column": {"type": "integer"},
            },
        },
    },
    "validate_regex": {
        "description": "Test a Python regular expression against sample strings and report match/fullmatch status, spans, groups, and errors.",
        "tier": 1,
        "tags": ["text", "regex", "validation", "pattern"],
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
                "ignore_case": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use IGNORECASE flag",
                },
                "multiline": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use MULTILINE flag",
                },
                "dotall": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use DOTALL flag",
                },
                "ascii": {
                    "type": "boolean",
                    "default": False,
                    "description": "Use ASCII flag",
                },
            },
            "required": ["pattern", "samples"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "valid_pattern": {"type": "boolean"},
                "results": {"type": "array"},
                "error": {"type": "string"},
                "flags_used": {"type": "object"},
            },
        },
    },
    "list_compare": {
        "description": "Compare two lists with explicit modes: ordered ( LCS-based alignment), set (presence only), multiset (count deltas). Near matches are optional and never replace exact missing/extra results.",
        "tier": 2,
        "tags": ["text", "list", "comparison", "set"],
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
                "mode": {
                    "type": "string",
                    "enum": ["ordered", "set", "multiset"],
                    "default": "set",
                    "description": "Comparison mode: ordered (first diff, aligned ops), set (presence only), multiset (count deltas)",
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
                "trim": {
                    "type": "boolean",
                    "default": False,
                    "description": "Trim whitespace from each element",
                },
                "include_near_matches": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include near matches (fuzzy matching)",
                },
                "near_match_threshold": {
                    "type": "integer",
                    "default": 2,
                    "description": "Maximum edit distance for near matches",
                },
                "ignore_order": {
                    "type": "boolean",
                    "description": "Legacy: use mode=set or mode=multiset instead",
                },
                "treat_as_multiset": {
                    "type": "boolean",
                    "description": "Legacy: use mode=multiset instead",
                },
            },
            "required": ["a", "b"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "equal": {"type": "boolean"},
                "first_diff_index": {"type": "integer", "description": "Index of first difference (ordered mode)"},
                "equal_prefix_length": {"type": "integer", "description": "Length of equal prefix (ordered mode)"},
                "aligned": {"type": "array", "description": "Aligned operations (ordered mode)"},
                "count_deltas": {"type": "object", "description": "Count differences (multiset mode)"},
                "only_in_a": {"type": "array"},
                "only_in_b": {"type": "array"},
                "duplicates_in_a": {"type": "array"},
                "duplicates_in_b": {"type": "array"},
                "near_matches": {"type": "array", "description": "Items that differ only by edit distance"},
            },
        },
    },
    "validate_toml": {
        "description": "Validate TOML configuration files (Cargo.toml, pyproject.toml, etc.) and report parse errors with line/column positions.",
        "tier": 1,
        "tags": ["validation", "structured-data", "toml", "config", "rust", "python"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "TOML document string to validate"},
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["text"],
        },
    },
    "json_extract": {
        "description": "Extract a value from JSON using RFC 6901 JSON Pointer (e.g., /foo/bar/0). Navigate nested objects and arrays.",
        "tier": 2,
        "tags": ["json", "structured-data", "extraction", "config", "pointer"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "JSON document string"},
                "pointer": {"type": "string", "default": "", "description": "RFC 6901 JSON Pointer path (e.g., /dependencies/tokio)"},
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
                "max_output_chars": {"type": "integer", "default": 4000},
            },
            "required": ["text"],
        },
    },
    "json_compare": {
        "description": "Compare two JSON documents semantically, ignoring formatting and key order.",
        "tier": 1,
        "tags": ["json", "structured-data", "comparison", "config"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "string", "description": "First JSON document"},
                "b": {"type": "string", "description": "Second JSON document"},
                "ignore_object_order": {"type": "boolean", "default": True},
                "ignore_array_order": {"type": "boolean", "default": False},
                "numeric_string_equivalence": {"type": "boolean", "default": False},
                "casefold_keys": {"type": "boolean", "default": False},
                "treat_missing_null_as_equal": {"type": "boolean", "default": False},
                "max_diffs": {"type": "integer", "default":    50},
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["a", "b"],
        },
    },
    "text_position": {
        "description": "Convert between byte offsets, codepoint indices, line/column positions, and UTF-16 offsets.",
        "tier": 2,
        "tags": ["text", "position", "offset", "unicode", "lsp"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "byte_offset": {"type": "integer"},
                "codepoint_index": {"type": "integer"},
                "line": {"type": "integer"},
                "column": {"type": "integer"},
                "utf16_offset": {"type": "integer"},
                "line_base": {"type": "integer", "default": 1},
                "column_base": {"type": "integer", "default": 1},
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["text"],
        },
    },
    "text_hash": {
        "description": "Compute cryptographic hashes of text for identity checking.",
        "tier": 2,
        "tags": ["text", "hash", "identity", "security"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "algorithms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Hash algorithms (sha256, sha1, md5, crc32)",
                    "default": ["sha256"],
                },
                "encoding": {"type": "string", "default": "utf-8"},
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["text"],
        },
    },
    "escape_text": {
        "description": "Escape text for various output formats.",
        "tier": 1,
        "tags": ["text", "escape", "encoding", "shell", "json", "regex"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "mode": {
                    "type": "string",
                    "enum": ["json_string", "python_string", "rust_string", "posix_shell_single", "regex_literal", "markdown_inline_code", "markdown_code_block", "html_text", "url_component"],
                },
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["text", "mode"],
        },
    },
    "unescape_text": {
        "description": "Unescape text from various formats.",
        "tier": 1,
        "tags": ["text", "escape", "encoding", "shell", "json", "regex"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "mode": {
                    "type": "string",
                    "enum": ["json_string", "python_string", "unicode_escape", "url_component"],
                },
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["text", "mode"],
        },
    },
    "identifier_analyze": {
        "description": "Classify and validate identifier naming conventions across languages.",
        "tier": 3,
        "tags": ["text", "identifier", "naming", "validation", "language"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "languages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Languages to check (python, rust, javascript, env)",
                    "default": ["python", "rust", "javascript", "env"],
                },
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["text"],
        },
    },
    "regex_finditer": {
        "description": "Find all regex matches in text with positions, line/column info, and capture groups.",
        "tier": 1,
        "tags": ["text", "regex", "search", "find", "pattern"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regular expression pattern"},
                "text": {"type": "string", "description": "Input string to search"},
                "flags": {"type": "array", "items": {"type": "string"}, "description": "Flag names (IGNORECASE, MULTILINE, DOTALL, etc.)"},
                "max_matches": {"type": "integer", "default": 100, "description": "Maximum matches to return"},
                "include_line_column": {"type": "boolean", "default": True, "description": "Include line and column info"},
                "include_groups": {"type": "boolean", "default": True, "description": "Include capture groups"},
            },
            "required": ["pattern", "text"],
        },
    },
    "regex_safety_check": {
        "description": "Heuristic check for potential catastrophic backtracking risks in regex patterns. Flags nested quantifiers, repeated alternations, ambiguous dot-star, and backreferences.",
        "tier": 1,
        "tags": ["text", "regex", "safety", "security", "backtracking"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regular expression pattern to check"},
            },
            "required": ["pattern"],
        },
    },
    "validate_schema_light": {
        "description": "Validate JSON against a simple schema format with type, required, enum, pattern, and nested constraints.",
        "tier": 3,
        "tags": ["validation", "json", "schema", "structured-data"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "JSON document to validate"},
                "schema": {"type": "object", "description": "Schema to validate against"},
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["text", "schema"],
        },
    },
    "path_normalize": {
        "description": "Normalize a path using posixpath or ntpath semantics. Collapse dot segments, resolve components.",
        "tier": 0,
        "tags": ["text", "path", "filesystem", "normalize"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path string to normalize"},
                "platform": {"type": "string", "enum": ["posix", "windows"], "default": "posix", "description": "Platform semantics to use"},
                "collapse_dot_segments": {"type": "boolean", "default": True, "description": "Collapse dot and dot-dot segments"},
                "preserve_trailing_separator": {"type": "boolean", "default": False, "description": "Preserve trailing separator"},
            },
            "required": ["path"],
        },
    },
    "path_analyze": {
        "description": "Analyze path components, extensions, hidden status, and traversal without filesystem access.",
        "tier": 2,
        "tags": ["text", "path", "filesystem", "lexical"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "style": {"type": "string", "enum": ["auto", "posix", "windows"], "default": "auto"},
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["path"],
        },
    },
    "path_compare": {
        "description": "Compare two paths under explicit normalization rules: separator normalization, dot-segment collapsing, and optional case-insensitive comparison.",
        "tier": 2,
        "tags": ["text", "path", "filesystem", "comparison"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "left": {"type": "string", "description": "First path string"},
                "right": {"type": "string", "description": "Second path string"},
                "platform": {"type": "string", "enum": ["posix", "windows"], "default": "posix", "description": "Platform semantics"},
                "case_sensitive": {"type": "boolean", "default": True, "description": "Case-sensitive comparison"},
                "normalize_separators": {"type": "boolean", "default": True, "description": "Normalize path separators"},
                "collapse_dot_segments": {"type": "boolean", "default": True, "description": "Collapse . and .. segments"},
            },
            "required": ["left", "right"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "equal": {"type": "boolean", "description": "Whether paths are equal under normalization"},
                "left_normalized": {"type": "string", "description": "Normalized left path"},
                "right_normalized": {"type": "string", "description": "Normalized right path"},
                "differences": {"type": "array", "description": "List of differences found"},
                "findings": {"type": "array", "description": "Normalization notes"},
            },
        },
    },
    "path_scope_check": {
        "description": "Determine whether a target path remains lexically inside a declared root. Lexical only, does not resolve symlinks.",
        "tier": 2,
        "tags": ["text", "path", "filesystem", "security", "scope"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "root": {"type": "string", "description": "Root directory path"},
                "target": {"type": "string", "description": "Target path to check"},
                "platform": {"type": "string", "enum": ["posix", "windows"], "default": "posix", "description": "Platform semantics"},
                "case_sensitive": {"type": "boolean", "default": True, "description": "Case-sensitive comparison"},
            },
            "required": ["root", "target"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "inside_root": {"type": "boolean", "description": "Whether target is lexically inside root"},
                "root_normalized": {"type": "string", "description": "Normalized root path"},
                "target_normalized": {"type": "string", "description": "Normalized target path"},
                "relative_path": {"type": "string", "description": "Relative path from root to target (if inside)"},
                "escapes_via_dotdot": {"type": "boolean", "description": "Whether target contains parent traversal"},
                "absolute_target": {"type": "string", "description": "Absolute form of target"},
                "findings": {"type": "array", "description": "Analysis notes"},
            },
        },
    },
    "json_shape": {
        "description": "Analyze the structure of a JSON document without returning values. Shows type, keys, and nested structure with configurable depth limits.",
        "tier": 3,
        "tags": ["json", "structured-data", "shape", "schema"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "JSON document string to analyze"},
                "max_depth": {"type": "integer", "default": 4, "description": "Maximum depth for nested structure"},
                "max_keys": {"type": "integer", "default": 100, "description": "Maximum keys to show per object"},
                "max_array_items": {"type": "integer", "default": 5, "description": "Maximum array item previews"},
            },
            "required": ["text"],
        },
    },
    "text_window": {
        "description": "Get a window around a position in text with context lines. Shows line at position with surrounding context, position metrics, and character details.",
        "tier": 1,
        "tags": ["text", "position", "context", "unicode", "window"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input string to analyze"},
                "position": {
                    "type": "object",
                    "description": "Position specification with kind and value",
                    "properties": {
                        "kind": {"type": "string", "enum": ["byte_offset", "codepoint_index", "grapheme_index", "line_column"]},
                        "value": {"type": "integer", "description": "Value for byte_offset, codepoint_index, or grapheme_index"},
                        "byte_offset": {"type": "integer", "description": "UTF-8 byte offset (alternative to value)"},
                        "codepoint_index": {"type": "integer", "description": "Codepoint index (alternative to value)"},
                        "grapheme_index": {"type": "integer", "description": "Grapheme index (alternative to value)"},
                        "line": {"type": "integer", "description": "Line number for line_column kind"},
                        "column": {"type": "integer", "description": "Column number for line_column kind"},
                        "line_base": {"type": "integer", "default": 1, "description": "Base for line numbers (1 for 1-based)"},
                        "column_base": {"type": "integer", "default": 1, "description": "Base for column numbers (1 for 1-based)"},
                    },
                    "required": ["kind"],
                },
                "context_lines": {"type": "integer", "default": 2, "description": "Number of context lines before and after"},
                "include_visible_repr": {"type": "boolean", "default": True, "description": "Include visible representation of the line"},
            },
            "required": ["text", "position"],
        },
    },
    "json_canonicalize": {
        "description": "Canonicalize JSON with deterministic formatting, key ordering, duplicate key detection, and stable hashes.",
        "tier": 1,
        "tags": ["json", "canonical", "hash", "deterministic", "format"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input JSON string to canonicalize"},
                "sort_keys": {"type": "boolean", "default": True, "description": "Sort object keys alphabetically"},
                "indent": {"type": "integer", "description": "Indentation spaces (None for minified)"},
                "ensure_ascii": {"type": "boolean", "default": False, "description": "Use ASCII escaping for non-ASCII characters"},
                "detect_duplicate_keys": {"type": "boolean", "default": True, "description": "Report duplicate keys in the input"},
                "trailing_newline": {"type": "boolean", "default": False, "description": "Add a trailing newline to the canonical form"},
            },
            "required": ["text"],
        },
    },
    "json_query": {
        "description": "Extract a value from JSON using RFC 6901 JSON Pointer. Navigate nested objects and arrays.",
        "tier": 1,
        "tags": ["json", "pointer", "extraction", "query", "rfc6901"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "JSON document string"},
                "pointer": {"type": "string", "default": "", "description": "RFC 6901 JSON Pointer path (e.g., /foo/bar/0)"},
            },
            "required": ["text"],
        },
    },
    "glob_match": {
        "description": "Match a glob pattern against a path with explicit semantics: * matches within one segment, ** matches zero or more segments, ? matches one char. Python fnmatch limitations around ** are documented.",
        "tier": 1,
        "tags": ["text", "glob", "pattern", "path", "wildcard"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern to match (e.g., src/**/*.rs)"},
                "path": {"type": "string", "description": "Path string to match against"},
                "platform": {"type": "string", "enum": ["posix", "windows"], "default": "posix", "description": "Path platform"},
                "case_sensitive": {"type": "boolean", "default": True, "description": "Case-sensitive matching"},
            },
            "required": ["pattern", "path"],
        },
    },
    "text_fingerprint": {
        "description": "Compute a deterministic SHA-256 fingerprint of text with canonicalization options for Unicode normalization, newline style, casefold, and final newline trimming.",
        "tier": 0,
        "tags": ["text", "hash", "fingerprint", "sha256", "identity", "canonicalization"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input string to fingerprint"},
                "unicode": {"type": "string", "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"], "default": "raw", "description": "Unicode normalization form"},
                "newline": {"type": "string", "enum": ["raw", "LF"], "default": "raw", "description": "Newline normalization"},
                "trim_final_newline": {"type": "boolean", "default": False, "description": "Remove trailing newline before hashing"},
                "casefold": {"type": "boolean", "default": False, "description": "Apply casefolding before hashing"},
            },
            "required": ["text"],
        },
    },
    "identifier_inspect": {
        "description": "Inspect identifiers for validity and collisions. Detects confusables, mixed scripts, normalization issues, and casefold collisions across a list of identifiers.",
        "tier": 1,
        "tags": ["text", "identifier", "collision", "confusable", "security", "validation"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "identifiers": {"type": "array", "items": {"type": "string"}, "description": "List of identifier strings to inspect"},
                "language": {"type": "string", "enum": ["generic", "python", "rust", "javascript", "typescript", "json_key"], "default": "generic", "description": "Language for validation"},
                "normalization": {"type": "string", "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"], "default": "NFC", "description": "Unicode normalization form"},
                "casefold": {"type": "boolean", "default": False, "description": "Apply casefolding for collision detection"},
                "check_confusables": {"type": "boolean", "default": True, "description": "Check for confusable characters"},
            },
            "required": ["identifiers"],
        },
    },
    "version_compare": {
        "description": "Compare two version strings with explicit scheme. Supports semver (major.minor.patch), loose (numeric parts), and deferred pep440.",
        "tier": 2,
        "tags": ["version", "semver", "comparison"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "a": {"type": "string", "description": "First version string"},
                "b": {"type": "string", "description": "Second version string"},
                "scheme": {"type": "string", "enum": ["semver", "pep440", "loose"], "default": "semver", "description": "Version scheme"},
            },
            "required": ["a", "b"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "comparison": {"type": "integer", "description": "Comparison result: -1 (a < b), 0 (equal), 1 (a > b)"},
                "valid": {"type": "boolean", "description": "Whether versions are valid for the scheme"},
                "scheme": {"type": "string"},
                "summary": {"type": "string"},
            },
        },
    },
    "toml_shape": {
        "description": "Analyze the structure of a TOML document: top-level keys, tables, and nesting hierarchy.",
        "tier": 2,
        "tags": ["toml", "structure", "shape", "config", "validation"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "TOML document string"},
                "max_tables": {"type": "integer", "default": 100, "description": "Maximum tables to return"},
                "detail": {"type": "string", "enum": ["summary", "normal", "full"], "default": "normal"},
            },
            "required": ["text"],
        },
    },
    "list_dedupe": {
        "description": "Remove duplicates from a list while preserving order. Supports Unicode normalization and casefolding.",
        "tier": 1,
        "tags": ["list", "dedupe", "unique", "normalization"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "string"}, "description": "List of strings to dedupe"},
                "normalization": {"type": "string", "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"], "default": "NFC"},
                "casefold": {"type": "boolean", "default": False, "description": "Apply casefolding before comparison"},
                "stable": {"type": "boolean", "default": True, "description": "Preserve first occurrence order"},
            },
            "required": ["items"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "string"}},
                "original_count": {"type": "integer"},
                "deduped_count": {"type": "integer"},
                "duplicates_removed": {"type": "integer"},
            },
        },
    },
    "list_sort": {
        "description": "Sort a list of strings with Unicode normalization and casefold support.",
        "tier": 1,
        "tags": ["list", "sort", "order", "normalization"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "string"}, "description": "List of strings to sort"},
                "normalization": {"type": "string", "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"], "default": "NFC"},
                "casefold": {"type": "boolean", "default": False, "description": "Apply casefolding for sorting"},
                "reverse": {"type": "boolean", "default": False, "description": "Sort in descending order"},
                "stable": {"type": "boolean", "default": True, "description": "Preserve original order for equal elements"},
            },
            "required": ["items"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "items": {"type": "string"}},
                "original_count": {"type": "integer"},
                "sorted_count": {"type": "integer"},
            },
        },
    },
    "text_replace_check": {
        "description": "Check whether a text replacement would apply cleanly before an agent attempts to edit. Reports match count, positions, ambiguity, and optional preview of before/after.",
        "tier": 1,
        "tags": ["text", "replace", "edit", "safety", "check"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Source text to search in"},
                "old": {"type": "string", "description": "Text to find"},
                "new": {"type": "string", "description": "Replacement text"},
                "mode": {
                    "type": "string",
                    "enum": ["exact", "nfc", "nfkc", "casefold", "whitespace_collapse"],
                    "default": "exact",
                    "description": "Matching mode",
                },
                "expected_count": {
                    "type": "integer",
                    "description": "Expected number of matches (optional)",
                },
                "allow_multiple": {
                    "type": "boolean",
                    "default": False,
                    "description": "If False and more than one match, add a finding",
                },
                "newline_policy": {
                    "type": "string",
                    "enum": ["preserve", "normalize_lf", "normalize_crlf"],
                    "default": "preserve",
                    "description": "How to handle newlines",
                },
                "return_preview": {
                    "type": "boolean",
                    "default": False,
                    "description": "If True, include before/after text previews",
                },
                "max_preview_chars": {
                    "type": "integer",
                    "default": 2000,
                    "description": "Maximum characters in preview output",
                },
            },
            "required": ["text", "old", "new"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "match_count": {"type": "integer", "description": "Number of matches found"},
                "unique_match": {"type": "boolean", "description": "True if exactly one match"},
                "expected_count_met": {"type": "boolean", "description": "True if match count matches expected_count"},
                "would_change": {"type": "boolean", "description": "True if replacement would change text"},
                "positions": {"type": "array", "description": "Match positions with byte offsets and line/column"},
                "changed_text_fingerprint": {"type": "string", "description": "SHA-256 fingerprint of changed text"},
                "newline_style_before": {"type": "string"},
                "newline_style_after": {"type": "string"},
                "preview_before": {"type": "string"},
                "preview_after": {"type": "string"},
                "findings": {"type": "array", "description": "Warnings and info messages"},
            },
        },
    },
    "line_range_extract": {
        "description": "Extract exact line ranges from text and return stable offsets, byte positions, line counts, and optional fingerprint.",
        "tier": 1,
        "tags": ["text", "line", "range", "extract", "offset"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input text"},
                "start_line": {"type": "integer", "description": "First line to extract"},
                "end_line": {"type": "integer", "description": "Last line to extract (inclusive)"},
                "line_base": {
                    "type": "integer",
                    "default": 1,
                    "description": "Base for line numbers (1 for 1-based, 0 for 0-based)",
                },
                "include_line_numbers": {
                    "type": "boolean",
                    "default": False,
                    "description": "Include line number in each line dict",
                },
                "include_fingerprint": {
                    "type": "boolean",
                    "default": True,
                    "description": "Compute SHA-256 fingerprint of extracted text",
                },
            },
            "required": ["text", "start_line", "end_line"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "line_count_total": {"type": "integer", "description": "Total line count in input"},
                "start_line": {"type": "integer"},
                "end_line": {"type": "integer"},
                "valid_range": {"type": "boolean", "description": "True if range is within bounds"},
                "text": {"type": "string", "description": "Extracted text (lines joined by LF)"},
                "lines": {"type": "array", "description": "Structured line list"},
                "byte_start": {"type": "integer", "description": "UTF-8 byte offset of start"},
                "byte_end": {"type": "integer", "description": "UTF-8 byte offset of end"},
                "char_start": {"type": "integer", "description": "Codepoint index of start"},
                "char_end": {"type": "integer", "description": "Codepoint index of end"},
                "newline_style": {"type": "string"},
                "ends_with_newline": {"type": "boolean"},
                "fingerprint": {"type": "string"},
                "findings": {"type": "array"},
            },
        },
    },
    "line_range_compare": {
        "description": "Compare a line range from two text inputs with exact, trailing-whitespace-ignoring, or newline-normalizing comparison.",
        "tier": 2,
        "tags": ["text", "line", "range", "compare", "diff"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "left_text": {"type": "string", "description": "First text input"},
                "right_text": {"type": "string", "description": "Second text input"},
                "start_line": {"type": "integer", "description": "First line to compare"},
                "end_line": {"type": "integer", "description": "Last line to compare (inclusive)"},
                "line_base": {
                    "type": "integer",
                    "default": 1,
                    "description": "Base for line numbers",
                },
                "comparison_mode": {
                    "type": "string",
                    "enum": ["exact", "ignore_trailing_whitespace", "normalize_newlines"],
                    "default": "exact",
                    "description": "Comparison mode",
                },
            },
            "required": ["left_text", "right_text", "start_line", "end_line"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "equal": {"type": "boolean", "description": "True if ranges are equal under the chosen mode"},
                "left_fingerprint": {"type": "string", "description": "SHA-256 fingerprint of left range"},
                "right_fingerprint": {"type": "string", "description": "SHA-256 fingerprint of right range"},
                "diff_summary": {"type": "string", "description": "Human-readable diff summary"},
                "first_difference": {"type": "object", "description": "First differing line (if any)"},
            },
        },
    },
    "shell_split": {
        "description": "Parse a shell-like command string into argv tokens and report risky lexical features (pipes, redirections, command substitution, variable expansion, globs, control operators). Lexical POSIX-like parsing only, not full shell evaluation.",
        "tier": 2,
        "tags": ["shell", "argv", "parsing", "security", "sanity"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command string to parse",
                },
                "shell": {
                    "type": "string",
                    "enum": ["posix"],
                    "default": "posix",
                    "description": "Shell dialect (only posix is supported)",
                },
                "detect_risky_features": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to detect risky lexical features",
                },
            },
            "required": ["command"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "parse_ok": {"type": "boolean", "description": "True if the command parsed successfully"},
                "argv": {"type": "array", "items": {"type": "string"}, "description": "Parsed argument tokens"},
                "argc": {"type": "integer", "description": "Number of arguments"},
                "features": {
                    "type": "object",
                    "description": "Detected risky features",
                    "properties": {
                        "has_pipe": {"type": "boolean"},
                        "has_redirection": {"type": "boolean"},
                        "has_command_substitution": {"type": "boolean"},
                        "has_variable_expansion": {"type": "boolean"},
                        "has_glob_pattern": {"type": "boolean"},
                        "has_control_operator": {"type": "boolean"},
                        "has_unbalanced_quotes": {"type": "boolean"},
                    },
                },
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Analysis notes and warnings"},
            },
        },
    },
    "shell_quote_join": {
        "description": "Safely quote a list of argv tokens into a POSIX-like shell string. Verifies round-trip safety with shell_split.",
        "tier": 2,
        "tags": ["shell", "argv", "quoting", "safety"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "argv": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of argument strings to join",
                },
                "shell": {
                    "type": "string",
                    "enum": ["posix"],
                    "default": "posix",
                    "description": "Shell dialect (only posix is supported)",
                },
            },
            "required": ["argv"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Safely quoted command string"},
                "roundtrip_ok": {"type": "boolean", "description": "True if shell_split(quote_join(argv)) produces equivalent argv"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Analysis notes"},
            },
        },
    },
    "argv_compare": {
        "description": "Compare two command strings or argv lists by parsed argv tokens rather than raw text. Supports command strings, pre-parsed argv lists, or both.",
        "tier": 2,
        "tags": ["shell", "argv", "comparison", "sanity"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "left_command": {
                    "type": "string",
                    "description": "Left command string to parse and compare",
                },
                "right_command": {
                    "type": "string",
                    "description": "Right command string to parse and compare",
                },
                "left_argv": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Left pre-parsed argv list",
                },
                "right_argv": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Right pre-parsed argv list",
                },
                "shell": {
                    "type": "string",
                    "enum": ["posix"],
                    "default": "posix",
                    "description": "Shell dialect (only posix is supported)",
                },
            },
            "required": [],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "argv_equal": {"type": "boolean", "description": "True if parsed argv lists are identical"},
                "left_argv": {"type": "array", "items": {"type": "string"}, "description": "Resolved left argv"},
                "right_argv": {"type": "array", "items": {"type": "string"}, "description": "Resolved right argv"},
                "first_difference": {"type": "integer", "description": "Index of first differing token, or null if equal"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Analysis notes"},
            },
        },
    },
    "markdown_structure": {
        "description": "Parse Markdown structure with a deterministic line scanner: headings (level, text, slug), code fences (language, open/close state), links (visible vs target mismatch), HTML comments, frontmatter detection, and table detection. Not a full CommonMark parser.",
        "tier": 2,
        "tags": ["markdown", "structure", "headings", "code-fences", "links", "frontmatter"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Markdown text to analyze"},
                "include_sections": {"type": "boolean", "default": True, "description": "Include heading detection"},
                "include_links": {"type": "boolean", "default": True, "description": "Include link detection"},
                "include_code_fences": {"type": "boolean", "default": True, "description": "Include code fence detection"},
                "include_html_comments": {"type": "boolean", "default": True, "description": "Include HTML comment detection"},
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "headings": {"type": "array", "description": "Headings with level, text, line, slug"},
                "code_fences": {"type": "array", "description": "Code fences with language, lines, closed state"},
                "links": {"type": "array", "description": "Links with visible text, target, mismatch flags"},
                "html_comments": {"type": "array", "description": "HTML comments with text and position"},
                "frontmatter": {"type": "object", "description": "Frontmatter detection (present, format, line range)"},
                "tables_detected": {"type": "boolean", "description": "Whether Markdown tables were detected"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Warnings and findings"},
            },
        },
    },
    "code_fence_extract": {
        "description": "Extract fenced code blocks from Markdown with exact line ranges, optional language filter, content, and SHA-256 fingerprints. Reports unclosed fences.",
        "tier": 2,
        "tags": ["markdown", "code-fences", "extraction", "fingerprint"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Markdown text to scan"},
                "language": {"type": "string", "description": "Optional language filter (case-insensitive)"},
                "include_content": {"type": "boolean", "default": True, "description": "Include block content in output"},
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "blocks": {"type": "array", "description": "Extracted code blocks with index, language, lines, content, fingerprint"},
                "unclosed_fences": {"type": "array", "description": "Unclosed code fences found"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Warnings and findings"},
            },
        },
    },
    "dotenv_validate": {
        "description": "Validate .env-style key=value configuration text. Detects invalid keys, duplicate keys, missing quotes, and variable expansion syntax. Line-by-line parser, no shell evaluation.",
        "tier": 2,
        "tags": ["validation", "config", "env", "dotenv"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": ".env file content to validate"},
                "allow_export": {"type": "boolean", "default": True, "description": "Allow export KEY=VALUE syntax"},
                "key_pattern": {"type": "string", "default": "^[A-Za-z_][A-Za-z0-9_]*$", "description": "Regex pattern keys must match"},
                "duplicate_policy": {"type": "string", "enum": ["warn", "error", "allow"], "default": "warn", "description": "How to handle duplicate keys"},
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "parse_ok": {"type": "boolean", "description": "True if no parse errors found"},
                "entries": {"type": "array", "description": "Parsed entries with key, value, quote_style, line"},
                "duplicates": {"type": "array", "description": "Duplicate key entries with line numbers"},
                "invalid_lines": {"type": "array", "description": "Lines that failed to parse"},
                "requires_quoting": {"type": "array", "description": "Keys whose values contain spaces and should be quoted"},
                "contains_expansion_syntax": {"type": "array", "description": "Keys with ${VAR} or $VAR expansion syntax"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Human-readable findings"},
            },
        },
    },
    "ini_validate": {
        "description": "Validate simple INI-style configuration files. Supports [section] headers, key=value and key:value lines, comments. Detects duplicate sections, duplicate keys, and malformed lines.",
        "tier": 2,
        "tags": ["validation", "config", "ini"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "INI file content to validate"},
                "duplicate_policy": {"type": "string", "enum": ["warn", "error", "allow"], "default": "warn", "description": "How to handle duplicate keys/sections"},
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "parse_ok": {"type": "boolean", "description": "True if no parse errors found"},
                "sections": {"type": "array", "description": "Ordered list of section names"},
                "keys_by_section": {"type": "object", "description": "Keys grouped by section"},
                "duplicates": {"type": "array", "description": "Duplicate keys/sections with line numbers"},
                "invalid_lines": {"type": "array", "description": "Lines that failed to parse"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Human-readable findings"},
            },
        },
    },
    "patch_apply_check": {
        "description": "Validate and simulate a unified diff against provided in-memory files/text without touching the filesystem. Reports parse status, application success, failed hunks with context, and optional result fingerprint.",
        "tier": 2,
        "tags": ["patch", "diff", "unified", "validation", "apply"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "original_text": {
                    "type": "string",
                    "description": "The original source text to apply the patch to",
                },
                "patch_text": {
                    "type": "string",
                    "description": "The unified diff patch text",
                },
                "strict": {
                    "type": "boolean",
                    "default": True,
                    "description": "If True, context lines must match exactly",
                },
                "return_result_fingerprint": {
                    "type": "boolean",
                    "default": True,
                    "description": "If True, compute SHA-256 fingerprint of the result",
                },
                "return_result_text": {
                    "type": "boolean",
                    "default": False,
                    "description": "If True, include the resulting text (bounded to 50000 chars)",
                },
            },
            "required": ["original_text", "patch_text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "patch_parse_ok": {"type": "boolean", "description": "True if patch parsed successfully"},
                "applies": {"type": "boolean", "description": "True if all hunks applied cleanly"},
                "hunks_total": {"type": "integer", "description": "Total number of hunks in patch"},
                "hunks_applied": {"type": "integer", "description": "Number of hunks that applied successfully"},
                "hunks_failed": {"type": "integer", "description": "Number of hunks that failed to apply"},
                "failed_hunks": {
                    "type": "array",
                    "description": "Details of each failed hunk",
                    "items": {
                        "type": "object",
                        "properties": {
                            "hunk_index": {"type": "integer"},
                            "old_start": {"type": "integer"},
                            "old_count": {"type": "integer"},
                            "expected_context": {"type": "array", "items": {"type": "string"}},
                            "actual_context": {"type": "array", "items": {"type": "string"}},
                            "reason": {"type": "string"},
                        },
                    },
                },
                "affected_line_ranges": {
                    "type": "array",
                    "description": "Line ranges affected by successful hunks",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "integer"},
                            "end": {"type": "integer"},
                        },
                    },
                },
                "newline_style_before": {"type": "string", "description": "Newline style in original text"},
                "newline_style_after": {"type": "string", "description": "Newline style in result text"},
                "result_fingerprint": {"type": "string", "description": "SHA-256 of the result text"},
                "result_text": {"type": ["string", "null"], "description": "Resulting text if requested"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Analysis notes and warnings"},
            },
        },
    },
    "patch_summary": {
        "description": "Summarize a unified diff without applying it. Reports file counts, hunk counts, additions, deletions, renames, and line ranges by file.",
        "tier": 2,
        "tags": ["patch", "diff", "unified", "summary", "statistics"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "patch_text": {
                    "type": "string",
                    "description": "The unified diff text to summarize",
                },
            },
            "required": ["patch_text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "files_changed": {"type": "integer", "description": "Number of files changed"},
                "hunks_total": {"type": "integer", "description": "Total number of hunks across all files"},
                "additions": {"type": "integer", "description": "Total number of added lines"},
                "deletions": {"type": "integer", "description": "Total number of deleted lines"},
                "renames_detected": {
                    "type": "array",
                    "description": "Detected file renames",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                        },
                    },
                },
                "binary_patch_detected": {"type": "boolean", "description": "True if binary patch content detected"},
                "line_ranges_by_file": {
                    "type": "object",
                    "description": "Line ranges affected per file",
                    "additionalProperties": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "start": {"type": "integer"},
                                "end": {"type": "integer"},
                            },
                        },
                    },
                },
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Analysis notes and warnings"},
            },
        },
    },
    "unicode_policy_check": {
        "description": "Apply a named deterministic Unicode safety policy to input text. Policies include identifier_strict (mixed scripts, bidi, confusables), filename_safe (control chars, path separators, reserved names), source_code, human_text (warn-only), json_key, and domain_like.",
        "tier": 2,
        "tags": ["text", "unicode", "policy", "security", "validation"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input text to check"},
                "policy": {
                    "type": "string",
                    "enum": ["identifier_strict", "filename_safe", "source_code", "human_text", "json_key", "domain_like"],
                    "description": "Policy to apply",
                },
                "normalization": {
                    "type": "string",
                    "enum": ["raw", "NFC", "NFD", "NFKC", "NFKD"],
                    "default": None,
                    "description": "Normalization form (default: policy-specific)",
                },
            },
            "required": ["text", "policy"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "pass": {"type": "boolean", "description": "True if text passes the policy (no errors)"},
                "policy": {"type": "string", "description": "Policy name that was applied"},
                "normalized_form": {"type": "string", "description": "Text after normalization"},
                "findings": {
                    "type": "array",
                    "description": "Policy findings with rule, severity, and message",
                    "items": {
                        "type": "object",
                        "properties": {
                            "rule": {"type": "string"},
                            "severity": {"type": "string"},
                            "message": {"type": "string"},
                        },
                    },
                },
                "summary": {"type": "string", "description": "Human-readable summary"},
            },
        },
    },
    "canonicalize_text": {
        "description": "Apply a named text canonicalization profile. Profiles include source_file_identity (NFC + LF + newline), identifier_compare (NFC + casefold), human_label_compare (NFC + casefold + whitespace collapse), json_key_compare (NFC + casefold), and path_segment_compare (NFC + lowercase + LF).",
        "tier": 2,
        "tags": ["text", "unicode", "canonicalization", "normalization", "identity"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Input text to canonicalize"},
                "profile": {
                    "type": "string",
                    "enum": ["source_file_identity", "identifier_compare", "human_label_compare", "json_key_compare", "path_segment_compare"],
                    "description": "Canonicalization profile to apply",
                },
                "return_mapping": {
                    "type": "boolean",
                    "default": False,
                    "description": "If True, include a character mapping of changes",
                },
            },
            "required": ["text", "profile"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Canonicalized text"},
                "changed": {"type": "boolean", "description": "True if text was modified"},
                "operations_applied": {"type": "array", "description": "List of operations applied"},
                "fingerprint_before": {"type": "string", "description": "SHA-256 of original text"},
                "fingerprint_after": {"type": "string", "description": "SHA-256 of canonicalized text"},
                "mapping": {"type": "array", "description": "Character mapping if return_mapping was True"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Analysis notes and warnings"},
            },
        },
    },
    "identifier_table_inspect": {
        "description": "Inspect a table of identifiers for casefold collisions, normalization collisions, confusable/near-collisions, style variants, reserved keyword hits, and mixed naming style groups. Accepts structured entries with name, kind, file, and line metadata.",
        "tier": 3,
        "tags": ["text", "identifier", "collision", "naming", "style", "reserved", "validation"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "identifiers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Identifier name (required)"},
                            "kind": {"type": "string", "description": "Optional kind/category"},
                            "file": {"type": "string", "description": "Source file path"},
                            "line": {"type": "integer", "description": "Line number"},
                        },
                        "required": ["name"],
                    },
                    "description": "List of identifier entries to inspect",
                },
                "language": {
                    "type": "string",
                    "enum": ["generic", "python", "rust", "javascript", "typescript", "json_key"],
                    "default": "python",
                    "description": "Target language for reserved keyword checking",
                },
                "checks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Subset of checks: casefold, normalization, confusable, style, reserved, mixed_style",
                },
            },
            "required": ["identifiers"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "count": {"type": "integer", "description": "Number of identifiers inspected"},
                "collisions": {
                    "type": "array",
                    "description": "Detected collisions",
                    "items": {
                        "type": "object",
                        "properties": {
                            "kind": {"type": "string"},
                            "names": {"type": "array", "items": {"type": "string"}},
                            "detail": {"type": "string"},
                        },
                    },
                },
                "reserved_keyword_hits": {
                    "type": "array",
                    "description": "Identifiers matching reserved keywords",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "language": {"type": "string"},
                            "file": {"type": "string"},
                            "line": {"type": "integer"},
                        },
                    },
                },
                "mixed_style_groups": {
                    "type": "array",
                    "description": "Groups with mixed naming styles",
                    "items": {
                        "type": "object",
                        "properties": {
                            "stripped": {"type": "string"},
                            "names": {"type": "array", "items": {"type": "string"}},
                            "styles": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                },
                "findings": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    "version_constraint_check": {
        "description": "Check whether a version satisfies a constraint under a declared versioning scheme (semver or cargo). Supports comparison operators, caret, tilde, wildcard, range, and comma-separated constraints.",
        "tier": 3,
        "tags": ["version", "semver", "cargo", "constraint", "satisfiability"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "version": {
                    "type": "string",
                    "description": "Version string to check (e.g., '1.2.3', '0.5.0-beta.1')",
                },
                "constraint": {
                    "type": "string",
                    "description": "Version constraint (e.g., '>=1.0,<2.0', '^1.2.3', '~0.5', '1.*')",
                },
                "scheme": {
                    "type": "string",
                    "enum": ["semver", "cargo"],
                    "default": "semver",
                    "description": "Versioning scheme to use for parsing and evaluation",
                },
            },
            "required": ["version", "constraint"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "satisfies": {"type": "boolean", "description": "Whether the version satisfies the constraint"},
                "parsed_version": {"type": "object", "description": "Parsed version components"},
                "parsed_constraint": {"type": "object", "description": "Parsed constraint components"},
                "scheme": {"type": "string", "description": "Versioning scheme used"},
                "explanation": {"type": "string", "description": "Human-readable explanation"},
                "findings": {"type": "array", "items": {"type": "string"}, "description": "Analysis notes and warnings"},
            },
        },
    },
    "cargo_toml_inspect": {
        "description": "Inspect Cargo.toml text without network or filesystem access. Reports package metadata, workspace configuration, dependency forms (version/path/git/workspace), path dependencies, suspicious or confusable dependency names, and structural findings.",
        "tier": 3,
        "tags": ["rust", "cargo", "toml", "dependencies", "workspace", "inspection"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The Cargo.toml content to inspect",
                },
                "check_workspace": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to analyze [workspace] section",
                },
                "check_dependencies": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether to analyze dependency sections",
                },
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "parse_ok": {"type": "boolean", "description": "Whether TOML parsed successfully"},
                "package": {
                    "type": "object",
                    "description": "Package metadata from [package] section",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                        "edition": {"type": "string"},
                        "license": {"type": "string"},
                        "repository": {"type": "string"},
                        "readme": {"type": "string"},
                    },
                },
                "workspace": {
                    "type": "object",
                    "description": "Workspace section information",
                    "properties": {
                        "present": {"type": "boolean"},
                        "members": {"type": "array", "items": {"type": "string"}},
                        "exclude": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "dependencies": {
                    "type": "object",
                    "description": "Dependencies by section",
                },
                "path_dependencies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Extracted path dependency values",
                },
                "suspicious_dependency_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dependency names with suspicious patterns",
                },
                "duplicate_or_confusable_dependency_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dependency names that normalize to the same form",
                },
                "findings": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Structural findings and warnings",
                },
            },
        },
    },
    "prompt_input_inspect": {
        "description": "Deterministically inspect text for red flags that may influence agents or humans unexpectedly. Detects hidden Unicode characters, bidirectional controls, HTML comments, Markdown link mismatches, ANSI escapes, terminal controls, base64-like blobs, instruction-like phrases, and very long minified lines. This is NOT a prompt-injection detector -- it reports observable features only, not intent.",
        "tier": 2,
        "tags": ["text", "security", "inspection", "prompt", "unicode", "hidden"],
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to inspect for red flags",
                },
                "checks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Subset of checks to run: unicode_hidden, bidi, html_comments, markdown_links, ansi_escapes, terminal_controls, base64_like_blobs, instruction_phrases, long_minified_lines",
                },
                "phrase_patterns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional literal strings or safe regexes to detect as instruction-like phrases",
                },
            },
            "required": ["text"],
        },
        "outputSchema": {
            "type": "object",
            "properties": {
                "findings": {
                    "type": "array",
                    "description": "Structured findings with code, severity, message, span, and details",
                    "items": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "severity": {"type": "string"},
                            "message": {"type": "string"},
                            "span": {"type": "object"},
                            "details": {"type": "object"},
                        },
                    },
                },
                "summary": {"type": "string", "description": "Human-readable summary"},
                "risk_score": {"type": "integer", "description": "Deterministic risk score"},
                "recommended_next_tool": {
                    "type": ["string", "array"],
                    "description": "Recommended follow-up tool(s)",
                },
                "text_length": {"type": "integer", "description": "Input text length"},
                "checks_run": {"type": "array", "items": {"type": "string"}, "description": "Checks that were executed"},
            },
        },
    },
}
