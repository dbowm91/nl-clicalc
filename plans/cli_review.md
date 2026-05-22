# CLI Architecture Review

## Summary

The CLI module (`__main__.py` + `normalize.py`) provides a command-line interface for the natural language calculator. Entry point is via `python -m nl_calc` which delegates to `main()` in `normalize.py:1215`. The CLI handles expression evaluation, unit conversions, text inspection commands (inspect/count/regex), interactive REPL mode, shell glob detection, and JSON output.

---

## Verified Claims

| Claim (from cli.md) | Status | Implementation |
|---------------------|--------|----------------|
| `python -m nl_calc` entry point | ✅ Verified | `__main__.py:17` imports `main` from normalize.py |
| `main()` handles CLI parsing | ✅ Verified | `normalize.py:1215` |
| `-h, --help` shows help | ✅ Verified | `normalize.py:1228` |
| `--usage` shows full usage | ✅ Verified | `normalize.py:1230-1231` |
| `-v, --version` shows version | ✅ Verified | `normalize.py:1233` |
| `-e, --expression` for single expression | ✅ Verified | `normalize.py:1237-1242` |
| `-q, --quiet` suppresses output | ✅ Verified | `normalize.py:1234` |
| `--json` JSON output | ✅ Verified | `normalize.py:1235` |
| `-i, --interactive` REPL mode | ✅ Verified | `normalize.py:1244-1245` |
| `calc inspect <text>` | ✅ Verified | `normalize.py:1118-1140` |
| `calc count <text> [char]` | ✅ Verified | `normalize.py:1142-1180` |
| `calc regex <pattern> <text>` | ✅ Verified | `normalize.py:1182-1210` |
| REPL `help` command | ✅ Verified | `normalize.py:1013-1014` |
| REPL `history` command | ✅ Verified | `normalize.py:1017-1020` |
| REPL `clear` command | ✅ Verified | `normalize.py:1022-1023` |
| REPL `quit`/`exit` command | ✅ Verified | `normalize.py:1010-1011` |
| Shell glob detection | ✅ Verified | `normalize.py:1278-1297` |
| Error handling (stderr) | ✅ Verified | `normalize.py:602-615` |
| `calc inspect` confusables example | ✅ Verified | Output shows confusables |

---

## Issues Found

### Issue 1: `--mcp` Flag Missing from Source Module (Critical)

**Claim (cli.md:27):** `--mcp` runs as MCP server for exact text tools

**Actual:**
- The `--mcp` argument exists only in the **built single-file version** (`build_single.py:380`)
- When running via `python -m nl_calc`, the argparse in `normalize.py` does **not** include `--mcp`

**Evidence:**
```bash
$ python3 -m nl_calc --mcp
usage: python3 -m nl_calc [-h] [--usage] [-v] [-q] [--json] [-e <expr>] [-i] [-s]
python3 -m nl_calc: error: unrecognized arguments: --mcp

$ python3 nl_calc.py --mcp  # works (built file)
```

**Location:** `normalize.py:1220-1252` (argparse definition missing `--mcp`)

**Impact:** Users following the documentation will fail when trying to use `--mcp` via the module entry point.

---

### Issue 2: Documentation Inconsistency - Entry Point Description

**Claim (cli.md:5-8):**
```markdown
`__main__.py` provides the entry point for running as a module:
python -m nl_calc "five plus two"
```

**Actual:** `__main__.py` is merely a bootstrap that imports `main` from `normalize.py:17`. The actual CLI logic is in `normalize.py:1215-1315`.

---

### Issue 3: JSON Output Format Inconsistency

**Claim (cli.md:107-110):** JSON output should be:
```json
{"expression": "5+3", "result": "8"}
```

**Actual:** When `--json` is used, output is:
```
nl_calc $ python3 -m nl_calc --json "5+3"
{"expression": "5+3", "result": "8"}
```

This is correct and matches the documentation.

---

### Issue 4: REPL `show_expression` Default Behavior

**Claim (cli.md:65-68):**
```
# >>> five plus two
# 5+2 -> 7
# >>> quit
```

The doc shows REPL displaying expression->result format. The implementation at `normalize.py:1026` uses `show_expression` from the `_run_repl` parameter, defaulting to `True`. However, the `main()` function at `normalize.py:1267-1268` passes `args.show` which defaults to `False`.

**Actual behavior:**
- CLI: `python3 -m nl_calc -i` - shows expression->result (correct)
- But the default `show_expression=False` in `main()` at line 1312 means non-REPL non-quiet non-show cases hide the expression

This is correct, but the default `args.show` is False at `normalize.py:1249` while the REPL always shows expressions.

---

### Issue 5: Verbose Mode Not Documented

**Claim (cli.md:121):** "Verbose mode (`-v`) shows full traceback"

**Actual:**
- `-v` is defined in argparse as `--version` (line 1233), not verbose
- There is no verbose flag implemented
- Error handling at `normalize.py:602-615` has a `verbose` parameter but it's never exposed via CLI

---

## Missing Features

### Missing 1: No Verbose Error Mode

The error_message function (`normalize.py:602-615`) accepts a `verbose` parameter but the CLI never passes `True`. Users cannot get full tracebacks.

### Missing 2: `-s`/`--show` Default for REPL Not Enforced

In `main()` at line 1307-1312, when `quiet_by_default` is False (positional expression), `show_expression` defaults to `False` regardless of whether running interactively. The `-s` flag works, but is not automatically on for REPL.

---

## Recommendations

### Recommendation 1: Add `--mcp` to `normalize.py` argparse

**File:** `nl_calc/normalize.py:1220-1252`

Add to the argument parser:
```python
parser.add_argument(
    "--mcp", action="store_true", help="Run as MCP server for exact text tools"
)
```

And handle it in main() around line 1255, importing and calling `mcp_main()` from the mcp.server module.

**Note:** This requires careful handling since mcp.server.main is a separate entry point that runs a stdio loop. It should replace the entire CLI execution, not return to it.

### Recommendation 2: Document `-v` Properly

**File:** `nl_calc/normalize.py:1233`

The `-v` flag is currently `--version`. If verbose error output is desired, add a separate flag like `--verbose` or `-V`. Update documentation accordingly.

### Recommendation 3: Ensure Consistent REPL Show Behavior

**File:** `nl_calc/normalize.py:1267-1268`

Consider always passing `show_expression=True` when calling `_run_repl()` since REPL users expect to see the expression->result format shown in the documentation.

---

## File References

- `architecture/cli.md:1-121` - Architecture document reviewed
- `nl_calc/__main__.py:12-18` - Entry point bootstrap
- `nl_calc/normalize.py:1215-1315` - Main CLI function
- `nl_calc/normalize.py:1220-1252` - Argument parser definition
- `nl_calc/normalize.py:1267-1268` - REPL invocation
- `nl_calc/normalize.py:1278-1297` - Shell glob detection
- `nl_calc/normalize.py:1106-1212` - Text commands (inspect, count, regex)
- `nl_calc/normalize.py:991-1031` - REPL implementation
- `nl_calc/mcp/server.py:378-416` - MCP server main (not reachable via `python -m nl_calc`)
- `build_single.py:376-410` - Combined entry point that includes `--mcp`