# CLI Usage

## Synopsis

```bash
calc [OPTIONS] [EXPRESSION]
calc -i
echo "5 + 3" | calc -e
```

## Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message and available operators |
| `-v`, `--version` | Show version information |
| `-e`, `--expression` | Evaluate a single expression (quiet mode by default) |
| `-q`, `--quiet` | Suppress expression in output |
| `-s`, `--show` | Show expression in output (useful with `-e`) |
| `--json` | Output result as JSON |
| `-i`, `--interactive` | Start interactive REPL mode |

## Modes

### Single Expression

```bash
calc "5 + 3"
# 5+3 -> 8
```

### Quiet Mode

Use `-e` for quiet output (result only):

```bash
calc -e "5 + 3"
# 8
```

### Show Expression

Use `-s` with `-e` to show the expression:

```bash
calc -e -s "five plus three"
# 5+3 -> 8
```

### JSON Output

```bash
calc --json "5 + 3"
# {"result": 8, "expression": "5+3"}
```

### Interactive Mode

```bash
calc -i
>>> 5 + 3
8
>>> sin(pi/2)
1.0
>>> 30m + 100ft
60.48 m
>>> quit
```

### Pipe Input

```bash
echo "5 + 3" | calc -e
# 8

cat expressions.txt | calc -e
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid expression |
| 2 | Input too long |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CLICALC_MAX_INPUT_LENGTH` | Override max input length |
| `CLICALC_CACHE_SIZE` | Set cache size |

## Examples

### Arithmetic

```bash
calc "2 + 2"           # 4
calc "10 / 3"          # 3.333...
calc "2 ** 10"         # 1024
```

### Natural Language

```bash
calc "five plus two"   # 7
calc "hundred times five"  # 500
```

### Units

```bash
calc "5km in miles"    # 3.107 mi
calc "1GB in MB"       # 1024 MB
```

### Functions

```bash
calc "sqrt(16)"        # 4
calc "sin(pi/6)"       # 0.5
calc "factorial(5)"    # 120
```

### Constants

```bash
calc "pi"              # 3.14159...
calc "avogadro"        # 6.022e+23
calc "c"               # 299792458
```
