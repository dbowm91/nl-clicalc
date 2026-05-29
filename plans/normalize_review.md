# Architecture Review: normalize.md vs normalize.py

## Overview

This review compares the architecture document `architecture/normalize.md` against the actual implementation in `nl_calc/normalize.py` and identifies bugs, discrepancies, and improvement opportunities.

---

## Verified Claims

### Exports (MATCHES)
**Architecture:** Lists 9 exports
**Code:** `__all__` at lines 27-40 has 12 exports including re-exports

The architecture document's export list is incomplete. It omits `evaluate`, `EvaluationError`, and `UnitValue` which are re-exported for convenience.

### Re-exported Symbols (MATCHES)
**Architecture:** Claims re-exports from evaluator and units modules
**Code:** Lines 23-24 confirm imports; lines 28-30 confirm re-exports

### Data Structures (PARTIAL MATCH)

| Structure | Architecture | Code | Status |
|-----------|--------------|------|--------|
| `OPERATOR_CONVERSIONS` | Shows partial list | Lines 101-118 show more complete list | Architecture incomplete |
| `FUNCTION_MAPPINGS` | Shows examples | Lines 123-217, much larger | Architecture shows examples only |
| `NUMBER_WORDS` | Shows examples | Lines 220-261, complete | Architecture shows examples only |
| `CONSTANT_WORDS` | Shows examples | Lines 279-300 | Architecture shows examples only |
| `STRIPPED_PHRASES` | Full list | Lines 264-276 | MATCHES |

### Core Functions (MATCHES)

| Function | Signature | Status |
|----------|-----------|--------|
| `normalize` | Lines 888-939 | MATCHES |
| `normalize_expression` | Lines 1105-1150 | MATCHES |
| `run` | Lines 1153-1191 | MATCHES |
| `check_if_number` | Lines 388-472 | MATCHES |

### check_if_number Handlers (MATCHES)
Architecture lists: integers, floats, percentages, complex numbers, hex/binary/octal, numbers with units
**Code:** Lines 397-471 confirm all these cases are handled.

### Processing Pipeline (MATCHES)
Architecture shows example flow; code implements similar logic. Minor discrepancy in step ordering but overall approach matches.

### Regex Patterns (MATCHES for float, BUG for int patterns)
Architecture lists all pattern names; code at lines 357-373 confirms presence.

**BUG FOUND:** Float pattern (`^[-+]?[0-9]\d*\.\d+?$`) is correct, BUT:
- Int pattern (`^[-|+]?[0-9]\d*$`) incorrectly allows `|` as a sign character
- Int_number_combine pattern (`^[-|+|*]?[0-9]\d*$`) incorrectly allows `|` and `*` as sign characters

### Constants (MATCHES)
Architecture lists: MAX_INPUT_LENGTH=10000, MAX_NESTING_DEPTH=100, _UNITS_BY_LENGTH, _COMMON_UNITS, _UNIT_PREFIXES
**Code:** Lines 42-97 confirm all values.

### Module Dependencies (MATCHES)
Architecture lists dependencies; code at lines 23-25 confirms exact imports.

### Security Notes (MATCHES)
- No eval() usage: Confirmed (uses AST parsing)
- Input length limits: Line 1125 enforces MAX_INPUT_LENGTH
- Nesting depth limits: Line 924 enforces MAX_NESTING_DEPTH
- Invalid tokens raise ValueError: Line 489

---

## Discrepancies Found

### 1. Architecture Export List Incomplete
**Location:** architecture/normalize.md lines 17-28
**Issue:** Document lists 9 exports but `__all__` has 12. Missing: `evaluate`, `EvaluationError`, `UnitValue`
**Severity:** Low (documentation only)

### 2. OPERATOR_CONVERSIONS Incomplete
**Location:** architecture/normalize.md lines 54-65
**Issue:** Architecture shows `"**": ["^", "raised to", "to the power of"]` but code at line 106 also has `"raised to the power"`. Architecture is incomplete.
**Severity:** Low (documentation only)

### 3. Float Regex Fixed but Int Regex Not
**Location:** architecture/normalize.md (Implementation Notes) claims line 368 was fixed
**Issue:** Float pattern WAS fixed correctly to `[-+]?`, but int patterns (lines 367, 369) still have the erroneous `|` and `*` in character classes. Architecture implies the bug class was fixed, but only float was addressed.
**Severity:** Medium (the bug still exists in int patterns, though low practical impact)

---

## Bugs Identified

### BUG 1: Negative Number Handling - Double Minus Concatenation
**Severity:** HIGH
**Location:** normalize.py lines 762-763 in `split_at_operators`

**Description:**
When input contains "5 minus -2" or similar expressions, the double minus "--" causes incorrect tokenization:
- "5 minus -2" becomes "5--2" after normalization
- This token does not match any special handling pattern
- Falls through to `tokens[i].replace("-", "")` which strips ALL hyphens
- Result: "5--2" becomes "52" instead of being split into ["5", "-", "-2"]

