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
        "tier": 2,
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
        "tier": 1,
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
        "tier": 2,
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
        "tier": 2,
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
        "tier": 2,
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
        "tier": 2,
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
        "tier": 2,
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
        "tier": 1,
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
        "tier": 1,
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
}
