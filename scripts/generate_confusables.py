#!/usr/bin/env python3
"""Parse Unicode confusables.txt and generate confusables.py.

This script downloads the latest confusables.txt from Unicode consortium
and generates a Python dictionary for use in unicode_tools.
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path


CONFUSABLES_URL = "https://www.unicode.org/Public/security/latest/confusables.txt"
OUTPUT_FILE = Path(__file__).parent.parent / "nl_calc" / "exact" / "confusables.py"
COMMENTS_AND_HEADER_LINES = 35  # Approximate header lines to skip


def fetch_confusables_txt() -> str:
    """Download the confusables.txt file."""
    print(f"Fetching {CONFUSABLES_URL}...")
    with urllib.request.urlopen(CONFUSABLES_URL, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_code_point(s: str) -> str | None:
    """Parse a hex code point like '05AD' or '041F' into Unicode char.

    Returns the character, or None if invalid.
    """
    s = s.strip()
    if not s:
        return None
    match = re.fullmatch(r"([0-9A-Fa-f]{4,6})", s)
    if not match:
        return None
    return chr(int(s, 16))


def parse_line(line: str) -> tuple[str, str] | None:
    """Parse a single line from confusables.txt.

    Returns (source_char, substitution) tuple, or None if skip.
    Format: CODEPOINT ; SUBSTITUTION ; TYPE # ... comment
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = line.split(";")
    if len(parts) < 2:
        return None

    source_str = parts[0].strip()
    substitution_str = parts[1].strip()

    # Parse source code point
    source_char = parse_code_point(source_str)
    if source_char is None:
        return None

    # Parse substitution - may be multiple code points
    sub_parts = substitution_str.split()
    if not sub_parts:
        return None

    try:
        # Handle multi-char substitutions by concatenating
        substitution = "".join(chr(int(p.strip(), 16)) for p in sub_parts)
        return (source_char, substitution)
    except (ValueError, OverflowError):
        return None


def parse_confusables(content: str) -> dict[str, str]:
    """Parse confusables.txt content into a dictionary.

    Returns dict mapping source_char -> substitution (may be multi-char).
    """
    result: dict[str, str] = {}
    lines = content.split("\n")

    # Skip header comments
    data_started = False
    for line in lines:
        stripped = line.strip()
        if not data_started:
            if stripped.startswith("0") or stripped.startswith("#"):
                continue
            # First non-comment, non-header line onwards is data
            data_started = True

        parsed = parse_line(line)
        if parsed:
            source, sub = parsed
            result[source] = sub

    return result


def generate_python_file(confusables: dict[str, str]) -> str:
    """Generate Python source for confusables.py."""
    lines = [
        '"""',
        "Unicode confusables table.",
        "",
        "Auto-generated from confusables.txt (Unicode UTS #39).",
        "DO NOT EDIT - regenerate with scripts/generate_confusables.py",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "# Confusables table: codepoint string -> substitution codepoint string(s).",
        "# e.g., 'U+0410' (Cyrillic A) -> 'U+0041' (Latin A)",
        "# Names are derived at runtime via unicodedata.name().",
        "",
        "CONFUSABLES: dict[str, str] = {",
    ]

    # Sort by codepoint for deterministic output
    sorted_items = sorted(confusables.items(), key=lambda x: ord(x[0]))

    for source, sub in sorted_items:
        source_cp = f"U+{ord(source):04X}"
        sub_cps = " ".join(f"U+{ord(c):04X}" for c in sub)
        lines.append(f'    "{source_cp}": "{sub_cps}",')

    lines.append("}")
    lines.append("")
    lines.append("__all__ = [\"CONFUSABLES\"]")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    # Fetch
    content = fetch_confusables_txt()
    print(f"Downloaded {len(content)} bytes")

    # Parse
    confusables = parse_confusables(content)
    print(f"Parsed {len(confusables)} confusable entries")

    # Generate
    python_source = generate_python_file(confusables)

    # Write
    OUTPUT_FILE.write_text(python_source)
    print(f"Wrote {OUTPUT_FILE}")

    # Verify by importing
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from nl_calc.exact import confusables as conf_module

    loaded = conf_module.CONFUSABLES
    print(f"Verified import: {len(loaded)} entries loaded")

    # Spot check
    assert "U+0410" in loaded, "Cyrillic A should be present"
    assert loaded["U+0410"] == "U+0041", "Cyrillic A should map to Latin A"
    print("Spot checks passed!")


if __name__ == "__main__":
    main()
