"""
Low-level Unicode text primitives.

These primitives are deterministic, independently testable, and do not
perform semantic interpretation or call LLMs.

All modules in exact/ build on these primitives.
"""

from __future__ import annotations

import unicodedata
from typing import NamedTuple, TypedDict


class CodepointInfo(NamedTuple):
    """Information about a single codepoint."""
    index: int
    char: str
    codepoint: str
    name: str
    category: str


class MeasureBasic(TypedDict):
    """Basic text measurements."""
    bytes_utf8: int
    codepoints: int
    graphemes_estimate: None
    chars_no_whitespace: int
    ascii: int
    non_ascii: int


class InvisibleCharInfo(TypedDict):
    """Information about an invisible character."""
    index: int
    char: str
    codepoint: str
    name: str
    category: str
    display: str


# Invisible characters to detect
_INVISIBLE_CHARS: dict[str, tuple[str, str]] = {
    "\u200b": ("ZERO WIDTH SPACE", "ZWSP"),
    "\u200c": ("ZERO WIDTH NON-JOINER", "ZWNJ"),
    "\u200d": ("ZERO WIDTH JOINER", "ZWJ"),
    "\u200e": ("LEFT-TO-RIGHT MARK", "LRM"),
    "\u200f": ("RIGHT-TO-LEFT MARK", "RLM"),
    "\ufeff": ("ZERO WIDTH NO-BREAK SPACE", "BOM"),
    "\u00a0": ("NO-BREAK SPACE", "NBSP"),
    "\u2028": ("LINE SEPARATOR", "LINE SEP"),
    "\u2029": ("PARAGRAPH SEPARATOR", "PARA SEP"),
    "\u202a": ("LEFT-TO-RIGHT EMBEDDING", "LRE"),
    "\u202b": ("RIGHT-TO-LEFT EMBEDDING", "RLE"),
    "\u202c": ("POP DIRECTIONAL FORMATTING", "PDF"),
    "\u202d": ("LEFT-TO-RIGHT OVERRIDE", "LRO"),
    "\u202e": ("RIGHT-TO-LEFT OVERRIDE", "RLO"),
    "\u2066": ("LEFT-TO-RIGHT ISOLATE", "LRI"),
    "\u2067": ("RIGHT-TO-LEFT ISOLATE", "RLI"),
    "\u2068": ("FIRST STRONG ISOLATE", "FSI"),
    "\u2069": ("POP DIRECTIONAL ISOLATE", "PDI"),
    "\u2060": ("WORD JOINER", "WORD JOINER"),
    "\u00ad": ("SOFT HYPHEN", "SHY"),
    "\u180e": ("MONGOLIAN VOWEL SEPARATOR", "MVS"),
    "\u034f": ("COMBINING GRAPHEME JOINER", "CGJ"),
}

# Variation selectors (U+FE00 to U+FE0F)
_VARIATION_SELECTORS = set(range(0xfe00, 0xfe10))


def utf8_bytes(s: str) -> bytes:
    """Return raw UTF-8 bytes of the string.

    Args:
        s: Input string.

    Returns:
        UTF-8 encoded bytes.
    """
    return s.encode("utf-8")


def codepoints(s: str) -> list[CodepointInfo]:
    """Return detailed information about each codepoint in the string.

    Args:
        s: Input string.

    Returns:
        List of CodepointInfo namedtuples with index, char, codepoint (U+XXXX),
        Unicode name, and category.
    """
    result: list[CodepointInfo] = []
    for index, char in enumerate(s):
        codepoint_str = f"U+{ord(char):04X}"
        name = unicodedata.name(char, "<unknown>")
        category = unicodedata.category(char)
        result.append(CodepointInfo(index, char, codepoint_str, name, category))
    return result


def normalize_unicode(s: str, form: str) -> str:
    """Normalize Unicode string to the specified form.

    Args:
        s: Input string.
        form: Normalization form - one of NFC, NFD, NFKC, NFKD.

    Returns:
        Normalized string.

    Raises:
        ValueError: If form is not a recognized normalization form.
    """
    valid_forms = {"NFC", "NFD", "NFKC", "NFKD"}
    form_upper = form.upper()
    if form_upper not in valid_forms:
        raise ValueError(f"Unsupported normalization form: {form}. Use one of: {', '.join(valid_forms)}")
    return unicodedata.normalize(form_upper, s)


def casefold_text(s: str) -> str:
    """Return casefolded version of the string for case-insensitive comparison.

    Args:
        s: Input string.

    Returns:
        Casefolded string using str.casefold().
    """
    return s.casefold()


