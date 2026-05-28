# normalize.py Module Review — Improvement Plan

**Reviewed:** architecture/normalize.md against nl_calc/normalize.py
**Date:** 2026-05-28

## Verified Claims (with line references)

### Key Exports (lines 17-28)
- `run`, `normalize`, `normalize_expression`, `main`, `print_help`, `NORMALIZE`, `PATTERNS`, `MAX_INPUT_LENGTH`, `MAX_NESTING_DEPTH` are all correctly exported and match `__all__` (lines 27-40)
- `MAX_INPUT_LENGTH = 10000` (line 42) matches documentation (line 222)
- `MAX_NESTING_DEPTH = 100` (line 43) matches documentation (line 223)

### Re-exported Symbols (lines 31-49)
- `evaluate` and `EvaluationError` are correctly re-exported from `evaluator.py` (line 23)
- `UnitValue` is correctly re-exported from `units.py` (line 24)
- All three are listed in `__all__` (lines 28-30)

### Data Structures
- `OPERATOR_CONVERSIONS` (lines 101-119): All mappings match documented structure (lines 53-65)
- `FUNCTION_MAPPINGS` (lines 123-217): All function mappings match documented structure (lines 68-82)
- `NUMBER_WORDS` (lines 219-261): All number words match documented structure (lines 84-99)
- `CONSTANT_WORDS` (lines 278-300): Physical constant mappings match documented structure (lines 101-112)
- `STRIPPED_PHRASES` (lines 263-276): Filler phrases match documented structure (lines 114-128)
- `_COMMON_UNITS` (lines 49-91), `_UNIT_PREFIXES` (lines 94-97), `_UNITS_BY_LENGTH` (line 46): All match documentation (lines 224-226)

### Core Functions
- `normalize()` (lines 888-939): Signature and behavior match documentation (lines 132-141)
- `normalize_expression()` (lines 1105-1150): Signature returns `tuple[str, int]` as documented (line 143)
- `run()` (lines 1153-1194): Signature and behavior match documentation (lines 148-154)
- `check_if_number()` (lines 388-472): Returns dict with `bool`, `converted`, `type` keys as documented (lines 156-175)

### Regex Patterns (lines 194-210)
All PATTERNS entries are correctly compiled in `_build_config()` (lines 357-373):
- `space`, `point`, `negative`, `thousands_separator`, `inline_negative`, `parenthesis`, `operators`, `stripped_chars`, `int`, `float`, `int_number_combine`, `valid_operations`

### Configuration Building
- `_build_config()` (lines 303-375): Words sorted by length descending as documented (line 216)

### Security Notes
- No `eval()` usage — uses AST parsing: CORRECT
- Input length limits enforced at lines 42, 1125-1126: CORRECT
- Nesting depth limits enforced at line 924-925: CORRECT
- Invalid tokens raise `ValueError` (line 489): CORRECT

### Module Dependencies
- normalize.py imports from evaluator (line 23), units (line 24), exact (line 25): CORRECT

## Discrepancies Between Documentation and Code

- [MEDIUM] **Pipeline example shows incorrect number combining**
  - Documentation says (lines 185-186): "Convert number words: [5, +, 3, 100, 20, 2]" then "Combine numbers: [5, +, 322]"
  - Code actually produces: `5+3*100+22` which equals 327, not 322
  - The step 4 shows `[5, +, 322]` implying the combination is `5 + 322 = 327`, but the intermediate shows `[5, +, 3, 100, 20, 2]` which should combine to `5 + 3*100 + 22 = 327`
  - The actual expression is `5+3*100+22`, so step 4 should show `[5, +, 3, *, 100, +, 22]` or explain the multiplication more clearly
  - Impact: Documentation could mislead readers about how "three hundred twenty two" is parsed

- [LOW] **Docstring at line 947 contains incorrect example**
  - normalize.py line 947 docstring says: `"three hundred twenty two" -> 3+100+20+2 -> 125`
  - This is mathematically incorrect: 3+100+20+2 = 125, but "three hundred twenty two" = 3*100 + 22 = 322
  - The code actually produces `3*100+22` which is correct; only the docstring example is wrong
  - Impact: Developer confusion about expected behavior

- [LOW] **Documentation shows incomplete data structure entries**
  - `NUMBER_WORDS` documentation (lines 87-98) shows entries like "10": ["teen", "ten"], but code (lines 219-261) has additional entries not shown: "1000000000": ["billion"], "1000000000000": ["trillion"], etc.
  - `STRIPPED_PHRASES` documentation (lines 114-128) shows 10 items, but code (lines 263-276) has additional: "tell me", "give me", "the "
  - `CONSTANT_WORDS` documentation (lines 101-112) shows 8 entries, code (lines 278-300) has 15 entries
  - Impact: Documentation is incomplete but not misleading; it shows representative samples

## Potential Bugs

**No bugs found.** The code is functioning correctly for the reviewed claims. The only issue is documentation inaccuracy, not code bugs.

## Improvement Suggestions

### HIGH Priority

1. **Fix pipeline example in architecture/normalize.md (lines 176-192)**
   - Step 4 shows `[5, +, 322]` but should clarify that "three hundred twenty two" becomes `3*100+22` (322)
   - Suggest showing the multiplication explicitly: `[5, +, 3, '*', 100, '+', 22]` or a cleaner representation
   - The key issue is that "three hundred" means 3*100, not 3+100

### MEDIUM Priority

2. **Fix docstring at normalize.py:947**
   - Change `"3+100+20+2 -> 125"` to `"3*100+20+2 -> 322"` or similar
   - This docstring is in `_join_number_parts()` and explains the purpose of joining number parts

### LOW Priority

3. **Consider adding more complete data structure documentation**
   - For `NUMBER_WORDS`, `STRIPPED_PHRASES`, `CONSTANT_WORDS`, the docs show representative samples
   - Could add a note like "additional entries exist - see source" or show "..." to indicate incompleteness

4. **Consider adding `evaluate_raw` to normalize.md exports section**
   - While `evaluate_raw` is in `evaluator.__all__`, normalize.py re-exports `evaluate` but not `evaluate_raw`
   - If users are expected to import from normalize.py, consider whether `evaluate_raw` should also be re-exported

## Summary

The normalize.py module documentation is largely accurate. All function signatures, data structures, and security claims verify correctly against the source code. The only issues are:

1. A pipeline example showing an intermediate step that could mislead readers about how compound numbers like "three hundred twenty two" are parsed
2. A docstring containing a mathematically incorrect example (125 instead of 322)

These are documentation-only issues; the actual code implementation is correct and well-designed.
