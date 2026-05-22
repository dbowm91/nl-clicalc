"""
Synthesis functions built on exact primitives.

These functions combine primitives to provide higher-level operations
for text inspection, comparison, and measurement.
"""

from __future__ import annotations

import unicodedata
from typing import Any, TypedDict

from .diff import (
    common_prefix_suffix as _common_prefix_suffix,
)
from .diff import (
    diff_spans as _diff_spans,
)
from .diff import (
    first_diff as _first_diff,
)
from .diff import (
    levenshtein_distance as _levenshtein_distance,
)
from .measure import (
    char_category_metrics as _char_category_metrics,
)
from .measure import (
    line_metrics as _line_metrics,
)
from .measure import (
    word_metrics as _word_metrics,
)
from .primitives import casefold_text as _casefold_text
from .primitives import (
    count_graphemes as _count_graphemes,
)
from .primitives import (
    find_invisibles as _find_invisibles,
)
from .primitives import (
    measure_basic as _measure_basic,
)
from .primitives import normalize_unicode as _normalize_unicode
from .primitives import (
    normalized_equal as _normalized_equal,
)
from .primitives import (
    raw_equal as _raw_equal,
)
from .primitives import (
    visible_repr as _visible_repr,
)
from .unicode_tools import (
    detect_confusables as _detect_confusables,
)
from .unicode_tools import (
    detect_mixed_scripts as _detect_mixed_scripts,
)

MAX_TEXT_LENGTH = 100_000
MAX_DIFF_SPANS = 50


class NormalizationState(TypedDict):
    """Unicode normalization state."""
    is_nfc: bool
    is_nfd: bool
    is_nfkc: bool
    is_nfkd: bool


class UnicodeRisks(TypedDict):
    """Unicode risk signals."""
    contains_invisibles: bool
    contains_bidi_controls: bool
    mixed_scripts: bool
    scripts: list[str]


class MeasureTextResult(TypedDict):
    """Complete text measurement result."""
    bytes_utf8: int
    codepoints: int
    graphemes: int
    words: int
    unique_words_casefolded: int
    lines: int
    nonempty_lines: int
    blank_lines: int
    max_line_length_codepoints: int
    chars_no_whitespace: int
    ascii: int
    non_ascii: int
    letters: int
    digits: int
    punctuation: int
    symbols: int
    spaces: int
    control_chars: int
    combining_marks: int
    invisible_chars: int
    newline_style: str
    ends_with_newline: bool
    normalization: NormalizationState
    unicode_risks: UnicodeRisks


class TextEqualResult(TypedDict):
    """Text equality comparison result."""
    equal: bool
    mode: dict[str, Any]
    raw_equal: bool
    nfc_equal: bool
    nfd_equal: bool
    nfkc_equal: bool
    nfkd_equal: bool
    casefold_equal: bool
    byte_equal: bool
    lengths: dict[str, int]
    first_difference: dict[str, Any] | None
    classification: str


class DiffInfo(TypedDict):
    """A single diff span with detailed information."""
    kind: str
    a_span: list[int]
    b_span: list[int]
    a_text: str
    b_text: str
    a_visible: str
    b_visible: str
    a_codepoints: list[dict]
    b_codepoints: list[dict]
    note: str


class ExplainDiffResult(TypedDict):
    """Detailed diff explanation result."""
    equal: bool
    classification: str
    summary: dict[str, Any]
    a_metrics: dict[str, int]
    b_metrics: dict[str, int]
    diffs: list[DiffInfo]
    security_findings: list[dict]
    agent_instruction: str


class InspectTextResult(TypedDict):
    """Complete text inspection result."""
    safe_repr: str
    metrics: dict[str, Any]
    normalization: dict[str, bool]
    invisibles: list[dict]
    scripts: dict[str, Any]
    confusables: list[dict]
    warnings: list[dict]


class CountCharsResult(TypedDict):
    """Character counting result."""
    target: str
    normalization: str
    count: int
    positions: list[int]
    text_length_codepoints: int


