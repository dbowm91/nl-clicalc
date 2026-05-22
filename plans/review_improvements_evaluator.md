# Evaluator Module Review - Improvement Plan

## Verified Claims (with line references)

### AST-Based Evaluation
- **Confirmed**: `evaluate()` at line 1280 uses `ast.parse()` for safe AST-based evaluation (not `eval()`)
- **Confirmed**: `_validate_node()` at line 1219 validates all nodes and forbids dangerous types like `ast.Subscript`, `ast.Lambda`, `ast.IfExp`, `ast.Compare`, `ast.BoolOp`
- **Confirmed**: `Evaluator` class (line 821) implements `ast.NodeVisitor` pattern with `visit_*` methods

### Operator Handling
- **Confirmed**: `BINOPS` dict at line 1007 maps all arithmetic operators including bitwise
- **Confirmed**: `UNARYOPS` dict at line 1024 handles `+`, `-`, `~`
- **Confirmed**: Bitwise operations require integers (line 1151-1152)

### Function Implementations
- **Confirmed**: Trigonometric functions (line 888-893) use `_complex_aware` wrapper
- **Confirmed**: Statistical functions (`_mean`, `_median`, `_mode`, `_std`, `_variance`) at lines 217-370
- **Confirmed**: Random functions at lines 529-564 use dedicated `_random_generator` instance
- **Confirmed**: Complex number functions at lines 308-342

### Security Limits
- **Confirmed**: `MAX_EXPONENT = 10000` (line 60) enforced in `_safe_pow()`
- **Confirmed**: `MAX_FACTORIAL = 1000` (line 61) enforced in `_safe_factorial()`
- **Confirmed**: `MAX_NESTING_DEPTH` and `MAX_RESULT_VALUE` defined at lines 62-63

### Unit Handling
- **Confirmed**: `visit_Constant()` at line 1078 parses unit suffixes
- **Confirmed**: `visit_BinOp()` at line 1113 handles unit conversion for addition/subtraction

---

## Discrepancies Between Documentation and Code

### 1. Missing `fact` Alias (HIGH priority)
**Documentation**: `evaluator.md` line 105 says `factorial(n)` / `fact(n)` are equivalent
**Code**: `FUNCTIONS` dict (line 920) only has `"factorial": _safe_factorial` - `fact` is missing

### 2. Missing `wien` Constant (MEDIUM priority)
**Documentation**: `evaluator.md` line 162 lists `wien` constant as 2.897771955e-3
**Code**: `CONSTANTS` dict (line 830-883) does NOT contain `wien` or `wienconstant`

### 3. Missing `me`, `mp`, `mn`, `re`, `alpha` Constants (MEDIUM priority)
**Documentation**: `evaluator.md` lines 155-159 list electron/proton/neutron mass, electron radius, fine structure constant
**Code**: `CONSTANTS` dict only has:
- `mu0` (line 867) but NOT `me`, `mp`, `mn`, `re`, `alpha`

Note: `mu0` IS present at line 867.

### 4. `evaluate_raw()` Description Mismatch (LOW priority)
**Documentation**: `evaluator.md` line 220-221 says "Evaluates with NL normalization (calls `normalize_expression` first)"
**Code**: `evaluate_raw()` at line 1289 does NOT call `normalize_expression` - it calls `normalize_expression` with `skip_validation=True` which is different behavior

---

## Potential Bugs

### Bug 1: Bitwise NOT on Float Returns Integer (MEDIUM priority)
**Location**: `evaluator.py:1027`
```python
ast.Invert: (lambda x: ~int(x)),
```
For `~5.5`, this returns `-6` (bitwise NOT of integer 5), not an error. Should raise an error for non-integers.

### Bug 2: `primefactors` Returns String Instead of List (MEDIUM priority)
**Location**: `evaluator.py:475`
```python
def _prime_factors(n: int) -> str:
```
Returns `"2 × 3 × 5"` as a formatted string. For consistency with other functions that return lists (e.g., `gcd` returns integer), this should return a list or the formatted output should be configurable.

### Bug 3: `variance` vs `variance_sample` Naming Inconsistency (LOW priority)
**Location**: `evaluator.py:936-938`
```python
"variance": _variance,
"var": _variance,
"variance_sample": _variance_sample,
```
Both `var` and `variance` map to population variance. This is fine, but the sample variance has a different name `variance_sample` while it could also be aliased as `var_s` or similar.

---

## Improvement Suggestions

### HIGH Priority

1. **Add `fact` alias**
   - Location: `evaluator.py` line 920
   - Change: Add `"fact": _safe_factorial,` alongside `"factorial": _safe_factorial,`
   - Reason: Documentation promises this alias

2. **Add missing physical constants**
   - Location: `evaluator.py` lines 830-883
   - Add: `me` (9.1093837015e-31), `mp` (1.67262192369e-27), `mn` (1.67493e-27), `re` (2.817952326e-15), `alpha` (7.2973525693e-3), `wien` (2.897771955e-3)
   - Reason: Documentation lists these constants

3. **Fix `ast.Invert` to reject floats**
   - Location: `evaluator.py:1027`
   - Change: Check if input is integer, raise `EvaluationError` if float
   - Reason: Bitwise NOT on floats is typically unintended

### MEDIUM Priority

4. **Add `fact` alias for combinatorics**
   - Location: `evaluator.py` line 924
   - Add: `"nCr": _comb,` could also have `"nPr": _perm,` (already present at 925)
   - Already has `nCr` at line 926

5. **Document the `skip_validation=True` behavior difference**
   - Location: Either in `evaluator.md` or change `evaluate_raw()` to match docs
   - Reason: Currently `evaluate_raw()` skips validation which may be intentional but differs from documentation

6. **Consider adding `fact` to combinatorics aliases**
   - Add `"fact": _safe_factorial` near line 925

### LOW Priority

7. **Consider adding `round` overload variants**
   - `round(5.5)` → 6 (banker's rounding) vs `round(5.5, 0)` → 6.0
   - Already works correctly via Python's `round()`

8. **Consider adding `median` aliased as `med`**
   - Consistency with other short aliases

9. **`variance_sample` alias**
   - Add `"vars"` or `"var_sample"` as aliases for sample variance

---

## Summary

The evaluator module is well-architected with strong security boundaries. The AST-based approach is sound, and most functions work correctly. Main issues are:

1. **Missing `fact` alias** - documented but not implemented
2. **Missing physical constants** (`me`, `mp`, `mn`, `re`, `alpha`, `wien`) - listed in docs but absent in code
3. **Bitwise NOT accepts floats** - potential bug for type safety

The module correctly uses `evaluate_raw()` or `run()` for NL/unit expressions, not `evaluate()` directly, which aligns with the architecture documentation.