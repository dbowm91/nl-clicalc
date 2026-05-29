# CLI Architecture Review

## Entry Point
| Claim | Status | Notes |
|-------|--------|-------|
| `__main__.py` is a bootstrap module that imports `main()` from `normalize.py` and delegates all CLI parsing and execution to it | **MATCHES** | Verified in `nl_calc/__main__.py:17` - imports `main` from `normalize.py` and calls `sys.exit(main())` |

## Main Function
| Claim | Status | Notes |
|-------|--------|-------|
| `main()` in `normalize.py` handles all CLI parsing and execution | **MATCHES** | Verified at `normalize.py:1418` |
| When assembled into a single file by `build_single.py`, it is aliased as `normalize_main()` to avoid conflict with the MCP server's `main()` function | **MATCHES** | Verified in `build_single.py:244-245` - the `def main() -> int:` in normalize.py becomes `def normalize_main() -> int:` |

## CLI Options
| Option | Claim | Status | Notes |
|--------|-------|--------|-------|
| `-h`, `--help` | Show help and available operators | **MATCHES** | `normalize.py:1431` |
| `--usage` | Show full usage information and examples | **MATCHES** | `normalize.py:1434` |
| `-v`, `--version` | Show version information | **MATCHES** | `normalize.py:1436` |
| `-e`, `--expression` | Evaluate single expression (quiet mode) | **MATCHES** | `normalize.py:1441-1446` |
| `-q`, `--quiet` | Suppress expression in output | **MATCHES** | `normalize.py:1437` |
| `-s`, `--show` | Show expression in output | **MATCHES** | `normalize.py:1451-1454` |
| `--json` | Output result as JSON | **MATCHES** | `normalize.py:1439` |
| `-i`, `--interactive` | Start interactive REPL mode | **MATCHES** | `normalize.py:1448` |
| `--mcp` | Run as MCP server for exact text tools | **MATCHES** | `normalize.py:1456-1464` |
| `--verbose` | Show expression in output | **MATCHES** | `normalize.py:1438` - argument exists |

## Text Commands
| Claim | Status | Notes |
|-------|--------|-------|
| `calc inspect <text>` - Check for hidden characters and confusables | **MATCHES** | `normalize.py:1321-1343` - uses `inspect_text` from `exact` |
| `calc count <text> [char]` - Count character frequency | **MATCHES** | `normalize.py:1345-1383` - uses `count_chars` from `exact` |
| `calc regex <pattern> <text>` - Test regex patterns | **MATCHES** | `normalize.py:1385-1413` - uses `regex_test` from `exact` |

## Interactive REPL
| Claim | Status | Notes |
|-------|--------|-------|
| Enter interactive mode with `-i` | **MATCHES** | `normalize.py:1478-1479` |
| REPL commands: `help`, `history`, `clear`, `quit`/`exit`/`exit()` | **MATCHES** | `normalize.py:1212-1226` |

## Shell Glob Detection
| Claim | Status | Notes |
|-------|--------|-------|
| CLI detects when `*` is expanded by shell and warns user | **MATCHES** | `normalize.py:1488-1509` - checks if args are existing file paths |

## Output Formats
| Claim | Status | Notes |
|-------|--------|-------|
| Plain (default) format: `5+3 -> 8` | **MATCHES** | `normalize.py:1180-1181` |
| Quiet format: just `8` | **MATCHES** | `normalize.py:1182-1183` |
| JSON format: `{"expression": "...", "result": "..."}` | **MATCHES** | `normalize.py:1175-1178` |
| The `expression` field contains normalized expression, not original input | **MATCHES** | Verified in `run()` at `normalize.py:1178` - uses `joined` (normalized) |

## Error Handling
| Claim | Status | Notes |
|-------|--------|-------|
| `Unrecognized command: '...'` | **MATCHES** | `normalize.py:641` |
| `Can't divide by 0: '...'` | **MATCHES** | `normalize.py:643` |
| `Evaluation error: ...` | **MATCHES** | `normalize.py:645` |
| `Error: ...` | **MATCHES** | `normalize.py:650` |

---

## Discrepancies Found

### 1. `--verbose` Flag Logic Bug (MEDIUM severity)
**Location:** `normalize.py:1517`

**Issue:** The `--verbose` flag does not actually enable expression output when used alone. The logic is:
```python
show_expression = not args.quiet and (args.verbose or args.show) and not quiet_by_default
```

When using `--verbose` with positional expression (not `-e`), `quiet_by_default=False`, so this works. But when using `-e` (`quiet_by_default=True`), `--verbose` is negated out.

**Impact:** User cannot enable verbose output when using `-e` flag, despite `--verbose` being a documented option.

---

## Bugs Identified

### 1. `--verbose` Ineffective with `-e` Flag (MEDIUM)
**File:** `normalize.py:1517`
```python
show_expression = not args.quiet and (args.verbose or args.show) and not quiet_by_default
```
When `quiet_by_default=True` (from `-e`), the `and not quiet_by_default` prevents `show_expression` from being True even when `args.verbose=True`.

**Suggested Fix:**
```python
show_expression = args.verbose or args.show or (not args.quiet and not quiet_by_default and not args.single_expr)
```

### 2. Redundant `import sys` in `_run_repl` (LOW)
**File:** `normalize.py:1195`
```python
def _run_repl(show_expression: bool = True) -> int:
    """Run interactive REPL mode."""
    import sys  # Already imported at module level
```

The `sys` module is already imported at the top of the file (`normalize.py:18`). The local import at line 1195 is redundant but harmless.

### 3. Typo in Comment (LOW - cosmetic)
**File:** `normalize.py:1260`
```python
"  calc regex <pat> <text>  Test regex pattern against text",
```
Missing space before "Test" - formatting inconsistency.

---

## Improvements Suggested

### 1. Add `--quiet` Override for `-e` Behavior (LOW priority)
Currently `-e` forces quiet mode. Consider allowing `--verbose` to override this. Document the behavior or adjust logic as noted above.

### 2. Improve Error Message for Glob Detection (LOW priority)
**File:** `normalize.py:1501-1502`

The glob detection error message hardcodes `'*'` in the description even if a different character triggered it:
```python
f"The '*' character was expanded to file(s): {glob_indicators[:5]}..."
```

Should track which character actually caused the warning.

### 3. Consider Using `argparse.BooleanOptionalAction` for `--show`/`--verbose` (LOW priority)
For cleaner CLI design, could use Python 3.9+ `argparse.BooleanOptionalAction` to allow `--show`/`--no-show` and `--verbose`/`--no-verbose` syntax.

---

## Priority Summary

| Priority | Item | Severity |
|----------|------|----------|
| HIGH | Fix `--verbose` flag logic bug | MEDIUM - Feature doesn't work as documented |
| MEDIUM | Consider clarifying `-e` and `--verbose` interaction | LOW - Usability issue |
| LOW | Remove redundant `import sys` in `_run_repl` | Trivial |
| LOW | Fix glob detection error message to show actual character | Cosmetic |

---

## Verification Notes

- All 88 tests in `test_clicalc.py` pass
- CLI options all correctly route to their claimed implementations
- Text commands (`inspect`, `count`, `regex`) correctly delegate to `exact` module functions
- Error handling matches documented messages
- JSON output contains normalized expression as documented