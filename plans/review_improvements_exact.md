# exact Subpackage Review — Improvement Plan

**Reviewed:** architecture/exact.md against nl_calc/exact/*.py
**Date:** 2026-05-28

## Verified Claims (with line references)

### Module Structure (lines 7-17)
- All files listed exist in correct locations: `__init__.py`, `primitives.py`, `unicode_tools.py`, `measure.py`, `diff.py`, `validate.py`, `synthesis.py`, `confusables.py` ✓

### primitives.py (lines 52-115)
- `utf8_bytes(s)` returns `bytes` ✓ (primitives.py:75-84)
- `codepoints(s)` returns `list[CodepointInfo]` ✓ (primitives.py:87-103)
- `CodepointInfo` is a NamedTuple with index, char, codepoint, name, category ✓ (primitives.py:16-22)
- `normalize_unicode(s, form)` ✓ (primitives.py:106-123)
- `casefold_text(s)` ✓ (primitives.py:126-135)
- `raw_equal(a, b)` ✓ (primitives.py:138-148)
- `normalized_equal(a, b)` ✓ (primitives.py:151-162)
- `count_graphemes(s)` ✓ (primitives.py:291-348)
- `truncate_to_grapheme(s, max_len)` ✓ (primitives.py:391-456)
- `find_invisibles(s)` returns `list[InvisibleCharInfo]` ✓ (primitives.py:192-244)
- `visible_repr(s)` ✓ (primitives.py:247-288)
- Invisible characters list matches code ✓ (lines 74-89)

### unicode_tools.py (lines 119-143)
- `unicode_script(char)` ✓ (unicode_tools.py:119-135)
- `unicode_scripts(s)` ✓ (unicode_tools.py:138-147)
- `detect_mixed_scripts(s)` ✓ (unicode_tools.py:150-184)
- `detect_confusables(s)` ✓ (unicode_tools.py:187-230)
- `confusables_count(s)` ✓ (unicode_tools.py:233-247)

### measure.py LineMetrics fields (lines 170-182)
- All fields match: `lines`, `nonempty_lines`, `blank_lines`, `max_line_length_codepoints`, `trailing_whitespace_lines`, `newline_style`, `ends_with_newline` ✓

### measure.py CharCategoryMetrics (lines 157-168)
- All documented categories exist in code: letters, digits, punctuation, symbols, spaces, control_chars, combining_marks ✓ (measure.py:35-43)

### diff.py functions (lines 186-221)
- `levenshtein_distance(a, b)` ✓ (diff.py:131-174)
- `diff_spans(a, b)` ✓ (diff.py:214-246)
- `longest_common_subsequence(a, b)` ✓ (diff.py:177-211)
- `MAX_LEVENSHTEIN_LEN = 10000` ✓ (diff.py:53)

### validate.py (lines 225-270)
- `check_brackets(s)` returns `CheckBracketsResult` with balanced, unmatched_openers, unmatched_closers ✓
- `validate_json(s)` returns `ValidateJsonResult` ✓ (validate.py:170-219)
- `regex_test(pattern, samples)` returns `RegexTestResult` ✓ (validate.py:269-344)
- `MAX_INPUT_LENGTH = 100_000` enforced ✓ (validate.py:14, 111-112, 183-184)
- `BracketError` has char, index, line, column ✓ (validate.py:19-24)
- Handles bracket types: (), [], {}, <> ✓

### synthesis.py (lines 274-332)
- `measure_text(s)` combines basic + categories + lines + words + invisibles + mixed_scripts ✓ (synthesis.py:171-229)
- `text_equal(a, b, ...)` returns TextEqualResult with documented fields ✓
- `inspect_text(s, ...)` returns InspectTextResult ✓ (synthesis.py:515-578)
- `explain_diff(a, b, ...)` returns ExplainDiffResult ✓ (synthesis.py:366-495)
- `count_chars(s, ...)` returns CountCharsResult ✓ (synthesis.py:581-619)
- `list_compare(a, b)` ✓ (synthesis.py:622-727)

### confusables.py (lines 336-353)
- CONFUSABLES is a dict[str, str] ✓ (confusables.py:14)
- __all__ = ["CONFUSABLES"] ✓ (confusables.py:6581)

### Architecture Notes (lines 375-386)
- utf8_bytes() returns bytes (not int count) ✓
- visible_repr() variation selector checks before combining mark checks ✓ (primitives.py:273-276)
- _get_script_heuristic() has @functools.lru_cache ✓ (unicode_tools.py:72)
- Cf (format) characters excluded from control_chars ✓ (measure.py:234-235)
- confusables_count() helper exists ✓ (unicode_tools.py:233-247)
- TypedDict used throughout (not NamedTuple) ✓

---

## Discrepancies Between Documentation and Code

### [HIGH] `FirstDiff` TypedDict fields incorrect in documentation
- **Documentation says** (lines 199-215):
  ```python
  FirstDiff(
      kind=str,            # Not in actual code!
      a_span=list[int],    # Not in actual code!
      ...
  )
  ```
  Actually docs show (line 201-206):
  ```python
  FirstDiff(
      kind=str,            # "equal", "insert", "delete", "replace"
      a_span=list[int],    # [start, end) in string a
      b_span=list[int],    # [start, end) in string b
      a_text=str,
      b_text=str,
  )
  ```
  But this is the `DiffSpan` structure, NOT `FirstDiff`.

- **Code actually does** (diff.py:28-35):
  ```python
  class FirstDiff(TypedDict):
      a_index: int
      b_index: int
      a_char: str
      b_char: str
      a_codepoint: str
      b_codepoint: str
  ```

- **Impact**: Documentation completely misrepresents `FirstDiff`. The documented structure matches `DiffSpan` instead. Anyone relying on documentation would get wrong field names.

### [HIGH] `common_prefix_suffix` return type incomplete in documentation
- **Documentation says** (lines 193, 219-220):
  ```python
  # Line 193 shows only common_prefix_len in table
  | common_prefix_suffix(a, b) | CommonPrefixSuffix | ... |
  
  # Lines 219-220 show:
  >>> common_prefix_suffix("abc123", "abc456")
  # → CommonPrefixSuffix(common_prefix_len=3, common_suffix_len=0)
  ```
  Only `common_prefix_len` shown.

- **Code actually does** (diff.py:38-41, 125-128):
  ```python
  class CommonPrefixSuffix(TypedDict):
      common_prefix_len: int
      common_suffix_len: int
  ```
  Returns BOTH prefix AND suffix lengths.

- **Impact**: Documentation shows incomplete return value. The example shows `common_suffix_len=0` which implies the field exists, but the table doesn't list it.

### [HIGH] `measure_basic` documented in wrong module section
- **Documentation says** (lines 148-156, measure.py section):
  ```python
  | Function          | Returns        | Description |
  | measure_basic(s)  | MeasureBasic   | Basic metrics |
  ```
  This appears under "## measure.py — Text Metrics"

- **Code actually does**: `measure_basic` is defined in `primitives.py` (lines 165-189), NOT in `measure.py`. The `measure.py` module does NOT export `measure_basic`.

- **Impact**: Documentation incorrectly associates `measure_basic` with `measure.py` when it belongs to `primitives.py`.

### [MEDIUM] `reverse_confusables` function missing from documentation
- **Documentation says** (lines 119-142): No mention of `reverse_confusables`
- **Code actually does**: `reverse_confusables` is defined in `unicode_tools.py:268-292` AND exported in `__init__.py:52` and `__all__:108`
- **Impact**: Public API function is undocumented. However, the AGENTS.md notes mention "D1 (reverse confusables) implemented", suggesting this was a deferred item that is now complete but docs weren't updated.

### [MEDIUM] `confusables_count` missing from unicode_tools documentation
- **Documentation says** (lines 127-129): Not listed in the unicode_tools functions table
- **Code actually does**: Function exists at `unicode_tools.py:233-247` and is exported
- **Impact**: Function exists and is exported but not documented in the module's public API table.

### [LOW] `MAX_LEVENSHTEIN_LEN` not documented
- **Documentation says**: No mention of `MAX_LEVENSHTEIN_LEN`
- **Code actually does**: Defined in `diff.py:53` with value `10000`
- **Impact**: Low - constant is exported in `diff.__all__` but is implementation detail.

---

## Potential Bugs

### No bugs found - code appears correct and consistent with itself

Verified:
- `__init__.py` correctly re-exports all public functions from submodules
- `__all__` in each module matches actual exports
- TypedDict definitions in code match usage throughout
- No circular import issues detected
- Input length limits (`MAX_INPUT_LENGTH`, `MAX_TEXT_LENGTH`) properly enforced

---

## Improvement Suggestions

### HIGH Priority

1. **Fix `FirstDiff` documentation** (exact.md:199-215)
   - Current docs show `DiffSpan` structure under `FirstDiff` heading
   - Should show:
   ```python
   FirstDiff(
       a_index=int,        # Position in string a
       b_index=int,        # Position in string b
       a_char=str,         # Character from a
       b_char=str,         # Character from b
       a_codepoint=str,    # "U+XXXX" format
       b_codepoint=str,    # "U+XXXX" format
   )
   ```

2. **Fix `common_prefix_suffix` documentation** (exact.md:193, 219-220)
   - Add `common_suffix_len` to the table and example
   - Example should show a case where suffix > 0, e.g.:
   ```python
   >>> common_prefix_suffix("prefix_middle_suffix", "prefix_other_suffix")
   # → CommonPrefixSuffix(common_prefix_len=7, common_suffix_len=7)
   ```

3. **Move `measure_basic` to correct module section** (exact.md:148-156)
   - `measure_basic` belongs under "## primitives.py" section, not "## measure.py"
   - The measure.py section should only list: `line_metrics`, `word_metrics`, `char_category_metrics`

### MEDIUM Priority

4. **Document `reverse_confusables`** (exact.md)
   - Add to unicode_tools functions table:
   ```
   | reverse_confusables(char) | list[str] | Characters confusable with input |
   ```
   - Add to Public API re-exports section

5. **Document `confusables_count`** (exact.md:127-129)
   - Add to unicode_tools functions table:
   ```
   | confusables_count(s)      | int       | Fast confusable count |
   ```

6. **Add `MAX_LEVENSHTEIN_LEN` to diff.py documentation** (exact.md:186-196)
   - Optionally document the constant

### LOW Priority

7. **Clarify `DiffSpan` vs `FirstDiff` distinction** (exact.md)
   - The documentation shows `DiffSpan` structure right after `FirstDiff` heading, which may cause confusion
   - Consider reorganizing to make clear these are different return types

---

## Summary

The documentation for `exact.md` is mostly accurate but has **4 HIGH/MEDIUM priority discrepancies**:

1. **HIGH**: `FirstDiff` structure is wrong - shows `DiffSpan` structure instead
2. **HIGH**: `common_prefix_suffix` return type incomplete - missing `common_suffix_len`
3. **HIGH**: `measure_basic` placed in wrong module section (measure.py instead of primitives.py)
4. **MEDIUM**: `reverse_confusables` function exists in code but is not documented
5. **MEDIUM**: `confusables_count` exists but is not documented

The code itself is well-structured and consistent. All `__init__.py` re-exports match actual module contents. TypedDict definitions are consistent. No circular dependencies or import issues detected.

The most critical fix needed is correcting the `FirstDiff` documentation which currently describes `DiffSpan` entirely.
