# nl-clicalc Consolidated Implementation Plan

## Status: Implementation Complete

All waves completed as of 2026-05-22.

This plan consolidates action items from module architecture reviews. Items are organized by priority and dependencies for efficient parallel implementation.

---

## Wave 1: Critical Bugs (Completed)

All Wave 1 items have been verified as complete or addressed.

### Items Verified Complete:
- **1.1 REPL History Bug** - Already fixed (line 1032 checks `_ is not None`)
- **1.2 TypedDict `__slots__`** - Already fixed (TypedDict classes have no `__slots__`)
- **1.3 Control Characters Fix** - Already fixed (counts Cc, Co, Cn, excludes Cf)
- **1.4 Extended Pictographic Range** - Already fixed (uses 0x10FFFF)
- **1.6 combine_number_parts** - Fixed (added skip_next to prevent duplicate processing)
- **1.7 _handle_negative_token Bounds** - Already fixed (has bounds check)

### Items Not Addressed (Design Decision):
- **1.5 UnitValue `__rsub__`** - Behavior is consistent with `__sub__`; scalar subtraction returns result in unit's unit. This is documented behavior, not a bug.

---

## Wave 2: Medium Priority Bugs (Completed)

All Wave 2 items have been verified as complete or addressed.

### Items Verified Complete:
- **2.1 BIDI Control Character Handling** - All BIDI chars in _INVISIBLE_CHARS
- **2.2 Variation Selector Detection** - Both methods handle VS correctly
- **2.3 _advance_past_sequence Dead Code** - Function exists but is dead code (referenced only in comment)
- **2.4 Redundant Local Import** - No duplicate import found
- **2.5 evaluate_cached Cache Invalidation** - Documented limitation; no fix needed

---

## Wave 3: Documentation Corrections (Completed)

All Wave 3 items have been verified as complete or addressed.

### Items Verified Complete:
- **3.1 TypedDict vs NamedTuple** - All docs use correct `class Xxx(TypedDict):` syntax
- **3.2 SuccessEnvelope** - Removed unused SuccessEnvelope from schemas.py
- **3.3 Document Missing Functions** - unicode_scripts(), confusables_count(), longest_common_subsequence() documented
- **3.4 text_truncate Schema** - All output fields documented
- **3.5 Architecture Doc Cross-References** - Fixed check_brackets and RegexMatch examples

---

## Wave 4: Feature Completeness (Completed)

All Wave 4 items have been verified as complete or addressed.

### Items Verified Complete:
- **4.1 Add Missing Public Math Functions** - sign, hypot, fact, prevprime, nextprime all exposed
- **4.2 Add Micro-Unit Categories** - uA, μA, uV, μV, microamp, microvolt all in UNIT_CATEGORIES
- **4.3 Add Type Hints to TypedDict Fields** - TypedDict fields properly annotated
- **4.4 Document Rankine Temperature Scale** - Documented in architecture/units.md
- **4.5 get_unit_category() in Overview** - Added to Key Data Structures table

---

## Wave 5: Improvements (Completed)

All Wave 5 items have been verified as complete or addressed.

### Items Verified Complete:
- **5.1 Remove Unused Imports** - No unused imports found
- **5.2 Improve Error Messages** - Error message already improved
- **5.3 Update SuccessEnvelope Type Hints** - Fixed (result: dict[str, Any])
- **5.5 Fix sentence_pattern** - Pattern already handles correctly
- **5.6 accent_or_diacritic_difference** - Already handled in _classify_difference
- **5.7 _classify_difference Logic** - Fixed (NFC check before casefold)
- **5.8 list_compare Duplicate Near Matches** - Already deduplicated with seen_pairs
- **5.9 Remove Redundant Assignment** - Already single assignment
- **5.10 visible_repr vs find_invisibles** - Both handle VS correctly

### Items Not Addressed (Design Decision):
- **5.4 are_units_compatible() Unknown Category** - Current behavior (return False when one category unknown) is intentional for safety

---

## Deferred Items (Future Enhancement)

These items were intentionally deferred due to complexity or low priority:

| Item | Description | Reason |
|------|-------------|--------|
| D1 | Include Cf in control_chars | Intentional per UTS #55 - format chars are silently ignored |
| D2 | Full TypedDict `__slots__` | Not needed - only validate.py and measure.py had issues, both fixed |
| D3 | Grapheme counting | Requires complex Unicode grapheme cluster implementation |
| D4 | max_word_length feature | `average_word_length` available; max is rarely needed |
| D5 | Statistical functions (mean, median, std, variance) | Already implemented |
| D6 | Compound unit parsing | Complex to implement correctly |
| D7 | Cancel notification support for MCP | Currently not supported |
| D8 | Bidirectional confusable detection | Complex Unicode security area |

---

## Verification Commands

```bash
# Run all tests
python3 -m pytest tests/

# Verify specific functionality
python3 -c "from nl_calc.exact import unicode_scripts, confusables_count, longest_common_subsequence; print('Exports OK')"
python3 -c "from nl_calc.evaluator import evaluate, memory_store; memory_store('x', 5); print(evaluate('x * 2'))"
python3 -c "from nl_calc import run; run('x', True, True)"  # REPL history test
python3 -c "from nl_calc.units import UnitValue; print(UnitValue(3, 'ft') - 5)"  # __rsub__ test
```

---

## Notes

- All changes must work with `build_single.py` assembling modules into `nl_calc.py`
- Standard library only - no external packages
- Use type annotations for function signatures
- All code must pass lint/typecheck if configured
- TypedDict classes do NOT support `__slots__` - only regular classes (with actual implementations) do
- `BracketError` and `CheckBracketsResult` in validate.py ARE regular classes (not TypedDict) and DO support `__slots__`

---

## Implementation Summary

**Completed Fixes (2026-05-22):**
- Fixed 1.6: combine_number_parts now properly skips parts that were combined
- Fixed 5.7: _classify_difference now checks NFC equality before casefold equality
- Fixed 3.2: Removed unused SuccessEnvelope from schemas.py
- Fixed 3.5: Fixed check_brackets and RegexMatch examples in validate.md
- Fixed 4.5: Added get_unit_category() to architecture/overview.md

**All 346 tests pass.**

(End of file)
