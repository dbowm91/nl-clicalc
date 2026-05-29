"""
Identifier inspection for collision and validity checking.

Provides detection of identifier collisions across multiple identifiers
including confusables, normalization issues, and casefold collisions.
"""

from __future__ import annotations

import keyword
import unicodedata
from typing import TypedDict

from .unicode_tools import detect_confusables


class IdentifierInspectResult(TypedDict):
    """Result of identifier inspection."""
    identifiers: list[IdentifierInfo]
    collisions: list[CollisionInfo]


class IdentifierInfo(TypedDict):
    """Information about a single identifier."""
    raw: str
    normalized: str
    valid: bool
    scripts: list[str]
    has_invisibles: bool
    has_confusables: bool
    warnings: list[str]


class CollisionInfo(TypedDict):
    """Information about a collision between two identifiers."""
    kind: str
    a: str
    b: str


_JS_KEYWORDS: frozenset[str] = frozenset({
    "break", "case", "catch", "const", "continue", "debugger", "default",
    "delete", "do", "else", "enum", "export", "extends", "false", "finally",
    "for", "function", "if", "import", "in", "instanceof", "let", "new",
    "null", "return", "static", "super", "switch", "this", "throw", "true",
    "try", "typeof", "var", "void", "while", "with", "yield",
})


_SCRIPT_RANGES: list[tuple[int, int, str]] = [
    (0x0041, 0x005a, "Latin"),
    (0x0061, 0x007a, "Latin"),
    (0x00c0, 0x00ff, "Latin"),
    (0x0100, 0x017f, "Latin"),
    (0x0180, 0x024f, "Latin"),
    (0x0400, 0x04ff, "Cyrillic"),
    (0x0500, 0x052f, "Cyrillic"),
    (0x0370, 0x03ff, "Greek"),
    (0x1f00, 0x1fff, "Greek"),
    (0x4e00, 0x9fff, "Han"),
    (0x3000, 0x303f, "CJK"),
    (0x3040, 0x309f, "Hiragana"),
    (0x30a0, 0x30ff, "Katakana"),
    (0x0600, 0x06ff, "Arabic"),
    (0x0590, 0x05ff, "Hebrew"),
    (0x0900, 0x097f, "Devanagari"),
    (0x0e00, 0x0e7f, "Thai"),
    (0xac00, 0xd7af, "Hangul"),
    (0x10a0, 0x10ff, "Georgian"),
    (0x0530, 0x058f, "Armenian"),
    (0x13a0, 0x13ff, "Cherokee"),
    (0x1400, 0x167f, "Canadian_Aboriginal"),
]


def _get_script_heuristic(char: str) -> str:
    """Determine script for a character using heuristic detection."""
    codepoint = ord(char)

    if unicodedata.category(char).startswith("M"):
        return "Inherited"

    for start, end, script_name in _SCRIPT_RANGES:
        if start <= codepoint <= end:
            return script_name

    return "Other"


def _normalize_nfc(text: str) -> str:
    """Normalize text to NFC form."""
    return unicodedata.normalize("NFC", text)


def _casefold(text: str) -> str:
    """Casefold text for case-insensitive comparison."""
    return text.casefold()


def _has_invisibles(text: str) -> bool:
    """Check if text contains invisible characters."""
    invisible_chars = {
        "\u200b", "\u200c", "\u200d", "\u200e", "\u200f",
        "\ufeff", "\u00a0", "\u2028", "\u2029",
        "\u202a", "\u202b", "\u202c", "\u202d", "\u202e",
        "\u2066", "\u2067", "\u2068", "\u2069", "\u2060",
    }
    for char in text:
        if char in invisible_chars:
            return True
    return False


def _check_python_valid(text: str) -> bool:
    """Check if identifier is valid Python identifier."""
    if not text:
        return False
    if not text.isidentifier():
        return False
    if keyword.iskeyword(text):
        return False
    return True


def _check_js_valid(text: str) -> bool:
    """Check if identifier is valid JavaScript identifier."""
    if not text:
        return False
    if text in _JS_KEYWORDS:
        return False
    if not text.isidentifier():
        return False
    return True


def _get_scripts(text: str) -> list[str]:
    """Get list of Unicode scripts used in text."""
    scripts: set[str] = set()
    for char in text:
        script = _get_script_heuristic(char)
        if script not in ("Common", "Inherited", "Unknown", "Other"):
            scripts.add(script)
    return sorted(list(scripts))


