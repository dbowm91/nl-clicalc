# Quick Start

## Basic Arithmetic

```bash
calc "5 + 3"
# 8

calc "2 + 3 * 4"
# 14
```

## Natural Language

```bash
calc "five plus three"
# 5+3 -> 8

calc "twenty times five"
# 20*5 -> 100

calc "one hundred divided by four"
# 100/4 -> 25
```

## Unit Conversions

```bash
calc "30m + 100ft"
# 60.48 m

calc "1 mile in kilometers"
# 1.609 km

calc "1GB in MB"
# 1024 MB
```

## Scientific Functions

```bash
calc "sin(pi/2)"
# 1.0

calc "sqrt(144)"
# 12

calc "log(e)"
# 1.0
```

## Physical Constants

```bash
calc "avogadro"
# 6.022e+23

calc "speed of light"
# 299792458

calc "5 * planck"
# 3.31e-33
```

## Interactive Mode

```bash
calc -i
>>> 5 + 3
8
>>> sin(pi)
0.0
>>> quit
```

## Pipe Input

```bash
echo "5 + 3" | calc -e
# 8

echo "100ft in meters" | calc -e
# 30.48
```

## Python API

```python
from nl_clicalc import evaluate_raw

result = evaluate_raw("five plus three")
print(result)  # 8
```

## Next Steps

- [CLI Usage](cli.md) - All command-line options
- [Natural Language](natural-language.md) - Full language support
- [Functions](functions.md) - All available functions
- [Units](units.md) - All supported units
