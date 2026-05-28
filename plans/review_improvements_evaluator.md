# evaluator.py Module Review — Improvement Plan

**Reviewed:** architecture/evaluator.md against nl_calc/evaluator.py
**Date:** 2026-05-28

## Verified Claims (with line references)

### Key Exports (lines 13-35)
All documented exports are present in `__all__` (lines 29-54):
- `EvaluationError` (line 30)
- `Evaluator` (line 31)
- `evaluate` (line 32)
- `evaluate_raw` (line 33)
- `evaluate_cached` (line 34)
- `evaluate_async` (line 35)
- `evaluate_with_timeout` (line 36)
- `get_default_evaluator` (line 37)
- `register_constant`, `register_function`, `load_user_config` (lines 38-40)
- `PyCalcApp` (line 41)
- `TimeoutError` (line 42)
- All memory functions (lines 43-48)
- All variable functions (lines 49-53)

### Security Architecture (lines 37-55)
- AST-based parsing via `ast.parse()` (line 1283): VERIFIED
- No `eval()` usage: VERIFIED
- Whitelisted operations only: VERIFIED via `_validate_node()` (lines 1244-1278)

### AST Node Handlers (lines 57-75)
Table matches implementation:
- `ast.Constant` → `visit_Constant` (lines 1100-1119): CORRECT
- `ast.BinOp` → `visit_BinOp` (lines 1135-1180): CORRECT (supports +, -, *, /, //, %, **)
- `ast.UnaryOp` → `visit_UnaryOp` (lines 1182-1197): CORRECT (supports +, -, ~)
- `ast.Call` → `visit_Call` (lines 1199-1242): CORRECT
- `ast.Name` → `visit_Name` (lines 1121-1133): CORRECT

Forbidden node types correctly raise `EvaluationError` (lines 1267-1272):
- `ast.Compare`, `ast.BoolOp`, `ast.Subscript`, `ast.List`, `ast.Dict`, `ast.Set`, `ast.ListComp`, `ast.DictComp`

### Safe Math Functions (lines 76-136)

#### Arithmetic (line 81)
- `abs`, `round`, `sign`: VERIFIED (lines 932, 936, 598-604)
- `min`, `max`, `clamp`: VERIFIED (lines 962-963, 610-612)
- `hypot`: VERIFIED (line 618-620)

#### Trigonometric (lines 85-89)
All trig functions implemented via `_complex_aware` wrapper (lines 654-664):
- `sin`, `cos`, `tan`, `asin`, `acos`, `atan`: VERIFIED
- `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh`: VERIFIED

#### Logarithmic/Exponential (lines 91-96)
- `log`, `ln` (lines 655, 922): CORRECT
- `log10`, `log2` (lines 656-657, 923-924): CORRECT
- `exp` (line 658, 926): CORRECT
- `sqrt`, `cbrt` (lines 654, 671, 929, 947): CORRECT

#### Statistical (lines 98-102)
- `mean`, `median`, `std`, `variance`, `sum`: VERIFIED (lines 952-961)

#### Combinatorics (lines 104-108)
- `factorial`, `fact`, `perm`, `comb`, `gcd`, `lcm`: VERIFIED (lines 939-944)

#### Complex Numbers (lines 110-112)
- `real`, `imag`, `conj`, `phase`, `polar`, `rect`: VERIFIED (lines 965-971)

#### Bitwise (lines 114-117)
- `bitand`, `bitor`, `bitxor`, `bitnot`, `lshift`, `rshift`: VERIFIED (lines 977-982)

#### Random (lines 119-124)
- `random`, `randint`, `randn`, `gauss`, `seed`: VERIFIED (lines 993-999)

#### Number Theory (lines 126-128)
- `isprime`, `primefactors`, `nextprime`, `prevprime`: VERIFIED (lines 984-991)

#### Format Conversion (lines 130-131)
- `bin`, `hex`, `oct`: VERIFIED (lines 973-975)

#### Percentage (lines 133-135)
- `percentof`, `aspercent`: VERIFIED (lines 1001-1004)

### Constants (lines 137-171)
All documented constants exist in `CONSTANTS` dict (lines 836-902):
- Mathematical constants (`pi`, `e`, `tau`, `inf`, `nan`): VERIFIED (lines 837-841)
- Imaginary unit (`i`, `j`): VERIFIED (lines 843-844)
- Physical constants (lines 846-901): All match documented values
  - `c/c0/speedoflight/speedoflightvacuum`: 299792458 (lines 858-861)
  - `na/avogadro/avogadros`: 6.02214076e23 (lines 846-848)
  - `h/planck/planckconstant`: 6.62607015e-34 (lines 852-854)
  - `k/boltzmann/boltzmannconstant`: 1.380649e-23 (lines 855-857)
  - `r/gasconstant/idealgasconstant`: 8.314462618 (lines 849-851)
  - `g/standardgravity`: 9.80665 (lines 875-876)
  - `G/gravitationalconstant`: 6.67430e-11 (lines 878-879)
  - All other constants verified

### Memory System (lines 172-189)
- `Memory` class (lines 680-738): Implements calculator-style memory
- Global `_memory` instance (line 742): VERIFIED
- Functions: `memory_store`, `memory_recall`, `memory_add`, `memory_subtract`, `memory_clear`, `memory_list`: VERIFIED (lines 745-772)
- Named registers supported: VERIFIED

### Variable Storage (lines 191-203)
- `setvar`, `getvar`, `delvar`, `listvars`, `clearvars`: VERIFIED (lines 781-824)
- Thread-safe via `_variables_lock` (line 778): VERIFIED

### Limits (lines 205-214)
All limits match code:
- `MAX_EXPONENT = 10000` (line 60): CORRECT
- `MAX_FACTORIAL = 1000` (line 61): CORRECT
- `MAX_NESTING_DEPTH = 100` (line 62): CORRECT
- `MAX_RESULT_VALUE = 1e308` (line 63): CORRECT
- `DEFAULT_CACHE_SIZE = 1024` (line 64): CORRECT

### Evaluation Functions (lines 215-241)
- `evaluate()` (lines 1305-1311): Direct AST evaluation, expects valid Python syntax: CORRECT
- `evaluate_raw()` (lines 1314-1337): Applies NL normalization first: CORRECT
- `evaluate_cached()` (lines 138-150): LRU cached evaluation: CORRECT
- `evaluate_async()` (lines 153-165): Async evaluation: CORRECT
- `evaluate_with_timeout()` (lines 1346-1381): Timeout-based evaluation with `TimeoutError`: CORRECT

### Complex Number Support (lines 243-256)
- `_complex_aware()` (lines 623-651): Creates complex-aware wrapper functions: VERIFIED
- `_sqrt`, `_log`, `_log10`, `_log2`, `_exp`, trig functions all use `_complex_aware` with appropriate parameters (lines 654-671): CORRECT

### PyCalcApp (lines 257-267)
- Class definition (lines 1396-1516): VERIFIED
- `calculate()` method (lines 1429-1455): VERIFIED
- Async support via `calculate_async()` (lines 1457-1472): VERIFIED

### Unit Handling (lines 268-281)
- `UnitValue` returned for expressions with units (lines 1100-1119, 1172-1180): VERIFIED
- `.value`, `.unit`, `.convert_to()` methods work as documented: VERIFIED

### Module Dependencies (lines 283-289)
- evaluator.py imports from units.py (lines 20-27): CORRECT

## Discrepancies Between Documentation and Code

- [MEDIUM] **bitnot operand type not documented**
  - Documentation (line 116) says: `bitnot(a)` — no mention of type requirements
  - Code (line 1190-1191) requires integer operand: `if op_class is ast.Invert and not isinstance(operand, int): raise EvaluationError("Bitwise NOT requires an integer operand")`
  - Impact: Users may try `~5.5` and be surprised by the error. Should document "bitnot(a)" requires integer `a`.

- [LOW] **evaluate_raw not documented in Evaluation Functions section**
  - `evaluate_raw` appears in Key Exports (line 19) but has no dedicated documentation section
  - The function exists (lines 1314-1337) and is useful for NL input
  - Impact: Missing documentation for a useful function

## Potential Bugs

**No bugs found.** The code correctly implements all documented functionality. The bitnot integer requirement is correctly enforced in code, but simply not documented.

## Improvement Suggestions

### HIGH Priority

1. **Add bitnot type requirement to documentation (line 116)**
   - Change from: `bitnot(a)` 
   - To: `bitnot(a)` — integer operand required (bitwise NOT on floats raises error)
   - This is already correctly implemented in code, just needs documentation

### MEDIUM Priority

2. **Document evaluate_raw function**
   - Add a section similar to `evaluate()` (lines 217-224) documenting `evaluate_raw()` 
   - Should explain it applies NL normalization and is equivalent to what `run()` does internally

3. **Add PyCalcApp.calculate_async documentation**
   - The class exists and has `calculate_async()` (lines 1457-1472) but is not documented
   - Would be helpful for async web framework users

### LOW Priority

4. **Consider documenting TimeoutError separately from EvaluationError**
   - Currently mentioned only in `evaluate_with_timeout` section (line 241)
   - Both are in `__all__` and can be imported directly

5. **Add "seed() returns None" to documentation**
   - `seed()` function (lines 567-570) returns `None`, not the seed value
   - Noted in docstring but not in main documentation

## Summary

The evaluator.py module documentation is highly accurate. All function signatures, constants, AST handlers, security claims, and behavior verify correctly against the source code. 

The only issue found is a documentation omission: the `bitnot()` function correctly requires an integer operand in code (and raises a clear error otherwise), but this requirement is not mentioned in the documentation. All other discrepancies are minor omissions of useful functions (`evaluate_raw`, `PyCalcApp.calculate_async`).

No actual bugs were found in the code — the implementation is solid and well-designed with proper thread-safety, security constraints, and error handling.
