# Evaluator Module Review

## Verified Claims

- **Purpose**: AST-based evaluation using `ast.NodeVisitor` - Correct (evaluator.py:811)
- **Security**: `eval()` not used - Correct
- **Constants**: Physical constants present (avogadro, planck, boltzmann, speedoflight, etc.) - Correct (lines 830-873)
- **Functions Registry**: Comprehensive list including trig, hyperbolic, logarithmic, combinatorial, statistical functions - Correct (lines 876-993)
- **Complex number support**: `_complex_aware` decorator handles complex inputs for sqrt, log, asin, acos - Correct (lines 645-655)
- **DoS Protection**: MAX_EXPONENT=10000, MAX_FACTORIAL=1000, MAX_NESTING_DEPTH=100, MAX_RESULT_VALUE=1e308 - Correct (lines 49-52)
- **Node Validation**: `_validate_node` blocks forbidden node types (Subscript, List, Dict, Lambda, etc.) - Correct (lines 1205-1235)
- **Memory class**: Returns float values, has store/recall/add/subtract/clear/list - Correct (lines 664-756)
- **PyCalcApp**: Thread-safe wrapper with caching - Correct (lines 1353-1473)
- **Public API**: `evaluate`, `evaluate_raw`, `evaluate_cached`, `evaluate_async`, `evaluate_with_timeout` - Correct (lines 1262-1338)

## Discrepancies

### 1. Complex Number Support Documentation Overstates Coverage
**Doc says (line 93-95):**
> `_complex_aware()` decorator wraps math functions to handle both real and complex inputs:
> - `sqrt`, `log`, `log10`, `log2`, `exp` - handle negative reals via complex branch
> - `asin`, `acos` - use complex functions when `|x| > 1`

**Actual code:**
- `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh` in FUNCTIONS use `math.*` directly, NOT complex-aware wrappers
- Only `sin`, `cos`, `tan`, `atan`, `asin`, `acos`, `sqrt`, `log`, `log10`, `log2`, `exp` use `_complex_aware`

**Impact**: `sinh(1+2j)` would fail or produce incorrect results while doc claims hyperbolic functions work with complex numbers.

## Bugs Found

### HIGH PRIORITY

1. **`_cbrt()` Does Not Support Complex Numbers** (line 206-210)
   ```python
   def _cbrt(x: float) -> float:
       if x >= 0:
           return x ** (1 / 3)
       return -((-x) ** (1 / 3))
   ```
   When called with `complex(-8, 0)`, raises `TypeError: '>=' not supported between instances of 'complex' and 'int'`. Should use `_complex_aware(math.cbrt, cmath.cbrt)` pattern like `sqrt` does.

2. **`_median()` Returns Float for Even-Length Lists** (line 346-355)
   When `n` is even, returns `(sorted_args[mid - 1] + sorted_args[mid]) / 2` which is always float even for integer inputs. This is correct behavior for population median, but the function is called `_median` (not `_population_median`). However, `_std()` and `_variance()` also compute population statistics. This appears intentional.

### MEDIUM PRIORITY

3. **Bitwise Operations Convert to `int` Silently** (lines 1006-1010)
   `BitAnd`, `BitOr`, `BitXor`, `LShift`, `RShift` all call `int(a)` which truncates floats silently. No error is raised for non-integer inputs.

4. **Division by Zero in `_as_percent()` Only Checked for Exact Zero** (line 574-578)
   ```python
   if total == 0:
       raise EvaluationError("Cannot divide by zero")
   ```
   Does not handle near-zero values which could produce overflow/inf results.

## Improvements

### MEDIUM PRIORITY

1. **Add Complex-Aware Wrappers for Hyperbolic Functions**
   ```python
   _sinh = _complex_aware(math.sinh, cmath.sinh)
   _cosh = _complex_aware(math.cosh, cmath.cosh)
   _tanh = _complex_aware(math.tanh, cmath.tanh)
   _asinh = _complex_aware(math.asinh, cmath.asinh)
   _acosh = _complex_aware(math.acosh, cmath.acosh)
   _atanh = _complex_aware(math.atanh, cmath.atanh)
   ```
   Rationale: Users expect `sinh(1+2j)` to work based on documentation.

2. **Make `_cbrt` Complex-Aware**
   ```python
   _cbrt = _complex_aware(lambda x: _cbrt_real(x), cmath.cbrt, use_complex_for_negative=True)
   ```
   Rationale: Consistency with `_sqrt` behavior; cube root of negatives should return complex result.

### LOW PRIORITY

3. **Add Type Check for Bitwise Operations**
   Consider raising `EvaluationError` if inputs are not integers rather than silently truncating.

4. **Document `memory_list()` Return Type** (line 754)
   The doc claims it returns `dict[str, float]` which is correct, but `Memory.list_registers()` also returns `{"M": ...}` - this is fine but could be clarified.

5. **Consider Adding `factorial` to `FUNCTIONS` Alias** (line 910)
   `factorial` is aliased but not mapped - should probably add `"factorial": _safe_factorial` to FUNCTIONS dict.

6. **Missing `degrees` and `radians` in `_complex_aware` Coverage**
   These are simple pass-throughs to `math.degrees`/`math.radians` but should be noted as not complex-aware.

## Summary

| Item | Type | Priority |
|------|------|----------|
| `_cbrt()` no complex support | Bug | High |
| Hyperbolic funcs not complex-aware | Discrepancy | Medium |
| Bitwise silent int conversion | Bug | Medium |
| `factorial` not in FUNCTIONS | Bug | Low |
| `as_percent` near-zero check | Bug | Medium |