def measure_text(text: str) -> MeasureTextResult:
    """Measure text properties combining multiple primitives.

    Args:
        text: Input string.

    Returns:
        Complete text measurement with metrics, normalization, and risk signals.

    Raises:
        ValueError: If text exceeds MAX_TEXT_LENGTH.
    """
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"Input length {len(text)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}")

    basic = _measure_basic(text)
    lines = _line_metrics(text)
    words = _word_metrics(text)
    categories = _char_category_metrics(text)
    invisibles = _find_invisibles(text)
    scripts = _detect_mixed_scripts(text)
    grapheme_count = _count_graphemes(text)

    return MeasureTextResult(
        bytes_utf8=basic["bytes_utf8"],
        codepoints=basic["codepoints"],
        graphemes=grapheme_count,
        words=words["words"],
        unique_words_casefolded=words["unique_words_casefolded"],
        lines=lines["lines"],
        nonempty_lines=lines["nonempty_lines"],
        blank_lines=lines["blank_lines"],
        max_line_length_codepoints=lines["max_line_length_codepoints"],
        chars_no_whitespace=basic["chars_no_whitespace"],
        ascii=basic["ascii"],
        non_ascii=basic["non_ascii"],
        letters=categories["letters"],
        digits=categories["digits"],
        punctuation=categories["punctuation"],
        symbols=categories["symbols"],
        spaces=categories["spaces"],
        control_chars=categories["control_chars"],
        combining_marks=categories["combining_marks"],
        invisible_chars=len(invisibles),
        newline_style=lines["newline_style"],
        ends_with_newline=lines["ends_with_newline"],
        normalization=NormalizationState(
            is_nfc=unicodedata.is_normalized("NFC", text),
            is_nfd=unicodedata.is_normalized("NFD", text),
            is_nfkc=unicodedata.is_normalized("NFKC", text),
            is_nfkd=unicodedata.is_normalized("NFKD", text),
        ),
        unicode_risks=UnicodeRisks(
            contains_invisibles=len(invisibles) > 0,
            contains_bidi_controls=any("BIDI" in inv.get("display", "") for inv in invisibles),
            mixed_scripts=scripts["mixed_scripts"],
            scripts=scripts["scripts"],
        ),
    )


def text_equal(
    a: str,
    b: str,
    normalization: str = "raw",
    casefold: bool = False,
    trim: bool = False,
) -> TextEqualResult:
    """Compare two strings under various equality modes.

    Args:
        a: First string.
        b: Second string.
        normalization: "raw", "NFC", "NFD", "NFKC", or "NFKD".
        casefold: If True, use casefolded comparison.
        trim: If True, trim whitespace.

    Returns:
        Detailed equality comparison with evidence.
    """
    a_work = a
    b_work = b

    if trim:
        a_work = a_work.strip()
        b_work = b_work.strip()

    raw_equal = _raw_equal(a_work, b_work)
    nfc_equal = _normalized_equal(a_work, b_work, "NFC")
    nfd_equal = _normalized_equal(a_work, b_work, "NFD")
    nfkc_equal = _normalized_equal(a_work, b_work, "NFKC")
    nfkd_equal = _normalized_equal(a_work, b_work, "NFKD")
    casefold_equal = _casefold_text(a_work) == _casefold_text(b_work)
    byte_equal = a_work.encode("utf-8") == b_work.encode("utf-8")

    # Length metrics
    lengths = {
        "a_codepoints": len(a_work),
        "b_codepoints": len(b_work),
        "a_bytes_utf8": len(a_work.encode("utf-8")),
        "b_bytes_utf8": len(b_work.encode("utf-8")),
    }

    # First difference
    first_difference = _first_diff(a_work, b_work)
    if first_difference:
        first_difference["a_visible"] = _visible_repr(a_work[first_difference["a_index"]:first_difference["a_index"]+1])
        first_difference["b_visible"] = _visible_repr(b_work[first_difference["b_index"]:first_difference["b_index"]+1])

    # Detect invisibles before classification
    invisibles_a = _find_invisibles(a_work)
    invisibles_b = _find_invisibles(b_work)
    invisibles_detected = bool(invisibles_a or invisibles_b)

    # Classification
    classification = _classify_difference(
        raw_equal, nfc_equal, casefold_equal, byte_equal,
        len(a_work) != len(b_work), first_difference, invisibles_detected=invisibles_detected
    )

    # Determine overall equality based on mode
    if casefold:
        equal = casefold_equal
    elif normalization == "raw":
        equal = raw_equal
    elif normalization in ("NFC", "NFD", "NFKC", "NFKD"):
        equal = _normalized_equal(a_work, b_work, normalization)
    else:
        equal = raw_equal

    return TextEqualResult(
        equal=equal,
        mode={
            "normalization": normalization,
            "casefold": casefold,
            "trim": trim,
        },
        raw_equal=raw_equal,
        nfc_equal=nfc_equal,
        nfd_equal=nfd_equal,
        nfkc_equal=nfkc_equal,
        nfkd_equal=nfkd_equal,
        casefold_equal=casefold_equal,
        byte_equal=byte_equal,
        lengths=lengths,
        first_difference=first_difference,
        classification=classification,
    )


