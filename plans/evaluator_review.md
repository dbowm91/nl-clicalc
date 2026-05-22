# Evaluator Module Review

## Summary

The `nl_calc/evaluator.py` module provides safe AST-based evaluation of mathematical expressions without using `eval()`. It uses Python's `ast` module to parse expressions into an Abstract Syntax Tree, then uses a custom `ast.NodeVisitor` subclass to evaluate only allowed operations. The module supports arithmetic, trigonometric, logarithmic, constant, unit operations, complex numbers, statistical functions, combinatorics, bitwise operations, prime functions, random functions, and memory/variable storage.

## Verified Claims

### Core Architecture
- **AST-based evaluation**: Uses `ast.NodeVisitor` subclass (`Evaluator`) - CORRECT
- **Safe evaluation without eval()**: Uses `ast.parse()` with node validation - CORRECT

### Constants Registry (lines 820-873)
The document lists constants that exist in the implementation:
- Mathematical: `pi`, `e`, `tau`, `inf`, `nan`, `i`, `j` - ALL PRESENT
- Physical constants listed in doc (avogadro, gasconstant, planck, boltzmann, speedoflight, etc.) - ALL PRESENT

### Functions Registry (lines 876-993)
The document lists function categories that exist in the implementation:
- Trigonometric: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2` - ALL PRESENT
- Hyperbolic: `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` - ALL PRESENT
- Logarithmic: `log`, `log10`, `log2`, `log1p`, `exp`, `expm1` - ALL PRESENT
- Power/Root: `sqrt`, `pow`, `cbrt` - ALL PRESENT
- Statistical: `mean`, `median`, `mode`, `std`, `variance`, `sum`, `max`, `min` - ALL PRESENT
- Combinatorics: `factorial`, `gcd`, `lcm`, `perm`, `comb`, `nPr`, `nCr` - ALL PRESENT
- Complex: `real`, `imag`, `conj`, `phase`, `polar`, `rect` - ALL PRESENT
- Bitwise: `bitand`, `bitor`, `bitxor`, `bitnot`, `bitlshift`, `bitrshift` - ALL PRESENT
- Prime: `isprime`, `primefactors`, `nextprime`, `prevprime` - ALL PRESENT
- Random: `random`, `randint`, `randrange`, `uniform`, `randn`, `gauss`, `seed` - ALL PRESENT
- Utility: `clamp`, `hypot`, `round`, `sign`, `degrees`, `radians` - ALL PRESENT
- Memory: `store`, `recall`, `M`, `Mplus`, `Mminus`, `MC`, `MR` - ALL PRESENT
- Variables: `setvar`, `getvar`, `delvar`, `listvars`, `clearvars` - ALL PRESENT
- Units: `temp`, `convert` - ALL PRESENT

### Security Features
- **Node Validation**: `_validate_node()` blocks forbidden node types - CORRECT (lines 1205-1235)
- **DoS Protection**: `MAX_EXPONENT = 10000`, `MAX_FACTORIAL = 1000`, `MAX_NESTING_DEPTH = 100`, `MAX_RESULT_VALUE = 1e308` - ALL PRESENT (lines 49-52)

### Public API Functions
- `evaluate(expr)` - PRESENT (line 1262)
- `evaluate_raw(expr)` - PRESENT (line 1271)
- `evaluate_cached(expr)` - PRESENT (line 127)
- `evaluate_async(expr)` - PRESENT (line 142)
- `evaluate_with_timeout(expr, timeout)` - PRESENT (line 1303)
- `register_constant(name, value)` - PRESENT (line 56)
- `register_function(name, func)` - PRESENT (line 62)
- `load_user_config()` - PRESENT (line 68)

### Complex Number Support
- `_complex_aware()` decorator wraps math functions - CORRECT (lines 614-642)
- Complex-aware functions: `sqrt`, `log`, `log10`, `log2`, `exp`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan` - ALL PRESENT

### Unit Handling
- `visit_BinOp()` handles unit conversion during arithmetic - CORRECT (lines 1103-1144)
- Addition/subtraction with incompatible units raises error - CORRECT

### Classes
- **`Evaluator`**: AST visitor class - CORRECT (line 811)
- **`Memory`**: Calculator memory registers - CORRECT (line 664)
- **`PyCalcApp`**: Thread-safe wrapper - CORRECT (line 1349)

## Issues Found

### 1. `evaluate_cached` Missing from `__all__` (line 29-43)
The `__all__` list does not include `evaluate_cached`, even though the architecture document lists it as a public API function and the function is defined at line 127.

**Reference**: `evaluator.py:29-43`

### 2. `evaluate_raw` Misleading Documentation (line 1272-1294)
The docstring for `evaluate_raw` says "skip_validation=True" but this appears to skip the normalization validation, not AST node validation. The AST node validation is always performed by `_validate_node()` called inside `evaluate()`.

**Reference**: `evaluator.py:1289-1291`

### 3. `load_user_config_extended` Not Documented
The architecture document does not mention `load_user_config_extended()` (line 157-176), which extends user configuration to include normalize module customizations (number words, operator words).

**Reference**: `evaluator.py:157-176`

### 4. `TimeoutError` Not Documented
The architecture document lists public API functions but does not mention `TimeoutError` as an exported exception, even though it is part of the public API (`__all__` line 42) and is raised by `evaluate_with_timeout()`.

