# primitives.py Architecture Review

## Verified Claims

1. **Purpose**: Low-level Unicode text primitives, deterministic and testable - MATCHES (lines 1-8)
2. **`utf8_bytes(s: str) -> bytes`**: Returns raw UTF-8 bytes - MATCHES (line 75)
3. **`codepoints(s: str) -> list[CodepointInfo]`**: Returns detailed codepoint info - MATCHES (line 87)
4. **`CodepointInfo` NamedTuple**: index, char, codepoint, name, category - MATCHES (lines 16-22)
5. **`normalize_unicode(s: str, form: str) -> str`**: NFC/NFD/NFKC/NFKD support - MATCHES (line 106)
6. **`casefold_text(s: str) -> str`**: Casefolded string - MATCHES (line 126)
7. **`raw_equal(a: str, b: str) -> bool`**: Byte identity check - MATCHES (line 138)
8. **`normalized_equal(a: str, b: str, form: str = "NFC") -> bool`**: Unicode normalization equality - MATCHES (line 151)
9. **`measure_basic(s: str) -> MeasureBasic`**: Basic measurements - MATCHES (line 165)
10. **`find_invisibles(s: str) -> list[InvisibleCharInfo]`**: Finds invisible chars - MATCHES (line 192)
11. **`visible_repr(s: str) -> str`**: Display-safe representation - MATCHES (line 247)
12. **`_INVISIBLE_CHARS`**: Dictionary mapping to (name, display) tuples - MATCHES (lines 46-69)
13. **`_VARIATION_SELECTORS`**: Set of codepoint values - MATCHES (line 72)
14. **Dependencies**: unicodedata, typing - MATCHES

## Discrepancies

1. **Documentation issue**:
   - Architecture doc shows `find_invisibles()` detects "Variation selectors" in the table at lines 119-120, but the code's `visible_repr()` does NOT map variation selectors to markers - they display as themselves
   - Variation selectors (U+FE00-U+FE0F) in `visible_repr()` fall through to the `else` clause at line 287, meaning they display as-is rather than as "⟦VS⟧"
   - This is actually more correct since VS are combining marks, but documentation doesn't reflect this

2. **Missing from documentation**:
   - The `CodepointInfo`, `MeasureBasic`, `InvisibleCharInfo` types are used as return types but their definitions in code are slightly more verbose than examples shown (line 16 vs doc example lines 27-34)
   - The actual implementation returns these types correctly

3. **Potential confusion in visible_repr()**:
   - Line 277-278 has explicit handling for `\u2060` (WORD JOINER) even though it's already in `_INVISIBLE_CHARS` - but this appears intentional for display clarity

## Bugs Found

No actual bugs. Code is correct.

## Improvements

1. **Low Priority**: Update architecture doc to clarify that `visible_repr()` displays variation selectors as themselves (not as markers) since they are combining marks
2. **Low Priority**: Add note that `find_invisibles()` detects VS as "VS" but `visible_repr()` shows them as-is
3. **Low Priority**: The WORD JOINER handling at line 277-278 is redundant but harmless - could be removed but no need

## Priority

- **Low**: Documentation clarification about VS handling
- **Low**: No code changes needed