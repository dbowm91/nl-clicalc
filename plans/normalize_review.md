# normalize.py Architecture Review

## Overview
Reviewed architecture document (`architecture/normalize.md`) against implementation (`nl_calc/normalize.py`).

---

## Verified Claims

### Core Purpose
- Document correctly states the purpose: converting natural language math expressions to executable math expressions.

### Main Functions
- `normalize()` - Correctly documented as handling word replacement, percentage conversion, complex number suffix, and whitespace handling.
- `normalize_expression()` - Pipeline order documented correctly: normalize → split_at_operators → convert_from_human_handler → apply_math_functions → unit conversion handling → preprocess.

### Key Responsibilities
All five responsibilities verified:
1. Word-to-Number Conversion - `NUMBER_WORDS` and `word_to_number` mapping
2. Operator Mapping - `OPERATOR_CONVERSIONS`
3. Tokenization - `split_at_operators()`
4. Unit Preprocessing - `_preprocess_units()`
5. Unit Conversion Detection - `_handle_unit_conversion_from_tokens()`

### Data Structures
- `OPERATOR_CONVERSIONS`, `NUMBER_WORDS`, `FUNCTION_MAPPINGS`, `CONSTANT_WORDS`, `STRIPPED_PHRASES` all documented and implemented correctly.

### Performance Optimizations
- LRU cache on `check_if_number()` with 1024 entries - VERIFIED (line 388)
- Pre-sorted `_UNITS_BY_LENGTH` for longest-match unit detection - VERIFIED (line 46)
- Combined regex patterns for single-pass replacement - VERIFIED (lines 335-342, 743-745)

### Constants
- `MAX_INPUT_LENGTH = 10000` - VERIFIED (line 42)
- `MAX_NESTING_DEPTH = 100` - VERIFIED (line 43)

### Dependencies
- Imports from `evaluator.py` and `units.py` correctly documented.

---

## Discrepancies

### 1. Duplicate "Data Structures" Section (Priority: Low)
**Location**: Architecture doc lines 38-76 and 82-102

The Data Structures section appears twice with identical content. Should be consolidated into one section.

### 2. "Unit Conversion Detection" Description Misleading (Priority: Medium)
**Architecture doc states**: "Identifies and handles unit conversion expressions"
**Implementation**: `_handle_unit_conversion_from_tokens()` only detects explicit conversion patterns like `X unit IN target_unit`. It does NOT handle arithmetic expressions with mixed units like `30m + 100ft`.

**Actual behavior**: Mixed-unit arithmetic works due to `_preprocess_units()` adding multiplication (`30m+100ft` → `30*m+100*ft`), not the unit conversion detection function.

---

## Bugs Found

**None identified.** Testing confirmed the implementation works correctly for all documented patterns including "N percent of X" expressions.

---

## Improvements

### Improvement 1: Document Unit Conversion Detection Limitations (Priority: Medium)
**Rationale**: The architecture doc overstates what `_handle_unit_conversion_from_tokens()` does, which could mislead developers.

**Suggested fix**: Update architecture doc to clarify that unit conversion detection only handles explicit "X unit in/as/into/to target_unit" patterns, not mixed-unit arithmetic.

### Improvement 2: Consolidate Duplicate Documentation (Priority: Low)
**Rationale**: The Data Structures section appears twice with identical content.

---

## Priority Summary

| Item | Type | Priority |
|------|------|----------|
| Document unit conversion limitations | Improvement | Medium |
| Duplicate Data Structures section | Discrepancy (Low) | Low |

---

## Testing Notes

- All 346 existing tests pass
- Verified patterns that work correctly:
  - "5 percent of 200" → "0.05*200" → 10.0
  - "50% of 200" → "0.5*200" → 100.0
  - "2m in feet" → explicit unit conversion
  - "30m + 100ft" → "30*m+100*ft" via preprocessing

**No bugs found in the normalize module implementation.**