def _classify_difference(
    raw_equal: bool,
    nfc_equal: bool,
    casefold_equal: bool,
    byte_equal: bool,
    length_diff: bool,
    first_diff: dict | None,
    invisibles_detected: bool,
) -> str:
    """Classify the type of difference between two strings."""
    if raw_equal:
        return "exact_match"

    if casefold_equal:
        return "case_only"

    if nfc_equal:
        if not casefold_equal:
            return "accent_or_diacritic_difference"
        return "unicode_normalization_only"

    if length_diff:
        return "length_only"

    if invisibles_detected:
        return "invisible_character"

    return "ordinary_text_difference"


def _codepoint_details(s: str, start: int, end: int) -> list[dict]:
    """Get codepoint details for a span."""
    result = []
    for i in range(start, min(end, len(s))):
        char = s[i]
        result.append({
            "char": char,
            "codepoint": f"U+{ord(char):04X}",
            "name": unicodedata.name(char, "<unknown>"),
        })
    return result


def explain_diff(
    a: str,
    b: str,
    max_diffs: int = 20,
    include_codepoints: bool = True,
    include_context: bool = True,
) -> ExplainDiffResult:
    """Explain why two strings differ with detailed evidence.

    Args:
        a: First string.
        b: Second string.
        max_diffs: Maximum number of diff spans.
        include_codepoints: Include codepoint details.
        include_context: Include context in notes.

    Returns:
        Detailed diff explanation with classification and agent instruction.
    """
    if len(a) > MAX_TEXT_LENGTH or len(b) > MAX_TEXT_LENGTH:
        raise ValueError(f"Input exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}")

    raw_equal = _raw_equal(a, b)
    nfc_equal = _normalized_equal(a, b, "NFC")
    nfkc_equal = _normalized_equal(a, b, "NFKC")
    casefold_equal = _casefold_text(a) == _casefold_text(b)
    byte_equal = a.encode("utf-8") == b.encode("utf-8")

    same_length_codepoints = len(a) == len(b)
    edit_distance = _levenshtein_distance(a, b) if not raw_equal else 0
    prefix_suffix = _common_prefix_suffix(a, b)

    a_metrics = {
        "bytes_utf8": len(a.encode("utf-8")),
        "codepoints": len(a),
    }
    b_metrics = {
        "bytes_utf8": len(b.encode("utf-8")),
        "codepoints": len(b),
    }

    diffs_raw = _diff_spans(a, b, max_diffs=max_diffs)
    diffs: list[DiffInfo] = []

    invisibles_a = _find_invisibles(a)
    invisibles_b = _find_invisibles(b)
    invisibles_detected = bool(invisibles_a or invisibles_b)
    confusables_a = _detect_confusables(a)
    confusables_b = _detect_confusables(b)

    same_length_codepoints = len(a) == len(b)

    classification = _classify_difference(
        raw_equal, nfc_equal, casefold_equal, byte_equal,
        not same_length_codepoints, None, invisibles_detected
    )

    if classification == "ordinary_text_difference" and nfkc_equal:
        classification = "compatibility_normalization_only"

    security_findings: list[dict] = []
    if invisibles_a or invisibles_b:
        security_findings.append({
            "kind": "invisible_characters",
            "a_count": len(invisibles_a),
            "b_count": len(invisibles_b),
        })
    if confusables_a or confusables_b:
        security_findings.append({
            "kind": "confusables",
            "a_count": len(confusables_a),
            "b_count": len(confusables_b),
        })

    for d in diffs_raw:
        a_start, a_end = d["a_span"]
        b_start, b_end = d["b_span"]

        a_text = d["a_text"]
        b_text = d["b_text"]

        note = ""
        if d["kind"] == "equal":
            note = "Matching text"
        elif len(a_text) != len(b_text):
            note = f"Length difference: {len(a_text)} vs {len(b_text)} codepoints"
        elif nfc_equal:
            note = "Different raw codepoints, equal after NFC normalization"
        else:
            note = "Different codepoints"

        diff_info = DiffInfo(
            kind=d["kind"],
            a_span=d["a_span"],
            b_span=d["b_span"],
            a_text=a_text,
            b_text=b_text,
            a_visible=_visible_repr(a_text),
            b_visible=_visible_repr(b_text),
            a_codepoints=_codepoint_details(a, a_start, a_end) if include_codepoints else [],
            b_codepoints=_codepoint_details(b, b_start, b_end) if include_codepoints else [],
            note=note,
        )
        diffs.append(diff_info)

        # Update classification based on diff type
        if not classification or classification == "exact_match":
            if d["kind"] == "replace":
                classification = "ordinary_text_difference"

    agent_instruction = _generate_agent_instruction(classification, raw_equal, nfc_equal, byte_equal)

    return ExplainDiffResult(
        equal=raw_equal,
        classification=classification,
        summary={
            "raw_equal": raw_equal,
            "byte_equal": byte_equal,
            "nfc_equal": nfc_equal,
            "nfkc_equal": nfkc_equal,
            "casefold_equal": casefold_equal,
            "same_length_codepoints": same_length_codepoints,
            "edit_distance": edit_distance,
            "common_prefix_len": prefix_suffix["common_prefix_len"],
            "common_suffix_len": prefix_suffix["common_suffix_len"],
        },
        a_metrics=a_metrics,
        b_metrics=b_metrics,
        diffs=diffs,
        security_findings=security_findings,
        agent_instruction=agent_instruction,
    )


