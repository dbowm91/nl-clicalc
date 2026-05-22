"""
Unicode script detection and confusable character detection.

Provides functions to detect Unicode scripts and identify confusable
homoglyphs that could be used for spoofing attacks.

The confusables table is derived from Unicode Standard Annex #39:
https://www.unicode.org/reports/tr39/
The full confusables.txt can be loaded at build time for comprehensive detection.
"""

from __future__ import annotations

import functools
import unicodedata
from typing import TypedDict

from .confusables import CONFUSABLES


class ScriptInfo(TypedDict):
    """Information about a script detection result."""
    index: int
    char: str
    script: str
    codepoint: str


class ConfusableInfo(TypedDict):
    """Information about a confusable character."""
    index: int
    char: str
    codepoint: str
    name: str
    confusable_with: str
    confusable_name: str


# Unicode script ranges for heuristic detection
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


@functools.lru_cache(maxsize=128)
def _get_script_heuristic(char: str) -> str:
    """Determine script for a character using codepoint ranges.

    Uses heuristic range-based detection since unicodedata.script()
    may not be available in all Python versions.

    Args:
        char: Single character.

    Returns:
        Script name or 'Other'.
    """
    codepoint = ord(char)

    # Check if it's a combining mark
    if unicodedata.category(char).startswith("M"):
        return "Inherited"

    # Check predefined scripts via unicodedata.name for Common script
    try:
        name = unicodedata.name(char, "")
        if "COMMON" in name.upper():
            return "Common"
        # Check for inherited scripts by name patterns
        if "INHERITED" in name.upper():
            return "Inherited"
    except ValueError:
        pass

    # Use range heuristic for script detection
    for start, end, script_name in _SCRIPT_RANGES:
        if start <= codepoint <= end:
            return script_name

    return "Other"


def unicode_script(char: str) -> str:
    """Determine the Unicode script of a single character.

    Uses Unicode script property with heuristic fallback for
    characters where the property returns Unknown.

    Args:
        char: Single character.

    Returns:
        Script name (Latin, Cyrillic, Greek, Han, Hiragana,
        Katakana, Arabic, Hebrew, Devanagari, Common, Inherited, Other).
    """
    if len(char) != 1:
        raise ValueError("char must be a single character")

    return _get_script_heuristic(char)


def unicode_scripts(s: str) -> list[str]:
    """Determine the Unicode scripts for all characters in a string.

    Args:
        s: Input string.

    Returns:
        List of script names for each character.
    """
    return [_get_script_heuristic(char) for char in s]


def detect_mixed_scripts(s: str) -> dict:
    """Detect if string contains mixed scripts.

    Ignores Common, Inherited, and Other scripts for the mixed-script
    verdict. Characters classified as "Other" (digits, punctuation,
    whitespace, etc.) are excluded from the mixed-script analysis.

    Args:
        s: Input string.

    Returns:
        Dictionary with mixed_scripts (bool), scripts (list of distinct
        scripts excluding Common/Inherited/Other), and positions (list of
        ScriptInfo dicts for non-Common/Inherited/Other chars).
    """
    positions: list[ScriptInfo] = []
    scripts: set[str] = set()

    for index, char in enumerate(s):
        script = _get_script_heuristic(char)
        if script not in ("Common", "Inherited", "Other"):
            scripts.add(script)
            codepoint_str = f"U+{ord(char):04X}"
            positions.append(ScriptInfo(
                index=index,
                char=char,
                script=script,
                codepoint=codepoint_str,
            ))

    return {
        "mixed_scripts": len(scripts) > 1,
        "scripts": sorted(scripts),
        "positions": positions,
    }


def detect_confusables(s: str) -> list[ConfusableInfo]:
    """Detect confusable homoglyph characters in the string.

    Uses the full Unicode confusables table (UTS #39) loaded from
    confusables.py, which was generated from confusables.txt.

    Args:
        s: Input string.

    Returns:
        List of ConfusableInfo dicts with position, char, codepoint,
        name, confusable_with, and confusable_name.
    """
    result: list[ConfusableInfo] = []

    for index, char in enumerate(s):
        key = f"U+{ord(char):04X}"
        if key in CONFUSABLES:
            sub_str = CONFUSABLES[key]
            codepoint_str = f"U+{ord(char):04X}"
            name = unicodedata.name(char, "<unknown>")

            # Parse substitution codepoints back to characters
            confusable_with = "".join(chr(int(cp[2:], 16)) for cp in sub_str.split())

            confusable_name = ""
            for c in confusable_with:
                n = unicodedata.name(c, "")
                if n:
                    confusable_name += n + " "
                else:
                    confusable_name += c
            confusable_name = confusable_name.strip()

            result.append(ConfusableInfo(
                index=index,
                char=char,
                codepoint=codepoint_str,
                name=name,
                confusable_with=confusable_with,
                confusable_name=confusable_name,
            ))

    return result


def confusables_count(s: str) -> int:
    """Count confusable homoglyph characters in the string.

    Args:
        s: Input string.

    Returns:
        Count of confusable characters.
    """
    count = 0
    for char in s:
        key = f"U+{ord(char):04X}"
        if key in CONFUSABLES:
            count += 1
    return count