**Reference**: `evaluator.py:1297-1300, 42`

### 5. `get_default_evaluator()` Not Documented
The architecture document does not mention `get_default_evaluator()` (line 1340), which is part of the public API.

**Reference**: `evaluator.py:1340-1346, 37`

### 6. `_cached_normalize_and_evaluate` Not Exported
The function `_cached_normalize_and_evaluate` (line 115) is used by `evaluate_cached` but is not exported via `__all__` and is not documented. This is a minor internal design issue.

**Reference**: `evaluator.py:115`

### 7. Memory Functions Not Documented
The architecture document lists memory functions (`store`, `recall`, `M`, `Mplus`, `Mminus`, `MC`, `MR`) under the Functions Registry section, but the module-level functions (`memory_store`, `memory_recall`, etc.) are not documented in the Public API Functions table.

**Reference**: `evaluator.py:729-756`

### 8. `_variance_sample` Not Documented
The function `_variance_sample` (line 380) exists and is registered in FUNCTIONS as `"variance_sample"` (line 928), but it is not mentioned in the architecture document's Functions Registry.

**Reference**: `evaluator.py:380, 928`

### 9. Percentage Functions Not Documented
`_percent_of` (line 569) and `_as_percent` (line 574) exist and are registered as `"percentof"`, `"percent_of"`, `"aspercent"`, `"as_percent"` (lines 969-972), but are not mentioned in the architecture document.

**Reference**: `evaluator.py:569-578, 969-972`

### 10. Base Conversion Functions Not Documented
`bin`, `hex`, `oct` functions (lines 941-943) exist but are not listed in the Functions Registry of the architecture document.

**Reference**: `evaluator.py:248-260, 941-943`

### 11. Complex Number Aliases Not Documented
`conjugate` is registered as an alias for `conj` (line 936), but not documented.

**Reference**: `evaluator.py:936`

### 12. Prime Function Aliases Not Documented
`is_prime`, `prime_factors`, `next_prime`, `prev_prime` are registered as aliases (lines 953-959), but not documented.

**Reference**: `evaluator.py:953-959`

### 13. `var` Alias Not Documented
`var` is registered as an alias for `variance` (line 927), but not documented.

**Reference**: `evaluator.py:927`

### 14. Missing `abs` in Functions Registry Documentation
The function `abs` (line 903) exists and is registered in FUNCTIONS, but is not listed in the architecture document's Functions Registry.

**Reference**: `evaluator.py:903`

### 15. Missing `floor`, `ceil`, `trunc` in Functions Registry Documentation
These functions (lines 904-906) exist and are registered, but are not listed in the architecture document's Functions Registry.

**Reference**: `evaluator.py:904-906`

## Improvement Recommendations

### High Priority

1. **Add `evaluate_cached` to `__all__`**
   - **File**: `evaluator.py:29-43`
   - **Issue**: Function is public but not exported
   - **Fix**: Add `"evaluate_cached"` to `__all__` list

2. **Document `TimeoutError` and `get_default_evaluator()` in architecture**
   - **File**: `architecture/evaluator.md:62-74`
   - **Issue**: Missing from Public API Functions table
   - **Fix**: Add `TimeoutError` exception and `get_default_evaluator()` to the table

3. **Document all registered function aliases**
   - **File**: `architecture/evaluator.md:21-35`
   - **Issue**: Many aliases (conjugate, is_prime, prime_factors, next_prime, prev_prime, var, etc.) are not documented
   - **Fix**: Update Functions Registry to include all aliases or clarify that the list shows primary names

### Medium Priority

4. **Document additional functions not in architecture**
   - **File**: `architecture/evaluator.md:21-35`
   - **Issue**: Functions like `percentof`, `percent_of`, `aspercent`, `as_percent`, `bin`, `hex`, `oct`, `abs`, `floor`, `ceil`, `trunc`, `variance_sample` are missing
   - **Fix**: Add a "Additional Functions" section or incorporate into existing categories

5. **Document `load_user_config_extended()`**
   - **File**: `architecture/evaluator.md`
   - **Issue**: Not mentioned anywhere in the architecture document
   - **Fix**: Add to Public API Functions table or document in a separate section

6. **Clarify `evaluate_raw` skip_validation parameter**
   - **File**: `evaluator.py:1272-1294`
   - **Issue**: Docstring implies AST validation is skipped, but normalization validation is what's actually skipped
   - **Fix**: Change docstring to clarify "skip_validation skips normalization validation, not AST security validation"

### Low Priority

7. **Document module-level memory functions**
   - **File**: `architecture/evaluator.md`
   - **Issue**: Memory functions listed under Functions Registry but module-level functions (memory_store, memory_recall, etc.) not documented
   - **Fix**: Add module-level memory functions to Public API Functions table

8. **Add `_cached_normalize_and_evaluate` to exports or mark as private**
   - **File**: `evaluator.py:115`
   - **Issue**: Internal function not clearly marked
   - **Fix**: Either add to `__all__` if intended public, or rename with underscore prefix to indicate private

### Test Recommendations

9. **Verify unit handling in `visit_BinOp`** works correctly for edge cases:
   - When left_unit is None but right_unit exists (line 1138)
   - When neither unit is set but result should be dimensionless (line 1144)

10. **Test `_complex_aware` behavior** with boundary conditions:
    - Verify `asin(2)` returns complex result
    - Verify `acos(2)` returns complex result