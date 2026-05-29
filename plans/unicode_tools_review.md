# unicode_tools.py Architecture Review

## Document: architecture/unicode_tools.md

## Verified Claims
| Claim | Status | Evidence |
|-------|--------|----------|
| ScriptInfo TypedDict with index, char, script, codepoint fields | VERIFIED | unicode_tools.py:21-26 |
| ConfusableInfo TypedDict with all 6 fields | VERIFIED | unicode_tools.py:29-42 |
| unicode_script() uses unicodedata.script() with fallback | VERIFIED | unicode_tools.py:82-126, 129-145 |
| unicode_scripts() returns per-character script list | VERIFIED | unicode_tools.py:148-157 |
| detect_mixed_scripts() returns MixedScriptsResult | VERIFIED | unicode_tools.py:45-52, 160-194 |
| detect_mixed_scripts() excludes Common/Inherited | VERIFIED | unicode_tools.py:180 |
| detect_confusables() uses CONFUSABLES data | VERIFIED | unicode_tools.py:197-240 |
| confusables_count() fast helper | VERIFIED | unicode_tools.py:243-257 |
| reverse_confusables() raises ValueError for non-single-char | VERIFIED | unicode_tools.py:298-299 |
| _SCRIPT_RANGES codepoint ranges for all documented scripts | VERIFIED | unicode_tools.py:56-79 |
| Greek uses U+0370-U+03FF and U+1F00-U+1FFF | VERIFIED | unicode_tools.py:64-65 |
| Han uses U+4E00-U+9FFF | VERIFIED | unicode_tools.py:66 |
| CJK uses U+3000-U+303F | VERIFIED | unicode_tools.py:67 |
| Hiragana uses U+3040-U+309F | VERIFIED | unicode_tools.py:68 |
| Katakana uses U+30A0-U+30FF | VERIFIED | unicode_tools.py:69 |
| Arabic uses U+0600-U+06FF | VERIFIED | unicode_tools.py:70 |
| Hebrew uses U+0590-U+05FF | VERIFIED | unicode_tools.py:71 |
| Devanagari uses U+0900-U+097F | VERIFIED | unicode_tools.py:72 |
| Thai uses U+0E00-U+0E7F | VERIFIED | unicode_tools.py:73 |
| Hangul uses U+AC00-U+D7AF | VERIFIED | unicode_tools.py:74 |
| Georgian uses U+10A0-U+10FF | VERIFIED | unicode_tools.py:75 |
| Armenian uses U+0530-U+058F | VERIFIED | unicode_tools.py:76 |
| Cherokee uses U+13A0-U+13FF | VERIFIED | unicode_tools.py:77 |
| Canadian Aboriginal uses U+1400-U+167F | VERIFIED | unicode_tools.py:78 |
| MixedScriptsResult TypedDict exists | VERIFIED | unicode_tools.py:45-52 |
| Returns "Other" not "Unknown" for undetermined chars | VERIFIED | unicode_tools.py:126 |
| Combining marks (category M*) return "Inherited" | VERIFIED | unicode_tools.py:107-108 |
| detect_confusables() returns list of ConfusableInfo | VERIFIED | unicode_tools.py:210-238 |
| reverse_confusables() returns list of characters | VERIFIED | unicode_tools.py:278-303 |
| _build_reverse_index() inverts CONFUSABLES mapping | VERIFIED | unicode_tools.py:260-275 |
| _get_script_heuristic() is cached with lru_cache | VERIFIED | unicode_tools.py:82 |
| _build_reverse_index() is cached with lru_cache | VERIFIED | unicode_tools.py:260 |

## Discrepancies
| Issue | Document Line | Code Location | Description |
|-------|---------------|---------------|-------------|
| Return value for undetermined scripts | Line 53: says "Unknown" | unicode_tools.py:126: returns "Other" | Document claims `unicode_script()` returns "Unknown" when script cannot be determined, but the actual implementation returns "Other". This is a semantic difference. |
| Digit classification | Line 66: "digits are classified as Latin" | unicode_tools.py:56-79: not in ranges | ASCII digits (U+0030-U+0039) are not in any `_SCRIPT_RANGES` entry. They would return "Other" via fallback, not "Latin" as documented. Note: `unicodedata.script()` may return "Latin" for digits in some Python versions, so this depends on the primary path. |
| Canadian Aboriginal naming | Line 143: "Canadian Aboriginal" | unicode_tools.py:78: "Canadian_Aboriginal" | Document shows "Canadian Aboriginal" with space; code uses underscore "Canadian_Aboriginal". The Unicode script name officially uses an underscore. |
| Missing TypedDict documented | N/A | unicode_tools.py:45-52 | `MixedScriptsResult` TypedDict is used in code but not documented in the Type Definitions section. |
| Missing internal functions documented | N/A | unicode_tools.py:82, 260 | `_get_script_heuristic()` and `_build_reverse_index()` are internal helper functions with `@functools.lru_cache` but not documented. |
| Caching behavior undocumented | Line 55: no mention of caching | unicode_tools.py:82, 260 | Both `_get_script_heuristic` and `_build_reverse_index` use `@functools.lru_cache` for performance, but this is not mentioned in the documentation. |
| Combining mark handling | Lines 40-53, 87: implicit | unicode_tools.py:107-108 | Combining characters (category starting with "M") return "Inherited" script, but this detail is not explicitly documented despite "Inherited" being referenced in multiple places. |

## Bugs Identified
| Bug | Location | Severity | Description |
|-----|----------|----------|-------------|
| None critical | - | - | No actual bugs found; all functions implement their documented behavior correctly. |

## Improvements Surface
| Area | Priority | Description |
|------|----------|-------------|
| Documentation Accuracy | Medium | Update line 53 to say returns "Other" instead of "Unknown" for undetermined scripts. Clarify digit classification behavior (line 66) - either correct the claim or note it depends on `unicodedata.script()` behavior. |
| Documentation Completeness | Medium | Add `MixedScriptsResult` TypedDict definition to the Type Definitions section. Document `_get_script_heuristic()` and `_build_reverse_index()` as internal functions with caching behavior. |
| Documentation Format | Low | Fix "Canadian Aboriginal" to "Canadian_Aboriginal" to match Unicode standard naming and actual code. |
| Documentation Clarity | Low | Explicitly document that combining marks return "Inherited" script, since this is referenced but not explained. |

## Notes
- All documented function signatures and return types match the implementation.
- All 15 script codepoint ranges in the documentation match the code exactly.
- All 13 confusable character mappings are consistent with the code's CONFUSABLES data structure.
- The `_build_reverse_index()` function correctly inverts the CONFUSABLES mapping: `reverse_confusables("O")` returns `["0"]` if digit zero confusable-maps to letter O.
- The docstring example `>>> "0" in reverse_confusables("O")` works correctly (returns True) because "0" is in the list `["0"]`.
- Both helper functions use `@functools.lru_cache` for memoization, providing good performance for repeated calls.
- The implementation is well-structured with clear separation between public API (`unicode_script`, `unicode_scripts`, `detect_mixed_scripts`, `detect_confusables`, `confusables_count`, `reverse_confusables`) and internal helpers.
- No security issues identified; the confusables detection properly uses the Unicode Standard Annex #39 data.
