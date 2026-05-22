"""
Low-level Unicode text primitives.

These primitives are deterministic, independently testable, and do not
perform semantic interpretation or call LLMs.
"""

from __future__ import annotations

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
    ScriptInfo,
    detect_confusables,
    detect_mixed_scripts,
    unicode_script,
    unicode_scripts,
    confusables_count,
)

# Re-export validate
from .validate import (
    CheckBracketsResult,
    RegexTestResult,
    ValidateJsonResult,
    check_brackets,
    regex_test,
    validate_json,
)

# Re-export diff
from .diff import (
    DiffSpan,
    FirstDiff,
    common_prefix_suffix,
    diff_spans,
    first_diff,
    levenshtein_distance,
    longest_common_subsequence,
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

__all__ = [
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
    "ScriptInfo",
    "ConfusableInfo",
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
    "regex_test",
    "CheckBracketsResult",
    "ValidateJsonResult",
    "RegexTestResult",
    # Measure
    "line_metrics",
    "word_metrics",
    "char_category_metrics",
    "LineMetrics",
    "WordMetrics",
    "CharCategoryMetrics",
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
]