def identifier_inspect(
    identifiers: list[str],
    language: str = "generic",
    normalization: str = "NFC",
    casefold: bool = False,
    check_confusables: bool = True,
) -> IdentifierInspectResult:
    """Inspect a list of identifiers for validity and collisions.

    Detects confusables, mixed scripts, normalization issues, and
    casefold collisions across identifiers.

    Args:
        identifiers: List of identifier strings to inspect.
        language: Language for validation ("generic", "python", "rust",
                  "javascript", "typescript", "json_key").
        normalization: Unicode normalization form ("NFC", "NFD", etc).
        casefold: Apply casefolding for collision detection.
        check_confusables: Check for confusable characters.

    Returns:
        IdentifierInspectResult with per-identifier info and collisions.

    Example:
        >>> result = identifier_inspect(["paypal", "pаypal"], language="python")
        >>> result["collisions"]
        [{'kind': 'confusable', 'a': 'paypal', 'b': 'pаypal'}]
    """
    normalized_ids: list[str] = []
    id_infos: list[IdentifierInfo] = []
    collisions: list[CollisionInfo] = []

    for raw_id in identifiers:
        normalized = raw_id
        if normalization != "raw":
            normalized = unicodedata.normalize(normalization, raw_id)

        scripts = _get_scripts(normalized)
        has_invisibles = _has_invisibles(raw_id)

        confusables_found = []
        if check_confusables:
            confusables_found = detect_confusables(normalized)

        has_confusables = len(confusables_found) > 0

        valid = True
        warnings: list[str] = []

        if language == "python":
            valid = _check_python_valid(normalized)
            if not valid:
                warnings.append("Invalid Python identifier")
        elif language in ("javascript", "typescript"):
            valid = _check_js_valid(normalized)
            if not valid:
                warnings.append(f"Invalid {language} identifier")

        if has_invisibles:
            warnings.append("Contains invisible characters")

        if has_confusables:
            warnings.append("Contains confusable characters")

        if len(scripts) > 1:
            warnings.append("Mixed script identifier")

        id_infos.append(IdentifierInfo(
            raw=raw_id,
            normalized=normalized,
            valid=valid,
            scripts=scripts,
            has_invisibles=has_invisibles,
            has_confusables=has_confusables,
            warnings=warnings,
        ))
        normalized_ids.append(normalized)

    collision_pairs: set[tuple[str, str]] = set()

    if check_confusables:
        for i, a_raw in enumerate(identifiers):
            for j, b_raw in enumerate(identifiers):
                if i >= j:
                    continue

                a_norm = normalized_ids[i]
                b_norm = normalized_ids[j]

                a_confusables = detect_confusables(a_norm)
                b_confusables = detect_confusables(b_norm)

                if a_confusables and b_confusables:
                    a_targets = {c["confusable_with"] for c in a_confusables}
                    b_targets = {c["confusable_with"] for c in b_confusables}
                    shared_targets = a_targets & b_targets
                    if shared_targets:
                        pair = (a_raw, b_raw) if a_raw <= b_raw else (b_raw, a_raw)
                        if pair not in collision_pairs:
                            collision_pairs.add(pair)
                            collisions.append(CollisionInfo(
                                kind="confusable",
                                a=a_raw,
                                b=b_raw,
                            ))
                        continue

                for a_conf in a_confusables:
                    if a_conf["confusable_with"] in b_norm:
                        pair = (a_raw, b_raw) if a_raw <= b_raw else (b_raw, a_raw)
                        if pair not in collision_pairs:
                            collision_pairs.add(pair)
                            collisions.append(CollisionInfo(
                                kind="confusable",
                                a=a_raw,
                                b=b_raw,
                            ))
                        break

                for b_conf in b_confusables:
                    if b_conf["confusable_with"] in a_norm:
                        pair = (a_raw, b_raw) if a_raw <= b_raw else (b_raw, a_raw)
                        if pair not in collision_pairs:
                            collision_pairs.add(pair)
                            collisions.append(CollisionInfo(
                                kind="confusable",
                                a=a_raw,
                                b=b_raw,
                            ))
                        break

    if casefold:
        casefold_map: dict[str, list[str]] = {}
        for i, (raw, norm) in enumerate(zip(identifiers, normalized_ids)):
            cf_key = _casefold(norm)
            if cf_key not in casefold_map:
                casefold_map[cf_key] = []
            casefold_map[cf_key].append(raw)

        for cf_key, items in casefold_map.items():
            if len(items) > 1:
                for i in range(len(items)):
                    for j in range(i + 1, len(items)):
                        pair = (items[i], items[j]) if items[i] <= items[j] else (items[j], items[i])
                        if pair not in collision_pairs:
                            collision_pairs.add(pair)
                            collisions.append(CollisionInfo(
                                kind="casefold",
                                a=items[i],
                                b=items[j],
                            ))

    if normalization != "raw":
        norm_map: dict[str, list[str]] = {}
        for raw, norm in zip(identifiers, normalized_ids):
            if norm not in norm_map:
                norm_map[norm] = []
            norm_map[norm].append(raw)

        for norm_key, items in norm_map.items():
            if len(items) > 1:
                for i in range(len(items)):
                    for j in range(i + 1, len(items)):
                        pair = (items[i], items[j]) if items[i] <= items[j] else (items[j], items[i])
                        if pair not in collision_pairs:
                            collision_pairs.add(pair)
                            collisions.append(CollisionInfo(
                                kind="normalization",
                                a=items[i],
                                b=items[j],
                            ))

    return IdentifierInspectResult(
        identifiers=id_infos,
        collisions=collisions,
    )
