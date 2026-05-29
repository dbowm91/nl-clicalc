# Natural Language

eggcalc converts natural language expressions into mathematical operations. Understanding how parsing works helps you write expressions that work reliably.

## How Parsing Works

The parser splits input by operator boundaries, then converts each segment:

1. **Split by operators** (`+`, `-`, `*`, `/`, `^`, spaces) into tokens
2. **Convert number words** to digits ("twenty five" → "20+5")
3. **Convert operator words** to symbols ("plus" → "+")
4. **Strip filler phrases** ("what is", "calculate the")
5. **Handle special patterns** like "point" for decimals

**Why this matters:** "twenty five" becomes "20+5" not "25" because the parser splits on spaces and operator words. This is intentional—it allows expressions like "twenty one" (21) to parse correctly.

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
ten, eleven, twelve, thirteen, fourteen, fifteen,
sixteen, seventeen, eighteen, nineteen
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

## Number Combination Rules

Numbers combine according to these rules:

### Ones + Tens → Addition

"twenty five" → 20 + 5 → 25

```bash
calc "twenty five"           # 25
calc "thirty two"            # 32
calc "ninety nine"           # 99
```

### Ones + Scale → Multiply or Add

"one hundred fifty" → 1 * 100 + 50 → 150

```bash
calc "one hundred fifty"    # 150
calc "two hundred"           # 200
```

### Scale + Scale → Multiply

"million billion" → 1,000,000 × 1,000,000,000 → 1×10¹⁵

```bash
calc "million billion"       # 1e+15
```

### Multiple Scales

"three million two hundred thousand" → 3,200,000

```bash
calc "three million two hundred thousand"
# 3000000+200000 -> 3200000
```

**Important:** The parser treats consecutive number words as either addition or multiplication based on the scale. "twenty five" = 20 + 5, but "five million" = 5 × 1,000,000.

### Special Cases

**"a" as 1:**
```bash
calc "a hundred"            # 100
calc "a thousand"           # 1000
```

**"half" as 0.5:**
```bash
calc "half of ten"          # 0.5*10 -> 5
```

**"quarter" as 0.25:**
```bash
calc "quarter of twenty"    # 0.25*20 -> 5
```

## Decimals with "point"

Use "point" to indicate decimal values:

```bash
calc "three point one four"  # 3.1.4 -> 3.14
calc "one point five"        # 1.1.5 -> 1.5
calc "twenty point seven five"  # 20.1.7.5 -> 20.175
```

**How it works:** "point" creates a decimal point in the current accumulated number. "three point one four" becomes "3.1.4" which evaluates to 3.14.

## Stripped Phrases

Certain conversational phrases and filler words are automatically removed before processing:

| Stripped | Example | Why |
|----------|---------|-----|
| `what's`, `what is` | "what is five plus three" | Question prefixes |
| `calculate`, `compute`, `convert` | "calculate the square root" | Action words |
| `tell me`, `give me` | "tell me the result of" | Request phrases |
| `the`, `a` | "the square root of" | Articles |
| `of` | "square root of sixteen" | Preposition |

These work because stripping happens before tokenization:

```bash
calc "what is five plus three"       # 5+3 -> 8
calc "calculate the square root of 16"  # sqrt(16) -> 4
calc "convert 100 meters to feet"   # 100*m -> 328.084 ft
```

## Operators

| Natural Language | Operator | Example |
|-----------------|----------|---------|
| `plus`, `positive` | `+` | "five plus three" → 5+3 |
| `minus`, `negative` | `-` | "ten minus three" → 10-3 |
| `times`, `multiplied by` | `*` | "five times three" → 5*3 |
| `of` | `*` | "half of ten" → 0.5*10 |
| `divided by`, `over`, `per`, `divide` | `/` | "ten divided by two" → 10/2 |
| `to the power of`, `raised to`, `to the` | `**` | "two to the power of ten" → 2**10 |
| `mod`, `modulo`, `percent`, `remainder` | `%` | "ten mod three" → 10%3 |
| `point` | `.` | "three point one four" → 3.14 |

**Note on "of":** "of" maps to multiplication because that's how English works—"half of a pie" means "half times a pie". This allows natural expressions like "quarter of twenty".

## Functions

Natural language function names map to their mathematical equivalents:

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

**Function name variations:** "sine", "sin", and "arcsine", "asin" all work. The parser recognizes common synonyms.