def _generate_agent_instruction(classification: str, raw_equal: bool, nfc_equal: bool, byte_equal: bool) -> str:
    """Generate agent-facing instruction based on classification."""
    if raw_equal:
        return "Strings are identical."
    if classification == "unicode_normalization_only":
        return "Treat these strings as equivalent only if NFC normalization is acceptable. They are not byte-identical."
    if classification == "case_only":
        return "Strings differ only by case. Case-insensitive comparison should treat them as equal."
    if classification == "compatibility_normalization_only":
        return "Strings differ in compatibility normalization (NFKC). Treat as equivalent if compatibility normalization is acceptable."
    if not byte_equal:
        return "Strings are not byte-identical and differ in Unicode normalization. Choose appropriate normalization for your use case."
    return "Strings differ. Review diff details for specifics."


def inspect_text(
    text: str,
    include_codepoints: bool = True,
    include_confusables: bool = True,
) -> InspectTextResult:
    """Inspect text for hidden characters, confusables, and Unicode signals.

    Args:
        text: Input string.
        include_codepoints: Include codepoint details in invisibles.
        include_confusables: Check for confusables.

    Returns:
        Complete text inspection with safe representation.
    """
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"Input length {len(text)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}")

    metrics = measure_text(text)
    invisibles = _find_invisibles(text)
    scripts = _detect_mixed_scripts(text)
    confusables = _detect_confusables(text) if include_confusables else []
    safe_repr = _visible_repr(text)

    warnings: list[dict] = []
    if metrics["unicode_risks"]["contains_invisibles"]:
        for inv in invisibles:
            warnings.append({
                "severity": "warning",
                "kind": "invisible_character",
                "message": f"Text contains {inv['name']} at index {inv['index']}.\n    {inv['codepoint']}",
            })
    if metrics["unicode_risks"]["contains_bidi_controls"]:
        warnings.append({
            "severity": "warning",
            "kind": "bidi_control",
            "message": "Text contains bidirectional control characters.",
        })
    if metrics["unicode_risks"]["mixed_scripts"]:
        warnings.append({
            "severity": "warning",
            "kind": "mixed_scripts",
            "message": f"Text contains mixed scripts: {', '.join(metrics['unicode_risks']['scripts'])}.",
        })
    if confusables:
        for conf in confusables:
            warnings.append({
                "severity": "warning",
                "kind": "confusable",
                "message": f"Text contains confusable character '{conf['char']}' (looks like '{conf['confusable_with']}') at index {conf['index']}.",
            })

    return InspectTextResult(
        safe_repr=safe_repr,
        metrics=metrics,
        normalization={
            "is_nfc": metrics["normalization"]["is_nfc"],
            "is_nfkc": metrics["normalization"]["is_nfkc"],
        },
        invisibles=invisibles,
        scripts=scripts,
        confusables=confusables,
        warnings=warnings,
    )


