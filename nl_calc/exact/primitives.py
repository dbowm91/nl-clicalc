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
    graphemes_estimate: int
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
        Dictionary with bytes_utf8, codepoints, graphemes_estimate,
        chars_no_whitespace, ascii, and non_ascii counts.
    """
    bytes_utf8 = len(s.encode("utf-8"))
    codepoints_count = len(s)
    grapheme_count = count_graphemes(s)
    chars_no_whitespace = sum(1 for c in s if not c.isspace())
    ascii_count = sum(1 for c in s if ord(c) < 128)
    non_ascii = codepoints_count - ascii_count

    return MeasureBasic(
        bytes_utf8=bytes_utf8,
        codepoints=codepoints_count,
        graphemes_estimate=grapheme_count,
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


def count_graphemes(s: str) -> int:
    """Count extended grapheme clusters in a string.

    Implements Unicode UAX #29 grapheme cluster boundary rules.
    A grapheme cluster is what a user would perceive as a single character.
    For example, 'é' as precomposed (U+00E9) or decomposed ('e' + combining
    acute) both count as 1 grapheme. Emoji sequences like '🏳️' or '👨‍👩‍👧‍👦'
    each count as 1 grapheme.

    Args:
        s: Input string.

    Returns:
        Number of grapheme clusters in the string.
    """
    count = 0
    i = 0
    n = len(s)

    while i < n:
        count += 1
        i += 1  # Move past base character

        # Process all Extend characters and ZWJ sequences
        while i < n:
            cp = ord(s[i])

            # GB9: Extend characters (combining marks, ZWNJ, VS)
            if _is_extend_char(s[i]):
                i += 1
                continue

            # GB11: Emoji ZWJ sequences
            # Pattern: Extended_Pictographic (ZWJ Extend*)* ZWJ Extended_Pictographic
            if cp == 0x200D:  # ZWJ
                i += 1  # Skip ZWJ
                # If next is pictographic, consume it as part of this grapheme
                if i < n and _is_extended_pictographic(s[i]):
                    i += 1
                    # After pictographic, continue checking for more extends/ZWJ
                    continue
                # No pictographic after ZWJ, break and let main loop handle
                break

            # GB12/GB13: Regional Indicator pairs for flags
            # Two consecutive RIs form one grapheme
            if 0x1F1E6 <= cp <= 0x1F1FF:
                # Check if next is also RI
                if i + 1 < n and 0x1F1E6 <= ord(s[i + 1]) <= 0x1F1FF:
                    i += 2  # Skip both RIs
                    continue
                i += 1
                continue

            # Not an extend or ZWJ or RI pair, this is the start of next grapheme
            break

    return count


def _is_extend_char(char: str) -> bool:
    """Check if char is an Extend-class character per UAX #29 GB9.

    Note: ZWJ (U+200D) is NOT included here because it's part of emoji
    ZWJ sequences (GB11) and must be handled specially in _advance_past_sequence.
    """
    cat = unicodedata.category(char)
    cp = ord(char)

    # Extend: Mn (nonspacing mark), Me (enclosing mark), Mc (spacing combining mark)
    # Also: ZWNJ (U+200C), Variation Selectors (U+FE00-U+FE0F)
    if cat.startswith('M'):
        return True
    if cp == 0x200C:  # ZWNJ only (not ZWJ)
        return True
    if 0xFE00 <= cp <= 0xFE0F:  # Variation selectors
        return True
    return False


def _is_extended_pictographic(char: str) -> bool:
    """Check if char is an Extended Pictographic (for emoji ZWJ sequences).

    Uses codepoint ranges for common emoji blocks.
    """
    cp = ord(char)
    # Common emoji ranges:
    # U+1F300 to U+1F9FF (Misc Symbols, Emoticons, Transport, etc.)
    # U+2600 to U+26FF (Misc symbols)
    # U+2700 to U+27BF (Dingbats)
    # Also check category 'So' (Symbol other) which includes many emoji
    if 0x1F300 <= cp <= 0x10FFFF:
        return True
    if 0x2600 <= cp <= 0x26FF:
        return True
    if 0x2700 <= cp <= 0x27BF:
        return True
    # Check if it's an emoji via category and name patterns
    cat = unicodedata.category(char)
    if cat == 'So':
        name = unicodedata.name(char, '')
        # Most emoji names contain 'EMOJI' or 'FACE' or 'SYMBOL'
        if 'EMOJI' in name or 'FACE' in name or 'SYMBOL' in name or 'SIGN' in name:
            return True
    return False


def _advance_past_sequence(s: str, i: int) -> int:
    """Handle special grapheme sequence rules after a base character.

    Handles:
    - Emoji ZWJ sequences (GB11): Extended_Pictographic (ZWJ Extend*)* ZWJ Extended_Pictographic
    - Regional indicator pairs (flags): must stay together (GB12/GB13)
    - Hangul LVT+T sequences
    - Emoji modifier sequences (skin tones U+1F3FB-U+1F3FF)

    Args:
        s: Input string.
        i: Current index after base and extend chars.

    Returns:
        New index after handling any special sequences.
    """
    if i >= len(s):
        return i

    cp = ord(s[i])

    # GB11: Emoji ZWJ sequences
    # Pattern: Extended_Pictographic (ZWJ Extend*)* ZWJ Extended_Pictographic
    # Check if we have ZWJ followed by Extended_Pictographic
    if cp == 0x200D:  # ZWJ
        # Check if previous char (which should be after base+extends) was pictographic
        # Actually, we need to check if current position is ZWJ and next is Extended_Pictographic
        if i + 1 < len(s) and _is_extended_pictographic(s[i + 1]):
            # This is an emoji ZWJ sequence - skip the ZWJ and the following pictographic
            return i + 2

    # Regional Indicator (RI) pairs for flags - GB12/GB13
    # U+1F1E6 to U+1F1FF are RI characters
    if 0x1F1E6 <= cp <= 0x1F1FF:
        # Check for second RI to form a flag pair
        if i + 1 < len(s) and 0x1F1E6 <= ord(s[i + 1]) <= 0x1F1FF:
            return i + 2  # Skip both RIs
        return i + 1

    # Emoji modifier (Fitzpatrick skin tone modifiers U+1F3FB to U+1F3FF)
    # These modify the preceding emoji
    if 0x1F3FB <= cp <= 0x1F3FF:
        return i + 1

    # Hangul syllables: U+AC00 to U+D7AF
    if 0xAC00 <= cp <= 0xD7AF:
        return i + 1

    return i


def truncate_to_grapheme(s: str, max_graphemes: int) -> str:
    """Truncate a string to at most max_grapheme grapheme clusters.

    This ensures the result doesn't cut mid-grapheme, preserving emoji,
    combining sequences, and flag sequences intact.

    Args:
        s: Input string.
        max_graphemes: Maximum number of grapheme clusters to return.

    Returns:
        Truncated string with at most max_graphemes grapheme clusters.
    """
    if max_graphemes <= 0:
        return ""

    if len(s) == 0:
        return s

    result: list[str] = []
    grapheme_count = 0
    i = 0
    n = len(s)

    while i < n and grapheme_count < max_graphemes:
        result.append(s[i])
        grapheme_count += 1
        i += 1  # Move past base character

        # Process all Extend characters and ZWJ sequences
        while i < n:
            cp = ord(s[i])

            # GB9: Extend characters
            if _is_extend_char(s[i]):
                result.append(s[i])
                i += 1
                continue

            # GB11: Emoji ZWJ sequences
            if cp == 0x200D:  # ZWJ
                result.append(s[i])
                i += 1  # Skip ZWJ
                # If next is pictographic, consume it as part of this grapheme
                if i < n and _is_extended_pictographic(s[i]):
                    result.append(s[i])
                    i += 1
                    # Continue checking for more extends/ZWJ
                    continue
                break

            # GB12/GB13: Regional Indicator pairs for flags
            if 0x1F1E6 <= cp <= 0x1F1FF:
                if i + 1 < n and 0x1F1E6 <= ord(s[i + 1]) <= 0x1F1FF:
                    result.append(s[i])
                    result.append(s[i + 1])
                    i += 2
                    continue
                result.append(s[i])
                i += 1
                continue

            # Not extend or ZWJ or RI, break to start next grapheme
            break

    return "".join(result)
