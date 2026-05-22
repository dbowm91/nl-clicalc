# primitives.py Architecture Review

## Verified Claims

| Claim | Status |
|-------|--------|
| `utf8_bytes()` returns raw UTF-8 bytes | ✓ Verified |
| `codepoints()` returns detailed codepoint info | ✓ Verified |
| `normalize_unicode()` handles NFC/NFD/NFKC/NFKD | ✓ Verified |
| `casefold_text()` returns casefolded string | ✓ Verified |
| `raw_equal()` checks byte identity | ✓ Verified |
| `normalized_equal()` checks equality after normalization | ✓ Verified |
| `_INVISIBLE_CHARS` dict structure and contents | ✓ Verified |
| `_VARIATION_SELECTORS` set (U+FE00 to U+FE0F) | ✓ Verified |

## Discrepancies

### 1. `graphemes_estimate` in `MeasureBasic`
- **Documentation**: Claims `graphemes_estimate: None # Not implemented`
- **Actual**: Functioning implementation via `count_graphemes(s)` at line 177
- **Impact**: Documentation is outdated; implementation works correctly

### 2. Missing Documentation for Implemented Functions
The following functions are fully implemented and tested but **not documented** in primitives.md:

- `count_graphemes()` (lines 291-348) - Full UAX #29 grapheme cluster boundary implementation
- `truncate_to_grapheme()` (lines 449-514) - Grapheme-safe truncation
- `_is_extend_char()` (lines 351-368) - Extend class check per UAX #29 GB9
- `_is_extended_pictographic()` (lines 371-395) - Emoji detection
- `_advance_past_sequence()` (lines 398-446) - Special sequence handling

### 3. `visible_repr()` Ordering Note
- The AGENTS.md notes "Variation selector checks must come BEFORE combining mark checks (U+FE00-U+FE0F should be checked before category 'M'). The code at primitives.py:273-276 is correct."
- Implementation order (lines 273-276): VS range check comes before M category check ✓
- Documentation does not explain WHY this ordering matters

## Bugs Found

### HIGH Priority

**1. Dead Code: `_advance_past_sequence()` never called**
- Location: `primitives.py:398-446`
- Issue: This function is never imported or called anywhere in the codebase
- The grapheme cluster counting logic in `count_graphemes()` duplicates this functionality inline
- Recommendation: Either integrate into `count_graphemes()` and remove, or document why it exists

### MEDIUM Priority

**2. VS Detection Inconsistency**
- Location: `find_invisibles()` line 216 vs `visible_repr()` line 273
- `find_invisibles()` uses set membership: `codepoint_val in _VARIATION_SELECTORS`
- `visible_repr()` uses range check: `0xfe00 <= ord(char) <= 0xfe0f`
- Both are functionally equivalent but inconsistent style
- Recommendation: Use consistent approach (prefer set membership for clarity)

**3. `_is_extended_pictographic()` range overinclusive**
- Location: `primitives.py:382`
- Issue: `0x1F300 <= cp <= 0x1FFFF` extends to U+1FFFF which is beyond Unicode range
- Valid emoji: U+1F300 to U+1FAFF (Emoticons block + newer additions)
- Recommendation: Change upper bound to `0x1FAFF` or verify actual emoji range needed

### LOW Priority

**4. Combining mark handling in `visible_repr()`**
- Location: `primitives.py:275-276`
- Current: Only prepends `◌` to combining marks
- Per documentation, should show `◌ + char` (with the combining character itself)
- Current implementation is correct visually but documentation is slightly misleading

**5. Documentation lacks internal constants section**
- The `_is_extend_char()` helper is critical for understanding grapheme counting but is internal
- Consider adding internal helper documentation or restructuring

## Improvements with Priority

### High Priority
1. **Remove dead code** `_advance_past_sequence()` or document its purpose
2. **Update MeasureBasic docstring**: Remove "Not implemented" claim for `graphemes_estimate`
3. **Add missing documentation**: Document `count_graphemes()`, `truncate_to_grapheme()`, and helper functions

### Medium Priority
4. **Standardize VS detection**: Use set membership consistently in `visible_repr()`
5. **Fix emoji range**: Change `0x1FFFF` to `0x1FAFF` or appropriate upper bound

### Low Priority
6. **Clarify visible_repr() ordering**: Add comment explaining VS must be checked before M category
7. **Update visible_repr() docs**: Clarify combining mark display format

## Summary

The primitives.py implementation is largely correct and well-structured. The main issues are:
- Documentation lagging behind implementation (missing functions documented)
- One dead code function that should be removed or integrated
- Minor inconsistencies in detection style between functions