def count_chars(
    text: str,
    target: str | None = None,
    normalization: str = "raw",
) -> CountCharsResult | dict[str, int]:
    """Count character occurrences or return frequency table.

    Args:
        text: Input string.
        target: Single character to count (None for frequency table).
        normalization: "raw", "NFC", or "NFKC".

    Returns:
        Counting result or frequency table if target is None.
    """
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"Input length {len(text)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}")

    if normalization != "raw":
        text = _normalize_unicode(text, normalization)

    if target is None:
        freq: dict[str, int] = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        return freq

    if len(target) != 1:
        raise ValueError("target must be a single character")

    positions = [i for i, c in enumerate(text) if c == target]

    return CountCharsResult(
        target=target,
        normalization=normalization,
        count=len(positions),
        positions=positions,
        text_length_codepoints=len(text),
    )


def list_compare(
    a: list[str],
    b: list[str],
    ignore_order: bool = True,
    casefold: bool = False,
    normalization: str = "NFC",
) -> dict:
    """Compare two lists with optional ignore_order, casefold, normalization.

    Args:
        a: First list.
        b: Second list.
        ignore_order: If True, compare as sets.
        casefold: If True, casefold elements before comparison.
        normalization: Unicode normalization form.

    Returns:
        Comparison result with same_ordered, same_unordered, only_in_a,
        only_in_b, duplicates_a, duplicates_b, near_matches.
    """
    def transform(s: str) -> str:
        result = s
        if normalization != "raw":
            result = _normalize_unicode(result, normalization)
        if casefold:
            result = _casefold_text(result)
        return result

    a_transformed = [transform(x) for x in a]
    b_transformed = [transform(x) for x in b]

    a_set = set(a_transformed)
    b_set = set(b_transformed)

    only_in_a = [a[i] for i, x in enumerate(a_transformed) if x not in b_set]
    only_in_b = [b[i] for i, x in enumerate(b_transformed) if x not in a_set]

    # Duplicates
    from collections import Counter
    a_counts = Counter(a_transformed)
    b_counts = Counter(b_transformed)
    duplicates_a = [x for x, c in a_counts.items() if c > 1]
    duplicates_b = [x for x, c in b_counts.items() if c > 1]

    # Near matches (case-only or normalization-only differences)
    # Use set-based matching for O(n) instead of O(n²)
    near_matches: list[dict] = []
    seen_pairs: set[tuple[str, str]] = set()

    casefold_groups: dict[str, list[tuple[int, str, str]]] = {}
    for i, (item, t) in enumerate(zip(a, a_transformed, strict=True)):
        cf = t.casefold()
        if cf not in casefold_groups:
            casefold_groups[cf] = []
        casefold_groups[cf].append((i, item, t))

    norm_groups: dict[str, list[tuple[int, str, str]]] = {}
    for i, (item, t) in enumerate(zip(a, a_transformed, strict=True)):
        nfc = _normalize_unicode(t, "NFC")
        if nfc not in norm_groups:
            norm_groups[nfc] = []
        norm_groups[nfc].append((i, item, t))

    b_casefold_index: dict[str, str] = {}
    b_norm_index: dict[str, str] = {}
    for b_item, b_t in zip(b, b_transformed, strict=True):
        b_casefold_index[b_t.casefold()] = b_item
        b_norm_index[_normalize_unicode(b_t, "NFC")] = b_item

    for cf_key, a_group in casefold_groups.items():
        if cf_key in b_casefold_index:
            b_item = b_casefold_index[cf_key]
            for _, a_item, _ in a_group:
                pair = (a_item, b_item) if a_item <= b_item else (b_item, a_item)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    near_matches.append({"a": a_item, "b": b_item, "classification": "case_only"})

    for nfc_key, a_group in norm_groups.items():
        if nfc_key in b_norm_index:
            b_item = b_norm_index[nfc_key]
            for _, a_item, _ in a_group:
                pair = (a_item, b_item) if a_item <= b_item else (b_item, a_item)
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    near_matches.append({"a": a_item, "b": b_item, "classification": "unicode_normalization_only"})

    same_ordered = ignore_order or (a_transformed == b_transformed)
    same_unordered = a_set == b_set

    return {
        "same_ordered": same_ordered,
        "same_unordered": same_unordered,
        "only_in_a": only_in_a,
        "only_in_b": only_in_b,
        "duplicates_a": duplicates_a,
        "duplicates_b": duplicates_b,
        "near_matches": near_matches,
    }
