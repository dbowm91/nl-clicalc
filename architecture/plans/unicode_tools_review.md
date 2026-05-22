# unicode_tools.py Architecture Review

## Verified Claims

1. **Purpose**: Script detection and confusable detection for spoofing attacks - MATCHES (lines 1-9)
2. **`unicode_script(char: str) -> str`**: Returns script name - MATCHES (line 98)
3. **Script names returned**: Latin, Cyrillic, Greek, Han, Hiragana, Katakana, Arabic, Hebrew, Devanagari, Common, Inherited, Other - MATCHES (lines 108-109)
4. **Algorithm**: Uses codepoint range heuristics since `unicodedata.script()` may not be available - MATCHES (lines 60-95, _get_script_heuristic)
5. **`detect_mixed_scripts(s: str) -> dict`**: Returns mixed_scripts, scripts, positions - MATCHES (line 117)
6. **ScriptInfo TypedDict**: index, char, script, codepoint - MATCHES (lines 21-26)
7. **`detect_confusables(s: str) -> list[ConfusableInfo]`**: Detects confusables - MATCHES (line 152)
8. **ConfusableInfo TypedDict**: index, char, codepoint, name, confusable_with, confusable_name - MATCHES (lines 29-36)
9. **Data source**: Unicode Standard Annex #39 - MATCHES (lines 7-8)
10. **_SCRIPT_RANGES**: Script range heuristics - MATCHES (lines 40-57)
11. **Dependencies**: unicodedata, confusables - MATCHES
12. **Security applications** (homoglyph attacks, mixed-script spoofing, IDN homograph attacks) - MATCHES

## Discrepancies

1. **Documentation formatting issue**:
   - Code uses `unicode_script` (function name) but doc shows `"unicode_script"` with quotes - minor presentation issue
   - Doc shows `ScriptInfo` as `@dataclass` but code uses TypedDict - functionally equivalent

2. **Missing from documentation**:
   - `_get_script_heuristic()` helper function not documented
   - The function has `@functools.lru_cache(maxsize=128)` decorator for performance - not in docs
   - Note: "Common" and "Inherited" are ignored for mixed-script detection is documented at line 62 and matches code

## Bugs Found

No bugs found. Implementation is correct.

## Improvements

1. **Low Priority**: Update architecture doc to remove quotes around function names
2. **Low Priority**: Add `_get_script_heuristic()` and its lru_cache decorator to documentation
3. **Low Priority**: Change `@dataclass` to `TypedDict` in documentation example for accuracy

## Priority

- **Low**: Documentation improvements only
- **No code changes needed**