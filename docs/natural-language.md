# Natural Language

nl-clicalc supports natural language input for numbers, operators, and functions.

## Number Words

### Basic Numbers (0-9)

```
zero, one, two, three, four, five, six, seven, eight, nine
```

Example:
```bash
calc "five plus three"
# 5+3 -> 8
```

### Teens (10-19)

```
ten, eleven, twelve, thirteen, fourteen, fifteen, sixteen, 
seventeen, eighteen, nineteen
```

### Tens (20-90)

```
twenty, thirty, forty, fifty, sixty, seventy, eighty, ninety
```

### Scales

```
hundred, thousand, million, billion, trillion, quadrillion, quintillion
```

### Fractions

```
half, quarter, thousandth, millionth, billionth
```

## Combining Numbers

Number words combine according to these rules:

- **Ones + Tens**: "twenty five" → 25 (add)
- **Ones + Scale**: "one hundred fifty" → 150 (add or multiply based on scale)
- **Scale + Scale**: "million billion" → 1,000,000,000,000 (multiply)

```bash
calc "twenty five"           # 25
calc "one hundred fifty"     # 150
calc "two thousand twenty four"  # 2024
calc "five million"          # 5000000
calc "three hundred thousand" # 300000
```

**Note on "point" for decimals**: Use "point" to indicate decimal values:

```bash
calc "three point one four"  # 3.14
calc "one point five"        # 1.5
```

## Stripped Phrases

Certain conversational phrases and filler words are automatically removed before processing:

| Stripped | Reason |
|----------|--------|
| `what's`, `what is` | Question prefixes |
| `calculate`, `compute`, `convert` | Action words |
| `tell me`, `give me` | Request phrases |
| `the`, `a` | Articles |
| `of` | Preposition (in certain contexts) |

```bash
calc "what is five plus three"       # 5+3 -> 8
calc "calculate the square root of 16"  # sqrt(16) -> 4
calc "convert 100 meters to feet"   # 100*m -> 328.084 ft
```

## Operators

| Natural Language | Operator |
|-----------------|----------|
| `plus`, `positive` | `+` |
| `minus`, `negative` | `-` |
| `times`, `multiplied by`, `of` | `*` |
| `divided by`, `over`, `per`, `divide` | `/` |
| `to the power of`, `raised to`, `^` | `**` |
| `mod`, `modulo`, `percent`, `remainder` | `%` |
| `point` | `.` (decimal) |

**Note**: "of" typically maps to multiplication (e.g., "half of 10" → 5), following standard usage in phrases like "a quarter of a pie".

Examples:

```bash
calc "five plus three"
# 5+3 -> 8

calc "ten times five"
# 10*5 -> 50

calc "hundred divided by four"
# 100/4 -> 25

calc "two to the power of ten"
# 2**10 -> 1024
```

## Functions

Natural language function names map to their mathematical equivalents. Use parentheses for arguments:

| Natural Language | Function | Example |
|-----------------|----------|---------|
| `sine`, `sin` | `sin()` | `sin(pi/2)` → 1.0 |
| `cosine`, `cos` | `cos()` | `cos(0)` → 1.0 |
| `tangent`, `tan` | `tan()` | `tan(pi/4)` → 1.0 |
| `arcsine`, `asin` | `asin()` | `asin(1)` → 1.5708 |
| `arccos`, `acos` | `acos()` | `acos(1)` → 0.0 |
| `arctan`, `atan` | `atan()` | `atan(1)` → 0.7854 |
| `logarithm`, `ln`, `log` | `log()` | `log(e)` → 1.0 |
| `square root`, `sqrt` | `sqrt()` | `sqrt(144)` → 12 |
| `absolute`, `abs` | `abs()` | `abs(-5)` → 5 |
| `ceiling`, `ceil` | `ceil()` | `ceil(3.2)` → 4 |
| `floor` | `floor()` | `floor(3.7)` → 3 |

Examples:

```bash
calc "sin(pi/2)"          # 1.0
calc "cos(0)"             # 1.0
calc "sqrt(144)"          # 12
calc "abs(-5)"            # 5
calc "log(e)"             # 1.0
```

**Note**: The "of" pattern (e.g., `square root of 16`) is recognized but arguments must follow differently. For reliable results, use parentheses: `sqrt(16)` not `square root of 16`.

## Parentheses

Use "open" and "close" or actual parentheses:

```bash
calc "open five plus three close times two"
# (5+3)*2 -> 16

calc "(five plus three) times two"
# (5+3)*2 -> 16
```

## Negative Numbers

```bash
calc "negative five"
# -5

calc "minus twenty"
# -20

calc "five minus negative three"
# 5-(-3) -> 8
```

## Conversational Phrases

The following conversational phrases are automatically stripped from input:

```
what's, what is, calculate, compute, convert, tell me, give me, the, of, a
```

Examples:
```bash
calc "what is five plus three"
# 5+3 -> 8

calc "calculate square root of 16"
# sqrt(16) -> 4

calc "convert 100 meters to feet"
# 100m -> 328.084 ft
```

## Examples

### Simple

```bash
calc "two plus two"           # 4
calc "ten minus three"        # 7
calc "five times six"         # 30
```

### Complex

```bash
calc "twenty five times four plus ten"
# 25*4+10 -> 110

calc "one hundred divided by five plus three"
# 100/5+3 -> 23

calc "square root of one hundred forty four"
# sqrt(144) -> 12
```

### With Units

```bash
calc "thirty meters plus one hundred feet"
# 30*m+100*ft -> 60.48 m

calc "five kilometers in miles"
# 5 km -> 3.107 mi
```
