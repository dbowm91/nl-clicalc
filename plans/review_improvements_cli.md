# cli Module Review — Improvement Plan

**Reviewed:** architecture/cli.md against nl_calc/__main__.py and nl_calc/normalize.py
**Date:** 2026-05-28

## Verified Claims (with line references)

### Entry Point Bootstrap ✓
- `__main__.py:12-18` correctly imports `main` from `normalize.py` and calls `sys.exit(main())`
- `normalize.py:1421` defines `main() -> int` as the CLI entry point

### CLI Arguments (normalize.py:1426-1461)
All documented CLI options exist in code:
- `-h`, `--help` → line 1434
- `--usage` → line 1437
- `-v`, `--version` → line 1439
- `-e`, `--expression` → lines 1443-1449 (dest="single_expr")
- `-q`, `--quiet` → line 1440
- `-s`, `--show` → lines 1453-1458
- `--json` → line 1442
- `-i`, `--interactive` → lines 1450-1452
- `--mcp` → lines 1459-1461
- `--verbose` → line 1441

### Text Commands (normalize.py:1312-1418)
- `inspect`, `count`, `regex` commands implemented and imported from exact module (line 25)
- Command syntax matches documentation

### Interactive REPL (normalize.py:1196-1236)
- Commands `help`, `history`, `clear`, `quit`/`exit`/`exit()` all work (lines 1207-1229)
- REPL always passes `show_expression=True` to `run()` (line 1231)

### Shell Glob Detection (normalize.py:1491-1512)
- Detection logic exists and warning message matches documentation

### Error Messages (normalize.py:637-650)
- All documented error message formats exist in `error_message()` function

## Discrepancies Between Documentation and Code

- [HIGH] `--verbose` flag description is incorrect
  - Documentation says (`cli.md:32`): "Show detailed error information and tracebacks"
  - Code actually does (`normalize.py:1441`): `action="store_true", help="Show expression in output"`
  - `--verbose` behaves identically to `--show` (see `normalize.py:1520`: `show_expression = not args.quiet and (args.verbose or args.show)`)
  - Impact: Users expecting tracebacks from `--verbose` get expression display instead. The actual traceback-enabling behavior is via the `verbose` parameter to `error_message()`, but `main()` never passes `verbose=True` to `run()`.

- [MEDIUM] `normalize_main()` alias documentation is misleading
  - Documentation says (`cli.md:13-16`): "main() in normalize.py (aliased as normalize_main() for build compatibility)" and shows import statement
  - Code actually does: `normalize.py` only defines `def main()`. The `normalize_main()` name is created by `build_single.py:236` during single-file assembly
  - Impact: Readers may look for `normalize_main` in source and not find it, or try to import it

- [LOW] `exit()` REPL command undocumented
  - Documentation lists (`cli.md:80`): `quit` / `exit`
  - Code actually accepts (`normalize.py:1215`): `("quit", "exit", "exit()")`
  - Impact: Minor - `exit()` works but isn't documented

- [LOW] REPL example output differs slightly from code
  - Documentation shows (`cli.md:71-73`):
    ```
    # >>> five plus two
    # 5+2 -> 7
    ```
  - Code shows (`normalize.py:1200`): "nl-calc interactive mode. Type 'help'..." header before REPL starts
  - Impact: First-time user may see extra header text

## Potential Bugs

### Bug 1: Type mismatch in `run()` return when exit_code == 2
- **Location**: `normalize.py:1168-1171`
- **Code**:
  ```python
  if exit_code != 0:
      if exit_code == 2:
          print(joined, file=sys.stderr)
      return None, exit_code
  ```
- **Problem**: When `normalize_expression()` returns length error, `run()` returns `(None, 2)`. But `main()` at line 1522 does `_, exit_code = run(...)` which would try to unpack `None` as a tuple, causing `TypeError: cannot unpack non-iterable NoneType object`
- **Trigger**: Input longer than `MAX_INPUT_LENGTH` (10000 chars)
- **Severity**: HIGH - crashes with TypeError instead of proper error

### Bug 2: `--verbose` never enables tracebacks despite documentation promise
- **Location**: `normalize.py:637-650` (`error_message`) and how it's called from `run()` (line 1188-1193)
- **Problem**: `run()` calls `error_message(original, e)` without passing `verbose=True`, so even with `--verbose` flag, tracebacks are never shown. The `--verbose` flag only affects `show_expression` (line 1520)
- **Impact**: Documentation promises tracebacks via `--verbose` but code never delivers them

### Bug 3: Hardcoded "calc" in glob error message
- **Location**: `normalize.py:1506`
- **Code**: `f'  calc "{" ".join(args.expression)}"'`  (hardcoded "calc")
- **Problem**: When invoked as `python -m nl_calc`, the suggested command should be `nl_calc` or `python -m nl_calc`, not `calc`
- **Impact**: Minor confusion for module users

## Improvement Suggestions

### HIGH Priority

1. **Fix `run()` return type mismatch bug** (`normalize.py:1168-1171`)
   - `run()` declares return type `tuple[Any, int]` but returns `tuple[None, int]` when exit_code == 2
   - `main()` unpacking at line 1522: `_, exit_code = run(...)` will crash
   - Fix: Either change return to `(None, exit_code)` tuple consistently with typing, or change `main()` to handle `None` first value

2. **Fix `--verbose` traceback behavior or update documentation**
   - Option A: Make `--verbose` actually pass `verbose=True` to `error_message()` in `run()` at lines 1188-1193
   - Option B: Update documentation to accurately describe that `--verbose` shows expressions (same as `--show`)
   - Recommended: Option A - make `--verbose` work as documented

3. **Fix misleading `normalize_main()` documentation**
   - Update `cli.md:13-16` to clarify this is a build-time transformation, not a source-level alias
   - Change from: "aliased as `normalize_main()` for build compatibility"
   - To: "renamed to `normalize_main()` during single-file assembly by build_single.py"

### MEDIUM Priority

4. **Document `exit()` REPL command**
   - Update `cli.md:80` to: `quit` / `exit` / `exit()`

5. **Update REPL header documentation**
   - Either document the startup header in `cli.md:71-73`, or remove it from code if unwanted

6. **Use `sys.argv[0]` or `prog` for glob error message**
   - Replace hardcoded "calc" at `normalize.py:1506` with proper program name

### LOW Priority

7. **Consider consolidating `--verbose` and `--show`**
   - They do the same thing (line 1520)
   - Could simplify by removing one, or make `--verbose` do actual tracebacks (see Bug 2)

8. **Consider using `result` instead of `_` in REPL** (`normalize.py:1233`)
   - Using `_` shadows Python's last-expression-value feature
   - Minor readability concern

## Summary

The CLI module is mostly well-implemented and matches documentation. Three issues require attention:

1. **Critical bug**: `run()` returns `None` when exit_code == 2 but `main()` unpacks assuming tuple
2. **Documentation error**: `--verbose` described as showing tracebacks but only shows expressions
3. **Misleading docs**: `normalize_main()` claimed as source alias but is build-time artifact

The core entry point, text commands, REPL, and glob detection all work as documented. With the above fixes, the CLI would fully match its documentation.
