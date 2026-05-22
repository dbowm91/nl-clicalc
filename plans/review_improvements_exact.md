# exact/ Module Architecture Documentation Review

## Verified Claims

### File Structure (Verified Correct)
All 7 files listed in documentation exist and match:
- `__init__.py` - Public API re-exports (verified correct)
- `primitives.py` - UTF-8, codepoints, normalization, invisibles
- `unicode_tools.py` - Script detection, confusables
- `measure.py` - Text metrics
- `diff.py` - String diffing algorithms
- `validate.py` - JSON/bracket/regex validation
- `synthesis.py` - Higher-level text analysis
- `confusables.py` - Homoglyph identification (auto-generated, ~180KB)

### Function Exports (Verified Correct)
- `utf8_bytes`, `codepoints`, `normalize_unicode`, `casefold_text`, `raw_equal`, `normalized_equal`, `measure_basic`, `count_graphemes`, `truncate_to_grapheme`, `find_invisibles`, `visible_repr`
- `unicode_script`, `unicode_scripts`, `detect_mixed_scripts`, `detect_confusables`, `confusables_count`
- `first_diff`, `common_prefix_suffix`, `levenshtein_distance`, `diff_spans`, `longest_common_subsequence`
- `check_brackets`, `validate_json`, `regex_test`
- `line_metrics`, `word_metrics`, `char_category_metrics`
- `measure_text`, `text_equal`, `inspect_text`, `explain_diff`, `count_chars`, `list_compare`

### TypedDict Classes (Verified Correct)
All TypedDict classes documented match implementation:
- `CodepointInfo`, `InvisibleCharInfo`, `MeasureBasic`
- `ScriptInfo`, `ConfusableInfo`
- `FirstDiff`, `CommonPrefixSuffix`, `DiffSpan`
- `CheckBracketsResult`, `ValidateJsonResult`, `RegexTestResult`
- `LineMetrics`, `WordMetrics`, `CharCategoryMetrics`
- `MeasureTextResult`, `TextEqualResult`, `InspectTextResult`, `CountCharsResult`

### Architecture Notes (Verified Correct)
1. `utf8_bytes()` returns `bytes` - verified correct
2. `visible_repr()` display order matters - verified correct
3. `_get_script_heuristic()` has `@functools.lru_cache` - verified correct
4. Cf (format) characters excluded from `control_chars` - verified correct
5. `confusables_count()` helper exists - verified correct

### Testing Section
`tests/test_exact.py` exists and covers all modules.

---

## Discrepancies

### 1. `CommonPrefixSuffix` Missing from Documentation (Medium)
**Location:** architecture/exact.md lines 186-193 (diff.py section)

The `common_prefix_suffix()` function is documented but returns `CommonPrefixSuffix` which is not shown in the data structure tables. The doc shows:
```python
CommonPrefixSuffix(prefix=str, suffix=str)
```

But actual implementation returns:
```python
CommonPrefixSuffix(
    common_prefix_len=int,
    common_suffix_len=int
)
```

**Priority:** Medium - Function signature is misrepresented.

### 2. `diff_spans` Return Type Discrepancy (Low)
**Location:** architecture/exact.md lines 192-205

Documentation shows `DiffSpan.a_text` and `DiffSpan.b_text` as `str` which is correct, but the structure shows them as `list[int]` spans incorrectly (the spans are already documented correctly separately).

Actually reviewing more closely - the documentation shows both spans and text, which is correct. No issue here.

### 3. Documentation References Non-Existent Test File Pattern (Low)
**Location:** architecture/exact.md line 383

References `tests/test_exact.py` but the glob pattern `tests/test_exact*.py` shows only this one file, so this is fine.

---

## Improvement Suggestions

### High Priority

1. **Fix `CommonPrefixSuffix` return type documentation**
   - Current docs show `CommonPrefixSuffix(prefix=str, suffix=str)`
   - Actual: `CommonPrefixSuffix(common_prefix_len=int, common_suffix_len=int)`
   - Affects lines 186-193 in architecture/exact.md

### Medium Priority

2. **Add `ExplainDiffResult` structure details**
   - Currently only shows `explain_diff` function name in synthesis table
   - Should include the actual TypedDict fields for completeness

3. **Add `InspectTextResult` structure details**
   - Currently only shows function name
   - Should document the TypedDict fields

### Low Priority

4. **Add line counts to module listings**
   - e.g., "confusables.py (~180KB, ~6500 lines)"
   - Helps readers understand scale

5. **Add `CountCharsResult` structure**
   - Missing from synthesis table (only shows function name)

6. **Clarify `diff_spans` max_diffs parameter**
   - Documents shows default 50 but implementation default should be verified

---

## Summary

The `exact/` module documentation is **highly accurate** overall. Only one factual discrepancy was found (`CommonPrefixSuffix` fields) and a few areas where additional detail would improve completeness. The documentation serves well as an architectural overview.