# unicode_tools.py - Script Detection and Confusable Detection

## Purpose

Provides functions to detect Unicode scripts and identify confusable homoglyph characters that could be used for spoofing attacks (e.g., Cyrillic 'а' vs Latin 'a').

## Core Functions

### `unicode_script(char: str) -> str`

Determine the Unicode script of a single character.

Returns script name: `"Latin"`, `"Cyrillic"`, `"Greek"`, `"Han"`, `"Hiragana"`, `"Katakana"`, `"Arabic"`, `"Hebrew"`, `"Devanagari"`, `"Common"`, `"Inherited"`, `"Other"`

```python
>>> unicode_script("A")
'Latin'
>>> unicode_script("Ж")
'Cyrillic'
>>> unicode_script("Ω")
'Greek'
>>> unicode_script("日")
'Han'
```

**Algorithm**: Uses codepoint range heuristics since `unicodedata.script()` may not be available in all Python versions.

### `detect_mixed_scripts(s: str) -> dict`

Detect if string contains mixed scripts.

```python
{
    "mixed_scripts": bool,      # True if multiple scripts present
    "scripts": list[str],       # Distinct scripts (excluding Common/Inherited)
    "positions": list[ScriptInfo]  # Positions of non-Common/Inherited chars
}
```

```python
@dataclass
class ScriptInfo(TypedDict):
    index: int
    char: str
    script: str
    codepoint: str  # "U+XXXX"
```

```python
>>> detect_mixed_scripts("HelloМир")
{'mixed_scripts': True, 'scripts': ['Latin', 'Cyrillic'],
 'positions': [{'index': 5, 'char': 'М', 'script': 'Cyrillic', 'codepoint': 'U+041C'},
              {'index': 6, 'char': 'и', 'script': 'Cyrillic', 'codepoint': 'U+0438'},
              {'index': 7, 'char': 'р', 'script': 'Cyrillic', 'codepoint': 'U+0440'}]}
```

**Note**: Ignores `"Common"` and `"Inherited"` scripts for the mixed-script verdict.

### `detect_confusables(s: str) -> list[ConfusableInfo]`

Detect confusable homoglyph characters.

```python
@dataclass
class ConfusableInfo(TypedDict):
    index: int
    char: str
    codepoint: str            # "U+XXXX"
    name: str                 # Unicode name
    confusable_with: str      # Character it looks like
    confusable_name: str      # Unicode name of confusable
```

```python
>>> detect_confusables("pаypal")  # Cyrillic 'а' instead of Latin 'a'
[{'index': 1, 'char': 'а', 'codepoint': 'U+0430',
  'name': 'CYRILLIC SMALL LETTER A',
  'confusable_with': 'a',
  'confusable_name': 'LATIN SMALL LETTER A'},
 {'index': 2, 'char': 'y', 'codepoint': 'U+0443',
  'name': 'CYRILLIC SMALL LETTER YERU',
  'confusable_with': 'y',
  'confusable_name': 'LATIN SMALL LETTER Y'}]
```

## Data Source

The confusables table is derived from **Unicode Standard Annex #39** (https://www.unicode.org/reports/tr39/). The table in `confusables.py` was generated from the official `confusables.txt` file.

## Script Range Heuristics

```python
_SCRIPT_RANGES = [
    (0x0041, 0x005a, "Latin"),      # A-Z
    (0x0061, 0x007a, "Latin"),      # a-z
    (0x00c0, 0x00ff, "Latin"),      # Latin-1 Supplement
    (0x0100, 0x017f, "Latin"),      # Latin Extended-A
    (0x0180, 0x024f, "Latin"),      # Latin Extended-B
    (0x0400, 0x04ff, "Cyrillic"),
    (0x0370, 0x03ff, "Greek"),
    (0x1f00, 0x1fff, "Greek"),
    (0x4e00, 0x9fff, "Han"),
    (0x3000, 0x303f, "CJK"),
    (0x3040, 0x309f, "Hiragana"),
    (0x30a0, 0x30ff, "Katakana"),
    (0x0600, 0x06ff, "Arabic"),
    (0x0590, 0x05ff, "Hebrew"),
    (0x0900, 0x097f, "Devanagari"),
]
```

## Dependencies

- `unicodedata` - Standard library for Unicode data
- `confusables` - Confusables table from `exact/confusables.py`

## Security Applications

These tools help detect:
- **Homoglyph attacks**: "pаypal.com" looks like "paypal.com"
- **Mixed-script spoofing**: Using visually similar characters from different scripts
- **IDN homograph attacks**: Internationalized domain names that look legitimate

## Index

See [overview.md](overview.md) for the module index.