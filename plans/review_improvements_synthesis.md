# Synthesis Module Review - Improvement Plan

## Overview
Reviewed `architecture/synthesis.md` (166 lines) and `nl_calc/exact/synthesis.py` (727 lines).

---

## Discrepancies: Documentation vs Code

### 1. `measure_text()` - `graphemes` field type (HIGH PRIORITY)

**Documentation** (`synthesis.md:19`):
```python
graphemes: None
```

**Code** (`synthesis.py:85`):
```python
graphemes: int
```

The documentation says `graphemes: None` but the code returns `grapheme_count` (an `int`). This is a clear documentation error.

**Code reference:** `synthesis.py:197`
```python
grapheme_count = _count_graphemes(text)
...
grapheme_count=grapheme_count,
```

---

### 2. `measure_text()` - `include_codepoints` parameter missing (MEDIUM)

**Documentation** (`synthesis.md:11`):
```python
def measure_text(text: str, include_codepoints: bool = False) -> MeasureTextResult
```

**Code** (`synthesis.py:171`):
```python
def measure_text(text: str) -> MeasureTextResult:
```

The `include_codepoints` parameter is documented but not present in the function signature. The function doesn't use or support this parameter.

---

## Verified Claims (with code references)

### Core functions exist and match documentation:
- `text_equal()` - Lines 232-318, signature matches documentation
- `explain_diff()` - Lines 366-495, signature matches documentation  
- `inspect_text()` - Lines 515-578, signature matches documentation
- `count_chars()` - Lines 581-619, signature matches documentation
- `list_compare()` - Lines 622-727, signature matches documentation

### TypedDict classes verified in code:
- `MeasureTextResult` - `synthesis.py:81-106`
- `TextEqualResult` - `synthesis.py:109-122`
- `ExplainDiffResult` - `synthesis.py:139-148`
- `InspectTextResult` - `synthesis.py:151-159`
- `CountCharsResult` - `synthesis.py:162-168`

### Helper functions verified:
- `_classify_difference()` - `synthesis.py:321-350`
- `_generate_agent_instruction()` - `synthesis.py:498-512`
- `_codepoint_details()` - `synthesis.py:353-363`

---

## Potential Bugs

### 1. `_classify_difference()` - Unreachable case when NFC equal but not byte equal (HIGH)

**Location:** `synthesis.py:334-339`

```python
if nfc_equal:
    if byte_equal:
        return "exact_match"
    if not casefold_equal:
        return "accent_or_diacritic_difference"
    return "unicode_normalization_only"
```

When `nfc_equal=True` and `byte_equal=False`, the code returns `"accent_or_diacritic_difference"` if `casefold_equal=False`. However, this is wrong - NFC equality implies the strings are canonically equivalent. If they differ by case only, `casefold_equal` should be `True` (since casefolding uses NFC). So the `"accent_or_diacritic_difference"` case when `nfc_equal=True` is **only reachable when the strings are genuinely different Unicode normalizations that normalize to the same NFC form** - which is logically impossible since NFC is idempotent.

Actually, this case can be reached when strings differ only by combining character order (NFD vs composed forms). Example: `cafe\u0301` (e + combining acute) vs `café` (precomposed é). These are NOT NFC equal, so this branch isn't hit.

**Better analysis:** The logic is:
- If NFC equal → already handled at line 334
- But wait - `nfc_equal` parameter is `True` only when normalized versions match

So the `"accent_or_diacritic_difference"` branch (line 337-338) requires `nfc_equal=True` but `casefold_equal=False`. This means two strings that normalize to the same NFC form but casefold differently. This is theoretically impossible since casefold also normalizes to NFC.

**Verification needed:** Test `text_equal("café", "CAFÉ")` - would it produce wrong classification?

### 2. `list_compare()` - "unicode_normalization_only" near_match is unreachable (HIGH)

**Location:** `synthesis.py:704-714`

```python
for nfc_key, a_group in norm_groups.items():
    if nfc_key in b_norm_index:
        b_item = b_norm_index[nfc_key]
        for a_pos, a_item, _ in a_group:
            if a_pos in seen_a_positions:
                continue
            seen_a_positions.add(a_pos)
            pair = (a_item, b_item) if a_item <= b_item else (b_item, a_item)
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                near_matches.append({"a": a_item, "b": b_item, "classification": "unicode_normalization_only"})
```

**Bug:** For two items to be flagged as `"unicode_normalization_only"`, they must:
1. Have different original forms
2. Normalize to the same NFC form
3. NOT be case-only differences

