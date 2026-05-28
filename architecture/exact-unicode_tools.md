# exact/unicode_tools.py — Script and Confusable Detection

Unicode script detection and confusable character identification.

## File: `nl_calc/exact/unicode_tools.py`

## Overview

Detects:
- Unicode scripts (Latin, Cyrillic, Greek, Arabic, Han, etc.)
- Mixed-script strings (potential security issues)
- Confusable homoglyphs (characters that look identical but have different code points)

## Type Definitions

### ScriptInfo (TypedDict)

```python
class ScriptInfo(TypedDict):
    index: int        # Index in string
    char: str         # The character
    script: str       # Script name (e.g., "Latin", "Cyrillic")
    codepoint: str    # "U+XXXX" format
```

### ConfusableInfo (TypedDict)

```python
class ConfusableInfo(TypedDict):
    index: int             # Index in string
    char: str              # The confusable character
    codepoint: str         # "U+XXXX" format
    name: str              # Unicode name
    confusable_with: str   # What it might be confused with
    confusable_name: str    # Confusing character's name
```

## Functions

### `unicode_script(char: str) -> str`

Returns the script of a single character.

```python
unicode_script("A")      # → "Latin"
unicode_script("А")       # → "Cyrillic"
unicode_script("α")       # → "Greek"
unicode_script("中")      # → "Han"
unicode_script("ב")       # → "Hebrew"
unicode_script("あ")      # → "Hiragana"
```

**Returns:** Script name or "Unknown" if not determinable.

### `unicode_scripts(s: str) -> list[str]`

Returns script for all characters in string.

```python
unicode_scripts("Hello")     # → ["Latin", "Latin", "Latin", "Latin", "Latin"]
unicode_scripts("Привет")    # → ["Cyrillic", ...]
unicode_scripts("abc123")    # → ["Latin", "Latin", "Latin", "Latin", "Latin", "Latin"]
```

### `detect_mixed_scripts(s: str) -> dict`

Detects runs of mixed scripts in a string.
Returns dict with keys: `mixed_scripts` (list of ScriptInfo), `scripts` (list), `positions` (list).

```python
detect_mixed_scripts("Hello")       # → {'mixed_scripts': [], 'scripts': [...], 'positions': [...]}
detect_mixed_scripts("Привет")       # → {'mixed_scripts': [], ...}
detect_mixed_scripts("abcЯзык")      # → {'mixed_scripts': [ScriptInfo(index=3, char='Я', script='Cyrillic', codepoint='U+042F'), ...], ...}
```

**Security use case:** Detecting homoglyph attacks (e.g., "p@ypass.com" using Cyrillic 'a')

### `detect_confusables(s: str) -> list[ConfusableInfo]`

Finds characters that might be confusable homoglyphs.

```python
# Latin 'a' confusable with Cyrillic 'а'
detect_confusables("paypal")  # Returns any Cyrillic 'а' found

# Greek 'α' confusable with Latin 'a'
detect_confusables("αjax")   # Returns Greek alpha info
```

### `confusables_count(s: str) -> int`

Fast helper to count confusables without building full list.

```python
confusables_count("access")  # → 0 or more depending on confusables present
confusables_count("а")       # → 1 if Cyrillic 'а' looks like Latin 'a'
```

## Supported Scripts

| Script | Example Characters |
|--------|-------------------|
| Latin | A-Z, a-z |
| Cyrillic | А-Я, а-я (Russian, etc.) |
| Greek | α-ω, Α-Ω |
| Arabic | ا-ي (Arabic letters) |
| Hebrew | א-ת (Hebrew letters) |
| Han | 中, 文 (Chinese) |
| Hiragana | あ, い, う (Japanese) |
| Katakana | ア, イ, ウ (Japanese) |
| Hangul | ㄱ, ㄴ (Korean) |
| Thai | ก-๛ (Thai letters) |
| Devanagari | अ-ह (Hindi, Sanskrit) |

## Confusables Database

Uses `confusables.py` data file (~180KB) which maps:
- Latin characters → similar characters in other scripts
- Greek characters → similar Latin/Cyrillic
- etc.

Key confusables:
| Looks Like | Actual Character | Script |
|------------|------------------|--------|
| a | а | Cyrillic |
| A | А | Cyrillic |
| o | о | Cyrillic |
| e | е | Cyrillic |
| y | у | Cyrillic |
| p | р | Cyrillic |
| c | с | Cyrillic |
| B | В | Cyrillic |
| H | Н | Cyrillic |
| K | К | Cyrillic |
| M | М | Cyrillic |
| T | Т | Cyrillic |
| X | Х | Cyrillic |

## Script Detection Heuristic

The `_get_script_heuristic()` function uses caching for performance:

```python
@lru_cache
def _get_script_heuristic(char: str) -> str:
    # Fast script detection via Unicode blocks
    # Cached to avoid repeated lookups
```

### Algorithm

1. Check if character is in Known script blocks
2. Handle special cases (Latin Extended, Greek Extended)
3. Fall back to character name parsing

## Security Applications

### Homoglyph Attack Detection

```python
def detect_potential_homoglyph_attack(domain: str) -> bool:
    """Check if domain might be using confusable characters."""
    confusables = detect_confusables(domain)
    return len(confusables) > 0
```

### Mixed Script Detection

```python
def check_domain_safety(domain: str) -> bool:
    """Check for mixed scripts in domain (common attack vector)."""
    mixed = detect_mixed_scripts(domain)
    # Normal domains should be single-script
    return len(mixed) <= 1
```

## Dependencies

```
unicode_tools.py
    ├── primitives.py (utf8_bytes, casefold_text)
    └── confusables.py (CONFUSABLES data)
```

## Usage Example

```python
from nl_calc.exact import (
    unicode_script, unicode_scripts,
    detect_mixed_scripts, detect_confusables
)

# Check a string for security issues
text = "p@ypal.com"

# Check for mixed scripts
mixed = detect_mixed_scripts(text)
if mixed:
    print("WARNING: Mixed scripts detected!")

# Check for confusables
confusables = detect_confusables(text)
for c in confusables:
    print(f"Confusable: {c['char']} ({c['name']}) looks like {c['confusable_with']}")
```

## Testing

Test cases should include:
- Pure ASCII (no mixed scripts, no confusables)
- Single non-Latin script (no mixed scripts)
- Mixed scripts (Latin + Cyrillic common in attacks)
- Confusable characters in isolation
- Emoji and ZWJ sequences (should not trigger confusable alerts)
- Empty string