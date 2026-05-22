# normalize.py Architecture Review

## Verified Claims

1. **Purpose**: Correctly describes that normalize.py converts NL math expressions to executable expressions
2. **Main Functions**:
   - `normalize()` - exists (line 734), applies word replacements, percentage conversion, complex number suffix handling, whitespace handling - MATCHES
   - `normalize_expression()` - exists (line 901), has skip_validation parameter - MATCHES
   - `check_if_number()` - exists (line 388) with lru_cache(maxsize=1024) - MATCHES

3. **Data Structures**:
   - `OPERATOR_CONVERSIONS` - exists (line 101), contains all documented operators - MATCHES
   - `NUMBER_WORDS` - exists (line 220), contains mappings from "0"-"quintillion" plus fractions - MATCHES
   - `FUNCTION_MAPPINGS` - exists (line 123), comprehensive function name mappings - MATCHES
   - `CONSTANT_WORDS` - exists (line 279), physical constant mappings - MATCHES
   - `STRIPPED_PHRASES` - exists (line 264), filler words removal list - MATCHES

4. **Performance Optimizations**:
   - `_UNITS_BY_LENGTH` - exists (line 46), pre-sorted unit list - MATCHES
   - `_UNIT_PREFIXES` - exists (line 94), O(1) prefix lookup set - MATCHES
   - LRU cache on `check_if_number()` (1024 entries) - MATCHES

5. **Constants**:
   - `MAX_INPUT_LENGTH = 10000` - exists (line 42) - MATCHES
   - `MAX_NESTING_DEPTH = 100` - exists (line 43) - MATCHES

6. **Dependencies** - All imports match: `evaluator.py` (EvaluationError, evaluate), `units.py` (UnitValue, UNIT_ALIASES, is_unit, UNIT_CATEGORIES), `exact` (inspect_text, count_chars, regex_test) - MATCHES

## Discrepancies

1. **Documentation error**: The architecture doc shows `NUMBER_WORDS` and `OPERATOR_CONVERSIONS` twice (lines 39-75 and 82-102) - duplicate/redundant

2. **Missing from documentation**:
   - `_preprocess_units()` function (line 784) is not documented but handles unit preprocessing
   - `_handle_unit_conversion_from_tokens()` function (line 842) is not documented
   - `split_at_operators()` function (line 692) is not documented
   - `convert_from_human_handler()` function (line 618) is not documented
   - `apply_math_functions()` function (line 554) is not documented
   - `validate_for_eval()` function (line 475) is not documented
   - `_build_config()` function (line 303) is not documented
   - `_COMMON_UNITS` list (line 49) is not documented
   - `_UNIT_PREFIXES` set (line 94) is not explicitly mentioned in docs

3. **Documentation mentions "Unit Preprocessing" as a responsibility but doesn't document `_preprocess_units()` or `_handle_unit_conversion_from_tokens()`**

## Bugs Found

No bugs found. The code appears to be correctly implemented.

## Improvements

1. **Documentation**: Add missing functions to architecture doc:
   - `_preprocess_units()` - adds multiplication before units
   - `_handle_unit_conversion_from_tokens()` - handles "X in Y" unit conversion patterns
   - `split_at_operators()` - tokenizes at operator boundaries
   - `convert_from_human_handler()` - converts number words to numeric values
   - `apply_math_functions()` - converts function names to math function calls

2. **Documentation structure**: Remove duplicate data structure section (lines 82-102 is redundant with lines 39-75)

3. **Documentation**: Add `_COMMON_UNITS` and `_UNIT_PREFIXES` to performance optimizations section

## Priority

- **Medium**: Update architecture doc to include missing functions
- **Low**: Remove duplicate data structure section in documentation