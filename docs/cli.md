# CLI Usage

## Synopsis

```bash
calc [OPTIONS] [EXPRESSION]
calc inspect <text>
calc count <text> [char]
calc regex <pattern> <text>
calc -i
echo "5 + 3" | calc -e
```

## Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message with operators, units, and examples |
| `-v`, `--version` | Show version information |
| `-e`, `--expression` | Evaluate a single expression (quiet mode by default) |
| `-q`, `--quiet` | Suppress expression in output |
| `-s`, `--show` | Show expression in output (useful with `-e`) |
| `--json` | Output result as JSON |
| `-i`, `--interactive` | Start interactive REPL mode |
| `--mcp` | Run as MCP server for exact text tools |

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

## Text Tools

nl-clicalc includes text inspection tools for detecting hidden characters and testing patterns.

### inspect — Hidden Character Detection

Check text for invisible characters, confusables, and Unicode risks:

```bash
# Clean text
calc inspect "hello"
# ✓ No hidden characters

# Hidden NULL character
calc inspect "hello\x00world"
# ✗ HIDDEN: Text contains NULL (U+0000) at index 5.

# Confusable characters (Cyrillic 'а' vs Latin 'a')
calc inspect "pаypal"
# ✗ CONFUSABLE: Text contains confusable character 'а' (looks like 'a') at index 1.
```

Uses Unicode confusables database (6500+ entries) to detect homoglyph attacks.

### count — Character Counting

Count characters in text, with optional frequency table:

```bash
# Single character count
calc count "hello" l
# 'l' appears 3 time(s) in "hello"

# Full frequency table for multi-word text
calc count "hello world"
# "hello world":
#   11 characters
#   'l': 3
#   'o': 2
#   (space): 1
#   ...
```

### regex — Pattern Testing

Test regex patterns against sample text:

```bash
# Match found
calc regex "^\d+$" "12345"
# ✓ Match: '12345'

# No match
calc regex "^hello" "world"
# ✗ No match

# With capture groups
calc regex "(\d+)-(\d+)" "555-1234"
# ✓ Match: '555-1234'
#   Groups: ('555', '1234')
```

## MCP Server Mode

nl-clicalc can run as an MCP server, exposing exact text tools to AI agents:

```bash
calc --mcp
```

The MCP server provides these tools:

| Tool | Description |
|------|-------------|
| `math_eval` | Evaluate math expressions |
| `text_measure` | Text metrics (UTF-8 bytes, codepoints, words, lines) |
| `text_equal` | String comparison with normalization options |
| `text_diff_explain` | Explain differences between strings |
| `text_inspect` | Hidden characters, confusables, mixed scripts |
| `text_count` | Character counting and frequency |
| `validate_brackets` | Bracket pair matching |
| `validate_json` | JSON parsing validation |
| `validate_regex` | Regex pattern testing |
| `list_compare` | List comparison |
