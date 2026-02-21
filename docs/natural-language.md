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

Numbers can be combined:

```bash
calc "twenty five"           # 25
calc "one hundred fifty"     # 150
calc "two thousand twenty four"  # 2024
calc "five million"          # 5000000
```

## Operators

| Natural Language | Operator |
|-----------------|----------|
| `plus`, `positive` | `+` |
| `minus`, `negative` | `-` |
| `times`, `multiplied by` | `*` |
| `divided by`, `over`, `per`, `divide` | `/` |
| `to the power of`, `raised to` | `**` |
| `mod`, `modulo`, `percent`, `remainder` | `%` |

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

Natural language function names:

| Natural Language | Function |
|-----------------|----------|
| `square root of`, `sqrt` | `sqrt()` |
| `cube root`, `cbrt` | `cbrt()` |
| `sine of`, `sin` | `sin()` |
| `cosine of`, `cos` | `cos()` |
| `tangent of`, `tan` | `tan()` |
| `arcsine`, `inverse sine` | `asin()` |
| `arccos`, `inverse cosine` | `acos()` |
| `arctan`, `inverse tangent` | `atan()` |
| `logarithm of`, `ln`, `log` | `log()` |
| `absolute value of`, `abs`, `magnitude` | `abs()` |
| `ceiling`, `ceil` | `ceil()` |
| `floor` | `floor()` |

Examples:

```bash
calc "square root of sixteen"
# sqrt(16) -> 4

calc "sine of pi over two"
# sin(pi/2) -> 1.0

calc "absolute value of negative five"
# abs(-5) -> 5
```

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
