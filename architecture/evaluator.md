# evaluator.py - AST-Based Expression Evaluator

## Purpose

Safe AST-based evaluation of mathematical expressions without using `eval()`. Supports arithmetic, trigonometric, logarithmic, constant, and unit operations.

## Architecture

Uses Python's `ast` module to parse expressions into an Abstract Syntax Tree, then uses a custom `ast.NodeVisitor` subclass to evaluate only allowed operations.

## Key Classes

### `Evaluator`

AST visitor that evaluates mathematical expressions.

**Constants Registry** (`CONSTANTS`):
- Mathematical: `pi`, `e`, `tau`, `inf`, `nan`, `i`, `j`
- Physical: `avogadro`, `gasconstant`, `planck`, `boltzmann`, `speedoflight`, `elementarycharge`, `faraday`, `amu`, `epsilon0`, `mu0`, `g`, `G`, `rydberg`, `stefan`, `hbar`

**Functions Registry** (`FUNCTIONS`):
- Trigonometric: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`
- Hyperbolic: `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh`
- Logarithmic: `log`, `log10`, `log2`, `log1p`, `exp`, `expm1`
- Power/Root: `sqrt`, `pow`, `cbrt`
- Statistical: `mean`, `median`, `mode`, `std`, `variance`, `sum`, `max`, `min`
- Combinatorics: `factorial`, `gcd`, `lcm`, `perm`, `comb`, `nPr`, `nCr`
- Complex: `real`, `imag`, `conj`, `phase`, `polar`, `rect`
- Bitwise: `bitand`, `bitor`, `bitxor`, `bitnot`, `bitlshift`, `bitrshift`
- Prime: `isprime`, `primefactors`, `nextprime`, `prevprime`
- Random: `random`, `randint`, `randrange`, `uniform`, `randn`, `gauss`, `seed`
- Utility: `clamp`, `hypot`, `round`, `sign`, `degrees`, `radians`
- Memory: `store`, `recall`, `M`, `Mplus`, `Mminus`, `MC`, `MR`
- Variables: `setvar`, `getvar`, `delvar`, `listvars`, `clearvars`
- Units: `temp`, `convert`

### `Memory`

Calculator-style memory registers for storing values.

### `PyCalcApp`

Thread-safe wrapper optimized for webapps with caching and instance isolation.

## Security Features

### Node Validation

`_validate_node()` blocks forbidden node types:
- Subscript, List, Dict, Set
- ListComp, DictComp, SetComp, GeneratorExp
- Lambda, IfExp, Compare, BoolOp
- Attribute access except `math.real`, `math.imag`, `math.conjugate`

### DoS Protection

- `MAX_EXPONENT = 10000` - Maximum exponent value
- `MAX_FACTORIAL = 1000` - Maximum factorial input
- `MAX_NESTING_DEPTH = 100` - Maximum parentheses depth
- `MAX_RESULT_VALUE = 1e308` - Maximum result value

## Public API Functions

| Function | Description |
|----------|-------------|
| `evaluate(expr)` | Pre-normalized expression (no spaces) |
| `evaluate_raw(expr)` | Full pipeline with NL support |
| `evaluate_cached(expr)` | LRU cached evaluation |
| `evaluate_async(expr)` | Async evaluation |
| `evaluate_with_timeout(expr, timeout)` | Timeout-protected evaluation |
| `register_constant(name, value)` | Add custom constant |
| `register_function(name, func)` | Add custom function |
| `load_user_config()` | Load from nl_calc_config.py |

## Complex Number Support

`_complex_aware()` decorator wraps math functions to handle both real and complex inputs:
- `sqrt`, `log`, `log10`, `log2`, `exp` - handle negative reals via complex branch
- `asin`, `acos` - use complex functions when `|x| > 1`

## Unit Handling

`visit_BinOp()` automatically handles unit conversion during arithmetic:
- Addition/subtraction with incompatible units raises error
- Mixed units are converted to left operand's unit