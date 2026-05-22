# CLI Module Architecture Review

## Verified Claims

1. **Entry Point**: `__main__.py` correctly imports `main()` from `normalize.py` and delegates execution
2. **All CLI Options Implemented**:
   - `-h`, `--help` - Shows help
   - `--usage` - Shows full usage info
   - `-v`, `--version` - Shows version
   - `-e`, `--expression` - Single expression mode
   - `-q`, `--quiet` - Suppress expression output
   - `-s`, `--show` - Show expression output
   - `--json` - JSON output format
   - `-i`, `--interactive` - Interactive REPL
   - `--mcp` - MCP server mode
3. **Text Commands**: `inspect`, `count`, `regex` all implemented and functional
4. **Interactive REPL**: Commands `help`, `history`, `clear`, `quit`/`exit` all work
5. **Shell Glob Detection**: Detects expanded `*` and warns user to quote expressions
6. **Output Formats**: Plain, quiet, and JSON formats all work correctly
7. **Error Handling**: All error messages match documentation (`Unrecognized command`, `Can't divide by 0`, `Evaluation error`, `Error`)

## Discrepancies

### 1. `normalize_main()` Alias Documentation (Medium)
**Location**: architecture/cli.md:13-16

The architecture doc shows:
```python
from nl_calc.normalize import main, normalize_main  # Both refer to same function
```

**Reality**: `normalize_main` does not exist in source code. It is created at **build time** by `build_single.py:234-236` which renames `main()` to `normalize_main()` to avoid conflict with MCP's `main()`.

**Impact**: Documentation is misleading. Users cannot `from nl_calc.normalize import normalize_main` directly - it only exists after `build_single.py` runs.

### 2. Undocumented `--verbose` Flag (Medium)
**Location**: nl_calc/normalize.py:1235

The implementation has an undocumented `--verbose` flag that sets `show_expression = True` (same behavior as `--show`).

**Discrepancy**: Architecture doc only mentions `-v, --version` but `--verbose` is not documented.

## Bugs Found

### 1. REPL History Stores `None` on Evaluation Failure
**Location**: nl_calc/normalize.py:1026-1029

```python
_, exit_code = run(line, NORMALIZE, PATTERNS, "plain", show_expression)

if exit_code == 0:
    history.append((line, _))  # BUG: `_` is result from `run()`, could be None
```

When `run()` returns `(None, 0)` due to an evaluation error (see line 966: `return None, exit_code`), the `None` is appended to history. The next `history` command will print `None` as the result.

**Expected**: Only append to history when we have an actual result, or skip failed evaluations.

## Improvements

### High Priority

1. **Fix REPL history bug** - Line 1029 stores `None` when evaluation fails but `exit_code == 0`
   - Root cause: `run()` returns `(None, 0)` when `normalize_expression` fails with exit_code=2 (input too long)
   - Should check if result is not None before appending to history

### Medium Priority

2. **Update `normalize_main()` documentation** - Clarify that the alias is created at build time, not in source
   - Either remove the import example or add clarifying comment
   - Or export `normalize_main = main` in normalize.py for source compatibility

3. **Document `--verbose` flag** - Add to CLI options table or clarify relationship with `--show`

### Low Priority

4. **Consider separating `-v` and `--verbose`** - Currently `-v` is `--version` and `--verbose` is for output. Consider if `-v` should be shorthand for `--verbose` instead (breaking change).

## Summary

| Category | Count |
|----------|-------|
| Verified Claims | 7 |
| Discrepancies | 2 |
| Bugs | 1 |
| Improvements | 4 |
