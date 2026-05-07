# cli.md - Command-Line Interface

## Entry Point

`__main__.py` provides the entry point for running as a module:

```bash
python -m nl_calc "five plus two"
```

## Main Function

`main()` in `normalize.py` handles all CLI parsing and execution.

## CLI Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help and available operators |
| `--usage` | Show full usage information and examples |
| `-v`, `--version` | Show version information |
| `-e`, `--expression` | Evaluate single expression (quiet mode) |
| `-q`, `--quiet` | Suppress expression in output |
| `-s`, `--show` | Show expression in output |
| `--json` | Output result as JSON |
| `-i`, `--interactive` | Start interactive REPL mode |
| `--mcp` | Run as MCP server for exact text tools |

## Text Commands

The CLI includes built-in text inspection commands:

### `calc inspect <text>`

Check for hidden characters and confusables:

```bash
calc inspect "pаypal"  # Cyrillic 'а' confusable
# ✗ CONFUSABLE: Text contains confusable character
```

### `calc count <text> [char]`

Count character frequency:

```bash
calc count "hello world"
calc count "hello" l  # Count specific character
```

### `calc regex <pattern> <text>`

Test regex patterns:

```bash
calc regex "^\d+$" "12345"
# ✓ Match: '12345'
```

## Interactive REPL

Enter interactive mode with `-i`:

```bash
calc -i
# >>> five plus two
# 5+2 -> 7
# >>> quit
```

Commands in REPL:
- `help` - Show available operators and functions
- `history` - Show evaluation history
- `clear` - Clear history
- `quit` / `exit` - Exit REPL

## Shell Glob Detection

The CLI detects when `*` is expanded by the shell (glob pattern) and warns the user to quote expressions:

```
Error: Possible shell glob expansion detected.
The '*' character was expanded to file(s): [...]
Please quote your expression:
  calc "30 * 3"
Or use -e flag:
  calc -e "30 * 3"
```

## Output Formats

### Plain (default)

```
5+3 -> 8
30*m+100*ft -> 60.48 m
```

### Quiet

```
8
60.48 m
```

### JSON

```json
{"expression": "5+3", "result": "8"}
{"expression": "30*m+100*ft", "result": "60.48 m"}
```

## Error Handling

Errors are printed to stderr with user-friendly messages:
- `Unrecognized command: '...'`
- `Can't divide by 0: '...'`
- `Evaluation error: ...`
- `Error: ...`

Verbose mode (`-v`) shows full traceback.