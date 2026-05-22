# unicode_tools Module Review - Improvement Plan

## Verified Claims

1. **`unicode_script(char: str) -> str`** - Function exists and correctly identifies scripts (Latin, Cyrillic, Greek, Han, Hiragana, Katakana, Arabic, Hebrew, Devanagari, Common, Inherited, Other).

2. **`detect_mixed_scripts(s: str) -> dict`** - Returns correct structure with `mixed_scripts`, `scripts`, and `positions` fields. Ignores Common/Inherited/Other scripts.

3. **`detect_confusables(s: str) -> list[ConfusableInfo]`** - Returns list of ConfusableInfo dicts with index, char, codepoint, name, confusable_with, confusable_name.

4. **`confusables_count(s: str) -> int`** - Fast helper function documented and implemented.

5. **`unicode_scripts(s: str) -> list[str]`** - Batch function that returns script list for all characters.

6. **`_get_script_heuristic()` has `@functools.lru_cache`** - Implemented with `maxsize=128`.

7. **Confusables table source** - Derived from Unicode Standard Annex #39, loaded from `confusables.py`.

8. **Script range heuristics** - `_SCRIPT_RANGES` table matches documented ranges.

## Discrepancies

1. **Documented `@dataclass` vs actual `TypedDict`** - The architecture doc shows `@dataclass class ScriptInfo(TypedDict)` which is invalid Python. The implementation correctly uses plain `class ScriptInfo(TypedDict)`.

2. **Extra script ranges in code vs documentation** - Implementation includes ranges not documented:
   - `Thai` (0x0e00-0x0e7f)
   - `Hangul` (0xac00-0xd7af)
   - `Georgian` (0x10a0-0x10ff)
   - `Armenian` (0x0530-0x058f)
   - `Cherokee` (0x13a0-0x13ff)
   - `Canadian_Aboriginal` (0x1400-0x167f)

3. **Missing `unicode_scripts()` in documentation** - The batch function `unicode_scripts()` exists in code but is not documented in the architecture doc.

4. **`confusables_count()` not documented** - The helper function exists but is not documented.

5. **Documentation shows `@dataclass` for ConfusableInfo** - Same invalid syntax issue as ScriptInfo.

## Bugs Found

1. **Combining mark check ordering** - `visible_repr()` in `primitives.py:273-276` checks variation selectors (U+FE00-U+FE0F) BEFORE checking combining marks category 'M'. This is correct per `primitives.py` implementation notes, but `_get_script_heuristic()` checks category starting with "M" first without explicit variation selector handling. While variation selectors are technically in the `Mn` category, the explicit check before category 'M' in `visible_repr` suggests a pattern that `_get_script_heuristic` may want to follow for consistency.

2. **No explicit BIDI control character handling** - `_get_script_heuristic()` does not check for BIDI control characters (U+202a-U+202e, U+2066-U+2069) which are classified as "Other" but represent significant security concerns. These should arguably be flagged as confusables or at least handled specially.

## Improvements with Priority

### Medium Priority

1. **Update architecture doc to include missing functions** - Add `unicode_scripts()` and `confusables_count()` to the Core Functions section.

2. **Document extra script ranges** - Update `_SCRIPT_RANGES` documentation to include Thai, Hangul, Georgian, Armenian, Cherokee, Canadian_Aboriginal.

3. **Fix documentation syntax** - Change `@dataclass class ScriptInfo(TypedDict)` to `class ScriptInfo(TypedDict)` (remove invalid `@dataclass` decorator).

### Low Priority

4. **Consider BIDI control character detection** - Add explicit handling or warning for BIDI control characters in `_get_script_heuristic()` since they pose security risks in homograph attacks.

5. **Variation selector consistency** - Consider whether `_get_script_heuristic()` should explicitly handle variation selectors (U+FE00-U+FE0F) before the combining mark category check, for consistency with `visible_repr()` pattern.