def raw_equal(a: str, b: str) -> bool:
    """Check if two strings are exactly equal (byte identity).

    Args:
        a: First string.
        b: Second string.

    Returns:
        True if strings are identical, False otherwise.
    """
    return a == b


def normalized_equal(a: str, b: str, form: str = "NFC") -> bool:
    """Check if two strings are equal after Unicode normalization.

    Args:
        a: First string.
        b: Second string.
        form: Normalization form - one of NFC, NFD, NFKC, NFKD.

    Returns:
        True if strings are equal after normalization.
    """
    return normalize_unicode(a, form) == normalize_unicode(b, form)


def measure_basic(s: str) -> MeasureBasic:
    """Return basic text measurements.

    Args:
        s: Input string.

    Returns:
        Dictionary with bytes_utf8, codepoints, graphemes_estimate (null),
        chars_no_whitespace, ascii, and non_ascii counts.
    """
    bytes_utf8 = len(s.encode("utf-8"))
    codepoints_count = len(s)
    chars_no_whitespace = sum(1 for c in s if not c.isspace())
    ascii_count = sum(1 for c in s if ord(c) < 128)
    non_ascii = codepoints_count - ascii_count

    return MeasureBasic(
        bytes_utf8=bytes_utf8,
        codepoints=codepoints_count,
        graphemes_estimate=None,
        chars_no_whitespace=chars_no_whitespace,
        ascii=ascii_count,
        non_ascii=non_ascii,
    )


def find_invisibles(s: str) -> list[InvisibleCharInfo]:
    """Find all invisible or control characters in the string.

    Detects zero-width spaces, joiners, BOM, word joiner, soft hyphen,
    variation selectors, bidi controls, and combining marks.

    Args:
        s: Input string.

    Returns:
        List of InvisibleCharInfo dicts with position, char, codepoint,
        name, category, and display marker.
    """
    result: list[InvisibleCharInfo] = []

    for index, char in enumerate(s):
        codepoint_val = ord(char)
        display = None
        name = None

        # Check known invisible chars
        if char in _INVISIBLE_CHARS:
            name, display = _INVISIBLE_CHARS[char]
        # Check variation selectors
        elif codepoint_val in _VARIATION_SELECTORS:
            name = "VARIATION SELECTOR"
            display = "VS"
        # Check bidi control characters (U+2060 to U+206F)
        elif 0x2060 <= codepoint_val <= 0x206f:
            name = unicodedata.name(char, "<unknown>")
            display = f"BIDI:{name.split()[-1]}" if name else "BIDI"
        # Check combining marks (category M*)
        elif unicodedata.category(char).startswith("M"):
            name = unicodedata.name(char, "<unknown>")
            display = "CM"
        # Check other control characters (category C*) but exclude newlines
        elif unicodedata.category(char).startswith("C") and char not in "\n\t\r":
            name = unicodedata.name(char, "<unknown>") if unicodedata.name(char, None) else "CONTROL"
            display = "CTRL"

        if display:
            codepoint_str = f"U+{codepoint_val:04X}"
            category = unicodedata.category(char)
            result.append(InvisibleCharInfo(
                index=index,
                char=char,
                codepoint=codepoint_str,
                name=name or "<unknown>",
                category=category,
                display=display,
            ))

    return result


def visible_repr(s: str) -> str:
    """Return a display-safe representation of the string.

    Maps invisible or ambiguous characters to display-safe markers.

    Args:
        s: Input string.

    Returns:
        String with invisible chars replaced by markers like ␠ (space),
        ␉ (tab), ⟦ZWSP⟧, etc.
    """
    result: list[str] = []

    for char in s:
        if char == " ":
            result.append("␠")
        elif char == "\t":
            result.append("␉")
        elif char == "\n":
            result.append("␊")
        elif char == "\r":
            result.append("␍")
        elif char in _INVISIBLE_CHARS:
            _, display = _INVISIBLE_CHARS[char]
            result.append(f"⟦{display}⟧")
        elif 0xfe00 <= ord(char) <= 0xfe0f:
            result.append("⟦VS⟧")
        elif unicodedata.category(char).startswith("M"):
            result.append(f"◌{char}")
        elif char == "\u2060":
            result.append("⟦WORD JOINER⟧")
        elif 0x2060 <= ord(char) <= 0x206f:
            bidi_names = {
                0x2066: "LRI", 0x2067: "RLI", 0x2068: "FSI", 0x2069: "PDI",
                0x202a: "LRE", 0x202b: "RLE", 0x202c: "PDF",
                0x202d: "LRO", 0x202e: "RLO",
            }
            name = bidi_names.get(ord(char), "BIDI")
            result.append(f"⟦{name}⟧")
        else:
            result.append(char)

    return "".join(result)
