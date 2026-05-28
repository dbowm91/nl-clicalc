# cli Module Review — Improvement Plan

**Reviewed:** architecture/cli.md against nl_calc/__main__.py and nl_calc/normalize.py
**Date:** 2026-05-28

## Verified Claims (with line references)
- Entry point bootstrap module `__main__.py` — VERIFIED at normalize.py:1421 (main function)
- `python -m nl_calc` invocation — VERIFIED at __main__.py:5-6
- `-h/--help` option — VERIFIED at normalize.py:1434
- `--usage` option — VERIFIED at normalize.py:1437
- `-v/--version` option — VERIFIED at normalize.py:1439
- `-e/--expression` option — VERIFIED at normalize.py:1443-1448
- `-q/--quiet` option — VERIFIED at normalize.py:1440
- `-i/--interactive` option — VERIFIED at normalize.py:1451
- `-s/--show` option — VERIFIED at normalize.py:1454-1458
- `--json` option — VERIFIED at normalize.py:1442
- `--mcp` option — VERIFIED at normalize.py:1459-1461,1465-1467
- Text command `inspect` — VERIFIED at normalize.py:1324-1346
- Text command `count` — VERIFIED at normalize.py:1348-1386
- Text command `regex` — VERIFIED at normalize.py:1388-1416
- REPL command `help` — VERIFIED at normalize.py:1218-1219
- REPL command `history` — VERIFIED at normalize.py:1222-1224
- REPL command `clear` — VERIFIED at normalize.py:1227-1229
- REPL command `quit`/`exit`/`exit()` — VERIFIED at normalize.py:1215
- Shell glob detection — VERIFIED at normalize.py:1492-1512
- JSON output format — VERIFIED at normalize.py:1175-1181
- Error message `Unrecognized command` — VERIFIED at normalize.py:641
- Error message `Can't divide by 0` — VERIFIED at normalize.py:643
- Error message `Evaluation error` — VERIFIED at normalize.py:645

## Discrepancies Between Documentation and Code

### MEDIUM — `--verbose` flag behavior mismatch
- **Documentation says:** `--verbose` is "Show detailed error information and tracebacks" (cli.md:32)
- **Code actually does:** `--verbose` shows expression in output (normalize.py:1441, 1520)
- **Impact:** Users expecting tracebacks will not get them; `--verbose` actually behaves like `--show` in non-interactive mode

### MEDIUM — `normalize_main` alias not found
- **Documentation says:** `main()` is "aliased as `normalize_main()` for build compatibility" (cli.md:13)
- **Documentation also says:** `from nl_calc.normalize import main, normalize_main` (cli.md:16)
- **Code actually does:** No `normalize_main` alias exists anywhere in normalize.py or `__init__.py`
- **Impact:** Code referencing `normalize_main` will fail with ImportError

### LOW — No line number references in docs
- **Documentation says:** References to "Line X" style references do not exist in cli.md
- **Code location:** All actual code is in normalize.py, not __main__.py as implied
- **Impact:** Makes it harder to verify documentation accuracy

### LOW — Interactive REPL description incomplete
- **Documentation says:** REPL shows `5+2 -> 7` (cli.md:72) but actual output is `5+2 -> 7` (verified correct)
- **Documentation omits:** The welcome message shown on REPL entry ("nl-calc interactive mode...")

## Potential Bugs

### LOW — Shell glob detection path component check is fragile
- **Location:** `normalize.py:1498`
- **Code:** `if os.path.exists(path) and arg not in (".", ".."):`
- **Issue:** Only checks literal strings "." and ".." but doesn't handle other path components like "./" or "../"
- **Example:** If user runs `calc ./*` and there's a file `./file`, detection may fail or behave unexpectedly

### LOW — `_cli_text_command` uses broad exception for regex
- **Location:** `normalize.py:1396`
- **Code:** `except Exception as e:`
- **Issue:** Catches all exceptions including KeyboardInterrupt, SystemExit
- **Suggested investigation:** Should be `except re.error as e:` for regex compilation failures

### LOW — JSON output includes normalized expression unconditionally
- **Location:** `normalize.py:1179`
- **Code:** `if show_expression: print(json.dumps({"expression": joined, "result": str(result)}))`
- **Issue:** When `--json` is used without `--show`, the expression field is omitted but docs claim it "contains the normalized expression" implying it always exists
- **Impact:** JSON schema is inconsistent between modes

## Improvement Suggestions

### HIGH Priority
1. **Fix `--verbose` documentation or code:**
   - Either update cli.md to say "Show expression in output" and document it's equivalent to `--show`
   - Or change code to actually show tracebacks (current `--verbose` doesn't show tracebacks)
   - Note: `verbose` arg actually controls `show_expression` per line 1520, not error detail

2. **Remove or document `normalize_main` alias:**
   - If alias is needed for build, add it: `normalize_main = main` at end of normalize.py
   - Or update documentation to remove the alias claim

### MEDIUM Priority
3. **Add line number references to architecture docs:**
   - When referencing functions like `main()`, include "normalize.py:1421" style references

4. **Document the REPL welcome message:**
   - Add to cli.md that entering REPL shows: "nl-calc interactive mode. Type 'help' for available commands, 'quit' or 'exit' to exit."

5. **Fix `except Exception` in regex handler:**
   - Change to `except re.error` since only regex compilation can fail in that block (line 1396)

### LOW Priority
6. **Improve shell glob detection:**
   - Consider checking for path separators in args rather than just "." and ".."
   - e.g., `arg not in (".", "..") and not arg.startswith(('.', '/', '\\'))`

7. **Document JSON output schema more precisely:**
   - Note that `expression` field only appears when `--show` is used with `--json`

8. **Update docstring for `print_help()` in normalize.py:1253:**
   - Currently says "Print available operators, functions, and units" but doesn't mention it shows usage examples

## Summary

The CLI architecture is well-structured with `__main__.py` as a minimal bootstrap and `main()` in normalize.py handling all logic. Documentation accurately describes most CLI options and text commands. Two significant discrepancies exist: `--verbose` behavior doesn't match docs (shows expression instead of tracebacks), and `normalize_main` alias doesn't exist. Shell glob detection and error handling are mostly robust with minor edge case concerns in path checking and exception handling.