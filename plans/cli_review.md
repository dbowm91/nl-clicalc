# CLI Module Architecture Review

## Verified Claims

The following claims in `cli.md` are **correct**:

| Claim | Status |
|-------|--------|
| `__main__.py` imports `main()` from `normalize.py` | Verified |
| Entry point works: `python -m nl_calc "five plus two"` | Verified |
| `-h`, `--help` shows help and available operators | Verified |
| `--usage` shows full usage information and examples | Verified |
| `-v`, `--version` shows version information | Verified |
| `-e`, `--expression` evaluates single expression | Verified |
| `-q`, `--quiet` suppresses expression in output | Verified |
| `-s`, `--show` shows expression in output | Verified |
| `--json` outputs result as JSON | Verified |
| `-i`, `--interactive` starts REPL mode | Verified |
| `--mcp` runs MCP server | Verified |
| `calc inspect <text>` checks for confusables | Verified |
| `calc count <text> [char]` counts characters | Verified |
| `calc regex <pattern> <text>` tests regex | Verified |
| REPL commands: `help`, `history`, `clear`, `quit`/`exit` | Verified |
| Shell glob detection warns about `*` expansion | Verified |
| Plain output format: `5+3 -> 8` | Verified |
| JSON output format | Verified |
| Error messages: `Unrecognized command`, `Can't divide by 0`, etc. | Verified |

## Discrepancies

### 1. `normalize_main()` Alias Claim (Medium Priority)

**Location:** `architecture/cli.md:13-17`

**Claim:**
```python
from nl_calc.normalize import main, normalize_main  # Both refer to same function
```

**Reality:** At runtime, `normalize_main` does **not exist** in `normalize.py`. The `main()` function is defined as `main`, not as an alias. The `normalize_main` name is only created by `build_single.py` during the build process (see `build_single.py:236`):
```python
code = code.replace("def main() -> int:", "def normalize_main() -> int:")
```

**Fix:** The documentation should clarify that `normalize_main` is a build-time alias, or remove the claim about the alias existing at runtime.

## Bugs Found

### 1. Verbose Mode Not Implemented (High Priority)

**Location:** `architecture/cli.md:125`

**Claim:** "Verbose mode (`-v`) shows full traceback."

**Reality:** The `-v` flag is used for `--version`, not verbose mode. The `error_message()` function at `normalize.py:602-615` has a `verbose` parameter but it's never passed `True` from the CLI. There is no `--verbose` flag defined in the argument parser.

**Impact:** Users cannot get detailed error tracebacks even when debugging complex expressions.

**Fix:** Either add a `--verbose` flag (requiring `-v` to be repurposed, which would be a breaking change), or document that verbose mode is not currently available.

### 2. REPL Default `show_expression` Incorrect (Medium Priority)

**Location:** `normalize.py:1275`

**Documentation says:** "-s, --show Show expression in output (default for interactive)"

**Code:**
```python
if args.interactive:
    return _run_repl(show_expression=args.show)
```

**Problem:** `args.show` defaults to `False` (argparse default), but documentation says it should be "default for interactive".

**Impact:** Interactive REPL does NOT show expressions by default, contrary to documentation.

**Fix:** Change line 1275 to:
```python
return _run_repl(show_expression=args.show if args.show else True)
```

## Improvements

### 1. `-e` Flag Description is Misleading (Medium Priority)

**Location:** `normalize.py:1241`

**Current:** `-e, --expression, dest="single_expr", help="Evaluate a single expression (useful for piping)"`

**Issue:** Architecture doc says "(quiet mode)" but the actual behavior is that it just changes the default for `show_expression`. The `-q` flag is what actually suppresses output.

**Fix:** Update help text to clarify behavior or remove "(quiet mode)" from architecture doc.

### 2. Redundant `--usage` Flag (Low Priority)

**Location:** `normalize.py:1266-1268`

Both `--usage` and `-h`/`--help` call `print_help()`. This is redundant.

**Fix:** Either make `--usage` show more detailed examples (as architecture suggests), or remove `--usage` as an alias.

### 3. Shell Glob Detection Only Checks First Arg (Low Priority)

**Location:** `normalize.py:1285-1291`

The glob detection only checks `args.expression[0]` for file existence, but could miss cases where glob expands to multiple files and the first isn't a match.

**Current:**
```python
if args.expression and len(args.expression) > 1:
    path = os.path.join(cwd, args.expression[0])
    if os.path.exists(path) and arg not in (".", ".."):
```

**Issue:** This only detects glob expansion in the first argument token.

## Priority Summary

| Item | Type | Priority |
|------|------|----------|
| Verbose mode not implemented | Bug | High |
| REPL default show_expression | Bug | Medium |
| `normalize_main` alias claim | Discrepancy | Medium |
| `-e` flag description misleading | Improvement | Medium |
| Redundant `--usage` flag | Improvement | Low |
| Shell glob detection partial | Improvement | Low |