**Root Cause:**
1. The check at line 762 `tokens[i - 1] != "."` uses Python negative indexing when `i=0`, wrapping to the last element instead of properly checking bounds
2. Pattern `^\d+-\d+$` at line 753 only matches single hyphen, not double hyphen

**Reproduction:**
```python
from nl_calc.normalize import normalize_expression, NORMALIZE, PATTERNS
result, code = normalize_expression('5 minus -2', NORMALIZE, PATTERNS)
# Returns: '52' (WRONG - should be '5-(-2)' or similar)
```

**Test Cases Failing:**
- "5 minus -2" → "52" (should be 7)
- "5 minus negative 2" → "52" (should be 7)
- "5 -- 3" → "53" (should be 8)
- "5 - - 3" → "53" (should be 8)

---

### BUG 2: Regex Character Class Contains Pipe (Intentional vs Actual)
**Severity:** LOW (no practical impact)
**Location:** normalize.py lines 367, 369

**Description:**
The int and int_number_combine patterns use `[-|+]?` and `[-|+|*]?` which include `|` and `*` as literal characters in the character class. This means:
- `|` can act as a "sign" (e.g., `|5` matches)
- `*` can act as a "sign" in int_number_combine (e.g., `*5` matches)

**Practical Impact:** LOW - These characters would not normally appear in the token stream from natural language input. The thousands separator only matches commas, so `|` cannot enter through that path.

**Fix:** Change `[-|+]?` to `[-+]?` and `[-|+|*]?` to `[-+*]?` (if multiplication sign is intentional) or `[-+]?` (if only minus/plus should be allowed).

---

## Edge Cases Tested

| Input | Expected | Actual | Status |
|-------|----------|--------|--------|
| "five minus six" | 5-6 | 5-6 | PASS |
| "five-six" | 5-6 | 5-6 | PASS |
| "thirty two" | 32 | 32 | PASS |
| "three hundred twenty two" | 322 | 3*100+22 | PASS |
| "5-2" | 5-2 | 5-2 | PASS |
| "5 . negative two" | 5.-2 | 5.-2 | PASS |
| "5 minus -2" | 7 | 52 | FAIL |
| "5 minus negative 2" | 7 | 52 | FAIL |
| "what is five plus three" | 8 | 5+3 | PASS |
| "10 percent of 200" | 20 | 0.1*200 | PASS |
| "1km in m" | 1000 | convert(1*km,m) | PASS |
| "30m + 100ft" | ~60.48m | 30*m+100*ft | PASS |

---

## Architecture Claims vs Code Summary

| Claim | Status | Notes |
|-------|--------|-------|
| Entry point for NL input | MATCHES | Correct |
| Number word conversion | MATCHES | Working |
| Operator word conversion | MATCHES | Working |
| Function name normalization | MATCHES | Working |
| Physical constant words | MATCHES | Working |
| Unit suffix parsing | MATCHES | Working |
| Filler phrase stripping | MATCHES | Working |
| Uses AST (not eval) | MATCHES | Correct |
| Input length limits | MATCHES | Line 1125 |
| Nesting depth limits | MATCHES | Line 924 |
| Invalid tokens raise ValueError | MATCHES | Line 489 |

---

## Improvements Suggested

### Priority 1 (High) - Bug 1 Fix
The double-minus handling bug is a significant correctness issue. The fix should:
1. Add bounds checking before accessing `tokens[i-1]` at line 762
2. Extend `_should_split_number_minus` or add handler for multi-hyphen patterns like "5--2"

### Priority 2 (Medium) - Architecture Document Update
Update architecture/normalize.md to:
1. Include all 12 exports in the Key Exports section
2. Include "raised to the power" in OPERATOR_CONVERSIONS
3. Clarify that the float regex fix (line 368) did not extend to int patterns

### Priority 3 (Low) - Regex Pattern Cleanup
Fix the int and int_number_combine patterns to remove erroneous `|` and `*` from sign character classes:
- Line 367: `^[-|+]?[0-9]\d*$` → `^[-+]?[0-9]\d*$`
- Line 369: `^[-|+|*]?[0-9]\d*$` → `^[-+]?[0-9]\d*$` (or `^[-+*]?` if multiplication sign is intentional)

---

## Priority Summary

1. **HIGH**: Fix double-minus concatenation bug (lines 762-763) - causes incorrect evaluation
2. **MEDIUM**: Update architecture document to reflect actual exports and OPERATOR_CONVERSIONS
3. **LOW**: Fix int/int_number_combine regex patterns to remove `|` and `*` from sign character class (no practical impact but semantically wrong)
4. **LOW**: Architecture document should clarify the partial nature of the float regex fix