**Using parentheses:**
The most reliable way to use functions is with parentheses directly:

```bash
calc "sin(pi/2)"          # 1.0
calc "sqrt(144)"          # 12
calc "abs(-5)"            # 5
```

**"of" pattern:** The "of" pattern works for some functions:

```bash
calc "square root of 16"  # sqrt(16) -> 4
calc "logarithm of e"     # log(e) -> 1
calc "sine of pi"         # sin(pi) -> ~0
```

However, for complex expressions, parentheses are more reliable:

```bash
# Prefer this
calc "sqrt(16)"           # 4

# Over this (may have edge cases)
calc "square root of 16"  # 4
```

## Parentheses

Use "open" and "close" or actual parentheses:

```bash
calc "open five plus three close times two"
# (5+3)*2 -> 16

calc "(five plus three) times two"
# (5+3)*2 -> 16

calc "open two close to the power of open three plus one close close"
# 2**(3+1) -> 16
```

**Why "open/close":** In interactive mode, you might want to type natural language. "open" and "close" map to `(` and `)`.

## Negative Numbers

```bash
calc "negative five"              # -5
calc "minus twenty"               # -20
calc "five minus negative three"  # 5-(-3) -> 8
calc "negative three times four"  # -3*4 -> -12
```

**How negative works:** "negative five" parses as `-5` (unary minus). "minus twenty" also parses as `-20`.

## Order of Operations

eggcalc follows standard mathematical precedence:

```bash
calc "five plus three times two"
# 5+3*2 -> 11 (NOT 16 - multiplication before addition)

calc "ten minus two plus three"
# 10-2+3 -> 11 (left-to-right for same precedence)

calc "twenty divided by four times two"
# 20/4*2 -> 10 (left-to-right)
```

**Use parentheses to override:**

```bash
calc "(five plus three) times two"
# (5+3)*2 -> 16
```

## Variable Assignment

Set and use variables:

```bash
calc 'setvar("x", 10)'        # x = 10
calc "x + 5"                  # x+5 -> 15
calc 'setvar("y", 20)'        # y = 20
calc "x * y"                  # x*y -> 200
```

See [API Reference](api.md) for variable functions (`setvar`, `getvar`, `delvar`, `listvars`, `clearvars`).

## Common Mistakes

### Missing Spaces Between Number Words

```bash
# Correct - space between words
calc "twenty five"            # 25

# May not parse as expected (depends on context)
calc "fifteen"               # 15
```

### Ambiguous "of"

```bash
# "of" becomes multiplication - may be unexpected
calc "half of quarter"        # 0.5*0.25 -> 0.125
```

### Parentheses with Nested Expressions

```bash
# Complex nested parentheses
calc "(5 + 3) * (2 + 1)"     # (5+3)*(2+1) -> 24

# Same using natural language
calc "open five plus three close times open two plus one close"
# (5+3)*(2+1) -> 24
```

## Examples

### Simple

```bash
calc "two plus two"           # 4
calc "ten minus three"        # 7
calc "five times six"         # 30
calc "twenty divided by four" # 5
```

### Complex

```bash
calc "twenty five times four plus ten"
# 25*4+10 -> 110

calc "one hundred divided by five plus three"
# 100/5+3 -> 23

calc "square root of one hundred forty four"
# sqrt(100+44) -> 12 (parsed as 100+44, not 144!)
```

**Warning:** "one hundred forty four" parses as "100 + 44" = 144, not as the number 144. For the number 144, say "one hundred forty-four" (hyphenated) or just "one forty four".

### With Units

```bash
calc "thirty meters plus one hundred feet"
# 30*m+100*ft -> 60.48 m

calc "five kilometers in miles"
# 5*km -> 3.107 mi

calc "one hundred pounds minus ten ounces"
# 100*lb-10*oz -> 99.375 lb
```

### With Functions

```bash
calc "sine of thirty degrees"
# sin(30) -> 0.5 (note: uses radians by default in expressions)

calc "sqrt of (two to the power of six)"
# sqrt(2**6) -> 8.0

calc "log of (one hundred times ten)"
# log(100*10) -> 6.0 (natural log)
```

## See Also

- [Functions](functions.md) - All available mathematical functions
- [Constants](constants.md) - Physical and mathematical constants
- [Units](units.md) - Unit conversions
- [API Reference](api.md) - Python API details