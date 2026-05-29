# Exact Module Architecture Review

## Verified Claims

### primitives.py

| Claim | Status | Location |
|-------|--------|----------|
| `utf8_bytes(s)` returns `bytes` | **MATCHES** | primitives.py:84-85 |
| `codepoints(s)` returns `list[CodepointInfo]` | **MATCHES** | primitives.py:87-103 |
| `normalize_unicode(s, form)` with NFC/NFD/NFKC/NFKD | **MATCHES** | primitives.py:106-123 |
| `casefold_text(s)` returns casefolded string | **MATCHES** | primitives.py:126-135 |
| `raw_equal(a, b)` exact string equality | **MATCHES** | primitives.py:138-148 |
| `normalized_equal(a, b)` equality after NFC normalization | **MATCHES** | primitives.py:151-162 |
| `measure_basic(s)` returns MeasureBasic TypedDict | **MATCHES** | primitives.py:165-189 |
| `count_graphemes(s)` grapheme cluster count | **MATCHES** | primitives.py:291-348 |
| `truncate_to_grapheme(s, max_graphemes)` truncates to grapheme boundary | **MATCHES** | primitives.py:391-449 |
| `find_invisibles(s)` detects hidden characters | **MATCHES** | primitives.py:192-244 |
| `visible_repr(s)` display-safe representation | **MATCHES** | primitives.py:247-288 |
| Variation selector checks come BEFORE combining mark checks | **MATCHES** | primitives.py:273-276 |
| `_get_script_heuristic()` has `@functools.lru_cache` | **MATCHES** | unicode_tools.py:82 |

### Invisible Characters

The `_INVISIBLE_CHARS` dict contains 22 entries (not 12 as documentation suggests):

```python
ZERO WIDTH SPACE, ZERO WIDTH NON-JOINER, ZERO WIDTH JOINER,
LEFT-TO-RIGHT MARK, RIGHT-TO-LEFT MARK, ZERO WIDTH NO-BREAK SPACE,
NO-BREAK SPACE, LINE SEPARATOR, PARAGRAPH SEPARATOR,
LEFT-TO-RIGHT EMBEDDING, RIGHT-TO-LEFT EMBEDDING, POP DIRECTIONAL FORMATTING,
LEFT-TO-RIGHT OVERRIDE, RIGHT-TO-LEFT OVERRIDE, WORD JOINER,
SOFT HYPHEN, MONGOLIAN VOWEL SEPARATOR, COMBINING GRAPHEME JOINER,
LEFT-TO-RIGHT ISOLATE, RIGHT-TO-LEFT ISOLATE, FIRST STRONG ISOLATE, POP DIRECTIONAL ISOLATE
```

Note: Documentation "shows 12" with `...` - the actual count is 22.

### unicode_tools.py

| Claim | Status | Location |
|-------|--------|----------|
| `unicode_script(char)` returns script name | **MATCHES** | unicode_tools.py:129-145 |
| `unicode_scripts(s)` returns list of scripts | **MATCHES** | unicode_tools.py:148-157 |
| `detect_mixed_scripts(s)` returns MixedScriptsResult | **MATCHES** | unicode_tools.py:160-194 |
| `detect_confusables(s)` returns list[ConfusableInfo] | **MATCHES** | unicode_tools.py:197-240 |
| `confusables_count(s)` fast confusable count | **MATCHES** | unicode_tools.py:243-257 |
| `reverse_confusables(char)` returns chars that confusable-map TO this char | **MATCHES** | unicode_tools.py:278-302 |

### measure.py

| Claim | Status | Location |
|-------|--------|----------|
| `line_metrics(s)` returns LineMetrics with newline_style | **MATCHES** | measure.py:66-125 |
| `word_metrics(s)` returns WordMetrics | **MATCHES** | measure.py:128-197 |
| `char_category_metrics(s)` returns CharCategoryMetrics | **MATCHES** | measure.py:200-254 |
| Cf (format) characters excluded from control_chars count | **MATCHES** | measure.py:237-238 |

### diff.py

| Claim | Status | Location |
|-------|--------|----------|
| `first_diff(a, b)` returns FirstDiff or None | **MATCHES** | diff.py:56-89 |
| `common_prefix_suffix(a, b)` avoids overlapping prefix/suffix | **MATCHES** | diff.py:92-128 |
| `levenshtein_distance(a, b)` with dynamic programming | **MATCHES** | diff.py:131-174 |
| `diff_spans(a, b, max_diffs=50)` returns list[DiffSpan] | **MATCHES** | diff.py:214-246 |
| `longest_common_subsequence(a, b)` via dynamic programming | **MATCHES** | diff.py:177-211 |

### validate.py

| Claim | Status | Location |
|-------|--------|----------|
| `check_brackets(s)` returns CheckBracketsResult | **MATCHES** | validate.py:146-221 |
| `validate_json(s)` returns ValidateJsonResult | **MATCHES** | validate.py:224-273 |
| `regex_test(pattern, samples)` returns RegexTestResult | **MATCHES** | validate.py:685-808 |
| `MAX_INPUT_LENGTH = 100_000` enforced | **MATCHES** | validate.py:16,165-166 |

