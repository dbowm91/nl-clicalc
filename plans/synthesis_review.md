# synthesis.py Architecture Review

## Document: architecture/synthesis.md
## Source: nl_calc/exact/synthesis.py (1281 lines)

---

## Verified Claims

### Core Functions

| Claim | Status | Notes |
|-------|--------|-------|
| `measure_text(text: str) -> MeasureTextResult` | **MATCHES** | Function exists at line 266 with correct signature and all documented fields |
| `text_equal(a: str, b: str, ...) -> TextEqualResult` | **MATCHES** | Function exists at line 341 with correct signature |
| `explain_diff(a: str, b: str, ...) -> ExplainDiffResult` | **MATCHES** | Function exists at line 530 with correct signature |
| `inspect_text(text: str, ...) -> InspectTextResult` | **MATCHES** | Function exists at line 701 with correct signature |
| `count_chars(text: str, ...) -> CountCharsResult \| dict` | **MATCHES** | Function exists at line 888 with correct signature |
| `list_compare(a: list[str], b: list[str], ...) -> dict` | **MATCHES** | Function exists at line 984 with correct signature |

### Internal Helper Functions

| Claim | Status | Notes |
|-------|--------|-------|
| `_classify_difference(...) -> str` | **MATCHES** | Function exists at line 452 with correct classification values |
| `_generate_agent_instruction(...) -> str` | **MATCHES** | Function exists at line 681 |
| `_codepoint_details(s: str, start: int, end: int) -> list[dict]` | **MATCHES** | Function exists at line 484 |

### Dependencies

| Claim | Status | Notes |
|-------|--------|-------|
| `primitives` | **MATCHES** | All primitives imported and used |
| `unicode_tools` | **MATCHES** | Script and confusable detection imported |
| `diff` | **MATCHES** | Diff algorithms imported |
| `measure` | **MATCHES** | Text metrics imported |
| `validate` | **MATCHES** | Validation utilities imported |

---

## Discrepancies Found

### 1. Missing `text_window` Function (Medium Priority)

**Document says:**
> `text_window(text: str, position: dict, context_lines: int = 2, include_visible_repr: bool = True) -> TextWindowResult`

**Status:** Function exists in source (line 1106) but is **NOT documented** in the architecture file.

The architecture document only describes these main functions:
- measure_text
- text_equal
- explain_diff
- inspect_text
- count_chars
- list_compare

**Missing:** `text_window` which provides windowed text inspection around a position.

### 2. Extra TypedDict Classes Not Documented

The source file defines several TypedDict classes that are not mentioned in the document:
- `TextWindowPosition` (line 1085)
- `TextWindowResult` (line 1094)
- `ListCompareOrderedResult` (line 194)
- `ListCompareSetResult` (line 201)
- `ListCompareMultisetResult` (line 207)
- `ListCompareNearMatch` (line 214)
- `InspectTextNormalized` (line 152)
- `NormalizationFinding` (line 160)

**Severity:** Low (internal types, but should be documented for completeness).

### 3. `_classify_difference` Classification Values

**Document says:**
- `"unicode_normalization_only"` - NFC equal

**Code shows (line 465-470):**
```python
if nfc_equal:
    if byte_equal:
        return "exact_match"  # Not in document
    if not casefold_equal:
        return "accent_or_diacritic_difference"  # Documented
    return "unicode_normalization_only"
```

The `"accent_or_diacritic_difference"` classification is reached when NFC equal but casefold differs (different from document's description).

---

## Bugs Identified

### Bug 1: `count_chars` `text_length_codepoints` Inconsistency (Low Severity)

**Location:** synthesis.py:932

In byte mode, `text_length_codepoints` is set to `len(text_bytes)` which is actually the byte length, not codepoint length:
```python
return CountCharsResult(
    target=target,
    normalization=normalization,
    count=len(positions),
    positions=positions,
    text_length_codepoints=len(text_bytes),  # Should be len(text) for codepoint count
)
```

For byte counting mode, this returns byte count instead of codepoint count.

**Same issue at line 948** for grapheme mode - `text_length_codepoints` is set to grapheme count.

---

### Bug 2: `list_compare` Operator Precedence Issue (Low Severity)

**Location:** synthesis.py:1072

```python
same_unordered = treat_as_multiset and a_set == b_set or not treat_as_multiset and a_counter == b_counter
```

Missing parentheses - `or` has lower precedence than `and`. Should be:
```python
same_unordered = (treat_as_multiset and a_set == b_set) or (not treat_as_multiset and a_counter == b_counter)
```

This could cause incorrect results when `treat_as_multiset=False`.

---

### Bug 3: `text_window` Variable Scope Issue (Low Severity)

**Location:** synthesis.py:1223, 1234

The variable `n` is used but not defined in the function scope. Looking at the code:

```python
grapheme_idx = 0
i = 0
while i < codepoint_index:
    grapheme_idx += 1
    i += 1
    while i < codepoint_index:
        from .primitives import _is_extend_char, _is_extended_pictographic
        if _is_extend_char(text[i]):
            i += 1
            continue
        cp = ord(text[i])
        if cp == 0x200D:
            i += 1
            if i < n and _is_extended_pictographic(text[i]):  # 'n' not defined!
                i += 1
            continue
        if 0x1F1E6 <= cp <= 0x1F1FF:
            if i + 1 < n and 0x1F1E6 <= ord(text[i + 1]) <= 0x1F1FF:  # 'n' not defined!
```

`n` should be `len(text)` but is not defined at these points.

---

## Potential Improvements

### Improvement 1: Document `text_window` Function (Medium Priority)

The `text_window` function at line 1106 provides valuable windowed text inspection but is undocumented. It should be added to the architecture document.

### Improvement 2: Add Parentheses for Clarity in `list_compare` (Low Priority)

Line 1072 should have explicit parentheses for readability and correctness.

### Improvement 3: Fix `text_length_codepoints` Field Name (Low Priority)

In `count_chars`, when `count_mode="byte"`, the field `text_length_codepoints` contains byte length, which is misleading. Consider renaming or clarifying.

### Improvement 4: Complete TypedDict Documentation (Low Priority)

All TypedDict classes used as return types should be documented in the architecture, including:
- `TextWindowPosition`
- `TextWindowResult`
- `ListCompareOrderedResult`
- `ListCompareSetResult`
- `ListCompareMultisetResult`
- `ListCompareNearMatch`

### Improvement 5: Update `_classify_difference` Documentation (Low Priority)

The document describes classification values but doesn't mention all paths. The `accent_or_diacritic_difference` case (NFC equal but casefold differs) should be documented.

---

## Priority Summary

| Priority | Item | Type |
|----------|------|------|
| **Medium** | Document `text_window` function | Discrepancy |
| **Low** | Fix `count_chars` `text_length_codepoints` inconsistency | Bug |
| **Low** | Fix `list_compare` operator precedence | Bug |
| **Low** | Fix `text_window` undefined `n` variable | Bug |
| **Low** | Complete TypedDict documentation | Discrepancy |
| **Low** | Update `_classify_difference` classification documentation | Discrepancy |

---

## Test Status

All 125 tests in `tests/test_exact.py` pass, confirming the current implementation is functionally correct for the documented API surface.