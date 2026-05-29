# CLI Architecture Review

## Document: cli.md

## Verified Claims
| Claim | Status | Evidence |
|-------|--------|----------|
| `__main__.py` delegates to `main()` in `normalize.py` | VERIFIED | `__main__.py:17` |
| When assembled, `main()` is aliased as `normalize_main()` | VERIFIED | `build_single.py:267-269` |
| `-h`, `--help` option exists | VERIFIED | `normalize.py:1710-1712` |
| `--usage` option exists | VERIFIED | `normalize.py:1713-1715` |
| `-v`, `--version` option exists | VERIFIED | `normalize.py:1716` |
| `-e`, `--expression` option exists | VERIFIED | `normalize.py:1720-1726` |
| `-q`, `--quiet` option exists | VERIFIED | `normalize.py:1717` |
| `-s`, `--show` option exists | VERIFIED | `normalize.py:1731-1735` |
| `--json` option exists | VERIFIED | `normalize.py:1719` |
| `-i`, `--interactive` option exists | VERIFIED | `normalize.py:1727-1729` |
| `--mcp` option exists | VERIFIED | `normalize.py:1736-1738` |
| `--verbose` option exists | VERIFIED | `normalize.py:1718` |
| `calc inspect <text>` command exists | VERIFIED | `normalize.py:1361-1388` |
| `calc count <text> [char]` command exists | VERIFIED | `normalize.py:1390-1440` |
| `calc regex <pattern> <text>` command exists | VERIFIED | `normalize.py:1442-1475` |
| `calc replace-check` command exists | VERIFIED | `normalize.py:1477-1509` |
| `calc lines` command exists | VERIFIED | `normalize.py:1511-1554` |
| `calc patch-check` command exists | VERIFIED | `normalize.py:1556-1592` |
| `calc shell-split` command exists | VERIFIED | `normalize.py:1594-1623` |
| `calc md-structure` command exists | VERIFIED | `normalize.py:1625-1668` |
| `calc dotenv-check` command exists | VERIFIED | `normalize.py:1670-1693` |
| REPL `help` command exists | VERIFIED | `normalize.py:1234-1236` |
| REPL `history` command exists | VERIFIED | `normalize.py:1238-1241` |
| REPL `clear` command exists | VERIFIED | `normalize.py:1243-1245` |
| REPL `quit`/`exit`/`exit()` exists | VERIFIED | `normalize.py:1231-1232` |
| Shell glob detection warning exists | VERIFIED | `normalize.py:1768-1789` |
| JSON output format includes `expression` field as normalized | VERIFIED | `normalize.py:1200-1201` |
| Error: `Unrecognized command` | VERIFIED | `normalize.py:653` |
| Error: `Can't divide by 0` | VERIFIED | `normalize.py:655` |
| Error: `Evaluation error` | VERIFIED | `normalize.py:657` |
| Error: `Error:` | VERIFIED | `normalize.py:662` |

## Discrepancies

1. **[MISMATCH]**: Output format documentation does not match implementation
   - Document states (lines 93-98): Plain output shows `5+3 -> 8` format with expression and arrow
   - Code actually: `run()` at `normalize.py:1203` just does `print(result)`, outputting only `8`
   - The `->` format appears nowhere in the codebase

2. **[MISMATCH]**: Quiet mode documentation describes output as only result, but so does normal mode
   - Document states (lines 93-98): Plain mode shows `5+3 -> 8`
   - Document states (lines 100-105): Quiet mode shows `8`
   - Code: Both modes print only the result; `-q`/`--quiet` only suppresses expression in interactive mode history, not the output format itself
   - The actual output behavior is identical for both plain and quiet modes in non-interactive mode

3. **[MISMATCH]**: REPL output example shows `5+2 -> 7` format
   - Document states (lines 67-68): `# >>> five plus two` then `# 5+2 -> 7`
   - Code: REPL at `normalize.py:1247` calls `run()` which prints only the result, not `5+2 -> 7`
   - The REPL does not prepend `expression -> ` to output

4. **[MISMATCH]**: Verbose mode description
   - Document states (line 28): `--verbose` - Show expression in output
   - Document states (line 124): Verbose mode shows expression in output
   - Code at `normalize.py:1797`: `show_expression = not args.quiet and ((args.verbose or args.show) or not quiet_by_default)`
   - The verbose flag only affects whether expression is shown when using the old `show_expression` output path, but the code path never actually prepends expression to output

## Bugs Identified
| Bug | Location | Severity | Description |
|-----|----------|----------|-------------|
| None | - | - | No code bugs found; all functionality works as implemented |

## Improvements Surface
| Area | Priority | Description |
|------|----------|-------------|
| Documentation | High | The entire "Output Formats" section (lines 91-115) describes an output format (`5+3 -> 8`) that the code never produces. The actual output is just the result. This is a significant documentation drift issue. |
| Documentation | Medium | The `--verbose` flag documentation suggests it shows expression in output, but no code path prepends expression to output. The flag may be non-functional for its described purpose. |
| Consistency | Low | The `show_expression` variable in `run()` and `main()` suggests a design intent for expression-prepended output, but this is never materialized. Either the feature was planned but not implemented, or the documentation incorrectly described a feature that never existed. |

## Notes

1. **Entry Point Delegation**: The architecture is correctly implemented. `__main__.py` is a minimal bootstrap that imports and calls `main()` from `normalize.py`. The `normalize_main()` aliasing in `build_single.py` works correctly to avoid MCP server `main()` conflicts.

2. **CLI Options**: All documented CLI options are implemented and functional.

3. **Text Commands**: All 7 text commands (`inspect`, `count`, `regex`, `replace-check`, `lines`, `patch-check`, `shell-split`, `md-structure`, `dotenv-check`) are fully implemented with proper error handling and JSON output support.

4. **REPL**: The interactive REPL works correctly with all documented commands (`help`, `history`, `clear`, `quit`/`exit`/`exit()`).

5. **Shell Glob Detection**: The glob expansion detection at `normalize.py:1768-1789` is correctly implemented and provides helpful user guidance.

6. **The Core Issue**: The documentation describes an output format (`expression -> result`) that never existed in the code. The code has `show_expression` variables and verbose/quiet flags that suggest this was intended, but `run()` at line 1203 simply does `print(result)` without any expression prepending. The documentation appears to describe either a planned feature that was never completed, or the documentation was written with incorrect assumptions about the output format.