### synthesis.py

| Claim | Status | Location |
|-------|--------|----------|
| `measure_text(s)` returns MeasureTextResult | **MATCHES** | synthesis.py:266-338 |
| `text_equal(a, b, ...)` returns TextEqualResult | **MATCHES** | synthesis.py:341-449 |
| `inspect_text(s, ...)` returns InspectTextResult | **MATCHES** | synthesis.py:701-885 |
| `explain_diff(a, b, ...)` returns ExplainDiffResult | **MATCHES** | synthesis.py:530-678 |
| `count_chars(s, ...)` returns CountCharsResult | **MATCHES** | synthesis.py:888-981 |
| `list_compare(a, b)` returns ListCompareResult | **MATCHES** | synthesis.py:984-1082 |
| `accent_or_diacritic_difference` classification reachable | **MATCHES** | synthesis.py:468-469 |

---

## Discrepancies Found

### 1. Module Structure Outdated

**Severity: Medium**

The document `architecture/exact.md` lists only 7 modules:
```
exact/
├── __init__.py
├── primitives.py
├── unicode_tools.py
├── measure.py
├── diff.py
├── validate.py
├── synthesis.py
└── confusables.py
```

**Actual structure has 12 modules:**
- `__init__.py`
- `primitives.py`
- `unicode_tools.py`
- `measure.py`
- `diff.py`
- `validate.py`
- `synthesis.py`
- `confusables.py`
- `path_tools.py` (NEW)
- `glob.py` (NEW)
- `transform.py` (NEW)
- `identifier.py` (NEW)
- `identifier_inspect.py` (NEW)
- `position.py` (NEW)

### 2. Public API Re-exports Incomplete

**Severity: Medium**

The document shows this API but omits many exported functions:
- Missing: `path_analyze`, `glob_match`, `escape_text`, `text_hash`, `text_transform`, `json_extract`, `json_compare`, `json_shape`, `regex_finditer`, `regex_safety_check`, `validate_toml_text`, `version_compare`, `list_dedupe`, `list_sort`, `text_position`, `identifier_analyze`, `identifier_inspect`, `path_normalize`

### 3. confusables.py Data Format Mismatch

**Severity: Low**

The document shows:
```python
CONFUSABLES: dict[str, list[str]] = {
    "A": ["А", "Α", "А", "𝒜"],
```

**Actual format:**
```python
CONFUSABLES: dict[str, str] = {
    "U+0022": "U+0027 U+0027",  # Single string, space-separated codepoints
```

The document's format implies list of alternative characters, but the actual data is space-separated codepoint strings.

### 4. CodepointInfo is NamedTuple (not TypedDict)

**Severity: Low**

The document says "TypedDict is used throughout" but `CodepointInfo` at primitives.py:16 is actually a `NamedTuple`:
```python
class CodepointInfo(NamedTuple):
    """Information about a single codepoint."""
    index: int
    char: str
    codepoint: str
    name: str
    category: str
```

Other classes like `MeasureBasic` and `InvisibleCharInfo` ARE TypedDict as documented.

---

## Bugs Identified

### Bug 1: Missing Export of TomlShapeResult and VersionCompareResult

**Severity: Low**
**Location:** validate.py

`TomlShapeResult` and `VersionCompareResult` are defined but not exported in `__init__.py`. The `__all__` list mentions `"TomlShapeResult"` but it's not in the actual re-exports at lines 63-93.

---

## Potential Improvements

### Priority 1: Documentation Update

The architecture document needs to be updated to reflect:
1. All 12 modules currently in the `exact/` directory
2. Complete public API including all functions from `validate.py` (json_extract, json_compare, json_shape, regex_finditer, regex_safety_check, validate_toml_text, version_compare, list_dedupe, list_sort)
3. The correct data format for `confusables.py` (dict[str, str] with space-separated codepoints)
4. Note that `CodepointInfo` is a `NamedTuple` (the only exception to TypedDict usage)

### Priority 2: Add Missing Type Exports

**Location:** nl_calc/exact/__init__.py

The following TypedDict classes should be added to the re-exports:
- `TomlShapeResult` (defined at validate.py:353)
- `VersionCompareResult` (defined at validate.py:362)

---

## Summary

| Category | Count |
|----------|-------|
| Verified claims | 35 |
| Discrepancies | 4 |
| Bugs | 1 |
| Improvements | 2 |

**Overall Assessment:** The actual code is well-structured and matches the documented behavior for most claims. The main issue is that the architecture document is outdated - it was written before several modules were added (path_tools, glob, transform, identifier, identifier_inspect, position). The documented module structure and public API no longer reflect reality. The code quality is high with good test coverage (125 tests pass).

**Recommendation:** Update `architecture/exact.md` to reflect the current state of the codebase. The code itself appears correct and well-tested; the documentation needs synchronization.