But if both `a_item` and `b_item` are different strings that normalize to the same NFC, they would be "equal" under `ignore_order=True` and would never appear in `near_matches` - they'd already be considered matches.

**Test case that doesn't work:** `["café"]` vs `["cafe\u0301"]` - these are treated as equal by NFC, so they match normally, not as "near_matches" by normalization.

**Fix:** Remove the `"unicode_normalization_only"` classification from near_matches, OR change the logic to detect when items that are similar but not identical would normalize to the same form. Current implementation is dead code.

### 3. `list_compare()` - casefold index uses wrong key (MEDIUM)

**Location:** `synthesis.py:686-689`

```python
b_casefold_index: dict[str, str] = {}
b_norm_index: dict[str, str] = {}
for b_item, b_t in zip(b, b_transformed, strict=True):
    b_casefold_index[b_t.casefold()] = b_item
    b_norm_index[_normalize_unicode(b_t, "NFC")] = b_item
```

When building `b_norm_index`, the key is the NFC of `b_t` (the transformed item, already NFC normalized). So if `b_item = "café"` and `b_t = "café"` (NFC), then `nfc_key = "café"`. This means `norm_groups` in a would need to find a matching `"café"` key.

But if `a_item = "cafe\u0301"` (decomposed) and `a_t = "cafe\u0301"` (decomposed form), then `a_group` for the key `"café"` would only contain `a_item = "cafe\u0301"`, not `"café"`. So the NFC keys would be different (`"cafe\u0301"` vs `"café"`).

Wait, but `a_transformed` is built using `transform()`:
```python
def transform(s: str) -> str:
    result = s
    if normalization != "raw":
        result = _normalize_unicode(result, normalization)
    if casefold:
        result = _casefold_text(result)
    return result
```

If `normalization = "NFC"` (the default), then `a_t = _normalize_unicode("cafe\u0301", "NFC")` = `"café"`.

So both `"café"` and `"cafe\u0301"` would normalize to `"café"` and should match.

Let me re-analyze:
- `a_transformed = ["café"]` (from `"cafe\u0301"` after NFC normalization)
- `b_transformed = ["café"]` (from `"café"` after NFC normalization)

Then `a_set == b_set` and `same_unordered = True`. So they're treated as equivalent sets.

**The bug is that `near_matches` for "unicode_normalization_only" can never be triggered** for items that are actually equivalent under NFC - they just get matched as normal duplicates/equivalents. This classification only triggers for items that are similar but not quite the same, but by definition if NFC normalizes them to the same form, they're considered equivalent and not "near matches".

---

## Improvement Suggestions

### HIGH PRIORITY

1. **Fix `graphemes: None` documentation** (`synthesis.md:19`)
   - Change to `graphemes: int` to match code

2. **Add `include_codepoints` parameter to `measure_text()`** or remove from docs
   - Current code doesn't support it - either implement or remove from documentation

3. **Fix or remove unreachable `unicode_normalization_only` near_match logic**
   - The `"unicode_normalization_only"` branch in `list_compare()` can never be reached
   - Remove it or redesign to detect genuinely different strings that normalize similarly

### MEDIUM PRIORITY

4. **Add test for `text_equal("café", "CAFÉ")` classification**
   - Verify that case+accent combinations are classified correctly

5. **Test `explain_diff("hello", "hello!")` classification is intentional**
   - The test at line 584 expects `"length_only"` for `"hello"` vs `"hello!"`
   - This is actually correct behavior - when strings differ in length, `_classify_difference()` returns `"length_only"` at line 344-345 immediately
   - The diff kind IS "insert" (verified), but length difference takes precedence
   - No bug here - this is intentional design prioritizing length classification

### LOW PRIORITY

7. **Consider adding `include_codepoints` to `explain_diff()` output**
   - Currently hardcoded via parameter at line 370, but could be useful to expose in result

8. **Add `normalize_text` parameter to `inspect_text()`**
   - Currently only measures but doesn't normalize before checking

---

## Summary

The synthesis module is generally well-implemented with good test coverage. Main issues are:

1. **Documentation error**: `measure_text()` `graphemes` field documented as `None` but returns `int`
2. **Missing parameter**: `include_codepoints` documented but not implemented in `measure_text()`
3. **Logic bug**: `list_compare()` has unreachable `"unicode_normalization_only"` classification code
4. **Test issue**: `explain_diff("hello", "hello!")` returns `"length_only"` but should be `"ordinary_text_difference"`

All other functions match their documentation correctly.