"""
Low-level Unicode text primitives.

These primitives are deterministic, independently testable, and do not
perform semantic interpretation or call LLMs.
"""

from __future__ import annotations

# Re-export path_tools
from .path_tools import (
    PathAnalyzeResult,
    PathNormalizeResult,
    path_analyze,
    path_normalize,
)

# Re-export primitives
from .primitives import (
    CodepointInfo,
    InvisibleCharInfo,
    MeasureBasic,
    casefold_text,
    codepoints,
    count_graphemes,
    truncate_to_grapheme,
    find_invisibles,
    measure_basic,
    normalize_unicode,
    normalized_equal,
    raw_equal,
    utf8_bytes,
    visible_repr,
)

# Re-export synthesis
from .synthesis import (
    CountCharsResult,
    ExplainDiffResult,
    InspectTextResult,
    MeasureTextResult,
    TextEqualResult,
    count_chars,
    explain_diff,
    inspect_text,
    list_compare,
    measure_text,
    text_equal,
)

# Re-export unicode_tools
from .unicode_tools import (
    ConfusableInfo,
    MixedScriptsResult,
    ScriptInfo,
    detect_confusables,
    detect_mixed_scripts,
    unicode_script,
    unicode_scripts,
    confusables_count,
    reverse_confusables,
)

# Re-export validate
from .validate import (
    CheckBracketsResult,
    JsonCompareDiff,
    JsonCompareResult,
    JsonExtractResult,
    JsonShapeKey,
    JsonShapeResult,
    RegexFindIterMatch,
    RegexFindIterResult,
    RegexSafetyFinding,
    RegexSafetyResult,
    RegexTestResult,
    TomlShapeResult,
    ValidateJsonResult,
    ValidateSchemaLightResult,
    ValidateTomlResult,
    VersionCompareResult,
    check_brackets,
    json_compare,
    json_extract,
    json_shape,
    regex_finditer,
    regex_safety_check,
    regex_test,
    validate_json,
    validate_schema_light,
    validate_toml_text,
    toml_shape,
    version_compare,
    list_dedupe,
    list_sort,
)

# Re-export glob
from .glob import (
    GlobMatchResult,
    glob_match,
)

# Re-export transform
from .transform import (
    EscapeTextResult,
    RemovedChar,
    TextTransformResult,
    TextFingerprintResult,
    UnescapeTextResult,
    escape_text,
    text_hash,
    text_transform,
    text_fingerprint,
    unescape_text,
)

# Re-export diff
from .diff import (
    CommonPrefixSuffix,
    DiffSpan,
    FirstDiff,
    common_prefix_suffix,
    diff_spans,
    first_diff,
    levenshtein_distance,
    longest_common_subsequence,
)

# Re-export position
from .position import (
    TextPositionResult,
    text_position,
)

# Re-export measure
from .measure import (
    CharCategoryMetrics,
    LineMetrics,
    WordMetrics,
    char_category_metrics,
    line_metrics,
    word_metrics,
)

# Re-export identifier
from .identifier import (
    IdentifierAnalyzeResult,
    identifier_analyze,
)

# Re-export identifier_inspect
from .identifier_inspect import (
    IdentifierInspectResult,
    CollisionInfo,
    IdentifierInfo,
    identifier_inspect,
)

# Re-export path_tools
from .path_tools import (
    PathAnalyzeResult,
    path_analyze,
)

__all__ = [
    # Glob
    "glob_match",
    "GlobMatchResult",
    # Primitives
    "utf8_bytes",
    "codepoints",
    "normalize_unicode",
    "casefold_text",
    "raw_equal",
    "normalized_equal",
    "measure_basic",
    "count_graphemes",
    "truncate_to_grapheme",
    "find_invisibles",
    "visible_repr",
    "CodepointInfo",
    "MeasureBasic",
    "InvisibleCharInfo",
    # Unicode tools
    "unicode_script",
    "unicode_scripts",
    "detect_mixed_scripts",
    "detect_confusables",
    "confusables_count",
    "reverse_confusables",
    "ScriptInfo",
    "ConfusableInfo",
    "MixedScriptsResult",
    # Diff
    "first_diff",
    "common_prefix_suffix",
    "levenshtein_distance",
    "diff_spans",
    "longest_common_subsequence",
    "FirstDiff",
    "CommonPrefixSuffix",
    "DiffSpan",
    # Validate
    "check_brackets",
    "validate_json",
    "validate_toml_text",
    "validate_schema_light",
    "regex_test",
    "regex_finditer",
    "regex_safety_check",
    "json_extract",
    "json_compare",
    "json_shape",
    "CheckBracketsResult",
    "ValidateJsonResult",
    "ValidateSchemaLightResult",
    "ValidateTomlResult",
    "TomlShapeResult",
    "VersionCompareResult",
    "RegexTestResult",
    "RegexFindIterResult",
    "RegexFindIterMatch",
    "RegexSafetyResult",
    "RegexSafetyFinding",
    "JsonExtractResult",
    "JsonCompareDiff",
    "JsonCompareResult",
    "JsonShapeResult",
    "JsonShapeKey",
    # Measure
    "line_metrics",
    "word_metrics",
    "char_category_metrics",
    "LineMetrics",
    "WordMetrics",
    "CharCategoryMetrics",
    # Position
    "text_position",
    "TextPositionResult",
    # Transform
    "escape_text",
    "unescape_text",
    "text_hash",
    "text_transform",
    "text_fingerprint",
    "TextFingerprintResult",
    "EscapeTextResult",
    "UnescapeTextResult",
    "TextTransformResult",
    "RemovedChar",
    # Synthesis
    "measure_text",
    "text_equal",
    "explain_diff",
    "inspect_text",
    "count_chars",
    "list_compare",
    "MeasureTextResult",
    "TextEqualResult",
    "ExplainDiffResult",
    "InspectTextResult",
    "CountCharsResult",
    # Identifier
    "identifier_analyze",
    "IdentifierAnalyzeResult",
    "identifier_inspect",
    "IdentifierInspectResult",
    "CollisionInfo",
    "IdentifierInfo",
    # Path
    "path_analyze",
    "path_normalize",
    "PathAnalyzeResult",
    "PathNormalizeResult",
]
